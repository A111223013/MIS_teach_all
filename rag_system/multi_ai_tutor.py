#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支援多AI模型的智能教師
"""

import sys
from pathlib import Path
import requests
import json
import google.generativeai as genai
import logging # 導入 logging 模組
import config

# 將父目錄添加到系統路徑，確保可以導入 rag_ai_responder
sys.path.append(str(Path(__file__).parent))

from rag_ai_responder import AIResponder

class MultiAITutor:
    """支援多AI模型的智能教師"""
    
    def __init__(self, ai_model="llama"):
        """初始化教師"""
        # 關閉所有不必要的日誌
        logging.getLogger('rag_ai_responder').setLevel(logging.CRITICAL)
        logging.getLogger('rag_processor').setLevel(logging.CRITICAL)
        logging.getLogger('sentence_transformers').setLevel(logging.CRITICAL)
        logging.getLogger('chromadb').setLevel(logging.CRITICAL)
        logging.getLogger('transformers').setLevel(logging.CRITICAL)
        
        self.ai_responder = AIResponder(language='chinese')
        self.ai_model_type = ai_model
        
        # 根據選擇的模型設置配置
        if ai_model == "gemini":
            self.model_config = config.GEMINI_CONFIG
            try:
                genai.configure(api_key=self.model_config['api_key'])
                self.gemini_model = genai.GenerativeModel(self.model_config['model'])
                print(f"🤖 使用 Gemini AI 模型: {self.model_config['model']}")
            except Exception as e:
                print(f"❌ Gemini 配置錯誤: {e}. 請檢查 API Key 和模型名稱。")
                self.gemini_model = None # 設置為 None，避免後續錯誤
        else:
            self.model_config = config.AI_CONFIG
            print(f"🤖 使用 Llama 本地模型: {self.model_config['model']}")
        
        # 核心變數
        self.original_question = ""  # 主問題
        self.context = ""  # 對話上下文，儲存為字符串
        self.topic_knowledge = ""  # 主題知識
        
        # 統一的教學風格提示詞
        self.TEACHER_STYLE = """你是一位經驗豐富的資管系教授，正在一對一輔導學生，幫助學生透過逐步引導方式理解考題與資管系相關知識，確保學生真正掌握概念，而不只是背誦答案。

**你的教學原則**：
- **引導式對話**：透過一步步提問，引導學生自行思考並得出答案，而非直接給予解答。
- **針對性反饋**：精準評價學生回答，肯定其正確部分，並禮貌地指出需要補充或糾正之處。
- **概念拆解與類比**：當學生不理解時，將複雜概念拆解為更小步驟，並使用生活化例子或類比幫助理解。
- **動態調整難度**：根據學生回答判斷其掌握度，靈活調整問題難度，促進深度學習。
- **避免重複**：回答中絕不重複學生已經說過或你之前說過的內容，力求簡潔有效。

**回應要求**：
- 語氣親切自然，如同真正的老師。
- 回答後，必須提出一個清晰的引導問題，推進學生對當前概念的理解。
- 嚴禁使用任何格式化標題（如 "💡 詳細回答"），直接以自然段落呈現內容。
- 禁止暴露你的思考過程。

現在，讓我們開始一場有深度的學習對話。
"""
        
        print(f"🎓 多AI智能教師已啟動 ({config.AVAILABLE_AI_MODELS[ai_model]['name']})")
    

    def get_topic_knowledge(self, question: str) -> str:
        """獲取主題相關知識"""
        try:
            # 翻譯成英文搜索
            english_question = self._translate_to_english(question)
            search_results = self.ai_responder.search_knowledge(english_question)
            
            if search_results:
                # 提取前3個結果的內容，限制每個結果的長度
                knowledge = "\n".join([
                    result.get('content', '')[:400] 
                    for result in search_results[:3]
                ])
                logging.debug(f"RAG 檢索到的知識: {knowledge[:200]}...") # 添加日誌
                return knowledge
        except Exception as e:
            logging.error(f"獲取主題知識時發生錯誤: {e}")
            pass # 即使RAG失敗也不會讓主流程崩潰
        return "" # 確保始終返回字符串
    
    def _translate_to_english(self, text: str) -> str:
        """翻譯成英文"""
        try:
            if self.ai_model_type == "gemini":
                if not self.gemini_model: # 檢查模型是否成功初始化
                    logging.error("Gemini 模型未初始化，無法進行翻譯。")
                    return text
                prompt = f"Translate to English: {text}"
                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
            else:
                prompt = f"Translate to English: {text}"
                response = requests.post(
                    f"{self.model_config['base_url']}/api/generate",
                    json={
                        "model": self.model_config['model'],
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 50}
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json().get('response', '').strip()
                else:
                    logging.error(f"Llama 翻譯 API 返回錯誤: {response.status_code}, {response.text}")
        except Exception as e:
            logging.error(f"翻譯時發生錯誤: {e}")
            pass
        return text
    
    def ask_ai(self, student_input: str, is_new_question: bool = False) -> str:
        """統一的AI回應函式"""
        
        # 確保上下文包含在提示詞中
        # full_context = self.context if hasattr(self, 'context') else "" # 確保context存在
        # 使用更安全的獲取方式，確保 self.context 始終存在
        full_context = self.context if isinstance(self.context, str) else "" 
        
        # 根據是否是新問題來構建提示詞
        if is_new_question:
            prompt = f"""{self.TEACHER_STYLE}

你當前的對話歷史如下：
{full_context}

學生提出一個新問題：{student_input}
{f"你已獲取與此問題相關的知識，請**自然地將這些知識融入你的解釋和引導中**：" + self.topic_knowledge if self.topic_knowledge else "目前沒有找到相關知識，請僅憑通用知識和你的教學原則進行回答。"}

請先用繁體中文複誦題目，確認題目方向，然後**簡潔地解釋這個概念的核心要點**。
隨後，請從最基礎的相關概念開始，提出一個引導性問題。
例如：如果問「銀行家演算法」，你可以先簡述它是避免死鎖的演算法，然後問學生「你知道什麼是死鎖嗎？」
請確保你的回答語氣親切、專業，並且**不要使用任何格式化標題**。
"""
        else:
            # 學生回答後的追問模式
            prompt = f"""{self.TEACHER_STYLE}

你當前的對話歷史如下：
{full_context}

原始問題：「{self.original_question}」
學生對你上一個引導問題的回答是：{student_input}
{f"你已獲取與此問題相關的知識，請**自然地將這些知識融入你的解釋和引導中**：" + self.topic_knowledge if self.topic_knowledge else "目前沒有找到相關知識，請僅憑通用知識和你的教學原則進行回答。"}

請：
1. **精準評價學生回答**：
   - 根據學生回答判斷其理解程度。如果學生回答表示不清楚、不知道或回答有明顯錯誤：請禮貌地指出其不足，並提供更簡單的提示、不同的類比或將概念拆解成更小的部分，**避免引入新的概念或跳到下一階段**。然後提出一個更具體的引導問題來幫助學生理解。
   - 如果學生回答正確或部分正確：肯定其正確部分，並禮貌地指出需要補充或糾正的地方。
2. **補充和深化知識**：針對學生回答的不足之處，**自然地利用已獲取的相關知識**進行簡潔的補充或糾正。**切勿重複學生已經說過或你之前說過的內容。**
3. **提出下一個引導問題**：這個問題應當旨在**推進學生對「{self.original_question}」的理解**，可以是從原理、應用、優缺點、比較等不同維度進行引導。請確保問題清晰、具體。
請確保你的回答語氣親切、專業，並且**不要使用任何格式化標題**。
"""
        logging.debug(f"完整提示詞長度: {len(prompt)} 字符") # 添加日誌
        logging.debug(f"完整提示詞前200字: {prompt[:200]}...") # 添加日誌
        return self._call_ai(prompt)
    
    def _call_ai(self, prompt: str) -> str:
        """調用AI"""
        try:
            if self.ai_model_type == "gemini":
                if not self.gemini_model: # 檢查模型是否成功初始化
                    return "Gemini 模型未成功初始化，請檢查 API Key 或模型名稱。"
                
                logging.debug("正在調用 Gemini 模型...") 
                
                response = self.gemini_model.generate_content(prompt)
                
                # 檢查 response 是否有內容，以及 text 屬性是否存在且不為 None
                if response and hasattr(response, 'text') and response.text is not None:
                    ai_response = response.text.strip()
                    logging.debug(f"Gemini 原始回應: {ai_response[:100]}...")
                else:
                    logging.warning("Gemini 模型未返回有效文本或回應為空。")
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback.safety_ratings:
                        logging.warning(f"Gemini 安全過濾信息: {response.prompt_feedback.safety_ratings}")
                    return "抱歉，Gemini 模型目前無法提供回應，可能與內容或安全設置有關。"

            else: # Llama 模型
                logging.debug("正在調用 Llama 模型...")
                response = requests.post(
                    f"{self.model_config['base_url']}/api/generate",
                    json={
                        "model": self.model_config['model'],
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 250, # 增加預測長度，減少截斷
                            "top_p": 0.9,
                            "repeat_penalty": 1.3,
                            "stop": ["學生：", "💭", "🤔", "學生回答："] # 更保守的停止詞
                        }
                    },
                    timeout=60 # 增加 timeout
                )
                
                if response.status_code == 200:
                    ai_response = response.json().get('response', '').strip()
                    logging.debug(f"Llama 原始回應: {ai_response[:100]}...")
                else:
                    logging.error(f"Llama API 返回錯誤狀態碼: {response.status_code}, 內容: {response.text}")
                    return f"抱歉，本地模型發生錯誤，狀態碼: {response.status_code}。"
            
            # 驗證回應品質
            if ai_response and len(ai_response) > 10:
                # 檢查是否被截斷 (但不再硬性截斷，僅為觀察)
                if ai_response.endswith(('讓我們', '想像一下', '現在', '但是')) and len(ai_response) < 150: # 短於150字時才嘗試補足
                    ai_response += "你覺得呢？"
                return ai_response
            else:
                logging.warning("AI 回應太短或為空，可能是模型未能生成有效內容。")
                return "讓我們繼續探討這個概念。"
                
        except requests.exceptions.Timeout:
            logging.error("AI 模型回應超時。")
            return "抱歉，AI 模型回應超時了，請稍後再試。"
        except requests.exceptions.ConnectionError:
            logging.error("無法連接到 AI 模型服務。")
            return "抱歉，無法連接到 AI 模型服務，請檢查網路或服務是否運行。"
        except Exception as e:
            logging.error(f"調用 AI 時發生未預期錯誤: {e}", exc_info=True) # 打印完整的錯誤堆棧
            return f"請稍等，讓我重新思考一下。系統內部錯誤：{e}"
    
    def start_new_question(self, question: str) -> str:
        """開始新問題"""

        # 以下是處理正常教學問題的邏輯
        self.original_question = question
        self.context = "" # 開始新問題時清空上下文
        
        logging.info(f"開始新問題: {question}")
        self.topic_knowledge = self.get_topic_knowledge(question)
        
        response = self.ask_ai(question, is_new_question=True)
        
        self.context = f"學生問：{question}\n老師：{response}"
        
        return response
    
    def continue_conversation(self, student_answer: str) -> str:
        """繼續對話"""
        if not self.original_question:
            return "請先提出一個問題開始學習。"
        
        # 在繼續對話時，也要檢查是否為元問題（例如學生突然轉移話題問你是誰）
        meta_response = self.handle_meta_question(student_answer)
        if meta_response:
            # 如果是元問題，返回預設回應，並更新上下文
            self.context += f"\n\n學生：{student_answer}\n老師：{meta_response}"
            # 保持上下文在合理長度
            parts = self.context.split('\n\n')
            if len(parts) > 6: # 只保留最近3輪對話
                self.context = '\n\n'.join(parts[-6:])
            return meta_response

        logging.info(f"學生回答: {student_answer}")
        # 生成回應
        response = self.ask_ai(student_answer, is_new_question=False)
        
        # 更新上下文
        self.context += f"\n\n學生：{student_answer}\n老師：{response}"
        
        # 保持上下文在合理長度
        if len(self.context) > 1500:
            parts = self.context.split('\n\n')
            if len(parts) > 6:  # 3輪對話 = 6個部分
                self.context = '\n\n'.join(parts[-6:])
        
        return response
    
    def get_status(self) -> str:
        """獲取當前狀態"""
        return f"""
📊 學習狀態
AI模型: {config.AVAILABLE_AI_MODELS[self.ai_model_type]['name']}
原始問題: {self.original_question or '無'}
對話輪數: {self.context.count('學生：')}
上下文長度: {len(self.context)} 字符
"""
    
    def reset(self):
        """重置對話"""
        self.original_question = ""
        self.context = ""
        self.topic_knowledge = ""