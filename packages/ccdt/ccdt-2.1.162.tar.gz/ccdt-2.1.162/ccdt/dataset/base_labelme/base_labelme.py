# 计算机登录用户: jk
# 系统日期: 2023/5/17 9:46
# 项目名称: async_ccdt
# 开发者: zhanyong
# from ccdt.dataset import *
# from tqdm import tqdm
import os
import shutil
from multiprocessing import Pool
import matplotlib.pyplot as plt
import prettytable as pt
import time
from .async_io_task import *
from collections import defaultdict, Counter
import random
from shapely.geometry import Polygon, Point, box, MultiPolygon, GeometryCollection
from shapely.geometry.base import BaseGeometry
import cv2
import numpy as np
from pathlib import Path
import copy
import json
from ccdt.dataset.utils.encoder import Encoder
from sklearn.decomposition import PCA  # 使用它来执行主成分分析和降维操作
from itertools import count
from PIL import Image, ImageDraw, ImageFont
import pkg_resources  # ✅ 用于加载包内资源


def my_sort(item):
    """
    自定义标注形状排序，把标注形状为矩形框的排序在列表第一位
    :param item:
    :return:
    """
    if item['shape_type'] == 'polygon':
        # 由于任何数除以负无穷大都是负数，所以将其返回值设为 -float('inf')
        return str('inf')
    else:
        return item['shape_type']


class SingletonMeta(type):
    """
    type 类也是一个元类
    使用基于元类的实现方式实现单例设计模式基类，是因为它在代码结构和执行效率方面都更加高效
    单例设计模式，只会生成一个对象，并在应用程序中全局访问它，节省内存和CPU时间
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseLabelme(metaclass=SingletonMeta):
    def __init__(self, *args, **kwargs):
        """
        传参初始化labelme数据集对象
        """
        self.datasets = args[0]
        self.check_error_dataset = list()  # 存储错误图像数据变量列表
        self.error_output_path = ''  # 定义全局错误输出路径变量
        self.error_image_path = ''  # 定义全局图像路径变量
        self.automatic_correction = list()  # 定义存放逻辑处理后封装数据的存放列表
        self.output_dir = ''  # 自定义数据保存输入目录，用于传参时灵活使用

    def save_labelme(self, output_dir, index, custom_label):
        print('异步写内存数据到磁盘操作开始')
        # ==============================异步写内存数据到磁盘操作==================================================
        async_io_task = AsyncIoTask()
        async_time = time.time()
        if isinstance(output_dir, str) or output_dir is None:
            asyncio.run(async_io_task.process_files(self.datasets, output_dir, None, custom_label))
        if isinstance(output_dir, list) and output_dir != []:  # 传递列表，传递索引
            asyncio.run(async_io_task.process_files(output_dir, True, index, custom_label))
        print('数据写入使用异步计算耗时')
        print(time.time() - async_time)
        # ==============================异步写内存数据到磁盘操作==================================================

    def rename_labelme(self, parameter):
        """
        重命名功能实现，包含label和flags
        :param parameter:
        """
        print(f'重命名label标签名称')
        for data_info in tqdm(self.datasets):
            if data_info['labelme_info'] is not None:
                for shape in data_info['labelme_info']['shapes']:
                    if parameter.rename_attribute.get('label') is None and parameter.rename_attribute.get(
                            'flags') is None:
                        assert False, '输入的（--rename-label）重命名属性值为空'.format(parameter.rename_attribute)
                    if parameter.rename_attribute.get('label') and parameter.rename_attribute.get('flags'):
                        self.label_rename(shape, parameter.rename_attribute)
                        self.flags_rename(shape, parameter.rename_attribute)
                    if parameter.rename_attribute.get('flags'):
                        self.flags_rename(shape, parameter.rename_attribute)
                    if parameter.rename_attribute.get('label'):
                        self.label_rename(shape, parameter.rename_attribute)
        print(f'保存重命名后的labelme数据集')
        self.save_labelme(parameter.output_dir, None, None)

    @staticmethod
    def label_rename(shape, rename):
        """
        重命名label
        :param shape:
        :param rename:
        """
        if shape['label'] in rename.get('label'):  # 修改标签类别名称
            shape['label'] = rename.get('label').get(shape['label'])

    @staticmethod
    def flags_rename(shape, rename):
        """
        重命名flags
        :param shape:
        :param rename:
        """
        # 判断一个列表的元素是否在另一个列表中
        if set(rename.get('flags').keys()).issubset(shape['flags'].keys()):
            for rename_key in rename.get('flags').keys():  # 修改标签类别属性名称
                shape['flags'][rename.get('flags')[rename_key]] = shape['flags'].pop(rename_key)

    def del_label(self, label):
        """
        指定label类别进行删除操作，假删除，一定写输出路径防止错误发生
        :param label:
        """
        print(f'指定label类别进行删除处理')
        for data_info in tqdm(self.datasets):
            if data_info['labelme_info'] is None:
                continue
            elif data_info['labelme_info']:
                for shape in reversed(data_info['labelme_info']['shapes']):
                    if shape['label'] in label:
                        data_info.get('labelme_info').get('shapes').remove(shape)
        return self.datasets

    def __repr__(self):
        """
        打印功能实现
        :return:
        """
        num_shapes = 0  # 计数shape为空
        num_labelme = 0  # 计数labelme_info
        num_images = 0  # 计数image_file
        label_num_shapes = list()  # 统计每一个标签的框数量
        num_background = 0  # 计数labelme_info为空并且image_file不为空.有图片没有标注的算背景，有json文件就算背景不对
        property_tb = pt.PrettyTable(['label_name', 'shape_type_name', 'flags_name', 'label_num_shapes'])
        num_tb = pt.PrettyTable(['num_images', 'num_labelme', 'num_background', 'num_shapes'])
        # flags_true_tb = pt.PrettyTable(
        #     ['不确定车牌颜色数量', '黄绿色车牌数量', '黄色车牌数量', '蓝色车牌数量', '绿色车牌数量', '白色车牌数量', '黑色车牌数量', '单层车牌数量',
        #      '双层车牌数量', '完整车牌数量', '不完整车牌数量'])
        flags_true_tb = pt.PrettyTable(['other', 'yellow_green', 'yellow', 'blue', 'green', 'white', 'black', 'single', 'double', 'complete', 'incomplete', ])
        # flags_false_tb = pt.PrettyTable()
        other = 0
        yellow_green = 0
        yellow = 0
        blue = 0
        green = 0
        white = 0
        black = 0
        single = 0
        double = 0
        complete = 0
        incomplete = 0
        label_value = []
        print_data = list()
        title = ''
        true_counts = Counter()
        false_counts = Counter()
        # 动态获取 Counter 中的键作为列名，并设置为表格的字段
        # flags_true_tb.field_names = list()
        print(f'筛选及重组满足打印条件的labelme数据集')
        for data_info in tqdm(self.datasets):
            # true_counts, false_counts = self.count_flags(data_info)
            title = data_info.get('input_dir')
            num_images += 1
            if data_info.get('image_file') and data_info.get('labelme_info'):
                num_labelme += 1
            if data_info.get('background') is False:
                num_background += 1
            if data_info.get('background') is True:
                for shape in data_info.get('labelme_info').get('shapes'):
                    num_shapes += 1
                    label_num_shapes.append(shape.get('label'))
                    if shape.get('label') not in label_value:
                        rebuild_shape = {}
                        label_value.append(shape.get('label'))
                        rebuild_shape.update({'label': shape.get('label')})
                        rebuild_shape.update({'shape_type': shape.get('shape_type')})
                        rebuild_shape.update({'flags': shape.get('flags')})
                        print_data.append(rebuild_shape)
                    if shape.get('flags'):  # 如果标注属性存在值，就进行统计每个键对应为真的数量
                        for key, value in shape.get('flags').items():
                            # if key not in flags_true_tb.field_names:  # 动态追加键，作为列名称，并设置为表格的字段
                            #     flags_true_tb.field_names.append(key)
                            if value:
                                true_counts[key] += 1
                            else:
                                false_counts[key] += 1
        count_label = Counter(label_num_shapes)  # 统计每个标签元素出现的次数
        num_tb.add_row([num_images, num_labelme, num_background, num_shapes])
        # print(f'打印满足重组条件的labelme数据集')
        for data in print_data:
            property_tb.add_row([data.get('label'), data.get('shape_type'), data.get('flags'), count_label])
        print(num_tb.get_string(title=title))
        print(property_tb.get_string(title=title))
        print("Flags with True counts:", true_counts)
        print("Flags with False counts:", false_counts)

        # 遍历 Counter 对象，并添加数据到表格中
        for flag, count_true in true_counts.items():
            if flag == "other":
                other = count_true
            if flag == "yellow_green":
                yellow_green = count_true
            if flag == "yellow":
                yellow = count_true
            if flag == "blue":
                blue = count_true
            if flag == "green":
                green = count_true
            if flag == "white":
                white = count_true
            if flag == "black":
                black = count_true
            if flag == "single":
                single = count_true
            if flag == "double":
                double = count_true
            if flag == "complete":
                complete = count_true
            if flag == "incomplete":
                incomplete = count_true
        flags_true_tb.add_row([other, yellow_green, yellow, blue, green, white, black, single, double, complete, incomplete])
        print(flags_true_tb.get_string(title=title))

    def split_list(self, parameter):
        """
        将列表平均分成 extract_amount 份。同时把向下取整的余数自动多增加一份。
        :param parameter: 指定份数
        """
        random.shuffle(self.datasets)  # 随机打乱列表
        avg = len(self.datasets) // float(parameter.extract_portion)
        remainder = len(self.datasets) % float(parameter.extract_portion)
        # result = []  # 分好后追加列表又会导致内存里面多了一份数据集
        last = 0.0
        index = 0
        while index < parameter.extract_portion:
            if remainder == 0:
                self.save_labelme(self.datasets[int(last):int(last + avg)], index, parameter.label_name)
                last += avg
                index += 1
            else:
                if index == parameter.extract_portion - 1:  # 如果是最后一组,索引结束位置添加余数
                    self.save_labelme(self.datasets[int(last):int(last + avg + remainder)], index, parameter.label_name)
                else:
                    self.save_labelme(self.datasets[int(last):int(last + avg)], index, parameter.label_name)
                last += avg
                index += 1
        # return result

    def extract_labelme(self, parameter):
        """
        抽取labelme数据集功能实现，可按指定份数、指定文件数量抽取
        :param parameter:
        """
        if parameter.select_cut is False:  # 拷贝
            print(f'拷贝labelme数据处理')
            # 按指定份数抽取labelme数据集
            if parameter.extract_portion and parameter.extract_portion > 0:
                self.split_list(parameter)
                # 指定张数抽取
            elif parameter.extract_amount and parameter.extract_amount > 0:
                self.save_labelme(random.sample(self.datasets, parameter.extract_amount), parameter.select_cut, None)
            elif isinstance(parameter.extract_text, list):
                print(f'抽取text字段的文本内容数据处理')
                save_dataset = list()
                for index, dataset in tqdm(enumerate(self.datasets)):
                    if dataset.get('background') is True:
                        for shape in dataset.get('labelme_info').get('shapes'):
                            num_rounded = shape.get('text')[:shape.get('text').find('.') + 2]  # 取小数点后一位并截断  # 保留一位小数
                            if num_rounded in parameter.extract_text:
                                print(num_rounded)
                                # print(dataset.get('full_path'))
                                save_dataset.append(dataset)
                            # else:
                            # del self.datasets[index]
                print(f'保存抽取数据集')
                self.save_labelme(save_dataset, parameter.output_dir, None)
            else:
                print(f'抽取份数不能为零：{parameter.extract_portion}{parameter.extract_amount}')
                exit()
        if parameter.select_cut is True:  # 剪切
            print(f'剪切labelme数据处理')
            # 按照指定数量抽取labelme数据集
            if parameter.extract_amount and parameter.extract_amount > 0:
                # 从列表self.datasets中随机抽取3个元素
                # extract_dataset = random.sample(self.datasets, parameter.extract_amount)
                self.save_labelme(random.sample(self.datasets, parameter.extract_amount), parameter.select_cut, None)
            else:
                print(f'抽取份数不能为零：{parameter.extract_portion}{parameter.extract_amount}')
                exit()

    def filter_positive(self, parameter):
        """
        筛选正样本
        筛选负样本
        :param parameter:
        """
        print(f'筛选数据集样本处理')
        positive_data = list()
        for filter_data in tqdm(self.datasets):
            if filter_data.get('background') is True and parameter.function == 'filter_positive':
                positive_data.append(filter_data)
            if filter_data.get('background') is False and parameter.function == 'filter_negative':
                positive_data.append(filter_data)
        print(f'保存筛选样本数据集')
        self.save_labelme(positive_data, parameter.output_dir, None)

    def filter_label(self, parameter):
        """
        根据标注label进行筛选
        :param parameter:
        """
        print(f'根据标注label进行筛选labelme数据封装处理')
        rebuild_dataset = list()
        print_list = ['persom_modify', 'plate_modify', 'OilTankTruck']
        if bool(parameter.filter_label):
            if isinstance(parameter.filter_label, list):
                for label in parameter.filter_label:  # 根据标签查找对应的标注
                    data_info = self.label_find(label, parameter)
                    rebuild_dataset.extend(data_info)
            else:
                print(f'请核对输入参数是否为列表{parameter.filter_label}，列表正确格式为：{print_list}')
        else:
            label_value = list()
            for filter_data in self.datasets:  # 获取所有标注标签，用于判断
                if filter_data.get('background') is True:
                    for shape in filter_data.get('labelme_info').get('shapes'):
                        if shape.get('label') not in label_value:
                            label_value.append(shape.get('label'))

            for label in label_value:  # 根据标签查找对应的标注
                data_info = self.label_find(label, parameter)
                rebuild_dataset.extend(data_info)
        # 保存挑选后封装好的数据
        print(f'保存挑选后封装好的labelme数据')
        self.save_labelme(rebuild_dataset, parameter.output_dir, None)

    def label_find(self, label, parameter):
        """
        根据标签、flag，查找标注属性，并重组一个文件与json文件对象
        :param label:可传入label、flag
        :return:
        @param label:
        @param parameter:
        """
        label_dataset = list()
        for filter_data in self.datasets:
            rebuild_filter_data = {}  # 不修改原始加载封装数据，重新构建新的输出组合数据
            if filter_data.get('background') is True:
                label_in_shape = {}
                label_to_shapes = list()
                flags_to_shapes = list()
                for shape in filter_data.get('labelme_info').get('shapes'):
                    if shape.get('label') == label:  # 根据label追加shape标注
                        label_to_shapes.append(shape)
                    if label in shape.get('flags').keys() and shape.get('flags').get(label) == parameter.flags_true:  # 根据flag为true追加shape标注
                        flags_to_shapes.append(shape)
                # labelme_info数据封装
                label_in_shape.update({'version': filter_data.get('labelme_info').get('version')})
                label_in_shape.update({'flags': filter_data.get('labelme_info').get('flags')})
                if label_to_shapes:
                    label_in_shape.update({'shapes': label_to_shapes})
                if flags_to_shapes:
                    label_in_shape.update({'shapes': flags_to_shapes})
                if flags_to_shapes and label_to_shapes:
                    print(f'标注的label和flag名称相同{label}，筛选异常，需要人工复核')
                    exit()
                label_in_shape.update({'imagePath': filter_data.get('labelme_info').get('imagePath')})
                label_in_shape.update({'imageData': filter_data.get('labelme_info').get('imageData')})
                label_in_shape.update({'imageHeight': filter_data.get('labelme_info').get('imageHeight')})
                label_in_shape.update({'imageWidth': filter_data.get('labelme_info').get('imageWidth')})
                # filter_data数据封装
                new_output_dir = os.path.join(filter_data.get('output_dir'), label)
                new_json_path = os.path.join(new_output_dir, filter_data.get('labelme_dir'), filter_data.get('labelme_file'))
                rebuild_filter_data.update({'image_dir': filter_data.get('image_dir')})
                rebuild_filter_data.update({'image_file': filter_data.get('image_file')})
                rebuild_filter_data.update({'labelme_dir': filter_data.get('labelme_dir')})
                rebuild_filter_data.update({'labelme_file': filter_data.get('labelme_file')})
                rebuild_filter_data.update({'input_dir': filter_data.get('input_dir')})
                rebuild_filter_data.update({'output_dir': new_output_dir})
                rebuild_filter_data.update({'http_url': filter_data.get('http_url')})
                rebuild_filter_data.update({'data_type': filter_data.get('data_type')})
                rebuild_filter_data['labelme_info'] = label_in_shape
                rebuild_filter_data.update({'background': filter_data.get('background')})
                rebuild_filter_data.update({'full_path': filter_data.get('full_path')})
                rebuild_filter_data.update({'json_path': new_json_path})
                rebuild_filter_data.update({'original_json_path': filter_data.get('original_json_path')})
                rebuild_filter_data.update({'md5_value': filter_data.get('md5_value')})
                rebuild_filter_data.update({'relative_path': filter_data.get('relative_path')})
                rebuild_filter_data.update({'only_annotation': filter_data.get('only_annotation')})
                if rebuild_filter_data.get('labelme_info').get('shapes'):
                    label_dataset.append(rebuild_filter_data)  # 筛选正样本，有标注框才追加封装数据
        return label_dataset

    def filter_flags(self, parameter):
        """
        根据flag筛选标注数据集
        :param parameter:
        """
        print(f'根据flag筛选标注数据集处理')
        rebuild_dataset = list()
        print_list = ['blue', 'green', 'yellow']
        if bool(parameter.filter_flags):
            if isinstance(parameter.filter_flags, list):
                for flag in tqdm(parameter.filter_flags):  # 根据标签的flag属性，查找对应的标注
                    data_info = self.label_find(flag, parameter)  # 把flags为true的保留一份
                    rebuild_dataset.extend(data_info)
            else:
                print(f'请核对输入参数是否为列表{parameter.filter_flags}，列表正确格式为：{print_list}')
        # 保存挑选后封装好的数据
        print(f'保存挑选后封装好的labelme数据')
        self.save_labelme(rebuild_dataset, parameter.output_dir, None)

    def check_image_path(self, parameter):
        """
        imagePath检查功能实现，如果不符合标注规范，就重写json内容
        """
        print(f'检查imagePath路径，是否符合..\\00.images\\*.jpg的标准规范')
        build_path_dataset = list()
        i = 0
        for dataset in tqdm(self.datasets):
            if dataset.get('labelme_info') is not None:
                if dataset.get('labelme_info').get('imagePath').count('00.images') != 1:
                    i += 1
                    dataset.get('labelme_info').update({'imagePath': dataset.get('relative_path')})
                    if dataset.get('background') is False:
                        dataset.update({'background': True})  # 方便写json文件数据
                    build_path_dataset.append(dataset)  # 只对有问题的进行更新，即json文件重写
            # else:
            # print(dataset)
        print(f'不符合标注规范的图像有{i}张')
        print(f'把不符合要求的json文件进行重写')
        self.save_labelme(build_path_dataset, parameter.output_dir, None)

    def save_chipeak_data(self, parameter):
        build_path_dataset = list()
        for dataset in tqdm(self.datasets):
            # 原 JSON 文件路径
            json_name = os.path.splitext(dataset['image_file'])[0] + ".json"
            json_src = os.path.join(dataset['input_dir'], dataset['labelme_dir'])
            # 目标 JSON 文件夹
            os.makedirs(json_src, exist_ok=True)
            json_dst = os.path.join(dataset['input_dir'],dataset['image_dir'], json_name)
            if os.path.exists(json_dst):
                # 移动 JSON 文件到 labelme 文件夹
                shutil.move(json_dst, json_src)
                # 更新 dataset 内部的路径信息
                dataset['labelme_file'] = json_name
                dataset['background'] = True
                # 读取 JSON 内容到 labelme_info
                with open(dataset['json_path'], 'r', encoding='utf-8') as f:
                    dataset['labelme_info'] = json.load(f)
                    dataset['labelme_info']['imagePath'] = dataset['relative_path']
                    dataset['labelme_info']['imageData'] = None
                build_path_dataset.append(dataset)
            else:
                print(f"[Warning] JSON not found for image {dataset['full_path']}")
        self.save_labelme(build_path_dataset, parameter.output_dir, None)

    def filter_images(self, parameter):
        """
        筛选训练样本数据，默认勾选1保留选择数据，勾选0删除选择数据
        @param parameter:
        """
        filter_images = list()
        print(f'筛选flgas标记勾选为真的图像，默认约定1=true、0=false')
        for dataset in tqdm(reversed(self.datasets)):
            if dataset.get('labelme_info'):
                if dataset.get('labelme_info').get('flags'):  # 如果flags字典不为空
                    if parameter.right_check and dataset.get('labelme_info').get('flags').get('1') and dataset.get('labelme_info').get('flags').get(
                            '0'):  # 如果勾选0又勾选1打印提示信息
                        # filter_images.append(dataset)
                        print("标记有错误，出现即保留又删除的勾选，请核对")
                        print(dataset.get('full_path'))
                        exit()
                    # 有=true、没有=false；训练=true、不训练=false；要=true、不要=false；真=true、假=false；1=true、0=false；开=true、关=false；勾选=true、不勾选=false；
                    if parameter.right_check and dataset.get('labelme_info').get('flags').get('1'):  # 勾选1代表保留勾选图像及对应标注的json文件
                        filter_images.append(dataset)
                        # dataset.update({'background': True})  # 同时更新没有标注框的图像不为背景
                    if parameter.right_check and dataset.get('labelme_info').get('flags').get('0'):  # 勾选0代表删除图像及对应的标注json文件---修改为移动比较靠谱
                        print(f"删除数据为：{dataset.get('full_path')}")
                        os.remove(dataset.get('full_path'))  # 删除图像文件
                        os.remove(dataset.get('original_json_path'))  # 删除图像对应的标注json文件
        print(f'保存筛选数据开始')
        if parameter.select_cut:  # 移动筛选数据
            self.save_labelme(filter_images, parameter.select_cut, "right_check")
        else:  # 拷贝筛选数据
            self.save_labelme(filter_images, self.output_dir, None)

    def merge_labelme(self, parameter):
        """
        针对筛选数据集进行合并，筛选后保存的首级目录可以被修改，不影响合并功能
        根据图像文件唯一MD5值，查找标注shape属性并进行合并
        :param parameter:
        """
        print(f'对筛选的labelme数据集进行合并处理')
        md5_value_list = list()
        # 使用，列表推导式将会创建一个新的列表md5_value_list，这种方法的时间复杂度为O(n)，把每一个文件的MD5值都追加在列表中
        [md5_value_list.append(dataset.get('md5_value')) for dataset in self.datasets if dataset.get('md5_value') not in md5_value_list]
        distinct_md5_list = list(set(md5_value_list))  # 对所有MD5值元素去重，减少查询相同MD5值时的迭代次数
        if len(md5_value_list) == len(self.datasets):
            print("请检查图像文件元数据是否发生变化，未找到相同的图像存在，无法进行合并")
            exit()
        # 判断 len(self.datasets) 是否是 distinct_md5_list 的倍数
        # result = self.is_multiple(len(self.datasets), len(distinct_md5_list))
        # if result is False:
        #     print("发现要合并的文件中MD5值，不存在倍数关系，无法进行合并。也就是说要合并的标签份数中，存在部分MD5值相同，部分MD5值不同")
        #     exit()
        merge_datasets = list()
        for md5 in tqdm(md5_value_list):  # 根据文件MD5值在加载数据集中查找标注属性
            data = self.md5_value_find(md5)  # 这里，每一个MD5值都要在所有封装的文件中进行查找，然而相同的元素只有一个
            merge_datasets.append(data)
        print(f'保存labelme标注属性合并完成的数据集')
        # 保存合并后的数据集
        self.save_labelme(merge_datasets, parameter, None)

    @staticmethod
    def is_multiple(n, m):
        """
        判断一个数与另一个数之间是否存在倍数关系
        @param n:
        @param m:
        @return:
        """
        if n % m == 0:
            return True
        else:
            return False

    def md5_value_find(self, md5):
        """
        根据图像MD5值查询标注数据集，如果MD5值相同就追加shape
        :param md5:
        :return:返回结果只能有一个封装的数据集，也就是一张图像，针对不同目录有相同MD5值图像的，以最后一次查找为准
        """
        rebuild_merge_data = {}  # 重组数据后的输出目录，以最后一次查找到的目录为准，正常情况下，目录都相同
        rebuild_labelme_info = {}  # 重组labelme_info数据，以最后一次查找的图像文件为准，可以保障图像名称与重组的输出目录保持一致
        md5_find_shape = list()
        for dataset in self.datasets:
            if md5 == dataset.get('md5_value'):  # 如果找到相同的MD5值的 就进行重构
                md5_find_shape.extend(dataset.get('labelme_info').get('shapes'))
                rebuild_labelme_info.update({'version': dataset.get('labelme_info').get('version')})
                rebuild_labelme_info.update({'flags': dataset.get('labelme_info').get('flags')})
                rebuild_labelme_info.update({'shapes': list()})
                rebuild_labelme_info.update({'imagePath': dataset.get('labelme_info').get('imagePath')})
                rebuild_labelme_info.update({'imageData': dataset.get('labelme_info').get('imageData')})
                rebuild_labelme_info.update({'imageHeight': dataset.get('labelme_info').get('imageHeight')})
                rebuild_labelme_info.update({'imageWidth': dataset.get('labelme_info').get('imageWidth')})
                image_dir_parts = Path(dataset.get('image_dir')).parts  # 使用parts获取目录的列表
                labelme_dir_parts = Path(dataset.get('labelme_dir')).parts  # 使用parts获取目录的列表
                new_image_dir = Path(*image_dir_parts[1:])  # 移除第一个目录，即约定的按照标签名称创建的目录，重构新合并的相对目录
                # 移除第一个目录
                new_labelme_dir = Path(*labelme_dir_parts[1:])  # 移除第一个目录，即约定的按照标签名称创建的目录，重构新合并的相对目录
                # 这里需要构建输出路径，输出路径为，重组的路径，不包含类别标签名称的目录，即WindowsPath('car/1/678/999/00.images')路径中，需要把car去掉
                rebuild_json_path = Path(dataset.get('output_dir'), new_labelme_dir, dataset.get('labelme_file'))
                rebuild_merge_data.update({'image_dir': new_image_dir})  # 重构图像相对目录
                rebuild_merge_data.update({'image_file': dataset.get('image_file')})
                rebuild_merge_data.update({'labelme_dir': new_labelme_dir})  # 重构json相对目录
                rebuild_merge_data.update({'labelme_file': dataset.get('labelme_file')})
                rebuild_merge_data.update({'input_dir': dataset.get('input_dir')})
                rebuild_merge_data.update({'output_dir': dataset.get('output_dir')})
                rebuild_merge_data.update({'http_url': dataset.get('http_url')})
                rebuild_merge_data.update({'data_type': dataset.get('data_type')})
                rebuild_merge_data.update({'labelme_info': rebuild_labelme_info})
                rebuild_merge_data.update({'background': dataset.get('background')})
                rebuild_merge_data.update({'full_path': dataset.get('full_path')})
                rebuild_merge_data.update({'json_path': rebuild_json_path})  # 变更为输出路径的json_path
                rebuild_merge_data.update({'original_json_path': dataset.get('original_json_path')})
                rebuild_merge_data.update({'md5_value': dataset.get('md5_value')})
                rebuild_merge_data.update({'relative_path': dataset.get('relative_path')})
                rebuild_merge_data.update({'only_annotation': dataset.get('only_annotation')})
        # 更新标注元素属性
        rebuild_labelme_info.update({'shapes': self.duplicate_removal(md5_find_shape)})
        return rebuild_merge_data  # 根据图像MD5值组合新的合并数据，只返回一张图像封装数据

    @staticmethod
    def make_up_dir(dir_parts):
        """
        重组图像存储目录和json文件存储目录
        自动去除相对路径\\的开始目录，保留其它目录
        :param dir_parts:
        :return:
        """
        try:
            if dir_parts[0] and not dir_parts[0].endswith(':'):
                dir_parts.pop(0)
            new_file_path = '\\'.join(dir_parts)  # 输出去除第一个 \\ 开头的字符串后的文件路径
            return new_file_path
        except Exception as e:
            print(e)
            print(
                "以label标签命名的目录不对或者不存在相同的MD5值的图像（每张图像都唯一存在，无法合并）。1、请检查图像文件元数据是否发生变化。2、检查以标签命名的目录存在其它目录")
            exit()

    @staticmethod
    def duplicate_removal(shape_list):
        """
        对标注shape进行去重
        使用哈希表来实现去重，时间复杂度为 O(n)，空间复杂度为 O(n)
        1、创建一个空字典 seen 用于存储已经出现过的元素。
        2、遍历列表中的每个元素，将其转换为字符串并计算哈希值。
        3、如果哈希值在 seen 中已经存在，则说明该元素已经出现过，直接跳过。
        4、如果哈希值在 seen 中不存在，则将该哈希值加入 seen 中，并将该元素加入结果列表中。
        5、返回结果列表。
        :param shape_list:
        :return:
        """
        seen = {}
        result_find_shape = []
        for shape in shape_list:
            key = str(shape)
            h = hash(key)
            if h not in seen:
                seen[h] = True
                result_find_shape.append(shape)
        return result_find_shape

    def self2coco(self, parameter):
        """
        labelme转coco
        coco子类没有实现,就报错
        """
        raise NotImplementedError("这是一个抽象方法，需要在子类中实现")

    def relation_labelme(self, parameter):
        """
        对标注形状位置进行分离，包含关系打组，抠图生成新的labelme
        :param parameter:
        """
        rebuild_datasets = list()
        print(f'分离矩形框包含的多边形框且自动打组')
        for data in tqdm(self.datasets):
            rebuild_datasets.append(self.separate_shape(data))
        # 保存合并后的数据集
        print(f'保存矩形框包含多边形框且自动分组数据')
        self.save_labelme(rebuild_datasets, parameter, None)

    def separate_shape(self, dataset):
        """
        分离标注形状，并对比矩形框是否包含多边形框
        :param dataset:
        """
        file_path = dataset.get('full_path')
        rectangle_list = list()
        polygon_list = list()
        judge_shape = list()
        if dataset.get('background') is True:  # 如果不是背景就进行自动打组
            if dataset.get('labelme_info').get('shapes'):
                for shape in dataset.get('labelme_info').get('shapes'):
                    if shape.get('shape_type') == 'rectangle':
                        rectangle_list.append(shape)
                    if shape.get('shape_type') == 'polygon':
                        polygon_list.append(shape)
                # 使用 Shapely 库中提供的 Polygon 类，实现标注shape的包含关系
                for poly_index, polygon in enumerate(polygon_list):
                    # print(polygon)
                    # 找到多边形，左上、右上、右下、左下的顺序排列4个顶点
                    poly_sequential_coordinates = self.find_poly_sequential_coordinates(polygon, file_path)
                    # 把多边形跟矩形框逐一比较
                    for rect_index, rectangle in enumerate(rectangle_list):
                        # print(polygon)
                        # 找到矩形框，左上、右上、右下、左下的顺序排列4个角点坐标
                        rect_sequential_coordinates = self.find_rect_sequential_coordinates(rectangle, file_path)
                        # 创建矩形框和多边形对象
                        rect = Polygon(rect_sequential_coordinates)
                        poly = Polygon(poly_sequential_coordinates)
                        # 判断多边形是否与矩形框相交
                        # if poly.intersects(rect):
                        #     # 如果矩形框的group_id没有值，就赋值索引号并且追加到新的列表中。
                        #     if rectangle_list[rect_index]['group_id'] is None:
                        #         # print("判断多边形是否在矩形框内部或边界上")
                        #         polygon_list[poly_index]['group_id'] = rect_index
                        #         rectangle_list[rect_index]['group_id'] = rect_index
                        #         judge_shape.append(polygon)
                        #         judge_shape.append(rectangle)
                        #     else:
                        #         # 如果矩形框的group_id有值，则把多边形的group_id赋值为矩形框的索引值并追加到新列表中
                        #         polygon_list[poly_index]['group_id'] = rect_index
                        #         judge_shape.append(polygon)
                        # if poly.contains(rect):
                        #     print("判断多边形是否包含矩形")
                        if rect.contains(poly):
                            # print("判断矩形是否包含多边形")
                            if rectangle_list[rect_index]['group_id'] is None:
                                # print("判断多边形是否在矩形框内部或边界上")
                                polygon_list[poly_index]['group_id'] = rect_index
                                rectangle_list[rect_index]['group_id'] = rect_index
                                judge_shape.append(polygon)
                                judge_shape.append(rectangle)
                            else:
                                # 如果矩形框的group_id有值，则把多边形的group_id赋值为矩形框的索引值并追加到新列表中
                                polygon_list[poly_index]['group_id'] = rect_index
                                judge_shape.append(polygon)
            # 对列表进行去重
            new_judge_shape = []
            for shape in judge_shape:
                if shape not in new_judge_shape:
                    new_judge_shape.append(shape)
            dataset['labelme_info'].update({'shapes': new_judge_shape})
            # dataset['labelme_info'].update({'shapes': judge_shape})
        # else:
        # print(f'当前图像为背景图像{file_path}')
        return dataset

    @staticmethod
    def find_rect_sequential_coordinates(rectangle, file_path):
        """
        找到矩形框，左上、右上、右下、左下的顺序排列4个顶点
        这种算法同样只适用于矩形框只有水平和垂直两个方向的情况。如果矩形框存在旋转或倾斜的情况，需要使用其他方法来计算四个顶点的坐标。
        :param rectangle:
        :param file_path:
        """
        if len(rectangle['points']) == 2:
            # 先确定左上角和右下角
            x_min = min(rectangle['points'][0][0], rectangle['points'][1][0])
            y_min = min(rectangle['points'][0][1], rectangle['points'][1][1])
            x_max = max(rectangle['points'][0][0], rectangle['points'][1][0])
            y_max = max(rectangle['points'][0][1], rectangle['points'][1][1])
            # 再确定左下角和右上角
            vertices = [
                [x_min, y_min],  # 左上角
                [x_max, y_min],  # 右上角
                [x_max, y_max],  # 右下角
                [x_min, y_max],  # 左下角
            ]
            # 按照左上、右上、右下、左下的顺序排列4个顶点，并返回列表
            return vertices
        else:
            points = rectangle['points']
            print(f'矩形框标注点的数量不对{points}，请核对数据{file_path}')

    @staticmethod
    def find_poly_sequential_coordinates(polygon, file_path):
        """
        找到多边形，左上、右上、右下、左下的顺序排列4个顶点
        这个算法的时间复杂度为 O(n)，其中n 是多边形的点数。
        :param polygon:
        :param file_path:
        """
        if len(polygon.get('points')) == 4:
            # 初始化最左、最右、最上和最下的点为多边形的第一个点
            leftmost, rightmost, topmost, bottommost = polygon.get('points')[0], polygon.get('points')[0], \
                polygon.get('points')[0], polygon.get('points')[0]

            # 遍历多边形的每一个点，并更新最左、最右、最上和最下的点的坐标值
            for point in polygon.get('points'):
                if point[0] < leftmost[0]:
                    leftmost = point
                if point[0] > rightmost[0]:
                    rightmost = point
                if point[1] < topmost[1]:
                    topmost = point
                if point[1] > bottommost[1]:
                    bottommost = point
            return [leftmost, topmost, rightmost, bottommost]
        else:
            points = polygon.get('points')
            print(f'多边形标注点不为4个点{points}，请核对数据{file_path}')

    def intercept_coordinates(self):
        """
        根据矩形框截取图像，并保存矩形框内包含的多边形标注属性
        该功能内部循环嵌套太多，时间复杂度太高，待优化
        """
        print(f'截取标注矩形框图像，并重写矩形框内包含的多边形标注属性')

        for dataset in tqdm(self.datasets):
            # 每张图像迭代时清空列表数据
            # list_of_boxes = []  # 矩形框列表
            # list_of_polygons = []  # 多边形框列表
            # results = []
            # file_path = dataset.get('full_path')
            structure_shapes = defaultdict(list)
            if dataset.get('background') is True:  # 如果不是背景就进行自动打组
                # 根据group_id把矩形框内包含的多边形框进行分组
                for shape in dataset.get('labelme_info').get('shapes'):
                    # 判断两个矩形框标注是否存在交集，以及判断相交区域内是否存在多边形标注。您可以使用 Python 中的几何计算库（如 Shapely）来实现这些任务。Shapely 提供了简单易用的几何对象和方法，可以帮助您进行几何计算。
                    # if shape.get('shape_type') == 'rectangle':
                    #     # 如果是矩形框标注，将坐标转换为 Shapely box 对象
                    #     x_min, y_min = shape.get('points')[0]
                    #     x_max, y_max = shape.get('points')[1]
                    #     list_of_boxes.append(box(x_min, y_min, x_max, y_max))
                    # elif shape.get('shape_type') == 'polygon':
                    #     # 如果是多边形标注，将坐标转换为 Shapely Polygon 对象
                    #     list_of_polygons.append(Polygon(shape.get('points')))
                    if shape.get('group_id') is None and shape.get('shape_type') == 'polygon':  # 避免一辆车不打组的情况，但只要是多边形车牌必须存在打组
                        # 只要组id为空就追加为打组出错的数据集，同时跳过该shape。存在单独一辆车不打组的情况也算错了。
                        self.error_dataset_handle(dataset)
                        print("当前图像存在未分组情况" + dataset.get("full_path"))
                    # 判断矩形框和多边形相交的情况，并对相交的情况分组
                    else:
                        structure_shapes[shape['group_id']].append(shape)
                # # 遍历矩形框列表，判断矩形框之间是否存在交集
                # for i in range(len(list_of_boxes)):
                #     for j in range(i + 1, len(list_of_boxes)):
                #         box1 = list_of_boxes[i]
                #         box2 = list_of_boxes[j]
                #         # 检查两个矩形框是否存在交集
                #         if box1.intersects(box2):
                #             # 获取两个矩形框的相交区域
                #             intersection_area = box1.intersection(box2)
                #             # 判断相交区域内是否存在多边形标注
                #             overlap_with_polygon = any(intersection_area.intersects(polygon) for polygon in list_of_polygons)
                #             # 判断相交区域内是否存在多边形标注
                #             for k, polygon in enumerate(list_of_polygons):
                #                 # 检查多边形是否与相交区域相交
                #                 if intersection_area.intersects(polygon):
                #                     # 获取多边形与相交区域的交集部分
                #                     polygon_intersection = intersection_area.intersection(polygon)
                #                     # 判断多边形交集部分的面积是否大于二分之一的多边形面积
                #                     if polygon_intersection.area >= polygon.area / 2:
                #                         # 记录结果
                #                         results.append((i, j, k))
                #             # 记录结果，该结果是多边形标注只要存在一小部分在相交区域就返回true
                #             # results.append((i, j, overlap_with_polygon))
                # # # 检查矩形框标注之间是否存在交集，以及相交区域内是否存在多边形标注
                # for i, j, overlap_with_polygon in results:
                #     print(f"矩形框标注 {i} 和矩形框标注 {j} 存在交集")
                #     print(f"相交区域内是否存在多边形标注: {overlap_with_polygon}")
                # ***************************************************************
                copy_structure_shapes = copy.deepcopy(structure_shapes)  # 使用copy.deepcopy进行深度拷贝
                # 分组后的列表集合逐一比较，
                for group_id, shapes_list in copy_structure_shapes.items():
                    for other_group_id, other_shapes_list in copy_structure_shapes.items():
                        if other_group_id is None or group_id is None:
                            continue
                        # 通过确保外层循环的索引始终小于内层循环的索引，你可以避免重复比较。这种方法在列表数量较多的情况下也是有效的，因为它只比较不同的组对。
                        if group_id < other_group_id:  # 确保只比较 group_id < other_group_id 的组合，避免重复比较。只对列表中的元素进行独特比较。
                            # 默认列表第一个元素就为矩形框，优先比较是否存在交集，不存在交集的无需继续，判断相交区域内是否存在多边形标注
                            if shapes_list[0].get("shape_type") == other_shapes_list[0].get("shape_type") == "rectangle":
                                # 把矩形框标注，将坐标转换为 Shapely box 对象
                                box1 = box(*shapes_list[0].get("points")[0], *shapes_list[0].get("points")[1])
                                box2 = box(*other_shapes_list[0].get("points")[0], *other_shapes_list[0].get("points")[1])
                                # 检查两个矩形框是否存在交集
                                if box1.intersects(box2):
                                    # 获取两个矩形框的相交区域
                                    intersection_area = box1.intersection(box2)
                                    # 在当前分组中查找多边形标注是否与矩形框相交区域相交
                                    shapes_list_polygon = self.get_shape_to_compare_polygon_in_box(intersection_area, shapes_list)
                                    # 在当前分组中查找多边形标注是否与矩形框相交区域相交
                                    other_shapes_list_polygon = self.get_shape_to_compare_polygon_in_box(intersection_area, other_shapes_list)
                                    # 比较判断查找多边形框的归属于哪一个组，然后追加过去
                                    if shapes_list_polygon:  # 如果在当前分组中找到了，就归属于另一个分组中。因为在当前分组中找到说明本金存在于当前组中，与此对比的另一组必然缺失。
                                        structure_shapes[other_group_id].extend(shapes_list_polygon)
                                    if other_shapes_list_polygon:  # 如果在当前分组中找到了，就归属于另一个分组中。
                                        structure_shapes[group_id].extend(other_shapes_list_polygon)
                            else:
                                # print("分组列表第一个元素不为矩形框标注")
                                # print(dataset.get("full_path"))
                                self.error_dataset_handle(dataset)
                # 截取图像，把矩形框排序，最前面进行遍历
                for shape_key, shapes_value in structure_shapes.items():
                    # 分组数量等于一且是矩形框标注的，没有group_id号的不用截取图像。无需人工检查，跳过
                    if len(shapes_value) == 1:
                        if shapes_value[0].get("shape_type") == "rectangle":
                            # 判断当前矩形框内是否存在多边形，如果存在就不截取
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.save_rectangle_image(shapes_value, dataset)
                        if shapes_value[0].get("shape_type") == "polygon":
                            self.error_dataset_handle(dataset)  # 分组数量等一的，且是多边形标注的，必然标注存在错误。
                    # 分组数量为2，根据排序规则，矩形框第一，多边形第二，如果第一第二都是多边形则标注有问题
                    elif len(shapes_value) == 2:
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == "polygon":  # 国内车牌一辆车一块车牌，香港车一辆车两块车牌
                            self.error_dataset_handle(dataset)
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == "rectangle":  # 如2个元素都是矩形框且没有车牌，则跳过无需追加打组错误
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.save_rectangle_image(shapes_value, dataset)
                        if shapes_value[0].get("shape_type") == "rectangle" and shapes_value[1].get("shape_type") == "polygon":
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.error_dataset_handle(dataset)
                            else:  # 分组的矩形框内包含多边形
                                if self.judge_polygon_whether_box(shapes_value, "group_id") is True:
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, None)  # group_id值都相同，是正确标注截取矩形框标注图像，并保存多边形属性为labelme数据集格式
                                else:
                                    # group_id值存在不同的情况，需要单独保存人工查看，矫正标注问题
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, "please_manually_check_data")
                    elif len(shapes_value) == 3:
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == shapes_value[2].get("shape_type") == "polygon":
                            self.error_dataset_handle(dataset)
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == shapes_value[2].get("shape_type") == "rectangle":
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.save_rectangle_image(shapes_value, dataset)
                        if shapes_value[0].get("shape_type") == "rectangle" and shapes_value[1].get("shape_type") == "polygon" and shapes_value[2].get(
                                "shape_type") == "polygon":
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.error_dataset_handle(dataset)
                            else:  # 分组的矩形框内包含多边形
                                if self.judge_polygon_whether_box(shapes_value, "group_id") is True:
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, None)  # group_id值都相同，是正确标注截取矩形框标注图像，并保存多边形属性为labelme数据集格式
                                else:
                                    # group_id值存在不同的情况，需要单独保存人工查看，矫正标注问题
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, "please_manually_check_data")
                                    # 分组数量等于五的，且group_id值都相同的，必然打组存在错误。or 分组数量等于四的，且group_id值都相同的，必然打组存在错误。或者等于3等于2
                    elif len(shapes_value) == 5:
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == \
                                shapes_value[2].get("shape_type") == shapes_value[3].get("shape_type") == shapes_value[4].get("shape_type") == "polygon":
                            self.error_dataset_handle(dataset)
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == \
                                shapes_value[2].get("shape_type") == shapes_value[3].get("shape_type") == shapes_value[4].get("shape_type") == "rectangle":
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.save_rectangle_image(shapes_value, dataset)
                        if shapes_value[0].get("shape_type") == "rectangle" and shapes_value[1].get("shape_type") \
                                == "polygon" and shapes_value[2].get("shape_type") == "polygon" and \
                                shapes_value[3].get("shape_type") == "polygon" and shapes_value[4].get("shape_type") == "polygon":
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.error_dataset_handle(dataset)
                            else:  # 分组的矩形框内包含多边形
                                if self.judge_polygon_whether_box(shapes_value, "group_id") is True:
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, None)  # group_id值都相同，是正确标注截取矩形框标注图像，并保存多边形属性为labelme数据集格式
                                else:
                                    # group_id值存在不同的情况，需要单独保存人工查看，矫正标注问题
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, "please_manually_check_data")
                    elif len(shapes_value) == 4:
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == \
                                shapes_value[2].get("shape_type") == shapes_value[3].get("shape_type") == "polygon":
                            self.error_dataset_handle(dataset)
                        if shapes_value[0].get("shape_type") == shapes_value[1].get("shape_type") == \
                                shapes_value[2].get("shape_type") == shapes_value[3].get("shape_type") == "rectangle":
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                # self.save_rectangle_image(shapes_value, dataset)
                                continue
                        if shapes_value[0].get("shape_type") == "rectangle" and shapes_value[1].get("shape_type") \
                                == "polygon" and shapes_value[2].get("shape_type") == "polygon" and shapes_value[3].get("shape_type") == "polygon":
                            if self.judge_polygon_whether_box(shapes_value, None) is False:  # 分组的矩形框内不包含多边形
                                self.error_dataset_handle(dataset)
                            else:  # 分组的矩形框内包含多边形
                                if self.judge_polygon_whether_box(shapes_value, "group_id") is True:
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, None)  # group_id值都相同，是正确标注截取矩形框标注图像，并保存多边形属性为labelme数据集格式
                                else:
                                    # group_id值存在不同的情况，需要单独保存人工查看，矫正标注问题
                                    self.cut_out_labelme_image(shape_key, shapes_value, dataset, "please_manually_check_data")
                    elif len(shapes_value) >= 6:
                        self.error_dataset_handle(dataset)
                    # # 多边形都在当前分组矩形框外围，则打组存在错误，不进行抠图截取
                    # elif self.judge_polygon_whether_box(shapes_value, None) is False:
                    #     self.error_dataset_handle(dataset)
                    # else:  # 如下抠图执行的逻辑，必须是正确分组的标注才能够执行，否则抠图会出错。如果上述错误标注检查，所有条件都为 False，执行这个代码块
                    #     # 分组数量为3和2的情况，如果group_id值都相同就正常保存，如果值不同就要单独保存人工查看，矫正标注问题
                    #     if len(shapes_value) == 3 or len(shapes_value) == 2:
                    #         if self.judge_polygon_whether_box(shapes_value, "group_id") is True:
                    #             self.cut_out_labelme_image(shape_key, shapes_value, dataset, None)  # group_id值都相同，是正确标注截取矩形框标注图像，并保存多边形属性为labelme数据集格式
                    #         else:
                    #             self.cut_out_labelme_image(shape_key, shapes_value, dataset, "please_manually_check_data")  # group_id值存在不同的情况，需要单独保存人工查看，矫正标注问题

        if self.check_error_dataset:  # 如果有值才保存，否则会保存出错
            # 保存合并后的数据集
            print(f'保存打组出错数据集，需要人工矫正!!!')
            rebuild_dataset = list()
            for dataset in self.check_error_dataset:
                dataset.update({'output_dir': dataset['group_error_path']})  # 重写保存路径
                new_json_path = os.path.join(dataset.get('group_error_path'), dataset.get('labelme_dir'), dataset.get('labelme_file'))
                dataset.update({'json_path': new_json_path})  # 重写保存路径
                rebuild_dataset.append(dataset)
            self.save_labelme(rebuild_dataset, self.error_output_path, None)

    def intercept_coordinates_optimize(self):
        """
        优化截取车包含车牌为labelme数据集问题，无需打组group_id
        每张图像，划分两个列表，矩形框分一组列表，多边形框分一组列表，就判断矩形框内是否包含多边形，且包含多边形在矩形框内的面积大于三分之二就截取矩形框并写入多边形标注属性。
        不能解决，漏标和错标
        """
        for dataset in tqdm(self.datasets):
            list_of_boxes = []  # 矩形框列表
            list_of_polygons = []  # 多边形框列表
            if dataset.get('background') is True:  # 如果不是背景就进行矩形框和多边形标注分类
                for shape in dataset.get('labelme_info').get('shapes'):
                    if shape.get('shape_type') == 'polygon':
                        list_of_polygons.append(shape)
                    if shape.get('shape_type') == 'rectangle':
                        list_of_boxes.append(shape)

            for shape_key, rectangle_shape in enumerate(list_of_boxes):  # 遍历矩形框列表
                # judging_conditions = False
                polygon_in_rectangle = list()
                # 把矩形框标注，将坐标转换为 Shapely box 对象
                rectangle_shapely = box(*rectangle_shape.get("points")[0], *rectangle_shape.get("points")[1])
                for polygon_shape in list_of_polygons:  # 遍历矩多边形框列表
                    # 把多边形标注，将坐标转换为 Shapely Polygon 对象
                    polygon = Polygon(polygon_shape.get('points'))
                    # 计算多边形与矩形框的交集
                    intersection = rectangle_shapely.intersection(polygon)
                    # 判断交集是否是多边形对象，以及交集面积是否大于矩形框面积的三分之二
                    # if self.compute_intersection(rectangle_shapely, polygon):
                    #     polygon_in_rectangle.append(polygon_shape)
                    #     judging_conditions = True  # 只要存在包含关系就把判断条件设置为true，用于人工查看数据
                    if isinstance(intersection, Polygon) and intersection.area > rectangle_shapely.area * (2 / 3):
                        polygon_in_rectangle.append(polygon_shape)
                        # judging_conditions = True  # 只要存在包含关系就把判断条件设置为true，用于人工查看数据
                    if rectangle_shapely.contains(polygon):  # 判断矩形框是否包含多边形。如果包含则返回 True，否则返回 False。
                        polygon_in_rectangle.append(polygon_shape)
                # 根据矩形框进行截取图像，封装截取对象
                encapsulation_shape = list()
                encapsulation_shape.append(rectangle_shape)  # 矩形框永远排在第一个位置
                encapsulation_shape.extend(polygon_in_rectangle)
                if len(encapsulation_shape) == 1:
                    self.save_rectangle_image(encapsulation_shape, dataset)  # 只截取车的标注
                if len(encapsulation_shape) == 2:
                    self.cut_out_labelme_image(shape_key, encapsulation_shape, dataset, None)
                if len(encapsulation_shape) >= 3:
                    self.cut_out_labelme_image(shape_key, encapsulation_shape, dataset, "please_manually_check_data")  # 人工检查

    @staticmethod
    def compute_intersection(rectangle, polygon):
        """
        确保能够正确地处理多边形和矩形的交集计算。是为了解决如下问题，但实际并没有解决
        F:\ProgramData\Anaconda3\envs\chipeak_cv_data_tool\lib\site-packages\shapely\set_operations.py:133: RuntimeWarning: invalid value encountered in intersection
        @param rectangle:
        @param polygon:
        @return:
        """
        try:
            intersection = rectangle.intersection(polygon)  # 计算多边形与矩形框的交集
            # 交集只包含一个多边形，那么计算该多边形的面积，并判断是否大于等于原多边形 polygon 面积的 2/3。如果是，则返回 True
            if isinstance(intersection, Polygon):
                return intersection.area >= 2 / 3 * polygon.area
            # 交集包含了多个不同的多边形，那么计算所有这些多边形的总面积，并判断是否大于等于原多边形 polygon 面积的 2/3。如果是，则返回 True
            elif isinstance(intersection, MultiPolygon):
                return sum(poly.area for poly in intersection) >= 2 / 3 * polygon.area
            else:
                return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    def save_rectangle_image(self, sorted_list, dataset):
        """
        只截取矩形框，保存相关属性
        @param sorted_list:
        @param dataset:
        """
        for index1, sort in enumerate(sorted_list):
            # rect_x = 0
            # rect_y = 0
            # crop_height = 0
            # crop_width = 0
            # roi = np.empty((10, 10), dtype=float)  # 每次抠图前重新初始化numpy空数组
            # 加载图像
            img = cv2.imread(str(dataset.get('full_path')))
            # 永恒获取左上角的坐标点
            rect_sequential_coordinates = self.find_rect_sequential_coordinates(sort, dataset.get('full_path'))
            # rect_x = rect_sequential_coordinates[0][0]
            # rect_y = rect_sequential_coordinates[0][1]
            # 把矩形框的坐标进行四舍五入后，再次用于计算多边形，比dtype=np.float32精度损失要低
            pts = [[round(x), round(y)] for x, y in sort['points']]
            rect = cv2.boundingRect(np.array(pts))
            if np.any(np.array(rect) < 0):
                # 将负数替换为0
                rebuild_rect = np.maximum(np.array(rect), 0)
                x, y, w, h = rebuild_rect
                # crop_height = h
                # crop_width = w
                roi = img[y:y + h, x:x + w]
            else:
                x, y, w, h = rect
                # crop_height = h
                # crop_width = w
                roi = img[y:y + h, x:x + w]
            obj_path = Path(dataset.get('image_file'))
            rebuild_img_name = obj_path.stem + '_' + str(index1) + obj_path.suffix
            rebuild_img_dir = os.path.join(dataset.get('output_dir'), "background_data", dataset.get('image_dir'))
            rebuild_json_dir = os.path.join(dataset.get('output_dir'), "background_data", dataset.get('labelme_dir'))
            os.makedirs(rebuild_img_dir, exist_ok=True)
            os.makedirs(rebuild_json_dir, exist_ok=True)
            # 重构图像文件路径
            final_image_path = os.path.join(rebuild_img_dir, rebuild_img_name)
            cv2.imwrite(final_image_path, roi)

    def save_rectangle_polygon_image(self, sorted_list, dataset):
        """
        截取一个矩形框下，分组多个多边形的情况
        @param sorted_list:
        @param dataset:
        @return:
        """
        polygon_shape = list()
        rect_x = 0
        rect_y = 0
        crop_height = 0
        crop_width = 0
        roi = np.empty((10, 10), dtype=float)  # 每次抠图前重新初始化numpy空数组
        for index1, sort in enumerate(sorted_list):
            if sort['shape_type'] == 'rectangle':
                # 加载图像
                img = cv2.imread(str(dataset.get('full_path')))
                # 永恒获取左上角的坐标点
                rect_sequential_coordinates = self.find_rect_sequential_coordinates(sort, dataset.get('full_path'))
                rect_x = rect_sequential_coordinates[0][0]
                rect_y = rect_sequential_coordinates[0][1]
                # 把矩形框的坐标进行四舍五入后，再次用于计算多边形，比dtype=np.float32精度损失要低
                pts = [[round(x), round(y)] for x, y in sort['points']]
                # print(pts)
                # rect = cv2.boundingRect(np.array(pts, dtype=np.float32))
                rect = cv2.boundingRect(np.array(pts))
                # print(rect)
                if np.any(np.array(rect) < 0):
                    # 将负数替换为0
                    rebuild_rect = np.maximum(np.array(rect), 0)
                    x, y, w, h = rebuild_rect
                    crop_height = h
                    crop_width = w
                    roi = img[y:y + h, x:x + w]
                    # print(f'截取矩形框时发现，图像标注超出图像边界{file_path}')
                else:
                    x, y, w, h = rect
                    crop_height = h
                    crop_width = w
                    roi = img[y:y + h, x:x + w]
                    # print(rect)
            else:
                polygon_points = self.get_crop_location_and_coords(rect_x, rect_y, sort['points'], dataset.get('full_path'))
                rebuild_shape = {
                    'label': sort['label'],
                    'points': polygon_points,
                    "group_id": sort['group_id'],
                    "shape_type": "polygon",
                    "flags": sort['flags'],
                    "text": sort['text']
                }
                polygon_shape.append(rebuild_shape)
        return polygon_shape, crop_height, crop_width, roi

    def cut_out_labelme_image(self, shape_key, shapes_value, dataset, please_manually_check):
        """
        截取矩形框图像，绘制多边形车牌标注，保存为labelme数据集格式
        @param shape_key:分组唯一标识key
        @param shapes_value:分组标注列表
        @param dataset:labelme数据集封装数据结构体
        @param please_manually_check:手动检查参数
        """
        rebuild_json = {
            "version": "4.5.13",
            "flags": {},
            "shapes": [],
            "imagePath": "",
            "imageData": None,
            "imageHeight": 0,
            "imageWidth": 0
        }
        # polygon_shape_multiplexing = list()
        # crop_height_multiplexing = 0
        # crop_width_multiplexing = 0
        # roi_multiplexing = np.empty((10, 10), dtype=float)  # 每次抠图前重新初始化numpy空数组
        sorted_list = sorted(shapes_value, key=my_sort, reverse=True)  # 对列表进行排序，把矩形框标注排序为首位
        # if cut_car:  # 只扣车的标注
        #     pass
        # else:  # 抠出车和车牌标注
        polygon_shape, crop_height, crop_width, roi = self.save_rectangle_polygon_image(sorted_list, dataset)
        # polygon_shape_multiplexing.extend(polygon_shape)
        # crop_height_multiplexing = crop_height
        # crop_width_multiplexing = crop_width
        # roi_multiplexing = roi
        rebuild_json['shapes'].extend(polygon_shape)
        obj_path = Path(dataset.get('image_file'))
        rebuild_img_name = obj_path.stem + '_' + str(shape_key) + obj_path.suffix
        rebuild_json_name = obj_path.stem + '_' + str(shape_key) + '.json'
        image_path = os.path.join('..', '00.images', rebuild_img_name)
        rebuild_json.update({'imageHeight': crop_height})
        rebuild_json.update({'imagePath': image_path})
        rebuild_json.update({'imageWidth': crop_width})
        rebuild_img_dir = os.path.join(dataset.get('output_dir'), "correct_data", dataset.get('image_dir'))
        rebuild_json_dir = os.path.join(dataset.get('output_dir'), "correct_data", dataset.get('labelme_dir'))
        os.makedirs(rebuild_img_dir, exist_ok=True)
        os.makedirs(rebuild_json_dir, exist_ok=True)
        if please_manually_check is None:  # 正常标注
            # 重构json文件路径
            final_json_path = os.path.join(rebuild_json_dir, rebuild_json_name)
            # 重构图像文件路径
            final_image_path = os.path.join(rebuild_img_dir, rebuild_img_name)
            self.save_cut_images(final_json_path, final_image_path, rebuild_json, roi)
            # with open(final_json_path, "w", encoding='UTF-8', ) as labelme_fp:  # 以写入模式打开这个文件
            #     json.dump(rebuild_json, labelme_fp, indent=2, cls=Encoder)
            # cv2.imwrite(final_image_path, roi)
        else:  # 需要人工核验的标注
            check_image_dir = os.path.join(dataset.get('output_dir'), please_manually_check, dataset.get('image_dir'))
            check_json_dir = os.path.join(dataset.get('output_dir'), please_manually_check, dataset.get('labelme_dir'))
            os.makedirs(check_image_dir, exist_ok=True)
            os.makedirs(check_json_dir, exist_ok=True)
            # 重写json文件
            rebuild_final_json_path = os.path.join(check_json_dir, rebuild_json_name)
            # 保存截取到的图像
            rebuild_final_image_path = os.path.join(check_image_dir, rebuild_img_name)
            self.save_cut_images(rebuild_final_json_path, rebuild_final_image_path, rebuild_json, roi)
            # with open(final_json_path, "w", encoding='UTF-8', ) as labelme_fp:  # 以写入模式打开这个文件
            #     json.dump(rebuild_json, labelme_fp, indent=2, cls=Encoder)
            # cv2.imwrite(final_image_path, roi)

    @staticmethod
    def save_cut_images(json_path, image_path, json_data, image_data):
        """
        保存labelme格式数据集图像文件和json文件
        @param json_path: json文件路径
        @param image_path: 图像文件路径
        @param json_data: json文件数据内容
        @param image_data: 图像文件数据内容
        """
        with open(json_path, "w", encoding='UTF-8', ) as labelme_fp:  # 以写入模式打开这个文件
            json.dump(json_data, labelme_fp, indent=2, cls=Encoder)
        cv2.imwrite(image_path, image_data)

    @staticmethod
    def get_shape_to_compare_polygon_in_box(intersection_area, shape_list):
        """
        判断相交区域内是否存在多边形标注。且多边形交集部分的面积是否大于二分之一的多边形面积。
        @param intersection_area:相交区域
        @param shape_list:分组标注列表
        @return:返回相交的多边形标注列表
        """
        list_of_polygons = []
        # 比较相交区域内是否存在多边形标注，并把其追加到比较对象不存在的一方
        for shape in shape_list:
            if shape.get('shape_type') == 'polygon':
                # 把多边形标注，将坐标转换为 Shapely Polygon 对象
                polygon = Polygon(shape.get('points'))
                # 检查多边形是否与相交区域相交
                if intersection_area.intersects(polygon):
                    # 获取多边形与相交区域的交集部分
                    polygon_intersection = intersection_area.intersection(polygon)
                    # 判断多边形交集部分的面积是否大于二分之一的多边形面积
                    # if polygon_intersection.area >= polygon.area / 2:
                    # 判断多边形交集部分的面积是否大于三分之二的多边形面积
                    if polygon_intersection.area >= polygon.area * 2 / 3:
                        list_of_polygons.append(shape)
        return list_of_polygons

    @staticmethod
    def judge_polygon_whether_box(shapes_value, group_id):
        """
        判断矩形框内是否包含多边形标注
        判断所有分组元素的id是否相同
        判断是否存在多个矩形框标注元素
        @param group_id:自定义字符串判断条件
        @param shapes_value:分组标注列表
        """
        list_of_rectangle = []  # 矩形框列表
        list_of_polygon = []  # 多边形框列表
        list_of_group_id = []  # 打组id列表
        for shape in shapes_value:
            if shape.get('shape_type') == 'rectangle':
                # 把矩形框标注，将坐标转换为 Shapely box 对象
                rectangle = box(*shape.get("points")[0], *shape.get("points")[1])
                list_of_rectangle.append(rectangle)
            if shape.get('shape_type') == 'polygon':
                # 把多边形标注，将坐标转换为 Shapely Polygon 对象
                polygon = Polygon(shape.get('points'))
                list_of_polygon.append(polygon)
            if shape.get('group_id') is not None:
                list_of_group_id.append(shape.get('group_id'))
        if len(list_of_polygon) == 0:  # 如果两个shape,都是多边形，返回false
            return False
        if group_id is not None:
            # 判断列表中的所有元素是否都相同，所有元素都相同，结果将是 True，否则是 False
            return all(element == list_of_group_id[0] for element in list_of_group_id)
        else:
            # 使用 rectangle.contains(polygon) 判断矩形框是否包含多边形。如果包含则返回 True，否则返回 False。
            for polygon in list_of_polygon:
                return list_of_rectangle[0].contains(polygon)

    @staticmethod
    def get_crop_location_and_coords(img_width, img_height, coords, file_path):
        """
        计算多边形位置，在截取的矩形框的位置
        :param img_width: 矩形框宽度
        :param img_height: 矩形框高度
        :param coords: 标注坐标列表
        :param file_path: 图片路径
        :return: 截取区域在原图中的坐标位置，以及在截图中各标注坐标的位置
        """
        crop_coords = []
        for (x0, y0) in coords:
            x = x0 - img_width
            y = y0 - img_height
            crop_coords.append([x, y])
        # if any(num < 0 for sublist in crop_coords for num in sublist):
        #     print(file_path)
        #     print("列表中存在负数")
        # if not crop_coords:
        #     print(file_path)
        return crop_coords

    def duplicate_images(self):
        """
        labelme数据集去重处理
        """
        md5_list = list()
        del_num = 0
        print(f'处理删除重复的图片及json文件')
        for index, repeat_data in tqdm(enumerate(reversed(self.datasets))):
            if repeat_data.get('md5_value') not in md5_list:  # 如果md5值重复直接删除元素
                md5_list.append(repeat_data.get('md5_value'))
            else:
                del_num += 1
                try:
                    os.remove(repeat_data.get('full_path'))
                except Exception as e:
                    print(e)
                    image_path = repeat_data.get('full_path')
                    print(f'图像文件删除失败{image_path}')
                try:
                    os.remove(repeat_data.get('json_path'))
                except Exception as e:
                    print(e)
                    json_path = repeat_data.get('json_path')
                    print(f'json文件删除失败{json_path}')
        print(
            f'去重前文件数量有{len(self.datasets)}，去重后文件数量有{len(self.datasets) - del_num}，删除重复的文件有{del_num}')

    def check_group_labelme(self, parameter):
        """
        labelme数据集检查功能实现，包含标注多边形点数错误、标注分组错误、标注越界错误、标注flags属性错误、
        :param parameter:
        """
        if isinstance(parameter.judging_letter, list):
            for dataset in tqdm(self.datasets):
                if dataset.get('background') is True:
                    for shape in dataset.get('labelme_info').get('shapes'):
                        if shape.get('text'):
                            for character in shape.get('text'):
                                if character in parameter.judging_letter:
                                    self.error_dataset_handle(dataset)
        if isinstance(parameter.judging_group_id_num, bool):
            for dataset in tqdm(self.datasets):
                car_group_id = list()
                plate_group_id = list()
                if dataset.get('background') is True:
                    for shape in dataset.get('labelme_info').get('shapes'):
                        if shape.get('shape_type') == 'rectangle':
                            if shape.get('group_id') is not None:
                                car_group_id.append(shape.get('group_id'))
                        if shape.get('shape_type') == 'polygon':
                            if shape.get('group_id') is not None:
                                plate_group_id.append(shape.get('group_id'))
                    if len(plate_group_id) < len(car_group_id):
                        self.error_dataset_handle(dataset)
        if isinstance(parameter.judging_label, str):
            for dataset in tqdm(self.datasets):
                one_image_group_id = list()
                if dataset.get('background') is True:
                    for shape in dataset.get('labelme_info').get('shapes'):
                        # 根据填写的标签内容进行逻辑唯一判断，筛选打组出错的数据。车牌没有打组出错唯一，车打组的值相同出错唯一。
                        if parameter.judging_label == shape.get('label'):
                            if shape.get('shape_type') == 'rectangle':  # 车牌标注都是多边形的，只要group_id为空就追加
                                if shape.get('group_id') is None:
                                    continue
                                if shape.get('group_id') not in one_image_group_id:
                                    one_image_group_id.append(shape.get('group_id'))
                                else:
                                    self.error_dataset_handle(dataset)
                            if shape.get('shape_type') == 'polygon':  # 车牌标注都是多边形的，只要group_id为空就追加
                                if shape.get('group_id') is None:
                                    self.error_dataset_handle(dataset)
        if isinstance(parameter.judging_polygon, int):  # 检查多边形点是否超出5个点
            print(f'多边形标注的点是否超出预期数量，预期为4个点，超出则人工矫正')
            for dataset in tqdm(self.datasets):
                if dataset.get('background') is True:
                    for shape in dataset.get('labelme_info').get('shapes'):
                        if shape.get('shape_type') == 'polygon':
                            if len(shape.get('points')) != parameter.judging_polygon:
                                self.error_dataset_handle(dataset)
        if isinstance(parameter.judging_group, int):
            print(f'对标注元素进行分组处理，并判断分组标注元素数量，是否符合判断条件预期')
            for dataset in tqdm(self.datasets):
                group_id_list = defaultdict(list)
                if dataset.get('background') is True:
                    for shape in dataset.get('labelme_info').get('shapes'):
                        group_id_list[shape['group_id']].append(shape)
                    # 判断分组标注元素数量，是否符合预测判断条件预期
                    for group_shape_key, group_shape_value in group_id_list.items():
                        if len(group_shape_value) != parameter.judging_group:
                            # 如果同一张图像分组出现多次错误，只追加一次dataset
                            self.error_dataset_handle(dataset)
        if isinstance(parameter.judging_flags, dict):
            print(f'对标注flags属性进行检查，比如检查车牌颜色、单双层字符，是否，漏勾选。complete被勾选后，车牌号是否录入')
            for dataset in tqdm(self.datasets):
                file_path = dataset.get('full_path')
                if dataset.get('background') is True:
                    for shape in dataset.get('labelme_info').get('shapes'):
                        colour = list()
                        single_double = list()
                        complete_incomplete = list()
                        if shape.get('flags'):
                            # 车牌颜色是否需要勾选，勾选则跳过，否则人工检查。颜色包含yellow_green、yellow、blue、green、white、black
                            if shape.get('flags').get('yellow_green') or shape.get('flags').get('yellow') \
                                    or shape.get('flags').get('blue') or shape.get('flags').get('green') or \
                                    shape.get('flags').get('white') or shape.get('flags').get('black') or \
                                    shape.get('flags').get('other'):
                                colour.append(shape.get('flags').get('yellow_green'))
                                colour.append(shape.get('flags').get('yellow'))
                                colour.append(shape.get('flags').get('blue'))
                                colour.append(shape.get('flags').get('green'))
                                colour.append(shape.get('flags').get('white'))
                                colour.append(shape.get('flags').get('black'))
                                colour.append(shape.get('flags').get('other'))
                            else:
                                print(f'车牌颜色未勾选{file_path}')
                                self.error_dataset_handle(dataset)
                            # 判断单双层字符是否已经勾选，勾选则跳过，否则需要人工检查
                            if shape.get('flags').get('single') or shape.get('flags').get('double'):
                                single_double.append(shape.get('flags').get('single'))
                                single_double.append(shape.get('flags').get('double'))
                            else:
                                print(f'车牌单双层字符未勾选{file_path}')
                                self.error_dataset_handle(dataset)
                            # 车牌完整性检查，勾选后如果没有填写车牌，就让人工检查
                            if shape.get('flags').get('complete') or shape.get('flags').get('incomplete'):
                                complete_incomplete.append(shape.get('flags').get('complete'))
                                complete_incomplete.append(shape.get('flags').get('incomplete'))
                            else:
                                print(f'车牌完整性与不完整性未勾选{file_path}')
                                self.error_dataset_handle(dataset)
                        if colour.count(True) > 1 or single_double.count(True) > 1 or complete_incomplete.count(True) > 1:
                            self.error_dataset_handle(dataset)
        if isinstance(parameter.judging_cross_the_border, str):
            print(f'检查标注坐标位置，是否超越原始图像宽高边界')
            for dataset in tqdm(self.datasets):
                if dataset.get('background') is True:
                    for shape in dataset.get('labelme_info').get('shapes'):
                        self.rectangle_cross_the_border(shape, dataset, parameter.automatic_correction)
        if self.check_error_dataset:  # 如果有值才保存，否则会保存出错
            # 保存合并后的数据集
            print(f'保存出错数据集，需要人工矫正')
            self.save_labelme(self.check_error_dataset, self.error_output_path, None)

    def sort_correct_labelme(self, parameter):
        """
        通过坐标点排序后，抠出车牌，并对倾斜的车牌进行矫正
        也可以对原始标注进行截取
        这里写车牌图像，没有异步非阻塞高并发
        :param parameter:
        """
        print(f'更新多边形标注坐标的排序顺序')
        for dataset in tqdm(self.datasets):
            if dataset.get('background') is True:
                for shape in dataset.get('labelme_info').get('shapes'):
                    if shape.get('shape_type') == 'polygon':
                        if parameter.function == 'correct':
                            if shape.get('text'):  # 有车牌的才进行截取图像并矫正车牌
                                if shape.get('flags').get('double'):  # 双层车牌
                                    crop_img = self.correct_shape_cutout(shape, dataset.get('full_path'))
                                    if crop_img is None:
                                        continue
                                    self.save_poly_cut_img(crop_img, dataset, shape, 'double')
                                else:  # 单层车牌
                                    crop_img = self.correct_shape_cutout(shape, dataset.get('full_path'))
                                    if crop_img is None:
                                        continue
                                    self.save_poly_cut_img(crop_img, dataset, shape, 'single')
                        if parameter.function == 'original':
                            if shape.get('text'):  # 有车牌的才进行截取图像
                                if shape.get('flags').get('double'):  # 双层车牌
                                    crop_img = self.original_shape_cutout(shape, dataset.get('full_path'))
                                    if crop_img is None:
                                        continue
                                    self.save_poly_cut_img(crop_img, dataset, shape, 'double')
                                else:  # 单层车牌
                                    crop_img = self.original_shape_cutout(shape, dataset.get('full_path'))
                                    if crop_img is None:
                                        continue
                                    self.save_poly_cut_img(crop_img, dataset, shape, 'single')

    def error_dataset_handle(self, dataset):
        """
        判断追加的封装数据是否重复，如果重复就不继续追加
        :param dataset:
        """
        # 如果同一张图像分组出现多次错误，只追加一次dataset
        if dataset not in self.check_error_dataset:
            self.error_output_path = dataset.get('group_error_path')
            self.check_error_dataset.append(dataset)

    def rectangle_cross_the_border(self, bbox, dataset, automatic_correction):
        """
        标注坐标超越原始图像边界逻辑实现
        :param bbox:
        :param dataset:
        :param automatic_correction:自动矫正越界标注参数
        :return:
        """
        w = dataset.get('image_width')
        h = dataset.get('image_height')
        self.error_image_path = dataset.get('full_path')
        if isinstance(bbox, list):
            x1 = bbox[0][0]
            y1 = bbox[0][1]
            x2 = bbox[1][0]
            y2 = bbox[1][1]
            # 只针对坐标点越界的矩形进行处理,多边形会转为矩形框
            if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x1 > w or y1 > h or x2 > w or y2 > h:
                return True
        if isinstance(bbox, dict):
            if bbox.get('shape_type') == 'rectangle':
                if len(bbox.get('points')) == 2:
                    x1 = bbox.get('points')[0][0]
                    y1 = bbox.get('points')[0][1]
                    x2 = bbox.get('points')[1][0]
                    y2 = bbox.get('points')[1][1]
                    if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x1 > w or y1 > h or x2 > w or y2 > h:
                        if automatic_correction:  # 自动矫正越界标注形状
                            clamp_x1 = np.clip(x1, 0, w)
                            clamp_y1 = np.clip(y1, 0, h)
                            clamp_x2 = np.clip(x2, 0, w)
                            clamp_y2 = np.clip(y2, 0, h)
                            # 替换
                            bbox.get('points')[0][0] = clamp_x1
                            bbox.get('points')[0][1] = clamp_y1
                            bbox.get('points')[1][0] = clamp_x2
                            bbox.get('points')[1][1] = clamp_y2
                            self.output_dir = dataset.get('output_dir')
                            self.automatic_correction.append(dataset)
                        else:
                            print(f'标注的矩形框已经超越图像边界{self.error_image_path}')
                            self.error_dataset_handle(dataset)
                else:
                    print(f'标注的矩形框坐标点不对，保存到错误数据集')
                    self.error_dataset_handle(dataset)
            if bbox.get('shape_type') == 'polygon':
                if len(bbox.get('points')) == 4:
                    x1 = bbox.get('points')[0][0]
                    y1 = bbox.get('points')[0][1]
                    x2 = bbox.get('points')[1][0]
                    y2 = bbox.get('points')[1][1]
                    x3 = bbox.get('points')[2][0]
                    y3 = bbox.get('points')[2][1]
                    x4 = bbox.get('points')[3][0]
                    y4 = bbox.get('points')[3][1]
                    # 所有点的坐标小于宽高，代表图像左边和顶边越界。所以坐标点大于宽高，代表图像右边和底边越界
                    if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x3 < 0 or y3 < 0 or x4 < 0 or y4 < 0 or \
                            x1 > w or y1 > h or x2 > w or y2 > h or x3 > w or y3 > h or x4 > w or y4 > h:
                        if automatic_correction:  # 自动矫正越界标注形状
                            if (x1 < 0 and x2 < 0 and x3 < 0 and x4 < 0) or (y1 < 0 and y2 < 0 and y3 < 0 and y4 < 0) or \
                                    (x1 > w and x2 > w and x3 > w and x4 > w) or (y1 > h and y2 > h and y3 > h and y4 > h):
                                # 删除为负数的shape标注，然后重写
                                lst = list(filter(lambda x: x != bbox, dataset.get('labelme_info').get('shapes')))
                                # 清空列表
                                dataset.get('labelme_info').get('shapes').clear()
                                # 追加未删除的元素
                                dataset.get('labelme_info').get('shapes').extend(lst)
                                # 追加到自动矫正列表，进行重写json
                                self.automatic_correction.append(dataset)
                            else:
                                # np.clip(a, a_min, a_max, out=None) 接收三个参数.np.clip() 会将数组 a 中所有大于 a_max 的元素截断为 a_max，同时将所有小于 a_min 的元素截断为 a_min
                                clamp_x1 = np.clip(x1, 0, w)
                                clamp_y1 = np.clip(y1, 0, h)
                                clamp_x2 = np.clip(x2, 0, w)
                                clamp_y2 = np.clip(y2, 0, h)
                                clamp_x3 = np.clip(x3, 0, w)
                                clamp_y3 = np.clip(y3, 0, h)
                                clamp_x4 = np.clip(x4, 0, w)
                                clamp_y4 = np.clip(y4, 0, h)
                                # 替换
                                bbox.get('points')[0][0] = clamp_x1
                                bbox.get('points')[0][1] = clamp_y1
                                bbox.get('points')[1][0] = clamp_x2
                                bbox.get('points')[1][1] = clamp_y2
                                bbox.get('points')[2][0] = clamp_x3
                                bbox.get('points')[2][1] = clamp_y3
                                bbox.get('points')[3][0] = clamp_x4
                                bbox.get('points')[3][1] = clamp_y4
                                self.output_dir = dataset.get('output_dir')
                                self.automatic_correction.append(dataset)
                        else:
                            if (x1 < 0 and x2 < 0 and x3 < 0 and x4 < 0) or (y1 < 0 and y2 < 0 and y3 < 0 and y4 < 0) or \
                                    (x1 > w and x2 > w and x3 > w and x4 > w) or (y1 > h and y2 > h and y3 > h and y4 > h):
                                print(f'标注的多边形框已经超越图像边界，人工打组出错{self.error_image_path}')
                                self.error_dataset_handle(dataset)
                else:
                    print(f'标注的多边形坐标点不为4个，保存到错误数据集')
                    self.error_dataset_handle(dataset)

    # def correct_shape_cutout(self, shape, image_path):
    #     points = self.sort_lmks(np.array(shape['points']), image_path)  # 把传入的列表坐标转成numpy，然后进行排序，左上、右上、右下、左下的顺序排列4个顶点
    #     # 读取原始图像
    #     img = cv2.imread(image_path)
    #     xmax, ymax = np.max(points, axis=0)
    #     point_max = np.array([xmax, ymax])
    #     w = int(abs(points[0][0] - point_max[0]))
    #     h = int(abs(points[0][1] - point_max[1]))
    #     # 获取新坐标点
    #     left_top = points[0]
    #     right_top = [points[0][0] + w, points[0][1] + 0]
    #     right_down = [points[0][0] + w, points[0][1] + h]
    #     left_down = [points[0][0] + 0, points[0][1] + h]
    #
    #     new_points = np.array([left_top, right_top, right_down, left_down], dtype=np.float32)
    #     points = points.astype(np.float32)
    #     # 透视变换
    #     mat = cv2.getPerspectiveTransform(points, new_points)
    #     plate_img = cv2.warpPerspective(img, mat, (img.shape[1], img.shape[0]))[int(points[0][1]):int(points[0][1] + h),
    #                 int(points[0][0]):int(points[0][0] + w), :]
    #     return plate_img

    @staticmethod
    def imread_unicode(path):
        # 这个方法适用于所有中文路径、特殊符号路径。
        try:
            stream = np.fromfile(path, dtype=np.uint8)
            img = cv2.imdecode(stream, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"⚠️ 解码失败: {path} 原因: {e}")
            return None

    def correct_shape_cutout(self, shape, image_path):
        try:
            # from paddleocr import PaddleOCR
            # from paddleocr.tools.infer.predict_cls import TextClassifier
            # 初始化 OCR（启用自动倾斜校正 cls=True）
            # ocr = PaddleOCR(use_angle_cls=True, lang='ch', det=False, rec=False, cls=True)
            # C:\Users\jk\.paddleocr\whl\cls\ch_ppocr_mobile_v2.0_cls_infer
            # angle_corrector = TextClassifier("C:\Users\jk\.paddleocr\whl\cls\ch_ppocr_mobile_v2.0_cls_infer")
            # img = self.imread_unicode(image_path)
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"图像读取失败：{image_path}")

            if len(shape['points']) != 4:
                raise ValueError(f"⚠️ 标注点数错误，不为4点：{shape['points']}")
            # 透视函数
            plate_img = self.correct_plate_perspective(shape['points'], img)

            # 使用 paddleocr 的 angle classifier 对 plate_img 进行矫正
            # cls_results, cls_img_list = ocr.cls.cls_batch([plate_img])
            # # 得到矫正后的图像
            # corrected_img = cls_img_list[0]
            # # 显示原始 vs 矫正
            # cv2.imshow("原始车牌", plate_img)
            # cv2.imshow("矫正后车牌", corrected_img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            return plate_img
        except Exception as e:
            print(f"⚠️ 跳过图像: {e}")
            return None

    # def correct_shape_cutout(self, shape, image_path):
    #     # points = self.sort_lmks(np.array(shape['points']), image_path)  # 确保是左上 -> 右上 -> 右下 -> 左下 顺序
    #     points = self.correct_plate_perspective(shape['points'], image_path)
    #     points = points.astype(np.float32)
    #
    #     # 计算宽高
    #     width_top = np.linalg.norm(points[0] - points[1])
    #     width_bottom = np.linalg.norm(points[3] - points[2])
    #     height_left = np.linalg.norm(points[0] - points[3])
    #     height_right = np.linalg.norm(points[1] - points[2])
    #
    #     width = int(max(width_top, width_bottom))
    #     height = int(max(height_left, height_right))
    #
    #     # 目标矩形四个点（从新图像左上角开始）
    #     new_points = np.array([
    #         [0, 0],
    #         [width - 1, 0],
    #         [width - 1, height - 1],
    #         [0, height - 1]
    #     ], dtype=np.float32)
    #
    #     try:
    #         # 加载图像并检查
    #         img = cv2.imread(image_path)
    #         if img is None:
    #             raise ValueError(f"图像读取失败：{image_path}")
    #         else:
    #             # 获取透视变换矩阵
    #             mat = cv2.getPerspectiveTransform(points, new_points)
    #             # 应用透视变换，输出新尺寸的车牌图像
    #             plate_img = cv2.warpPerspective(img, mat, (width, height))
    #             return plate_img
    #     except ValueError as e:
    #         print(f"跳过图像: {e}")

    def correct_plate_perspective(self, points, image):
        """
        image: OpenCV 图像
        points: 原图中车牌的 4 个多边形点
        返回：矫正后的车牌图像
        """
        pts = np.array(points, dtype="float32")
        rect = self.order_points_clockwise(pts)

        # 计算目标宽高
        (tl, tr, br, bl) = rect
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = int(max(widthA, widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = int(max(heightA, heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        # 执行透视变换
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped

    def order_points_clockwise(self, pts):
        # 4个点，按左上、右上、右下、左下排序
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # 左上
        rect[2] = pts[np.argmax(s)]  # 右下

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # 右上
        rect[3] = pts[np.argmax(diff)]  # 左下

        return rect

    # def sort_lmks(self, landmarks, file_path):
    #     """
    #     多边形标注排序，左上、右上、右下、左下的顺序排列
    #     :return:
    #     @param landmarks:
    #     @param file_path:
    #     """
    #     assert len(landmarks) == 4
    #     x = list(copy.copy(landmarks[:, 0]))
    #     y = list(copy.copy(landmarks[:, 1]))
    #     points = landmarks
    #     x.sort()
    #     y.sort()
    #     other = list()
    #     l_t = np.empty(shape=0)
    #     if abs(x[0] - x[1]) < abs(np.mean(x[:2]) - np.mean(x[2:])) and abs(x[2] - x[3]) < abs(np.mean(x[:2]) - np.mean(x[2:])):
    #         l_t, other = self.sort_x(np.array(points).reshape(-1, 2), x)
    #     elif abs(y[0] - y[1]) < abs(np.mean(y[:2]) - np.mean(y[2:])) and abs(y[2] - y[3]) < abs(np.mean(y[:2]) - np.mean(y[2:])):
    #         l_t, other = self.sort_y(np.array(points).reshape(-1, 2), y)
    #     else:
    #         print(f'梯形多边形坐标{landmarks},{file_path}')
    #         return None  # 多边形坐标不转，返回空让其报错后跳过
    #     cos_key = lambda points_distance: (points_distance[0] - min(x)) / (np.sqrt((points_distance[0] - min(x)) ** 2 + (points_distance[1] - min(y)) ** 2))
    #     other.sort(key=cos_key, reverse=True)
    #     other.insert(0, l_t)
    #     lmkds = np.array(other)
    #     return lmkds

    @staticmethod
    def sort_y(points, y):
        l_t = points[np.isin(points[:, 1], np.array(y[:2]))]
        l_t = l_t[np.where(l_t[:, 0] == np.min(l_t[:, 0]))]
        l_t = np.squeeze(l_t)
        return l_t, [point for point in points if (point != l_t).any()]

    @staticmethod
    def sort_x(points, x):
        l_t = points[np.isin(points[:, 0], np.array(x[:2]))]
        l_t = l_t[np.where(l_t[:, 1] == np.min(l_t[:, 1]))]
        l_t = np.squeeze(l_t)
        return l_t, [point for point in points if (point != l_t).any()]

    @staticmethod
    def original_shape_cutout(shape, image_path):
        """
        直接根据多边形坐标进行截取，不做矫正，只填写黑边
        :param shape:
        :param image_path:
        :return:
        """
        coordinates = list()
        img = cv2.imread(image_path)
        points = np.array(shape['points'])
        a = points[0]
        b = points[1]
        c = points[2]
        d = points[3]
        bbox = [int(np.min(points[:, 0])), int(np.min(points[:, 1])), int(np.max(points[:, 0])),
                int(np.max(points[:, 1]))]
        coordinate = [[[int(a[0]), int(a[1])], [int(b[0]), int(b[1])], [int(c[0]), int(c[1])], [int(d[0]), int(d[1])]]]
        coordinates.append(np.array(coordinate))
        # 抠出车牌
        mask = np.zeros(img.shape[:2], dtype=np.int8)
        mask = cv2.fillPoly(mask, coordinates, 255)
        bbox_mask = mask
        bbox_mask = bbox_mask.astype(np.bool_)
        temp_img = copy.deepcopy(img)
        for i in range(3):
            temp_img[:, :, i] *= bbox_mask
        crop_img = temp_img[bbox[1]:bbox[3], bbox[0]:bbox[2], :]
        return crop_img

    @staticmethod
    def save_poly_cut_img(crop_img, dataset, shape, single_double):
        """
        保存多边形截取图像
        :param crop_img:
        :param dataset:
        :param shape:
        :param single_double:单双车牌传参
        """
        obj = Path(dataset.get('full_path'))
        file_name = obj.stem + '_' + shape.get('text') + obj.suffix
        save_dir = os.path.join(dataset.get('output_dir'), single_double, file_name)
        os.makedirs(os.path.dirname(save_dir), exist_ok=True)
        cv2.imwrite(save_dir, crop_img)

    def cross_boundary_correction(self, parameter):
        print(f'程序自动矫正，标注形状超越图像边界情况')
        for dataset in tqdm(self.datasets):
            if dataset.get('background') is True:
                for shape in dataset.get('labelme_info').get('shapes'):
                    if parameter.automatic_correction:  # 参数为真，就进行处理，就矫正
                        self.rectangle_cross_the_border(shape, dataset, parameter.automatic_correction)
                    else:  # 参数为假，就进行筛选打组出错的抠图数据，把空白区域的车牌数据筛选出来
                        self.rectangle_cross_the_border(shape, dataset, parameter.automatic_correction)
        if self.check_error_dataset:  # 如果有值才保存，否则会保存出错
            # 保存合并后的数据集
            print(f'保存出错数据集，需要人工矫正')
            self.save_labelme(self.check_error_dataset, self.error_output_path, None)
        else:
            print(f'保存标注超越图像边界，矫正后的数据')
            self.save_labelme(self.automatic_correction, self.output_dir, None)

    def hanzi_to_pinyin(self):
        print(f'汉字转拼音逻辑实现开始')
        for dataset in tqdm(self.datasets):
            print(dataset)
            dataset.get('full_path')

    def labelme_rectangle_merge(self, parameter, model_dataset_info):
        # 先删除人工标注的矩形框
        original_dataset_info = self.del_label(parameter.del_label)
        # 根据MD5值，确定人工标注与模型预测的对应关系
        merged_list = []
        if len(model_dataset_info) == len(original_dataset_info):
            find_dict = {}
            for model_dataset in model_dataset_info:
                md5_find = list()
                md5_find.append(model_dataset)
                for original_dataset in original_dataset_info:
                    if model_dataset['md5_value'] == original_dataset['md5_value']:
                        md5_find.append(original_dataset)
                find_dict.update({model_dataset['md5_value']: md5_find})
            # 对建立好人工标注与模型预测的数据进行处理
            for key, merged_data in find_dict.items():
                merged_shapes = list()
                merged_dict = {}
                labelme_info_dict = {}
                for model_dataset in merged_data:
                    merged_shapes.extend(model_dataset.get('labelme_info').get('shapes'))
                    labelme_info_dict.update({
                        'version': model_dataset['labelme_info']['version'],
                        'flags': model_dataset['labelme_info']['flags'],
                        'shapes': [],
                        'imagePath': model_dataset['labelme_info']['imagePath'],
                        'imageData': model_dataset['labelme_info']['imageData'],
                        'imageHeight': model_dataset['labelme_info']['imageHeight'],
                        'imageWidth': model_dataset['labelme_info']['imageWidth']
                    })
                    # 新建一个包含合并后列表的字典
                    merged_dict.update({
                        'image_dir': model_dataset['image_dir'],
                        'image_file': model_dataset['image_file'],
                        'image_width': model_dataset['image_width'],
                        'image_height': model_dataset['image_height'],
                        'labelme_dir': model_dataset['labelme_dir'],
                        'labelme_file': model_dataset['labelme_file'],
                        'input_dir': model_dataset['input_dir'],
                        'output_dir': model_dataset['output_dir'],
                        'group_error_path': model_dataset['group_error_path'],
                        'out_of_bounds_path': model_dataset['out_of_bounds_path'],
                        'error_path': model_dataset['error_path'],
                        'http_url': model_dataset['http_url'],
                        'point_number': model_dataset['point_number'],
                        'data_type': model_dataset['data_type'],
                        'labelme_info': None,  # 主要是合并这里的数据
                        'background': model_dataset['background'],
                        'full_path': model_dataset['full_path'],
                        'json_path': model_dataset['json_path'],
                        'md5_value': model_dataset['md5_value'],
                        'relative_path': model_dataset['relative_path'],
                        'only_annotation': model_dataset['only_annotation']
                    })
                # 对merged_shapes列表进行去重操作
                list_unique = []
                for shape in merged_shapes:
                    if shape not in list_unique:
                        list_unique.append(shape)
                labelme_info_dict['shapes'] = list_unique
                merged_dict['labelme_info'] = labelme_info_dict
                merged_list.append(merged_dict)
        else:
            print(f'模型预测的图片数量{len(model_dataset_info)}与人工标注的图片数量{len(original_dataset_info)}，不相等,请核对labelme数据集')
        # 保存处理数据结果
        self.save_labelme(merged_list, self.output_dir, None)

    def model_to_iou(self, model_dataset, parameter):
        """
        标注数据集与模型预测数据集进行IOU比较，计算出，漏检、误检、检出
        @param parameter:
        @param model_dataset:
        """
        mark_positive = 0  # 标注正样本
        model_positive = 0  # 预测正样本
        negative_sample = 0  # 背景图像
        error_check = 0  # 误检出
        leak_check = 0  # 漏检出
        right_check = 0  # 正确检出
        leak_list = list()
        right_list = list()
        error_check_list = list()  # 挑选标注误检
        leak_check_list = list()  # 挑选标注漏检
        # 同时遍历两个列表，进行比较计算
        for mark_data, model_data in zip(self.datasets, model_dataset):
            # print(mark_data)
            # print(model_data)
            if mark_data.get('md5_value') == model_data.get('md5_value') and len(self.datasets) == len(model_dataset):
                # 标注正样本数量统计
                if mark_data.get('background') is True:
                    mark_positive += 1
                # 预测正样本数量统计
                if model_data.get('background') is True:
                    model_positive += 1
                # 同时为背景的情况，背景加1
                if mark_data.get('background') is False and model_data.get('background') is False:
                    negative_sample += 1
                # 标注有，预测没有，漏检出加1
                if mark_data.get('background') is True and model_data.get('background') is False:
                    leak_check += 1
                    leak_list.append(model_data)  # 追加模型预测漏检数据
                    leak_check_list.append(model_data)
                # 标注没有，预测有，误检出加1
                if mark_data.get('background') is False and model_data.get('background') is True:
                    error_check += 1
                    error_check_list.append(mark_data)
                # 标注有，预测有，漏检出、误检出、正确检测都可能存在
                if mark_data.get('background') is True and model_data.get('background') is True:
                    # 判断误检出，优先遍历预测的矩形框。预测的矩形框只要存在一个与标注的矩形框iou小于0.8就属于误检出
                    error_detection = self.shapes_list_data(model_data.get('labelme_info').get('shapes'), mark_data.get('labelme_info').get('shapes'),
                                                            parameter.threshold, model_data.get('image_width'), model_data.get('image_height'))
                    if error_detection:
                        error_check += 1
                        error_check_list.append(mark_data)
                    # 判断漏检出，优先遍历标注的矩形框。标注的一定是对的，如果预测的与标注的iou小于0.8就属于漏检
                    leak_detection = self.shapes_list_data(mark_data.get('labelme_info').get('shapes'), model_data.get('labelme_info').get('shapes'),
                                                           parameter.threshold, model_data.get('image_width'), model_data.get('image_height'))
                    if leak_detection or error_detection:
                        leak_check += 1
                        leak_list.append(model_data)  # 追加模型预测漏检数据
                        leak_check_list.append(mark_data)
                    if error_detection is False and leak_detection is False:  # 如果既不是误检出，也不是漏检出，则判断为正确检出
                        right_check += 1
                        right_list.append(model_data)  # 追加模型预测正确检出数据
            else:
                mark_data_check = mark_data.get('full_path')
                model_data_check = model_data.get('full_path')
                print(f'当前计算IOU文件MD5值不同或文件数量未保持一致，请核对标注数据集与模型预测数据集')
                print(f'标注数据集路径为：{mark_data_check}')
                print(f'模型预测数据集路径为：{model_data_check}')
                print(f'请把标注的图像覆盖到模型预测结果中，或者模型重新预测')
                exit()
        # 计算并打印结果
        # 图像精确率=right_check/model_positive，Precision = 正确 / (正确 + 误检)
        precision = right_check / model_positive
        images_precision = round(precision, 4)
        # 图像召回率=right_check/mark_positive，Recall = 正确 / (正确 + 漏检)
        recall = right_check / mark_positive
        images_recall = round(recall, 4)
        # 图像准确率=(正确 + 背景) / (正确 + 背景 + 误检 + 漏检)，
        accuracy = (right_check + negative_sample) / (right_check + negative_sample + error_check + leak_check)
        images_accuracy = round(accuracy, 4)
        statistical_tb = pt.PrettyTable(
            ['误检出', '漏检出', '背景图像', '正确检出', '图像精确率', '图像召回率', '标注正样本', '预测正样本', '图像准确率', 'F1分数'])
        image_title = '基于图像统计'
        #  分数（ Score），又称平衡F分数（balanced F Score），它被定义为精确率和召回率的调和平均数。
        f1_score = 2 * ((images_accuracy * images_recall) / (images_accuracy + images_recall))
        f1_score_4 = round(f1_score, 4)  # 保留小数点后四位
        statistical_tb.add_row(
            [error_check, leak_check, negative_sample, right_check, images_precision, images_recall, mark_positive, model_positive, images_accuracy,
             f1_score_4])
        print(statistical_tb.get_string(title=image_title))
        # 筛选漏检检出
        if parameter.leak_check:
            self.save_labelme(leak_check_list, self.output_dir, None)
        # 筛选正确检出
        if parameter.right_check:
            self.save_labelme(right_list, self.output_dir, None)
        # 筛选错误检出
        if parameter.right_check:
            self.save_labelme(error_check_list, self.output_dir, None)

        # 把漏检出与正确检出进行比对，MD5值相同的留下

    # @staticmethod
    def bbox_iou(self, box1, box2, w, h):
        """
        计算IOU值
        :return: IOU值
        @param box1: 格式[x1, y1, x2, y2]，模型预测坐标
        @param box2: 格式[x1, y1, x2, y2]，人工标注坐标
        @param h:
        @param w:
        """
        # h = image.shape[0]
        # w = image.shape[1]
        box1_x1, box1_y1, box1_x2, box1_y2 = self.convert_coordinates(box1, w, h)
        box2_x1, box2_y1, box2_x2, box2_y2 = self.convert_coordinates(box2, w, h)
        x1 = max(box1_x1, box2_x1)
        y1 = max(box1_y1, box2_y1)
        x2 = min(box1_x2, box2_x2)
        y2 = min(box1_y2, box2_y2)

        # 把坐标点转为左上，右下。做完坐标转换后导致结果不对
        # box1 = [[min(box_one[0]), min(box_one[1])], [max(box_one[0]), max(box_one[1])]]
        # box2 = [[min(box_two[0]), min(box_two[1])], [max(box_two[0]), max(box_two[1])]]
        # 不转换坐标计算方法
        # x1 = max(box1[0][0], box2[0][0])
        # y1 = max(box1[0][1], box2[0][1])
        # x2 = min(box1[1][0], box2[1][0])
        # y2 = min(box1[1][1], box2[1][1])
        inter_area = max(0, x2 - x1) * max(0, y2 - y1)  # 交集面积
        box1_area = (box1[1][0] - box1[0][0]) * (box1[1][1] - box1[0][1])  # 并集面积
        box2_area = (box2[1][0] - box2[0][0]) * (box2[1][1] - box2[0][1])  # 并集面积
        iou = inter_area / float(box1_area + box2_area - inter_area)  # 交集面积与并集面积的比值
        return iou

    @staticmethod
    def convert_coordinates(bbox, w, h):
        """
        把从任意角度标注兼容计算,把负数变成0
        @param bbox:
        @param w:
        @param h:
        @return:
        """
        points = np.array(bbox)
        point_min, point_max = points.min(axis=0), points.max(axis=0)
        x1, y1 = int(max(0, min(point_min[0], w))), int(max(0, min(point_min[1], h)))
        x2, y2 = int(max(0, min(point_max[0], w))), int(max(0, min(point_max[1], h)))
        return x1, y1, x2, y2

    def shapes_list_data(self, mark_shapes, model_shapes, threshold, w, h):
        """
        预测矩形框列表与标注矩形框列表，正反传参进行iou比较，得到漏检出、误检出、正确检出
        预测的N个矩形框与标注的矩形框挨个比较，两个矩形框没有交集或有交集，小于固定iou比值0.8，误检出
        标注的N个矩形框与预测的矩形框挨个比较，两个矩形框没有交集或有交集，小于固定iou比值0.8，漏检出
        都不满足误检出、漏检出，则就是正确检出
        @param h:
        @param w:
        @param threshold:
        @param mark_shapes:
        @param model_shapes:
        """
        flag = 0
        for mark_shape in mark_shapes:
            for model_shape in model_shapes:
                get_iou = self.bbox_iou(model_shape.get('points'), mark_shape.get('points'), w, h)
                if get_iou >= threshold:
                    flag = 1
                    break
            if flag == 1:
                flag = 0
            else:
                return True
        return False

    def compare_labelme(self, right_check, parameter):
        """
        比较漏检和正确检出中，找到相同的图像
        @param right_check:
        @param parameter:
        """
        # 找出漏检的图像MD5值与正确检出图像MD5值相同的情况
        leak_check_data = list()
        right_check_data = list()
        if parameter.leak_check:
            print(f'筛选，漏检存在于正确检出中的图像')
            for leak_data in self.datasets:
                for right_data in right_check:
                    if leak_data.get('md5_value') == right_data.get('md5_value'):
                        leak_check_data.append(leak_data)
            self.save_labelme(leak_check_data, self.output_dir, None)
        if parameter.right_check:
            print(f'筛选，正确检出存在于漏检出中的图像')
            for right_data in right_check:
                for leak_data in self.datasets:
                    if leak_data.get('md5_value') == right_data.get('md5_value'):
                        right_check_data.append(right_data)
            self.save_labelme(right_check_data, self.output_dir, None)

    def threshold_filter_labelme(self, parameter):
        """
        根据阈值筛选labelme数据集
        @param parameter:
        """
        filter_threshold = list()
        print(f'根据阈值筛选labelme数据集开始')
        for dataset in tqdm(self.datasets):
            if dataset.get('background') is True:
                for shape in dataset.get('labelme_info').get('shapes'):
                    if round(float(shape.get('text')), 1) == parameter.threshold:
                        filter_threshold.append(dataset)
        self.save_labelme(filter_threshold, self.output_dir, None)

    def bhattacharyya_filter_labelme(self, parameter):
        """
        图像内容相似度去重
        1. 欧氏距离：
           - 欧氏距离是最常用的距离度量之一，它计算两个直方图在每个维度上对应的直方柱之间的欧氏距离，并对所有维度上的距离进行平方和开根号。
           - 这种方法简单直观，计算效率较高。
        2. 曼哈顿距离：
           - 曼哈顿距离也是一种常用的距离度量方式，它计算两个直方图在每个维度上对应的直方柱之间的距离的绝对值之和。
           - 这种方法计算效率高，尤其在具有较高维度的直方图上。
        3. Bhattacharyya距离：
           - Bhattacharyya距离衡量了两个概率分布之间的相似程度，它直接基于直方图的概率分布计算。
           - 这种方法在度量直方图相似性时通常比其他方法更加有效。
        @param parameter:
        """
        print(f'根据余弦相似度，开始计算所有图像直方图，进行图像内容相似度去重开始')
        start_time = time.time()
        # 使用多线程计算所有图像的直方图
        with Pool() as pool:
            if parameter.opt == 'global':  # 全局直方图计算
                histogram_lists = pool.map(self.calc_histogram_block, [dataset['full_path'] for dataset in self.datasets])
            if parameter.opt == 'local':  # 局部直方图计算，局部计算更精准，优先使用
                histogram_lists = pool.map(self.hog_histogram, [dataset['full_path'] for dataset in self.datasets])
        end_time = time.time()
        print(f'余弦相似度计算耗时：{end_time - start_time}')
        # 中心化
        histogram_lists = np.array(histogram_lists).reshape(len(self.datasets), -1)
        if parameter.is_PCA:
            print('对直方图进行降维请耐心等待。。。')
            histogram_lists = histogram_lists - histogram_lists.mean(axis=1).reshape(len(self.datasets), -1)
            if histogram_lists.shape[0] < histogram_lists.shape[1]:
                model = PCA(n_components=0.98)  # 无法使用极大似然估计样本太少，只能主观设定
            else:
                print(f'使用极大似然估计，当前图像特征数量为：{histogram_lists.shape[1]}。图像数量为：{histogram_lists.shape[0]}')
                model = PCA(n_components='mle')  # 使用极大似然估计
            histogram_lists = model.fit_transform(histogram_lists.reshape(len(self.datasets), -1)).astype(np.float32)
        output_idx = []
        # print('开始分别比较直方图之间差异，计算两两之间的直方图距离')
        # dists = np.dot(histogram_lists, histogram_lists.T) / np.dot(np.linalg.norm(histogram_lists, axis=1).reshape(-1, 1),
        #                                                             np.linalg.norm(histogram_lists, axis=1).reshape(-1, 1).T)
        output_dataset = list()
        for index, dataset in tqdm(enumerate(self.datasets)):
            similarity1 = 0
            for j in range(len(output_idx) - 1, len(output_idx) - 101, -1):
                if j < 0:
                    break
                similarity1 = histogram_lists[index].dot(histogram_lists[output_idx[j]]) / (
                        np.linalg.norm(histogram_lists[index]) * np.linalg.norm(histogram_lists[output_idx[j]]))  # 余弦相似度
                if similarity1 > parameter.threshold:
                    break
            if similarity1 <= parameter.threshold:
                output_idx.append(index)
                output_dataset.append(dataset)
        print('保留的图片数量：{}'.format(len(output_idx)))
        self.save_labelme(output_dataset, self.output_dir, None)

    @staticmethod
    def calc_histogram_block(img1_path, resize_scale=(224, 224), block_size=8, hist_size=64):
        """
        计算所有图像直方图，整张图像全局计算
        @param img1_path:图片绝对路径
        @param resize_scale:图像缩放尺寸，224x224的像素
        @param block_size:分块大小，8x8的像素块
        @param hist_size:直方图大小尺寸，64
        @return:
        """
        num_block = int(resize_scale[0] * resize_scale[1] / (block_size ** 2))
        img1 = cv2.imdecode(np.fromfile(img1_path, dtype=np.uint8), -1)
        img1 = cv2.resize(img1, resize_scale)

        def calc_histogram_opt(img):
            block = np.zeros([block_size, block_size, num_block])
            block_count = 0
            for row in range(0, resize_scale[0], block_size):
                for col in range(0, resize_scale[1], block_size):
                    block[:, :, block_count] = img[row:row + 8, col:col + 8]
                    block_count += 1
            hist_total = np.zeros([int(block_size ** 2), hist_size])
            hist_count = 0
            for i in range(block_size):
                for j in range(block_size):
                    hist_res = np.histogram(block[i, j], bins=hist_size, range=[0, 255])[0]
                    hist_res = hist_res / np.sum(hist_res)
                    hist_total[hist_count, :] = hist_res
            return hist_total

        b_hist = calc_histogram_opt(img1[:, :, 0])
        g_hist = calc_histogram_opt(img1[:, :, 1])
        r_hist = calc_histogram_opt(img1[:, :, 2])
        hist_img = np.concatenate([b_hist, g_hist, r_hist], 1)
        return hist_img.astype(np.float32)

    @staticmethod
    def hog_histogram(img1_path, resize_scale=(120, 120), block_size=16, step=8):
        """
        计算所有图像直方图，整张图像局部计算，即只寻找有目标轮廓进行计算
        @param img1_path: 图片绝对路径
        @param resize_scale: 图像缩放尺寸，120x120的像素
        @param block_size: cell尺寸，等于16即为32像素块
        @param step: 步长
        @return:
        """

        def hog(block):
            # grads = copy.copy(block)
            # power = copy.copy(block)
            hist = np.zeros([9])
            for i in range(block_size):
                for j in range(block_size):
                    if i == 0 or i == block_size - 1:
                        if i == 0:
                            gx = block[i + 1, j] - 0
                        else:
                            gx = 0 - block[i - 1, j]
                    else:
                        gx = block[i + 1, j] - block[i - 1, j]

                    if j == 0 or j == block_size - 1:
                        if j == 0:
                            gy = block[i, j + 1] - 0
                        else:
                            gy = 0 - block[i, j - 1]
                    else:
                        gy = block[i, j + 1] - block[i, j - 1]
                    angle = np.arctan(gy / (gx + 0.000001)) * 180 / np.pi
                    mag = np.sqrt(gx ** 2 + gy ** 2)
                    # grads[i, j] = angle if angle >= 0 else 360 + angle
                    # power[i, j] = np.sqrt(gx**2 + gy**2)
                    hist[int(angle // 40)] += mag
            return hist

        img1 = cv2.imdecode(np.fromfile(img1_path, dtype=np.uint8), -1)
        img1 = cv2.resize(img1, resize_scale)
        img1 = np.float32(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY))
        # 伽马校正
        img1 = ((img1 + 0.5) / 256) ** (1 / 2) * 256 - 0.5
        # 归一化
        img1 = img1 / 255.0
        overlap_block_size = block_size + block_size - step
        img_hist = []
        for i in range(0, resize_scale[0], overlap_block_size):
            for j in range(0, resize_scale[1], overlap_block_size):
                overlap_block = img1[i:i + overlap_block_size, j:j + overlap_block_size]
                overlap_block_hist = []
                for row in range(0, overlap_block_size, step):
                    if overlap_block_size - row < block_size:
                        break
                    for col in range(0, overlap_block_size, step):
                        if overlap_block_size - col < block_size:
                            break
                        block = overlap_block[row:row + block_size, col:col + block_size]
                        hog_hist = hog(block)
                        overlap_block_hist = np.append(overlap_block_hist, hog_hist)
                overlap_block_hist_norm = overlap_block_hist / np.sum(overlap_block_hist)
                img_hist = np.append(img_hist, overlap_block_hist_norm)
        return img_hist

    @staticmethod
    def visualization_bbox2(image, shapes):
        """
        在开发工具中显示内存图像及坐标画框
        @param image:
        @param shapes:
        """
        image = copy.deepcopy(image)
        image = np.ascontiguousarray(image)
        for i in range(len(shapes)):
            x, y = shapes[i]['points']
            image = cv2.rectangle(image, (int(x[0]), int(x[1])), (int(y[0]), int(y[1])), 255, 2)
        plt.imshow(image[..., ::-1])
        plt.show()

    def chipeak_mosaic(self):
        json_dataset = list()
        for index, dataset in tqdm(enumerate(self.datasets)):
            img, shapes = self.mosaic(index)
            # img, shapes = self.mosaic_zy(index)
            self.visualization_bbox2(img, shapes)
            new_dataset = copy.deepcopy(dataset)  # 深度拷贝一份内存数据
            new_dataset.get('labelme_info').get('shapes').clear()  # 清空原有标注
            new_dataset.get('labelme_info').get('shapes').extend(shapes)
            # json_dataset.append(new_dataset)
            # 构造新的图像输出路径
            final_image_dir = os.path.join(new_dataset.get('output_dir'), new_dataset.get('image_dir'))
            final_labelme_dir = os.path.join(new_dataset.get('output_dir'), new_dataset.get('labelme_dir'))
            os.makedirs(final_image_dir, exist_ok=True)
            os.makedirs(final_labelme_dir, exist_ok=True)
            final_json_path = os.path.join(final_labelme_dir, new_dataset.get('labelme_file'))
            final_image_path = os.path.join(final_image_dir, new_dataset.get('image_file'))
            cv2.imwrite(final_image_path, img)
            # 重写json文件
            with open(final_json_path, "w", encoding='UTF-8', ) as labelme_fp:  # 以写入模式打开这个文件
                json.dump(new_dataset.get('labelme_info'), labelme_fp, indent=2, cls=Encoder)
        self.save_labelme(json_dataset, self.output_dir, None)

    def mosaic(self, index, s=640):
        # 计算马赛克图像中心
        min_offset_x = random.uniform(0.25, 0.75)
        min_offset_y = random.uniform(0.25, 0.75)
        # 再随机选取三张不同图像
        indices = [index] + [random.randint(0, len(self.datasets) - 1) for _ in range(3)]
        index = 0
        w, h, c = s, s, 3
        split_point_x = int(h * min_offset_x)
        split_point_y = int(w * min_offset_y)
        place_x = [0, 0, split_point_x, split_point_x]
        place_y = [0, split_point_y, 0, split_point_y]
        place_h = [split_point_x, split_point_x, h, h]
        place_w = [split_point_y, w, split_point_y, w]
        new_image = np.zeros([w, h, c]).astype(np.uint8)
        count = 0
        shapes_mosaic = []  # 马赛克的框数据
        for idx in indices:
            image = cv2.imread(self.datasets[idx].get('full_path'))
            iw, ih, c = image.shape
            dx = place_x[index]  # 左上角x
            dy = place_y[index]  # 左上角y
            dx2 = place_h[index]  # 该区域的高
            dy2 = place_w[index]  # 该区域的宽
            index += 1
            new_dx2 = ih if dx2 - dx > ih else dx2 - dx
            new_dy2 = iw if dy2 - dy > iw else dy2 - dy
            if count == 0:  # 左上
                new_image[split_point_y - new_dy2:split_point_y, split_point_x - new_dx2:split_point_x, :] = image[0:new_dy2, 0:new_dx2, :]
                dx = split_point_x - new_dx2
                dy = split_point_y - new_dy2
            elif count == 1:  # 左下角
                new_image[split_point_y:split_point_y + new_dy2, split_point_x - new_dx2:split_point_x, :] = image[0:new_dy2, 0:new_dx2, :]
                dy = split_point_y
                dx = split_point_x - new_dx2
            elif count == 2:  # 右上角
                new_image[split_point_y - new_dy2:split_point_y, split_point_x:split_point_x + new_dx2, :] = image[0:new_dy2, 0:new_dx2, :]
                dx = split_point_x
                dy = split_point_y - new_dy2
            else:  # 右下角
                new_image[split_point_y:split_point_y + new_dy2, split_point_x:split_point_x + new_dx2, :] = image[0:new_dy2, 0:new_dx2, :]
                dx = split_point_x
                dy = split_point_y
            for shape in self.datasets[idx].get('labelme_info').get('shapes'):
                bbox = shape['points']
                x1 = np.min(np.array(bbox)[:, 0])
                y1 = np.min(np.array(bbox)[:, 1])
                x2 = np.max(np.array(bbox)[:, 0])
                y2 = np.max(np.array(bbox)[:, 1])
                ori_area = (x2 - x1) * (y2 - y1)

                x1 += dx
                y1 += dy
                x2 += dx
                y2 += dy

                bbox = [x1, y1, x2, y2]

                # 获取每个检测框的宽高
                # x1, y1, x2, y2 = box

                # 如果是左上图，修正右侧和下侧框线
                if count == 0:
                    # 如果检测框左上坐标点不在第一部分中，就忽略它
                    if x1 > split_point_x or y1 > split_point_y:
                        continue

                    # 如果检测框右下坐标点不在第一部分中，右下坐标变成边缘点
                    if y2 >= split_point_y and y1 <= split_point_y:
                        y2 = split_point_y

                    if x2 >= split_point_x and x1 <= split_point_x:
                        x2 = split_point_x
                        # 如果修正后的左上坐标和右下坐标之间的距离过小，就忽略这个框

                # 如果是右上图，修正左侧和下册框线
                if count == 2:
                    if x2 < split_point_x or y1 > split_point_y:
                        continue

                    if y2 >= split_point_y and y1 <= split_point_y:
                        y2 = split_point_y

                    if x1 <= split_point_x and x2 >= split_point_x:
                        x1 = split_point_x

                # 如果是左下图
                if count == 1:
                    if x1 > split_point_x or y2 < split_point_y:
                        continue

                    if y1 <= split_point_y and y2 >= split_point_y:
                        y1 = split_point_y

                    if x1 <= split_point_x and x2 >= split_point_x:
                        x2 = split_point_x
                        continue

                # 如果是右下图
                if count == 3:
                    if x2 < split_point_x or y2 < split_point_y:
                        continue

                    if x1 <= split_point_x and x2 >= split_point_x:
                        x1 = split_point_x

                    if y1 <= split_point_y and y2 >= split_point_y:
                        y1 = split_point_y
                    # 更新坐标信息

                # if bbox[0] >= dx + new_dx2 or bbox[1] >= dy + new_dy2: # or bbox[0] + bbox[2] <= dx or bbox[1] + bbox[3] <= dy:
                #     continue
                # else:
                #     # x2, y2 = bbox[2] + bbox[0], bbox[3] + bbox[1]  # x2是高，y2是宽
                #     bbox[0] = max(bbox[0], dx)
                #     bbox[1] = max(bbox[1], dy)
                #     bbox[2] = min(dx2, x2)
                #     bbox[3] = min(dy2, y2)
                bbox = [[x1, y1], [x2, y2]]
                # if ori_area * 0.5 <= (bbox[1][0] - bbox[0][0]) * (bbox[1][1] - bbox[0][1]):
                shape['points'] = bbox
                shapes_mosaic.append(shape)
            count += 1
        return new_image, shapes_mosaic

    def chipeak_make_dir(self, parameter):
        """
        移动文件，创建目录，定制功能
        @param parameter:
        """
        print(f"移动文件，创建目录开始")
        for dataset in tqdm(self.datasets):
            obj_path = Path(dataset)
            try:
                if parameter.image_file not in str(obj_path.parent) and parameter.json_file not in str(obj_path.parent):  # 处理图像文件逻辑
                    final_image_dir = Path(obj_path.parent, parameter.image_file)
                    if parameter.image_file not in str(obj_path.parent):  # 如果00.images不存在于当前路径中则创建。00.image
                        os.makedirs(final_image_dir, exist_ok=True)
                    if obj_path.suffix in parameter.file_formats:
                        shutil.move(dataset, final_image_dir)
                if parameter.json_file not in str(obj_path.parent) and parameter.image_file not in str(obj_path.parent):  # 处理json文件逻辑
                    final_json_dir = Path(obj_path.parent, parameter.json_file)
                    os.makedirs(final_json_dir, exist_ok=True)
                    if obj_path.suffix not in parameter.file_formats:  # 文件后缀不在图像后缀列表中代表为json文件
                        shutil.move(dataset, final_json_dir)
            except Exception as e:
                print(e)
                print(f"出错路径为：{dataset}")

    def chipea_make_flags(self, parameter):
        """
        给指定目录，生成flags属性
        @param parameter:
        """
        ok_dataset = list()
        for dataset in tqdm(self.datasets):
            obj_path = Path(dataset.get('full_path'))
            if obj_path.parent.parent.name == parameter.helmet_true:
                if dataset.get('background') is True:
                    helmet_true = {'helmet': True}
                    data = self.shape_flags(dataset, helmet_true)
                    ok_dataset.append(data)
            if obj_path.parent.parent.name == parameter.helmet_false:
                if dataset.get('background') is True:
                    helmet_false = {'helmet': False}
                    data = self.shape_flags(dataset, helmet_false)
                    ok_dataset.append(data)
        self.save_labelme(ok_dataset, self.output_dir, None)

    @staticmethod
    def shape_flags(dataset, helmet):
        for shape in dataset.get('labelme_info').get('shapes'):
            shape.get('flags').update(helmet)
        return dataset

    def chipea_make_md5(self, parameter):
        """
        给每个图像文件对应的标注文件赋值MD5值
        """
        md5_value = list()
        for dataset in tqdm(self.datasets):
            if dataset.get('labelme_info') is not None:
                if parameter.mv5_value not in dataset.get('labelme_info'):
                    dataset.get('labelme_info')['md5Value'] = dataset.get("md5_value")
                    md5_value.append(dataset)
                if parameter.mv5_value in dataset.get('labelme_info'):
                    if self.count_digits(dataset.get('labelme_info')['md5Value']) < 32:
                        dataset.get('labelme_info')['md5Value'] = dataset.get("md5_value")
                        md5_value.append(dataset)
        self.save_labelme(md5_value, self.output_dir, None)

    @staticmethod
    def count_digits(input_string):  # 验证MD5值的长度是否符合新的sha3-512算法
        digit_count = sum(1 for char in input_string if char.isdigit())
        return digit_count

    def soft_deletion_json(self, args):
        """
        软删除json文件
        @param args:
        """
        soft_deletion = list()
        for dataset in tqdm(self.datasets):
            dataset.update({'background': args.background})
            soft_deletion.append(dataset)
        self.save_labelme(soft_deletion, self.output_dir, None)

    def rename_file_name(self, args):
        # 创建一个无限递增的整数序列，从1后面跟着8个0开始
        counter = count(start=1e8, step=1)
        for dataset in tqdm(self.datasets):
            unique_number = int(next(counter))  # 每次调用next(counter)都会返回一个不重复的整数,并把float类型转换为整形
            image_path = Path(dataset.get('full_path'))
            json_path = Path(dataset.get('original_json_path'))
            try:
                new_image_name = ""
                if image_path.suffix in args.file_formats:
                    new_image_name = str(unique_number) + image_path.suffix  # 组合新的文件名称
                    new_image_path = os.path.join(image_path.parent, new_image_name)  # 组合新的名称路径
                    os.rename(dataset.get('full_path'), new_image_path)  # 旧名称,新名称
                if json_path.suffix not in args.file_formats:
                    new_json_name = str(unique_number) + json_path.suffix  # 组合新的文件名称
                    new_json_path = os.path.join(json_path.parent, new_json_name)  # 组合新的名称路径
                    relative_path = os.path.join('../', '00.images', new_image_name)
                    # 先读取json，重命名json文件内部的名称，然后重命名整个文件名称
                    with open(json_path, 'r', encoding='UTF-8') as labelme_fp:
                        content = json.load(labelme_fp)
                        content.update({'imagePath': relative_path})
                    with open(json_path, 'w') as f:  # 重写json内容
                        # cls=json.JSONEncoder不是必须的，因为json.dumps() 函数会自动选择适当的编码器来对 Python 对象进行编码
                        f.write(json.dumps(content, indent=2, cls=Encoder))
                    os.rename(dataset.get('original_json_path'), new_json_path)  # 旧名称,新名称
            except Exception as e:
                print(e)
                if isinstance(e, json.JSONDecodeError):  # json文件存在错误，直接删除
                    print(f"JSON parsing error：{dataset.get('full_path')}")
                    os.remove(json_path)  # 删除错误json文件
                else:
                    print(f"其它错误：{dataset.get('full_path')}")

    def crop_objs(self, args):
        """
        截取图像功能实现，一张图片画框多少，就扣多少，不管是否重叠
        @param args: args.min_pixel 最小像素截图设置，默认512像素。即大于512像素的矩形框才进行截图
        """
        for dataset in tqdm(self.datasets):
            assert dataset['image_file'], '传入的图片路径为空，不能进行图片截取：{}'.format(dataset['labelme_file'])
            if dataset['labelme_file'] is None or dataset['labelme_info']['shapes'] == []:
                continue
            num_obj = 0
            for shape in dataset['labelme_info']['shapes']:
                # 组合保存抠图类别目录（Z:/4.my_work/9.zy/matting/00/00.images/call）
                save_img_dir = os.path.join(dataset['output_dir'], dataset['image_dir'], shape['label'])
                os.makedirs(save_img_dir, exist_ok=True)
                # 组合图片路径
                image_path = os.path.join(dataset['input_dir'], dataset['image_dir'], dataset['image_file'])
                # 组合抠图图片名称
                obj_img_file = Path(image_path)
                image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), 1)
                num_obj += 1
                # crop_file_name = obj_img_file.parent.parent.stem + '_' + obj_img_file.stem + '_{:0>6d}'.format(num_obj) + obj_img_file.suffix
                crop_file_name = obj_img_file.stem + '_{:0>6d}'.format(num_obj) + obj_img_file.suffix
                # 组合抠图图片存储路径
                crop_file_path = os.path.join(save_img_dir, crop_file_name)
                crop_obj = self.crop_rectangle(image, shape)
                if crop_obj.size == 0:
                    print("当前文件标注存在异常，路径如下所示:")
                    print(crop_file_path)
                # 默认像素小于10，就不进行截取，可以自动设置
                if crop_obj.shape[0] * crop_obj.shape[1] > args.min_pixel:
                    cv2.imencode(obj_img_file.suffix, crop_obj)[1].tofile(crop_file_path)

    @staticmethod
    def crop_rectangle(image, shape):
        """
        长方形截取计算过程
        :param image: 图像
        :param shape: 形状坐标
        :return:
        """
        h = image.shape[0]
        w = image.shape[1]
        # 把从任意角度标注兼容计算
        points = np.array(shape['points'])
        point_min, point_max = points.min(axis=0), points.max(axis=0)
        x1, y1 = int(max(0, min(point_min[0], w))), int(max(0, min(point_min[1], h)))
        x2, y2 = int(max(0, min(point_max[0], w))), int(max(0, min(point_max[1], h)))
        # y1:y2 x1:x2,针对负数框在图片的外面时截取不到,正常标注不会超出图片面积范围。max(0, min(x, img_info['width'])把负数变成0。np.clip(point_min)
        crop_obj = image[y1:y2, x1:x2]
        return crop_obj

    # def image_check(self, args):
    #     """
    #     检查图像问题，包含格式、通道、完整性及其它
    #     @param args:
    #     """
    #     for dataset in tqdm(self.datasets):
    #         if dataset.get("check") is False and args.image_check is True:
    #             try:
    #                 # os.makedirs(dataset.get("output_dir"), exist_ok=True)
    #                 # shutil.move(dataset.get("full_path"), dataset.get("output_dir"))
    #                 # shutil.move(dataset.get("original_json_path"), dataset.get("output_dir"))
    #             except Exception as e:
    #                 print(f"移动文件时出错: {e}")

    def move_file(self, parameter):
        for dataset in tqdm(self.datasets):
            obj_path = Path(dataset)
            try:
                # shutil.move(dataset, Path(obj_path.parent, parameter.image_file))
                # shutil.move(dataset, obj_path.parent.parent)
                if dataset.count('00.images') == 3:
                    print(dataset)
                    shutil.move(dataset, obj_path.parent.parent.parent)
            except Exception as e:
                print(e)
                print(f"出错路径为：{dataset}")

    def modify_flags(self, args):
        modify_flags_list = list()
        modify_condition = False  # 判断追加条件，有修改才回家dataset数据进行重写
        for dataset in tqdm(self.datasets):
            if dataset.get('labelme_info') is not None:
                for shape in dataset.get('labelme_info').get('shapes'):
                    for key, value in shape.get("flags").items():
                        if key == list(args.flags_value.keys())[0]:  # 把输入的键与标注的键进行比较
                            if value != list(args.flags_value.values())[0]:  # 把输入的值与标注的值进行比较
                                shape.get("flags").update({list(args.flags_value.keys())[0]: list(args.flags_value.values())[0]})  # 内存更新标注的值与期望的值
                                modify_condition = True
                # if not any(dataset.get('labelme_info').get("flags").values()):
                #     pass  # 字典为空
                # else:
                #     print("字典不为空")
                if modify_condition:
                    modify_flags_list.append(dataset)  # 追加修改后的数据
        self.save_labelme(modify_flags_list, self.output_dir, None)  # 保存修改好的数据

    def select_flags_true(self, args):
        for dataset in tqdm(self.datasets):
            print(dataset)
            print(args)
            if dataset.get('labelme_info') is not None:
                for shape in dataset.get('labelme_info').get('shapes'):
                    for key, value in shape.get("flags").items():
                        if value == args.flags_true:
                            if key in args.filter_flags:
                                print(key)

    # 按比例划分测试集和训练集,比例一般0.8/0.2或者是0.7/0.3，只实现剪切或移动文件，不能够拷贝，想拷贝需要修改输出的逻辑。
    def ratio_split(self, args):
        sublist_test, sublist_train = self.split_list_by_ratio(self.datasets, args.test_ratio, args.train_ratio)
        self.save_labelme(sublist_test, args.select_cut, "test")  # 保存划分测试集的数据
        self.save_labelme(sublist_train, args.select_cut, "train")  # 保存划分训练集的数据

    @staticmethod
    def split_list_by_ratio(lst, ratio_test, ratio_train):
        total_count = len(lst)
        sublist_test_count = round(total_count * ratio_test)  # 通过round进行四舍五入计算，保障奇数计算准确
        sublist_train_count = round(total_count * ratio_train)
        random.shuffle(lst)
        sublist_test = lst[:sublist_test_count]
        sublist_train = lst[sublist_test_count:sublist_test_count + sublist_train_count]
        return sublist_test, sublist_train

    def draw_video(self, args):
        """
        根据图片合成视频并绘制标注内容
        @param args:
        """
        video = None  # 初始化视频写入对象为 None
        output_video_file = ""
        for dataset in tqdm(self.datasets):
            os.makedirs(dataset.get("output_dir"), exist_ok=True)
            # 拼接视频文件名称
            output_video_file = os.path.join(dataset.get("output_dir"), "test.mp4")
            # 从第一张图片获取宽度和高度并初始化视频写入对象
            if video is None:
                # height, width, _ = image.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 设置为 MPEG-4 编码
                video = cv2.VideoWriter(output_video_file, fourcc, args.fps, (dataset.get("image_width"), dataset.get("image_height")))
            # 获取图片对象
            image = cv2.imread(dataset.get("full_path"))
            # 处理每张图片的标注
            if dataset.get('labelme_info') is not None:
                if len(args.filter_polygon) >= 2:  # 处理多个多边形的情况，比如闸机尾随
                    self.head_draw_annotations(image, dataset.get('labelme_info').get('shapes'), args)
                else:
                    # 处理一个多边形或者没有多边形的情况
                    image = self.draw_annotations(image, dataset.get('labelme_info').get('shapes'), args)  # 必须使用 image = 接收绘制后返回的新图像，才能够写入中文字体在视频上成功
            # 写入视频
            video.write(image)
        # 释放视频写入对象
        if video is not None:
            video.release()
            print(f"Video saved as {output_video_file}")

    # @staticmethod
    # def draw_annotations(image, shapes, args):
    #     for shape in shapes:
    #         points = shape['points']
    #         label = shape['label']
    #         if shape['shape_type'] == 'rectangle':
    #             # 处理第一个标签（如：开门红色）
    #             if len(args.filter_label) >= 1 and args.filter_label[0] == label:
    #                 color = (255, 51, 51)  # Red
    #                 cv2.rectangle(image, tuple(map(int, points[0])), tuple(map(int, points[1])), color, 2)
    #
    #             # 处理第二个标签（如：关门绿色），仅当存在时执行
    #             if len(args.filter_label) >= 2 and args.filter_label[1] == label:
    #                 color = (0, 255, 0)  # Green
    #                 cv2.rectangle(image, tuple(map(int, points[0])), tuple(map(int, points[1])), color, 2)
    #
    #             # 多边形区域可视化（可选）
    #             if args.filter_polygon:
    #                 color = (0, 255, 255)  # Yellow polygon
    #                 cv2.polylines(image, [np.array(args.filter_polygon, dtype=np.int32)], isClosed=True, color=color, thickness=2)
    #         # 标签文本显示
    #         cv2.putText(image, str(label), (int(points[0][0]), int(points[0][1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    @staticmethod
    def draw_chinese_text(image, text, position, font_size=20, color=(255, 255, 255)):
        try:
            # 获取包内 simhei.ttf 的真实路径
            font_path = pkg_resources.resource_filename('ccdt', 'fonts/simhei.ttf')
            # print(f"[字体路径] {font_path}")
            assert os.path.exists(font_path), f"字体路径无效: {font_path}"
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"[警告] 加载字体失败：{e}")
            return image

        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        draw.text(position, text, font=font, fill=color)
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    @staticmethod
    def draw_annotations(image, shapes, args):
        for shape in shapes:
            points = shape['points']
            label = shape['label']
            if shape['shape_type'] == 'rectangle':
                # ➤ 加入位置微扰动（不改原始标注）
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
                pt1 = (int(points[0][0] + offset_x), int(points[0][1] + offset_y))
                pt2 = (int(points[1][0] + offset_x), int(points[1][1] + offset_y))

                # ➤ 处理第一个标签（如：开门红色）
                if args.filter_label and len(args.filter_label) >= 1 and args.filter_label[0] == label:
                    color = (255, 51, 51)  # Red
                    cv2.rectangle(image, pt1, pt2, color, 2)

                # ➤ 处理第二个标签（如：关门绿色）
                if args.filter_label and len(args.filter_label) >= 2 and args.filter_label[1] == label:
                    color = (0, 255, 0)  # Green
                    cv2.rectangle(image, pt1, pt2, color, 2)

                # ➤ 多边形区域（可选）
                if args.filter_polygon:
                    color = (0, 255, 255)  # Yellow polygon
                    cv2.polylines(image, [np.array(args.filter_polygon, dtype=np.int32)], isClosed=True, color=color, thickness=2)

                # ➤ 显示位置：矩形框上方，自动防止越界，跟随扰动
                font_size = 32
                text_x = pt1[0]
                text_y = min(pt1[1], pt2[1]) - 10 - font_size
                position = (text_x, max(text_y, 0))  # 防止越界

                # ➤ 使用支持中文的方式显示标签
                image = BaseLabelme.draw_chinese_text(
                    image,
                    label,
                    position,
                    font_size=font_size,
                    color=(255, 0, 0)  # 红色字体
                )

        return image

    # @staticmethod
    # def draw_annotations(image, shapes, args):
    #     for shape in shapes:
    #         points = shape['points']
    #         label = shape['label']
    #         if shape['shape_type'] == 'rectangle':
    #             if args.filter_label[0] == label:  # 开门红色
    #                 color = (255, 51, 51)  # Red color for rectangle
    #                 cv2.rectangle(image, tuple(map(int, points[0])), tuple(map(int, points[1])), color, 2)
    #             if args.filter_label[1] == label:  # 关门绿色
    #                 color = (0, 255, 0)  # Green color for polygon
    #                 cv2.rectangle(image, tuple(map(int, points[0])), tuple(map(int, points[1])), color, 2)
    #             if args.filter_polygon:
    #                 color = (0, 255, 255)  # 黄色多边形
    #                 cv2.polylines(image, [np.array(args.filter_polygon, dtype=np.int32)], isClosed=True, color=color, thickness=2)
    #         # elif shape['shape_type'] == 'polygon':
    #         #     color = (0, 255, 255)  # 黄色多边形
    #         #     cv2.polylines(image, [np.array(args.filter_polygon, dtype=np.int32)], isClosed=True, color=color, thickness=2)
    #         cv2.putText(image, label, (int(points[0][0]), int(points[0][1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    @staticmethod
    # 射线法,这个方法的基本思想是：从点发出一条射线，计算射线与多边形边界的交点数。如果交点数是奇数，点在多边形内部；如果是偶数，点在多边形外部。
    def head_draw_annotations(image, shapes, args):
        # 检查每个通道的多边形
        for i, polygon in enumerate(args.filter_polygon):
            # 创建多边形对象
            polygon_points = Polygon(polygon)
            channel_count = 0  # 每个通道的人头计数
            ok_points = []
            for shape in shapes:
                points = shape['points']
                # label = shape['label']
                if shape['shape_type'] == 'rectangle':
                    center_x = (points[0][0] + points[1][0]) / 2
                    center_y = (points[0][1] + points[1][1]) / 2
                    point = Point(center_x, center_y)  # 计算矩形框的中心点
                    if polygon_points.contains(point):  # 如果中心点在多边形内，就进行人头数累计;判断点是否在多边形内
                        channel_count += 1
                        ok_points.append(points)
            if channel_count >= 2:
                # 画矩形框在图片中
                for point in ok_points:
                    color = (255, 51, 51)  # Red color for rectangle
                    cv2.rectangle(image, tuple(map(int, point[0])), tuple(map(int, point[1])), color, 2)
                    # cv2.putText(image, label, (int(points[0][0]), int(points[0][1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                # 画多边形框在图片中
                if polygon:
                    color = (0, 255, 255)  # 黄色多边形
                    cv2.polylines(image, [np.array(polygon, dtype=np.int32)], isClosed=True, color=color, thickness=2)

    def blacked_images(self):
        for dataset in tqdm(self.datasets):
            if dataset.get('labelme_info') is None:
                continue
            # 读取原始图片
            image_path = dataset.get('full_path')
            json_path = dataset.get('json_path')  # 删除涂黑矩形框的时候读取文件备用
            image = cv2.imread(image_path)

            if image is None:
                print(f"⚠️ 读取失败: {image_path}")
                continue

            # 遍历所有形状
            for shape in dataset['labelme_info'].get('shapes', []):
                if shape.get('shape_type') == 'rectangle':
                    points = shape.get('points', [])
                    if len(points) < 2:
                        continue

                    # 确保坐标是整数
                    x1, y1 = map(int, points[0])
                    x2, y2 = map(int, points[1])

                    # 画黑色矩形
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), thickness=-1)
            # 保存图片
            # save_path = image_path.replace('.jpg', '_black.jpg')  # 避免覆盖原图
            cv2.imwrite(dataset.get('full_path'), image)  # 覆盖原图
        print(f"✅ 涂黑目标矩形框，处理完成")

    def sahi_images(self, args):
        """
        滑窗切图
        :param args:
        """
        for dataset in tqdm(self.datasets):
            os.makedirs(os.path.join(dataset.get("output_dir"), dataset.get("image_dir")), exist_ok=True)
            os.makedirs(os.path.join(dataset.get("output_dir"), dataset.get("labelme_dir")), exist_ok=True)
            if dataset.get('labelme_info') is None:
                continue
            # 读取原始图片
            image_path = dataset.get('full_path')
            img = cv2.imread(image_path)
            h, w = img.shape[:2]
            filename = os.path.splitext(os.path.basename(image_path))[0]
            # 滑窗步长遍历
            for y in range(0, h, args.stride):
                for x in range(0, w, args.stride):
                    x_end = min(x + args.slice_width, w)
                    y_end = min(y + args.slice_height, h)
                    # 裁图
                    crop = img[y:y_end, x:x_end]
                    slice_name = f"{filename}_{x}_{y}.jpg"
                    slice_path = os.path.join(dataset.get("output_dir"), dataset.get("image_dir"), slice_name)
                    relative_path = os.path.join('../', '00.images', slice_name)
                    cv2.imwrite(slice_path, crop)
                    # 拷贝并过滤 label
                    new_data = {
                        'version': dataset['labelme_info'].get('version', ''),
                        'flags': dataset['labelme_info'].get('flags', ''),
                        'shapes': [],
                        'imagePath': relative_path,
                        'imageData': None,
                        'imageHeight': y_end - y,
                        'imageWidth': x_end - x
                    }
                    for shape in dataset['labelme_info'].get('shapes', []):
                        points = shape.get('points')
                        shape_type = shape.get('shape_type')
                        # 计算中心点
                        if shape_type == 'rectangle':
                            x1, y1 = points[0]
                            x2, y2 = points[1]
                            cx = (x1 + x2) / 2
                            cy = (y1 + y2) / 2
                        else:
                            xs = [p[0] for p in points]
                            ys = [p[1] for p in points]
                            cx = sum(xs) / len(xs)
                            cy = sum(ys) / len(ys)
                        # 修改为面积判断 + 裁剪后重构形状
                        # new_points = self.shape_crop_in_window(points, x, y, x_end, y_end)
                        if self.point_in_rect(cx, cy, x, y, x_end, y_end):
                            # 坐标偏移
                            new_points = [[p[0] - x, p[1] - y] for p in points]
                            new_shape = {
                                'label': shape['label'],
                                'points': new_points,
                                "group_id": None,
                                'shape_type': shape['shape_type'] if shape['shape_type'] == 'rectangle' else 'polygon',  # 裁剪后不能保证仍是矩形，也行是 polygon
                                'flags': shape.get('flags', {}),
                                'text': None
                            }
                            new_data['shapes'].append(new_shape)

                    # 如果有合法标注，保存 json
                    if len(new_data['shapes']) > 0:
                        json_name = os.path.splitext(slice_name)[0] + '.json'
                        json_path = os.path.join(dataset.get("output_dir"), dataset.get("labelme_dir"), json_name)
                        with open(json_path, 'w') as f:
                            json.dump(new_data, f, indent=2)

    @staticmethod
    def point_in_rect(x, y, xmin, ymin, xmax, ymax):
        return xmin <= x <= xmax and ymin <= y <= ymax

    @staticmethod
    def shape_crop_in_window(shape_points, crop_xmin, crop_ymin, crop_xmax, crop_ymax):
        """
        判断 shape 是否完全落入裁剪窗口中。如果完全在窗口中，则返回偏移后的点，否则返回 None。
        """
        for x, y in shape_points:
            if not (crop_xmin <= x <= crop_xmax and crop_ymin <= y <= crop_ymax):
                return None  # 只要有一个点在窗口外，就丢弃

        # 所有点都在裁剪区域内，进行坐标偏移
        offset_points = [[x - crop_xmin, y - crop_ymin] for x, y in shape_points]
        return offset_points

    @staticmethod
    def is_inside(inner, outer, epsilon=2.0):
        """
        判断 inner 是否在 outer 内，允许 epsilon 像素的容差。
        标注偏差：手动标注时略微多框了 1~2 像素，使得框“略微越界”，但仍然可以认为是属于该人。
        在图像标注中，有些矩形框（如手套框）理论上应该被包含在人框里，但由于以下原因可能出现轻微“越界”或“刚好贴边”的情况，导致无法通过 >= 和 <= 严格判断为“包含”。
        inner: [x1, y1, x2, y2], outer: [x1, y1, x2, y2]
        """
        try:
            if not all(isinstance(v, (int, float)) for v in inner + outer):
                return False
            if inner[2] <= inner[0] or inner[3] <= inner[1]:
                return False  # inner 是非法框
            if outer[2] <= outer[0] or outer[3] <= outer[1]:
                return False  # outer 是非法框
            return (inner[0] >= outer[0] - epsilon and
                    inner[1] >= outer[1] - epsilon and
                    inner[2] <= outer[2] + epsilon and
                    inner[3] <= outer[3] + epsilon)
        except Exception as e:
            print(f"[Warning] is_inside 判断失败: {e}")
            return False

    def intercept_images(self, args):
        for dataset in tqdm(self.datasets):
            os.makedirs(os.path.join(dataset.get("output_dir"), dataset.get("image_dir")), exist_ok=True)
            os.makedirs(os.path.join(dataset.get("output_dir"), dataset.get("labelme_dir")), exist_ok=True)
            if dataset.get('labelme_info') is None:
                continue
            # 加载图像和标注
            img = cv2.imread(dataset.get('full_path'))
            if img is None:
                print(f"[跳过] 图像加载失败: {dataset.get('full_path')}")
                continue
            h, w = img.shape[:2]
            filename = os.path.splitext(os.path.basename(dataset.get('full_path')))[0]
            # 分类人和手套
            person_boxes = []
            other_boxes = []  # glove or no_glove
            for shape in dataset.get('labelme_info').get('shapes'):
                label = shape['label']
                points = shape['points']
                x1, y1 = points[0]
                x2, y2 = points[1]
                box = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                if label == args.intercept_the_object:
                    person_boxes.append({'bbox': box, 'shape': shape})
                elif label in args.contained_of_object:
                    other_boxes.append({'bbox': box, 'shape': shape})

            for i, person in enumerate(person_boxes):
                person_box = person['bbox']
                px1, py1, px2, py2 = map(int, person_box)
                # 边界校正，防止越界
                px1 = max(0, min(px1, w - 1))
                px2 = max(0, min(px2, w))
                py1 = max(0, min(py1, h - 1))
                py2 = max(0, min(py2, h))

                # 宽或高为 0，非法
                if px2 <= px1 or py2 <= py1:
                    print(f"[跳过] 非法人框 (坐标不合法): {person_box}")
                    continue

                # 裁剪人图像
                person_img = img[py1:py2, px1:px2]
                if person_img is None or person_img.size == 0:
                    print(f"[跳过] 裁剪人图像为空: {person_box}")
                    continue
                # 找出在该人框内的手套/无手套框
                contained_shapes = []
                for item in other_boxes:
                    box = item['bbox']
                    # 修改函数调用方式，支持外部设定 epsilon 容差值
                    if self.is_inside(box, person_box, epsilon=args.epsilon):
                        # 坐标偏移到新图像中
                        offset_shape = item['shape'].copy()
                        offset_shape['points'] = [
                            [p[0] - px1, p[1] - py1] for p in offset_shape['points']
                        ]
                        contained_shapes.append(offset_shape)
                # 保存图像
                slice_name = f"{filename}_{i}.jpg"
                slice_path = os.path.join(dataset.get("output_dir"), dataset.get("image_dir"), slice_name)
                relative_path = os.path.join('../', '00.images', slice_name)
                cv2.imwrite(slice_path, person_img)

                # 保存对应的 JSON
                out_json = {
                    "version": dataset['labelme_info'].get('version', ''),
                    "flags": dataset['labelme_info'].get('flags', ''),
                    "shapes": contained_shapes,
                    "imagePath": relative_path,
                    'imageData': None,
                    "imageHeight": person_img.shape[0],
                    "imageWidth": person_img.shape[1]
                }
                json_name = os.path.splitext(slice_name)[0] + '.json'
                json_path = os.path.join(dataset.get("output_dir"), dataset.get("labelme_dir"), json_name)
                with open(json_path, 'w') as f:
                    json.dump(out_json, f, indent=2)

    # 计算标注目标与图像面积占比，划分保留大、中、小、的标注目标为labelme数据集功能。
    def mix_images(self, args):
        small_list = []
        medium_list = []
        large_list = []

        for dataset in tqdm(self.datasets):
            label_info = dataset.get('labelme_info')
            if not label_info:
                continue
            shapes = label_info.get('shapes', [])
            img_w = label_info.get('imageWidth')
            img_h = label_info.get('imageHeight')
            # 默认分类逻辑
            has_large = False
            has_medium = False
            for shape in shapes:
                if shape.get("shape_type") != "rectangle":
                    continue
                (xmin, ymin), (xmax, ymax) = shape.get("points")
                xmin, xmax = sorted([xmin, xmax])
                ymin, ymax = sorted([ymin, ymax])
                size = self.classify_object_size(xmin, ymin, xmax, ymax, img_w, img_h, args)
                if size == 'large':
                    has_large = True
                    break  # 优先级最高，直接分类为 large
                elif size == 'medium':
                    has_medium = True
                    # 不 break，继续看有没有 large

            # 唯一分类逻辑：大 > 中 > 小
            if has_large:
                large_list.append(dataset)
            elif has_medium:
                medium_list.append(dataset)
            else:
                small_list.append(dataset)

        # 保存各类目标的图像
        self.save_labelme(small_list, args.select_cut, "small")
        self.save_labelme(medium_list, args.select_cut, "medium")
        self.save_labelme(large_list, args.select_cut, "large")

    @staticmethod
    def classify_object_size(xmin, ymin, xmax, ymax, img_w, img_h, args):
        """
        计算目标面积占比
        @param xmin:
        @param ymin:
        @param xmax:
        @param ymax:
        @param img_w:
        @param img_h:
        @param args:
        @return:
        """
        box_area = (xmax - xmin) * (ymax - ymin)
        img_area = img_w * img_h
        ratio = box_area / img_area
        if ratio <= args.small_ratio:
            return 'small'
        elif ratio <= args.medium_ratio:
            return 'medium'
        else:
            return 'large'

    def sampling_images(self, args):
        exclude_if_only_list = []  # 要排除的（只含某类标签）
        include_focus_list = []  # 要保留的（含关注类标签）
        others_list = []  # 其它情况是否保留由参数控制

        for dataset in tqdm(self.datasets):
            if not dataset.get('background'):
                continue

            shapes = dataset.get('labelme_info', {}).get('shapes', [])
            labels = [shape.get('label') for shape in shapes]
            label_set = set(labels)

            # 1. 保留：不是仅包含排除标签的 → 加入 exclude_if_only_list
            if args.exclude_if_only:
                if not label_set.issubset(set(args.exclude_if_only)):
                    exclude_if_only_list.append(dataset)

            # 2. 保留：只要包含重点关注标签 → 加入 include_focus_list
            if args.include_focus:
                if label_set & set(args.include_focus):  # 有交集
                    include_focus_list.append(dataset)

            # # 全部标签都在排除集中 → 排除
            # if args.exclude_if_only and label_set.issubset(set(args.exclude_if_only)):
            #     continue
            #
            # # 包含关注标签 → 保留
            # if args.include_focus and label_set & set(args.include_focus):
            #     include_focus_list.append(dataset)
            # else:
            #     # 其它情况，根据是否保留其他图像来决定
            #     if getattr(args, 'keep_rest', True):  # 默认保留
            #         others_list.append(dataset)

        # 最终合并两类去重保存（有交集的话可能重复）
        # all_retained = list({id(x): x for x in exclude_if_only_list + include_focus_list}.values())
        # if all_retained:
        #     self.save_labelme(all_retained, self.output_dir, "filtered")

        # 保存结果（是否合并可以根据你的需求来）
        if include_focus_list and args.include_focus:
            self.save_labelme(include_focus_list, args.select_cut, "include_focus")
        if exclude_if_only_list and args.exclude_if_only:
            self.save_labelme(exclude_if_only_list, args.select_cut, "exclude_if_only")
