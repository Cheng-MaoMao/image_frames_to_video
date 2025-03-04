import cv2
import glob


def resize(img_array, align_mode):
    """调整图片数组大小，使所有图片尺寸一致
    :param img_array: 图片数组
    :param align_mode: 'smallest'以最小图片为准，其他以最大图片为准
    :return: 调整后的图片数组和统一尺寸
    """
    # 使用shape获取图片尺寸
    first_img = img_array[0]
    _height, _width = first_img.shape[:2]  # 使用shape属性获取高度和宽度
    
    # 找出所有图片中的最大/最小尺寸
    for img in img_array[1:]:
        height, width = img.shape[:2]
        if align_mode == 'smallest':
            _height = min(_height, height)
            _width = min(_width, width)
        else:
            _height = max(_height, height)
            _width = max(_width, width)

    # 调整所有图片大小
    resized_array = []
    for img in img_array:
        if img.shape[:2] != (_height, _width):
            resized = cv2.resize(img, (_width, _height), interpolation=cv2.INTER_LINEAR)
        else:
            resized = img.copy()  # 如果尺寸已经正确，创建副本避免修改原图
        resized_array.append(resized)

    return resized_array, (_width, _height)


def natural_sort_key(s):
    """用于文件名的自然排序"""
    import re
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def images_to_video(path, output_path='demo.mp4', fps=25, codec='mp4v'):
    """将指定路径下的所有jpg图片合成为视频
    :param path: 图片所在目录
    :param output_path: 输出视频路径，默认为'demo.mp4'
    :param fps: 帧率，默认为25
    :param codec: 视频编码格式，默认为'mp4v'
    """
    # 支持多种图片格式
    supported_formats = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    img_array = []
    
    # 获取所有支持格式的图片
    image_files = []
    for fmt in supported_formats:
        image_files.extend(glob.glob(path + '/' + fmt))
    
    if not image_files:
        raise ValueError(f"在路径 {path} 中没有找到支持的图片文件")
    
    # 使用自然排序
    image_files.sort(key=natural_sort_key)
    
    total_files = len(image_files)
    print(f"开始读取图片从路径: {path}")
    for i, filename in enumerate(image_files, 1):
        if i % 10 == 0:  # 每处理10张图片显示一次进度
            print(f"处理进度: {i}/{total_files} ({i/total_files*100:.1f}%)")
        img = cv2.imread(filename)
        if img is None:
            print(f"警告: {filename} 读取失败！")
            continue
        # 确保图片是BGR格式
        if len(img.shape) == 2:  # 如果是灰度图
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:  # 如果是RGBA
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img_array.append(img)
    
    if not img_array:
        raise ValueError("没有成功读取任何图片！")
    
    print(f"成功读取 {len(img_array)} 张图片")
    
    # 图片的大小需要一致
    img_array, size = resize(img_array, 'largest')
    print(f"调整后的图片尺寸: {size}")
    
    # 创建VideoWriter对象
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_path, fourcc, fps, size, True)  # 确保输出彩色视频
    
    if not out.isOpened():
        raise ValueError(f"无法创建视频文件 {output_path}，请检查编码格式和文件路径是否正确")

    try:
        # 写入视频帧
        for img in img_array:
            out.write(img)
    finally:
        out.release()  # 确保在出错时也能正确释放资源


def main():
    """主函数，处理用户输入并调用视频生成函数"""
    # 获取图片路径
    while True:
        path = input('请输入图片帧所在目录路径：').strip()
        if not path:
            print("路径不能为空，请重新输入")
            continue
        
        # 检查路径是否存在
        if not glob.glob(path + '/*'):
            print(f"警告: 路径 {path} 不存在或为空目录")
            continue
            
        # 检查是否包含图片文件
        image_files = []
        for fmt in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(glob.glob(path + '/' + fmt))
        if not image_files:
            print(f"警告: 在路径 {path} 中没有找到支持的图片文件(jpg/jpeg/png/bmp)")
            continue
        break
    
    # 处理输出路径
    output_path = input('请输入输出视频路径（默认：demo.mp4）：').strip() or 'demo.mp4'
    # 确保输出路径有.mp4扩展名
    if not output_path.lower().endswith('.mp4'):
        output_path = output_path.rstrip('\\') + '\\output.mp4' if '\\' in output_path else output_path + '.mp4'
    print(f"视频将保存为: {output_path}")
    
    fps = int(input('请输入帧率（默认：30）：') or 30)
    codec = 'mp4v'  # 使用MP4编码器
    
    try:
        images_to_video(path, output_path, fps, codec)
        print(f"视频已成功生成: {output_path}")
    except Exception as e:
        print(f"生成视频时出错: {str(e)}")


if __name__ == "__main__":
    main()
