#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件下载器 - 支持直连和代理两种方式
File Downloader - Supports both direct connection and proxy
"""

import os
import sys
import requests
from urllib.parse import urlparse
from pathlib import Path
import argparse


class FileDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.chunk_size = 8192  # 8KB chunks for download
    
    def download_direct(self, url, save_path=None, timeout=30):
        """
        直连下载文件
        Direct download without proxy
        
        Args:
            url (str): 文件下载链接
            save_path (str): 保存路径，默认为当前目录下的原文件名
            timeout (int): 超时时间（秒）
        
        Returns:
            bool: 下载是否成功
        """
        try:
            print(f"开始直连下载: {url}")
            
            # 获取文件信息
            response = self.session.head(url, timeout=timeout)
            response.raise_for_status()
            
            # 确定保存路径
            if not save_path:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = "downloaded_file"
                save_path = filename
            
            # 开始下载
            response = self.session.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            # 获取文件大小
            file_size = int(response.headers.get('content-length', 0))
            
            # 创建目录（如果不存在）
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 写入文件
            downloaded_size = 0
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示进度
                        if file_size > 0:
                            progress = (downloaded_size / file_size) * 100
                            print(f"\r下载进度: {progress:.1f}% ({downloaded_size}/{file_size} bytes)", end='')
                        else:
                            print(f"\r已下载: {downloaded_size} bytes", end='')
            
            print(f"\n✓ 文件下载成功: {save_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"\n✗ 下载失败: {e}")
            return False
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            return False
    
    def download_with_proxy(self, url, proxy_host, proxy_port, save_path=None, 
                          proxy_user=None, proxy_pass=None, proxy_type='http', timeout=30):
        """
        使用代理下载文件
        Download file through proxy
        
        Args:
            url (str): 文件下载链接
            proxy_host (str): 代理服务器地址
            proxy_port (int): 代理服务器端口
            save_path (str): 保存路径
            proxy_user (str): 代理用户名（可选）
            proxy_pass (str): 代理密码（可选）
            proxy_type (str): 代理类型 ('http', 'https', 'socks5')
            timeout (int): 超时时间（秒）
        
        Returns:
            bool: 下载是否成功
        """
        try:
            # 构建代理URL
            if proxy_user and proxy_pass:
                proxy_url = f"{proxy_type}://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
            else:
                proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
            
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            print(f"开始代理下载: {url}")
            print(f"代理设置: {proxy_type}://{proxy_host}:{proxy_port}")
            
            # 获取文件信息
            response = self.session.head(url, proxies=proxies, timeout=timeout)
            response.raise_for_status()
            
            # 确定保存路径
            if not save_path:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = "downloaded_file"
                save_path = filename
            
            # 开始下载
            response = self.session.get(url, stream=True, proxies=proxies, timeout=timeout)
            response.raise_for_status()
            
            # 获取文件大小
            file_size = int(response.headers.get('content-length', 0))
            
            # 创建目录（如果不存在）
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 写入文件
            downloaded_size = 0
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示进度
                        if file_size > 0:
                            progress = (downloaded_size / file_size) * 100
                            print(f"\r下载进度: {progress:.1f}% ({downloaded_size}/{file_size} bytes)", end='')
                        else:
                            print(f"\r已下载: {downloaded_size} bytes", end='')
            
            print(f"\n✓ 文件下载成功: {save_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"\n✗ 下载失败: {e}")
            return False
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            return False


def main():
    """主函数 - 命令行界面"""
    parser = argparse.ArgumentParser(description='文件下载器 - 支持直连和代理')
    parser.add_argument('url', help='要下载的文件URL')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--proxy-host', help='代理服务器地址')
    parser.add_argument('--proxy-port', type=int, help='代理服务器端口')
    parser.add_argument('--proxy-user', help='代理用户名')
    parser.add_argument('--proxy-pass', help='代理密码')
    parser.add_argument('--proxy-type', choices=['http', 'https', 'socks5'], 
                       default='http', help='代理类型 (默认: http)')
    parser.add_argument('--timeout', type=int, default=30, help='超时时间（秒，默认30）')
    
    args = parser.parse_args()
    
    downloader = FileDownloader()
    
    # 判断是使用代理还是直连
    if args.proxy_host and args.proxy_port:
        # 使用代理下载
        success = downloader.download_with_proxy(
            url=args.url,
            proxy_host=args.proxy_host,
            proxy_port=args.proxy_port,
            save_path=args.output,
            proxy_user=args.proxy_user,
            proxy_pass=args.proxy_pass,
            proxy_type=args.proxy_type,
            timeout=args.timeout
        )
    else:
        # 直连下载
        success = downloader.download_direct(
            url=args.url,
            save_path=args.output,
            timeout=args.timeout
        )
    
    sys.exit(0 if success else 1)


def interactive_mode():
    """交互式模式"""
    print("=" * 60)
    print("文件下载器 - 支持直连和代理")
    print("=" * 60)
    
    downloader = FileDownloader()
    
    # 获取下载URL
    url = input("请输入要下载的文件URL: ").strip()
    if not url:
        print("URL不能为空")
        return
    
    # 获取保存路径
    save_path = input("请输入保存路径（回车使用默认路径）: ").strip()
    if not save_path:
        save_path = None
    
    # 选择下载方式
    print("\n选择下载方式:")
    print("1. 直连下载")
    print("2. 代理下载")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == '1':
        # 直连下载
        success = downloader.download_direct(url, save_path)
    elif choice == '2':
        # 代理下载
        print("\n代理设置:")
        proxy_host = input("代理服务器地址: ").strip()
        proxy_port = input("代理服务器端口: ").strip()
        
        if not proxy_host or not proxy_port:
            print("代理地址和端口不能为空")
            return
        
        try:
            proxy_port = int(proxy_port)
        except ValueError:
            print("端口必须是数字")
            return
        
        proxy_user = input("代理用户名（可选，回车跳过）: ").strip() or None
        proxy_pass = input("代理密码（可选，回车跳过）: ").strip() or None
        
        print("代理类型: 1-HTTP, 2-HTTPS, 3-SOCKS5")
        proxy_type_choice = input("请选择代理类型 (默认1): ").strip() or '1'
        
        proxy_type_map = {'1': 'http', '2': 'https', '3': 'socks5'}
        proxy_type = proxy_type_map.get(proxy_type_choice, 'http')
        
        success = downloader.download_with_proxy(
            url=url,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            save_path=save_path,
            proxy_user=proxy_user,
            proxy_pass=proxy_pass,
            proxy_type=proxy_type
        )
    else:
        print("无效选择")
        return
    
    if success:
        print("\n🎉 下载完成！")
    else:
        print("\n❌ 下载失败！")


if __name__ == '__main__':
    # 如果有命令行参数，使用命令行模式；否则使用交互式模式
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode() 