#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG AI回答系統 - 支援中英文雙語的智能問答
整合向量檢索和本地AI模型，提供結構化回答
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime

# 導入配置和RAG處理器
import config
from rag_processor import RAGProcessor

# 設定日誌
logger = logging.getLogger(__name__)

class AIResponder:
    """
    AI回答系統 - 負責智能問答和回答生成

    主要功能:
    1. 支援中英文雙語回答
    2. 向量檢索相關知識點
    3. 結構化回答生成
    4. 本地AI模型整合
    """

    def __init__(self,
                 language: str = None,
                 rag_processor: RAGProcessor = None,
                 ai_model: str = None):
        """
        初始化AI回答系統

        Args:
            language: 回答語言 ('chinese', 'english')
            rag_processor: RAG處理器實例
            ai_model: AI模型名稱
        """
        # 設定語言
        self.language = language or config.DEFAULT_LANGUAGE
        if self.language not in config.SUPPORTED_LANGUAGES:
            logger.warning(f"⚠️ 不支援的語言: {self.language}，使用預設語言: {config.DEFAULT_LANGUAGE}")
            self.language = config.DEFAULT_LANGUAGE

        # 設定AI模型
        self.ai_model = ai_model or config.LOCAL_AI_MODEL
        self.ai_base_url = config.LOCAL_AI_BASE_URL

        # 初始化或載入RAG處理器
        self.rag_processor = rag_processor or self._init_rag_processor()

        # 科目資訊
        self.subject_info = config.DEFAULT_SUBJECT_INFO.copy()

        # 載入提示詞模板
        self.prompt_templates = self._load_prompt_templates()

        logger.info(f"🤖 AI回答系統初始化完成 (語言: {config.SUPPORTED_LANGUAGES[self.language]['name']})")

    def _init_rag_processor(self) -> RAGProcessor:
        """
        初始化RAG處理器 (支援GPU)

        Returns:
            RAGProcessor: RAG處理器實例
        """
        try:
            # 使用GPU初始化RAG處理器
            processor = RAGProcessor(
                verbose=False,
                use_gpu=config.GPU_CONFIG['enable_gpu']
            )

            # 嘗試載入現有的向量資料庫
            if processor.use_chromadb:
                try:
                    processor.collection = processor.chroma_client.get_collection(config.COLLECTION_NAME)
                    logger.info("✅ 成功載入現有的向量資料庫")
                    logger.info(f"🖥️ 向量處理設備: {processor.device}")
                except:
                    logger.warning("⚠️ 未找到現有的向量資料庫，請先建立知識庫")

            return processor

        except Exception as e:
            logger.error(f"❌ 初始化RAG處理器失敗: {e}")
            raise

    def _load_prompt_templates(self) -> Dict[str, str]:
        """
        載入提示詞模板

        Returns:
            Dict[str, str]: 提示詞模板字典
        """
        templates = {
            'chinese': """你是一位專業的資訊管理課程教學助理。請根據提供的教材內容，用繁體中文回答學生問題。

【教材內容參考】
{context}

【學生問題】
{question}

請根據上述教材內容，提供詳細且準確的回答。如果教材中沒有相關資訊，請誠實說明並提供一般性的解釋。""",

            'english': """You are a professional teaching assistant for Information Management courses. Please answer student questions in English based on the provided textbook content.

【Textbook Content Reference】
{context}

【Student Question】
{question}

Please provide a detailed and accurate answer based on the textbook content above. If there is no relevant information in the textbook, please state this honestly and provide a general explanation."""
        }

        return templates

    def set_language(self, language: str) -> bool:
        """
        設定回答語言

        Args:
            language: 語言代碼 ('chinese', 'english')

        Returns:
            bool: 設定是否成功
        """
        if language in config.SUPPORTED_LANGUAGES:
            self.language = language
            logger.info(f"🌐 語言已切換為: {config.SUPPORTED_LANGUAGES[language]['name']}")
            return True
        else:
            logger.warning(f"⚠️ 不支援的語言: {language}")
            return False

    def set_subject_info(self, subject_info: Dict[str, str]):
        """
        設定科目資訊

        Args:
            subject_info: 科目資訊字典
        """
        self.subject_info.update(subject_info)
        logger.info(f"📚 科目資訊已更新: {self.subject_info['科目名稱']}")

    def analyze_question(self, question: str) -> Dict[str, Any]:
        """
        分析問題並提取關鍵資訊

        Args:
            question: 學生問題

        Returns:
            Dict[str, Any]: 問題分析結果
        """
        # 問題類型分類
        question_types = {
            "定義類": ["什麼是", "定義", "definition", "what is", "概念", "meaning"],
            "功能類": ["功能", "作用", "用途", "function", "purpose", "how does", "作用是"],
            "比較類": ["區別", "差異", "比較", "difference", "compare", "vs", "versus", "對比"],
            "原理類": ["原理", "機制", "如何", "怎樣", "principle", "mechanism", "how", "工作原理"],
            "應用類": ["應用", "實例", "例子", "application", "example", "use case", "案例"],
            "步驟類": ["步驟", "流程", "過程", "steps", "process", "procedure", "如何做"]
        }

        detected_type = "一般問題"
        for q_type, keywords in question_types.items():
            if any(keyword.lower() in question.lower() for keyword in keywords):
                detected_type = q_type
                break

        # 提取關鍵概念
        common_concepts = [
            "作業系統", "operating system", "process", "進程", "thread", "線程",
            "memory", "記憶體", "virtual memory", "虛擬記憶體", "file system", "文件系統",
            "scheduling", "調度", "deadlock", "死鎖", "synchronization", "同步",
            "cpu", "kernel", "核心", "interrupt", "中斷", "system call", "系統調用",
            "database", "資料庫", "network", "網路", "security", "安全", "algorithm", "演算法"
        ]

        detected_concepts = [concept for concept in common_concepts
                           if concept.lower() in question.lower()]

        # 檢測語言
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', question))
        total_chars = len(question)
        is_chinese = chinese_chars / total_chars > 0.3 if total_chars > 0 else False

        return {
            "question_type": detected_type,
            "detected_concepts": detected_concepts,
            "question_language": "中文" if is_chinese else "英文",
            "complexity": "複雜" if len(question) > 50 else "簡單"
        }

    def search_knowledge(self, question: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        搜索相關知識點 (增強調試版)

        Args:
            question: 問題
            top_k: 返回結果數量

        Returns:
            List[Dict[str, Any]]: 搜索結果
        """
        if not self.rag_processor or not self.rag_processor.collection:
            logger.warning("⚠️ 向量資料庫未初始化")
            return []

        top_k = top_k or config.SEARCH_CONFIG['default_top_k']

        try:
            # 檢查資料庫狀態
            collection_count = self.rag_processor.collection.count()
            logger.info(f"📊 資料庫包含 {collection_count} 個向量")

            if collection_count == 0:
                logger.warning("⚠️ 資料庫為空，請先處理PDF建立知識庫")
                return []

            # 使用ChromaDB搜索
            logger.info(f"🔍 搜索問題: '{question}' (top_k={top_k})")
            results = self.rag_processor.collection.query(
                query_texts=[question],
                n_results=min(top_k, collection_count)  # 確保不超過資料庫大小
            )

            logger.info(f"🔍 原始搜索結果: {len(results.get('ids', [[]])[0])} 個")

            # 格式化搜索結果
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    distance = results['distances'][0][i] if 'distances' in results and results['distances'][0] else 0.0
                    similarity = 1 - distance if distance <= 1.0 else 0.0

                    result = {
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'][0] else {},
                        "distance": distance,
                        "similarity": similarity
                    }
                    search_results.append(result)

                    # 調試資訊：顯示前3個結果的相似度
                    if i < 5:
                        logger.info(f"  結果 {i+1}: 相似度={similarity:.3f}, 距離={distance:.3f}")

            # 過濾低相似度結果
            threshold = config.SEARCH_CONFIG['similarity_threshold']
            filtered_results = [r for r in search_results if r['similarity'] >= threshold]

            logger.info(f"🔍 過濾後結果: {len(filtered_results)} 個 (閾值={threshold})")

            # 強制返回結果策略
            if not filtered_results and search_results:
                logger.info("💡 閾值過濾後無結果，使用最相似的5個結果")
                filtered_results = search_results[:5]
            elif len(filtered_results) < config.SEARCH_CONFIG.get('min_results', 3) and search_results:
                logger.info(f"💡 結果數量不足，補充到{config.SEARCH_CONFIG.get('min_results', 3)}個")
                needed = config.SEARCH_CONFIG.get('min_results', 3) - len(filtered_results)
                additional = [r for r in search_results if r not in filtered_results][:needed]
                filtered_results.extend(additional)

            # 確保至少有結果
            if not filtered_results and search_results:
                logger.info("💡 強制返回前3個結果")
                filtered_results = search_results[:3]

            return filtered_results

        except Exception as e:
            logger.error(f"❌ 搜索知識點失敗: {e}")
            import traceback
            logger.error(f"錯誤詳情: {traceback.format_exc()}")
            return []

    def extract_structured_info(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        從搜索結果提取結構化資訊

        Args:
            search_results: 搜索結果

        Returns:
            Dict[str, Any]: 結構化資訊
        """
        if not search_results:
            return {
                "chapters": ["未找到相關章節"],
                "knowledge_points": ["未找到相關知識點"],
                "page_references": ["N/A"],
                "context": "沒有找到相關教材內容。"
            }

        # 提取章節資訊
        chapters = set()
        knowledge_points = set()
        page_references = set()
        context_parts = []

        for result in search_results:
            metadata = result.get('metadata', {})
            content = result.get('content', '')

            # 章節資訊
            chapter = metadata.get('chapter', '未知章節')
            section = metadata.get('section', '未知小節')

            if chapter and chapter != '前言':
                chapters.add(chapter)
            if section and section != '無小節':
                knowledge_points.add(section)

            # 頁碼
            page = metadata.get('page_number')
            if page and str(page) != 'N/A':
                page_references.add(str(page))

            # 內容摘要
            if content and len(content) > 50:
                similarity = result.get('similarity', 0)
                context_parts.append({
                    'content': content[:600] + "..." if len(content) > 300 else content,
                    'page': page,
                    'similarity': similarity
                })

        # 排序並格式化
        sorted_context = sorted(context_parts, key=lambda x: x['similarity'], reverse=True)
        context_text = "\n\n".join([
            f"【頁碼 {item['page']} | 相似度 {item['similarity']:.2f}】{item['content']}"
            for item in sorted_context[:3]
        ])

        return {
            "chapters": list(chapters)[:3] if chapters else ["相關章節"],
            "knowledge_points": list(knowledge_points)[:3] if knowledge_points else ["相關概念"],
            "page_references": sorted(list(page_references))[:5] if page_references else ["N/A"],
            "context": context_text if context_text else "未找到相關內容。"
        }

    def generate_ai_response(self, question: str, context: str) -> str:
        """
        使用本地AI模型生成回答

        Args:
            question: 問題
            context: 上下文

        Returns:
            str: AI生成的回答
        """
        try:
            template = self.prompt_templates[self.language]

            # 簡化的prompt格式化，只使用必要的參數
            prompt = template.format(
                context=context,
                question=question
            )

            # 調用本地AI模型
            response = requests.post(
                f"{self.ai_base_url}/api/generate",
                json={
                    "model": self.ai_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": config.AI_RESPONSE_CONFIG['temperature'],
                        "num_predict": config.AI_RESPONSE_CONFIG['max_tokens']
                    }
                },
                timeout=config.AI_RESPONSE_CONFIG['timeout']
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '抱歉，無法生成回答。')
            else:
                logger.error(f"❌ AI模型回應錯誤: {response.status_code}")
                return "抱歉，AI模型暫時無法回應。"

        except requests.exceptions.Timeout:
            logger.error("❌ AI模型回應超時")
            return "抱歉，AI模型回應超時，請稍後再試。"
        except Exception as e:
            logger.error(f"❌ 生成AI回答失敗: {e}")
            return "抱歉，生成回答時發生錯誤。"

    def generate_fallback_response(self, question: str, search_results: List[Dict]) -> str:
        """
        生成備用回答（當AI模型不可用時）

        Args:
            question: 問題
            search_results: 搜索結果

        Returns:
            str: 備用回答
        """
        if not search_results:
            return "抱歉，我在教材中沒有找到與您問題直接相關的內容。請嘗試重新表述您的問題或使用更具體的術語。"

        # 基於搜索結果生成簡單回答
        best_result = search_results[0]
        content = best_result.get('content', '')
        metadata = best_result.get('metadata', {})

        if self.language == 'chinese':
            response = f"根據教材內容，{content[:200]}..."
            if metadata.get('page_number'):
                response += f"\n\n詳細內容請參考教材第 {metadata['page_number']} 頁。"
        else:
            response = f"According to the textbook, {content[:200]}..."
            if metadata.get('page_number'):
                response += f"\n\nFor more details, please refer to page {metadata['page_number']} of the textbook."

        return response

    def answer_question(self, question: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        回答問題的主要方法

        Args:
            question: 學生問題
            use_ai: 是否使用AI模型生成回答

        Returns:
            Dict[str, Any]: 結構化回答
        """
        logger.info(f"🤔 收到問題: {question}")

        # 1. 分析問題
        question_analysis = self.analyze_question(question)

        # 2. 搜索相關知識點
        search_results = self.search_knowledge(question)

        # 3. 提取結構化資訊
        structured_info = self.extract_structured_info(search_results)

        # 4. 生成詳細回答
        try:
            if use_ai and search_results:
                detailed_answer = self.generate_ai_response(question, structured_info.get('context', ''))
            else:
                detailed_answer = self.generate_fallback_response(question, search_results)
        except Exception as e:
            logger.error(f"❌ 生成詳細回答失敗: {e}")
            detailed_answer = self.generate_fallback_response(question, search_results)

        # 5. 生成相關概念和學習建議
        related_concepts = self._extract_related_concepts(search_results)
        study_suggestions = self._generate_study_suggestions(question_analysis)

        # 6. 組裝最終回答
        response = {
            "科目": self.subject_info.get("科目名稱", "資訊管理概論"),
            "教材": f"{self.subject_info.get('英文名稱', 'Introduction to Information Management')} ({self.subject_info.get('版本', '最新版')})",
            "相關章節": " | ".join(structured_info.get("chapters", ["相關章節"])),
            "知識點": " | ".join(structured_info.get("knowledge_points", ["相關概念"])),
            "頁碼參考": " | ".join(structured_info.get("page_references", ["N/A"])),
            "詳細回答": detailed_answer,
            "相關概念": related_concepts,
            "學習建議": study_suggestions,
            "問題類型": question_analysis.get("question_type", "其他"),
            "檢測語言": question_analysis.get("question_language", "未知"),
            "搜索結果數量": len(search_results),
            "回答語言": config.SUPPORTED_LANGUAGES[self.language]['name'],
            "時間戳": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        logger.info(f"✅ 回答生成完成 (搜索到 {len(search_results)} 個相關結果)")
        return response

    def _extract_related_concepts(self, search_results: List[Dict]) -> str:
        """
        提取相關概念

        Args:
            search_results: 搜索結果

        Returns:
            str: 相關概念字符串
        """
        concepts = set()

        for result in search_results[:3]:
            content = result.get('content', '').lower()
            metadata = result.get('metadata', {})

            # 從關鍵詞中提取
            keywords = metadata.get('keywords', '')
            if keywords:
                concepts.update([kw.strip().title() for kw in keywords.split(',')[:3]])

            # 從內容中提取常見概念
            common_terms = [
                "process", "thread", "memory", "cpu", "kernel", "file system",
                "scheduling", "deadlock", "synchronization", "virtual memory",
                "database", "network", "security", "algorithm", "data structure"
            ]

            for term in common_terms:
                if term in content:
                    concepts.add(term.title())

        if concepts:
            return " | ".join(list(concepts)[:5])
        else:
            if self.language == 'chinese':
                return "進程管理 | 記憶體管理 | 文件系統 | 資料結構"
            else:
                return "Process Management | Memory Management | File System | Data Structure"

    def _generate_study_suggestions(self, question_analysis: Dict) -> str:
        """
        生成學習建議

        Args:
            question_analysis: 問題分析結果

        Returns:
            str: 學習建議
        """
        question_type = question_analysis["question_type"]

        if self.language == 'chinese':
            suggestions = {
                "定義類": "建議先理解基本概念，然後學習其在系統中的作用和實現方式。",
                "功能類": "建議結合實際例子理解功能，並思考為什麼需要這些功能。",
                "比較類": "建議製作對比表格，列出各自的特點、優缺點和適用場景。",
                "原理類": "建議畫出流程圖或示意圖，幫助理解工作原理和步驟。",
                "應用類": "建議尋找實際案例，理解理論如何應用到實際系統中。",
                "步驟類": "建議按步驟實際操作，加深對流程的理解。"
            }
            base_suggestion = suggestions.get(question_type, "建議多閱讀教材相關章節，並結合實例加深理解。")
            return f"{base_suggestion} 同時建議複習相關的前置知識點，確保理解的連貫性。"
        else:
            suggestions = {
                "定義類": "It's recommended to first understand the basic concepts, then learn their roles and implementation in the system.",
                "功能類": "It's recommended to understand functions through practical examples and think about why these functions are needed.",
                "比較類": "It's recommended to create comparison tables listing features, pros and cons, and applicable scenarios.",
                "原理類": "It's recommended to draw flowcharts or diagrams to help understand the working principles and steps.",
                "應用類": "It's recommended to find practical cases to understand how theory applies to actual systems.",
                "步驟類": "It's recommended to practice the steps hands-on to deepen understanding of the process."
            }
            base_suggestion = suggestions.get(question_type, "It's recommended to read related textbook chapters and combine with examples for deeper understanding.")
            return f"{base_suggestion} Also review related prerequisite knowledge points to ensure coherent understanding."

    def format_response_for_display(self, response: Dict[str, Any]) -> str:
        """
        格式化回答用於顯示

        Args:
            response: 回答字典

        Returns:
            str: 格式化的回答字符串
        """
        if self.language == 'chinese':
            formatted = f"""
📚 科目：{response['科目']}
📖 教材：{response['教材']}
📄 相關章節：{response['相關章節']}
🎯 知識點：{response['知識點']}
📍 頁碼參考：{response['頁碼參考']}

💡 詳細回答：
{response['詳細回答']}

🔗 相關概念：
{response['相關概念']}

📝 學習建議：
{response['學習建議']}

---
🔍 問題類型：{response['問題類型']} | 檢測語言：{response['檢測語言']} | 搜索結果：{response['搜索結果數量']}個
🌐 回答語言：{response['回答語言']} | 時間：{response['時間戳']}
"""
        else:
            formatted = f"""
📚 Subject: {response['科目']}
📖 Textbook: {response['教材']}
📄 Related Chapters: {response['相關章節']}
🎯 Knowledge Points: {response['知識點']}
📍 Page References: {response['頁碼參考']}

💡 Detailed Answer:
{response['詳細回答']}

🔗 Related Concepts:
{response['相關概念']}

📝 Study Suggestions:
{response['學習建議']}

---
🔍 Question Type: {response['問題類型']} | Detected Language: {response['檢測語言']} | Search Results: {response['搜索結果數量']}
🌐 Response Language: {response['回答語言']} | Time: {response['時間戳']}
"""

        return formatted.strip()

    def get_system_status(self) -> Dict[str, Any]:
        """
        獲取系統狀態 (包含GPU資訊)

        Returns:
            Dict[str, Any]: 系統狀態資訊
        """
        status = {
            "ai_responder_ready": True,
            "current_language": config.SUPPORTED_LANGUAGES[self.language]['name'],
            "ai_model": self.ai_model,
            "embedding_model": self.rag_processor.embedding_model_name if self.rag_processor else "未載入",
            "database_ready": bool(self.rag_processor and self.rag_processor.collection),
            "subject_info": self.subject_info
        }

        # 添加GPU資訊
        if self.rag_processor:
            status.update({
                "device": self.rag_processor.device,
                "gpu_available": self.rag_processor.gpu_info['available'],
                "gpu_name": self.rag_processor.gpu_info.get('device_name', 'N/A'),
                "gpu_memory_total": f"{self.rag_processor.gpu_info.get('memory_total', 0)}GB",
                "gpu_memory_free": f"{self.rag_processor.gpu_info.get('memory_free', 0)}GB"
            })
        else:
            gpu_info = config.check_gpu_availability()
            status.update({
                "device": "未初始化",
                "gpu_available": gpu_info['available'],
                "gpu_name": gpu_info.get('device_name', 'N/A'),
                "gpu_memory_total": f"{gpu_info.get('memory_total', 0)}GB",
                "gpu_memory_free": f"{gpu_info.get('memory_free', 0)}GB"
            })

        # 測試AI模型連接
        try:
            test_response = requests.get(f"{self.ai_base_url}/api/tags", timeout=5)
            status["ai_model_available"] = test_response.status_code == 200
        except:
            status["ai_model_available"] = False

        return status
