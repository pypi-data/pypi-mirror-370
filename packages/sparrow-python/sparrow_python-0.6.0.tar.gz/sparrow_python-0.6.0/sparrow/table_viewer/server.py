"""
表格查看器后端服务 - 基于FastAPI
支持表格展示、图片URL预览、筛选、编辑等功能
"""

from fastapi import FastAPI, Request, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import json
import uvicorn
import webbrowser
import asyncio
from dataclasses import dataclass
import re
import requests
import aiohttp
import aiofiles
from urllib.parse import urlparse
import hashlib
import tempfile
import os
import random
import time
from sparrow.helpers.parser import split_image_paths


@dataclass
class FilterConfig:
    """筛选配置"""

    column: str
    operator: str  # eq, ne, contains, startswith, endswith, gt, lt, ge, le
    value: Any


class TableViewerServer:
    """表格查看器服务器"""

    def __init__(
        self,
        file_path: str,
        port: int = 8080,
        host: str = "127.0.0.1",
        sheet_name: Union[str, int] = 0,
        image_columns: Optional[List[str]] = None,
        auto_detect_images: bool = True,
    ):
        self.file_path = Path(file_path)
        self.port = port
        self.host = host
        self.sheet_name = sheet_name
        self.image_columns = image_columns or []
        self.auto_detect_images = auto_detect_images

        # 初始化FastAPI应用
        self.app = FastAPI(
            title="Sparrow Table Viewer",
            description="高性能表格查看器，支持图片预览、筛选、编辑",
            version="1.0.0",
        )

        # 设置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 挂载静态文件
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

        # 加载数据
        self.df = self._load_data()
        self.original_df = self.df.copy()

        # 自动检测图片列
        if self.auto_detect_images:
            self._detect_image_columns()

        # 图片缓存
        self._image_cache = {}
        self._temp_dir = tempfile.mkdtemp(prefix="sparrow_table_viewer_")

        # 上传文件缓存
        self._uploads_dir = Path(self._temp_dir) / "uploads"
        self._uploads_dir.mkdir(exist_ok=True)

        # 异步HTTP会话
        self._http_session = None
        
        # 反爬虫User-Agent池
        self._user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"
        ]

        # 注册路由
        self._setup_routes()

    async def _get_http_session(self):
        """获取或创建HTTP会话"""
        if self._http_session is None or self._http_session.closed:
            # 创建连接器，优化性能
            connector = aiohttp.TCPConnector(
                limit=100,  # 总连接池大小
                limit_per_host=20,  # 每个主机的连接数
                ttl_dns_cache=300,  # DNS缓存时间
                use_dns_cache=True,
            )
            
            # 创建超时配置
            timeout = aiohttp.ClientTimeout(
                total=30,  # 总超时时间
                connect=10,  # 连接超时
                sock_read=20,  # 读取超时
            )
            
            self._http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Cache-Control": "no-cache",
                    "Sec-Fetch-Dest": "image",
                    "Sec-Fetch-Mode": "no-cors",
                    "Sec-Fetch-Site": "cross-site",
                }
            )
        return self._http_session

    def _get_anti_bot_headers(self):
        """获取反爬虫请求头"""
        return {
            "User-Agent": random.choice(self._user_agents),
            "Referer": "https://www.google.com/",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors", 
            "Sec-Fetch-Site": "cross-site",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    async def _download_image_async(self, url: str, cache_path: Path, max_retries: int = 3) -> bool:
        """异步下载图片到缓存路径，包含重试机制"""
        session = await self._get_http_session()
        
        for attempt in range(max_retries):
            try:
                # 随机延迟，避免被反爬虫检测
                if attempt > 0:
                    delay = (2 ** attempt) + random.uniform(0.1, 0.5)  # 指数退避 + 随机抖动
                    await asyncio.sleep(delay)
                
                # 获取反爬虫请求头
                headers = self._get_anti_bot_headers()
                
                async with session.get(url, headers=headers) as response:
                    # 检查响应状态
                    if response.status == 200:
                        # 异步写入文件
                        async with aiofiles.open(cache_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        return True
                    elif response.status == 403:
                        # 403错误，可能是反爬虫，增加延迟
                        print(f"图片下载被拒绝 (403): {url}, 尝试 {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(random.uniform(1.0, 3.0))
                            continue
                    elif response.status == 429:
                        # 429限流，增加更长延迟
                        print(f"请求过于频繁 (429): {url}, 尝试 {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(random.uniform(3.0, 8.0))
                            continue
                    else:
                        print(f"图片下载失败，状态码 {response.status}: {url}")
                        if attempt < max_retries - 1:
                            continue
                
            except asyncio.TimeoutError:
                print(f"图片下载超时: {url}, 尝试 {attempt + 1}/{max_retries}")
            except aiohttp.ClientError as e:
                print(f"网络错误: {url}, {e}, 尝试 {attempt + 1}/{max_retries}")
            except Exception as e:
                print(f"图片下载异常: {url}, {e}, 尝试 {attempt + 1}/{max_retries}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return False

    def _reload_data(self, new_file_path: Path):
        """重新加载新的数据文件"""
        self.file_path = new_file_path
        self.df = self._load_data_from_path(new_file_path)
        self.original_df = self.df.copy()

        # 重新检测图片列
        self.image_columns = []
        if self.auto_detect_images:
            self._detect_image_columns()

    def _load_data(self) -> pd.DataFrame:
        """加载当前文件路径的数据"""
        return self._load_data_from_path(self.file_path)

    def _load_data_from_path(self, file_path: Path) -> pd.DataFrame:
        """加载指定路径的表格数据"""
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_extension = file_path.suffix.lower()

        if file_extension == ".csv":
            try:
                # 尝试不同编码
                for encoding in ["utf-8", "gbk", "gb2312", "latin1"]:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        print(f"成功使用 {encoding} 编码加载CSV文件")
                        return df
                    except UnicodeDecodeError:
                        continue
                raise ValueError("无法确定CSV文件编码")
            except Exception as e:
                raise ValueError(f"加载CSV文件失败: {e}")

        elif file_extension in [".xlsx", ".xls"]:
            try:
                df = pd.read_excel(file_path, sheet_name=self.sheet_name)
                return df
            except Exception as e:
                raise ValueError(f"加载Excel文件失败: {e}")
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")

    def _detect_image_columns(self):
        """自动检测包含图片URL的列"""
        for column in self.df.columns:
            # 检查前10行的数据
            sample_data = self.df[column].dropna().head(10)
            image_count = 0

            for value in sample_data:
                if isinstance(value, str):
                    # 使用split_image_paths检测图片路径
                    image_paths = split_image_paths(value)
                    if image_paths:
                        image_count += 1

            # 如果超过50%的样本包含图片URL，则认为是图片列
            if image_count / len(sample_data) > 0.5 if len(sample_data) > 0 else False:
                if column not in self.image_columns:
                    self.image_columns.append(column)
                    print(f"自动检测到图片列: {column}")

    def _setup_routes(self):
        """设置API路由"""

        @self.app.get("/", response_class=HTMLResponse)
        async def get_index():
            """主页面"""
            return self._get_html_template()

        @self.app.get("/api/table/info")
        async def get_table_info():
            """获取表格基本信息"""
            return {
                "total_rows": len(self.original_df),
                "total_columns": len(self.original_df.columns),
                "columns": list(self.original_df.columns),
                "image_columns": self.image_columns,
                "file_path": str(self.file_path),
                "dtypes": {
                    col: str(dtype) for col, dtype in self.original_df.dtypes.items()
                },
            }

        @self.app.get("/api/table/data")
        async def get_table_data(
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=10, le=1000),
            sort_by: Optional[str] = None,
            sort_order: str = Query("asc", regex="^(asc|desc)$"),
            filters: Optional[str] = None,
            visible_columns: Optional[str] = None,
        ):
            """获取表格数据（分页）"""
            df = self.df.copy()

            # 应用行筛选
            if filters:
                try:
                    filter_configs = json.loads(filters)
                    df = self._apply_filters(df, filter_configs)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"筛选参数错误: {e}")

            # 应用列筛选
            display_columns = list(df.columns)
            if visible_columns:
                try:
                    visible_cols = json.loads(visible_columns)
                    if visible_cols and isinstance(visible_cols, list):
                        # 确保列存在
                        display_columns = [
                            col for col in visible_cols if col in df.columns
                        ]
                        if display_columns:
                            df = df[display_columns]
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"列筛选参数错误: {e}")

            # 排序
            if sort_by and sort_by in df.columns:
                ascending = sort_order == "asc"
                df = df.sort_values(by=sort_by, ascending=ascending)

            # 分页
            total_rows = len(df)
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            page_data = df.iloc[start_idx:end_idx]

            # 转换为前端格式
            data = []
            for idx, row in page_data.iterrows():
                row_data = {"_index": idx}
                for col in df.columns:
                    value = row[col]
                    # 处理NaN值
                    if pd.isna(value):
                        row_data[col] = None
                    else:
                        # 如果是图像列，预处理切分图像路径
                        if col in self.image_columns and isinstance(value, str):
                            image_paths = split_image_paths(value)
                            row_data[col] = {
                                "original": value,  # 保留原始字符串
                                "paths": image_paths  # 切分后的路径数组
                            }
                        else:
                            row_data[col] = value
                data.append(row_data)

            return {
                "data": data,
                "total": total_rows,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_rows + page_size - 1) // page_size,
                "visible_columns": display_columns,
            }

        @self.app.put("/api/table/cell/{row_index}/{column}")
        async def update_cell(row_index: int, column: str, request: Request):
            """更新单元格数据"""
            if column not in self.df.columns:
                raise HTTPException(status_code=404, detail="列不存在")

            if row_index < 0 or row_index >= len(self.df):
                raise HTTPException(status_code=404, detail="行索引超出范围")

            body = await request.json()
            new_value = body.get("value")

            # 更新数据
            try:
                self.df.at[row_index, column] = new_value
                return {"success": True, "message": "更新成功"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"更新失败: {e}")

        @self.app.post("/api/table/save")
        async def save_table():
            """保存表格到原文件"""
            try:
                if self.file_path.suffix.lower() == ".csv":
                    self.df.to_csv(self.file_path, index=False, encoding="utf-8")
                else:
                    self.df.to_excel(
                        self.file_path, index=False, sheet_name=self.sheet_name
                    )
                return {"success": True, "message": "保存成功"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"保存失败: {e}")

        @self.app.post("/api/table/reset")
        async def reset_table():
            """重置表格到原始状态"""
            self.df = self.original_df.copy()
            return {"success": True, "message": "重置成功"}

        @self.app.get("/api/image/proxy")
        async def image_proxy(url: str):
            """图片代理服务（解决跨域问题）"""
            if not url:
                raise HTTPException(status_code=400, detail="URL参数缺失")

            # 检查缓存
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_path = Path(self._temp_dir) / f"{url_hash}"

            if cache_path.exists():
                return FileResponse(cache_path)

            try:
                # 判断是本地文件还是网络URL
                if url.startswith(("http://", "https://")):
                    # 异步下载网络图片
                    success = await self._download_image_async(url, cache_path)
                    if success:
                        return FileResponse(cache_path)
                    else:
                        raise HTTPException(status_code=500, detail="图片下载失败")
                else:
                    # 本地文件
                    try:
                        # 规范化路径，处理各种路径格式
                        local_path = Path(url).resolve()
                        
                        # 检查文件是否存在
                        if local_path.exists() and local_path.is_file():
                            # 检查是否为图像文件
                            if local_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                                return FileResponse(local_path)
                            else:
                                raise HTTPException(status_code=400, detail=f"不支持的图像格式: {local_path.suffix}")
                        else:
                            # 提供更详细的错误信息
                            if not local_path.exists():
                                raise HTTPException(status_code=404, detail=f"文件不存在: {local_path}")
                            else:
                                raise HTTPException(status_code=400, detail=f"不是文件: {local_path}")
                    except Exception as e:
                        if isinstance(e, HTTPException):
                            raise
                        raise HTTPException(status_code=500, detail=f"处理本地文件时出错: {str(e)}")

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"加载图片失败: {e}")

        @self.app.post("/api/table/upload")
        async def upload_file(file: UploadFile = File(...)):
            """上传新的表格文件"""
            try:
                # 验证文件格式
                if not file.filename:
                    raise HTTPException(status_code=400, detail="未提供文件名")

                file_extension = Path(file.filename).suffix.lower()
                if file_extension not in [".csv", ".xlsx", ".xls"]:
                    raise HTTPException(
                        status_code=400, detail=f"不支持的文件格式: {file_extension}"
                    )

                # 保存上传的文件
                upload_path = self._uploads_dir / file.filename
                with open(upload_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                # 重新加载数据
                self._reload_data(upload_path)

                return {
                    "success": True,
                    "message": "文件上传成功",
                    "filename": file.filename,
                    "total_rows": len(self.df),
                    "total_columns": len(self.df.columns),
                    "columns": list(self.df.columns),
                    "image_columns": self.image_columns,
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    def _apply_filters(
        self, df: pd.DataFrame, filter_configs: List[Dict]
    ) -> pd.DataFrame:
        """应用筛选条件"""
        for filter_config in filter_configs:
            column = filter_config.get("column")
            operator = filter_config.get("operator", "contains")
            value = filter_config.get("value", "")

            if not column or column not in df.columns:
                continue

            if operator == "contains":
                mask = (
                    df[column]
                    .astype(str)
                    .str.contains(str(value), case=False, na=False)
                )
            elif operator == "eq":
                mask = df[column] == value
            elif operator == "ne":
                mask = df[column] != value
            elif operator == "startswith":
                mask = df[column].astype(str).str.startswith(str(value), na=False)
            elif operator == "endswith":
                mask = df[column].astype(str).str.endswith(str(value), na=False)
            elif operator == "gt":
                mask = pd.to_numeric(df[column], errors="coerce") > float(value)
            elif operator == "lt":
                mask = pd.to_numeric(df[column], errors="coerce") < float(value)
            elif operator == "ge":
                mask = pd.to_numeric(df[column], errors="coerce") >= float(value)
            elif operator == "le":
                mask = pd.to_numeric(df[column], errors="coerce") <= float(value)
            else:
                continue

            df = df[mask]

        return df

    def _get_html_template(self) -> str:
        """获取HTML模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sparrow Table Viewer</title>
    <script src="/static/vue.global.js"></script>
    <script src="/static/element-plus.js"></script>
    <script src="/static/element-plus-icons.js"></script>
    <link rel="stylesheet" href="/static/element-plus.css" />
    <style>
        :root {
            --image-width: 120px;
            --image-height: 90px;
        }
        
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .main-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: #fff;
            border-bottom: 1px solid #e6e6e6;
            padding: 16px 24px;
            display: flex;
            justify-content: between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .toolbar {
            background: #f5f5f5;
            padding: 12px 24px;
            border-bottom: 1px solid #e6e6e6;
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .table-container {
            flex: 1;
            overflow: auto;
            padding: 24px;
            background: #fff;
        }
        
        .image-preview {
            max-width: 200px;
            max-height: 150px;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .image-preview:hover {
            transform: scale(1.1);
        }
        
        .multi-images-container {
            display: flex;
            gap: 8px;
            align-items: center;
            overflow-x: auto;
            max-width: 100%;
            padding: 4px 0;
        }
        
        .multi-images-container::-webkit-scrollbar {
            height: 4px;
        }
        
        .multi-images-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 2px;
        }
        
        .multi-images-container::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 2px;
        }
        
        .multi-images-container::-webkit-scrollbar-thumb:hover {
            background: #a1a1a1;
        }
        
        .multi-image-item {
            flex-shrink: 0;
            max-width: var(--image-width);
            max-height: var(--image-height);
            width: var(--image-width);
            height: var(--image-height);
            object-fit: cover;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .multi-image-item:hover {
            transform: scale(1.05);
        }
        
        .image-placeholder {
            flex-shrink: 0;
            width: var(--image-width);
            height: var(--image-height);
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            border: 2px dashed #ddd;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 12px;
            position: relative;
            overflow: hidden;
        }
        
        .image-placeholder::before {
            content: '📷';
            font-size: 24px;
            margin-bottom: 4px;
            opacity: 0.6;
        }
        
        .image-placeholder.loading {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-color: #bae6fd;
            color: #0369a1;
        }
        
        .image-placeholder.loading::before {
            content: '⏳';
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        .image-placeholder.error {
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border-color: #fca5a5;
            color: #dc2626;
        }
        
        .image-placeholder.error::before {
            content: '❌';
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.6; }
            50% { transform: scale(1.1); opacity: 1; }
        }
        
        .loading-shimmer {
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .filter-row {
            background: #fafafa;
            padding: 12px 16px;
            border-bottom: 1px solid #e6e6e6;
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .stats-info {
            background: #e8f4fd;
            padding: 8px 16px;
            border-left: 4px solid #409eff;
            margin-bottom: 16px;
            border-radius: 4px;
        }
        
        .el-table .el-table__cell {
            padding: 8px 12px;
        }
        
        .cell-editor {
            width: 100%;
            border: none;
            background: transparent;
            outline: none;
            padding: 4px;
        }
        
        .cell-editor:focus {
            background: #fff;
            border: 1px solid #409eff;
            border-radius: 3px;
        }
        
        /* 表头按钮样式优化 */
        .el-table th.el-table__cell {
            padding: 8px 12px;
        }
        
        .el-button-group .el-button {
            margin: 0;
        }
        
        .el-table .el-table__header-wrapper .el-button {
            border: 1px solid #dcdfe6;
        }
        
        .el-table .el-table__header-wrapper .el-button:hover {
            background: #f5f7fa;
            border-color: #c0c4cc;
        }
        
        .el-table .el-table__header-wrapper .el-button--primary {
            background: #409eff;
            border-color: #409eff;
            color: #fff;
        }
        
        /* 拖拽上传区域样式 */
        .upload-area {
            border: 2px dashed #d9d9d9;
            border-radius: 8px;
            background: #fafafa;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .upload-area:hover, .upload-area.dragover {
            border-color: #409eff;
            background: #f0f9ff;
        }
        
        .upload-area.dragover {
            border-color: #67c23a;
            background: #f0f9f0;
        }
        
        .upload-icon {
            font-size: 48px;
            color: #c0c4cc;
            margin-bottom: 16px;
        }
        
        .upload-text {
            color: #606266;
            font-size: 16px;
            line-height: 1.6;
        }
        
        .upload-hint {
            color: #909399;
            font-size: 12px;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="main-container">
            <!-- 头部 -->
            <div class="header">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <h1 style="margin: 0; font-size: 20px; color: #303133;">
                        📊 Sparrow Table Viewer
                    </h1>
                    <el-tag v-if="tableInfo" type="info">{{ tableInfo.file_path }}</el-tag>
                </div>
                <div style="display: flex; gap: 12px;">
                    <el-button @click="showUploadDialog = true" type="success" size="small">
                        上传文件
                    </el-button>
                    <el-button @click="resetTable" type="warning" size="small">
                        重置
                    </el-button>
                    <el-button @click="saveTable" type="primary" size="small">
                        保存
                    </el-button>
                </div>
            </div>
            
            <!-- 内容区域 -->
            <div class="content">
                <!-- 工具栏 -->
                <div class="toolbar">
                    <el-button @click="refreshData" size="small" :loading="loading">
                        刷新数据
                    </el-button>
                    
                    <el-divider direction="vertical"></el-divider>
                    
                    <span style="color: #606266; font-size: 14px;">每页显示:</span>
                    <el-select v-model="pagination.pageSize" @change="loadTableData" size="small" style="width: 100px;">
                        <el-option :value="50" label="50"></el-option>
                        <el-option :value="100" label="100"></el-option>
                        <el-option :value="200" label="200"></el-option>
                        <el-option :value="500" label="500"></el-option>
                    </el-select>
                    
                    <el-divider direction="vertical"></el-divider>
                    
                    <el-button @click="showFilterDialog = true" size="small" type="info">
                        行筛选 ({{ activeFilters.length }})
                    </el-button>
                    
                    <el-button @click="clearFilters" size="small" v-if="activeFilters.length > 0">
                        清除行筛选
                    </el-button>
                    
                    <el-divider direction="vertical"></el-divider>
                    
                    <el-button @click="showColumnDialog = true" size="small" type="success">
                        列显示 ({{ visibleColumns.length }}/{{ allColumns.length }})
                    </el-button>
                    
                    <el-button @click="resetColumns" size="small" v-if="visibleColumns.length < allColumns.length">
                        显示全部列
                    </el-button>
                    
                    <el-divider direction="vertical" v-if="tableInfo && tableInfo.image_columns && tableInfo.image_columns.length"></el-divider>
                    
                    <!-- 图像设置 -->
                    <div v-if="tableInfo && tableInfo.image_columns && tableInfo.image_columns.length" style="display: flex; align-items: center; gap: 16px;">
                        <!-- 图像尺寸设置 -->
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #606266; font-size: 14px;">图像尺寸:</span>
                            <el-select v-model="imageSize" @change="onImageSizeChange" size="small" style="width: 140px;">
                                <el-option value="small" label="小 (80x60)"></el-option>
                                <el-option value="medium" label="中 (120x90)"></el-option>
                                <el-option value="large" label="大 (160x120)"></el-option>
                                <el-option value="xlarge" label="超大 (200x150)"></el-option>
                                <el-option value="xxlarge" label="最大 (400x300)"></el-option>
                            </el-select>
                        </div>
                        
                        <!-- 分隔符设置 -->
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #606266; font-size: 14px;">分隔符:</span>
                            <el-select v-model="imageSeparator" @change="onSeparatorChange" size="small" style="width: 120px;">
                                <el-option value="auto" label="自动检测"></el-option>
                                <el-option value="comma" label="逗号 ,"></el-option>
                                <el-option value="semicolon" label="分号 ;"></el-option>
                                <el-option value="newline" label="换行符"></el-option>
                                <el-option value="custom" label="自定义"></el-option>
                            </el-select>
                            
                            <!-- 自定义分隔符输入 -->
                            <el-input 
                                v-if="imageSeparator === 'custom'"
                                v-model="customSeparator"
                                @change="onSeparatorChange"
                                placeholder="输入分隔符"
                                size="small"
                                style="width: 100px;"
                            ></el-input>
                        </div>
                    </div>
                </div>
                
                <!-- 统计信息 -->
                <div class="stats-info" v-if="tableInfo">
                    <span style="margin-right: 24px;">
                        <strong>总行数:</strong> {{ tableData.total || 0 }} 行
                    </span>
                    <span style="margin-right: 24px;">
                        <strong>显示列数:</strong> {{ visibleColumns.length }}/{{ allColumns.length }} 列
                    </span>
                    <span v-if="tableInfo.image_columns && tableInfo.image_columns.length">
                        <strong>图片列:</strong> {{ tableInfo.image_columns.join(', ') }}
                    </span>
                </div>
                
                <!-- 表格容器 -->
                <div class="table-container">
                    <el-table 
                        :data="tableData.data" 
                        stripe
                        border
                        :loading="loading"
                        style="width: 100%;"
                        max-height="calc(100vh - 320px)"
                        size="small"
                    >
                        <el-table-column 
                            v-for="column in tableColumns" 
                            :key="column"
                            :prop="column"
                            :label="column"
                            :width="getColumnWidth(column)"
                            :sortable="false"
                            show-overflow-tooltip
                        >
                            <template #header="{ column: headerColumn }">
                                <div style="display: flex; align-items: center; gap: 8px; justify-content: space-between; width: 100%;">
                                    <span style="flex: 1;">{{ headerColumn.label }}</span>
                                    <div style="display: flex; align-items: center; gap: 4px;">
                                        <!-- 排序按钮 -->
                                        <el-button-group size="small">
                                            <el-button 
                                                @click.stop="handleSort(headerColumn.label, 'asc')"
                                                :type="sortConfig.prop === headerColumn.label && sortConfig.order === 'ascending' ? 'primary' : ''"
                                                size="small"
                                                style="padding: 2px 4px; font-size: 10px;"
                                                title="升序"
                                            >
                                                ↑
                                            </el-button>
                                            <el-button 
                                                @click.stop="handleSort(headerColumn.label, 'desc')"
                                                :type="sortConfig.prop === headerColumn.label && sortConfig.order === 'descending' ? 'primary' : ''"
                                                size="small"
                                                style="padding: 2px 4px; font-size: 10px;"
                                                title="降序"
                                            >
                                                ↓
                                            </el-button>
                                        </el-button-group>
                                        
                                        <!-- 筛选按钮 -->
                                        <el-button 
                                            @click.stop="addColumnFilter(headerColumn.label)"
                                            size="small"
                                            type="text"
                                            style="padding: 2px 4px; font-size: 10px;"
                                            title="筛选"
                                        >
                                            🔍
                                        </el-button>
                                    </div>
                                </div>
                            </template>
                            
                            <template #default="scope">
                                <div v-if="isImageColumn(column)">
                                    <div v-if="scope.row[column] && scope.row[column].paths && scope.row[column].paths.length > 0" class="multi-images-container">
                                        <template v-for="(imagePath, index) in scope.row[column].paths" :key="index">
                                            <!-- 图像加载成功时显示图片 -->
                                            <img 
                                                v-if="isImageLoaded(imagePath)"
                                                :src="`/api/image/proxy?url=${encodeURIComponent(imagePath)}`"
                                                :alt="imagePath"
                                                class="multi-image-item"
                                                @click="showImageDialog(imagePath, scope.row[column].original, index)"
                                            />
                                            <!-- 图像未加载成功时显示原始URL字符串 -->
                                            <div 
                                                v-else
                                                style="color: #666; font-size: 12px; word-break: break-all; line-height: 1.4; cursor: pointer; margin-right: 8px; padding: 4px;"
                                                @click="showImageDialog(imagePath, scope.row[column].original, index)"
                                            >
                                                {{ imagePath }}
                                            </div>
                                            <!-- 隐藏的图片元素用于检测加载状态 -->
                                            <img 
                                                v-if="!isImageLoaded(imagePath)"
                                                :src="`/api/image/proxy?url=${encodeURIComponent(imagePath)}`"
                                                style="display: none;"
                                                @load="onImageLoadSuccess(imagePath)"
                                                @error="onImageLoadError(imagePath)"
                                            />
                                        </template>
                                    </div>
                                    <div v-else style="color: #666; font-size: 12px; word-break: break-all; line-height: 1.4; padding: 4px;">
                                        {{ scope.row[column] && scope.row[column].original ? scope.row[column].original : (scope.row[column] || '') }}
                                    </div>
                                </div>
                                <div v-else>
                                    <input 
                                        v-if="editingCell && editingCell.row === scope.$index && editingCell.column === column"
                                        v-model="editingValue"
                                        @blur="saveCell(scope._index, column)"
                                        @keyup.enter="saveCell(scope._index, column)"
                                        @keyup.escape="cancelEdit"
                                        class="cell-editor"
                                        ref="cellInput"
                                    />
                                    <span 
                                        v-else
                                        @dblclick="startEdit(scope.$index, column, scope.row[column])"
                                        style="cursor: pointer; display: block; min-height: 20px;"
                                    >
                                        {{ scope.row[column] || '' }}
                                    </span>
                                </div>
                            </template>
                        </el-table-column>
                    </el-table>
                    
                    <!-- 分页 -->
                    <div style="margin-top: 20px; display: flex; justify-content: center;">
                        <el-pagination
                            v-model:current-page="pagination.currentPage"
                            v-model:page-size="pagination.pageSize"
                            :page-sizes="[50, 100, 200, 500]"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="tableData.total"
                            @size-change="handleSizeChange"
                            @current-change="handleCurrentChange"
                        />
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 筛选对话框 -->
        <el-dialog v-model="showFilterDialog" title="高级筛选" width="600px">
            <div v-for="(filter, index) in filterConfigs" :key="index" style="margin-bottom: 16px;">
                <el-row :gutter="12">
                    <el-col :span="6">
                        <el-select v-model="filter.column" placeholder="选择列">
                            <el-option v-for="col in tableColumns" :key="col" :value="col" :label="col"></el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="6">
                        <el-select v-model="filter.operator" placeholder="操作符">
                            <el-option value="contains" label="包含"></el-option>
                            <el-option value="eq" label="等于"></el-option>
                            <el-option value="ne" label="不等于"></el-option>
                            <el-option value="startswith" label="开头是"></el-option>
                            <el-option value="endswith" label="结尾是"></el-option>
                            <el-option value="gt" label="大于"></el-option>
                            <el-option value="lt" label="小于"></el-option>
                            <el-option value="ge" label="大于等于"></el-option>
                            <el-option value="le" label="小于等于"></el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="8">
                        <el-input v-model="filter.value" placeholder="筛选值"></el-input>
                    </el-col>
                    <el-col :span="4">
                        <el-button @click="removeFilter(index)" type="danger" size="small">删除</el-button>
                    </el-col>
                </el-row>
            </div>
            
            <el-button @click="addFilter" type="primary" size="small">添加筛选条件</el-button>
            
            <template #footer>
                <el-button @click="showFilterDialog = false">取消</el-button>
                <el-button @click="applyFilters" type="primary">应用筛选</el-button>
            </template>
        </el-dialog>
        
        <!-- 列显示管理对话框 -->
        <el-dialog v-model="showColumnDialog" title="列显示管理" width="500px">
            <div style="margin-bottom: 16px;">
                <el-button @click="selectAllColumns" size="small" type="primary">全选</el-button>
                <el-button @click="selectNoColumns" size="small">全不选</el-button>
                <span style="margin-left: 16px; color: #666;">
                    已选择 {{ visibleColumns.length }} / {{ allColumns.length }} 列
                </span>
            </div>
            
            <div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 12px; border-radius: 4px;">
                <el-row :gutter="12">
                    <el-col :span="12" v-for="column in allColumns" :key="column" style="margin-bottom: 8px;">
                        <el-checkbox 
                            :model-value="visibleColumns.includes(column)"
                            @change="toggleColumn(column)"
                            style="width: 100%;"
                        >
                            <span :style="{ fontWeight: tableInfo && tableInfo.image_columns && tableInfo.image_columns.includes(column) ? 'bold' : 'normal', color: tableInfo && tableInfo.image_columns && tableInfo.image_columns.includes(column) ? '#409eff' : '' }">
                                {{ column }}
                                <el-tag v-if="tableInfo && tableInfo.image_columns && tableInfo.image_columns.includes(column)" size="small" type="primary">图片</el-tag>
                            </span>
                        </el-checkbox>
                    </el-col>
                </el-row>
            </div>
            
            <template #footer>
                <el-button @click="showColumnDialog = false">取消</el-button>
                <el-button @click="resetColumns" type="warning">重置</el-button>
                <el-button @click="applyColumnFilter" type="primary" :disabled="visibleColumns.length === 0">应用</el-button>
            </template>
        </el-dialog>
        
        <!-- 图片查看对话框 -->
        <el-dialog v-model="showImagePreview" :title="`${currentImageIndex + 1}/${currentImageList.length} - ${currentImageUrl}`" width="90%">
            <div style="position: relative; text-align: center;">
                <!-- 左箭头按钮 -->
                <el-button 
                    v-if="currentImageList.length > 1 && currentImageIndex > 0"
                    @click="showPreviousImage"
                    type="primary"
                    size="large"
                    circle
                    style="position: absolute; left: 20px; top: 50%; transform: translateY(-50%); z-index: 10;"
                >
                    ←
                </el-button>
                
                <!-- 图片 -->
                <img 
                    :src="`/api/image/proxy?url=${encodeURIComponent(currentImageUrl)}`"
                    style="max-width: 100%; max-height: 100vh; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"
                    @error="handleImageError"
                />
                
                <!-- 右箭头按钮 -->
                <el-button 
                    v-if="currentImageList.length > 1 && currentImageIndex < currentImageList.length - 1"
                    @click="showNextImage"
                    type="primary"
                    size="large"
                    circle
                    style="position: absolute; right: 20px; top: 50%; transform: translateY(-50%); z-index: 10;"
                >
                    →
                </el-button>
            </div>
        </el-dialog>

        <!-- 文件上传对话框 -->
        <el-dialog v-model="showUploadDialog" title="上传表格文件" width="600px">
            <div class="upload-area" 
                 @click="triggerFileInput"
                 @drop="handleFileDrop" 
                 @dragover="handleDragOver" 
                 @dragleave="handleDragLeave"
                 :class="{ 'dragover': isDragOver }">
                <div class="upload-icon">📁</div>
                <div class="upload-text">
                    <div>点击选择文件或拖拽文件到此处</div>
                    <div class="upload-hint">支持 .xlsx, .xls, .csv 格式</div>
                </div>
            </div>
            
            <input type="file" 
                   ref="fileInput" 
                   @change="handleFileSelect" 
                   accept=".xlsx,.xls,.csv"
                   style="display: none;">
            
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="showUploadDialog = false">取消</el-button>
                </span>
            </template>
        </el-dialog>
    </div>

    <script>
        const { createApp } = Vue;
        const { ElMessage, ElMessageBox } = ElementPlus;

        createApp({
            data() {
                return {
                    loading: false,
                    tableInfo: null,
                    tableData: {
                        data: [],
                        total: 0,
                        page: 1,
                        page_size: 100,
                        total_pages: 0
                    },
                    pagination: {
                        currentPage: 1,
                        pageSize: 100
                    },
                    sortConfig: {
                        prop: null,
                        order: null
                    },
                    activeFilters: [],
                    showFilterDialog: false,
                    filterConfigs: [],
                    
                    // 列显示控制
                    showColumnDialog: false,
                    visibleColumns: [],
                    allColumns: [],
                    
                    // 编辑相关
                    editingCell: null,
                    editingValue: '',
                    
                    // 图片预览
                    showImagePreview: false,
                    currentImageUrl: '',
                    currentImageList: [], // 当前行的所有图片列表
                    currentImageIndex: 0, // 当前显示的图片索引
                    
                    // 文件上传
                    showUploadDialog: false,
                    isDragOver: false,
                    
                    // 图像尺寸设置
                    imageSize: 'medium', // small, medium, large, xlarge
                    
                    // 图像分隔符设置
                    imageSeparator: 'auto', // auto, comma, semicolon, newline, custom
                    customSeparator: '', // 自定义分隔符
                    
                    // 图像加载状态管理
                    loadedImages: new Set() // 存储已成功加载的图像URL
                };
            },
            
            computed: {
                tableColumns() {
                    // 如果有列筛选，使用筛选后的列，否则使用全部列
                    if (this.visibleColumns.length > 0) {
                        return this.visibleColumns;
                    }
                    return this.tableInfo ? this.tableInfo.columns : [];
                },
                
                // 计算当前图像尺寸
                currentImageSizes() {
                    const sizeMap = {
                        'small': { width: 80, height: 60 },
                        'medium': { width: 120, height: 90 },
                        'large': { width: 160, height: 120 },
                        'xlarge': { width: 200, height: 150 },
                        'xxlarge': { width: 400, height: 300 }
                    };
                    return sizeMap[this.imageSize] || sizeMap.medium;
                }
            },
            
            async mounted() {
                // 加载保存的设置
                this.loadImageSizeFromStorage();
                this.loadSeparatorFromStorage();
                
                // 初始化CSS变量
                this.updateImageSizeCss();
                
                await this.loadTableInfo();
                await this.loadTableData();
            },
            
            methods: {
                // 加载表格信息
                async loadTableInfo() {
                    try {
                        const response = await fetch('/api/table/info');
                        this.tableInfo = await response.json();
                        // 初始化列数据
                        if (this.tableInfo && this.tableInfo.columns) {
                            this.allColumns = [...this.tableInfo.columns];
                            if (this.visibleColumns.length === 0) {
                                this.visibleColumns = [...this.tableInfo.columns];
                            }
                        }
                    } catch (error) {
                        ElMessage.error('加载表格信息失败: ' + error.message);
                    }
                },
                
                // 加载表格数据
                async loadTableData() {
                    this.loading = true;
                    try {
                        const params = new URLSearchParams({
                            page: this.pagination.currentPage,
                            page_size: this.pagination.pageSize
                        });
                        
                        if (this.sortConfig.prop) {
                            params.append('sort_by', this.sortConfig.prop);
                            params.append('sort_order', this.sortConfig.order === 'ascending' ? 'asc' : 'desc');
                        }
                        
                        if (this.activeFilters.length > 0) {
                            params.append('filters', JSON.stringify(this.activeFilters));
                        }
                        
                        // 添加列筛选参数
                        if (this.visibleColumns.length > 0 && this.visibleColumns.length < this.allColumns.length) {
                            params.append('visible_columns', JSON.stringify(this.visibleColumns));
                        }
                        
                        const response = await fetch(`/api/table/data?${params}`);
                        this.tableData = await response.json();
                        
                        // 更新可见列（如果后端返回了）
                        if (this.tableData.visible_columns) {
                            this.visibleColumns = this.tableData.visible_columns;
                        }
                    } catch (error) {
                        ElMessage.error('加载数据失败: ' + error.message);
                    } finally {
                        this.loading = false;
                    }
                },
                
                // 刷新数据
                async refreshData() {
                    await this.loadTableInfo();
                    await this.loadTableData();
                    ElMessage.success('数据已刷新');
                },
                
                // 排序处理
                handleSort(column, direction) {
                    if (this.sortConfig.prop === column && 
                        this.sortConfig.order === (direction === 'asc' ? 'ascending' : 'descending')) {
                        // 如果点击的是当前排序列和方向，则清除排序
                        this.sortConfig = { prop: null, order: null };
                    } else {
                        // 设置新的排序
                        this.sortConfig = { 
                            prop: column, 
                            order: direction === 'asc' ? 'ascending' : 'descending' 
                        };
                    }
                    this.pagination.currentPage = 1;
                    this.loadTableData();
                },
                
                // 分页处理
                handleSizeChange(size) {
                    this.pagination.pageSize = size;
                    this.pagination.currentPage = 1;
                    this.loadTableData();
                },
                
                handleCurrentChange(page) {
                    this.pagination.currentPage = page;
                    this.loadTableData();
                },
                
                // 判断是否为图片列
                isImageColumn(column) {
                    return this.tableInfo && this.tableInfo.image_columns.includes(column);
                },
                
                // 获取列宽度
                getColumnWidth(column) {
                    if (this.isImageColumn(column)) {
                        // 根据图像尺寸动态调整列宽，预留3张图片的空间 + 边距
                        const imageWidth = this.currentImageSizes.width;
                        return Math.max(imageWidth * 3 + 40, 250); // 最小250px
                    }
                    return null;
                },
                
                
                // 检查图像是否已加载
                isImageLoaded(imageUrl) {
                    return this.loadedImages.has(imageUrl);
                },
                
                // 图像加载成功处理
                onImageLoadSuccess(imageUrl) {
                    this.loadedImages.add(imageUrl);
                    this.$forceUpdate(); // 强制更新视图
                },
                
                // 图像加载失败处理
                onImageLoadError(imageUrl) {
                    this.loadedImages.delete(imageUrl);
                },
                
                // 筛选相关
                addFilter() {
                    this.filterConfigs.push({
                        column: '',
                        operator: 'contains',
                        value: ''
                    });
                },
                
                removeFilter(index) {
                    this.filterConfigs.splice(index, 1);
                },
                
                addColumnFilter(column) {
                    this.filterConfigs.push({
                        column: column,
                        operator: 'contains',
                        value: ''
                    });
                    this.showFilterDialog = true;
                },
                
                applyFilters() {
                    this.activeFilters = this.filterConfigs.filter(f => f.column && f.value);
                    this.pagination.currentPage = 1;
                    this.showFilterDialog = false;
                    this.loadTableData();
                },
                
                clearFilters() {
                    this.activeFilters = [];
                    this.filterConfigs = [];
                    this.pagination.currentPage = 1;
                    this.loadTableData();
                },
                
                // 列管理相关
                applyColumnFilter() {
                    this.pagination.currentPage = 1;
                    this.showColumnDialog = false;
                    this.loadTableData();
                },
                
                resetColumns() {
                    this.visibleColumns = [...this.allColumns];
                    this.applyColumnFilter();
                },
                
                selectAllColumns() {
                    this.visibleColumns = [...this.allColumns];
                },
                
                selectNoColumns() {
                    this.visibleColumns = [];
                },
                
                toggleColumn(column) {
                    const index = this.visibleColumns.indexOf(column);
                    if (index > -1) {
                        this.visibleColumns.splice(index, 1);
                    } else {
                        this.visibleColumns.push(column);
                    }
                },
                
                // 编辑相关
                startEdit(row, column, value) {
                    if (this.isImageColumn(column)) return;
                    
                    this.editingCell = { row, column };
                    this.editingValue = value || '';
                    
                    this.$nextTick(() => {
                        const input = this.$refs.cellInput;
                        if (input && input[0]) {
                            input[0].focus();
                        }
                    });
                },
                
                async saveCell(rowIndex, column) {
                    try {
                        const response = await fetch(`/api/table/cell/${rowIndex}/${column}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ value: this.editingValue })
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            await this.loadTableData();
                            ElMessage.success('更新成功');
                        } else {
                            ElMessage.error('更新失败: ' + result.message);
                        }
                    } catch (error) {
                        ElMessage.error('更新失败: ' + error.message);
                    } finally {
                        this.editingCell = null;
                        this.editingValue = '';
                    }
                },
                
                cancelEdit() {
                    this.editingCell = null;
                    this.editingValue = '';
                },
                
                // 图片相关
                showImageDialog(imageUrl, allImagesData, clickedIndex) {
                    // 如果提供了完整的图片数据和索引，设置图片列表
                    if (allImagesData !== undefined && clickedIndex !== undefined) {
                        // allImagesData 现在是原始字符串，需要重新切分
                        // 使用简单的切分逻辑（兼容旧版本）
                        var paths = allImagesData.split(/[,;]+/);
                        var imagePaths = [];
                        for (var i = 0; i < paths.length; i++) {
                            var path = paths[i].trim();
                            if (path) imagePaths.push(path);
                        }
                        this.currentImageList = imagePaths;
                        this.currentImageIndex = clickedIndex;
                    } else {
                        // 兼容单图片模式
                        this.currentImageList = [imageUrl];
                        this.currentImageIndex = 0;
                    }
                    
                    this.currentImageUrl = imageUrl;
                    this.showImagePreview = true;
                },
                
                // 显示上一张图片
                showPreviousImage: function() {
                    if (this.currentImageIndex > 0) {
                        this.currentImageIndex--;
                        this.currentImageUrl = this.currentImageList[this.currentImageIndex];
                    }
                },
                
                // 显示下一张图片
                showNextImage: function() {
                    if (this.currentImageIndex < this.currentImageList.length - 1) {
                        this.currentImageIndex++;
                        this.currentImageUrl = this.currentImageList[this.currentImageIndex];
                    }
                },
                
                handleImageError(event) {
                    event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjEwMCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuWbvueJh+WKoOi9veWksei0pTwvdGV4dD48L3N2Zz4=';
                },
                
                // 表格操作
                async saveTable() {
                    try {
                        const response = await fetch('/api/table/save', { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.success) {
                            ElMessage.success('保存成功');
                        } else {
                            ElMessage.error('保存失败: ' + result.message);
                        }
                    } catch (error) {
                        ElMessage.error('保存失败: ' + error.message);
                    }
                },
                
                async resetTable() {
                    try {
                        await ElMessageBox.confirm('确定要重置表格到原始状态吗？这将丢失所有未保存的修改。', '确认重置', {
                            type: 'warning'
                        });
                        
                        const response = await fetch('/api/table/reset', { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.success) {
                            await this.loadTableData();
                            ElMessage.success('重置成功');
                        } else {
                            ElMessage.error('重置失败: ' + result.message);
                        }
                    } catch (error) {
                        if (error !== 'cancel') {
                            ElMessage.error('重置失败: ' + error.message);
                        }
                    }
                },
                
                // 图像尺寸相关
                onImageSizeChange() {
                    // 保存到本地存储
                    try {
                        localStorage.setItem('sparrow_table_viewer_image_size', this.imageSize);
                    } catch (e) {
                        // 忽略localStorage错误
                    }
                    
                    // 更新CSS变量
                    this.updateImageSizeCss();
                    
                    // 强制表格重新计算列宽
                    this.$nextTick(() => {
                        // 通过改变一个响应式属性触发表格重新渲染
                        const temp = this.tableData.data;
                        this.tableData.data = [];
                        this.$nextTick(() => {
                            this.tableData.data = temp;
                        });
                    });
                },
                
                updateImageSizeCss() {
                    const sizes = this.currentImageSizes;
                    const root = document.documentElement;
                    root.style.setProperty('--image-width', sizes.width + 'px');
                    root.style.setProperty('--image-height', sizes.height + 'px');
                },
                
                loadImageSizeFromStorage() {
                    try {
                        const saved = localStorage.getItem('sparrow_table_viewer_image_size');
                        if (saved && ['small', 'medium', 'large', 'xlarge', 'xxlarge'].includes(saved)) {
                            this.imageSize = saved;
                        }
                    } catch (e) {
                        // 忽略localStorage错误
                    }
                },
                
                // 分隔符相关方法
                onSeparatorChange() {
                    // 保存到本地存储
                    this.saveSeparatorToStorage();
                    
                    // 强制刷新图像显示
                    this.$nextTick(() => {
                        this.loadedImages.clear(); // 清空加载状态，重新加载图像
                        const temp = this.tableData.data;
                        this.tableData.data = [];
                        this.$nextTick(() => {
                            this.tableData.data = temp;
                        });
                    });
                },
                
                saveSeparatorToStorage() {
                    try {
                        localStorage.setItem('sparrow_table_viewer_separator', this.imageSeparator);
                        if (this.customSeparator) {
                            localStorage.setItem('sparrow_table_viewer_custom_separator', this.customSeparator);
                        }
                    } catch (e) {
                        // 忽略localStorage错误
                    }
                },
                
                loadSeparatorFromStorage() {
                    try {
                        const savedSeparator = localStorage.getItem('sparrow_table_viewer_separator');
                        if (savedSeparator && ['auto', 'comma', 'semicolon', 'newline', 'custom'].includes(savedSeparator)) {
                            this.imageSeparator = savedSeparator;
                        }
                        
                        const savedCustom = localStorage.getItem('sparrow_table_viewer_custom_separator');
                        if (savedCustom) {
                            this.customSeparator = savedCustom;
                        }
                    } catch (e) {
                        // 忽略localStorage错误
                    }
                },
                
                // 文件上传相关方法
                triggerFileInput() {
                    this.$refs.fileInput.click();
                },
                
                handleDragOver(event) {
                    event.preventDefault();
                    this.isDragOver = true;
                },
                
                handleDragLeave(event) {
                    event.preventDefault();
                    this.isDragOver = false;
                },
                
                async handleFileDrop(event) {
                    event.preventDefault();
                    this.isDragOver = false;
                    
                    const files = event.dataTransfer.files;
                    if (files.length > 0) {
                        await this.uploadFile(files[0]);
                    }
                },
                
                async handleFileSelect(event) {
                    const files = event.target.files;
                    if (files.length > 0) {
                        await this.uploadFile(files[0]);
                    }
                },
                
                async uploadFile(file) {
                    // 检查文件类型
                    const allowedTypes = ['.xlsx', '.xls', '.csv'];
                    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                    
                    if (!allowedTypes.includes(fileExtension)) {
                        ElMessage.error('不支持的文件格式，请选择 .xlsx, .xls 或 .csv 文件');
                        return;
                    }
                    
                    this.loading = true;
                    
                    try {
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const response = await fetch('/api/table/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            ElMessage.success('文件上传成功，正在加载数据...');
                            this.showUploadDialog = false;
                            
                            // 重新加载表格信息和数据
                            await this.loadTableInfo();
                            await this.loadTableData();
                        } else {
                            ElMessage.error('上传失败: ' + result.message);
                        }
                    } catch (error) {
                        ElMessage.error('上传失败: ' + error.message);
                    } finally {
                        this.loading = false;
                        // 清空文件输入
                        this.$refs.fileInput.value = '';
                    }
                }
            }
        }).use(ElementPlus).mount('#app');
    </script>
</body>
</html>
        """

    def run(self, auto_open: bool = True):
        """启动服务器"""
        print(f"启动表格查看器服务...")
        print(f"文件: {self.file_path}")
        print(f"地址: http://{self.host}:{self.port}")
        print(f"数据: {len(self.df)} 行 x {len(self.df.columns)} 列")
        if self.image_columns:
            print(f"图片列: {', '.join(self.image_columns)}")
            # 显示每个图像列的示例路径（用于调试）
            for col in self.image_columns:
                sample_value = self.df[col].dropna().iloc[0] if not self.df[col].dropna().empty else None
                if sample_value:
                    sample_paths = split_image_paths(str(sample_value))
                    print(f"  {col}: 示例路径 -> {sample_paths[:2]}{'...' if len(sample_paths) > 2 else ''}")
        else:
            print("未检测到图片列")
        print(f"提示: 双击单元格可编辑，Ctrl+C 停止服务")

        if auto_open:
            # 延迟打开浏览器
            def open_browser():
                import time

                time.sleep(1.5)
                webbrowser.open(f"http://{self.host}:{self.port}")

            import threading

            threading.Thread(target=open_browser, daemon=True).start()

        try:
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="warning",  # 减少日志输出
            )
        except KeyboardInterrupt:
            print("\n服务器已停止")
        finally:
            # 清理HTTP会话
            if self._http_session and not self._http_session.closed:
                asyncio.run(self._http_session.close())
            
            # 清理临时文件
            import shutil

            if Path(self._temp_dir).exists():
                shutil.rmtree(self._temp_dir, ignore_errors=True)


def start_table_viewer(
    file_path: str,
    port: int = 8080,
    host: str = "127.0.0.1",
    sheet_name: Union[str, int] = 0,
    image_columns: Optional[List[str]] = None,
    auto_detect_images: bool = True,
    auto_open: bool = True,
):
    """启动表格查看器的便捷函数"""
    server = TableViewerServer(
        file_path=file_path,
        port=port,
        host=host,
        sheet_name=sheet_name,
        image_columns=image_columns,
        auto_detect_images=auto_detect_images,
    )
    server.run(auto_open=auto_open)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python server.py <文件路径>")
        sys.exit(1)

    start_table_viewer(sys.argv[1])
