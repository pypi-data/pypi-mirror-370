# -*- coding: utf-8 -*-
# @Time : 2022/2/18 17:49
# @Author : Zhan Yong
from setuptools import find_packages
from setuptools import setup
import io

with io.open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


def get_install_requires():
    install_requires = [
        'tqdm',  # 更新指定包的版本，或者通过 >= 指定最小版本
        'opencv_python',  # for PyInstaller
        'numpy',
        'pycocotools',
        'prettytable',
        'shapely',
        'psutil',
        'pypinyin',
        'Pillow',
        'aiofiles',
        'moviepy',
        'scikit-learn',
        'pandas',
        'openpyxl',
        'xlrd',
        'resource'
        # 'google-cloud-translate'  # 谷歌翻译包
    ]
    return install_requires


setup(
    # 取名不能够用_会自动变-   ccdt
    name='ccdt',
    version='2.1.162',
    # metadata_version="2.1",  # 强制使用 Metadata 2.1
    packages=find_packages(exclude=['data']),
    include_package_data=True,
    package_data={
        'ccdt': ['fonts/*.ttf'],  # ✅ 打包 ttf 字体
    },
    install_requires=get_install_requires(),
    author='zhanyong',
    author_email='zhan.yong@chipeak.com',
    description='AI数据转换工具箱',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chipeak/chipeak_cv_data_tool',
    project_urls={
        'Bug Tracker': 'https://github.com/chipeak/chipeak_cv_data_tool/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
    ],

    # package_data={'cpdt': ['icons/*', 'config/*.yaml']},
    # pip install paddleocr==2.6.1.3 paddlepaddle==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
    # 这两个版本经过验证：
    # 包名	        版本	    Python 3.8 支持	    说明
    # paddleocr	    2.6.1.3	    ✅ 是	            支持检测+识别+矫正（cls）
    # paddlepaddle	2.5.2	    ✅ 是	            支持 CPU 使用
    # download https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_det_infer.tar to C:\Users\jk/.paddleocr/whl\det\ch\ch_PP-OCRv3_det_infer\ch_PP-OCRv3_det_infer.tar
    # download https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_rec_infer.tar to C:\Users\jk/.paddleocr/whl\rec\ch\ch_PP-OCRv3_rec_infer\ch_PP-OCRv3_rec_infer.tar
    # download https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar to C:\Users\jk/.paddleocr/whl\cls\ch_ppocr_mobile_v2.0_cls_infer\ch_ppocr_mobile_v2.0_cls_infer.tar
    entry_points={
        'console_scripts': [
            'ccdt=ccdt.dataset.main:main',
            # 视频切片集成
            'video=ccdt.video_tool.video_main:main',
            # 数据分配，分配图片，分配labelme
            #  'video=',
            # 'file',
            # 'labelme=labelme.__main__:main',
            # 'labelme_draw_json=labelme.cli.draw_json:main',
            # 'labelme_draw_label_png=labelme.cli.draw_label_png:main',
            # 'labelme_json_to_dataset=labelme.cli.json_to_dataset:main',
            # 'labelme_on_docker=labelme.cli.on_docker:main',
        ],
    },
    # package_dir={'': 'src'},
    # packages=setuptools.find_packages(where='src'),
    # packages=find_packages(exclude=('configs', 'tools', 'demo')),
    # package_dir={'chipeak_data_tool': 'chipeak_data_tool'},
    # packages=setuptools.find_packages(include=['chipeak_data_tool.*']),
    # python_requires='>=3.7',
)



