#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时图片清理工具
用于清理 interactive-feedback-mcp 生成的临时图片文件
"""

import os
import shutil
import sys
from datetime import datetime, timedelta
from temp_manager import temp_manager
from config import DEFAULT_CLEANUP_DAYS


def get_temp_images_dir():
    """获取临时图片目录路径"""
    return temp_manager.temp_dir


def cleanup_temp_images(days_old=DEFAULT_CLEANUP_DAYS, dry_run=False):
    """
    清理临时图片文件
    
    Args:
        days_old (int): 清理多少天前的文件，默认7天
        dry_run (bool): 是否为预览模式（不实际删除）
    
    Returns:
        dict: 清理结果统计
    """
    temp_dir = get_temp_images_dir()
    
    if not os.path.exists(temp_dir):
        return {
            'status': 'no_directory',
            'message': f'临时图片目录不存在: {temp_dir}',
            'deleted_files': 0,
            'total_size': 0
        }
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted_files = []
    total_size = 0
    
    try:
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            
            # 跳过非文件项
            if not os.path.isfile(file_path):
                continue
            
            # 检查文件修改时间
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_mtime < cutoff_date:
                file_size = os.path.getsize(file_path)
                total_size += file_size
                
                if not dry_run:
                    os.remove(file_path)
                
                deleted_files.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_size,
                    'mtime': file_mtime.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f'清理过程中出错: {str(e)}',
            'deleted_files': 0,
            'total_size': 0
        }
    
    return {
        'status': 'success',
        'message': f'{"预览" if dry_run else "清理"}完成',
        'deleted_files': len(deleted_files),
        'total_size': total_size,
        'files': deleted_files,
        'temp_dir': temp_dir
    }


def cleanup_all_temp_images(dry_run=False):
    """
    清理所有临时图片文件（不管时间）
    
    Args:
        dry_run (bool): 是否为预览模式
    
    Returns:
        dict: 清理结果
    """
    temp_dir = get_temp_images_dir()
    
    if not os.path.exists(temp_dir):
        return {
            'status': 'no_directory',
            'message': f'临时图片目录不存在: {temp_dir}',
            'deleted_files': 0,
            'total_size': 0
        }
    
    try:
        if not dry_run:
            shutil.rmtree(temp_dir)
            # 重新创建空目录
            os.makedirs(temp_dir)
        
        # 计算统计信息
        total_files = 0
        total_size = 0
        files_list = []
        
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    total_files += 1
                    
                    files_list.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_size,
                        'mtime': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return {
            'status': 'success',
            'message': f'{"预览" if dry_run else "清理"}所有临时图片完成',
            'deleted_files': total_files,
            'total_size': total_size,
            'files': files_list,
            'temp_dir': temp_dir
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f'清理过程中出错: {str(e)}',
            'deleted_files': 0,
            'total_size': 0
        }


def format_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def print_cleanup_result(result):
    """打印清理结果"""
    print(f"\n{'='*50}")
    print(f"状态: {result['status']}")
    print(f"消息: {result['message']}")
    
    if result['status'] == 'success':
        print(f"临时目录: {result['temp_dir']}")
        print(f"处理文件数: {result['deleted_files']}")
        print(f"总大小: {format_size(result['total_size'])}")
        
        if result.get('files') and len(result['files']) > 0:
            print(f"\n文件列表:")
            for file_info in result['files']:
                print(f"  - {file_info['name']} ({format_size(file_info['size'])}) - {file_info['mtime']}")
    
    print(f"{'='*50}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Interactive Feedback MCP 临时图片清理工具')
    parser.add_argument('--days', type=int, default=DEFAULT_CLEANUP_DAYS, help=f'清理多少天前的文件 (默认: {DEFAULT_CLEANUP_DAYS})')
    parser.add_argument('--all', action='store_true', help='清理所有临时图片文件')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际删除文件')
    parser.add_argument('--info', action='store_true', help='显示临时目录信息')
    
    args = parser.parse_args()
    
    if args.info:
        temp_dir = get_temp_images_dir()
        print(f"临时图片目录: {temp_dir}")
        
        if os.path.exists(temp_dir):
            files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            total_size = sum(os.path.getsize(os.path.join(temp_dir, f)) for f in files)
            print(f"文件数量: {len(files)}")
            print(f"总大小: {format_size(total_size)}")
        else:
            print("目录不存在")
        return
    
    if args.all:
        print("清理所有临时图片文件...")
        result = cleanup_all_temp_images(dry_run=args.dry_run)
    else:
        print(f"清理 {args.days} 天前的临时图片文件...")
        result = cleanup_temp_images(days_old=args.days, dry_run=args.dry_run)
    
    print_cleanup_result(result)


if __name__ == '__main__':
    main() 