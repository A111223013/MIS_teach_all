#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG智能教學系統 - 主程式
提供完整的互動式介面，支援PDF處理、知識庫建立和智能問答
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 導入核心模組
import config
from rag_processor import RAGProcessor
from rag_ai_responder import AIResponder

# 設定日誌
logging.basicConfig(
    level=getattr(logging, config.LOGGING_CONFIG['level']),
    format=config.LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

class RAGMainSystem:
    """
    RAG主系統 - 整合所有功能的主要介面

    功能包括:
    1. PDF教材批量處理
    2. 知識庫建立和管理
    3. 互動式智能問答
    4. 系統配置和狀態管理
    """

    def __init__(self):
        """初始化RAG主系統"""
        self.processor = None
        self.ai_responder = None
        self.conversation_history = []
        self.current_language = config.DEFAULT_LANGUAGE

        # 顯示歡迎資訊
        self._show_welcome()

        # 驗證配置
        if not config.validate_config():
            logger.error("❌ 配置驗證失敗，請檢查config.py")
            sys.exit(1)

    def _show_welcome(self):
        """顯示歡迎資訊"""
        welcome_text = f"""
{'='*80}
🎓 RAG智能教學系統 v1.0
{'='*80}

📚 功能特色：
• 批量處理PDF教材，自動建立知識庫
• 支援中英文雙語智能問答
• 結構化回答包含章節、知識點、頁碼參考
• 本地AI模型，保護資料隱私

🚀 快速開始：
1. 處理PDF教材 → 選項 1
2. 智能問答 → 選項 2
3. 系統設定 → 選項 3

💡 提示：首次使用請先處理PDF教材建立知識庫
{'='*80}
"""
        print(welcome_text)

    def run(self):
        """運行主程式"""
        try:
            while True:
                self._show_main_menu()
                choice = input("\n請選擇功能 (1-5): ").strip()

                if choice == '1':
                    self._handle_pdf_processing()
                elif choice == '2':
                    self._handle_unified_tutoring()
                elif choice == '3':
                    self._handle_system_settings()
                elif choice == '4':
                    self._handle_system_status()
                elif choice == '5':
                    self._handle_exit()
                    break
                else:
                    print("❌ 無效選擇，請輸入 1-5")

                input("\n按 Enter 繼續...")

        except KeyboardInterrupt:
            print("\n\n👋 感謝使用RAG智能教學系統！")
        except Exception as e:
            logger.error(f"❌ 系統運行錯誤: {e}")
            print(f"❌ 系統發生錯誤: {e}")

    def _handle_unified_tutoring(self):
        """處理多AI智能教學"""
        try:
            from multi_ai_learning import MultiAILearningSystem
            print("\n🎓 啟動多AI智能學習系統...")
            print("🤖 支援 Llama (本地) + Gemini (API)")
            print("🎯 真正老師風格，自然對話")
            print("🔄 可隨時切換AI模型")

            learning_system = MultiAILearningSystem()
            learning_system.run()

        except ImportError as e:
            print(f"❌ 多AI教學系統模組載入失敗: {e}")
            print("💡 請確認 multi_ai_tutor.py 和 multi_ai_learning.py 檔案存在")
            print("💡 請安裝 google-generativeai: pip install google-generativeai")
        except Exception as e:
            logger.error(f"❌ 多AI教學系統錯誤: {e}")
            print(f"❌ 多AI教學系統發生錯誤: {e}")
            print("💡 請檢查:")
            print("  1. Ollama是否運行: ollama serve (如果使用Llama)")
            print("  2. 網路連接是否正常 (如果使用Gemini)")
            print("  3. 向量資料庫是否建立")

    def _handle_exit(self):
        """處理退出"""
        print("\n👋 感謝使用RAG智能教學系統！")
        print("🎓 希望您學習愉快！")

    def _show_main_menu(self):
        """顯示主選單"""
        menu_text = f"""
🏠 主選單
{'='*50}
1. 📚 PDF教材處理 (建立知識庫)
2. 🎓 多AI智能學習 (Llama + Gemini)
3. ⚙️  系統設定
4. 📊 系統狀態
5. 🚪 退出系統

當前語言: {config.SUPPORTED_LANGUAGES[self.current_language]['name']}
"""
        print(menu_text)

    def _handle_pdf_processing(self):
        """處理PDF教材"""
        print("\n📚 PDF教材處理")
        print("="*50)

        # 檢查PDF目錄
        pdf_files = list(config.PDF_DIR.glob("*.pdf"))

        if not pdf_files:
            print(f"❌ 在 {config.PDF_DIR} 目錄中沒有找到PDF檔案")
            print(f"💡 請將PDF教材檔案放入 {config.PDF_DIR} 目錄")
            return

        print(f"📁 找到 {len(pdf_files)} 個PDF檔案:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file.name}")

        # 選擇處理方式
        print("\n處理選項:")
        print("1. 處理所有PDF檔案")
        print("2. 選擇特定檔案")
        print("3. 返回主選單")

        choice = input("\n請選擇 (1-3): ").strip()

        if choice == '1':
            selected_files = [str(f) for f in pdf_files]
        elif choice == '2':
            selected_files = self._select_pdf_files(pdf_files)
        elif choice == '3':
            return
        else:
            print("❌ 無效選擇")
            return

        if not selected_files:
            print("❌ 沒有選擇任何檔案")
            return

        # 開始處理
        self._process_pdfs(selected_files)

    def _select_pdf_files(self, pdf_files: List[Path]) -> List[str]:
        """選擇特定PDF檔案"""
        print("\n請輸入要處理的檔案編號 (用逗號分隔，例如: 1,3,5):")
        selection = input("檔案編號: ").strip()

        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_files = []

            for idx in indices:
                if 0 <= idx < len(pdf_files):
                    selected_files.append(str(pdf_files[idx]))
                else:
                    print(f"⚠️ 忽略無效編號: {idx + 1}")

            return selected_files

        except ValueError:
            print("❌ 輸入格式錯誤")
            return []

    def _process_pdfs(self, pdf_files: List[str]):
        """處理PDF檔案"""
        print(f"\n🔄 開始處理 {len(pdf_files)} 個PDF檔案...")

        try:
            # 初始化處理器
            if not self.processor:
                self.processor = RAGProcessor(verbose=True)

            # 處理PDF檔案
            success = self.processor.process_multiple_pdfs(pdf_files)

            if not success:
                print("❌ PDF處理失敗")
                return

            # 創建知識點
            print("\n🧠 正在創建知識點...")
            if not self.processor.create_knowledge_points():
                print("❌ 知識點創建失敗")
                return

            # 建立向量資料庫
            print("\n🔧 正在建立向量資料庫...")
            if not self.processor.build_knowledge_database():
                print("❌ 向量資料庫建立失敗")
                return

            # 保存知識點
            print("\n💾 正在保存知識點...")
            self.processor.save_knowledge_points()

            # 顯示處理摘要
            summary = self.processor.get_processing_summary()
            print(f"\n✅ 處理完成！")
            print(f"📊 處理摘要:")
            print(f"  • 結構化內容: {summary['structured_data_count']} 個")
            print(f"  • 知識點: {summary['knowledge_points_count']} 個")
            print(f"  • 向量模型: {summary['embedding_model']}")
            print(f"  • 資料庫類型: {summary['database_type']}")

        except Exception as e:
            logger.error(f"❌ PDF處理過程發生錯誤: {e}")
            print(f"❌ 處理失敗: {e}")

    def _handle_ai_qa(self):
        """處理智能問答"""
        print("\n🤖 智能問答系統")
        print("="*50)

        # 初始化AI回答系統
        if not self.ai_responder:
            try:
                self.ai_responder = AIResponder(
                    language=self.current_language,
                    rag_processor=self.processor
                )
            except Exception as e:
                print(f"❌ AI回答系統初始化失敗: {e}")
                return

        # 檢查系統狀態
        status = self.ai_responder.get_system_status()
        if not status['database_ready']:
            print("❌ 知識庫未準備就緒，請先處理PDF教材")
            return

        print("✅ AI問答系統已就緒")
        print(f"🌐 當前語言: {status['current_language']}")
        print(f"🤖 AI模型: {status['ai_model']} ({'可用' if status['ai_model_available'] else '不可用'})")

        # 開始問答對話
        self._start_qa_conversation()

    def _start_qa_conversation(self):
        """開始問答對話"""
        print(f"""
💬 問答對話已開始
{'='*30}
💡 使用提示:
• 直接輸入問題開始對話
• 輸入 'lang' 切換語言
• 輸入 'help' 查看幫助
• 輸入 'quit' 返回主選單

範例問題:
• "什麼是作業系統？"
• "進程和線程的區別"
• "virtual memory如何工作"
""")

        while True:
            try:
                question = input("\n🔍 請輸入您的問題: ").strip()

                if not question:
                    continue

                # 處理特殊命令
                if question.lower() == 'quit':
                    break
                elif question.lower() == 'lang':
                    self._change_language()
                    continue
                elif question.lower() == 'help':
                    self._show_qa_help()
                    continue

                # 生成回答
                print("\n⏳ 正在分析問題並搜索相關內容...")
                response = self.ai_responder.answer_question(question)

                # 顯示回答
                formatted_response = self.ai_responder.format_response_for_display(response)
                print(f"\n{formatted_response}")

                # 保存對話歷史
                self.conversation_history.append({
                    "question": question,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })

            except KeyboardInterrupt:
                print("\n\n返回主選單...")
                break
            except Exception as e:
                logger.error(f"❌ 問答過程發生錯誤: {e}")
                print(f"❌ 回答生成失敗: {e}")

    def _change_language(self):
        """切換語言"""
        print("\n🌐 語言設定")
        print("1. 中文")
        print("2. English")

        choice = input("請選擇語言 (1-2): ").strip()

        if choice == '1':
            new_language = 'chinese'
        elif choice == '2':
            new_language = 'english'
        else:
            print("❌ 無效選擇")
            return

        if self.ai_responder:
            if self.ai_responder.set_language(new_language):
                self.current_language = new_language
                print(f"✅ 語言已切換為: {config.SUPPORTED_LANGUAGES[new_language]['name']}")
            else:
                print("❌ 語言切換失敗")
        else:
            self.current_language = new_language
            print(f"✅ 語言已設定為: {config.SUPPORTED_LANGUAGES[new_language]['name']}")

    def _show_qa_help(self):
        """顯示問答幫助"""
        help_text = """
🆘 問答系統幫助
{'='*30}

📝 問題類型:
• 定義類: "什麼是...？", "定義..."
• 功能類: "...的功能是什麼？", "...有什麼作用？"
• 比較類: "...和...的區別？", "比較..."
• 原理類: "...如何工作？", "...的原理是什麼？"
• 應用類: "...的應用場景？", "...的例子？"

💡 提問技巧:
• 使用具體的技術術語
• 可以中英文混合提問
• 問題越詳細，回答越精確

🔍 範例問題:
• "什麼是死鎖？"
• "virtual memory management"
• "進程調度算法有哪些？"
• "file system structure"

⌨️ 特殊命令:
• 'lang' - 切換回答語言
• 'help' - 顯示此幫助
• 'quit' - 返回主選單
"""
        print(help_text)

    def _handle_system_settings(self):
        """處理系統設定"""
        print("\n⚙️ 系統設定")
        print("="*50)

        while True:
            print("\n設定選項:")
            print("1. 語言設定")
            print("2. 科目資訊設定")
            print("3. AI模型設定")
            print("4. 搜索參數設定")
            print("5. 查看當前配置")
            print("6. 返回主選單")

            choice = input("\n請選擇 (1-6): ").strip()

            if choice == '1':
                self._change_language()
            elif choice == '2':
                self._set_subject_info()
            elif choice == '3':
                self._set_ai_model()
            elif choice == '4':
                self._set_search_params()
            elif choice == '5':
                self._show_current_config()
            elif choice == '6':
                break
            else:
                print("❌ 無效選擇")

    def _set_subject_info(self):
        """設定科目資訊"""
        print("\n📚 科目資訊設定")
        print("="*30)

        current_info = self.ai_responder.subject_info if self.ai_responder else config.DEFAULT_SUBJECT_INFO

        print("當前科目資訊:")
        for key, value in current_info.items():
            print(f"  {key}: {value}")

        print("\n請輸入新的科目資訊 (直接按Enter保持原值):")

        new_info = {}
        for key, current_value in current_info.items():
            new_value = input(f"{key} [{current_value}]: ").strip()
            new_info[key] = new_value if new_value else current_value

        if self.ai_responder:
            self.ai_responder.set_subject_info(new_info)

        print("✅ 科目資訊已更新")

    def _set_ai_model(self):
        """設定AI模型"""
        print("\n🤖 AI模型設定")
        print("="*30)

        print(f"當前AI模型: {config.LOCAL_AI_MODEL}")
        print(f"當前基礎URL: {config.LOCAL_AI_BASE_URL}")

        new_model = input(f"新的AI模型名稱 [{config.LOCAL_AI_MODEL}]: ").strip()
        new_url = input(f"新的基礎URL [{config.LOCAL_AI_BASE_URL}]: ").strip()

        if new_model:
            config.LOCAL_AI_MODEL = new_model
        if new_url:
            config.LOCAL_AI_BASE_URL = new_url

        print("✅ AI模型設定已更新")
        print("💡 重新初始化AI回答系統以應用新設定")

    def _set_search_params(self):
        """設定搜索參數"""
        print("\n🔍 搜索參數設定")
        print("="*30)

        current_config = config.SEARCH_CONFIG
        print("當前搜索參數:")
        for key, value in current_config.items():
            print(f"  {key}: {value}")

        print("\n請輸入新的搜索參數 (直接按Enter保持原值):")

        try:
            new_top_k = input(f"預設返回結果數量 [{current_config['default_top_k']}]: ").strip()
            if new_top_k:
                config.SEARCH_CONFIG['default_top_k'] = int(new_top_k)

            new_threshold = input(f"相似度閾值 [{current_config['similarity_threshold']}]: ").strip()
            if new_threshold:
                config.SEARCH_CONFIG['similarity_threshold'] = float(new_threshold)

            print("✅ 搜索參數已更新")

        except ValueError:
            print("❌ 輸入格式錯誤")

    def _show_current_config(self):
        """顯示當前配置"""
        print("\n📋 當前系統配置")
        print("="*50)

        print(config.get_config_summary())

        if self.ai_responder:
            status = self.ai_responder.get_system_status()
            print(f"\n🤖 AI系統狀態:")
            print(f"  • AI回答系統: {'就緒' if status['ai_responder_ready'] else '未就緒'}")
            print(f"  • 當前語言: {status['current_language']}")
            print(f"  • AI模型: {status['ai_model']}")
            print(f"  • 向量模型: {status['embedding_model']}")
            print(f"  • 資料庫狀態: {'就緒' if status['database_ready'] else '未就緒'}")
            print(f"  • AI模型可用性: {'可用' if status['ai_model_available'] else '不可用'}")

    def _handle_system_status(self):
        """處理系統狀態"""
        print("\n📊 系統狀態")
        print("="*50)

        # 基本系統資訊
        print("🖥️ 基本資訊:")
        print(f"  • Python版本: {sys.version.split()[0]}")
        print(f"  • 工作目錄: {os.getcwd()}")
        print(f"  • 配置檔案: {'有效' if config.validate_config() else '無效'}")

        # 資料目錄狀態
        print(f"\n📁 資料目錄:")
        print(f"  • PDF目錄: {config.PDF_DIR} ({'存在' if config.PDF_DIR.exists() else '不存在'})")
        print(f"  • 知識庫目錄: {config.KNOWLEDGE_DB_DIR} ({'存在' if config.KNOWLEDGE_DB_DIR.exists() else '不存在'})")
        print(f"  • 輸出目錄: {config.OUTPUT_DIR} ({'存在' if config.OUTPUT_DIR.exists() else '不存在'})")

        # PDF檔案統計
        pdf_files = list(config.PDF_DIR.glob("*.pdf")) if config.PDF_DIR.exists() else []
        print(f"  • PDF檔案數量: {len(pdf_files)}")

        # 處理器狀態
        print(f"\n🔧 處理器狀態:")
        if self.processor:
            summary = self.processor.get_processing_summary()
            print(f"  • RAG處理器: 已初始化")
            print(f"  • 結構化數據: {summary['structured_data_count']} 個")
            print(f"  • 知識點: {summary['knowledge_points_count']} 個")
            print(f"  • 向量模型: {summary['embedding_model']}")
        else:
            print(f"  • RAG處理器: 未初始化")

        # AI回答系統狀態
        print(f"\n🤖 AI回答系統:")
        if self.ai_responder:
            status = self.ai_responder.get_system_status()
            print(f"  • 系統狀態: {'就緒' if status['ai_responder_ready'] else '未就緒'}")
            print(f"  • 當前語言: {status['current_language']}")
            print(f"  • AI模型: {status['ai_model']}")
            print(f"  • 模型可用性: {'可用' if status['ai_model_available'] else '不可用'}")
            print(f"  • 資料庫狀態: {'就緒' if status['database_ready'] else '未就緒'}")
        else:
            print(f"  • AI回答系統: 未初始化")

        # 對話歷史
        print(f"\n💬 對話統計:")
        print(f"  • 對話次數: {len(self.conversation_history)}")
        if self.conversation_history:
            latest = self.conversation_history[-1]
            print(f"  • 最近對話: {latest['timestamp']}")

    def _handle_exit(self):
        """處理退出"""
        print("\n🚪 正在退出系統...")

        # 保存對話歷史
        if self.conversation_history:
            try:
                history_file = config.OUTPUT_DIR / config.OUTPUT_FILES['conversation_history']
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
                print(f"💾 對話歷史已保存到: {history_file}")
            except Exception as e:
                logger.error(f"❌ 保存對話歷史失敗: {e}")

        print("👋 感謝使用RAG智能教學系統！")

def main():
    """主函數"""
    try:
        # 創建並運行主系統
        system = RAGMainSystem()
        system.run()

    except Exception as e:
        logger.error(f"❌ 系統啟動失敗: {e}")
        print(f"❌ 系統啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
