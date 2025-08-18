# 使用icrawler库实现图片下载器
# pip install icrawler Pillow

import os
import sys
import hashlib
import glob
import shutil
import io
import logging
import re
from collections import defaultdict

# 自动安装缺失的依赖
def _install_missing_packages():
    """自动安装缺失的依赖包"""
    missing_packages = []
    
    try:
        import icrawler
    except ImportError:
        missing_packages.append("icrawler")
    
    try:
        from PIL import Image
    except ImportError:
        missing_packages.append("Pillow")
    
    if missing_packages:
        print(f"检测到缺失的依赖包: {missing_packages}")
        print("正在尝试自动安装...")
        
        import subprocess
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ 成功安装 {package}")
            except subprocess.CalledProcessError as e:
                print(f"✗ 安装 {package} 失败: {e}")
                print(f"请手动运行: pip install {package}")
                return False
        
        print("依赖包安装完成，正在重新导入...")
        return True
    return True

# 尝试安装缺失的包
if not _install_missing_packages():
    print("请手动安装缺失的依赖包后重试")
    sys.exit(1)

# 导入依赖包
try:
    from icrawler.builtin import BingImageCrawler, BaiduImageCrawler, GoogleImageCrawler
    from PIL import Image
    from icrawler import ImageDownloader as BaseDownloader
    from icrawler.storage import BaseStorage
except ImportError as e:
    print(f"导入依赖包失败: {e}")
    print("请运行以下命令安装依赖:")
    print("pip install icrawler Pillow")
    sys.exit(1)


class URLCapturingHandler(logging.Handler):
    """自定义日志处理器，用于捕获icrawler的URL信息"""
    
    def __init__(self):
        super().__init__()
        self.url_mappings = {}
        self.image_counter = 0
    
    def emit(self, record):
        """处理日志记录，提取URL信息"""
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            # 匹配类似 "image #1    https://example.com/image.jpg" 的日志格式
            url_match = re.search(r'image #(\d+)\s+(https?://[^\s]+)', message)
            if url_match:
                image_num = int(url_match.group(1))
                url = url_match.group(2)
                # 根据icrawler的命名约定，图片文件名格式为 000001.jpg, 000002.jpg 等
                filename = f"{image_num:06d}.jpg"
                self.url_mappings[filename] = url


class URLMappingStorage(BaseStorage):
    """自定义存储类，用于捕获URL映射信息"""
    
    def __init__(self, root_dir, url_mappings):
        super().__init__(root_dir)
        self.url_mappings = url_mappings
    
    def write(self, task, **kwargs):
        """重写write方法来捕获URL信息"""
        file_idx = super().write(task, **kwargs)
        if file_idx is not None:
            # 捕获URL和文件路径信息
            filename = self.get_filename(task, file_idx, **kwargs)
            self.url_mappings.append({
                'file_path': filename,
                'original_url': task.get('img_url', ''),
                'keyword': task.get('keyword', ''),
                'engine': task.get('engine', '')
            })
        return file_idx


class ImageDownloader:
    """使用icrawler库实现的图片下载器"""
    
    def __init__(self, save_dir="downloaded_images"):
        """
        初始化图片下载器
        
        参数:
            save_dir: 图片保存的目录，默认为"downloaded_images"
        """
        self.save_dir = save_dir
        self.save_mapping = False
        self.url_mappings = []
        os.makedirs(save_dir, exist_ok=True)
    
    def download_from_baidu(self, keyword, num_images=20):
        """
        从百度图片搜索并下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
        
        返回:
            下载的图片数量
        """
        # 为每个关键词创建一个临时目录
        temp_dir = os.path.join(self.save_dir, "_temp_" + keyword.replace(" ", "_"))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建最终保存的关键词目录
        keyword_dir = os.path.join(self.save_dir, keyword.replace(" ", "_"))
        os.makedirs(keyword_dir, exist_ok=True)
        
        print(f"从百度搜索并下载 '{keyword}' 的图片...")
        
        # 创建百度爬虫
        crawler = BaiduImageCrawler(
            downloader_threads=4,
            storage={'root_dir': temp_dir}
        )
        
        # 执行爬取
        crawler.crawl(keyword=keyword, max_num=num_images)
        
        # 如果需要保存URL映射，先从日志中提取URL信息
        url_mappings = []
        if self.save_mapping:
            url_mappings = self._extract_urls_from_temp_dir(temp_dir, keyword, "baidu")
        
        # 转换所有图片为jpg格式并使用哈希文件名，保存到对应关键词目录
        converted = self._convert_images_to_jpg_with_hash(temp_dir, keyword, keyword_dir, "baidu", url_mappings)
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return converted
    
    def download_from_bing(self, keyword, num_images=20):
        """
        从必应图片搜索并下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
        
        返回:
            下载的图片数量
        """
        # 为每个关键词创建一个临时目录
        temp_dir = os.path.join(self.save_dir, "_temp_" + keyword.replace(" ", "_"))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建最终保存的关键词目录
        keyword_dir = os.path.join(self.save_dir, keyword.replace(" ", "_"))
        os.makedirs(keyword_dir, exist_ok=True)
        
        print(f"从必应搜索并下载 '{keyword}' 的图片...")
        
        # 如果需要捕获URL，设置日志处理器
        url_handler = None
        if self.save_mapping:
            url_handler = URLCapturingHandler()
            # 获取icrawler相关的所有logger并添加我们的处理器
            loggers = ['icrawler', 'downloader', 'parser', 'feeder']
            for logger_name in loggers:
                logger = logging.getLogger(logger_name)
                logger.addHandler(url_handler)
                logger.setLevel(logging.INFO)
        
        # 创建必应爬虫  
        crawler = BingImageCrawler(
            downloader_threads=4,
            storage={'root_dir': temp_dir}
        )
        
        # 执行爬取
        crawler.crawl(keyword=keyword, max_num=num_images)
        
        # 移除URL处理器
        if url_handler:
            loggers = ['icrawler', 'downloader', 'parser', 'feeder']
            for logger_name in loggers:
                logger = logging.getLogger(logger_name)
                logger.removeHandler(url_handler)
        
        # 如果需要保存URL映射，从URL处理器中获取URL信息
        url_mappings = {}
        if self.save_mapping and url_handler:
            url_mappings = url_handler.url_mappings
        
        # 转换所有图片为jpg格式并使用哈希文件名，保存到对应关键词目录
        converted = self._convert_images_to_jpg_with_hash(temp_dir, keyword, keyword_dir, "bing", url_mappings)
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return converted
    
    def download_from_google(self, keyword, num_images=20):
        """
        从谷歌图片搜索并下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
        
        返回:
            下载的图片数量
        """
        # 为每个关键词创建一个临时目录
        temp_dir = os.path.join(self.save_dir, "_temp_" + keyword.replace(" ", "_"))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建最终保存的关键词目录
        keyword_dir = os.path.join(self.save_dir, keyword.replace(" ", "_"))
        os.makedirs(keyword_dir, exist_ok=True)
        
        print(f"从谷歌搜索并下载 '{keyword}' 的图片...")
        
        # 创建谷歌爬虫
        crawler = GoogleImageCrawler(
            downloader_threads=4,
            storage={'root_dir': temp_dir}
        )
        
        # 执行爬取
        crawler.crawl(keyword=keyword, max_num=num_images)
        
        # 如果需要保存URL映射，先从日志中提取URL信息
        url_mappings = []
        if self.save_mapping:
            url_mappings = self._extract_urls_from_temp_dir(temp_dir, keyword, "google")
        
        # 转换所有图片为jpg格式并使用哈希文件名，保存到对应关键词目录
        converted = self._convert_images_to_jpg_with_hash(temp_dir, keyword, keyword_dir, "google", url_mappings)
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return converted
    
    def download_images(self, keyword, num_images=20, engine="bing"):
        """
        根据关键词从指定搜索引擎下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
            engine: 搜索引擎，支持"baidu"、"bing"或"google"
        
        返回:
            下载的图片数量
        """
        if engine == "baidu":
            return self.download_from_baidu(keyword, num_images)
        elif engine == "bing":
            return self.download_from_bing(keyword, num_images)
        elif engine == "google":
            return self.download_from_google(keyword, num_images)
        else:
            raise ValueError(f"不支持的搜索引擎: {engine}，请使用 'baidu', 'bing' 或 'google'")
    
    def _get_image_hash(self, image_data):
        """
        计算图片内容的MD5哈希值
        
        参数:
            image_data: 图片二进制数据
        
        返回:
            图片的哈希值
        """
        return hashlib.md5(image_data).hexdigest()
    
    def _extract_urls_from_temp_dir(self, temp_dir, keyword, engine):
        """
        从临时目录中提取文件名到URL的映射（使用icrawler的内置文件名约定）
        
        参数:
            temp_dir: 临时目录路径
            keyword: 搜索关键词
            engine: 搜索引擎
        
        返回:
            URL映射列表
        """
        # icrawler会将下载的图片按数字序号命名（000001.jpg, 000002.jpg, ...）
        # 我们创建一个映射字典来存储已知的URL信息
        # 由于无法直接从icrawler获取URL映射，这里提供基础结构
        # URL信息将在转换过程中从其他源获取
        mappings = []
        
        # 获取临时目录中的所有图片文件
        image_files = sorted(glob.glob(os.path.join(temp_dir, '*.*')))
        
        for i, img_path in enumerate(image_files):
            filename = os.path.basename(img_path)
            mappings.append({
                'temp_filename': filename,
                'temp_path': img_path,
                'index': i + 1,
                'original_url': ''  # 将在后续流程中填充
            })
        
        return mappings
    
    def _convert_images_to_jpg_with_hash(self, directory, keyword, target_dir, engine, url_mappings=None):
        """
        将目录中的所有图片转换为jpg格式，并使用哈希值作为文件名
        
        参数:
            directory: 图片所在目录
            keyword: 搜索关键词（用于元数据）
            target_dir: 图片保存的目标目录
            engine: 使用的搜索引擎
            url_mappings: URL映射列表（可选）
        
        返回:
            成功转换的图片数量
        """
        converted_count = 0
        # 获取所有图片文件
        image_files = glob.glob(os.path.join(directory, '*.*'))
        
        for i, img_path in enumerate(image_files):
            try:
                # 尝试打开图片
                with open(img_path, 'rb') as f:
                    image_data = f.read()
                
                # 计算图片内容的哈希值
                hash_value = self._get_image_hash(image_data)
                
                try:
                    # 尝试加载图片以确保它是有效的
                    img = Image.open(io.BytesIO(image_data))
                    
                    # 转换为RGB模式（以防是RGBA或其他模式）
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # 使用哈希值作为文件名
                    jpg_filename = f"{hash_value}.jpg"
                    jpg_path = os.path.join(target_dir, jpg_filename)
                    
                    # 如果文件已存在，跳过（避免重复）
                    if os.path.exists(jpg_path):
                        print(f"图片已存在 (哈希值: {hash_value})")
                        converted_count += 1
                        continue
                    
                    # 保存为jpg
                    img.save(jpg_path, "JPEG")
                    
                    # 更新URL映射信息（如果有保存URL映射的需求）
                    if self.save_mapping:
                        original_filename = os.path.basename(img_path)
                        # 从URL映射中获取原始URL
                        original_url = ''
                        if url_mappings and isinstance(url_mappings, dict):
                            original_url = url_mappings.get(original_filename, '')
                        
                        mapping_entry = {
                            'original_filename': original_filename,
                            'final_filename': jpg_filename,
                            'final_path': jpg_path,
                            'keyword': keyword,
                            'engine': engine,
                            'original_url': original_url,
                            'hash': hash_value
                        }
                        self.url_mappings.append(mapping_entry)
                    
                    converted_count += 1
                    print(f"保存图片到 {target_dir}: {jpg_filename}")
                    
                except Exception as e:
                    print(f"处理图片失败: {e}")
                
            except Exception as e:
                print(f"无法处理图片 {img_path}: {e}")
        
        print(f"成功处理并哈希化 {converted_count} 张图片，保存到 '{target_dir}'")
        return converted_count


def download_images_cli(keywords, num_images=50, engines=None, save_dir="downloaded_images", save_mapping=True):
    """
    CLI友好的图片下载函数
    
    参数:
        keywords: 搜索关键词列表或单个关键词字符串
        num_images: 每个关键词要下载的图片数量，默认50
        engines: 要使用的搜索引擎列表，默认["bing", "google"]
        save_dir: 图片保存目录，默认"downloaded_images"
        save_mapping: 是否保存图像元数据到metadata.jsonl文件，默认True
    
    返回:
        下载统计信息字典
    """
    # 处理输入参数
    if isinstance(keywords, str):
        keywords = [keywords]
    
    if engines is None:
        engines = ["bing", "google"]
    elif isinstance(engines, str):
        engines = [engines]
    
    # 创建下载器实例
    downloader = ImageDownloader(save_dir=save_dir)
    downloader.save_mapping = save_mapping
    
    # 统计信息
    stats = {
        "total_keywords": len(keywords),
        "total_engines": len(engines),
        "downloads": {},
        "total_downloaded": 0
    }
    
    print(f"开始下载图片...")
    print(f"关键词数量: {len(keywords)}")
    print(f"每个关键词下载: {num_images} 张图片")
    print(f"使用搜索引擎: {', '.join(engines)}")
    print(f"保存目录: {save_dir}")
    print("-" * 60)
    
    # 下载每个关键词的图片
    for i, keyword in enumerate(keywords, 1):
        print(f"\n[{i}/{len(keywords)}] 处理关键词: '{keyword}'")
        stats["downloads"][keyword] = {}
        
        for engine in engines:
            try:
                print(f"  使用 {engine} 搜索...")
                downloaded_count = downloader.download_images(
                    keyword, 
                    num_images=num_images, 
                    engine=engine
                )
                stats["downloads"][keyword][engine] = downloaded_count
                stats["total_downloaded"] += downloaded_count
                print(f"  {engine}: 成功下载 {downloaded_count} 张图片")
                
            except Exception as e:
                print(f"  {engine}: 下载失败 - {e}")
                stats["downloads"][keyword][engine] = 0
        
        print("-" * 50)
    
    # 保存元数据表（如果需要）
    if save_mapping and downloader.url_mappings:
        import json
        from pathlib import Path
        
        metadata_file = Path(save_dir) / "metadata.jsonl"
        
        # 检查文件是否已存在，决定是新建还是追加
        if metadata_file.exists():
            print(f"\n追加元数据到: {metadata_file}")
            mode = 'a'
        else:
            print(f"\n保存元数据表到: {metadata_file}")
            mode = 'w'
        
        with open(metadata_file, mode, encoding='utf-8') as f:
            for mapping in downloader.url_mappings:
                json.dump(mapping, f, ensure_ascii=False)
                f.write('\n')
        
        print(f"已保存 {len(downloader.url_mappings)} 条元数据记录")
    
    # 打印总结
    print(f"\n下载完成!")
    print(f"总共下载了 {stats['total_downloaded']} 张图片")
    print(f"图片保存在: {save_dir}")
    
    return stats


def main():
    """主函数，演示如何使用ImageDownloader类"""
    # 创建下载器实例
    downloader = ImageDownloader(save_dir="女性图片集")
    
    # 示例关键词
    keywords = [
        "户外自拍女性",
        "女性写真",
        "动漫女角色",
        "影视剧女角色",
        "短片",
        "校园 女生",
        "随手拍",
        "女性 自拍",
    ]
    
    # 下载每个关键词的图片
    for keyword in keywords:
        downloader.download_images(keyword, num_images=100, engine="bing")
        downloader.download_images(keyword, num_images=100, engine="google")
        downloader.download_images(keyword, num_images=100, engine="baidu")
        print("-" * 50)


def download_images_simple():
    from bing_image_downloader import downloader

    keywords = [
        "影视剧女演员",
        "户外自拍女性",
        "女性写真",
        "女明星生活照",
        "动漫女角色",
        "影视剧女角色",
        "短片 女性角色",
        "校园 女性",
        "女性 自拍",
        "女生",
        "女生自拍",
    ]
    
    # 下载每个关键词的图片
    for keyword in keywords:
        # 从必应下载图片
        downloader.download(
            keyword,
            limit=10,
            output_dir="女性图片集",
            adult_filter_off=False,
            force_replace=False,
            timeout=60
        )
        print(f"完成下载关键词: {keyword}")
        print("-" * 50)


if __name__ == "__main__":
    # download_images_simple()
    main()
