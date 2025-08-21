# 计算机登录用户: jk
# 系统日期: 2023/11/7 17:41
# 项目名称: chipeak_cv_data_tool
# 开发者: zhanyong
import os
from pathlib import Path
import ast
import json
from ccdt.dataset import *
from collections import defaultdict
import time
import itertools
import hashlib
import ccdt.dataset.utils.labelme_load


def _isArrayLike(obj):
    return hasattr(obj, '__iter__') and hasattr(obj, '__len__')

# coco转labelme
class CocoToLabelme(BaseLabelme):
    # 当前设计的coco转labelme，主要是图像文件没有对应的注释，注释都在coco文件中
    def __init__(self, *args, **kwargs):
        # 定义labelme保存数据的对象，通过coco从新封装每一张图像，对应的json属性，并追加列表，使用labelme的基类中self.save_labelme()保存方法
        self.input_dir = args[0][0].get('input_dir')
        self.coco_path = args[0][0].get('input_coco_file')  # 获取coco文件路径
        # load dataset
        self.dataset, self.anns, self.cats, self.imgs = dict(), dict(), dict(), dict()
        self.img_to_anns, self.cat_to_imgs = defaultdict(list), defaultdict(list)
        if self.coco_path is not None:
            print('loading annotations into memory...')
            tic = time.time()
            with open(self.coco_path, 'r') as f:
                dataset = json.load(f)
            assert type(dataset) == dict, 'annotation file format {} not supported'.format(type(dataset))
            print('Done (t={:0.2f}s)'.format(time.time() - tic))
            self.dataset = dataset
            self.create_index()  # 创建索引
        super(CocoToLabelme, self).__init__(*args, **kwargs)

    def coco2labelme(self):
        labelme_datasets = list()
        # 获取每一张图片的id
        img_ids = self.get_img_ids()
        for img_id in img_ids:
            dataset = {  # 每次迭代一张图像，就重新初始化
                "image_dir": "00.images",  # 封装图像文件存储目录的相对路径，方便后期路径重组及拼接
                "image_file": "",  # 封装图像文件名称
                "image_width": "",  # 封装图像宽度
                "image_height": "",  # 封装图像高度
                "labelme_dir": "01.labelme",  # 封装json文件存储目录的相对路径，方便重组及拼接
                "labelme_file": "",  # 封装json文件名称
                "input_dir": "",  # 封装处理数据，输入路径目录
                "output_dir": "",  # 封装输出路径目录
                "http_url": "",  # 封装http对象存储服务访问服务地址
                "error_path": "",  # 错误数据存放总目录，不分错误类别，一般为输出路径+error_path拼接，写死的自定义目录。coco转labelme时用不上。
                "labelme_info": None,
                "background": True,  # 封装一张图像属于负样本还是正样本，默认为True，正样本，有标注
                "full_path": "",  # 封装一张图像绝对路径
                "json_path": "",  # 封装一张图像对应json文件绝对路径，用于输出时写文件的路径使用
                "md5_value": "",  # 封装一张图像MD5值，用于唯一性判断
                "relative_path": "",  # 封装图像使用标注工具读取相对路径，格式为：..\\00.images\\000000000419.jpg
                "only_annotation": False,  # 封装是图像还是处理图像对应标注内容的判断条件，默认图片和注释文件一起处理
            }
            image_attr = self.load_imgs(img_id)[0]  # 根据图像索引，获取图像属性
            ann_ids = self.get_ann_ids(img_ids=img_id)  # 根据图像索引，获取注释索引
            anns = self.load_anns(ann_ids)  # 根据注释索引，获取注释属性
            if ann_ids:  # 当注释id不为空的情况下，才进行标注属性封装，才写json文件，否则为背景，无需写json
                obj_path = Path(image_attr.get("file_name"))
                relative_path = os.path.join('..', '00.images', image_attr.get("file_name"))
                json_name = obj_path.stem + ".json"
                image_width = image_attr.get('width')
                image_height = image_attr.get('height')
                dataset.update({'input_dir': self.input_dir})
                dataset.update({'imagePath': relative_path})
                dataset.update({'image_width': image_width})
                dataset.update({'image_height': image_height})
                dataset.update({'labelme_file': json_name})
                dataset.update({'image_file': image_attr.get("file_name")})
                full_path = os.path.join(dataset.get('input_dir'), dataset.get('image_dir'), dataset.get('image_file'))
                json_path = os.path.join(dataset.get('input_dir'), dataset.get('labelme_dir'), dataset.get('labelme_file'))
                md5value = self.calculate_file_md5(full_path, dataset)
                dataset.update({'full_path': full_path})
                dataset.update({'json_path': json_path})
                dataset.update({'md5_value': md5value})
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
                for index, ann in enumerate(anns):  # enumerate为一个可迭代对象，它的作用是为可迭代对象的每个元素分配一个唯一的索引，以便在迭代时轻松获取元素的索引和值。
                    # 取到同一张图片的多个注释属性
                    category_id = ann['category_id']
                    # 获取坐标框
                    bbox = ann['bbox']
                    # 坐标切割
                    bbox = [bbox[0:2], bbox[2:4]]
                    # 左上角的坐标(x,y)右上角的坐标(x,y+h)左下角的坐标(x+w,y)右下角的坐标(x+w,y+h)，一般coco文件中的注释坐标都为中心点坐标。
                    points = [bbox[0], [bbox[0][0] + bbox[1][0], bbox[0][1] + bbox[1][1]]]
                    # 通过类别id获取类别名称
                    cats = self.load_cats(category_id)[0]
                    # 取到类别名称
                    name = cats['name']
                    # 只处理带矩形框，并转labelme
                    shape = {"label": name, "points": points, "group_id": None, "shape_type": "rectangle", "flags": {}, 'text': None}
                    shapes.append(shape)
                # labelme_data['shapes'] = shapes
                labelme_data.update({'shapes': shapes})
                labelme_data.update({'imagePath': relative_path})
                labelme_data.update({'imageWidth': image_width})
                labelme_data.update({'imageHeight': image_height})
                labelme_data.update({'md5Value': md5value})
                dataset.update({'labelme_info': labelme_data})
                labelme_datasets.append(dataset)
        # 保存labelme数据集合
        self.save_labelme(labelme_datasets, self.output_dir, None)  # self.output_dir为空字符串也是可以的

    def create_index(self):
        # create index
        print('creating index...')
        anns, cats, imgs = {}, {}, {}
        img_to_anns, cat_to_imgs = defaultdict(list), defaultdict(list)
        if 'annotations' in self.dataset:
            for ann in self.dataset['annotations']:
                img_to_anns[ann['image_id']].append(ann)
                anns[ann['id']] = ann

        if 'images' in self.dataset:
            for img in self.dataset['images']:
                imgs[img['id']] = img

        if 'categories' in self.dataset:
            for cat in self.dataset['categories']:
                cats[cat['id']] = cat

        if 'annotations' in self.dataset and 'categories' in self.dataset:
            for ann in self.dataset['annotations']:
                cat_to_imgs[ann['category_id']].append(ann['image_id'])

        print('index created!')

        # create class members
        self.anns = anns
        self.img_to_anns = img_to_anns  # 图像与类别对应关系
        self.cat_to_imgs = cat_to_imgs  # 类别与图像对应关系
        self.imgs = imgs  # 图像属性
        self.cats = cats  # 类别

    def get_img_ids(self, img_ids=None, cat_ids=None):
        """
         Get img ids that satisfy given filter conditions.
        :param img_ids (int array) : get imgs for given ids
        :param cat_ids (int array) : get imgs with all given cats
        :return: ids (int array)  : integer array of img ids
        @param img_ids: 
        @param cat_ids: 
        @return: 
        """
        if cat_ids is None:
            cat_ids = []
        if img_ids is None:
            img_ids = []
        img_ids = img_ids if _isArrayLike(img_ids) else [img_ids]
        cat_ids = cat_ids if _isArrayLike(cat_ids) else [cat_ids]

        if len(img_ids) == len(cat_ids) == 0:
            ids = self.imgs.keys()
        else:
            ids = set(img_ids)
            for i, catId in enumerate(cat_ids):
                if i == 0 and len(ids) == 0:
                    ids = set(self.cat_to_imgs[catId])
                else:
                    ids &= set(self.cat_to_imgs[catId])
        return list(ids)

    def load_imgs(self, ids=None):
        """
        Load anns with the specified ids.
        :param ids (int array)       : integer ids specifying img
        :return: imgs (object array) : loaded img objects
        @param ids: 
        """
        if ids is None:
            ids = []
        if _isArrayLike(ids):
            return [self.imgs[id] for id in ids]
        elif type(ids) == int:
            return [self.imgs[ids]]

    def get_ann_ids(self, img_ids=None, cat_ids=None, area_rng=None, iscrowd=None):
        """
        Get ann ids that satisfy given filter conditions. default skips that filter
        :param img_ids  (int array)     : get anns for given imgs
               cat_ids  (int array)     : get anns for given cats
               area_rng (float array)   : get anns for given area range (e.g. [0 inf])
               iscrowd (boolean)       : get anns for given crowd label (False or True)
        :return: ids (int array)       : integer array of ann ids
        @param iscrowd:
        @param area_rng:
        @param cat_ids:
        @param img_ids:
        """
        if area_rng is None:
            area_rng = []
        if cat_ids is None:
            cat_ids = []
        if img_ids is None:
            img_ids = []
        img_ids = img_ids if _isArrayLike(img_ids) else [img_ids]
        cat_ids = cat_ids if _isArrayLike(cat_ids) else [cat_ids]

        if len(img_ids) == len(cat_ids) == len(area_rng) == 0:
            anns = self.dataset['annotations']
        else:
            if not len(img_ids) == 0:
                lists = [self.img_to_anns[imgId] for imgId in img_ids if imgId in self.img_to_anns]
                anns = list(itertools.chain.from_iterable(lists))
            else:
                anns = self.dataset['annotations']
            anns = anns if len(cat_ids) == 0 else [ann for ann in anns if ann['category_id'] in cat_ids]
            anns = anns if len(area_rng) == 0 else [ann for ann in anns if area_rng[0] < ann['area'] < area_rng[1]]
        if iscrowd is not None:
            ids = [ann['id'] for ann in anns if ann['iscrowd'] == iscrowd]
        else:
            ids = [ann['id'] for ann in anns]
        return ids  # 返回注释索引

    def load_anns(self, ids=None):
        """
        Load anns with the specified ids.
        :param ids (int array)       : integer ids specifying anns        :return:  (object array) : loaded ann objects
        @param ids:
        """
        if ids is None:
            ids = []
        if _isArrayLike(ids):
            return [self.anns[id] for id in ids]
        elif type(ids) == int:
            return [self.anns[ids]]

    def load_cats(self, ids=None):
        """
        Load cats with the specified ids.
        :param ids (int array)       : integer ids specifying cats        :return:  (object array) : loaded cat objects
        @param ids:
        """
        if ids is None:
            ids = []
        if _isArrayLike(ids):
            return [self.cats[id] for id in ids]
        elif type(ids) == int:
            return [self.cats[ids]]

    @staticmethod
    def calculate_file_md5(file_path, dataset):
        """
        functools.lru_cache装饰器对文件的MD5值进行了缓存，暂时没有用
        采用最近最少使用的缓存策略，最多缓存128个不同的文件的MD5值
        这样可以大大减少重复计算MD5值的次数，节约计算资源，提高程序性能。
        """

        # import ccdt.dataset.utils.labelme_load
        # from ccdt.dataset.utils.labelme_load import calculate_sha3_512
        # content = utils.labelme_load.LabelmeLoad.read_file(file_path)
        # sha3_512 = utils.labelme_load.LabelmeLoad.calculate_sha3_512(content)
        # print(sha3_512)
        try:
            with open(file_path, 'rb') as f:
                hasher = hashlib.sha3_512()
                buf = f.read(8192)
                while buf:
                    hasher.update(buf)
                    buf = f.read(8192)
                return hasher.hexdigest()
        except Exception as e:
            print(e)
            print("图片存放目录不存在00.images目录，该目录为标准，必须手动创建后把图像移动到00.images目录中，再次重新执行指令")
            images_path = os.path.join(dataset.get('input_dir'), dataset.get('image_dir'))
            json_path = os.path.join(dataset.get('input_dir'), dataset.get('labelme_dir'))
            os.makedirs(images_path, exist_ok=True)
            os.makedirs(json_path, exist_ok=True)
            print("请在此{}".format(dataset.get('input_dir')) + "   路径下移动图像到00.images目录")
            exit()
