from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class RAG(BaseModel):
    """
    RAG 模型
    """
    id: str = Field(..., description="文档ID")
    content: str = Field(..., description="文档内容")
    metadata: dict = Field(..., description="文档元数据")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class RAGQuery(BaseModel):
    """
    RAG 查询模型
    """
    query: str = Field(..., description="查询内容")  # 必填字段，无默认值
    top_k: Optional[int] = Field(10, description="返回结果数量")
    query_type: Optional[str] = Field("semanticSearch", description="查询类型")
    filter: Optional[Dict[str, Any]] = Field(default_factory=dict, description="过滤条件")
    rerank: Optional[bool] = Field(False, description="是否重新排序")
    rerank_model: Optional[str] = Field(None, description="重新排序模型")


