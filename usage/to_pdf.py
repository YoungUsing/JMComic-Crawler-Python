#!/usr/bin/env python3
"""
将JM_DOWNLOAD_DIR中各个子文件夹的图片按序拼接成单个PDF文件
使用JM_ALBUM_IDS参数为PDF文件命名，并将路径写入path_to_pdf环境变量
"""

import os
import sys
from PIL import Image
import glob
import re

def natural_sort_key(s):
    """
    自然排序函数，用于对文件名进行更人性化的排序
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def get_all_image_files_sorted(download_dir, album_ids=None):
    """
    获取所有子文件夹中的图片文件，并按文件夹和文件自然顺序排序
    如果指定了album_ids，则只处理这些子文件夹
    """
    supported_formats = ('*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', '*.webp')
    all_image_files = []
    
    # 获取所有子文件夹并按自然顺序排序
    subfolders = [f for f in os.listdir(download_dir) 
                 if os.path.isdir(os.path.join(download_dir, f))]
    subfolders.sort(key=natural_sort_key)
    
    # 如果指定了album_ids，只处理这些文件夹
    if album_ids:
        album_ids_list = [aid.strip() for aid in album_ids.split(',')]
        subfolders = [f for f in subfolders if f in album_ids_list]
        print(f"根据JM_ALBUM_IDS筛选，处理 {len(subfolders)} 个子文件夹")
    else:
        print(f"找到 {len(subfolders)} 个子文件夹")
    
    for folder in subfolders:
        folder_path = os.path.join(download_dir, folder)
        print(f"\n扫描文件夹: {folder}")
        
        folder_images = []
        for fmt in supported_formats:
            folder_images.extend(glob.glob(os.path.join(folder_path, fmt)))
            folder_images.extend(glob.glob(os.path.join(folder_path, fmt.upper())))
        
        # 按自然顺序排序当前文件夹的图片
        folder_images.sort(key=natural_sort_key)
        
        if folder_images:
            print(f"  找到 {len(folder_images)} 张图片")
            all_image_files.extend(folder_images)
        else:
            print(f"  未找到图片")
    
    return all_image_files

def convert_all_images_to_single_pdf(image_files, output_pdf_path):
    """
    将所有图片转换为单个PDF文件
    """
    if not image_files:
        print("错误: 没有找到任何图片文件")
        return False
    
    try:
        print(f"\n开始合并 {len(image_files)} 张图片到单个PDF...")
        
        # 打开所有图片并转换为RGB模式
        images = []
        success_count = 0
        
        for i, img_path in enumerate(image_files, 1):
            try:
                img = Image.open(img_path)
                # 转换为RGB模式（PDF需要）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
                success_count += 1
                
                if i % 10 == 0 or i == len(image_files):
                    print(f"  已加载 {i}/{len(image_files)} 张图片")
                    
            except Exception as e:
                print(f"  无法加载图片 {img_path}: {e}")
                continue
        
        if not images:
            print("错误: 没有有效的图片文件")
            return False
        
        # 保存为单个PDF
        print(f"正在生成PDF文件...")
        first_image = images[0]
        first_image.save(
            output_pdf_path, 
            "PDF", 
            resolution=100.0, 
            save_all=True, 
            append_images=images[1:],
            quality=95
        )
        
        print(f"✓ 成功生成合并的PDF文件")
        print(f"  包含 {success_count} 张图片")
        print(f"  文件大小: {os.path.getsize(output_pdf_path) / (1024*1024):.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"✗ 生成PDF失败: {e}")
        return False

def sanitize_filename(filename):
    """
    清理文件名，移除或替换不安全的字符
    """
    # 替换不安全的字符为下划线
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    # 移除首尾空格
    filename = filename.strip()
    # 限制文件名长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def write_path_to_env(pdf_path, env_file=None):
    """
    将PDF路径写入环境变量文件或直接设置环境变量
    """
    # 获取绝对路径
    abs_path = os.path.abspath(pdf_path)
    
    # 写入环境变量
    os.environ['path_to_pdf'] = abs_path
    
    # 如果指定了环境变量文件，也写入文件
    if env_file:
        try:
            with open(env_file, 'w') as f:
                f.write(f'path_to_pdf={abs_path}\n')
            print(f"PDF路径已写入环境变量文件: {env_file}")
        except Exception as e:
            print(f"警告: 无法写入环境变量文件 {env_file}: {e}")
    
    return abs_path

def main():
    # 获取环境变量
    download_dir = os.environ.get('JM_DOWNLOAD_DIR')
    album_ids = os.environ.get('JM_ALBUM_IDS')
    env_file = os.environ.get('JM_ENV_FILE')  # 可选的环境变量文件路径
    
    if not download_dir:
        print("错误: 未找到环境变量 JM_DOWNLOAD_DIR")
        print("请先设置环境变量: export JM_DOWNLOAD_DIR=您的下载目录路径")
        sys.exit(1)
    
    if not os.path.exists(download_dir):
        print(f"错误: 目录不存在: {download_dir}")
        sys.exit(1)
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 确定输出PDF文件名
    if album_ids:
        # 使用JM_ALBUM_IDS作为文件名
        pdf_name = sanitize_filename(album_ids) + ".pdf"
    else:
        # 默认文件名
        pdf_name = "combined_images.pdf"
    
    output_pdf_path = os.path.join(current_dir, pdf_name)
    
    print(f"扫描目录: {download_dir}")
    if album_ids:
        print(f"处理相册ID: {album_ids}")
    print(f"输出PDF: {output_pdf_path}")
    print("=" * 60)
    
    # 获取所有排序后的图片文件
    all_image_files = get_all_image_files_sorted(download_dir, album_ids)
    
    if not all_image_files:
        print("\n错误: 在指定目录中未找到任何图片文件")
        sys.exit(1)
    
    print(f"\n总共找到 {len(all_image_files)} 张图片")
    
    # 转换为单个PDF
    if convert_all_images_to_single_pdf(all_image_files, output_pdf_path):
        # 将路径写入环境变量
        abs_pdf_path = write_path_to_env(output_pdf_path, env_file)
        
        # 返回相对路径
        relative_path = os.path.relpath(output_pdf_path, current_dir)
        print(f"\n" + "=" * 60)
        print(f"处理完成!")
        print(f"PDF文件相对路径: ./{relative_path}")
        print(f"PDF文件绝对路径: {abs_pdf_path}")
        print(f"PDF路径已写入环境变量: path_to_pdf={abs_pdf_path}")
        
        # 返回绝对路径（可用于其他脚本调用）
        return abs_pdf_path
    else:
        print(f"\n处理失败!")
        return None

if __name__ == "__main__":
    result = main()
    # 如果需要在其他脚本中获取这个路径，可以打印出来或者通过退出码传递
    if result:
        # 打印路径，便于其他程序捕获
        print(f"OUTPUT_PATH:{result}")
    else:
        sys.exit(1)