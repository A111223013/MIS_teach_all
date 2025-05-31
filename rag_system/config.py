#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG智能教學系統 - 配置檔案
包含所有系統配置參數，方便統一管理和調整
"""

import os
from pathlib import Path

# =============================================================================
# 基本路徑配置
# =============================================================================

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent

# 資料目錄
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
KNOWLEDGE_DB_DIR = DATA_DIR / "knowledge_db"
OUTPUT_DIR = DATA_DIR / "outputs"

# 確保目錄存在
for directory in [DATA_DIR, PDF_DIR, KNOWLEDGE_DB_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =============================================================================
# AI模型配置
# =============================================================================

# 本地AI模型設定 (Ollama)
LOCAL_AI_MODEL = "llama3.1"
LOCAL_AI_BASE_URL = "http://localhost:11434"

# 向量化模型設定 - GPU優化
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
# 備選模型: "sentence-transformers/all-MiniLM-L6-v2"
# GPU優化模型: "all-mpnet-base-v2" (更大但更準確，適合16GB顯存)

# 向量化GPU優化設定
EMBEDDING_CONFIG = {
    "model_name": EMBEDDING_MODEL,
    "device": "cuda",                        # 強制使用GPU
    "normalize_embeddings": True,            # 標準化嵌入向量
    "convert_to_tensor": True,               # 轉換為GPU張量
    "show_progress_bar": True,               # 顯示進度條
    "batch_size": 64,                        # GPU批量大小 (針對16GB顯存)
    "max_seq_length": 512,                   # 最大序列長度
    "precision": "float32"                   # 暫時使用全精度確保一致性
}

# GPU設定 - RTX 4060 Ti 16GB 優化配置
GPU_CONFIG = {
    "enable_gpu": True,                      # 🚀 GPU已啟用！
    "device": "cuda",                        # GPU設備類型 (cuda/mps)
    "gpu_memory_fraction": 0.8,              # GPU記憶體使用比例 (約12.8GB)
    "mixed_precision": True,                 # 是否使用混合精度加速
    "batch_size_gpu": 64,                    # GPU批量大小 (針對16GB顯存優化)
    "cpu_fallback": True                     # GPU不可用時是否回退到CPU
}

# =============================================================================
# 資料庫配置
# =============================================================================

# ChromaDB設定
CHROMA_DB_PATH = str(KNOWLEDGE_DB_DIR / "chroma_db")
COLLECTION_NAME = "textbook_knowledge"

# FAISS設定 (備選)
FAISS_INDEX_PATH = str(KNOWLEDGE_DB_DIR / "faiss_index")

# =============================================================================
# PDF處理配置
# =============================================================================

# PDF處理參數
PDF_PROCESSING = {
    "strategy": "hi_res",                    # 解析策略: hi_res, fast, ocr_only
    "infer_table_structure": True,           # 是否推斷表格結構
    "chunking_strategy": "by_title",         # 分塊策略: by_title, by_page, basic
    "max_characters": 500,                  # 最大字符數
    "new_after_n_chars": 100,              # 新塊字符數閾值
    "languages": ["eng", "zho"],             # 支援語言: 英文和中文
    "min_content_length": 100                # 最小內容長度閾值
}

# =============================================================================
# 知識點處理配置
# =============================================================================

# 知識點生成參數
KNOWLEDGE_POINT_CONFIG = {
    "min_content_length": 100,               # 最小內容長度
    "max_title_length": 100,                 # 最大標題長度
    "max_summary_length": 200,               # 最大摘要長度
    "max_keywords": 10,                      # 最大關鍵詞數量
    "batch_size": 100                        # 批量處理大小
}

# =============================================================================
# 搜索和檢索配置
# =============================================================================

# 搜索參數 - 極度寬鬆的搜索設定
SEARCH_CONFIG = {
    "default_top_k": 15,                     # 增加返回結果數量
    "max_top_k": 25,                         # 最大返回結果數量
    "similarity_threshold": 0.09,            # 極低閾值，幾乎不過濾
    "enable_reranking": True,                # 是否啟用重排序
    "min_results": 5,                        # 最少返回結果數量
    "force_return_results": True             # 強制返回結果
}

# =============================================================================
# 語言配置
# =============================================================================

# 支援的語言
SUPPORTED_LANGUAGES = {
    "chinese": {
        "name": "中文",
        "code": "zh",
        "prompt_template": "chinese_prompt.txt"
    },
    "english": {
        "name": "English",
        "code": "en",
        "prompt_template": "english_prompt.txt"
    }
}

# 預設語言
DEFAULT_LANGUAGE = "chinese"

# =============================================================================
# 回答生成配置
# =============================================================================

# AI回答參數
AI_RESPONSE_CONFIG = {
    "temperature": 0.7,                      # 創造性參數
    "max_tokens": 2000,                      # 最大token數
    "timeout": 30,                           # 請求超時時間(秒)
    "retry_attempts": 3,                     # 重試次數
    "include_metadata": True,                # 是否包含元數據
    "structured_output": True                # 是否使用結構化輸出
}

# =============================================================================
# 系統配置
# =============================================================================

# 日誌配置
LOGGING_CONFIG = {
    "level": "INFO",                         # 日誌級別: DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(OUTPUT_DIR / "system.log")
}

# 效能配置 - RTX 4060 Ti 16GB 優化
PERFORMANCE_CONFIG = {
    "max_workers": 4,                        # 最大工作線程數
    "chunk_size": 1000,                      # 處理塊大小
    "memory_limit_mb": 4096,                 # 記憶體限制(MB)
    "enable_gpu": True,                      # 是否啟用GPU加速
    "gpu_batch_size": 64,                    # GPU批量處理大小 (16GB顯存可用更大批量)
    "cpu_batch_size": 16                     # CPU批量處理大小
}

# =============================================================================
# 科目資訊配置
# =============================================================================

# 預設科目資訊
DEFAULT_SUBJECT_INFO = {
    "科目名稱": "計算機概論",
    "英文名稱": "Introduction to Computer Science",
}

# =============================================================================
# 輸出檔案配置
# =============================================================================

# 輸出檔案名稱
OUTPUT_FILES = {
    "structured_content": "structured_content.json",
    "knowledge_points": "knowledge_points.json",
    "conversation_history": "conversation_history.json",
    "processing_log": "processing.log"
}

# =============================================================================
# 開發和調試配置
# =============================================================================

# 調試模式
DEBUG_MODE = False

# 是否顯示詳細進度
VERBOSE_MODE = True

# 是否保存中間結果
SAVE_INTERMEDIATE_RESULTS = True

# =============================================================================
# 配置驗證函數
# =============================================================================

def check_gpu_availability():
    """
    檢查GPU可用性

    Returns:
        dict: GPU狀態資訊
    """
    gpu_info = {
        "available": False,
        "device_count": 0,
        "device_name": None,
        "memory_total": 0,
        "memory_free": 0,
        "cuda_version": None
    }

    try:
        import torch

        if torch.cuda.is_available():
            gpu_info["available"] = True
            gpu_info["device_count"] = torch.cuda.device_count()
            gpu_info["device_name"] = torch.cuda.get_device_name(0)
            gpu_info["cuda_version"] = torch.version.cuda

            # 獲取GPU記憶體資訊
            if gpu_info["device_count"] > 0:
                memory_total = torch.cuda.get_device_properties(0).total_memory
                memory_reserved = torch.cuda.memory_reserved(0)
                memory_allocated = torch.cuda.memory_allocated(0)

                gpu_info["memory_total"] = memory_total // (1024**3)  # GB
                gpu_info["memory_free"] = (memory_total - memory_reserved) // (1024**3)  # GB
                gpu_info["memory_allocated"] = memory_allocated // (1024**3)  # GB

    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️ GPU檢查時發生錯誤: {e}")

    return gpu_info

def validate_config():
    """
    驗證配置是否正確

    Returns:
        bool: 配置是否有效
    """
    try:
        # 檢查必要目錄
        for directory in [DATA_DIR, PDF_DIR, KNOWLEDGE_DB_DIR, OUTPUT_DIR]:
            if not directory.exists():
                print(f"❌ 目錄不存在: {directory}")
                return False

        # 檢查模型配置
        if not LOCAL_AI_MODEL:
            print("❌ 未設定本地AI模型")
            return False

        if not EMBEDDING_MODEL:
            print("❌ 未設定向量化模型")
            return False

        # 檢查GPU配置
        if GPU_CONFIG["enable_gpu"]:
            gpu_info = check_gpu_availability()
            if gpu_info["available"]:
                print(f"✅ GPU可用: {gpu_info['device_name']} ({gpu_info['memory_total']}GB)")
            else:
                print("⚠️ GPU不可用，將使用CPU模式")
                if not GPU_CONFIG["cpu_fallback"]:
                    print("❌ GPU不可用且未啟用CPU回退")
                    return False

        print("✅ 配置驗證通過")
        return True

    except Exception as e:
        print(f"❌ 配置驗證失敗: {e}")
        return False

def get_config_summary():
    """
    獲取配置摘要

    Returns:
        str: 配置摘要字符串
    """
    summary = f"""
🔧 RAG系統配置摘要
==================
📁 資料目錄: {DATA_DIR}
🤖 AI模型: {LOCAL_AI_MODEL}
🧠 向量模型: {EMBEDDING_MODEL}
🗄️ 資料庫: ChromaDB ({CHROMA_DB_PATH})
🌐 預設語言: {SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]['name']}
📊 搜索結果數: {SEARCH_CONFIG['default_top_k']}
🔍 調試模式: {'開啟' if DEBUG_MODE else '關閉'}
"""
    return summary

if __name__ == "__main__":
    # 測試配置
    print("🧪 測試配置檔案...")
    if validate_config():
        print(get_config_summary())
    else:
        print("❌ 配置檔案有問題，請檢查設定")
