import os
from typing import Optional
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Config:
    """配置管理类，从环境变量读取配置"""
    
    # 基本配置
    RAG_MAX_RESULTS: int = int(os.getenv("RAG_MAX_RESULTS", "10"))
    RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))
    RAG_ENABLE_LOGGING: bool = os.getenv("RAG_ENABLE_LOGGING", "true").lower() == "true"
    RAG_LOG_LEVEL: str = os.getenv("RAG_LOG_LEVEL", "INFO")
    RAG_DEFAULT_TOP_K: int = int(os.getenv("RAG_DEFAULT_TOP_K", "10"))
    RAG_DEFAULT_SEARCH_TYPE: str = os.getenv("RAG_DEFAULT_SEARCH_TYPE", "semanticSearch")
    
    # 向量化器配置
    RAG_VECTORIZER_MAX_FEATURES: int = int(os.getenv("RAG_VECTORIZER_MAX_FEATURES", "1000"))
    RAG_VECTORIZER_NGRAM_RANGE: tuple = tuple(
        int(x) for x in os.getenv("RAG_VECTORIZER_NGRAM_RANGE", "1,2").split(",")
    )
    
    # 支持的文件格式
    RAG_SUPPORTED_FORMATS: list = os.getenv("RAG_SUPPORTED_FORMATS", "txt,md,pdf,docx").split(",")
    
    # 存储配置
    RAG_STORAGE_PATH: str = os.getenv("RAG_STORAGE_PATH", "./rag_data")
    
    # 备份配置
    RAG_BACKUP_ENABLED: bool = os.getenv("RAG_BACKUP_ENABLED", "false").lower() == "true"
    RAG_BACKUP_INTERVAL: int = int(os.getenv("RAG_BACKUP_INTERVAL", "3600"))
    
    # RAG API配置
    RAG_BASE_API: str = os.getenv("RAG_BASE_API", "http://localhost:8000")
    
    @classmethod
    def get_all_config(cls) -> dict:
        """获取所有配置"""
        return {
            "RAG_MAX_RESULTS": cls.RAG_MAX_RESULTS,
            "RAG_SIMILARITY_THRESHOLD": cls.RAG_SIMILARITY_THRESHOLD,
            "RAG_ENABLE_LOGGING": cls.RAG_ENABLE_LOGGING,
            "RAG_LOG_LEVEL": cls.RAG_LOG_LEVEL,
            "RAG_DEFAULT_TOP_K": cls.RAG_DEFAULT_TOP_K,
            "RAG_DEFAULT_SEARCH_TYPE": cls.RAG_DEFAULT_SEARCH_TYPE,
            "RAG_VECTORIZER_MAX_FEATURES": cls.RAG_VECTORIZER_MAX_FEATURES,
            "RAG_VECTORIZER_NGRAM_RANGE": cls.RAG_VECTORIZER_NGRAM_RANGE,
            "RAG_SUPPORTED_FORMATS": cls.RAG_SUPPORTED_FORMATS,
            "RAG_STORAGE_PATH": cls.RAG_STORAGE_PATH,
            "RAG_BACKUP_ENABLED": cls.RAG_BACKUP_ENABLED,
            "RAG_BACKUP_INTERVAL": cls.RAG_BACKUP_INTERVAL,
            "RAG_BASE_API": cls.RAG_BASE_API,
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置的有效性"""
        try:
            # 检查必要的目录是否存在
            if not os.path.exists(cls.RAG_STORAGE_PATH):
                os.makedirs(cls.RAG_STORAGE_PATH, exist_ok=True)
            
            # 验证数值范围
            if cls.RAG_SIMILARITY_THRESHOLD < 0 or cls.RAG_SIMILARITY_THRESHOLD > 1:
                raise ValueError("RAG_SIMILARITY_THRESHOLD must be between 0 and 1")
            
            if cls.RAG_MAX_RESULTS <= 0:
                raise ValueError("RAG_MAX_RESULTS must be positive")
            
            return True
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False

# 全局配置实例
config = Config() 