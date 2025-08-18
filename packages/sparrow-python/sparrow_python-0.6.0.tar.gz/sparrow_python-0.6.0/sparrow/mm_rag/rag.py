import os
import json
import asyncio
from typing import List, Dict, Union, Optional, Any
import base64
from io import BytesIO
from PIL import Image
import aiofiles
import openai
from .retriever import MultiModalRAG
from sparrow import messages_preprocess

class AsyncOpenAIMultiModalRAG:
    """基于OpenAI API的异步多模态RAG系统"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: str = "minicpm-v:latest",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """初始化异步OpenAI多模态RAG系统
        
        Args:
            persist_directory: ChromaDB持久化存储目录
            api_key: OpenAI API密钥，如果为None则从环境变量获取
            api_base: OpenAI API基础URL，如果为None则从环境变量获取
            model: 使用的OpenAI模型名称
            temperature: 生成文本的温度参数
            max_tokens: 生成文本的最大token数
        """
        
        # 初始化多模态检索器
        self.retriever = MultiModalRAG(persist_directory=persist_directory)
        
        # 设置OpenAI模型参数
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 创建异步客户端
        self.client = openai.AsyncOpenAI(api_key=api_key, base_url=api_base)
    
    async def add_text(self, texts: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None, 
                metadatas: Optional[Union[Dict, List[Dict]]] = None):
        """异步添加文本到知识库
        
        Args:
            texts: 文本内容或文本列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
        """
        await asyncio.to_thread(
            self.retriever.add_text,
            texts=texts,
            doc_ids=doc_ids,
            metadatas=metadatas
        )
    
    async def add_image(self, image_paths: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None,
                 metadatas: Optional[Union[Dict, List[Dict]]] = None):
        """异步添加图片到知识库
        
        Args:
            image_paths: 图片路径或路径列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
        """
        await asyncio.to_thread(
            self.retriever.add_image,
            image_paths=image_paths,
            doc_ids=doc_ids,
            metadatas=metadatas
        )
    
    async def _encode_image_to_base64(self, image_path: str) -> str:
        """异步将图片编码为base64字符串
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: base64编码的图片
        """
        async with aiofiles.open(image_path, "rb") as image_file:
            image_data = await image_file.read()
            return base64.b64encode(image_data).decode('utf-8')
    
    async def _prepare_messages_with_context(self, query: str, context: List[Dict], system_prompt: Optional[str] = None) -> List[Dict]:
        """准备带有上下文的消息列表
        
        Args:
            query: 用户查询
            context: 检索到的上下文
            system_prompt: 系统提示，如果为None则使用默认提示
            
        Returns:
            List[Dict]: 消息列表
        """
        if system_prompt is None:
            system_prompt = """你是一个智能助手，基于提供的上下文信息回答用户的问题。
如果上下文中没有足够的信息来回答问题，请诚实地告知用户你不知道，不要编造信息。
如果问题与上下文无关，请基于你的知识回答。"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 构建上下文提示
        context_prompt = "以下是与你的问题相关的信息：\n\n"
        
        for item in context:
            if "text" in item:
                context_prompt += f"文本内容: {item['text']}\n"
                if "metadata" in item and item["metadata"]:
                    context_prompt += f"元数据: {json.dumps(item['metadata'], ensure_ascii=False)}\n"
                context_prompt += "\n"
        
        # 添加上下文和用户查询
        messages.append({"role": "user", "content": context_prompt + f"\n用户问题: {query}"})

        return messages
    
    async def _prepare_messages_with_image_context(self, query: str, context: List[Dict], 
                                           image_path: Optional[str] = None,
                                           system_prompt: Optional[str] = None,
                                           preprocess: bool = True) -> List[Dict]:
        """异步准备带有图片和上下文的消息列表
        
        Args:
            query: 用户查询
            context: 检索到的上下文
            image_path: 可选的图片路径
            system_prompt: 系统提示，如果为None则使用默认提示
            preprocess: 是否预处理消息
            
        Returns:
            List[Dict]: 消息列表
        """
        if system_prompt is None:
            system_prompt = """你是一个智能助手，基于提供的上下文信息和图片回答用户的问题。
如果上下文中没有足够的信息来回答问题，请诚实地告知用户你不知道，不要编造信息。
如果问题与上下文无关，请基于你的知识回答。"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 构建上下文提示
        context_prompt = "以下是与你的问题相关的信息：\n\n"
        
        for item in context:
            if "text" in item:
                context_prompt += f"文本内容: {item['text']}\n"
                if "metadata" in item and item["metadata"]:
                    context_prompt += f"元数据: {json.dumps(item['metadata'], ensure_ascii=False)}\n"
                context_prompt += "\n"
        
        # 准备用户消息内容
        user_content = []
        
        # 添加文本内容
        user_content.append({"type": "text", "text": context_prompt + f"\n用户问题: {query}"})
        
        # 如果提供了图片，异步添加图片内容
        if image_path:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_path
                }
            })
        
        messages.append({"role": "user", "content": user_content})

        if preprocess:  
            messages = await messages_preprocess(messages)
        
        return messages
    
    async def query(self, query: str, n_results: int = 5, system_prompt: Optional[str] = None, 
                   retrieval_type: str = "text", preprocess: bool = True) -> str:
        """异步基于文本查询进行RAG
        
        Args:
            query: 用户查询
            n_results: 检索结果数量
            system_prompt: 可选的系统提示
            retrieval_type: 召回类型，可选值为"text"（文本召回）、"image"（图像召回）或"both"（文本和图像均召回）
            preprocess: 是否预处理消息
            
        Returns:
            str: 生成的回答
        """
        # 异步检索相关内容
        
        if retrieval_type == "text":
            # 文本召回
            context = await asyncio.to_thread(
                self.retriever.search_text, query=query, n_results=n_results
            )
            # 准备消息
            messages = await self._prepare_messages_with_context(query, context, system_prompt)
        elif retrieval_type == "image":
            # 图像召回
            context = await asyncio.to_thread(
                self.retriever.cross_modal_search, query=query, n_results=n_results
            )
            # 准备消息（不包含图片）
            messages = await self._prepare_messages_with_context(query, context, system_prompt)
        elif retrieval_type == "both":
            # 文本和图像均召回
            text_context = await asyncio.to_thread(
                self.retriever.search_text, query=query, n_results=n_results//2
            )
            image_context = await asyncio.to_thread(
                self.retriever.cross_modal_search, query=query, n_results=n_results//2
            )
            # 合并上下文
            combined_context = text_context + image_context
            # 按相似度排序
            combined_context.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            # 如果结果超过n_results，则截断
            if len(combined_context) > n_results:
                combined_context = combined_context[:n_results]
            # 准备消息
            messages = await self._prepare_messages_with_context(query, combined_context, system_prompt)
        else:
            raise ValueError(f"不支持的召回类型: {retrieval_type}，可选值为'text'、'image'或'both'")
        
        if preprocess:
            messages = await messages_preprocess(messages)
            
        # 异步调用OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def query_with_image(self, query: str, image_path: str, n_results: int = 5, 
                        system_prompt: Optional[str] = None,
                        preprocess: bool = True) -> str:
        """异步基于图片和文本查询进行RAG
        
        Args:
            query: 用户查询
            image_path: 图片路径
            n_results: 检索结果数量
            system_prompt: 可选的系统提示
            
        Returns:
            str: 生成的回答
        """
        # 异步检索相关内容
        context = await asyncio.to_thread(
            self.retriever.cross_modal_search, query=query, n_results=n_results
        )
        
        # 异步准备消息
        messages = await self._prepare_messages_with_image_context(query, context, image_path, system_prompt, preprocess)
        
        # 异步调用OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def query_image(self, image_path: str, query: str = "描述这张图片", n_results: int = 5,
                   system_prompt: Optional[str] = None,
                   preprocess: bool = True) -> str:
        """异步基于图片查询进行RAG
        
        Args:
            image_path: 图片路径
            query: 用户查询，默认为"描述这张图片"
            n_results: 检索结果数量
            system_prompt: 可选的系统提示
            preprocess: 是否预处理消息
            
        Returns:
            str: 生成的回答
        """
        # 异步检索相关图片
        context = await asyncio.to_thread(
            self.retriever.search_image, image_path=image_path, n_results=n_results
        )
        
        # 异步准备消息
        messages = await self._prepare_messages_with_image_context(query, context, image_path, system_prompt, preprocess)
        
        # 异步调用OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
        
    async def batch_query(self, queries: List[str], n_results: int = 5, 
                         system_prompt: Optional[str] = None,
                         retrieval_type: str = "text",
                         preprocess: bool = True) -> List[str]:
        """异步批量处理多个文本查询
        
        Args:
            queries: 查询列表
            n_results: 每个查询的检索结果数量
            system_prompt: 可选的系统提示
            retrieval_type: 召回类型，可选值为"text"（文本召回）、"image"（图像召回）或"both"（文本和图像均召回）
            preprocess: 是否预处理消息
            
        Returns:
            List[str]: 生成的回答列表
        """
        tasks = [self.query(query, n_results, system_prompt, retrieval_type, preprocess) for query in queries]
        return await asyncio.gather(*tasks)
    
    async def batch_query_with_images(self, queries: List[str], image_paths: List[str], 
                                    n_results: int = 5, system_prompt: Optional[str] = None,
                                    preprocess: bool = True) -> List[str]:
        """异步批量处理多个图文查询
        
        Args:
            queries: 查询列表
            image_paths: 图片路径列表，长度必须与queries相同
            n_results: 每个查询的检索结果数量
            system_prompt: 可选的系统提示
            
        Returns:
            List[str]: 生成的回答列表
        """
        if len(queries) != len(image_paths):
            raise ValueError("查询列表和图片路径列表长度必须相同")
            
        tasks = [self.query_with_image(query, image_path, n_results, system_prompt, preprocess) 
                for query, image_path in zip(queries, image_paths)]
        return await asyncio.gather(*tasks) 