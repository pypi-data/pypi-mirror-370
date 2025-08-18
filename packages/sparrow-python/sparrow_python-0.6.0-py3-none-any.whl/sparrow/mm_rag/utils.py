import torch
from PIL import Image
from cn_clip.clip import load_from_name
import cn_clip.clip as clip
from typing import Union, List, Tuple
import os
from sparrow import relp


class CLIPWrapper:
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model, self.preprocess = load_from_name("ViT-B-16", device=device, download_root=relp("./models/clip"))
        
    def encode_text(self, text: Union[str, List[str]]) -> torch.Tensor:
        """编码文本"""
        if isinstance(text, str):
            text = [text]
        text = clip.tokenize(text).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text)
        return text_features.cpu().numpy()
    
    def encode_image(self, image_path: Union[str, List[str]]) -> torch.Tensor:
        """编码图片"""
        if isinstance(image_path, str):
            image_path = [image_path]
            
        images = []
        for path in image_path:
            if not os.path.exists(path):
                raise FileNotFoundError(f"图片文件不存在: {path}")
            image = Image.open(path).convert('RGB')
            image = self.preprocess(image)
            images.append(image)
            
        images = torch.stack(images).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(images)
        return image_features.cpu().numpy()
    
    def compute_similarity(self, query_features: torch.Tensor, 
                         doc_features: torch.Tensor) -> torch.Tensor:
        """计算相似度"""
        query_features = query_features / query_features.norm(dim=-1, keepdim=True)
        doc_features = doc_features / doc_features.norm(dim=-1, keepdim=True)
        similarity = torch.matmul(query_features, doc_features.T)
        return similarity 