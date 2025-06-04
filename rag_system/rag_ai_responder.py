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
            'chinese': {
                'basic_definition': """你是一位專業的教學助理。請用繁體中文簡潔明確地回答學生的基礎定義問題。

【教材內容】
{context}

【學生問題】
{question}

請提供：
1. 清楚的定義
2. 核心特徵（2-3點）
3. 一個簡單的例子

回答要直接、準確，不需要過度解釋。""",

                'guided_teaching': """你是一位專業的教學助理，擅長引導式教學。請用繁體中文回答學生問題，並採用引導式教學方法。

【教材內容】
{context}

【學生問題】
{question}

【問題類型】{question_type}
【學習層次】{learning_level}
【複雜度】{complexity}

請按照以下引導式教學結構回答：

🎯 **核心概念**
先建立基礎理解

🔍 **深入探討**
逐步引導學生思考關鍵問題

💡 **實際應用**
連結理論與實務

🤔 **思考問題**
提出2-3個引導性問題，幫助學生深化理解

📚 **延伸學習**
建議相關的學習方向

回答要循序漸進，引導學生主動思考，而不是直接給答案。""",

                'problem_solving': """你是一位專業的教學助理，擅長問題解決指導。請用繁體中文幫助學生解決問題。

【教材內容】
{context}

【學生問題】
{question}

請採用問題解決導向的教學方式：

🎯 **問題分析**
幫助學生理解問題的本質

🔧 **解決策略**
提供系統性的解決方法

⚡ **實作步驟**
具體的操作指引

🚨 **常見陷阱**
提醒可能遇到的問題

✅ **驗證方法**
如何確認解決方案的正確性"""
            },

            'english': {
                'basic_definition': """You are a professional teaching assistant. Please provide a clear and concise answer to the student's basic definition question in English.

【Textbook Content】
{context}

【Student Question】
{question}

Please provide:
1. Clear definition
2. Core characteristics (2-3 points)
3. A simple example

Keep the answer direct and accurate without over-explanation.""",

                'guided_teaching': """You are a professional teaching assistant skilled in guided instruction. Please answer the student's question in English using guided teaching methods.

【Textbook Content】
{context}

【Student Question】
{question}

【Question Type】{question_type}
【Learning Level】{learning_level}
【Complexity】{complexity}

Please structure your response using guided teaching:

🎯 **Core Concept**
Establish foundational understanding

🔍 **Deep Exploration**
Guide students to think about key questions

💡 **Practical Application**
Connect theory with practice

🤔 **Thinking Questions**
Pose 2-3 guiding questions to deepen understanding

📚 **Extended Learning**
Suggest related learning directions

Guide students to think actively rather than giving direct answers.""",

                'problem_solving': """You are a professional teaching assistant skilled in problem-solving guidance. Please help the student solve problems in English.

【Textbook Content】
{context}

【Student Question】
{question}

Please use problem-solving oriented teaching:

🎯 **Problem Analysis**
Help students understand the nature of the problem

🔧 **Solution Strategy**
Provide systematic solution methods

⚡ **Implementation Steps**
Specific operational guidance

🚨 **Common Pitfalls**
Alert to potential issues

✅ **Verification Methods**
How to confirm solution correctness"""
            }
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
        使用AI智能分析問題

        Args:
            question: 學生問題

        Returns:
            Dict[str, Any]: 問題分析結果
        """
        try:
            # 使用AI進行問題分析
            analysis_prompt = self._create_analysis_prompt(question)

            response = requests.post(
                f"{self.ai_base_url}/api/generate",
                json={
                    "model": self.ai_model,
                    "prompt": analysis_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # 低溫度確保一致性
                        "num_predict": 500
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                ai_response = response.json().get('response', '')
                return self._parse_ai_analysis(ai_response, question)
            else:
                logger.warning("AI分析失敗，使用備用分析")
                return self._fallback_analysis(question)

        except Exception as e:
            logger.warning(f"AI分析出錯: {e}，使用備用分析")
            return self._fallback_analysis(question)

    def _create_analysis_prompt(self, question: str) -> str:
        """
        創建AI問題分析的prompt

        Args:
            question: 學生問題

        Returns:
            str: 分析prompt
        """
        if self.language == 'chinese':
            return f"""你是一位專業的教學分析專家。請分析以下學生問題，並以JSON格式回答：

學生問題：{question}

請分析並回答以下內容（必須是有效的JSON格式）：
{{
    "question_type": "問題類型（如：基礎定義、深度理解、比較分析、原理探討、實際應用、操作步驟、問題解決、評估判斷等）",
    "complexity": "複雜度（簡單/中等/複雜）",
    "learning_level": "學習層次（記憶/理解/應用/分析/評估/創造）",
    "concept_categories": ["相關概念類別（如：作業系統、演算法、資料結構、網路、資料庫等）"],
    "key_concepts": ["關鍵概念列表"],
    "needs_guidance": "是否需要引導式教學（true/false）",
    "teaching_approach": "建議的教學方式（直接回答/引導式教學/問題解決導向）",
    "question_language": "問題語言（中文/英文）"
}}

只回答JSON，不要其他文字。"""
        else:
            return f"""You are a professional educational analysis expert. Please analyze the following student question and respond in JSON format:

Student Question: {question}

Please analyze and answer the following content (must be valid JSON format):
{{
    "question_type": "Question type (e.g., basic definition, deep understanding, comparative analysis, principle exploration, practical application, operational steps, problem solving, evaluation judgment, etc.)",
    "complexity": "Complexity (simple/medium/complex)",
    "learning_level": "Learning level (remember/understand/apply/analyze/evaluate/create)",
    "concept_categories": ["Related concept categories (e.g., operating systems, algorithms, data structures, networks, databases, etc.)"],
    "key_concepts": ["Key concepts list"],
    "needs_guidance": "Whether guided teaching is needed (true/false)",
    "teaching_approach": "Recommended teaching approach (direct answer/guided teaching/problem-solving oriented)",
    "question_language": "Question language (Chinese/English)"
}}

Only respond with JSON, no other text."""

    def _parse_ai_analysis(self, ai_response: str, question: str) -> Dict[str, Any]:
        """
        解析AI分析結果

        Args:
            ai_response: AI回應
            question: 原始問題

        Returns:
            Dict[str, Any]: 解析後的分析結果
        """
        try:
            import json
            import re

            # 提取JSON部分
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)

                # 確保所有必要字段存在
                return {
                    "question_type": analysis.get("question_type", "一般問題"),
                    "complexity": analysis.get("complexity", "中等"),
                    "learning_level": analysis.get("learning_level", "理解"),
                    "concept_categories": analysis.get("concept_categories", []),
                    "key_concepts": analysis.get("key_concepts", []),
                    "needs_guidance": analysis.get("needs_guidance", True),
                    "teaching_approach": analysis.get("teaching_approach", "引導式教學"),
                    "question_language": analysis.get("question_language", "中文" if any('\u4e00' <= c <= '\u9fff' for c in question) else "英文")
                }
            else:
                logger.warning("無法從AI回應中提取JSON")
                return self._fallback_analysis(question)

        except Exception as e:
            logger.warning(f"解析AI分析結果失敗: {e}")
            return self._fallback_analysis(question)

    def _fallback_analysis(self, question: str) -> Dict[str, Any]:
        """
        備用分析方法（當AI分析失敗時）

        Args:
            question: 學生問題

        Returns:
            Dict[str, Any]: 基本分析結果
        """
        # 簡單的語言檢測
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', question))
        total_chars = len(question)
        is_chinese = chinese_chars / total_chars > 0.3 if total_chars > 0 else False

        # 基本複雜度判斷
        complexity = "簡單" if len(question) < 20 else "中等" if len(question) < 50 else "複雜"

        return {
            "question_type": "一般問題",
            "complexity": complexity,
            "learning_level": "理解",
            "concept_categories": [],
            "key_concepts": [],
            "needs_guidance": complexity != "簡單",
            "teaching_approach": "引導式教學",
            "question_language": "中文" if is_chinese else "英文"
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

    def generate_ai_response(self, question: str, context: str, question_analysis: Dict[str, Any] = None) -> str:
        """
        使用本地AI模型生成智能回答

        Args:
            question: 問題
            context: 上下文
            question_analysis: 問題分析結果

        Returns:
            str: AI生成的回答
        """
        try:
            # 智能選擇教學模板
            template_type = self._select_teaching_template(question_analysis or {})
            template = self.prompt_templates[self.language][template_type]

            # 根據模板類型格式化prompt
            if template_type == 'basic_definition':
                prompt = template.format(
                    context=context,
                    question=question
                )
            else:
                # 引導式教學或問題解決模板
                prompt = template.format(
                    context=context,
                    question=question,
                    question_type=question_analysis.get('question_type', '一般問題'),
                    learning_level=question_analysis.get('learning_level', '理解'),
                    complexity=question_analysis.get('complexity', '中等')
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

    def _select_teaching_template(self, question_analysis: Dict[str, Any]) -> str:
        """
        基於AI分析結果選擇教學模板

        Args:
            question_analysis: AI問題分析結果

        Returns:
            str: 模板類型
        """
        teaching_approach = question_analysis.get('teaching_approach', '引導式教學')
        complexity = question_analysis.get('complexity', '中等')
        question_type = question_analysis.get('question_type', '一般問題')

        # 直接使用AI建議的教學方式
        if teaching_approach == '直接回答' or (complexity == '簡單' and '定義' in question_type):
            return 'basic_definition'
        elif teaching_approach == '問題解決導向' or '解決' in question_type or '步驟' in question_type:
            return 'problem_solving'
        else:
            # 預設使用引導式教學
            return 'guided_teaching'

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

        # 4. 生成詳細回答（智能化）
        try:
            if use_ai and search_results:
                detailed_answer = self.generate_ai_response(
                    question,
                    structured_info.get('context', ''),
                    question_analysis
                )
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
        # 優先使用AI分析的關鍵概念
        key_concepts = question_analysis.get('key_concepts', [])
        concept_categories = question_analysis.get('concept_categories', [])

        if key_concepts:
            # 直接使用AI識別的關鍵概念
            return " | ".join(key_concepts[:5])  # 最多5個概念
        elif concept_categories:
            # 使用概念類別
            return " | ".join(concept_categories[:5])
        else:
            # 從搜索結果中提取（備用方法）
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
                    return "系統管理 | 資料處理 | 演算法 | 資料結構"
                else:
                    return "System Management | Data Processing | Algorithm | Data Structure"

    def _generate_study_suggestions(self, question_analysis: Dict) -> str:
        """
        基於AI分析結果生成智能學習建議

        Args:
            question_analysis: AI問題分析結果

        Returns:
            str: 學習建議
        """
        try:
            # 使用AI生成個性化學習建議
            suggestion_prompt = self._create_suggestion_prompt(question_analysis)

            response = requests.post(
                f"{self.ai_base_url}/api/generate",
                json={
                    "model": self.ai_model,
                    "prompt": suggestion_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200
                    }
                },
                timeout=20
            )

            if response.status_code == 200:
                ai_suggestion = response.json().get('response', '').strip()
                return ai_suggestion if ai_suggestion else self._fallback_suggestions(question_analysis)
            else:
                return self._fallback_suggestions(question_analysis)

        except Exception as e:
            logger.warning(f"AI學習建議生成失敗: {e}")
            return self._fallback_suggestions(question_analysis)

    def _create_suggestion_prompt(self, question_analysis: Dict) -> str:
        """
        創建學習建議生成的prompt

        Args:
            question_analysis: 問題分析結果

        Returns:
            str: 建議prompt
        """
        if self.language == 'chinese':
            return f"""基於以下問題分析，請提供簡潔的學習建議（不超過50字，使用emoji）：

問題類型：{question_analysis.get('question_type', '一般問題')}
複雜度：{question_analysis.get('complexity', '中等')}
學習層次：{question_analysis.get('learning_level', '理解')}
概念類別：{', '.join(question_analysis.get('concept_categories', []))}
關鍵概念：{', '.join(question_analysis.get('key_concepts', []))}

請提供針對性的學習建議，格式：emoji + 簡短建議 | emoji + 簡短建議"""
        else:
            return f"""Based on the following question analysis, please provide concise study suggestions (no more than 50 words, use emojis):

Question Type: {question_analysis.get('question_type', 'general question')}
Complexity: {question_analysis.get('complexity', 'medium')}
Learning Level: {question_analysis.get('learning_level', 'understand')}
Concept Categories: {', '.join(question_analysis.get('concept_categories', []))}
Key Concepts: {', '.join(question_analysis.get('key_concepts', []))}

Please provide targeted study suggestions, format: emoji + brief suggestion | emoji + brief suggestion"""

    def _fallback_suggestions(self, question_analysis: Dict) -> str:
        """
        備用學習建議生成

        Args:
            question_analysis: 問題分析結果

        Returns:
            str: 備用學習建議
        """
        complexity = question_analysis.get("complexity", "中等")
        learning_level = question_analysis.get("learning_level", "理解")

        if self.language == 'chinese':
            base_suggestions = []

            if learning_level == "記憶":
                base_suggestions.append("📝 重複練習關鍵概念")
            elif learning_level == "理解":
                base_suggestions.append("🔍 深入理解概念關聯")
            elif learning_level == "應用":
                base_suggestions.append("💻 實際操作練習")
            elif learning_level == "分析":
                base_suggestions.append("🔬 比較分析不同方法")
            else:
                base_suggestions.append("🎯 理解核心概念")

            if complexity == "複雜":
                base_suggestions.append("📚 分階段學習")

            return " | ".join(base_suggestions) + " | 🗺️ 複習前置知識"
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
