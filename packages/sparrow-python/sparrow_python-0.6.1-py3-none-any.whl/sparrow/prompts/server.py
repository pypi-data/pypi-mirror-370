from typing import Any, Dict, List, Optional  # noqa: D100, UP035

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from sparrow.prompts.manager import PromptManager

app = FastAPI()
manager = PromptManager()

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# 请求体模型
class SavePromptRequest(BaseModel):  # noqa: D101
    name: str
    messages: List[Dict[str, Any]]
    tags: Optional[List[str]] = None
    comment: str = ""
    model_type: str

class GetPromptRequest(BaseModel):
    name: str
    version: Optional[int] = None

class GetPromptDetailsRequest(BaseModel):
    name: str

class DeleteVersionRequest(BaseModel):
    name: str
    version: int

class CompareVersionsRequest(BaseModel):
    name: str
    version1: int
    version2: int

@app.post("/prompts/list")
def list_prompts():
    """获取所有prompt列表"""
    return manager.list_prompts()

@app.post("/prompts/details")
def get_prompt_details(request: GetPromptDetailsRequest):
    """获取指定prompt的详细信息"""
    data, _ = manager.load_prompt(request.name)
    if data is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return data

@app.post("/prompts/save")
def save_prompt(request: SavePromptRequest):
    """保存新的prompt或更新现有prompt"""
    success = manager.save_prompt(
        request.name,
        request.messages,
        request.tags,
        request.comment,
        request.model_type,
    )
    if not success:
        return {"message": "No changes detected"}
    return {"message": "Prompt saved successfully"}

@app.post("/prompts/get")
def get_prompt(request: GetPromptRequest):
    """获取指定prompt的内容"""
    messages = manager.get_prompt_messages(request.name, request.version)
    if messages is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return messages

@app.post("/prompts/conversation")
def get_conversation(request: GetPromptRequest):
    """获取对话消息(除system message外)"""
    messages = manager.get_conversation_messages(request.name, request.version)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return messages

@app.post("/prompts/delete")
def delete_prompt(request: GetPromptRequest):
    """删除指定的prompt"""
    try:
        success = manager.delete_prompt(request.name)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found or cannot be deleted")
        return {"message": "Prompt deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/prompts/delete_version")
def delete_version(request: DeleteVersionRequest):
    """删除指定版本"""
    try:
        success = manager.delete_version(request.name, request.version)
        if not success:
            raise HTTPException(status_code=404, detail="Version not found or cannot be deleted")
        return {"message": "Version deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/prompts/restore_version")
def restore_version(request: DeleteVersionRequest):
    """恢复指定版本"""
    success = manager.restore_version(request.name, request.version)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"message": "Version restored successfully"}

@app.post("/prompts/versions")
def get_prompt_versions(request: GetPromptRequest):
    """获取指定prompt的所有版本信息"""
    data, _ = manager.load_prompt(request.name)
    if data is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return data["versions"]

@app.post("/prompts/compare")
def compare_versions(request: CompareVersionsRequest):
    """比较两个版本的差异"""
    diff_html = manager.compare_versions(
        request.name,
        request.version1,
        request.version2
    )
    if diff_html is None:
        raise HTTPException(status_code=404, detail="Invalid versions")
    return diff_html

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=18000, reload=True)