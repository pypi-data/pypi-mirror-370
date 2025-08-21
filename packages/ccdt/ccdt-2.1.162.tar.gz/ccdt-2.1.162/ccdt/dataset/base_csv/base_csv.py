# 计算机登录用户: jk
# 系统日期: 2024/8/3 10:43
# 项目名称: chipeak_cv_data_tool
# 开发者: zhanyong
from pathlib import Path
from ccdt.dataset import *
import pandas as pd
import os
import shutil


class BaseCsv(BaseLabelme):
    def __init__(self, *args, **kwargs):
        self.output_csv = None
        self.output_dir = None
        # 在这里定义labelme数据结构格式初始化
        super(BaseCsv, self).__init__(*args, **kwargs)

    def labelme2csv(self):
        """
        labelme转csv
        """
        data = []
        for dataset in self.datasets:
            image_path = os.path.relpath(os.path.join(dataset.get('image_dir'), dataset.get('image_file'))).replace('\\', '/')
            image_width = dataset.get('image_width')
            image_height = dataset.get('image_height')
            stem = Path(dataset.get('input_dir')).stem
            self.output_csv = os.path.join(dataset.get('output_dir'), stem + '.csv')
            self.output_dir = os.path.join(dataset.get('output_dir'), dataset.get('image_dir'), stem)
            os.makedirs(self.output_dir, exist_ok=True)
            shutil.copy(dataset.get('full_path'), self.output_dir)
            if dataset.get('labelme_info') is not None:
                for shape in dataset.get('labelme_info').get('shapes'):
                    label = shape.get('label', '')
                    points = shape.get('points', [])
                    xmin = int(min(point[0] for point in points))
                    ymin = int(min(point[1] for point in points))
                    xmax = int(max(point[0] for point in points))
                    ymax = int(max(point[1] for point in points))
                    data.append({
                        'image_path': image_path,
                        'width': image_width,
                        'height': image_height,
                        'label': label,
                        'xmin': xmin,
                        'ymin': ymin,
                        'xmax': xmax,
                        'ymax': ymax
                    })
        # 将数据写入 CSV
        self.save_csv_image_file(data, self.output_csv)

    @staticmethod
    def save_csv_image_file(data_df, output_csv):
        try:
            df = pd.DataFrame(data_df)
            df.to_csv(output_csv, index=False)
            print(f"CSV file has been saved to {output_csv}")
        except Exception as e:
            print(e)
