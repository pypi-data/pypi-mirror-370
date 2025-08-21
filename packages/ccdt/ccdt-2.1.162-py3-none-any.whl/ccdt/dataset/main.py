# 计算机登录用户: jk
# 系统日期: 2023/5/17 9:45
# 项目名称: async_ccdt
# 开发者: zhanyong
import argparse
import ast
import asyncio
from ccdt.dataset import *
import time


def parser_args():
    parser = argparse.ArgumentParser()
    # input_datasets 是必须要传递的参数，可以是包含多个数据集路径的列表字典格式。
    parser.add_argument('input_datasets', type=str, help="labelme数据集路径、coco数据集路径，列表字典传参")
    parser.add_argument('--output-dir', type=str, help="保存路径")
    parser.add_argument('--output-format', type=str, help="输出功能格式，有labelme、coco")
    parser.add_argument('-f', '--function', type=str, required=True, help="功能参数:print,convert,filter,matting,rename,visualize,merge，只能输入单个")
    parser.add_argument('--filter-label', type=ast.literal_eval, help="类别筛选参数，单个与多个都可以输入")
    parser.add_argument('--exclude-if-only', type=ast.literal_eval, help="标签采样参数，排除某些标签为主的图片（即不希望看到的标签）")
    parser.add_argument('--include-focus', type=ast.literal_eval, help="标签采样参数，优先采集某些标签（即重点采集的标签）")
    # 当不输入--only_annotation，默认为False；输入--only_annotation，才会触发True值。False处理labelme和图片，True只处理labelme
    parser.add_argument('--only-annotation', action="store_true", help="默认False，是否只处理注释文件。是为True，否为False")
    parser.add_argument('--filter-shape-type', type=ast.literal_eval, help="形状筛选参数，单个与多个都可以输入")
    parser.add_argument('--input-coco-file', type=str, help="输入形状筛选参数，单个与多个都可以输入")
    parser.add_argument('--rename-attribute', type=ast.literal_eval, help="属性重命名，包含label、flags")
    parser.add_argument('--select-empty', action="store_true", help="默认False，是否保留背景类。是为True，否为False")
    parser.add_argument('--only-select-empty', action="store_true", help="默认False，是否只筛选背景数据。是为True，否为False")
    parser.add_argument('--only-select-shapes', action="store_true", help="默认False，是否只筛选标注有框的数据。是为True，否为False")
    parser.add_argument('--shapes-attribute', type=str, help="筛选属性，包含label（类别）、shape_type（类别形状）、flags（类别属性）")
    parser.add_argument('--filter-flags', type=ast.literal_eval, help="类别属性筛选，输入类别属性字典列表。比如person类下有，告警图片地址")
    parser.add_argument('--polygonVertex', type=ast.literal_eval, help="输入多边形列表坐标")
    parser.add_argument('--columns-fill', type=ast.literal_eval, help="输入except表格列号，列表")
    parser.add_argument('--column-titles', type=ast.literal_eval, help="输入except表格列号对应的标题")
    parser.add_argument('--column-content-type', type=ast.literal_eval, help="输入except表格列号，字典")
    parser.add_argument('--column-name', type=ast.literal_eval, help="excel表格列属性筛选，输入列名称。比如：视频源地址，手、脚、头")
    parser.add_argument('--algorithm-type', type=ast.literal_eval, help="算法类型筛选，输入算法类型名称。比如：安全帽，抽烟，区域入侵，烟雾")
    parser.add_argument('--file-formats', default=['.jpg', '.jpeg', '.png', '.JPEG', '.JPG', '.PNG', '.webp', '.bmp'], type=ast.literal_eval,
                        help="文件格式,其中,'.bmp','.gif','.tif',格式图像不做处理")
    parser.add_argument('--filter-combin', action="store_true", help="是否组合筛选，是为True，否为False")
    parser.add_argument('--extract-portion', type=int, help='按照指定份数平均抽取，比如400张图像，抽取10分，每份40张')
    parser.add_argument('--fps', type=int, help='视频每秒钟展示的帧数')
    parser.add_argument('--extract-text', type=ast.literal_eval, help='按照text字段的文本内容抽取')
    parser.add_argument('--select-cut', action="store_true", help="默认False即拷贝，是拷贝还是剪切。是为True移动，否为False拷贝")
    parser.add_argument('--judging-group-id-num', action="store_true", help="默认False即拷贝，有judging-group-id-num参则改变为True，否为False")
    parser.add_argument('--extract-amount', type=int, help='按照指定数量抽取，比如400张图像，抽取100张')
    parser.add_argument('--print-more', action="store_true", help="打印详细信息")
    parser.add_argument('--del-label', type=ast.literal_eval, help="删除label标签")
    parser.add_argument('--filter-polygon', type=ast.literal_eval, help="多边形列表")
    parser.add_argument('--judging-letter', type=ast.literal_eval, help="判断车牌字符串中是否存在，I，o,Q")
    parser.add_argument('--contained-of-object', type=ast.literal_eval, help="填写被截取目标框包含的标签名称")
    parser.add_argument('--label-name', type=str, help="自定义label标签，用于抽取份数时区别标注目录")
    parser.add_argument('--time', type=str, help="自定义时间段字符串")
    parser.add_argument('--http-url', type=str, help="minio文件对象存储中，网络文件统一资源定位器，http://192.168.1.235:9393/chipeak-dataset")
    parser.add_argument('--min-pixel', type=int, default=512, help='最小像素截图设置，默认512像素。即大于512像素的矩形框才进行截图')
    parser.add_argument('--judging-group', type=int, help='默认值为2个shape元素为一组，用于判断分组元素的数量')
    parser.add_argument('--epsilon', type=float, default=2,
                        help='手动标注时略微多框了 1~3 像素，使得框“略微越界”，但仍然可以认为是属于该人，默认2像素，值越小正确率越高')
    parser.add_argument('--judging-flags', type=ast.literal_eval, help="检查flags默认标注属性，是否符合标注准则")
    parser.add_argument('--judging-label', type=str, help="检查车牌默认分组属性，是否符合标注准则，车牌一定要打组，如果没有打组就筛选出来")
    parser.add_argument('--judging-polygon', type=int, help='检查多边形标注的点是否超出预期数量，比如4个点的多边形，不能出现5个')
    parser.add_argument('--judging-cross-the-border', type=str, help="检查标注形状是否超越原始图像边界")
    parser.add_argument('--point-number', type=int, help='点标注的数量，用于标注点排序时，追加标注点到列表中然后判断，是否满足标注规则')
    parser.add_argument('--automatic-correction', action="store_true", help="默认False，是否自动矫正标注形状超越图像边界情况。是为True，否为False")
    parser.add_argument('--rectangle-merge', action="store_true", help="默认False，填写参数代表为true，用于判断合并条件，该条件表示矩形框合并。是为True，否为False")
    parser.add_argument('--sync', action="store_true", help="默认False，填写参数代表为true，用于判断是同步处理，还是异步处理。是为True，否为False")
    parser.add_argument('--threshold', type=float, help="阈值参数，模型预测数据集，设定的阈值")
    parser.add_argument('--leak-check', action="store_true", help="默认False，填写参数代表为true，用于筛选漏检出数据。是为True，否为False")
    parser.add_argument('--randomize', action="store_true", help="默认False，填写参数代表为true，用于列表随机化。是为True，否为False")
    parser.add_argument('--test-ratio', type=float, default=0.2, help='默认测试集比例值')
    parser.add_argument('--train-ratio', type=float, default=0.8, help='默认训练集比例值')
    parser.add_argument('--small-ratio', type=float, default=0.01, help='默认小目标比例')
    parser.add_argument('--medium-ratio', type=float, default=0.1, help='默认中目标比例')
    parser.add_argument('--error-check', action="store_true", help="默认False，填写参数代表为true，用于筛选误检出数据。是为True，否为False")
    parser.add_argument('--right-check', action="store_true", help="默认False，填写参数代表为true，用于筛选正确检出数据。是为True，否为False")
    # parser.add_argument('--error-check', action="store_true", help="默认False，填写参数代表为true，用于筛选正确检出数据。是为True，否为False")
    parser.add_argument('--coco-to-bbox', action="store_true", help="默认False，填写参数代表为true，用于判断多边形转矩形框。是为True，否为False")
    parser.add_argument('--background', action="store_true", help="默认False，填写参数代表为true，用于把系统输出的json转换为labelme对应的json。是为True，否为False")
    parser.add_argument('--choose-more', action="store_true",
                        help="默认False，填写参数代表为true，用于获取更多数据，包含通道阻塞和通道占用，不填写则只获取通道占用数据。是为True，否为False")
    parser.add_argument('--choose_polygon', action="store_true", help="默认False，填写参数代表为true，不填写代表不保存多边形，填写则保存多边形。是为True，否为False")
    parser.add_argument('--fill-rules', action="store_true", help="默认False，填写参数代表为true，用于判断是否为chipeak系统上报数据")
    parser.add_argument('--statistics-check', action="store_true", help="默认False，填写参数代表为true，用于统计结果勾选记录")
    parser.add_argument('--is-PCA', action="store_true",
                        help="默认False，填写参数代表为true，用于直方图降维条件判断。是为True，但会造成信息丢失，否为False，信息更准确")
    parser.add_argument('--delete', action="store_true", help="默认False，填写参数代表为true，用于删除勾选数据。是为True，否为False")
    parser.add_argument('--flags-true', action="store_true", help="默认False，填写参数代表为true，用于删除勾选数据。是为True，否为False")
    parser.add_argument('--opt', type=str, help="opt值为local表示局部直方图计算，opt值为global表示全局直方图计算")
    parser.add_argument('--json-file', type=str, help="图像文件约定目录规则,00.images")
    parser.add_argument('--image-file', type=str, help="json文件约定目录规则，01.labelme")
    parser.add_argument('--helmet-true', type=str, help="分类目录规则,helmet")
    parser.add_argument('--helmet-false', type=str, help="分类目录规则，no_select")
    parser.add_argument('--mv5-value', type=str, help="分类目录规则，no_select")
    parser.add_argument('--flags-value', type=ast.literal_eval, help="填写flags的字典值")
    parser.add_argument('--fields', type=str, help="csv文件某列字段")
    parser.add_argument('--intercept-the-object', type=str, help="填写指定截取标注对象的标签名称")
    parser.add_argument('--slice-width', type=int, help="切图宽度")
    parser.add_argument('--slice-height', type=int, help="切图高度")
    parser.add_argument('--stride', type=int, help="滑动步长，推荐50%重叠")
    parser.add_argument('--image-check', action="store_true",
                        help="默认False，填写参数代表为true即开启检查功能并移除图像，用于检查图像格式、通道、完整性及其它问题。是为True，否为False")
    args = parser.parse_args()

    if args.function == 'filter_positive':  # 筛选正样本
        return args
    elif args.function == 'filter_negative':  # 筛选负样本
        return args
    elif args.function == 'filter_label':  # 筛选负样本
        return args
    elif args.function == 'filter_images':  # 筛选训练样本
        return args
    elif args.filter_label and args.function == 'filter_label':  # 按照标注目标的标签进行筛选
        return args
    elif args.filter_flags and args.function == 'filter_flags':  # 按照标注目标的flags属性筛选
        return args
    elif args.filter_shape_type and args.function == 'filter_shape_type':  # 按标注形状进行筛选
        return args
    # 重命名
    elif args.rename_attribute and args.function == 'rename':  # 标注属性重命名，包含label标签、flags、
        return args
    # labelme转coco，coco转labelme
    elif args.function == 'convert':
        return args
    # 抠图，单数据集、多数据集
    elif args.function == 'matting':
        return args
    # 可视化
    elif args.function == 'visualize':
        return args
    # 合并类别筛选数据
    elif args.function == 'merge':
        return args
    elif args.function == 'relation':  # 寻找shape标注形状包含关系，大矩形框包含小多边形
        return args
    elif args.function == 'print':  # 打印labelme标注信息，图像属性信息
        return args
    elif args.function == 'check_image_path':  # 检查标注路径
        return args
    elif args.function == 'save_chipeak_data':  # 处理save_chipeak_data
        return args
    elif args.function == 'delete':  # 按照标注标签删除标注
        return args
    elif args.function == 'extract':  # 抽取labelme数据集，包含按照指定份数抽取，按照图像张数抽取，可以拷贝、剪切
        return args
    elif args.function == 'duplicate':  # 对数据集去重
        return args
    elif args.function == 'compress':  # 对抽取数据集进行压缩
        return args
    elif args.function == 'check':  # 检查分组标注常见错误，包含：一组标注少一个标注框或点，一组标注的group_id值不对。
        return args
    elif args.function == 'correct' or args.function == 'original':  # 对多边形车牌标注进行排序，截取图像，矫正形状摆放位置
        return args
    elif args.function == 'cross':  # 针对标注形状超越图像边界情况，使用程序自动矫正
        return args
    elif args.function == 'pinyin':  # 汉字转拼音
        return args
    elif args.function == 'IOU':  # 标注数据与模型预测数据进行比较，给出漏检、误检、检出、完全预测正确、部分预测正确、完全预测错误、部分预测错误
        return args
    elif args.function == 'compare':  # 误检与漏检比较功能，把MD5值相同的留下
        return args
    elif args.function == 'threshold_filter':  # 阈值筛选，根据不同的阈值挑选不同的labelme数据集
        return args
    elif args.function == 'Bhattacharyya':  # 图像内容相似度去重,计算直方图之间的距离，使用Bhattacharyya（巴氏距离）距离，它衡量了两个概率分布之间的相似程度，它直接基于直方图的概率分布计算。
        return args
    elif args.function == 'mosaic':  # 马赛克
        return args
    elif args.function == 'create_dir':  # 创建00.images和01.labelme目录规则
        return args
    elif args.function == 'flags':  # 根据目录判断，设置flags属性
        return args
    elif args.function == 'md5':  # 对每张图像的标注文件赋值MD5
        return args
    elif args.function == 'video_mark_convert_labelme':  #
        return args
    elif args.function == 'change':  # 把系统输出格式，转换为labelme标注工具可读格式。
        return args
    elif args.function == 'rename_file_name':  # 把中文文件名称，重命名为英文
        return args
    elif args.function == 'soft_deletion':  # 把json数据删除，属于软删除，等同于只拷贝一份图像，原始数据保留
        return args
    elif args.function == 'crop':  # 把目标检测标注的矩形框，截取图像
        return args
    elif args.function == 'check_format':  # 检查图像是否存在，格式不对、通道不对、内容完整性不对等问题
        return args
    elif args.function == 'move':  # 移动文件，临时功能
        return args
    elif args.function == 'modify_flags':  # 修改flags字典值
        return args
    elif args.function == 'filter_flags_true':  # 筛选flags字典值为真的数据
        return args
    elif args.function == 'ratio':  # 筛选flags字典值为真的数据
        return args
    elif args.function == 'pinyin_images':  # 针对分类图像数据，没有labelme的情况，把文件夹中文转换为拼音
        return args
    elif args.function == 'category_name':  # 打印分类类别名称
        return args
    elif args.function == 'optimize':  # 优化截取车和车牌标注逻辑算法
        return args
    elif args.function == 'excel':  # 提取excel表格某列数据的url地址，并下载
        return args
    elif args.function == 'file_name':  # 同步重命名文件名称
        return args
    elif args.function == 'draw_video':  # 图片合并视频并绘制标注属性
        return args
    elif args.function == 'blacked':  # 目标矩形框涂黑操作
        return args
    elif args.function == 'csv':  # csv文件处理，提前某列字段数据
        return args
    elif args.function == 'sahi':  # 滑窗切图
        return args
    elif args.function == 'intercept':  # 截取标注的人矩形框图片，并包含在内的其它矩形框标注
        return args
    elif args.function == 'mix':  # 计算标注目标与图像面积占比，划分保留大、中、小、的标注目标为labelme数据集功能。
        return args
    elif args.function == 'sampling':  # 目标检测，标注数据的标签采样功能
        return args
    else:
        assert not args.function, '传入的操作功能参数不对:{}'.format(args.function)


def main():
    # async def main():
    args = parser_args()
    # print(args)
    # 把字符串中，转义字符转换成，列表内存储字典元素.
    input_datasets_list = ast.literal_eval(args.input_datasets.replace('\\', '/'))
    if args.sync:  # 同步读写数据处理
        data_info = LabelmeLoad(args, input_datasets_list)  # 初始化输入参数
        if args.function == 'compress':  # 对抽取数据集进行压缩。数据压缩无需对数据进行封装后操作
            async_time = time.time()
            zip_package = data_info.compress_labelme()  # 封装压缩路径及压缩对象
            data_info.make_compress(zip_package)  # 开始压缩
            print('数据读取、压缩使用同步计算耗时')
            print(time.time() - async_time)
        if args.function == 'pinyin':
            data_info.hanzi_to_pinyin()  # 对中文路径转拼音后，重新输出
        if args.function == 'file_name':
            data_info.rename_file_name()  # 重命名文件名称
        if args.function == 'pinyin_images':
            data_info.hanzi_to_pinyin_images()  # 对中文路径转拼音后，只处理有图像的情况，没有labelme
        if args.function == 'check_format':  # 检查图像格式
            data_info.check_images_format()
        if args.function == 'category_name':  # 检查图像格式
            data_info.print_icategory_name(args)
        if args.function == 'excel':  # 获取execl表格某列数据的url地址，并下载
            data_info.get_excel_url_data(args)
        elif args.function == 'ratio':  # 火柴人图像，按比例划分测试集和训练集
            data_info.ratio_split(args)
        elif args.function == 'csv':  # 获取csv文件中的url地址数据
            data_info.extract_fields_csv(args)

    else:  # 异步读写数据处理，存在少部分同步写数据处理
        async_time = time.time()
        data_info = LabelmeLoad(args, input_datasets_list)  # 初始化输入参数
        # 获取当前正在运行的事件循环，从而可以将异步任务添加到事件循环中执行。在等待IO操作完成的同时，利用CPU计算力进行其他计算，从而提高计算效率
        dataset_info = asyncio.run(data_info.recursive_walk(input_datasets_list[0].get('input_dir'), args))
        print('数据读取使用异步计算耗时')
        print(time.time() - async_time)
        dataset = BaseLabelme(dataset_info)  # 初始化labelme基类
        if args.function == 'merge':  # 合并功能
            if args.rectangle_merge:  # 删除人工标注矩形框，然后与模型预测出来的矩形框进行合并功能
                # 加载模型预测的labelme数据集
                model_dataset_info = asyncio.run(data_info.recursive_walk(input_datasets_list[0].get('model_input_dir'), args.function))
                # 先删除人工标注的矩形框
                # original_dataset_info = dataset.del_label(args.del_label)
                dataset.labelme_rectangle_merge(args, model_dataset_info)
            else:
                dataset.merge_labelme(args)  # 人工标注数据，根据label拆分后，自动合并实现功能，所有标签合并一起，只要MD5值相同的文件就进行合并。
            # BaseLabelme.merge(datasets)
        elif args.function == 'matting':  # 抠出标注位置保存labelme
            dataset.intercept_coordinates()
        elif args.function == 'optimize':  # 车和车牌标注优化
            dataset.intercept_coordinates_optimize()
        elif args.function == 'duplicate':  # 对labelme数据集进行去重，重复的图片就删除
            dataset.duplicate_images()
        elif args.function == 'crop':
            dataset.crop_objs(args)  # 目标检测矩形框，截取图像
        elif args.function == 'convert':  # 转换功能，包含labelme转coco，coco转labelme
            if args.output_format == 'labelme':  # coco转labelme
                # 由于dataset_info封装的数据集，无法快速索引，在coco转labelme的时候，从新封装该对象，无需传入labelme基类中
                coco_to_labelme = CocoToLabelme(input_datasets_list)
                coco_to_labelme.coco2labelme()
                # dataset.save_labelme(args.output_dir, None)  # 如果输出路径为空，就直接修改输入目录下的json文件，不为空则重新拷贝图像文件与重写json文件
            elif args.output_format == 'coco':  # labelme转coco
                coco = BaseCoco(dataset_info)
                coco.self2coco(args)
            elif args.output_format == 'voc':  # voc转labelme
                voc = BaseVoc(dataset_info, input_datasets_list[0].get('input_xml_dir'))
                voc.voc2labelme()
            elif args.output_format == 'txt':  # 视频标注转labelme，txt转labelme
                txt = BaseTxt(dataset_info, input_datasets_list[0].get('input_txt_dir'))
                txt.txt2labelme()
            elif args.output_format == 'sys':  # 把系统输出格式，转换为labelme标注工具可读格式。
                sys = BaseSys(dataset_info, args)
                sys.sys2labelme(args)
            elif args.output_format == 'newbie':  # 把系统输出格式，转换为labelme标注工具可读格式。
                sys = BaseSys(dataset_info, args)
                sys.newbie2labelme()
            elif args.output_format == 'polygon':  # 把多边形坐标写入labelme
                sys = BaseSys(dataset_info, args)
                sys.polygon2labelme()
            elif args.output_format == 'excel':  # 把except表格自动填充图片和车牌号
                sys = BaseSys(dataset_info, args)
                sys.labelme2excel()
            elif args.output_format == 'xml':  # 把labelme转xml格式，即VOC
                xml = BaseXml(dataset_info, args)
                xml.labelme2xml()
            elif args.output_format == 'yolo':  # 把labelme转yolo格式
                yolo = BaseYolo(dataset_info, args)
                yolo.labelme2yolo()
            elif args.output_format == 'csv':  # 把labelme转csv格式
                csv = BaseCsv(dataset_info, args)
                csv.labelme2csv()
            elif args.output_format == 'yolo_to_labelme':  # yolo转labelme
                voc = BaseYolo(dataset_info, args)
                voc.yolo2labelme()
        elif args.function == 'rename':  # 重命名label标签功能
            dataset.rename_labelme(args)
            # dataset.save_labelme(args.output_dir, None, None)
        # elif args.function == 'visualize':  # 可视化功能
        # dataset.visualization(args.output_dir)
        elif args.function == 'filter_positive':  # 筛选正样本
            dataset.filter_positive(args)
        elif args.function == 'filter_negative':  # 筛选负样本
            dataset.filter_positive(args)
        elif args.function == 'filter_images':  # 筛选训练样本数据
            dataset.filter_images(args)
        elif args.function == 'filter_label':  # 筛选，指定label标签数据集，默认正样本
            dataset.filter_label(args)
        elif args.function == 'filter_flags':  # 筛选，标注label下的flags类别数据集，默认正样本
            dataset.filter_flags(args)
        elif args.function == 'print':  # 打印功能
            dataset.__repr__()
        elif args.function == 'check_image_path':  # 检查image_path功能
            dataset.check_image_path(args)
        elif args.function == 'save_chipeak_data':  # 检查image_path功能
            dataset.save_chipeak_data(args)
        elif args.function == 'delete':  # 删除指定标签类别标注数据集
            dataset.del_label(args.del_label)
            print(f'保存指定label类别进行删除的labelme数据集')
            dataset.save_labelme(args.output_dir, None, None)
        elif args.function == 'extract':  # 抽取labelme数据集功能，指定份数抽取，只允许拷贝；指定图像张数抽取，允许剪切、拷贝
            dataset.extract_labelme(args)
        elif args.function == 'relation':  # 寻找标注形状包含关系，进行自动打组
            dataset.relation_labelme(args)
        elif args.function == 'check':  # 检查分组标注常见错误，包含：一组标注少一个标注框或点，一组标注的group_id值不对。
            dataset.check_group_labelme(args)
        # correct为排序并矫正后的车牌截取，original为不排序也不矫正的车牌截取
        elif args.function == 'correct' or args.function == 'original':  # 排序，按照多边形，左上、右上、右下、左下的顺序排列4个顶点，截取图像，矫正形状摆放位置
            dataset.sort_correct_labelme(args)
        elif args.function == 'cross':  # 针对标注形状超越图像边界情况，使用程序自动矫正
            dataset.cross_boundary_correction(args)
        elif args.function == 'pinyin':  # 针对标注形状超越图像边界情况，使用程序自动矫正
            dataset.hanzi_to_pinyin()
        elif args.function == 'threshold_filter':  # 阈值筛选labelme数据集
            dataset.threshold_filter_labelme(args)
        elif args.function == 'Bhattacharyya':  # 图像内容相似度去重，计算直方图之间的距离，使用Bhattacharyya（巴氏距离）距离，它衡量了两个概率分布之间的相似程度，它直接基于直方图的概率分布计算。
            dataset.bhattacharyya_filter_labelme(args)
        # TP = 标注数据集有标注框，模型预测为有标注框，并且iou重合度高。=正确检出
        # FP = 标注数据集没有标注框，模型预测为有标注框。=误检出
        # FN = 标注数据集有标注框，模型预测为没有标注框。=漏检出
        # TN = 标注数据集没有标注框，模型预测结果也没有标注框。=背景

        # TP：模型正确检测到的正样本数量（即检测正确且标签为1的样本数）
        # FP：模型错误地将负样本检测为正样本的数量（即检测错误且标签为0的样本数）
        # FN：模型没能检测到的正样本数量（即检测错误且标签为1的样本数）
        # TN：模型正确地将负样本检测为负样本的数量（即检测正确且标签为0的样本数）

        # 召回率（Recall，也称为灵敏度或真阳性率）：Recall = TP / (TP + FN)，70 / (70 + 8)
        # 精确率（Precision，也称为查准率）：Precision = TP / (TP + FP)，70 / (70 + 0)
        # 准确率 Accuracy = (TP + TN) / (TP + FN + FP + TN)，（70 + 26） / （70 + 8 + 26 + 0）
        elif args.function == 'IOU':  # 把模型预测结果与人工标注结果进行对比，计算模型预测结果的漏检、误检、检出
            # 加载模型预测的labelme数据集
            model_dataset_info = asyncio.run(data_info.recursive_walk(input_datasets_list[0].get('model_input_dir'), args))
            # 加载标注数据集
            dataset.model_to_iou(model_dataset_info, args)
        elif args.function == 'compare':  # 数据集比较功能，目前比较漏检和正确检出图像相同的情况
            # 加载正确检出数据集
            right_check_dataset_info = asyncio.run(data_info.recursive_walk(input_datasets_list[0].get('model_input_dir'), args))
            # 加载漏检出数据集
            dataset.compare_labelme(right_check_dataset_info, args)
        elif args.function == 'mosaic':
            dataset.chipeak_mosaic()
        elif args.function == 'create_dir':
            dataset.chipeak_make_dir(args)
        elif args.function == 'flags':
            dataset.chipea_make_flags(args)
        elif args.function == 'md5':
            dataset.chipea_make_md5(args)
        elif args.function == 'soft_deletion':  # 软删除json
            dataset.soft_deletion_json(args)
        elif args.function == 'rename_file_name':  # 自定义格式把文件重命名
            dataset.rename_file_name(args)
        # elif args.function == 'image_check':  # 检查图像问题，包含格式、完整性、通道及其它问题
        #     dataset.image_check(args)
        elif args.function == 'move':  # 自定义格式把文件重命名
            dataset.move_file(args)
        elif args.function == 'modify_flags':  # 修改falgs值
            dataset.modify_flags(args)
        elif args.function == 'filter_flags_true':  # 筛选falgs值为真的标注
            dataset.select_flags_true(args)
        elif args.function == 'ratio':  # 按比例划分测试集和训练集
            dataset.ratio_split(args)
        elif args.function == 'draw_video':  # 根据图片合成视频并绘制标注内容
            dataset.draw_video(args)
        elif args.function == 'blacked':  # 把通道占用抽取的数据中的矩形框涂黑
            dataset.blacked_images()
        elif args.function == 'sahi':  # 滑窗切图
            dataset.sahi_images(args)
        elif args.function == 'intercept':  # 截取标注的人矩形框图片，并包含在内的其它矩形框标注
            dataset.intercept_images(args)
        elif args.function == 'mix':  # 计算标注目标与图像面积占比，划分保留大、中、小、的标注目标为labelme数据集功能。
            dataset.mix_images(args)
        elif args.function == 'sampling':  # 目标检测，标注数据的标签采样功能
            dataset.sampling_images(args)


if __name__ == '__main__':
    main()
    # 使用了asyncio.run()函数来启动，协程事件循环，则不需要手动关闭事件循环
    # asyncio.run(main())
