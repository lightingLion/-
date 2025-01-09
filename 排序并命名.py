import os
import re
from PIL import Image, ImageEnhance, ImageFilter
import easyocr
import numpy as np

# 配置 EasyOCR 阅读器
reader = easyocr.Reader(['en'])

def preprocess_image(image_path):
    """
    对图片进行预处理以增强红色文本的可读性
    """
    image = Image.open(image_path)
    
    # 转换为 RGB 模式（确保兼容性）
    image = image.convert("RGB")
    
    # 提取红色通道
    red_channel = image.split()[0]
    
    # 增强对比度和锐化
    enhancer = ImageEnhance.Contrast(red_channel)
    enhanced_image = enhancer.enhance(2.0)  # 增强对比度
    enhanced_image = enhanced_image.filter(ImageFilter.SHARPEN)  # 锐化
    
    return enhanced_image

def extract_no(image_path):
    """
    从图片中提取票据编号（如 No. 开头的一串数字）
    """
    try:
        # 对图片进行预处理
        preprocessed_image = preprocess_image(image_path)
        
        # 将处理后的 PIL 图像转换为 NumPy 数组，以便 EasyOCR 处理
        preprocessed_image_np = np.array(preprocessed_image)
        
        # OCR 识别预处理后的图片文本
        text = reader.readtext(preprocessed_image_np)
        
        # 提取文本中的 "No." 开头的数字
        for _, txt, _ in text:
            match = re.search(r'No\.\s*(\d+)', txt, re.IGNORECASE)
            if match:
                return int(match.group(1))  # 返回提取到的编号作为整数
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    return None

def rename_images_by_no():
    """
    根据票据编号对当前目录中的图片文件进行重命名，并先给原文件名加上字母 'z'，防止重复
    """
    # 获取脚本所在的目录
    folder_path = os.path.dirname(os.path.abspath(__file__))

    # 获取文件夹中所有图片文件
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not image_files:
        print("当前目录中没有找到图片文件！")
        return

    # 首先给所有文件名前加上 'z'，防止文件名重复
    renamed_files = []
    for image_file in image_files:
        original_path = os.path.join(folder_path, image_file)
        new_name = f"z{image_file}"  # 给文件名前加上 'z'
        new_path = os.path.join(folder_path, new_name)
        os.rename(original_path, new_path)  # 重命名文件
        renamed_files.append(new_name)
        print(f"重命名 {image_file} -> {new_name}")

    no_to_file = {}

    # 提取编号并进行排序
    for image_file in renamed_files:
        image_path = os.path.join(folder_path, image_file)
        no = extract_no(image_path)
        if no is not None:
            no_to_file[no] = image_file
        else:
            print(f"未能从 {image_file} 中提取票据编号")

    # 根据票据编号排序
    sorted_files = sorted(no_to_file.items(), key=lambda x: x[0])

    # 按顺序重命名图片
    for i, (no, original_file) in enumerate(sorted_files, start=1):
        original_path = os.path.join(folder_path, original_file)
        new_name = f"{i}.jpg"  # 重命名为 1.jpg, 2.jpg, ...
        new_path = os.path.join(folder_path, new_name)
        os.rename(original_path, new_path)
        print(f"重命名 {original_file} -> {new_name}")

    print("重命名完成！")

# 主程序入口
if __name__ == "__main__":
    rename_images_by_no()
