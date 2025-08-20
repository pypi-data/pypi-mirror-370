from __future__ import annotations

import os
import pretty_errors
import rich
from rich import print
from typing import Literal, Tuple, Union
from pathlib import Path
import datetime


class Cli:
    def __init__(self):
        self._config = {
            "server": "http://127.0.0.1:8000",
            "croc_relay": "142.171.214.153:27011",
        }

        # 加载 Sparrow 配置文件
        self.sparrow_config = self._load_sparrow_config()

        self.flaxkv_server = self.sparrow_config.get("flaxkv_server", os.environ.get("FLAXKV_SERVER"))
        if self.flaxkv_server:
            try:
                from flaxkv import FlaxKV
                self._db = FlaxKV(db_name="sparrow", root_path_or_url=self.flaxkv_server, show_progress=True)
            except Exception as e:
                print(f"Error initializing FlaxKV: {e}")
                self._db = None
        else:
            self._db = None

    def _get_config_search_paths(self):
        """获取配置文件的搜索路径列表，按优先级排序"""
        config_filename = ".sparrow_config.yaml"
        search_paths = []
        
        # 1. 当前工作目录（最高优先级）
        search_paths.append(Path.cwd() / config_filename)
        
        # 2. 项目根目录（如果当前不在项目根目录）
        # 尝试向上查找直到找到 .git 目录或到达根目录
        current_path = Path.cwd()
        while current_path != current_path.parent:
            if (current_path / ".git").exists() or (current_path / "pyproject.toml").exists() or (current_path / "setup.py").exists():
                project_config = current_path / config_filename
                if project_config not in search_paths:
                    search_paths.append(project_config)
                break
            current_path = current_path.parent
        
        # 3. 用户家目录
        home_path = Path.home() / config_filename
        if home_path not in search_paths:
            search_paths.append(home_path)
        
        # 4. XDG 配置目录 (Linux/macOS)
        if os.name != 'nt':  # 非 Windows 系统
            xdg_config_home = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / ".config"))
            xdg_path = Path(xdg_config_home) / "sparrow" / config_filename
            if xdg_path not in search_paths:
                search_paths.append(xdg_path)
        else:
            # Windows 用户配置目录
            appdata = os.environ.get('APPDATA')
            if appdata:
                win_path = Path(appdata) / "sparrow" / config_filename
                if win_path not in search_paths:
                    search_paths.append(win_path)
        
        # 5. 系统级配置目录
        if os.name != 'nt':  # Linux/macOS
            search_paths.append(Path("/etc/sparrow") / config_filename)
        else:  # Windows
            programdata = os.environ.get('PROGRAMDATA')
            if programdata:
                search_paths.append(Path(programdata) / "sparrow" / config_filename)
        
        return search_paths

    def _load_sparrow_config(self):
        """从多个路径加载 Sparrow 配置文件"""
        from sparrow import yaml_load
        
        # 默认配置
        default_config = {
            "flaxkv_server": None,
            "mllm": {
                "model": "gemma3:latest",
                "base_url": "http://localhost:11434/v1",
                "api_key": "EMPTY"
            }
        }
        
        config_paths = self._get_config_search_paths()
        loaded_config = default_config.copy()
        loaded_from = None
        
        # 按优先级依次尝试加载配置文件
        for config_path in config_paths:
            try:
                if config_path.exists():
                    file_config = yaml_load(str(config_path))
                    if file_config:
                        # 深度合并配置
                        loaded_config = self._deep_merge_config(loaded_config, file_config)
                        loaded_from = str(config_path)
                        break
            except Exception as e:
                print(f"警告: 无法加载配置文件 {config_path}: {e}")
                continue
        
        if not loaded_from:
            print(f"以下路径中未找到配置文件。搜索路径:")
            for path in config_paths:  # 只显示前3个最常用的路径
                print(f"  - {path.resolve()}")
        
            print("请执行 `sparrow init-config` 初始化配置文件")
        
        return loaded_config

    def _deep_merge_config(self, base_config, new_config):
        """深度合并配置字典"""
        result = base_config.copy()
        
        for key, value in new_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_config(result[key], value)
            else:
                result[key] = value
        
        return result

    @staticmethod
    def init_config(path: str = None):
        """初始化配置文件
        
        Args:
            path (str): 配置文件路径，默认为当前目录下的 .sparrow_config.yaml
        """
        if path is None:
            path = ".sparrow_config.yaml"
        
        config_path = Path(path)
        
        if config_path.exists():
            print(f"配置文件已存在: {config_path.resolve()}")
            return
        
        # 默认配置内容
        default_config_content = """# Sparrow 配置文件
# 此文件用于配置 Sparrow 工具的默认参数

# FlaxKV 服务器配置
flaxkv_server: null  # 例如: "http://localhost:8000"

# MLLM (多模态大语言模型) 相关配置
mllm:
  # 默认模型名称
  model: "gemma3:latest"
  
  # API 基础URL
  base_url: "http://localhost:11434/v1"
  
  # API 密钥
  api_key: "EMPTY"

"""
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(default_config_content)
            print(f"已创建配置文件: {config_path.resolve()}")
            print("请根据需要编辑配置文件。")
        except Exception as e:
            print(f"创建配置文件失败: {e}")

    def get_config(self, key: str = None):
        """获取配置值
        
        Args:
            key (str): 配置键，支持点号分隔的嵌套键，如 'mllm.model'
                      如果为 None，返回整个配置
        """
        if key is None:
            return self.sparrow_config
        
        keys = key.split('.')
        value = self.sparrow_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return None

    def set(self, key: str, filepath: str):
        def _get_file_metadata(filepath: str) -> dict:
            file_stat = os.stat(filepath)
            return {
                "size": file_stat.st_size,
                "created_time": datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified_time": datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "accessed_time": datetime.datetime.fromtimestamp(file_stat.st_atime).isoformat(),
            }
        
        with open(filepath, 'rb') as f:
            content = f.read()
        self._db[key] = {
            "filename": Path(filepath).name,
            "content": content, 
            "metadata": _get_file_metadata(filepath)
            }
        self._db.write_immediately(block=True)

    def keys(self):
        from .string.color_string import rgb_string, color_const
        print(rgb_string(str(list(self._db.keys())), color_const.GREEN))

    def get(self, key: str, delete=False):
        from .string.color_string import rgb_string
        data = self._db[key] if key in self._db else None
        if data:
            with open(data["filename"], 'wb') as f:
                f.write(data["content"])
            if delete:
                del self._db[key]
                self._db.write_immediately(block=True)
        else:
            print(rgb_string(f"WARNING: {key} not found"))

    def info(self, key: str):
        from .string.color_string import rgb_string, color_const
        data = self._db.get(key)
        if data:
            print(rgb_string(f"Key: {key}", color_const.BLUE))
            print(rgb_string(f"Filename: {data['filename']}", color_const.BLUE))
            print(rgb_string(f"Size: {len(data['content'])} bytes", color_const.BLUE))
            print(rgb_string(f"Metadata: {data.get('metadata', {})}", color_const.BLUE))
        else:
            print(rgb_string(f"WARNING: {key} not found", color_const.RED))

    def clean(self):
        raise NotImplementedError

    @staticmethod
    def download(repo_id, download_dir=None, backend="huggingface", token=None, **kwargs):
        from .models.downloads import download_model
        download_model(repo_id, download_dir=download_dir, backend=backend, token=token, **kwargs)

    @staticmethod
    def deduplicate(in_file: str, out_file: str, target_col='data', chunk_size = 200, threshold=None, method:Literal["edit", "rouge", "bleu"]='edit', use_jieba=False):
        if method == "edit":
            from .nlp.deduplicate import EditSimilarity
            simi = EditSimilarity()
            if threshold is None:
                threshold = 0.7
        elif method == "rouge":
            from .nlp.deduplicate import RougeSimilarity
            simi = RougeSimilarity(use_jieba=use_jieba)
            if threshold is None:
                threshold = 0.5
        elif method == "bleu":
            from .nlp.deduplicate import BleuSimilarity
            simi = BleuSimilarity(use_jieba=use_jieba)
            if threshold is None:
                threshold = 0.5
        else:
            raise ValueError(f"method should be one of 'edit', 'rouge', 'bleu', but got {method}")
        simi.load_data(in_file, target_col=target_col)
        simi.deduplicate(chunk_size=chunk_size, save_to_file=out_file, threshold=threshold)

    @staticmethod
    def prev(extract_dir):
        from .parser.code.code import extract_to_md
        extract_to_md(extract_dir)

    def send(self, files_or_folder: str, **kwargs):
        command = f"croc  --relay {self._config['croc_relay']} send {files_or_folder} " + " ".join([f"--{k} {v}" for k, v in kwargs.items()])
        os.system(command)
    def send2(self, filename: str, space: str):
        from flaxkv import FlaxKV
        db = FlaxKV(db_name=space, root_path_or_url=self._config['server'], show_progress=True)
        with open(filename, 'rb') as f:
            content = f.read()
            db[filename] = content
            db.write_immediately(write=True)
            # 流式读取
            # while True:
            #     data = f.read(1024)
            #     if not data:
            #         break

    def recv2(self,filename: str, space: str):
        from flaxkv import FlaxKV
        db = FlaxKV(db_name=space, root_path_or_url=self._config['server'], show_progress=True)
        content = db[filename]
        with open(filename, 'wb') as f:
            f.write(content)
        db.buffer_dict.clear()

    @staticmethod
    def post(url: str, data: dict, concurrent: int = 10, ):
        import asyncio
        from .api.fetch import run
        asyncio.run(
            run(url=url, data=data, concurrent=concurrent, method="POST")
        )

    @staticmethod
    def get_url(url, data=None, concurrent=10):
        import asyncio
        from .api.fetch import run
        if data is None:
            data = {}
        asyncio.run(
            run(url=url, data=data, concurrent=concurrent, method="GET")
        )

    @staticmethod
    def timer(dt=0.01):
        from .widgets import timer
        return timer(dt)

    @staticmethod
    def auto_commit(
            repo_path='.',
            remote_repo_name: str | None = None,
            name="K.Y.Bot", email="beidongjiedeguang@gmail.com",
            interval=60
    ):
        from .git.monitor import start_watcher
        start_watcher(repo_path=repo_path, remote_repo_name=remote_repo_name,
                      name=name, email=email,
                      interval=interval)

    @staticmethod
    def install_node(version=16):
        from .cli.script import install_node_with_nvm
        install_node_with_nvm(version=version)

    @staticmethod
    def install_nvim(version='0.9.2'):
        from .cli.script import install_nvim
        install_nvim(version=version)

    @staticmethod
    def uninstall_nvim():
        from .cli.script import uninstall_nvim
        uninstall_nvim()

    @staticmethod
    def save_docker_images(filedir='.', skip_exists=True, use_stream=False):
        kwargs = locals()
        from .docker import save_docker_images
        return save_docker_images(**kwargs)

    @staticmethod
    def load_docker_images(filename_pattern="./*", skip_exists=True):
        kwargs = locals()
        from .docker import load_docker_images
        return load_docker_images(**kwargs)

    @staticmethod
    def docker_gpu_stat():
        from .docker.nvidia_stat import docker_gpu_stat
        return docker_gpu_stat()

    @staticmethod
    def pack(source_path: str, target_path=None, format='gztar'):
        kwargs = locals()
        from .utils.compress import pack
        return pack(**kwargs)

    @staticmethod
    def unpack(filename: str, extract_dir=None, format=None):
        kwargs = locals()
        from .utils.compress import unpack
        return unpack(**kwargs)

    @staticmethod
    def start_server(port=50001, deque_maxlen=None):
        kwargs = locals()
        from .multiprocess import start_server
        return start_server(**kwargs)

    @staticmethod
    def kill(ports: Tuple[int], view=False):
        from .multiprocess import kill
        return kill(ports, view)

    @staticmethod
    def split(file_path: str, chunk_size=1024*1024*1024):
        """将大文件分割成多个块。

        Args:
            file_path (str): 原始文件的路径。
            chunk_size (int): 每个块的大小（字节）。

        """

        from .io.ops import split_file
        return split_file(file_path, chunk_size=chunk_size)

    @staticmethod
    def merge(input_prefix, input_dir='./', output_path=None):
        """将分割后的文件块拼接回一个文件。

        Args:
            input_prefix (str): 分割文件的前缀。
            input_dir (str): 原始文件所在目录。
            output_path (str): 拼接后的文件路径。

        """
        from .io.ops import join_files
        return join_files(input_prefix=input_prefix, input_dir=input_dir, output_path=output_path)

    @staticmethod
    def clone(url: str, save_path=None, branch=None, proxy=False):
        kwargs = locals()
        from .cli.git import clone
        return clone(**kwargs)

    @staticmethod
    def get_ip(env="inner"):
        kwargs = locals()
        from .utils.net import get_ip
        return get_ip(**kwargs)

    @staticmethod
    def create(project_name: str, out=None):
        """创建项目
        Parameter
        ---------
        project_name : str
            package name
        out : str | None
            项目生成路径
        """
        if out is None:
            out = project_name
        from .template.scaffold.core import create_project
        return create_project(project_name, out)

    @staticmethod
    def milvus(flag='start'):
        kwargs = locals()
        from .ann import milvus
        return milvus(**kwargs)

    @staticmethod
    def reminder(port=50001):
        import uvicorn
        uvicorn.run(
            app="sparrow.espec.app:app",
            host="0.0.0.0",
            port=port,
            workers=1,
            app_dir="..",
        )

    @staticmethod
    def subtitles(video: str):
        from .subtitles import transcribe, translate, merge_subs_with_video
        origin_srt = transcribe(video)
        translated_srt = translate(origin_srt)
        merge_subs_with_video(video, origin_srt, translated_srt)

    @staticmethod
    def merge_subtitles(srt_en: str, srt_zh: str):
        from .subtitles import merge_subs
        merge_subs(srt_en=srt_en, srt_zh=srt_zh)

    @staticmethod
    def translate_subt(srt_name: str):
        """translate english srt file to chinese srt file"""
        from .subtitles import translate
        translate(subtitles_file=srt_name)


    @staticmethod
    def test_torch():
        from sparrow.experimental import test_torch

    @staticmethod
    def gen_key(rsa_name: str, email='beidongjiedeguang@gmail.com'):
        """
        Generate an SSH key pair for a given RSA name.

        Parameters:
            rsa_name (str): The name to be used for the RSA key pair.
            email (str): The email address to associate with the key pair. Default is 'beidongjiedeguang@gmail.com'.

        Returns:
            None

        """
        from pathlib import Path
        rsa_path = str(Path.home() / '.ssh' / f'id_rsa_{rsa_name}')
        command = f"ssh-keygen -t rsa -C {email} -f {rsa_path}"
        os.system(command)

        with open(rsa_path + '.pub', 'r', encoding='utf8') as f:
            rich.print("pub key:\n")
            print(f.read())

        config_path = str(Path.home() / '.ssh' / 'config')
        rich.print(f"""你可能需要将新添加的key 写入 {config_path}文件中，内容大概是：
# 如果是远程服务器
Host {rsa_name}
  HostName 198.211.51.254
  User root
  Port 22
  IdentityFile {rsa_path}
  
# 或者 git
Host {rsa_name}
  HostName github.com
  User git
  IdentityFile {rsa_path}
  IdentitiesOnly yes
""")

    @staticmethod
    def video_dedup(video_path: str, method: str = "phash", threshold: float = None, step: int = 1, resize: int = 256, workers: int = 1, fps: float = None, out_dir: str = "out"):
        """
        Detect and save unique frames from a video.

        Args:
            video_path (str): Path to the input video file.
            method (str): Method for comparing frames (default: "phash").
            threshold (float): Similarity threshold (method-specific default if not provided).
            step (int): Sample every Nth frame (default: 1).
            resize (int): Resize frame width before processing (default: 256).
            workers (int): Number of worker processes for hashing (default: 1).
            fps (float): Target frames per second to sample (default: None).
            out_dir (str): Base directory to save unique frames (default: "out").
                           Frames will be saved in '{out_dir}/{video_filename}/'.
        """
        from sparrow.dedup.video import VideoFrameDeduplicator
        from pathlib import Path  # Import Path
        from sparrow.performance._measure_time import MeasureTime # For timing

        # 延迟导入 cv2
        try:
            import cv2
        except ImportError:
            print("未检测到 opencv-python (cv2) 库。请先安装：pip install opencv-python")
            return

        mt = MeasureTime().start()

        try:
            dedup = VideoFrameDeduplicator(
                method=method,
                threshold=threshold,
                step=step,
                resize=resize,
                workers=workers,
                fps=fps
            )
        except ValueError as e:
            print(f"Error initializing deduplicator: {e}")
            return # Or raise the error

        try:
            count = dedup.process_and_save_unique_frames(video_path, out_dir)
            mt.show_interval(f"Completed processing. Saved {count} frames.") # Use simplified message
        except Exception as e:
            print(f"Operation failed: {e}")

    @staticmethod
    def frames_to_video(frames_dir: str, output_video: str = None, fps: float = 15.0, codec: str = 'mp4v', use_av: bool = False):
        """
        将一个目录中的帧图像合成为视频。
        
        Args:
            frames_dir (str): 包含帧图像的目录路径。
            output_video (str, optional): 输出视频的路径。如果为None，则默认为frames_dir旁边的同名mp4文件。
            fps (float, optional): 输出视频的帧率。默认为15.0。
            codec (str, optional): 视频编解码器。默认为'mp4v'，可选'avc1'等。
            use_av (bool, optional): 是否使用PyAV库加速（如果可用）。默认为False。
        """
        from sparrow.dedup.video import VideoFrameDeduplicator
        from pathlib import Path
        from sparrow.performance._measure_time import MeasureTime

        mt = MeasureTime().start()
        dedup = VideoFrameDeduplicator()  # 使用默认参数，这里实际上不需要设置去重参数
        
        try:
            output_path = dedup.frames_to_video(
                frames_dir=frames_dir,
                output_video=output_video,
                fps=fps,
                codec=codec,
                use_av=use_av
            )
            mt.show_interval(f"完成视频合成: {output_path}")
        except Exception as e:
            print(f"操作失败: {e}")

    @staticmethod
    def dedup_and_create_video(video_path: str, method: str = "phash", threshold: float = None, 
                              step: int = 1, resize: int = 256, workers: int = 1, fps: float = None, 
                              out_dir: str = "out", output_video: str = None, video_fps: float = 15.0, 
                              codec: str = 'mp4v', use_av: bool = False):
        """
        从视频中提取唯一帧并合成新视频。

        Args:
            video_path (str): 输入视频文件路径。
            method (str): 比较帧的方法 (默认: "phash")。
            threshold (float): 相似度阈值 (如果未提供，则使用方法特定的默认值)。
            step (int): 每N帧采样一次 (默认: 1)。
            resize (int): 处理前调整帧宽度 (默认: 256)。
            workers (int): 哈希计算的工作进程数 (默认: 1)。
            fps (float): 提取的目标采样帧率 (默认: None)。
            out_dir (str): 保存唯一帧的基础目录 (默认: "out")。
            output_video (str): 输出视频的路径 (默认: 在输入目录旁)。
            video_fps (float): 输出视频的帧率 (默认: 15.0)。
            codec (str): 视频编解码器 (默认: 'mp4v')。
            use_av (bool): 合成时使用PyAV库加速 (默认: False)。
        """
        from sparrow.dedup.video import VideoFrameDeduplicator
        from pathlib import Path
        from sparrow.performance._measure_time import MeasureTime

        mt = MeasureTime().start()

        try:
            dedup = VideoFrameDeduplicator(
                method=method,
                threshold=threshold,
                step=step,
                resize=resize,
                workers=workers,
                fps=fps
            )
        except ValueError as e:
            print(f"初始化去重器时出错: {e}")
            return
        
        try:
            # 1. 提取帧
            count = dedup.process_and_save_unique_frames(video_path, out_dir)
            print(f"完成提取。保存了 {count} 帧。")
            
            # 确定帧目录路径
            src_path = Path(video_path)
            if src_path.exists() and src_path.is_file():
                frames_dir = Path(out_dir) / src_path.stem
            else:
                frames_dir = Path(out_dir)
                
            # 2. 合成视频
            output_path = dedup.frames_to_video(
                frames_dir=frames_dir,
                output_video=output_video,
                fps=video_fps,
                codec=codec,
                use_av=use_av
            )
            mt.show_interval(f"完成流程。提取 {count} 帧并合成视频: {output_path}")
        except Exception as e:
            print(f"操作失败: {e}")

    @staticmethod
    def download_images(keywords, num_images=50, engines="google", save_dir="downloaded_images", save_mapping=True, flickr_api_key=None, flickr_api_secret=None, website_urls=None, url_list_file=None):
        """
        从搜索引擎下载图片
        
        Args:
            keywords (str): 搜索关键词，多个关键词用逗号分隔
            num_images (int): 每个关键词要下载的图片数量 (默认: 50)
            engines (str): 要使用的搜索引擎，多个引擎用逗号分隔 (默认: "bing,google")
                          传统引擎: "bing", "google", "baidu", "flickr"
                          免费图片源: "unsplash", "pixabay", "pexels" (无需API密钥，高质量)
                          特殊功能: "website", "urls"
            save_dir (str): 图片保存目录 (默认: "downloaded_images")
            save_mapping (bool): 是否保存图像元数据到metadata.jsonl文件 (默认: True)
            flickr_api_key (str): Flickr API密钥（使用flickr引擎时需要）
            flickr_api_secret (str): Flickr API密钥（使用flickr引擎时需要）
            website_urls (str): 网站URL列表，用逗号分隔（使用website引擎时需要）
            url_list_file (str): 包含图片URL列表的文件路径（使用urls引擎时需要）
        
        Examples:
            # 下载单个关键词的图片
            sparrow download_images "猫咪"
            
            # 下载多个关键词，指定数量和引擎
            sparrow download_images "猫咪,狗狗" --num_images=100 --engines="bing,google,baidu"
            
            # 使用免费高质量图片源（推荐）
            sparrow download_images "风景" --engines="unsplash,pixabay,pexels" --num_images=100
            
            # 使用Flickr引擎（需要API密钥）
            sparrow download_images "风景" --engines="flickr" --flickr_api_key="your_api_key" --flickr_api_secret="your_api_secret"
            
            # 从特定网站抓取图片
            sparrow download_images "产品图片" --engines="website" --website_urls="https://example.com,https://another-site.com"
            
            # 从URL列表文件下载
            sparrow download_images "自定义图片" --engines="urls" --url_list_file="image_urls.txt"
            
            # 指定保存目录（元数据默认保存）
            sparrow download_images "风景" --save_dir="my_images"
            
            # 禁用元数据保存
            sparrow download_images "风景" --save_mapping=False
        """
        from .web.image_downloader import download_images_cli
        
        # 处理关键词参数
        if isinstance(keywords, str):
            keyword_list = [k.strip() for k in keywords.split(',')]
        else:
            keyword_list = keywords
        
        # 处理搜索引擎参数
        if isinstance(engines, str):
            engine_list = [e.strip() for e in engines.split(',')]
        else:
            engine_list = engines
        
        # 验证搜索引擎
        valid_engines = ["bing", "google", "baidu", "flickr", "unsplash", "pixabay", "pexels", "website", "urls"]
        invalid_engines = [e for e in engine_list if e not in valid_engines]
        if invalid_engines:
            print(f"警告: 不支持的搜索引擎: {invalid_engines}")
            print(f"支持的搜索引擎: {valid_engines}")
            engine_list = [e for e in engine_list if e in valid_engines]
        
        if not engine_list:
            print("错误: 没有有效的搜索引擎")
            return
        
        # 验证特殊引擎的必需参数
        if "website" in engine_list and not website_urls:
            print("错误: 使用website引擎时必须提供 --website_urls 参数")
            return
        
        if "urls" in engine_list and not url_list_file:
            print("错误: 使用urls引擎时必须提供 --url_list_file 参数")
            return
        
        print(f"准备下载关键词: {keyword_list}")
        print(f"使用搜索引擎: {engine_list}")
        
        # 调用下载函数
        try:
            stats = download_images_cli(
                keywords=keyword_list,
                num_images=num_images,
                engines=engine_list,
                save_dir=save_dir,
                save_mapping=save_mapping,
                flickr_api_key=flickr_api_key,
                flickr_api_secret=flickr_api_secret,
                website_urls=website_urls,
                url_list_file=url_list_file
            )
            
            # 打印详细统计信息
            print("\n=== 下载统计 ===")
            for keyword, engines_stats in stats["downloads"].items():
                print(f"关键词 '{keyword}':")
                for engine, count in engines_stats.items():
                    print(f"  {engine}: {count} 张图片")
            
            return stats
            
        except Exception as e:
            print(f"下载过程中出现错误: {e}")
            return None

    def mllm_call_table(
        self,
        table_path: str,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        image_col: str = "image",
        system_prompt: str = "你是一个专业的图像识别专家。",
        text_prompt: str = "请描述这张图像。",
        sheet_name: str = 0,
        max_num=None,
        output_file: str = "table_results.csv",
        temperature: float = 0.1,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        对表格中的图像列进行批量大模型识别和分析
        
        Args:
            table_path (str): 表格文件路径（支持.xlsx和.csv格式）
            model (str): 使用的模型名称，默认从配置文件读取
            base_url (str): API基础URL地址，默认从配置文件读取
            api_key (str): API密钥，默认从配置文件读取
            image_col (str): 图像列名，默认为"image"
            system_prompt (str): 系统提示词，默认为空
            text_prompt (str): 对图像的提示词，默认为"请描述这幅图片"
            sheet_name (str): Excel文件的sheet名称，默认为0
            max_num (int): 最大处理图像数量限制，默认处理全部
            output_file (str): 结果输出文件路径，支持.json和.csv格式，根据扩展名自动选择格式
            temperature (float): 生成温度参数，默认为0.1
            max_tokens (int): 最大生成token数，默认为2000
            **kwargs: 其他模型参数
            
        Examples:
            # 基本用法 - 使用配置文件默认值
            sparrow mllm_call_table "images.xlsx"
            
            # 输出为CSV格式
            sparrow mllm_call_table "images.xlsx" --output_file="results.csv"
            
            # 自定义参数
            sparrow mllm_call_table "data.csv" --model="gpt-4o-mini" \
                --base_url="https://api.openai.com/v1" \
                --image_col="图片路径" \
                --text_prompt="详细描述这张图片的内容" \
                --max_num=50 \
                --output_file="results.csv"
                
            # 使用系统提示词
            sparrow mllm_call_table "products.xlsx" \
                --system_prompt="你是一个专业的产品分析师" \
                --text_prompt="分析这个产品图片的特点和卖点" \
                --output_file="products_analysis.csv"
        """
        import asyncio
        import json
        import csv
        from pathlib import Path
        from sparrow.mllm.mllm_client import MllmClient
        
        # 创建 Cli 实例以访问配置
        # cli = Cli()
        
        # 从配置文件获取默认值
        mllm_config = self.sparrow_config.get("mllm", {})
        
        # 应用默认值（只有当参数为 None 时才使用配置文件的值）
        if model is None:
            model = mllm_config.get("model", "gemma3:latest")
        if base_url is None:
            base_url = mllm_config.get("base_url", "http://localhost:11434/v1")
        if api_key is None:
            api_key = mllm_config.get("api_key", "EMPTY")
        
        async def _run_call_table_images():
            # 初始化MLLM客户端
            client = MllmClient(
                model=model,
                base_url=base_url,
                api_key=api_key,
                **kwargs
            )
            
            try:
                # 调用表格图像处理方法
                responses = await client.table.call_table_images(
                    table_path=table_path,
                    image_col=image_col,
                    system_prompt=system_prompt,
                    text_prompt=text_prompt,
                    sheet_name=sheet_name,
                    max_num=max_num,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                # 处理输出
                if output_file:
                    # 根据文件扩展名决定输出格式
                    file_path = Path(output_file)
                    file_extension = file_path.suffix.lower()
                    
                    if file_extension == '.csv':
                        # 保存为CSV格式
                        with open(output_file, 'w', encoding='utf-8', newline='') as f:
                            writer = csv.writer(f)
                            # 写入表头
                            writer.writerow(['index', 'response'])
                            # 写入数据
                            for i, response in enumerate(responses):
                                writer.writerow([i, response])
                    else:
                        # 保存为JSON格式（默认）
                        results = []
                        for i, response in enumerate(responses):
                            results.append({
                                "index": i,
                                "response": response
                            })
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)
                    
                    print(f"结果已保存到: {Path(output_file).resolve()}")
                    print(f"共处理 {len(responses)} 张图片")
                else:
                    # 打印到控制台
                    print(f"\n=== 图像识别结果 (共 {len(responses)} 张图片) ===")
                    for i, response in enumerate(responses):
                        print(f"\n--- 图片 {i+1} ---")
                        print(response)
                        print("-" * 50)
                
                return responses
                
            except Exception as e:
                print(f"处理过程中出现错误: {e}")
                return None
        
        # 运行异步函数
        asyncio.run(_run_call_table_images())

    def mllm_call_images(
        self,
        folder_path: str,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        system_prompt: str = "你是一个专业的图像识别专家。",
        text_prompt: str = "请描述这张图像。",
        recursive: bool = True,
        max_num: int = None,
        extensions: str = None,
        output_file: str = "results.csv",
        temperature: float = 0.1,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        对文件夹中的图像进行批量大模型识别和分析
        
        Args:
            folder_path (str): 文件夹路径
            model (str): 使用的模型名称，默认从配置文件读取
            base_url (str): API基础URL地址，默认从配置文件读取
            api_key (str): API密钥，默认从配置文件读取
            system_prompt (str): 系统提示词，默认为空
            text_prompt (str): 对图像的提示词，默认为"请描述这幅图片"
            recursive (bool): 是否递归扫描子文件夹，默认为True
            max_num (int): 最大处理图像数量限制，默认处理全部
            extensions (str): 支持的文件扩展名，用逗号分隔，如".jpg,.png,.gif"，默认使用所有支持的格式
            output_file (str): 结果输出文件路径，支持.json和.csv格式，根据扩展名自动选择格式
            temperature (float): 生成温度参数，默认为0.1
            max_tokens (int): 最大生成token数，默认为2000
            **kwargs: 其他模型参数
            
        Examples:
            # 基本用法 - 使用配置文件默认值
            sparrow mllm_call_images "./images"
            
            # 输出为CSV格式
            sparrow mllm_call_images "./images" --output_file="results.csv"
            
            # 自定义参数
            sparrow mllm_call_images "./photos" --model="gpt-4o-mini" \
                --base_url="https://api.openai.com/v1" \
                --text_prompt="详细描述这张图片的内容" \
                --max_num=50 \
                --recursive=False \
                --extensions=".jpg,.png" \
                --output_file="results.csv"
                
            # 使用系统提示词
            sparrow mllm_call_images "./products" \
                --system_prompt="你是一个专业的产品分析师" \
                --text_prompt="分析这个产品图片的特点和卖点" \
                --output_file="products_analysis.csv"
        """
        import asyncio
        import json
        import csv
        from pathlib import Path
        from sparrow.mllm.mllm_client import MllmClient
        
        # 创建 Cli 实例以访问配置
        # cli = Cli()
        
        # 从配置文件获取默认值
        mllm_config = self.sparrow_config.get("mllm", {})
        
        # 应用默认值（只有当参数为 None 时才使用配置文件的值）
        if model is None:
            model = mllm_config.get("model", "gemma3:latest")
        if base_url is None:
            base_url = mllm_config.get("base_url", "http://localhost:11434/v1")
        if api_key is None:
            api_key = mllm_config.get("api_key", "EMPTY")

        
        async def _run_call_folder_images():
            # 初始化MLLM客户端
            client = MllmClient(
                model=model,
                base_url=base_url,
                api_key=api_key,
                **kwargs
            )
            
            try:
                # 处理扩展名参数
                ext_set = None
                if extensions:
                    # 将字符串转换为集合
                    ext_list = [ext.strip() for ext in extensions.split(',')]
                    ext_set = set(mllm_config["extensions"])
                
                # 调用文件夹图像处理方法
                responses, image_files = await client.folder.call_folder_images(
                    folder_path=folder_path,
                    system_prompt=system_prompt,
                    text_prompt=text_prompt,
                    recursive=recursive,
                    max_num=max_num,
                    extensions=ext_set,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    return_image_files=True,
                    **kwargs
                )
                
                # 处理输出
                if output_file:
                    # 根据文件扩展名决定输出格式
                    file_path = Path(output_file)
                    file_extension = file_path.suffix.lower()
                    
                    if file_extension == '.csv':
                        # 使用Pandas 保存为CSV格式
                        import pandas as pd
                        df = pd.DataFrame(
                            {
                                "index": [i for i in range(len(responses))],
                                "image": image_files,
                                "response": responses,
                            },
                        )
                        df.to_csv(output_file, index=False, encoding='utf-8')
                    else:
                        # 保存为JSON格式
                        results = []
                        for i, response in enumerate(responses):
                            results.append(
                            {
                                "index": i,
                                "image": image_files[i],
                                "response": response,
                            })
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=4)
                    
                    print(f"结果已保存到: {Path(output_file).resolve()}")
                else:
                    # 打印到控制台
                    print(f"\n=== 图像识别结果 (共 {len(responses)} 张图片) ===")
                    for i, response in enumerate(responses):
                        print(f"\n--- 图片 {i+1} ---")
                        print(response)
                        print("-" * 50)
                
                return responses
                
            except Exception as e:
                print(f"处理过程中出现错误: {e}")
                return None
        
        # 运行异步函数
        asyncio.run(_run_call_folder_images())

    def table_viewer(
        self,
        file_path: str = None,
        port: int = 8080,
        host: str = "127.0.0.1",
        sheet_name: Union[str, int] = 0,
        image_columns: str = None,
        auto_detect_images: bool = True,
        auto_open: bool = True
    ):
        """
        启动交互式表格查看器，支持图片预览、筛选、编辑等功能
        
        Args:
            file_path (str, optional): 表格文件路径（支持.xlsx, .xls, .csv格式）。如果不指定，启动空白服务器，可通过网页上传文件
            port (int): 服务器端口，默认8080
            host (str): 服务器主机地址，默认127.0.0.1
            sheet_name (Union[str, int]): Excel文件的sheet名称或索引，默认为0
            image_columns (str): 指定图片列名，用逗号分隔，如"image,photo"
            auto_detect_images (bool): 是否自动检测图片列，默认True
            auto_open (bool): 是否自动打开浏览器，默认True
            
        Features:
            - 支持大表格高性能展示（分页、虚拟滚动）
            - 自动识别并预览图片URL（本地文件和网络链接）
            - 强大的筛选功能（包含、等于、大于等多种条件）
            - 双击单元格即可编辑内容
            - 支持保存修改到原文件
            - 可拖拽调整列宽
            - 响应式设计，支持宽屏显示
            
        Examples:
            # 启动空白服务器（可通过网页上传文件）
            sparrow table_viewer
            
            # 基本用法 - 直接加载文件
            sparrow table_viewer "data.xlsx"
            
            # 指定端口和不自动打开浏览器
            sparrow table_viewer "data.csv" --port=9090 --auto_open=False
            
            # 指定图片列（不使用自动检测）
            sparrow table_viewer "products.xlsx" --image_columns="product_image,thumbnail" --auto_detect_images=False
            
            # 查看特定sheet
            sparrow table_viewer "report.xlsx" --sheet_name="Sheet2"
            
        Performance:
            - 支持百万级行数据（分页加载）
            - 图片懒加载和缓存
            - 内存优化的数据处理
            - 快速搜索和筛选
        """
        from .table_viewer import TableViewerServer
        from pathlib import Path
        
        # 验证文件（如果提供了文件路径）
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"文件不存在: {file_path}")
                return
            
            if not file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                print(f"不支持的文件格式: {file_path.suffix}")
                print("支持的格式: .csv, .xlsx, .xls")
                return
            file_path = str(file_path)
        else:
            print("启动空白表格查看器，你可以通过网页上传文件")
        
        # 处理图片列参数
        image_cols = None
        if image_columns:
            image_cols = [col.strip() for col in image_columns.split(',')]
        
        try:
            # 创建并启动服务器
            server = TableViewerServer(
                file_path=file_path,
                port=port,
                host=host,
                sheet_name=sheet_name,
                image_columns=image_cols,
                auto_detect_images=auto_detect_images
            )
            server.run(auto_open=auto_open)
            
        except Exception as e:
            print(f"启动表格查看器失败: {e}")
            import traceback
            traceback.print_exc()


def fire_commands():
    import fire
    fire.Fire(Cli)


def typer_commands():
    import typer
    app = typer.Typer()
    # [app.command()(i) for i in func_list]
    # app()


def main():
    # 添加自动补全支持
    try:
        import argcomplete
        import sys
        
        # 为 fire 命令设置自动补全
        if len(sys.argv) > 1 and sys.argv[1] in ['--completion-script', '--completion']:
            # 生成补全脚本
            print(f"""
# 将以下内容添加到你的 shell 配置文件中 (如 ~/.bashrc, ~/.zshrc):

# For bash:
eval "$(_SP_COMPLETE=bash_source sp)"
eval "$(_SPR_COMPLETE=bash_source spr)" 
eval "$(_SPARROW_COMPLETE=bash_source sparrow)"

# For zsh:
eval "$(_SP_COMPLETE=zsh_source sp)"
eval "$(_SPR_COMPLETE=zsh_source spr)"
eval "$(_SPARROW_COMPLETE=zsh_source sparrow)"

# 或者运行以下命令来安装补全:
activate-global-python-argcomplete
""")
            return
            
        # 尝试启用 argcomplete (如果可用)
        argcomplete.autocomplete(None)
    except ImportError:
        pass  # argcomplete 不可用时忽略
    
    fire_commands()
