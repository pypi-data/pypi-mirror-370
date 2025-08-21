# 计算机登录用户: jk
# 系统日期: 2023/5/17 9:55
# 项目名称: async_ccdt
# 开发者: zhanyong
# import aiofiles
import asyncio
import os
from pathlib import Path
import hashlib
import json
from tqdm import tqdm
from PIL import Image
from typing import List, Optional, Union
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from tqdm.asyncio import tqdm_asyncio  # 引入 tqdm 的异步版本
import shutil
from pypinyin import pinyin, Style
import zipfile
from pyparsing import nestedExpr, removeQuotes
import pandas as pd
import requests
import warnings
import time
import random
import re
import sys
import csv
from urllib.parse import urlparse
if sys.platform != "win32":
    import resource  # 仅在非Windows平台导入


# from googletrans import Translator


class LabelmeLoad(object):
    """
    利用asyncio模块提供的异步API，实现了异步读取文件路径、异步计算文件MD5值、异步加载JSON文件内容和处理文件的功能，并利用异步并发的特性，提高了计算速度。同时也采用了缓存技术，避免了计算重复的操作。
    """

    def __init__(self, *args, **kwargs):
        self.parameter = args[0]
        self.type_args = args[1]
        self.group_error_path = ''
        self.out_of_bounds_path = ''
        self.error_path = ''
        self.dirs = list()
        # 线程池大小以当前计算机CPU逻辑核心数为准
        thread_pool_size = os.cpu_count() or 1
        self._executor = ThreadPoolExecutor(max_workers=thread_pool_size)
        # self.max_concurrency = max_concurrency = 5
        # 一个BoundedSemaphore信号量来限制并发度，即最大并发量。这可以避免对文件系统造成过大的并发读写负荷，从而提高程序的健壮性。
        # self.semaphore = asyncio.BoundedSemaphore(max_concurrency)

    async def read_directory(self, root_dir: str) -> List[str]:
        """
        异步并发读取目录下的所有图像文件路径，排除json文件
        """
        file_paths = []
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name.endswith(tuple(self.parameter.file_formats)):
                file_paths.append(entry.path)
            elif entry.is_dir() and not entry.name.endswith('01.labelme'):  # endswith检查字符串结尾的方法
                sub_paths = await self.read_directory(entry.path)
                file_paths.extend(sub_paths)
        return file_paths

    async def creat_directory(self, root_dir: str) -> List[str]:
        """
        获取json和图像路径
        @param root_dir:
        @return:
        """
        # 这里没有传参args.file_formats是因为，这个参数中没有.json格式，也不能有
        valid_extensions = ['.jpg', '.jpeg', '.png', '.JPEG', '.JPG', '.PNG', '.webp', '.json', '.bmp']
        file_all_paths = []
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name.endswith(tuple(valid_extensions)):
                file_all_paths.append(entry.path)
            elif entry.is_dir():  # endswith检查字符串结尾的方法
                sub_paths = await self.creat_directory(entry.path)
                file_all_paths.extend(sub_paths)
        return file_all_paths

    def linshi_directory(self, root_dir: str) -> List[str]:
        ok_path = list()
        for root, dirs, files in tqdm(os.walk(root_dir, topdown=True)):
            print(root)
            if root.count('00.images') == 2 or root.count('01.labelme') == 1:  # 设计规则，根据00.images目录，做唯一判断
                # if path_name not in file_path:
                if not os.listdir(root):  # 判断目录是否为空，如果目录下不存在文件就删除目录
                    os.rmdir(root)
        return ok_path

    @staticmethod
    def has_duplicate_folder_name(path, folder_name):
        folders = path.split('\\')  # 以'\\'拆分路径名
        count = 0

        for folder in folders:
            if folder == folder_name:
                count += 1
                if count >= 2:
                    return True
        return False

    @staticmethod
    async def calculate_file_md5(file_path: str) -> str:
        """
        functools.lru_cache装饰器对文件的MD5值进行了缓存，暂时没有用
        采用最近最少使用的缓存策略，最多缓存128个不同的文件的MD5值
        这样可以大大减少重复计算MD5值的次数，节约计算资源，提高程序性能。
        """
        async with aiofiles.open(file_path, 'rb') as f:
            hasher = hashlib.md5()
            buf = await f.read(8192)
            while buf:
                hasher.update(buf)
                buf = await f.read(8192)
            return hasher.hexdigest()

    @staticmethod
    async def read_file(file_path: str) -> Optional[bytes]:
        """
        异步文件句柄管理
        异步读取单个文件的内容
        Optional 类型用于标注一个变量的值或返回值可能为空（None）的情况。
        """
        if not os.path.isfile(file_path):
            print(f"Error: {file_path} is not a file!")
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
        return content

    async def calculate_file_md5_async(self, file_path: str) -> str:
        """
        在线程池中异步计算文件的MD5值
        使用了线程池执行 MD5 值计算的任务，从而充分利用了 CPU 的多核能力，可以更快地完成计算
        """
        content = await self.read_file(file_path)
        if content is None:
            print(f'图像文件内容为空，请核对该文件路径{file_path}')
            exit()
        # md5_value = await asyncio.get_running_loop().run_in_executor(self._executor, hashlib.md5, content)
        # return md5_value.hexdigest()
        # 修改MD5算法，使用SHA3-512算法，碰撞抵抗性，提供足够的安全性
        sha3_512_value = await asyncio.get_running_loop().run_in_executor(self._executor, self.calculate_sha3_512, content)
        return sha3_512_value

    @staticmethod
    def calculate_sha3_512(data: bytes) -> str:
        sha3_512_hash = hashlib.sha3_512(data)
        return sha3_512_hash.hexdigest()

    @staticmethod
    async def load_labelme(data_path: dict) -> dict:
        """
        异步加载json文件内容
        """
        # 组合加载json文件的路径
        labelme_path = os.path.join(data_path['original_json_path'])
        # print(labelme_path)
        try:
            async with aiofiles.open(labelme_path, 'r', encoding='UTF-8') as labelme_fp:
                content = await labelme_fp.read()
                data_path['labelme_info'] = json.loads(content)
                if data_path['labelme_info']['imageData'] is not None:
                    data_path['labelme_info']['imageData'] = None
                if not data_path['labelme_info']['shapes']:
                    data_path['background'] = False
        except Exception as e:  # 这里发现一个bug，自己根据图像封装的json文件路径，会存在有图像，但并没有json的情况，这样自己封装的json文件路径是找不到的，需要跳过，针对修改MD5值和相对图像路径需要跳过
            # 如果没有json文件，读取就跳过，并设置为背景
            if 'No such file or directory' in e.args:
                data_path['background'] = False
                data_path['labelme_file'] = None
                # return#突然想到这里可以不用改变，在具体实现的时候修改逻辑。
            else:  # 如果是其它情况错误（内容为空、格式错误），就删除json文件并打印错误信息
                print("json文件处理，存在问题，请手动排查")
                print(e)
                print(labelme_path)
                exit()
                # os.remove(labelme_path)
            data_path['background'] = False
        return data_path

    async def process_file(self, file_path: str, root_dir: str) -> Union[dict, str]:  # 返回两种类型之一，要么是一个字典（dict），要么是一个字符串（str）。
        """
        异步处理文件，返回封装后的数据结构
        针对一次性加载许多数据到内存导致，内存超载问题，方案如下。
        1、分批处理：将文件分成小批量，逐批处理。您可以将文件分为几个子集，然后逐一处理每个子集。这可以减少内存使用，并允许您逐步完成任务。
        2、使用数据库：将文件数据导入数据库，然后使用数据库查询来处理数据。数据库可以优化大规模数据的存储和检索。（最优推荐）
        """
        labelme_info = {}
        obj_path = Path(file_path)
        if "hw__C" in obj_path.name and self.parameter.output_format == 'newbie':
            return "skipping"
        try:
            if obj_path.suffix in self.parameter.file_formats:
                # 设计规则，根据图片文件查找json文件，同时根据约定的目录规则封装labelme数据集
                if file_path.count('00.images') == 1 or self.parameter.output_format == 'voc' or self.parameter.output_format == 'yolo_to_labelme' \
                        or self.parameter.output_format == 'sys' or self.parameter.output_format == 'xg':
                    # relative_path = os.path.join('..', obj_path.parent.name, obj_path.name)
                    relative_path = str(Path('..', obj_path.parent.name, obj_path.name))
                    # image_dir = str(obj_path.parent).replace('\\', '/').replace(root_dir, '').strip('\\/')
                    image_dir = obj_path.parent.relative_to(root_dir)
                    labelme_dir = str(Path(image_dir.parent, '01.labelme'))
                    # labelme_dir = os.path.join(image_dir.replace('00.images', '').strip('\\/'), '01.labelme')
                    labelme_file = obj_path.stem + '.json'
                    json_path = None
                    output_dir = str(Path(self.parameter.output_dir))
                    if self.parameter.output_dir:
                        # 打印的时候不需要用到，非打印功能，都会用到
                        json_path = str(Path(self.parameter.output_dir, labelme_dir, labelme_file))
                    original_json_path = str(Path(root_dir, labelme_dir, labelme_file))
                    md5_value = await self.calculate_file_md5_async(file_path)  # 如果不是图像，这里获取MD5值是无法获取的，会直接跳转，存在未知图像后缀格式数据的逻辑
                    if self.parameter.output_dir:  # 如果有输出路径，则自定义错误输出目录
                        self.group_error_path = str(Path(self.parameter.output_dir, 'group_error_data'))
                        self.out_of_bounds_path = str(Path(self.parameter.output_dir, 'out_of_bounds_path'))
                        self.error_path = str(Path(self.parameter.output_dir, 'error_path'))
                    image = Image.open(file_path)  # 当图像存在数据内容不存在的情况下，程序运行出错
                    # image, check = self.is_valid_image(file_path)  # 暂时不用
                    data_path = dict(image_dir=str(image_dir),  # 封装图像目录相对路径，方便后期路径重组及拼接
                                     image_file=obj_path.name,  # 封装图像文件名称
                                     image_width=image.width,  # 封装图像宽度
                                     image_height=image.height,  # 封装图像高度
                                     labelme_dir=labelme_dir,  # 封装json文件相对目录
                                     labelme_file=labelme_file,  # 封装json文件名称
                                     input_dir=root_dir,  # 封装输入路径目录
                                     output_dir=output_dir,  # 封装输出路径目录
                                     group_error_path=self.group_error_path,  # 标注分组出错路径
                                     out_of_bounds_path=self.out_of_bounds_path,  # 标注超出图像边界错误路径
                                     error_path=self.error_path,  # 错误数据存放总目录，不分错误类别
                                     http_url=self.parameter.http_url,  # 封装http对象存储服务访问服务地址
                                     point_number=self.parameter.point_number,
                                     # 封装数据处理类型，包含base_labelme基类和coco基类
                                     data_type=self.type_args[0].get('type'),
                                     labelme_info=None,  # 封装一张图像标注属性信息
                                     background=True,  # 封装一张图像属于负样本还是正样本，默认为True，正样本，有标注
                                     full_path=str(obj_path),  # 封装一张图像绝对路径
                                     json_path=json_path,  # 封装一张图像对应json文件绝对路径，用于输出时写文件的路径使用
                                     original_json_path=original_json_path,  # 封装原始json文件绝对路径
                                     md5_value=md5_value,  # 封装一张图像MD5值，用于唯一性判断
                                     relative_path=relative_path,
                                     # check=check,  # 图像校验结果记录，true为合格图像，false为不合格图像
                                     # 封装图像使用标注工具读取相对路径，格式为：..\\00.images\\000000000419.jpg
                                     only_annotation=False, )  # 封装是图像还是处理图像对应标注内容的判断条件，默认图片和注释文件一起处理
                    if self.parameter.output_format == 'xg':
                        labelme_info = await self.load_xg_labelme(data_path)  # 异步加载json文件,针对香港上报的车道数据
                    if self.parameter.output_format == 'newbie':
                        labelme_info = await self.load_newbie_labelme(data_path)  # 异步加载json文件,针对香港上报的车道+车牌的数据
                    else:
                        labelme_info = await self.load_labelme(data_path)  # 异步加载json文件
                    return labelme_info
                else:
                    # if self.parameter.function == 'change':  # 如果功能属于，系统输出结果，转labelme可用格式，直接追加图像路径，通过图像路径找到json路径，读取内容，转换格式
                    #     return file_path
                    # else:
                    print(f'文件夹目录不符合约定标准，请检查{file_path}')
            else:
                print(f'存在未知图像后缀格式数据{file_path}')
        except Exception as e:
            print("图像文件处理，存在问题，请手动排查,picture_of_the_problem目录中的图片")
            print(e)
            # **如果是 MemoryError，立即停止程序**
            if isinstance(e, MemoryError):
                print("内存不足，程序终止！")
                exit()  # 彻底终止
                # **判断是否是 "Too many open files"**
            if isinstance(e, OSError) and "Too many open files" in str(e):
                import resource  # 用于调整文件描述符限制（仅适用于类 Unix 系统）
                print("文件句柄超限，正在尝试增加系统文件描述符限制...")
                print(e)
                soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
                print(f"原始文件描述符限制: soft={soft_limit}, hard={hard_limit}")
                try:
                    # 提高至硬限制
                    resource.setrlimit(resource.RLIMIT_NOFILE, (hard_limit, hard_limit))
                    print("文件描述符限制已提升至硬限制。")
                except Exception as e:
                    print(f"修改文件描述符限制失败: {e}")
                soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
                print(f"当前文件描述符限制: soft={soft_limit}, hard={hard_limit}")
            else:
                # 比如图片本生为空打不开的问题
                problem_picture = os.path.join(root_dir, "picture_of_the_problem")
                os.makedirs(problem_picture, exist_ok=True)
                print(file_path)
                shutil.move(file_path, problem_picture)

    @staticmethod
    async def ensure_file_handle_limit():
        """
        提前调整文件描述符限制，防止文件句柄超限
        """
        if sys.platform == "win32":
            print("当前操作系统为Windows，不支持resource模块，跳过文件描述符调整。")
            return
        try:
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            print(f"原始文件描述符限制: soft={soft_limit}, hard={hard_limit}")
            # 提高至硬限制
            resource.setrlimit(resource.RLIMIT_NOFILE, (hard_limit, hard_limit))
            print("文件描述符限制已提升至硬限制。")
        except Exception as e:
            print(f"修改文件描述符限制失败: {e}")
        soft_limit_modify, hard_limit_modify = resource.getrlimit(resource.RLIMIT_NOFILE)
        print(f"当前文件描述符限制: soft={soft_limit_modify}, hard={hard_limit_modify}")

    async def recursive_walk(self, root_dir: str, args) -> List[str]:  # 增加函数注解，函数的返回值类型被指定为List[dict]，表示返回值是一个字典列表。
        """
        异步非阻塞并发遍历多级目录
        """
        # 提前检查和调整文件描述符限制
        await self.ensure_file_handle_limit()
        # all_images_file_path = []
        # file_paths = []
        print("异步读取文件路径完成")
        # tasks = [self.process_file(file_path, root_dir) for file_path in file_paths]  # 列表推导式处理文件异步任务列表，与下面的三行代码区别不大
        if args.function == "create_dir" or args.function == "move":
            file_all_paths = await self.creat_directory(root_dir)  # 异步读取文件路径,包含图像和json路径
            # file_all_paths = self.linshi_directory(root_dir)  # 临时删除目录方法
            return file_all_paths
        else:
            if args.function == "convert" and args.output_format == "sys":
                file_paths_all = await self.read_chipeak_directory(root_dir)
                # 筛选json文件前缀
                json_prefixes = {os.path.splitext(os.path.basename(p))[0] for p in file_paths_all if p.endswith(".json")}
                # 仅保留前缀在 json_prefixes 中的图片文件路径
                file_paths = [
                    p for p in file_paths_all
                    if p.endswith((".jpg", ".png", ".jpeg")) and os.path.splitext(os.path.basename(p))[0] in json_prefixes
                ]
            else:
                file_paths = await self.read_directory(root_dir)  # 异步读取文件路径，只获取图像路径
            # 自然排序文件路径
            file_paths = self.natural_sort(file_paths)
            # 分批异步任务调度
            print("分批异步任务调度开始")
            tasks = await self.process_files_in_batches(file_paths, root_dir, batch_size=1000)
            print("异步封装数据开始")
            all_images_file_path = await self.show_progress(tasks, desc="筛选异步处理文件数据，并封装为新列表进度")
            return all_images_file_path

            # results = await asyncio.gather(*tasks)
            # # 使用 tqdm.asyncio.tqdm() 上下文管理器将异步任务的执行过程打印到进度条中
            # with tqdm_asyncio(total=len(tasks), desc="读取文件数据并封装为新的数据结构进度条", unit="file") as progress_bar:
            #     for result in results:
            #         if result is not None and result != 'skipping':
            #             all_images_file_path.append(result)
            #         progress_bar.update(1)
            # return all_images_file_path

    async def process_files_in_batches(self, file_paths, root_dir, batch_size):
        """
        分批异步任务调度
        @param file_paths:
        @param root_dir:
        @param batch_size:
        @return:
        """
        results = []
        semaphore = asyncio.Semaphore(1024)  # 限制并发数为1024
        # 每个批次中的任务都是并发执行的，但批次之间是同步顺序执行。
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            # 使用自然排序确保按顺序读取图像
            tasks = [self.process_file_with_semaphore(file_path, root_dir, semaphore) for file_path in batch]
            batch_results = await asyncio.gather(*tasks)  # asyncio.gather等待当前批次的所有任务完成后才继续执行下一批次。
            results.extend(batch_results)
            print(f"已完成批次 {i // batch_size + 1}/{(len(file_paths) - 1) // batch_size + 1}")
        return results

    @staticmethod
    async def show_progress(tasks, desc, unit="file"):
        """
        使用异步进度条，避免阻塞
        @param tasks:
        @param desc:
        @param unit:
        @return:
        """
        results = []
        with tqdm_asyncio(total=len(tasks), desc=desc, unit=unit) as progress_bar:
            # 只提取字典的值作为协程对象列表
            for task in tasks:
                # for coro in asyncio.as_completed(tasks):
                #     result = await coro
                if task is not None and task != 'skipping':
                    results.append(task)
                progress_bar.update(1)
        print(f"新条件过滤后的列表数量为: {len(results)}")
        return results

    async def process_file_with_semaphore(self, file_path: str, root_dir: str, semaphore: asyncio.Semaphore) -> Union[dict, str]:
        async with semaphore:
            return await self.process_file(file_path, root_dir)

    @staticmethod
    def natural_sort(file_list: List[str]) -> List[str]:
        """
        自然排序文件列表,确保按顺序读取图像
        """
        convert = lambda text: int(text) if text.isdigit() else text
        key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(file_list, key=key)

    def compress_labelme(self):
        """
        封装压缩对象为字典，注意只对输入目录遍历一次，如果输入目录不对，封装结果就会出错
        :return:
        """
        print(f'封装压缩对象')
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            zip_data = {}
            for directory in dirs:
                rebuild_input_dir = os.path.join(self.type_args[0].get('input_dir'), directory)
                zipfile_obj = os.path.join(self.parameter.output_dir, directory + '.zip')
                zip_data.update({rebuild_input_dir: zipfile_obj})
            return zip_data

    @staticmethod
    def make_compress(zip_package):
        """
        针对封装好的压缩目录进行迭代写入压缩对象包中
        该算法可以跨平台解压
        :param zip_package:
        """
        print(f'开始压缩')
        for zip_key, zip_value in tqdm(zip_package.items()):
            # zip_value：压缩包名称路径
            os.makedirs(os.path.dirname(zip_value), exist_ok=True)
            with zipfile.ZipFile(zip_value, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip:  # 创建一个压缩文件对象
                for root, dirs, files in os.walk(zip_key):  # 递归遍历写入压缩文件到指定压缩文件对象中
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.join(os.path.basename(zip_key), os.path.relpath(file_path, zip_key))
                        # file_path：压缩文件绝对路径，relative_path：压缩文件相对路径，相对于压缩目录
                        zip.write(file_path, relative_path)

    def hanzi_to_pinyin(self):
        """
        汉字转拼音功能实现
        """
        file_path = list()
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix in self.parameter.file_formats:
                    # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中
                    if root.count('00.images') == 1:  # 设计规则，根据00.images目录，做唯一判断
                        if path_name not in file_path:
                            file_path.append(path_name)
        # 重命名路径
        print(f'重命名中文路径为英文开始')
        for rename_dir in tqdm(file_path):
            obj_path = Path(rename_dir)  # 初始化路径对象为对象
            input_dir = self.type_args[0].get('input_dir').replace('\\', '/')
            replace_path = str(obj_path.parent).replace('\\', '/')
            relateve_path = replace_path.replace(input_dir, '').strip('\\/')
            rebuild_output_dir = os.path.join(self.parameter.output_dir, relateve_path)
            rebuild_new_dir = self.convert_path_to_pinyin(rebuild_output_dir)
            labelme_dir = os.path.join(os.path.dirname(rebuild_new_dir), '01.labelme')
            json_file_name = obj_path.stem + '.json'
            src_json_file_path = os.path.join(obj_path.parent.parent, '01.labelme', json_file_name)
            # 创建输出目录
            os.makedirs(labelme_dir, exist_ok=True)
            os.makedirs(rebuild_new_dir, exist_ok=True)
            try:
                shutil.copy(rename_dir, rebuild_new_dir)
                shutil.copy(src_json_file_path, labelme_dir)
            except Exception as e:
                print(f"拷贝 {rename_dir} 失败: {e}")

    def rename_file_name(self):
        # 获取输入目录
        input_dir = self.type_args[0].get('input_dir')
        # 存储新文件名的集合，以避免重复
        existing_names = set()

        # 递归遍历目录
        for root, dirs, files in tqdm(os.walk(input_dir, topdown=True)):
            for file in files:
                # 获取原文件路径
                original_path = os.path.join(root, file)
                obj_path = Path(original_path)  # 使用Path对象

                # 检查文件格式是否符合要求
                # if obj_path.suffix in self.parameter.file_formats:
                # 获取当前时间戳作为文件名的一部分，精确到微秒
                timestamp = time.time()
                timestamp_sec = int(timestamp)  # 整秒部分
                timestamp_usec = int((timestamp - timestamp_sec) * 1_000_000)  # 微秒部分

                # 确保微秒部分有六位数，前面补零
                timestamp_str = f"{timestamp_sec}_{timestamp_usec:06d}"

                # 构建新的基础文件名（可以自定义前缀）
                base_new_name = f"{timestamp_str}"
                new_file_name = f"{base_new_name}{obj_path.suffix}"
                new_path = Path(root) / new_file_name  # 新路径

                # 确保新文件名不重复
                counter = 1
                while new_path.exists() or new_file_name in existing_names:
                    # 如果文件名已经存在，则添加计数后缀
                    new_file_name = f"{base_new_name}_{counter}{obj_path.suffix}"
                    new_path = Path(root) / new_file_name
                    counter += 1

                # 重命名文件
                os.rename(original_path, new_path)
                # 将新文件名添加到集合中
                existing_names.add(new_file_name)

    def hanzi_to_pinyin_images(self):
        """
        重命名目录汉字为拼音
        """
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            for dirname in dirs:
                original_dir = os.path.join(root, dirname)
                pinyin_dirname = self.convert_chinese_to_pinyin(dirname)
                new_dir = os.path.join(root, pinyin_dirname)
                try:
                    os.rename(original_dir, new_dir)
                except Exception as e:
                    print(f"重命名，存在相同名称的拼音 {original_dir} 失败: {e}")
            # # 递归处理子目录
            for dirpath, dirnames, filenames in os.walk(self.type_args[0].get('input_dir')):
                for subdir in dirnames:
                    self.convert_chinese_to_pinyin(os.path.join(dirpath, subdir))
                # 重命名路径
        print(f'注意不嵌套重命名自目录，嵌套几次目录就多执行几次指令')

    @staticmethod
    def convert_path_to_pinyin(path):
        """
        将给定路径中的汉字转换为拼音。
        path: 需要转换的路径。
        """
        # 获取路径的父目录和文件名
        parent_path, filename = os.path.split(path)
        # 将路径中的汉字转换为拼音并拼接成新的路径
        pinyin_list = pinyin(parent_path, style=Style.NORMAL)
        pinyin_path = ''.join([py[0] for py in pinyin_list])  # 提取每个汉字的首字母拼接成新的路径
        new_path = os.path.join(pinyin_path, filename)
        return new_path

    @staticmethod
    def convert_chinese_to_pinyin(chinese_text):
        """
        重命名目录的汉字为拼音
        @param chinese_text:
        @return:
        """
        pinyin_text = []
        for char in chinese_text:
            if isinstance(char, str):
                pinyin_list = pinyin(char, style=Style.NORMAL)
                pinyin_path = ''.join([py[0] for py in pinyin_list])  # 提取每个汉字的首字母拼接成新的路径
                pinyin_text.append(pinyin_path)
        return ''.join(pinyin_text)

    @classmethod
    def get_videos_path(cls, root_dir, file_formats):
        """
        视频帧提取组合路径
        :param root_dir:
        :param file_formats:
        :return:
        """
        file_path_name = list()  # 文件路径
        for root, dirs, files in os.walk(root_dir, topdown=True):
            dirs.sort()
            files.sort()
            # 遍历文件名称列表
            for file in files:
                # 获取文件后缀
                file_suffix = os.path.splitext(file)[-1]
                # 如果读取的文件后缀，在指定的后缀列表中，则返回真继续往下执行
                if file_suffix in file_formats:
                    # 如果文件在文件列表中，则返回真继续往下执行
                    file_path_name.append(os.path.join(root, file))
        return file_path_name

    @staticmethod
    def get_txt_path(root_dir):
        file_path_name = list()  # 文件路径
        for root, dirs, files in os.walk(root_dir, topdown=True):
            dirs.sort()
            files.sort()
            # 遍历文件名称列表
            for file in files:
                txt_dict = dict()  # 定义字典，存储key为关键判断值，value为路径
                obj_path = Path(file)
                key = obj_path.stem.split("_")[0]
                value = os.path.join(root, file)
                txt_dict[key] = value
                # 如果读取的文件后缀，在指定的后缀列表中，则返回真继续往下执行
                file_path_name.append(txt_dict)
        return file_path_name

    def get_english_name(self):
        file_name = list()
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix in self.parameter.file_formats:
                    # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中
                    if root.count('00.images') == 1:  # 设计规则，根据00.images目录，做唯一判断
                        if path_name not in file_name:
                            file_name.append(path_name)
        print(file_name)

    @staticmethod
    def is_valid_image(file_path, check=True):
        """
        验证图像格式及图像通道
        @param check: 默认为合格图像
        @param file_path:
        @return:
        """
        try:
            image = Image.open(file_path)
            # 验证图像格式是否为TIFF,# 验证图像是否为RGB格式
            if image.format == "TIFF" or image.mode == "RGB":
                print("图像校验存在问题" + file_path)
                return image, False  # 代表不符合标准的图像
            else:
                return image, check  # 代表正常符合标准的图像
        except Exception as e:
            print(e)
            print("图像校验存在未知情况问题" + file_path)
            # 捕获任何异常，包括文件格式不正确或文件损坏

    def check_images_format(self):
        """
        找出图像格式后缀
        """
        other_format = list()
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix not in self.parameter.file_formats and obj_path.suffix != '.json':
                    other_format.append(obj_path.suffix)
                    print(path_name)
        print(list(set(other_format)))

    def print_icategory_name(self, args):
        class_name_list = list()
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            print(dirs)
            print("类别名称打印完成")
            class_name_list.extend(dirs)
            break
        print("拷贝图像到分类目录开始")
        for name in class_name_list:
            new_input_dir = os.path.join(self.type_args[0].get('input_dir'), name)
            output_dir = os.path.join(args.output_dir, name)
            os.makedirs(output_dir, exist_ok=True)
            for root, dirs, files in tqdm(os.walk(new_input_dir, topdown=True)):
                for file in files:
                    new_image_path = os.path.join(root, file)
                    try:
                        shutil.copy(new_image_path, output_dir)
                    except Exception as e:
                        print(e)
                        print("拷贝图像出错")

    def get_excel_url_data(self, args):
        # 将单引号替换为双引号，并将反斜杠转义
        json_str = args.input_datasets.replace("'", '"').replace("\\", "\\\\")
        # 解析 JSON 字符串
        json_data = json.loads(json_str)
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
        # 获取 input_txt_dir 的值
        input_txt_dir = json_data[0]['input_dir_xls']
        # 读取Excel文件
        df = pd.read_excel(input_txt_dir)
        # 获取特定列的数据（确保你获取的是 Series 而不是 DataFrame）
        for column_name in args.column_name:
            column_data = df[column_name].tolist()  # 获取 Series 并转换为列表
            save_directory = os.path.join(args.output_dir, column_name)
            # 确保目录存在
            os.makedirs(save_directory, exist_ok=True)
            # 下载所有文件
            for url in column_data:
                self.download_file(url, save_directory, args.algorithm_type)

    @staticmethod
    def download_file(url, save_dir, algorithm_type):
        """
        下载指定 URL 的文件并保存到指定目录
        @param url: 文件的 URL
        @param save_dir: 文件保存的目录
        @param algorithm_type: 算法类型
        """
        try:
            # 获取文件名，替换特殊字符
            filename = os.path.basename(url)
            matched_keywords = [keyword for keyword in algorithm_type if keyword in url]
            if matched_keywords:
                # print("Matched keywords:", matched_keywords)
                new_save_dir = os.path.join(save_dir, str(matched_keywords))
                os.makedirs(new_save_dir, exist_ok=True)
                local_filename = os.path.join(new_save_dir, filename)
            else:
                # print("No keywords matched.")
                local_filename = os.path.join(save_dir, filename)
            # 发送请求获取文件大小以显示进度条
            response = requests.get(url, stream=True, verify=True)  # verify=False时，忽略了 HTTPS 证书验证
            # 检查请求是否成功
            if response.status_code == 200:
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024  # 设置进度条的块大小
                # 打开文件并写入
                with open(local_filename, 'wb') as f:
                    for data in tqdm(response.iter_content(block_size), total=total_size // block_size, unit='KB', desc=filename):
                        f.write(data)
                # with open(local_filename, 'wb') as file:
                #     for chunk in response.iter_content(chunk_size=8192):
                #         file.write(chunk)
                print(f"File downloaded successfully and saved to {local_filename}")
            else:
                print(f"Failed to download file. HTTP status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")

    async def load_xg_labelme(self, data_path: dict) -> dict:
        """
        异步加载json文件内容
        """
        # 组合加载json文件的路径
        labelme_path = os.path.join(data_path['original_json_path'])
        try:
            with open(labelme_path, 'r', encoding='UTF-8') as labelme_fp:
                content = labelme_fp.read()
                data_path['labelme_info'] = json.loads(content)
                nested = nestedExpr('{', '}').parseString('{' + data_path['labelme_info']["data"] + '}')
                # 转换为 JSON 对象
                json_data = self.parse_nested_list(nested.asList())
                # 输出 JSON 字符串
                json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                print(json_str)
                # if data_path['labelme_info']['imageData'] is not None:
                #     data_path['labelme_info']['imageData'] = None
                # if not data_path['labelme_info']['shapes']:
                #     data_path['background'] = False
        except Exception as e:  # 这里发现一个bug，自己根据图像封装的json文件路径，会存在有图像，但并没有json的情况，这样自己封装的json文件路径是找不到的，需要跳过，针对修改MD5值和相对图像路径需要跳过
            # 如果没有json文件，读取就跳过，并设置为背景
            if 'No such file or directory' in e.args:
                data_path['background'] = False
                data_path['labelme_file'] = None
                # return#突然想到这里可以不用改变，在具体实现的时候修改逻辑。
            else:  # 如果是其它情况错误（内容为空、格式错误），就删除json文件并打印错误信息
                print("json文件处理，存在问题，请手动排查")
                print(e)
                print(labelme_path)
                # exit()
                # os.remove(labelme_path)
            data_path['background'] = False
        return data_path

    @staticmethod
    async def load_newbie_labelme(data_path: dict) -> dict:
        # 组合加载json文件的路径
        labelme_path = os.path.join(data_path['original_json_path'])
        if os.path.exists(labelme_path):  # 文件路径存在的情况
            try:
                with open(labelme_path, 'r', encoding='UTF-8') as labelme_fp:
                    content = labelme_fp.read()
                    xg_data = json.loads(content)
                    labelme_data = dict(
                        version='4.5.9',
                        flags={},
                        shapes=[],
                        imagePath=None,
                        imageData=None,
                        imageHeight=None,
                        imageWidth=None,
                        md5Value=None
                    )
                    shapes = []
                    label = xg_data.get('data').get('vehicle_info').get('lane_id')
                    text = xg_data.get('data').get('vehicle_info').get('license_plate_id')
                    rectangle = xg_data.get('data').get('vehicle_info').get('obj_position')
                    lt_x = rectangle.get('lt_x')
                    lt_y = rectangle.get('lt_y')
                    rb_x = rectangle.get('rb_x')
                    rb_y = rectangle.get('rb_y')
                    rectangle_points = [[lt_x, lt_y], [rb_x, rb_y]]
                    # 只处理带多边形框，并转labelme
                    rectangle_shape = {"label": label, "points": rectangle_points, "group_id": None, "shape_type": "rectangle", "flags": {}, 'text': None}
                    polygon = xg_data.get('data').get('vehicle_info').get('car_plate_point')
                    x1 = polygon[0][0]
                    y1 = polygon[0][1]
                    x2 = polygon[0][2]
                    y2 = polygon[0][3]
                    x3 = polygon[0][4]
                    y3 = polygon[0][5]
                    x4 = polygon[0][6]
                    y4 = polygon[0][7]
                    polygon_points = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                    polygon_shape = {"label": 'plate', "points": polygon_points, "group_id": None, "shape_type": "polygon", "flags": {}, 'text': text}
                    shapes.append(rectangle_shape)
                    shapes.append(polygon_shape)
                    labelme_data.update({'shapes': shapes})
                    # park_slot_id车位id，park_slot_status事件状态
                    rectangle_shape.get("flags").update({xg_data.get('data').get('vehicle_info').get('park_slot_status'): True,
                                                         xg_data.get('data').get('vehicle_info').get('park_slot_id'): True})
                    data_path['labelme_info'] = labelme_data
            except Exception as e:
                print("针对newbie的json文件处理，存在问题，请手动排查")
                print(e)
            return data_path
        else:
            # 文件路径不存在
            data_path['background'] = False
            data_path['labelme_file'] = None
            return data_path

    # 递归解析函数
    def parse_nested_list(self, nested_list):
        it = iter(nested_list)
        result = {}
        for key in it:
            print(key)
            # key[1][3][3]
            # key[1][3][5]
            # key[1][3][1][31]
            # print(value)
            # 将字符串转换为 JSON 对象
            data_json = json.loads(key[1][3][1][31][3])
            # 去除外层的引号
            data_str = data_json.strip('"')
            if key.endswith(':'):
                key = key[:-1]
            value = next(it)
            if isinstance(value, list):
                result[key] = self.parse_nested_list(value)
            else:
                result[key] = value.strip('"')
        return result

    def ratio_split(self, args):
        # 创建输出目录结构
        train_dir = os.path.join(args.output_dir, 'train')
        test_dir = os.path.join(args.output_dir, 'test')
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)
        # 收集所有图片的完整路径
        image_paths = []
        for root, dirs, files in tqdm(os.walk(self.type_args[0].get('input_dir'), topdown=True)):
            # 假设 args.file_formats 是原始输入或参数
            if isinstance(args.file_formats, list):
                args.file_formats = tuple(args.file_formats)  # 转换为元组
            # 遍历文件
            image_files = [f for f in files if f.lower().endswith(args.file_formats)]
            for img in image_files:
                image_paths.append(os.path.join(root, img))
        # 打乱图片路径列表
        random.shuffle(image_paths)

        # 计算测试集的数量
        num_test = int(len(image_paths) * args.test_ratio)

        # 划分训练集和测试集
        test_images = image_paths[:num_test]
        train_images = image_paths[num_test:]

        # 保存训练集和测试集，保持目录结构
        for train_img_path in tqdm(train_images):
            # 计算目标路径
            relative_path = os.path.relpath(os.path.dirname(train_img_path), self.type_args[0].get('input_dir'))
            target_dir = os.path.join(train_dir, relative_path)
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(train_img_path, os.path.join(target_dir, os.path.basename(train_img_path)))

        for test_img_path in tqdm(test_images):
            # 计算目标路径
            relative_path = os.path.relpath(os.path.dirname(test_img_path), self.type_args[0].get('input_dir'))
            target_dir = os.path.join(test_dir, relative_path)
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(test_img_path, os.path.join(target_dir, os.path.basename(test_img_path)))

        print("数据集划分完成！\n训练集和测试集已创建。")

    async def read_chipeak_directory(self, root_dir):
        file_paths = []
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name.endswith((".jpg", ".json")):
                file_paths.append(entry.path)
            elif entry.is_dir() and not entry.name.endswith('01.labelme'):  # endswith检查字符串结尾的方法
                sub_paths = await self.read_chipeak_directory(entry.path)
                file_paths.extend(sub_paths)
        return file_paths

        # @staticmethod
    def extract_fields_csv(self, file_path, args):
        """
        从 CSV 文件中提取指定字段
        :param file_path: CSV 文件路径
        :param args: 要提取的字段名列表
        :return: 提取的字段数据（列表字典）
        内存占用低、速度快。
        """
        extracted_data = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            os.makedirs(args.output_dir, exist_ok=True)
            for idx, row in enumerate(reader):
                if not row:
                    continue  # 跳过空行
                url = row.get(args.fields)
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    # 取文件名（如果 URL 没有文件名，则用 idx 命名）
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path) or f'image_{idx}.jpg'
                    # 保证图片名称唯一，如果文件名冲突，自动追加编号，返回不重复的文件名
                    unique_path = self.get_unique_filename(args.output_dir, filename)
                    # 安全保存路径
                    # filepath = Path(args.output_dir) / filename
                    # 保存图片
                    with open(unique_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ 下载成功: {unique_path}")
                except Exception as e:
                    print(f"❌ 下载失败 (行{idx + 1}): {url}，错误：{e}")

    @staticmethod
    def get_unique_filename(save_dir, filename):
        """
        如果文件名冲突，自动追加编号，返回不重复的文件名
        """
        base, ext = os.path.splitext(filename)
        counter = 1
        candidate = Path(save_dir) / filename
        while candidate.exists():
            candidate = Path(save_dir) / f"{base}_{counter}{ext}"
            counter += 1
        return candidate
