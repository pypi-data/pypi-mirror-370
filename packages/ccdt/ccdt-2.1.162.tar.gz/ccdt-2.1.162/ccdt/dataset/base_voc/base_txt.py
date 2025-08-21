# 计算机登录用户: jk
# 系统日期: 2023/10/14 12:36
# 项目名称: chipeak_cv_data_tool
# 开发者: zhanyong
import os
from pathlib import Path
from ccdt.dataset import *

# 视频标注数据集处理
class BaseTxt(BaseLabelme):
    def __init__(self, *args, **kwargs):
        self.txt_path = args[1]  # 获取voc数据集对应的xml目录路径
        self.txt_path_list = LabelmeLoad.get_txt_path(self.txt_path)
        # 在这里定义labelme数据结构格式初始化
        super(BaseTxt, self).__init__(*args, **kwargs)

    def txt2labelme(self):
        txt_to_labelme = list()
        # 每循环一次，拼接对应的xml文件路径，直接读取xml文件，然后转换成labelme_info
        for dataset in self.datasets:
            judge_key = dataset.get("image_dir").split("/")[0]  # 获取唯一判断标识，视频目录不允许嵌套，否则唯一判断关系会错乱
            obj_path = Path(dataset.get('image_file'))  # 获取文件前缀
            lines_list = list()
            for txt_path in self.txt_path_list:
                txt_path.items()
                for key, value in txt_path.items():
                    if key == judge_key:
                        # 使用 readlines 方法读取文件内容，并去除每行末尾的换行符
                        with open(value, 'r') as file:
                            lines_list = [line.rstrip() for line in file.readlines()]
            find_shape_list = list()
            for line in lines_list:
                # 使用 zfill 方法将字符串往左补零到指定长度
                result = line.split(",")[0].zfill(8)
                if obj_path.stem == result:
                    find_shape_list.append(line)
                    break  # 找到唯一存在的那一帧图像后，就结束循环
            # 检查列表是否为空，为空就是没有找到当背景处理，不写json文件
            if len(find_shape_list) != 0:  # 不为空就是在tex文本中找到了标注，写入当前帧图像对应的标注json文件
                labelme_info = self.analysis_txt(find_shape_list, dataset.get("image_width"), dataset.get("image_height"), dataset.get("relative_path"))
                dataset.update({'background': True})
                dataset.update({'labelme_info': labelme_info})
            txt_to_labelme.append(dataset)
        self.save_labelme(txt_to_labelme, self.output_dir, None)  # self.output_dir为空字符串也是可以的

    @staticmethod
    def analysis_txt(find_shape, w, h, file_name):
        # image_path = os.path.join("../", "00.images", file_name).replace('\\', '/')
        # 定义labelme数据结构
        labelme_data = dict(
            version='4.5.14',
            flags={},
            shapes=[],
            imagePath=None,
            imageData=None,
            imageHeight=None,
            imageWidth=None
        )
        for shape in find_shape:
            xmin = int(shape.split(",")[2])
            ymin = int(shape.split(",")[3])
            xmax = int(shape.split(",")[4])
            ymax = int(shape.split(",")[5])
            name = shape.split(",")[6]
            points = [[xmin, ymin], [xmax, ymax]]  # 坐标点计算，目前使用左上角的点和右下角的点计算
            make_up_shape = {"label": name, "points": points, "group_id": None, "shape_type": "rectangle", "flags": {}, 'text': None}
            labelme_data.get('shapes').append(make_up_shape)  # 这里是确定了每一张图像只标注一个，如果是标注多个的话，就是一个列表了
        # labelme_data.update({"imagePath": image_path})
        labelme_data["imagePath"] = file_name
        labelme_data["imageWidth"] = w
        labelme_data["imageHeight"] = h
        return labelme_data
