import logging
import sys
import asyncio
import argparse
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from .schemas.rag import RAGQuery
from .service import RAGService
from .config import config

# 配置日志
if config.RAG_ENABLE_LOGGING:
    logging.basicConfig(
        level=getattr(logging, config.RAG_LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

# 创建FastMCP服务器实例
mcp = FastMCP("rag-mcp-server")

# 添加 HTTP 端点
@mcp.app.get("/")
async def root():
    return {"message": "RAG MCP Server", "version": "0.1.5"}

@mcp.app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

@mcp.app.get("/tools")
async def list_tools():
    return {"tools": ["rag_search"]}

@mcp.tool(name="rag_search", description="搜索文档，使用语义搜索或关键词搜索")
async def rag_search(
    query: str,
    top_k: int = 10,
    query_type: str = "semanticSearch",
    filter: Dict[str, Any] = None,
    rerank: bool = False,
    rerank_model: Optional[str] = None
) -> str:
    """
    搜索文档，使用语义搜索或关键词搜索
    
    Args:
        query: 查询内容
        top_k: 返回结果数量
        query_type: 查询类型
        filter: 过滤条件
        rerank: 是否重新排序
        rerank_model: 重新排序模型
    
    Returns:
        搜索结果
    """
    try:
        logger.info(f"收到搜索请求: {query}")
        
        # 构建RAGQuery对象
        rag_query = RAGQuery(
            query=query,
            top_k=top_k,
            query_type=query_type,
            filter=filter or {},
            rerank=rerank,
            rerank_model=rerank_model
        )
        
        # 调用RAG服务
        result = await RAGService.search(rag_query)
        
        logger.info("搜索完成")
        
        # 返回结果
        return f"搜索完成，找到文档：{result.id}\n内容：{result.content[:200]}...\n元数据：{result.metadata}"
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise

def run():
    mcp.run(transport="stdio")

def main():
    """主函数，支持命令行参数"""
    parser = argparse.ArgumentParser(description="RAG MCP Server")
    parser.add_argument("--port", type=int, default=8080, help="服务器端口")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务器主机")
    parser.add_argument("--stdio", action="store_true", help="使用标准输入输出模式")
    
    args = parser.parse_args()
    
    if args.stdio:
        # MCP 标准模式
        run()
    else:
        # HTTP 服务器模式
        import uvicorn
        uvicorn.run(mcp.app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()