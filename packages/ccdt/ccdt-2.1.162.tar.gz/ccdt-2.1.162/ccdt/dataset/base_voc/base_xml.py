# 计算机登录用户: jk
# 系统日期: 2024/6/25 17:00
# 项目名称: chipeak_cv_data_tool
# 开发者: zhanyong
import os
import shutil
from ccdt.dataset import *
import xml.etree.ElementTree as ET
from pathlib import Path

# labelme转voc
class BaseXml(BaseLabelme):
    def __init__(self, *args, **kwargs):
        # 在这里定义labelme数据结构格式初始化
        super(BaseXml, self).__init__(*args, **kwargs)

    def labelme2xml(self):
        """
        labelme转xml数据集，即voc
        """
        for dataset in self.datasets:
            annotation = ET.Element('annotation')
            ET.SubElement(annotation, 'folder').text = ''  # 保障相对路径可以打开，文件夹写空，绝对路径需要指定为dataset.get('image_dir')
            ET.SubElement(annotation, 'filename').text = dataset.get('image_file')
            ET.SubElement(annotation, 'path').text = dataset.get('labelme_file')

            source = ET.SubElement(annotation, 'source')
            ET.SubElement(source, 'database').text = 'chipeak.com'

            size = ET.SubElement(annotation, 'size')
            ET.SubElement(size, 'width').text = str(dataset.get('image_width'))
            ET.SubElement(size, 'height').text = str(dataset.get('image_height'))
            ET.SubElement(size, 'depth').text = '3'  # Assuming RGB image

            ET.SubElement(annotation, 'segmented').text = '0'
            if dataset.get('labelme_info') is not None:
                for shape in dataset.get('labelme_info').get('shapes'):
                    label = shape['label']
                    points = shape['points']
                    xmin = int(min(point[0] for point in points))
                    ymin = int(min(point[1] for point in points))
                    xmax = int(max(point[0] for point in points))
                    ymax = int(max(point[1] for point in points))
                    obj = ET.SubElement(annotation, 'object')
                    ET.SubElement(obj, 'name').text = label
                    ET.SubElement(obj, 'pose').text = 'Unspecified'
                    ET.SubElement(obj, 'truncated').text = '0'
                    ET.SubElement(obj, 'difficult').text = '0'
                    bndbox = ET.SubElement(obj, 'bndbox')
                    ET.SubElement(bndbox, 'xmin').text = str(xmin)
                    ET.SubElement(bndbox, 'ymin').text = str(ymin)
                    ET.SubElement(bndbox, 'xmax').text = str(xmax)
                    ET.SubElement(bndbox, 'ymax').text = str(ymax)
                # Save XML file
                xml_str = ET.tostring(annotation, encoding='unicode')  # 使用 ET.tostring(annotation, encoding='unicode') 将 XML 树转换为字符串，这样可以避免自动生成的 XML 声明。
                self.save_xml_image_file(xml_str, dataset)

    @staticmethod
    def save_xml_image_file(xml_str, dataset):
        try:
            xml_filename = Path(dataset.get('image_file')).stem + '.xml'
            xml_path = os.path.join(dataset.get('output_dir'), dataset.get('image_dir'), xml_filename)
            image_dir = os.path.join(dataset.get('output_dir'), dataset.get('image_dir'))
            os.makedirs(image_dir, exist_ok=True)
            # 使用 with open(xml_path, 'w', encoding='utf-8') as f 手动写入 XML 字符串到文件。
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
            # tree.write(xml_path, encoding='utf-8', xml_declaration=True)
            shutil.copy(dataset.get('full_path'), image_dir)
        except Exception as e:
            print(e)
