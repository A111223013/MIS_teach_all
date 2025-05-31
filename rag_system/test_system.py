#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG智能教學系統 - 系統測試腳本
快速測試系統各個組件的功能
"""

import sys
import traceback
from pathlib import Path

# 添加當前目錄到Python路徑
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """測試模組導入"""
    print("🧪 測試1: 模組導入")
    print("-" * 30)
    
    try:
        import config
        print("✅ config 模組導入成功")
        
        from rag_processor import RAGProcessor
        print("✅ RAGProcessor 導入成功")
        
        from rag_ai_responder import AIResponder
        print("✅ AIResponder 導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模組導入失敗: {e}")
        traceback.print_exc()
        return False

def test_config():
    """測試配置"""
    print("\n🧪 測試2: 配置驗證")
    print("-" * 30)
    
    try:
        import config
        
        # 驗證配置
        is_valid = config.validate_config()
        print(f"配置驗證: {'✅ 通過' if is_valid else '❌ 失敗'}")
        
        # 顯示配置摘要
        print("\n配置摘要:")
        print(config.get_config_summary())
        
        return is_valid
        
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False

def test_rag_processor():
    """測試RAG處理器"""
    print("\n🧪 測試3: RAG處理器")
    print("-" * 30)
    
    try:
        from rag_processor import RAGProcessor
        
        # 初始化處理器
        print("🔄 初始化RAG處理器...")
        processor = RAGProcessor(verbose=False)
        print("✅ RAG處理器初始化成功")
        
        # 測試向量化模型
        test_text = "這是一個測試文本 This is a test text"
        embeddings = processor.embedding_model.encode([test_text])
        print(f"✅ 向量化測試成功 (維度: {embeddings.shape[1]})")
        
        # 測試語言檢測
        lang_zh = processor._detect_language("這是中文文本")
        lang_en = processor._detect_language("This is English text")
        print(f"✅ 語言檢測測試: 中文={lang_zh}, 英文={lang_en}")
        
        # 測試章節識別
        chapter_info = processor._identify_chapter_structure("第1章 作業系統概論")
        print(f"✅ 章節識別測試: {chapter_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG處理器測試失敗: {e}")
        traceback.print_exc()
        return False

def test_ai_responder():
    """測試AI回答系統"""
    print("\n🧪 測試4: AI回答系統")
    print("-" * 30)
    
    try:
        from rag_ai_responder import AIResponder
        
        # 初始化AI回答系統
        print("🔄 初始化AI回答系統...")
        ai_responder = AIResponder(language='chinese')
        print("✅ AI回答系統初始化成功")
        
        # 測試問題分析
        test_question = "什麼是作業系統？"
        analysis = ai_responder.analyze_question(test_question)
        print(f"✅ 問題分析測試: {analysis}")
        
        # 測試語言切換
        ai_responder.set_language('english')
        print("✅ 語言切換測試成功")
        
        # 測試系統狀態
        status = ai_responder.get_system_status()
        print(f"✅ 系統狀態測試: AI模型可用={status.get('ai_model_available', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI回答系統測試失敗: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """測試資料庫連接"""
    print("\n🧪 測試5: 資料庫連接")
    print("-" * 30)
    
    try:
        import chromadb
        from rag_processor import RAGProcessor
        import config
        
        # 測試ChromaDB連接
        print("🔄 測試ChromaDB連接...")
        client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        print("✅ ChromaDB連接成功")
        
        # 嘗試創建測試集合
        test_collection = client.get_or_create_collection("test_collection")
        print("✅ 測試集合創建成功")
        
        # 清理測試集合
        client.delete_collection("test_collection")
        print("✅ 測試集合清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 資料庫連接測試失敗: {e}")
        return False

def test_ai_model_connection():
    """測試AI模型連接"""
    print("\n🧪 測試6: AI模型連接")
    print("-" * 30)
    
    try:
        import requests
        import config
        
        # 測試Ollama連接
        print(f"🔄 測試Ollama連接 ({config.LOCAL_AI_BASE_URL})...")
        response = requests.get(f"{config.LOCAL_AI_BASE_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama連接成功，可用模型數量: {len(models)}")
            
            # 檢查目標模型是否可用
            model_names = [model.get('name', '') for model in models]
            target_model = config.LOCAL_AI_MODEL
            
            if any(target_model in name for name in model_names):
                print(f"✅ 目標模型 {target_model} 可用")
                return True
            else:
                print(f"⚠️ 目標模型 {target_model} 不可用")
                print(f"可用模型: {model_names}")
                return False
        else:
            print(f"❌ Ollama連接失敗: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到Ollama服務")
        print("💡 請確保Ollama已啟動並運行在正確的端口")
        return False
    except Exception as e:
        print(f"❌ AI模型連接測試失敗: {e}")
        return False

def test_file_structure():
    """測試檔案結構"""
    print("\n🧪 測試7: 檔案結構")
    print("-" * 30)
    
    try:
        import config
        
        # 檢查必要目錄
        directories = [
            ("PDF目錄", config.PDF_DIR),
            ("知識庫目錄", config.KNOWLEDGE_DB_DIR),
            ("輸出目錄", config.OUTPUT_DIR)
        ]
        
        all_exist = True
        for name, path in directories:
            exists = path.exists()
            print(f"{'✅' if exists else '❌'} {name}: {path}")
            if not exists:
                all_exist = False
                # 嘗試創建目錄
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"  💡 已自動創建目錄")
                except Exception as e:
                    print(f"  ❌ 創建目錄失敗: {e}")
        
        # 檢查核心檔案
        core_files = [
            "config.py",
            "rag_processor.py", 
            "rag_ai_responder.py",
            "rag_main.py",
            "requirements.txt"
        ]
        
        for filename in core_files:
            file_path = Path(__file__).parent / filename
            exists = file_path.exists()
            print(f"{'✅' if exists else '❌'} 核心檔案: {filename}")
            if not exists:
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print(f"❌ 檔案結構測試失敗: {e}")
        return False

def run_all_tests():
    """運行所有測試"""
    print("🎯 RAG智能教學系統 - 系統測試")
    print("=" * 60)
    
    tests = [
        ("模組導入", test_imports),
        ("配置驗證", test_config),
        ("RAG處理器", test_rag_processor),
        ("AI回答系統", test_ai_responder),
        ("資料庫連接", test_database_connection),
        ("AI模型連接", test_ai_model_connection),
        ("檔案結構", test_file_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試 {test_name} 發生異常: {e}")
            results.append((test_name, False))
    
    # 顯示測試摘要
    print("\n" + "=" * 60)
    print("📊 測試摘要")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 個測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統準備就緒。")
        print("💡 您可以運行 'python rag_main.py' 來啟動系統")
    else:
        print("⚠️ 部分測試失敗，請檢查相關配置")
        print("💡 常見問題:")
        print("  • 確保已安裝所有依賴套件: pip install -r requirements.txt")
        print("  • 確保Ollama已啟動並下載了llama3.1模型")
        print("  • 檢查檔案權限和目錄結構")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
