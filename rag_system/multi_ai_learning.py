#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支援多AI模型選擇的學習系統
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from multi_ai_tutor import MultiAITutor
import config

class MultiAILearningSystem:
    """支援多AI模型的學習系統"""
    
    def __init__(self):
        """初始化系統"""
        self.tutor = None
        self.in_conversation = False
        self.current_ai_model = None
        
    def show_welcome(self):
        """顯示歡迎訊息"""
        print("="*80)
        print("🎓 多AI智能學習系統")
        print("="*80)
        print()
        print("🤖 可用AI模型：")
        for key, model_info in config.AVAILABLE_AI_MODELS.items():
            print(f"  • {model_info['name']}: {model_info['description']}")
        print()
        print("🌟 系統特色：")
        print("  • 🎓 支援多種AI模型選擇")
        print("  • 📝 真正老師風格，親切自然")
        print("  • 💡 針對性引導，推進理解")
        print("  • 🎯 始終記住原始問題")
        print("  • 🔄 可隨時切換AI模型")
        print()
        print("💡 使用說明：")
        print("  • 先選擇AI模型")
        print("  • 直接提問開始學習")
        print("  • 積極回答老師的引導問題")
        print("  • 輸入 'switch' 切換AI模型")
        print("  • 輸入 'new' 開始新問題")
        print("  • 輸入 'quit' 退出系統")
        print()
        print("🎯 設計理念：多AI模型，自由選擇")
        print("="*80)
    
    def select_ai_model(self):
        """選擇AI模型"""
        print("\n🤖 請選擇AI模型：")
        print("-" * 40)
        
        models = list(config.AVAILABLE_AI_MODELS.keys())
        for i, (key, model_info) in enumerate(config.AVAILABLE_AI_MODELS.items(), 1):
            print(f"{i}. {model_info['name']}")
            print(f"   {model_info['description']}")
            print()
        
        while True:
            try:
                choice = input("請選擇 (1-2): ").strip()
                if choice in ['1', '2']:
                    selected_model = models[int(choice) - 1]
                    self.current_ai_model = selected_model
                    self.tutor = MultiAITutor(ai_model=selected_model)
                    print(f"\n✅ 已選擇: {config.AVAILABLE_AI_MODELS[selected_model]['name']}")
                    return True
                else:
                    print("❌ 請輸入 1 或 2")
            except (ValueError, IndexError):
                print("❌ 請輸入有效的選項")
            except KeyboardInterrupt:
                return False
    
    def handle_special_commands(self, user_input: str) -> bool:
        """處理特殊命令"""
        user_input = user_input.lower().strip()
        
        if user_input in ['quit', 'exit', '退出', '結束']:
            print("\n👋 感謝使用多AI學習系統！")
            return True
        
        elif user_input in ['switch', '切換', '換模型']:
            print("\n🔄 切換AI模型...")
            if self.select_ai_model():
                self.in_conversation = False
                print("🆕 請提出新的問題開始學習：")
            return False
        
        elif user_input in ['new', '新問題', '新主題', 'reset']:
            if self.tutor:
                self.tutor.reset()
                self.in_conversation = False
                print("\n🆕 已重置，請提出新的問題：")
            else:
                print("💡 請先選擇AI模型")
            return False
        
        elif user_input in ['status', '狀態', '進度']:
            if self.tutor:
                status = self.tutor.get_status()
                print(f"\n{status}")
            else:
                print("💡 請先選擇AI模型")
            return False
        
        elif user_input in ['help', '幫助', '說明']:
            self.show_help()
            return False
        
        return False
    
    def show_help(self):
        """顯示幫助訊息"""
        print("\n📚 系統使用說明")
        print("-" * 50)
        print("🎯 學習命令：")
        print("  • 直接提問 - 開始新的學習主題")
        print("  • 回答問題 - 在引導過程中回答老師提問")
        print("  • new/新問題 - 開始新的學習主題")
        print()
        print("🤖 AI模型命令：")
        print("  • switch/切換 - 切換AI模型")
        print("  • status/狀態 - 查看學習狀態")
        print()
        print("🔧 系統命令：")
        print("  • help/幫助 - 顯示此說明")
        print("  • quit/退出 - 退出系統")
        print()
        print("💡 AI模型比較：")
        print("  • Llama (本地) - 隱私性好，無需網路，回應穩定")
        print("  • Gemini (API) - 功能強大，理解能力強，需要網路")
    
    def detect_input_type(self, user_input: str) -> str:
        """檢測輸入類型"""
        # 如果不在對話中，一定是新問題
        if not self.in_conversation:
            return "new_question"
        
        # 在對話中，檢查是否是新問題
        new_question_patterns = [
            "什麼是", "為什麼", "如何", "怎麼", "請解釋", "請說明",
            "能否", "可以", "告訴我", "我想知道", "什麼叫"
        ]
        
        if any(pattern in user_input for pattern in new_question_patterns):
            return "new_question"
        
        return "answer"
    
    def run(self):
        """運行學習系統"""
        self.show_welcome()
        
        # 首先選擇AI模型
        if not self.select_ai_model():
            return
        
        while True:
            try:
                # 根據狀態顯示提示
                if self.in_conversation:
                    prompt = "\n💭 您的回答: "
                else:
                    prompt = "\n🤔 請提出您的問題: "
                
                user_input = input(prompt).strip()
                
                if not user_input:
                    print("💡 請輸入您的問題或回答。")
                    continue
                
                # 處理特殊命令
                if self.handle_special_commands(user_input):
                    break
                
                # 確保已選擇AI模型
                if not self.tutor:
                    print("💡 請先選擇AI模型")
                    continue
                
                # 檢測輸入類型
                input_type = self.detect_input_type(user_input)
                
                if input_type == "new_question":
                    # 新問題
                    if self.in_conversation:
                        # 如果在對話中提新問題，先重置
                        self.tutor.reset()
                    
                    print(f"\n🎓 老師回應 ({config.AVAILABLE_AI_MODELS[self.current_ai_model]['name']})：")
                    response = self.tutor.start_new_question(user_input)
                    print(response)
                    
                    self.in_conversation = True
                
                else:
                    # 學生回答
                    if self.in_conversation:
                        print(f"\n🎓 老師回應 ({config.AVAILABLE_AI_MODELS[self.current_ai_model]['name']})：")
                        response = self.tutor.continue_conversation(user_input)
                        print(response)
                    else:
                        print("💡 請先提出一個問題開始學習，或輸入 'help' 查看說明。")
                
            except KeyboardInterrupt:
                print("\n\n👋 感謝使用多AI學習系統！")
                break
            except Exception as e:
                print(f"\n❌ 系統錯誤: {e}")
                print("💡 請重新輸入您的問題。")

def main():
    """主函數"""
    try:
        learning_system = MultiAILearningSystem()
        learning_system.run()
    except Exception as e:
        print(f"❌ 系統啟動失敗: {e}")
        print("💡 請檢查:")
        print("  1. Ollama是否運行: ollama serve (如果使用Llama)")
        print("  2. 網路連接是否正常 (如果使用Gemini)")
        print("  3. API金鑰是否有效 (如果使用Gemini)")

if __name__ == "__main__":
    main()
