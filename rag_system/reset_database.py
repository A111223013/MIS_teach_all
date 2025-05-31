#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置向量資料庫腳本
清除舊的向量資料庫，準備重新建立
"""

import shutil
import os
from pathlib import Path
import sys

# 添加當前目錄到Python路徑
sys.path.append(str(Path(__file__).parent))

import config

def reset_database():
    """重置向量資料庫"""
    print("🔄 重置向量資料庫")
    print("="*50)
    
    # 要清除的目錄和檔案
    paths_to_remove = [
        config.CHROMA_DB_PATH,
        config.KNOWLEDGE_DB_DIR / "faiss_index",
        config.OUTPUT_DIR / "structured_content.json",
        config.OUTPUT_DIR / "knowledge_points.json"
    ]
    
    removed_count = 0
    
    for path in paths_to_remove:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"✅ 已刪除目錄: {path}")
                else:
                    os.remove(path)
                    print(f"✅ 已刪除檔案: {path}")
                removed_count += 1
            else:
                print(f"⚠️ 路徑不存在: {path}")
        except Exception as e:
            print(f"❌ 刪除失敗 {path}: {e}")
    
    print(f"\n📊 清理完成，共處理 {removed_count} 個項目")
    
    # 重新創建必要目錄
    try:
        config.KNOWLEDGE_DB_DIR.mkdir(parents=True, exist_ok=True)
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print("✅ 重新創建必要目錄")
    except Exception as e:
        print(f"❌ 創建目錄失敗: {e}")
    
    print("\n🎯 資料庫已重置，現在可以重新處理PDF建立知識庫")
    print("💡 請運行: python rag_main.py")
    print("   然後選擇選項1處理PDF檔案")

if __name__ == "__main__":
    print("⚠️ 警告：此操作將刪除所有現有的向量資料庫和知識點")
    confirm = input("確定要繼續嗎？(y/n): ").strip().lower()
    
    if confirm in ['y', 'yes', '是']:
        reset_database()
    else:
        print("❌ 操作已取消")
