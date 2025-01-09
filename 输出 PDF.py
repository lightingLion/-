import os
from fpdf import FPDF
from pathlib import Path
from PIL import Image

# 获取当前脚本目录和文件夹名称
current_dir = Path(__file__).parent
folder_name = current_dir.name

# 初始化 PDF
pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.set_auto_page_break(auto=True, margin=15)

# 获取当前目录中以数字命名的 .jpg 文件
image_files = sorted(
    [f for f in os.listdir(current_dir) if f.endswith('.jpg') and f.split('.')[0].isdigit()],
    key=lambda x: int(x.split('.')[0])
)

# A4 页面宽度和高度
page_width = 210
page_height = 297
image_max_width = (page_width - 30) / 2  # 每张图片的最大宽度，左右边距各10mm，中间间距10mm
image_max_height = page_height - 40  # 每张图片的最大高度，上下边距各20mm

# 将图片插入 PDF，每页两张横向排列
for idx, image_file in enumerate(image_files, start=1):
    if idx % 2 == 1:
        pdf.add_page()  # 每两张图片开始新的一页

    img_path = current_dir / image_file

    # 使用 PIL 获取图片尺寸并计算缩放比例
    with Image.open(img_path) as img:
        img_width, img_height = img.size
        width_ratio = image_max_width / img_width
        height_ratio = image_max_height / img_height
        scale_ratio = min(width_ratio, height_ratio)  # 等比缩放

        resized_width = img_width * scale_ratio
        resized_height = img_height * scale_ratio

    # 确定图片的放置位置
    x_offset = 10 if idx % 2 == 1 else (10 + image_max_width + 10)  # 左边或右边
    y_offset = 20  # 顶部边距

    pdf.image(str(img_path), x=x_offset, y=y_offset, w=resized_width, h=resized_height)  # 添加图片

# 保存 PDF 文件
output_path = current_dir / f'{folder_name}.pdf'
pdf.output(str(output_path))

print(f"PDF 文档已生成：{output_path}")
