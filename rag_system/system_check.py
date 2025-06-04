#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG系統健康檢查
快速檢查系統各組件是否正常運作
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import requests
import config

def check_gpu():
    """檢查GPU狀態"""
    print("🖥️ 檢查GPU狀態...")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✅ GPU可用: {gpu_name} ({memory_total:.0f}GB)")
            return True
        else:
            print("⚠️ GPU不可用，將使用CPU模式")
            return False
    except ImportError:
        print("❌ PyTorch未安裝")
        return False

def check_ollama():
    """檢查Ollama連接"""
    print("🤖 檢查Ollama連接...")
    try:
        response = requests.get(f"{config.AI_CONFIG['base_url']}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            print(f"✅ Ollama連接正常，可用模型: {len(models)} 個")
            
            if config.AI_CONFIG['model'] in model_names:
                print(f"✅ 目標模型 {config.AI_CONFIG['model']} 可用")
                return True
            else:
                print(f"⚠️ 目標模型 {config.AI_CONFIG['model']} 不可用")
                print(f"可用模型: {model_names}")
                return False
        else:
            print(f"❌ Ollama連接失敗: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama連接失敗: {e}")
        print("💡 請確認:")
        print("  1. Ollama是否運行: ollama serve")
        print("  2. 模型是否安裝: ollama pull llama3.1")
        return False

def check_database():
    """檢查向量資料庫"""
    print("📊 檢查向量資料庫...")
    try:
        from rag_processor import RAGProcessor
        processor = RAGProcessor(verbose=False)

        # 嘗試載入現有集合
        try:
            processor.collection = processor.chroma_client.get_collection(config.COLLECTION_NAME)
            count = processor.collection.count()
            if count > 0:
                print(f"✅ 向量資料庫可用，包含 {count} 個向量")
                return True
            else:
                print("⚠️ 向量資料庫為空，需要處理PDF建立知識庫")
                return False
        except Exception as collection_error:
            print("⚠️ 向量資料庫集合不存在，需要處理PDF建立知識庫")
            return False

    except Exception as e:
        print(f"❌ 向量資料庫檢查失敗: {e}")
        return False

def check_files():
    """檢查核心檔案"""
    print("📁 檢查核心檔案...")
    
    required_files = [
        "config.py",
        "rag_processor.py", 
        "rag_ai_responder.py",
        "rag_main.py",
        "intelligent_tutor.py",
        "interactive_learning.py"
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} 缺失")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_directories():
    """檢查必要目錄"""
    print("📂 檢查目錄結構...")
    
    required_dirs = [
        config.DATA_DIR,
        config.PDF_DIR,
        config.KNOWLEDGE_DB_DIR,
        config.OUTPUT_DIR
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️ {dir_path} 不存在，將自動創建")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return True

def main():
    """主檢查函數"""
    print("🔍 RAG智能教學系統健康檢查")
    print("="*60)
    
    checks = [
        ("GPU狀態", check_gpu),
        ("Ollama連接", check_ollama), 
        ("向量資料庫", check_database),
        ("核心檔案", check_files),
        ("目錄結構", check_directories)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 30)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 檢查失敗: {e}")
            results.append((name, False))
    
    # 總結
    print(f"\n📋 檢查總結")
    print("="*60)
    
    passed = 0
    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{len(results)} 項檢查通過")
    
    if passed == len(results):
        print("🎉 系統狀態良好，可以正常使用！")
        print("\n🚀 啟動系統: python rag_main.py")
    else:
        print("⚠️ 系統存在問題，請根據上述提示進行修復")
        
        if not results[1][1]:  # Ollama檢查失敗
            print("\n💡 Ollama修復建議:")
            print("  1. 啟動Ollama: ollama serve")
            print("  2. 安裝模型: ollama pull llama3.1")
            
        if not results[2][1]:  # 資料庫檢查失敗
            print("\n💡 資料庫修復建議:")
            print("  1. 運行: python rag_main.py")
            print("  2. 選擇選項1處理PDF建立知識庫")

if __name__ == "__main__":
    main()
