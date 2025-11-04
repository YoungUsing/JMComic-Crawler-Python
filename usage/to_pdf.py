#!/usr/bin/env python3
"""
将JM_DOWNLOAD_DIR目录中各子文件夹的图片按序拼接成PDF文件
输出文件名为JM_ALBUM_IDS.pdf
"""

import os
import sys
import argparse
from PIL import Image
import glob

def convert_images_to_pdf(input_dir, output_pdf_path):
    """
    将输入目录中各子文件夹的图片按序拼接成PDF
    
    Args:
        input_dir: 包含图片子文件夹的根目录
        output_pdf_path: 输出的PDF文件路径
    """
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"错误: 目录 '{input_dir}' 不存在")
        return False
    
    # 获取所有子文件夹
    subdirs = [d for d in os.listdir(input_dir) 
              if os.path.isdir(os.path.join(input_dir, d))]
    
    if not subdirs:
        print(f"警告: 目录 '{input_dir}' 中没有子文件夹")
        return False
    
    # 支持的图片格式
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
    
    all_images = []
    
    # 按文件夹名称排序处理每个子文件夹
    for subdir in sorted(subdirs):
        subdir_path = os.path.join(input_dir, subdir)
        print(f"处理文件夹: {subdir}")
        
        folder_images = []
        
        # 查找所有支持的图片文件
        for extension in image_extensions:
            pattern = os.path.join(subdir_path, extension)
            folder_images.extend(glob.glob(pattern))
            # 同时查找大写扩展名
            pattern_upper = os.path.join(subdir_path, extension.upper())
            folder_images.extend(glob.glob(pattern_upper))
        
        # 按文件名排序图片
        folder_images.sort()
        
        if not folder_images:
            print(f"  警告: 文件夹 '{subdir}' 中没有找到图片文件")
            continue
        
        # 将图片转换为RGB模式并添加到总列表
        for img_path in folder_images:
            try:
                with Image.open(img_path) as img:
                    # 转换为RGB模式（PDF需要）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    all_images.append(img)
                    print(f"  添加图片: {os.path.basename(img_path)}")
            except Exception as e:
                print(f"  错误: 无法处理图片 {img_path}: {e}")
    
    if not all_images:
        print("错误: 没有找到可用的图片文件")
        return False
    
    # 保存为PDF
    try:
        # 使用第一张图片作为基础，将其他图片追加进去
        first_image = all_images[0]
        remaining_images = all_images[1:]
        
        print(f"正在生成PDF文件，共 {len(all_images)} 张图片...")
        first_image.save(
            output_pdf_path, 
            "PDF", 
            save_all=True, 
            append_images=remaining_images,
            resolution=100.0,
            quality=95
        )
        
        print(f"成功生成PDF文件: {output_pdf_path}")
        print(f"文件大小: {os.path.getsize(output_pdf_path) / 1024 / 1024:.2f} MB")
        return True
        
    except Exception as e:
        print(f"错误: 生成PDF失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将JM_DOWNLOAD_DIR目录中的图片子文件夹按序拼接成PDF文件'
    )
    parser.add_argument('JM_DOWNLOAD_DIR', help='包含图片子文件夹的根目录路径')
    parser.add_argument('JM_ALBUM_IDS', help='输出PDF文件的名称（不含扩展名）')
    
    args = parser.parse_args()
    
    # 构建输出PDF路径
    output_pdf = f"{args.JM_ALBUM_IDS}.pdf"
    
    print("=" * 50)
    print("图片转PDF工具")
    print("=" * 50)
    print(f"输入目录: {args.JM_DOWNLOAD_DIR}")
    print(f"输出文件: {output_pdf}")
    print("=" * 50)
    
    # 执行转换
    success = convert_images_to_pdf(args.JM_DOWNLOAD_DIR, output_pdf)
    
    if success:
        print("处理完成!")
        sys.exit(0)
    else:
        print("处理失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()