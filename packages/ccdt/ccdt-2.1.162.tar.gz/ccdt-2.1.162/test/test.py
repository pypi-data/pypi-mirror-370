import os
from multiprocessing import Pool, Manager
import argparse
from pathlib import Path
import numpy as np
import json
import subprocess
import shutil
from PIL import Image
import psutil


class Encoder(json.JSONEncoder):
    """
    labelme数据保存编码实现类
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(Encoder, self).default(obj)


def process_file(file_path, comman_pool):
    """
    调用darknet指令，返回网络预测结果
    @param file_path:
    @param comman_pool:
    @return:
    """
    os.system(comman_pool + ' ' + file_path)
    make_command = comman_pool + ' ' + file_path
    output = subprocess.check_output(make_command, shell=True, text=True)
    return output


def count_box(result):
    """
    计算矩形框
    @param result:
    """
    x = float(result.get('x'))
    y = float(result.get('y'))
    w = float(result.get('w'))
    h = float(result.get('h'))
    # 使用中心点计算左上角的坐标和右下角的坐标
    x1 = x - w / 2
    x2 = x1 + w
    y1 = y - h / 2
    y2 = y1 + h
    points = [[x1, y1], [x2, y2]]
    return points


def process_result(result_data):
    """
    处理异步处理完毕的任务结果
    @param result_data:
    """
    data_list = result_data.split('\n')
    print('迭代内容开始=====================================')
    # 开始封装labelme数据集
    labelme_data = dict(
        version='4.6.9',
        flags={},
        shapes=[],
        imagePath='',
        imageData=None,
        imageHeight=0,
        imageWidth=0
    )
    output_json_file_path = ''
    image_path = ''
    self_image_dir = ''
    shapes = list()
    for line in data_list:
        if line.startswith('/my_tmp'):  # 查找关键词进行判断
            image_path = line.split(':')[0]
            image = Image.open(image_path)  # 通过PIL模块获取图像宽高
            obj_path = Path(image_path)  # 初始化路径对象为对象
            parent_path = str(obj_path.parent)
            replate_path = parent_path.replace(args.input_dir, '').strip('\\/')
            self_image_dir = os.path.join(args.output_dir, replate_path)
            self_labelme_dir = os.path.join(os.path.dirname(self_image_dir), '01.labelme')
            os.makedirs(self_image_dir, exist_ok=True)
            os.makedirs(self_labelme_dir, exist_ok=True)
            labelme_file = obj_path.stem + '.json'
            output_json_file_path = os.path.join(self_labelme_dir, labelme_file)
            labelme_image_path = os.path.join('../00.images', obj_path.name)
            labelme_data['imageHeight'] = image.height
            labelme_data['imageWidth'] = image.width
            labelme_data['imageData'] = None
            labelme_data['imagePath'] = labelme_image_path
            # define_data_structure.update({'image_path': image_path})
        elif line.startswith('label'):
            objects = line.split(': ')  # 根据:分割为列表
            # print(f'目标矩形框{objects}')
            string = ' '.join(objects)  # 把列表转字符串
            # 把字符串转字典
            result = {item.split(':')[0]: item.split(':')[1] for item in string.split(' ')}
            # print(f'把字符串转字典{result}')
            if result.get('label') == str(0):
                # fall_doubt = result.get('label')
                # print(f'疑似跌倒报警{fall_doubt}')
                name = 'fall_doubt'
                shape = {"label": name, "points": count_box(result), "group_id": None,
                         "shape_type": "rectangle",
                         "flags": {}, "text": result.get('thresh')}
                shapes.append(shape)
            if result.get('label') == str(1):
                # fall = result.get('label')
                # print(f'跌倒报警{fall}')
                name = 'fall'
                shape = {"label": name, "points": count_box(result), "group_id": None,
                         "shape_type": "rectangle",
                         "flags": {}, "text": result.get('thresh')}
                shapes.append(shape)
    print('迭代内容结束=====================================')
    labelme_data['shapes'] = shapes
    with open(output_json_file_path, 'w', encoding='UTF-8') as labelme_fp:
        json.dump(labelme_data, labelme_fp, indent=2, cls=Encoder)
    # 拷贝图片
    shutil.copy(image_path, self_image_dir)


def get_args():
    parser = argparse.ArgumentParser('')
    parser.add_argument('--input_dir', type=str,
                        # default=r'H:\1.model_train\7.SDC\08.fall_fall_doubt-zy-20230406\01.Datasets\huawei_yan_xuan\ok',
                        default=r'/my_tmp/08.fall_fall_doubt-zy-20230406/test_images/boss_to_dataset/02.collect_datasets/PublicDatasets/20230605-qhy-fall',
                        # default=r'/my_tmp/08.fall_fall_doubt-zy-20230406/01.Datasets/20230509_add_negative_sample/train/huawei_negative',
                        # default=r'/my_tmp/08.fall_fall_doubt-zy-20230406/result_images/huawei_yan_xuan',
                        help='获取图片输入路径')
    parser.add_argument('--output_dir', type=str,
                        # default=r'H:\1.model_train\7.SDC\08.fall_fall_doubt-zy-20230406\01.Datasets\huawei_yan_xuan\lll',
                        default=r'/my_tmp/08.fall_fall_doubt-zy-20230406/result_images/boss_to_dataset_new_om_20260609_yolov3_20000.weights',
                        # default=r'/my_tmp/08.fall_fall_doubt-zy-20230406/result_images/standard/huawei_negative_20230515',
                        # default=r'/my_tmp/08.fall_fall_doubt-zy-20230406/result_images/huawei_yan_xuan_20230515_test',
                        help='获取图片输入路径')
    parser.add_argument('--file_formats', default=['.jpg', '.jpeg', '.png', '.JPEG', '.JPG', '.PNG'], type=str,
                        help="文件格式")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    comman_pool = '/work/darknet detector test all_data.data yolov3.cfg ./work_dirs/yolov3_10000.weights -thresh 0.5 -dont_show'
    # 获取逻辑 CPU 数量
    cpu_count = psutil.cpu_count(logical=True)
    # 获取未使用的 CPU 核心数量
    unused_cpu_count = psutil.cpu_count(logical=False)
    print(f"本计算机上有 {cpu_count} 个逻辑 CPU 核心")
    print(f"未使用的 CPU 核心数量为 {unused_cpu_count}")
    os.makedirs(args.output_dir, exist_ok=True)
    # 我们使用 Manager 对象创建了一个共享的队列 queue，该队列可以安全地在多个进程之间传递数据。
    with Manager() as manager:
        queue = manager.Queue()
        # pool = Pool(processes=os.cpu_count())  # 获取逻辑 CPU 数量
        pool = Pool(processes=10)
        print('多进程异步开始===============================')
        for subdir, dirs, files in os.walk(args.input_dir):
            for file in files:
                file_path = os.path.join(subdir, file)
                obj_file_path = Path(file_path)  # 初始化路径对象为对象
                if obj_file_path.suffix in args.file_formats:
                    # 多进程并发异步处理文件，返回处理结果
                    pool.apply_async(process_file, args=(file_path, comman_pool), callback=process_result)
        # 在主进程中等待队列中有一个元素就开始处理 result,这样我们就可以在队列中添加一条数据时，立即开始处理，无需等待全部多进程执行完毕。
        while True:
            try:
                result = queue.get_nowait()
            except:
                if pool._taskqueue.qsize() == 0:  # 如果队列已经为空，则跳出循环
                    break
                continue
            process_result(result)  # 这里直接处理已完成的结果
        pool.close()  # 关闭进程池
        pool.join()
        print('多进程异步结束===============================')
