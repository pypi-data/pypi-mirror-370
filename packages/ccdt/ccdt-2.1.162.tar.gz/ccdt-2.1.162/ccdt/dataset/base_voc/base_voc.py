# 计算机登录用户: jk
# 系统日期: 2023/7/31 18:06
# 项目名称: chipeak_cv_data_tool
# 开发者: zhanyong
import os
from pathlib import Path
from ccdt.dataset import *
import xml.etree.ElementTree as ET


# voc转labelme
class BaseVoc(BaseLabelme):
    def __init__(self, *args, **kwargs):
        self.voc_xml_path = args[1]  # 获取voc数据集对应的xml目录路径
        # 在这里定义labelme数据结构格式初始化
        super(BaseVoc, self).__init__(*args, **kwargs)

    def voc2labelme(self):
        """
        voc数据集转labelme数据集
        """
        voc_to_labelme = list()
        # 每循环一次，拼接对应的xml文件路径，直接读取xml文件，然后转换成labelme_info
        for dataset in self.datasets:
            image_file_name = dataset.get('image_file')
            obj_path = Path(image_file_name)
            xml_name = obj_path.stem + '.xml'
            voc_xml_path = os.path.join(self.voc_xml_path, xml_name)
            labelme_file = obj_path.stem + '.json'
            dataset.update({'image_dir': '00.images'})
            dataset.update({'labelme_file': labelme_file})
            relative_path = os.path.join('../', '00.images', image_file_name)
            labelme_info = self.analysis_xml(voc_xml_path)
            if labelme_info.get('shapes'):
                dataset.update({'background': True})
                labelme_info.update({'imagePath': relative_path})
                labelme_info.update({'imageHeight': dataset.get('image_height')})
                labelme_info.update({'imageWidth': dataset.get('image_width')})
                dataset.update({'relative_path': relative_path})
                dataset.update({'labelme_info': labelme_info})
            else:
                xml_path = dataset.get('full_path')
                print(f'xml标注对象为空f{xml_path}')
                dataset.update({'background': False})
            voc_to_labelme.append(dataset)
        self.save_labelme(voc_to_labelme, self.output_dir, None)  # self.output_dir为空字符串也是可以的

    # @staticmethod
    # def analysis_xml(xml_path):
    #     # 定义labelme数据结构
    #     labelme_data = dict(
    #         version='4.5.14',
    #         flags={},
    #         shapes=[],
    #         imagePath=None,
    #         imageData=None,
    #         imageHeight=None,
    #         imageWidth=None
    #     )
    #     # 解析XML文件
    #     tree = ET.parse(xml_path)
    #     root = tree.getroot()
    #     # 查找所有的object节点
    #     object_nodes = root.iter('object')
    #     # 遍历object节点
    #     for obj in object_nodes:
    #         # 根据需要提取所需的信息
    #         name = obj.find('name').text
    #         # pose = obj.find('pose').text
    #         bndbox = obj.find('bndbox')
    #         xmin = float(bndbox.find('xmin').text)  # 把字符串转float类型
    #         ymin = float(bndbox.find('ymin').text)
    #         xmax = float(bndbox.find('xmax').text)
    #         ymax = float(bndbox.find('ymax').text)
    #         points = [[xmin, ymin], [xmax, ymax]]  # 坐标点计算，目前使用左上角的点和右下角的点计算
    #         shape = {"label": name, "points": points, "group_id": None, "shape_type": "rectangle", "flags": {}, 'text': None}
    #         labelme_data.get('shapes').append(shape)
    #     return labelme_data

    @staticmethod
    def analysis_xml(xml_path):
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

        # 解析XML文件
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 提取图片宽高
        size_node = root.find('size')
        if size_node is not None:
            labelme_data['imageWidth'] = int(size_node.find('width').text)
            labelme_data['imageHeight'] = int(size_node.find('height').text)

        # 查找所有的object节点
        object_nodes = root.iter('object')
        for obj in object_nodes:
            name = obj.find('name').text

            # 优先处理 polygon 多边形
            polygon_node = obj.find('polygon')
            if polygon_node is not None:
                points = []
                i = 1
                while True:
                    x_tag = polygon_node.find(f'x{i}')
                    y_tag = polygon_node.find(f'y{i}')
                    if x_tag is None or y_tag is None:
                        break
                    x = float(x_tag.text)
                    y = float(y_tag.text)
                    points.append([x, y])
                    i += 1

                if len(points) >= 3:  # 至少三个点构成多边形
                    shape = {
                        "label": name,
                        "points": points,
                        "group_id": None,
                        "shape_type": "polygon",
                        "flags": {},
                        "text": None
                    }
                    labelme_data['shapes'].append(shape)

            else:
                # 兼容标准 VOC 格式的 bndbox
                bndbox = obj.find('bndbox')
                if bndbox is not None:
                    xmin = float(bndbox.find('xmin').text)
                    ymin = float(bndbox.find('ymin').text)
                    xmax = float(bndbox.find('xmax').text)
                    ymax = float(bndbox.find('ymax').text)
                    points = [[xmin, ymin], [xmax, ymax]]
                    shape = {
                        "label": name,
                        "points": points,
                        "group_id": None,
                        "shape_type": "rectangle",
                        "flags": {},
                        "text": None
                    }
                    labelme_data['shapes'].append(shape)

        return labelme_data
