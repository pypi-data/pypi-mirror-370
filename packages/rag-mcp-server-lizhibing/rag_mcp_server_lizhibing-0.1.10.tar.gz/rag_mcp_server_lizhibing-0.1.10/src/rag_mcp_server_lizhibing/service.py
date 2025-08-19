import asyncio
import logging
from typing import List, Optional
from .schemas.rag import RAG, RAGQuery
from .config import config
import httpx

# 配置日志
if config.RAG_ENABLE_LOGGING:
    logging.basicConfig(
        level=getattr(logging, config.RAG_LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

class RAGService:
    """RAG服务类，使用配置文件中的设置"""
    
    @classmethod
    def add_document(cls, document: RAG):
        """添加文档到RAG系统"""
        try:
            logger.info(f"添加文档: {document.id}")
            
            # 验证文档格式
            if not cls._validate_document_format(document):
                raise ValueError(f"不支持的文档格式")
            
            # 这里可以添加实际的文档处理逻辑
            # 比如向量化、存储等
            
            logger.info(f"文档 {document.id} 添加成功")
            return RAG(id=document.id, content=document.content, metadata=document.metadata)
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise
    
    @classmethod
    async def search(cls, query: RAGQuery):
        """搜索文档"""
        try:
            logger.info(f"执行搜索查询: {query.query}")
            def build_params(query: RAGQuery):
                """构建搜索参数"""
                return {
                    "query": query.query,
                    "searchOptions": {
                        "topK": query.top_k if query.top_k else config.RAG_DEFAULT_TOP_K,
                        "searchType": query.query_type if query.query_type else config.RAG_DEFAULT_SEARCH_TYPE,
                        "rerankingEnabled": query.rerank,
                        "rerankingModel": {
                            "rerankingModelName": query.rerank_model if query.rerank else None,
                        }
                    }
                }

            # 使用配置的API端点
            response = httpx.post(
                f"{config.RAG_BASE_API}/search", 
                json=build_params(query),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            records = result.get('data', {}).get('records', [])
            logger.info(f"搜索完成，找到 {len(records)} 个结果")
            
            if not records:
                raise ValueError("未找到搜索结果")
            
            # 获取第一个结果（得分最高的）
            first_record = records[0]
            segment = first_record.get('segement', {})
            
            from datetime import datetime
            now = datetime.now()
            
            return RAG(
                id=str(segment.get('id', '')),
                content=segment.get('content', ''),
                metadata={
                    'score': first_record.get('score'),
                    'bizId': first_record.get('bizId'),
                    'taskId': first_record.get('taskId'),
                    'segmentNum': segment.get('segmentNum'),
                    'enabled': segment.get('enabled')
                },
                created_at=now,
                updated_at=now
            )
            
        except httpx.RequestError as e:
            logger.error(f"API请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
  