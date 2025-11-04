#!/usr/bin/env python3
"""
将JM_DOWNLOAD_DIR目录中各子文件夹（包括嵌套文件夹）的图片按序拼接成PDF文件
输出文件名为JM_ALBUM_IDS.pdf
"""

import os
import sys
import argparse
from PIL import Image
import glob

def find_all_image_files(root_dir):
    """
    递归查找根目录下所有子文件夹中的图片文件
    
    Args:
        root_dir: 根目录路径
        
    Returns:
        dict: 按文件夹路径分组的图片文件列表
    """
    # 支持的图片格式
    image_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
    
    # 存储每个文件夹中的图片文件
    folder_images = {}
    
    # 使用os.walk递归遍历所有子目录
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 跳过根目录本身（只处理子文件夹）
        if dirpath == root_dir:
            continue
            
        # 查找当前目录中的所有图片文件
        images_in_current_dir = []
        for filename in filenames:
            file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
            if file_ext in image_extensions:
                full_path = os.path.join(dirpath, filename)
                images_in_current_dir.append(full_path)
        
        # 如果有图片文件，则按文件名排序并添加到字典中
        if images_in_current_dir:
            images_in_current_dir.sort()
            # 使用相对路径作为键，以便更好地显示
            rel_path = os.path.relpath(dirpath, root_dir)
            folder_images[rel_path] = images_in_current_dir
    
    return folder_images

def convert_images_to_pdf(input_dir, output_pdf_path):
    """
    将输入目录中各子文件夹（包括嵌套）的图片按序拼接成PDF
    
    Args:
        input_dir: 包含图片子文件夹的根目录
        output_pdf_path: 输出的PDF文件路径
    """
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"错误: 目录 '{input_dir}' 不存在")
        return False
    
    print("正在搜索所有子文件夹中的图片文件...")
    
    # 查找所有图片文件
    folder_images = find_all_image_files(input_dir)
    
    if not folder_images:
        print(f"错误: 在 '{input_dir}' 的子文件夹中没有找到任何图片文件")
        return False
    
    # 按文件夹路径排序（字母顺序）
    sorted_folders = sorted(folder_images.keys())
    
    print(f"找到 {len(sorted_folders)} 个包含图片的文件夹:")
    for folder in sorted_folders:
        print(f"  {folder}: {len(folder_images[folder])} 张图片")
    
    all_images = []
    
    # 按排序后的文件夹顺序处理图片
    for folder in sorted_folders:
        print(f"处理文件夹: {folder}")
        
        for img_path in folder_images[folder]:
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
        description='将JM_DOWNLOAD_DIR目录中的图片子文件夹（包括嵌套）按序拼接成PDF文件'
    )
    parser.add_argument('JM_DOWNLOAD_DIR', help='包含图片子文件夹的根目录路径')
    parser.add_argument('JM_ALBUM_IDS', help='输出PDF文件的名称（不含扩展名）')
    
    args = parser.parse_args()
    
    # 构建输出PDF路径
    output_pdf = f"{args.JM_ALBUM_IDS}.pdf"
    
    print("=" * 50)
    print("图片转PDF工具（支持嵌套文件夹）")
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