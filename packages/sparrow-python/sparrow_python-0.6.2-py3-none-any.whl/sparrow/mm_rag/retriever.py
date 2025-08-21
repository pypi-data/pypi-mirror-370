import chromadb
from chromadb.config import Settings
from typing import List, Dict, Union, Optional
import numpy as np
from .utils import CLIPWrapper
import uuid

class MultiModalRAG:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """初始化多模态RAG系统
        
        Args:
            persist_directory: ChromaDB持久化存储目录
        """
        self.clip = CLIPWrapper()
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 创建文本和图片的集合
        self.text_collection = self.client.get_or_create_collection(
            name="text_collection",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.image_collection = self.client.get_or_create_collection(
            name="image_collection",
            metadata={"hnsw:space": "cosine"}
        )
        
    def _prepare_text_data(self, texts: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None, metadatas: Optional[Union[Dict, List[Dict]]] = None) -> tuple:
        """准备文本数据，处理输入参数并编码文本
        
        Args:
            texts: 文本内容或文本列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
            
        Returns:
            tuple: (texts, doc_ids, metadatas, embeddings)
        """
        # 转换单个元素为列表
        if isinstance(texts, str):
            texts = [texts]
        
        # 处理doc_ids，如果不提供则自动生成
        if doc_ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        elif isinstance(doc_ids, str):
            doc_ids = [doc_ids]
        
        # 处理元数据
        if metadatas is not None and not isinstance(metadatas, list):
            metadatas = [metadatas]
        
        # 确保所有列表长度一致
        assert len(texts) == len(doc_ids), "texts和doc_ids的长度必须相同"
        if metadatas is not None:
            assert len(texts) == len(metadatas), "texts和metadatas的长度必须相同"
        
        # 批量编码文本 - 使用现有的encode_text方法，它已经支持批量处理
        features = self.clip.encode_text(texts)
        
        # 确保每个特征向量是一维的
        embeddings = []
        for i in range(len(features)):
            feature = features[i]
            if feature.ndim > 1:
                feature = feature.flatten()
            embeddings.append(feature.tolist())
            
        return texts, doc_ids, metadatas, embeddings
        
    def _prepare_image_data(self, image_paths: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None, metadatas: Optional[Union[Dict, List[Dict]]] = None) -> tuple:
        """准备图片数据，处理输入参数并编码图片
        
        Args:
            image_paths: 图片路径或路径列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
            
        Returns:
            tuple: (image_paths, doc_ids, metadatas, embeddings)
        """
        # 转换单个元素为列表
        if isinstance(image_paths, str):
            image_paths = [image_paths]
        
        # 处理doc_ids，如果不提供则自动生成
        if doc_ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in range(len(image_paths))]
        elif isinstance(doc_ids, str):
            doc_ids = [doc_ids]
        
        # 处理元数据
        if metadatas is not None and not isinstance(metadatas, list):
            metadatas = [metadatas]
        
        # 确保所有列表长度一致
        assert len(image_paths) == len(doc_ids), "image_paths和doc_ids的长度必须相同"
        if metadatas is not None:
            assert len(image_paths) == len(metadatas), "image_paths和metadatas的长度必须相同"
        
        # 批量编码图片 - 使用现有的encode_image方法，它已经支持批量处理
        features = self.clip.encode_image(image_paths)
        
        # 确保每个特征向量是一维的
        embeddings = []
        for i in range(len(features)):
            feature = features[i]
            if feature.ndim > 1:
                feature = feature.flatten()
            embeddings.append(feature.tolist())
            
        return image_paths, doc_ids, metadatas, embeddings

    def add_text(self, texts: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None, metadatas: Optional[Union[Dict, List[Dict]]] = None):
        """添加文本到检索系统
        
        Args:
            texts: 文本内容或文本列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
            
        Returns:
            生成的doc_ids
        """
        texts, doc_ids, metadatas, embeddings = self._prepare_text_data(texts, doc_ids, metadatas)
        
        self.text_collection.add(
            embeddings=embeddings,
            documents=texts,
            ids=doc_ids,
            metadatas=metadatas
        )
        
        # 返回生成的doc_ids，方便用户后续使用
        return doc_ids
        
    def add_image(self, image_paths: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None, metadatas: Optional[Union[Dict, List[Dict]]] = None):
        """添加图片到检索系统
        
        Args:
            image_paths: 图片路径或路径列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
            
        Returns:
            生成的doc_ids
        """
        image_paths, doc_ids, metadatas, embeddings = self._prepare_image_data(image_paths, doc_ids, metadatas)
        
        self.image_collection.add(
            embeddings=embeddings,
            documents=image_paths,
            ids=doc_ids,
            metadatas=metadatas
        )
        
        # 返回生成的doc_ids，方便用户后续使用
        return doc_ids

    def upsert_text(self, texts: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None, metadatas: Optional[Union[Dict, List[Dict]]] = None):
        """ 添加、更新 文本 至 collection 
        
        Args:
            texts: 文本内容或文本列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
            
        Returns:
            生成的doc_ids
        """
        texts, doc_ids, metadatas, embeddings = self._prepare_text_data(texts, doc_ids, metadatas)
        
        self.text_collection.upsert(
            embeddings=embeddings,
            documents=texts,
            ids=doc_ids,
            metadatas=metadatas
        )
        
        # 返回生成的doc_ids，方便用户后续使用
        return doc_ids
    
    def upsert_images(self, image_paths: Union[str, List[str]], doc_ids: Optional[Union[str, List[str]]] = None, metadatas: Optional[Union[Dict, List[Dict]]] = None):
        """ 添加、更新 图片 至 collection 
        
        Args:
            image_paths: 图片路径或路径列表
            doc_ids: 文档ID或ID列表，如果不提供则自动生成
            metadatas: 可选的元数据或元数据列表
            
        Returns:
            生成的doc_ids
        """
        image_paths, doc_ids, metadatas, embeddings = self._prepare_image_data(image_paths, doc_ids, metadatas)
        
        self.image_collection.upsert(
            embeddings=embeddings,
            documents=image_paths,
            ids=doc_ids,
            metadatas=metadatas
        )
        
        # 返回生成的doc_ids，方便用户后续使用
        return doc_ids
        
    def _process_search_results(self, results: Dict, n_results: int, use_similarity: bool = True) -> List[Dict]:
        """处理搜索结果，提取文档和元数据信息
        
        Args:
            results: ChromaDB返回的原始搜索结果
            n_results: 需要返回的结果数量
            use_similarity: 是否将距离转换为相似度，默认为True
            
        Returns:
            处理后的结果列表，每个元素包含文档和元数据
        """
        processed_results = []
        
        # 确保有结果返回
        if not results or 'documents' not in results or not results['documents']:
            return processed_results
            
        # 获取文档和元数据
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        ids = results.get('ids', [[]])[0]
        
        # 限制结果数量
        n = min(n_results, len(documents))
        
        # 组合文档和元数据
        for i in range(n):
            # 如果需要，将距离转换为相似度
            score = None
            if distances and i < len(distances):
                if use_similarity:
                    # 将距离转换为相似度，距离越小相似度越高
                    score = 1.0 - distances[i]
                else:
                    score = distances[i]
                    
            item = {
                'document': documents[i],
                'metadata': metadatas[i] if metadatas and i < len(metadatas) else None,
                'score': score,  # 使用统一的字段名，根据use_similarity决定是距离还是相似度
                'id': ids[i] if ids and i < len(ids) else None
            }
            processed_results.append(item)
            
        return processed_results
        
    def search_text(self, query: str, n_results: int = 5, process_results: bool = True, use_similarity: bool = True) -> List[Dict]:
        """文本检索
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            process_results: 是否对结果进行处理，默认为True
            use_similarity: 是否将距离转换为相似度，默认为True
            
        Returns:
            检索结果列表，每个元素包含文档和元数据
        """
        query_features = self.clip.encode_text(query)
        # 确保是一维数组
        if query_features.ndim > 1:
            query_features = query_features.flatten()
        results = self.text_collection.query(
            query_embeddings=[query_features.tolist()],
            n_results=n_results
        )
        
        if process_results:
            return self._process_search_results(results, n_results, use_similarity)
        return results
    
    def search_image(self, image_path: str, n_results: int = 5, process_results: bool = True, use_similarity: bool = True) -> List[Dict]:
        """图片检索
        
        Args:
            image_path: 查询图片路径
            n_results: 返回结果数量
            process_results: 是否对结果进行处理，默认为True
            use_similarity: 是否将距离转换为相似度，默认为True
            
        Returns:
            检索结果列表，每个元素包含文档和元数据
        """
        query_features = self.clip.encode_image(image_path)
        # 确保是一维数组
        if query_features.ndim > 1:
            query_features = query_features.flatten()
        results = self.image_collection.query(
            query_embeddings=[query_features.tolist()],
            n_results=n_results
        )
        
        if process_results:
            return self._process_search_results(results, n_results, use_similarity)
        return results
    
    def cross_modal_search(self, query: Union[str, str], 
                         n_results: int = 5, process_results: bool = True, use_similarity: bool = True) -> List[Dict]:
        """跨模态检索
        
        Args:
            query: 查询内容（文本或图片路径）
            n_results: 返回结果数量
            process_results: 是否对结果进行处理，默认为True
            use_similarity: 是否将距离转换为相似度，默认为True
            
        Returns:
            检索结果列表，每个元素包含文档和元数据
        """
        if isinstance(query, str) and query.endswith(('.jpg', '.jpeg', '.png')):
            # 图片查询文本
            query_features = self.clip.encode_image(query)
            # 确保是一维数组
            if query_features.ndim > 1:
                query_features = query_features.flatten()
            results = self.text_collection.query(
                query_embeddings=[query_features.tolist()],
                n_results=n_results
            )
        else:
            # 文本查询图片
            query_features = self.clip.encode_text(query)
            # 确保是一维数组
            if query_features.ndim > 1:
                query_features = query_features.flatten()
            results = self.image_collection.query(
                query_embeddings=[query_features.tolist()],
                n_results=n_results
            )
            
        if process_results:
            return self._process_search_results(results, n_results, use_similarity)
        return results
    

if __name__ == "__main__":
    from sparrow import relp
    mm_rag = MultiModalRAG()
    # 使用自动生成的doc_ids
    mm_rag.upsert_text("你好可爱")
    mm_rag.upsert_text("猪猪女孩")
    mm_rag.upsert_images(relp("../images/dog1.png"))
    mm_rag.upsert_images(relp("../images/dog2.png"))
    print("-"*100)
    # 展示使用相似度的结果（默认）
    print("使用相似度的结果（默认）:")
    similarity_results = mm_rag.search_text("可爱", 2)
    print(similarity_results)
    
    print("-"*100)
    # 展示使用距离的结果
    print("使用距离的结果:")
    distance_results = mm_rag.search_text("可爱", 2, use_similarity=False)
    print(distance_results)
    
    print("-"*100)
    # 展示原始结果
    print("原始结果:")
    raw_results = mm_rag.search_text("可爱", 2, process_results=False)
    print(raw_results)
    
    if len(mm_rag.image_collection.get()["ids"]) > 0:
        print("-"*100)
        # 展示图片搜索结果（使用相似度）
        print("图片搜索结果（使用相似度）:")
        image_results = mm_rag.search_image(relp("../images/dog1.png"), 2)
        print(image_results)
        
        print("-"*100)
        # 展示跨模态搜索结果（使用相似度）
        print("跨模态搜索结果（使用相似度）:")
        cross_results = mm_rag.cross_modal_search("可爱", 2)
        print(cross_results)