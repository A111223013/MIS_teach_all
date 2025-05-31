#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索功能測試腳本
用於診斷向量搜索問題
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import config
from rag_processor import RAGProcessor
from rag_ai_responder import AIResponder

def test_database_content():
    """測試資料庫內容"""
    print("🔍 測試資料庫內容")
    print("="*50)
    
    try:
        # 初始化處理器
        processor = RAGProcessor(verbose=False)
        
        # 檢查集合
        if not processor.collection:
            try:
                processor.collection = processor.chroma_client.get_collection(config.COLLECTION_NAME)
            except Exception as e:
                print(f"❌ 無法載入集合: {e}")
                return False
        
        # 檢查資料庫大小
        count = processor.collection.count()
        print(f"📊 資料庫包含: {count} 個向量")
        
        if count == 0:
            print("❌ 資料庫為空")
            return False
        
        # 獲取前5個文檔樣本
        print("\n📝 資料庫樣本內容:")
        sample = processor.collection.get(limit=5)
        
        for i, (doc_id, content, metadata) in enumerate(zip(
            sample['ids'], 
            sample['documents'], 
            sample['metadatas']
        )):
            print(f"\n樣本 {i+1}:")
            print(f"  ID: {doc_id}")
            print(f"  內容: {content[:100]}...")
            print(f"  章節: {metadata.get('chapter', 'N/A')}")
            print(f"  語言: {metadata.get('language', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_function():
    """測試搜索功能"""
    print("\n🔍 測試搜索功能")
    print("="*50)
    
    try:
        # 初始化AI回答系統
        ai_responder = AIResponder(language='chinese')
        
        # 測試問題列表
        test_questions = [
            "作業系統",
            "operating system", 
            "什麼是作業系統",
            "deadlock",
            "死鎖",
            "process",
            "進程",
            "memory",
            "記憶體"
        ]
        
        for question in test_questions:
            print(f"\n🔍 測試問題: '{question}'")
            
            # 直接測試ChromaDB查詢
            try:
                results = ai_responder.rag_processor.collection.query(
                    query_texts=[question],
                    n_results=5
                )
                
                result_count = len(results.get('ids', [[]])[0])
                print(f"  原始結果: {result_count} 個")
                
                if result_count > 0:
                    # 顯示前3個結果的距離
                    distances = results.get('distances', [[]])[0]
                    for i, distance in enumerate(distances[:3]):
                        similarity = 1 - distance if distance <= 1.0 else 0.0
                        print(f"    結果 {i+1}: 距離={distance:.3f}, 相似度={similarity:.3f}")
                        
                        # 顯示內容片段
                        if i < len(results['documents'][0]):
                            content = results['documents'][0][i][:50]
                            print(f"      內容: {content}...")
                
            except Exception as e:
                print(f"  ❌ 查詢失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_similarity():
    """測試向量相似度"""
    print("\n🧮 測試向量相似度")
    print("="*50)
    
    try:
        processor = RAGProcessor(verbose=False)
        
        # 測試向量化
        test_texts = [
            "作業系統是什麼",
            "operating system definition",
            "什麼是死鎖",
            "deadlock concept"
        ]
        
        print("🔄 生成測試向量...")
        embeddings = processor.embedding_model.encode(test_texts)
        print(f"✅ 成功生成 {len(embeddings)} 個向量，維度: {embeddings.shape[1]}")
        
        # 計算相似度
        import numpy as np
        
        print("\n📊 向量相似度矩陣:")
        for i, text1 in enumerate(test_texts):
            for j, text2 in enumerate(test_texts):
                if i <= j:
                    similarity = np.dot(embeddings[i], embeddings[j]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                    )
                    print(f"  '{text1[:20]}...' vs '{text2[:20]}...': {similarity:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 向量測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🧪 RAG搜索功能診斷")
    print("="*60)
    
    # 測試1: 資料庫內容
    if not test_database_content():
        print("\n❌ 資料庫測試失敗，請檢查資料庫是否正確建立")
        return
    
    # 測試2: 搜索功能
    if not test_search_function():
        print("\n❌ 搜索功能測試失敗")
        return
    
    # 測試3: 向量相似度
    if not test_vector_similarity():
        print("\n❌ 向量相似度測試失敗")
        return
    
    print("\n✅ 所有測試完成")
    print("\n💡 建議:")
    print("1. 如果搜索結果距離都很大(>1.0)，可能是向量化模型問題")
    print("2. 如果沒有中文內容，可能是PDF處理時語言識別問題")
    print("3. 如果相似度都很低(<0.3)，可能需要調整搜索閾值")

if __name__ == "__main__":
    main()
