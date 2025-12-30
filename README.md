# MIS_Teach 智慧學習平台

## 📚 專案簡介

MIS_Teach 是一個整合 AI 技術的智慧學習平台，專為資訊管理相關學科設計。系統結合了前端 Web 應用、後端 API 服務、YOLO 圖像識別、OCR 文字識別等多個子系統，提供完整的學習、測驗、分析、教學功能。

### 核心特色

- 🤖 **AI 輔助教學**: 整合 Google Gemini AI，提供五階段學習流程
- 📝 **多題型測驗系統**: 支援單選、多選、填空、簡答、畫圖、程式等 10+ 種題型
- 📊 **學習分析**: 完整的學習數據分析與弱點診斷
- 🔍 **RAG 知識檢索**: 基於 ChromaDB 的向量檢索增強生成
- 📸 **試卷數位化**: YOLO + OCR 自動處理試卷圖片
- 📱 **多平台支援**: Web 前端、LINE Bot 整合
- 📚 **教材管理**: Markdown 格式教材瀏覽與管理

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                        前端系統 (Angular)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 測驗系統  │  │ AI教學   │  │ 學習分析  │  │ 教材管理  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────┴──────────────────────────────────────┐
│                   後端系統 (Flask)                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 測驗API   │  │ AI教學API │  │ 學習分析  │  │ RAG系統  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  MySQL   │  │ MongoDB  │  │  Redis   │  │  Neo4j   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│              試卷處理流程                                        │
│                                                               │
│  試卷圖片 ──→ YOLO切割 ──→ OCR識別 ──→ AI分析 ──→ 資料庫      │
│     │            │            │          │           │        │
│     │         (yolo/)     (ocr/)    (Gemini)   (MongoDB)    │
└───────────────────────────────────────────────────────────────┘
```

## 📦 專案結構

```
MIS_teach_all/
├── frontend/              # Angular 前端應用
│   ├── src/              # 源代碼
│   │   ├── app/         # Angular 組件與服務
│   │   │   ├── views/   # 視圖組件
│   │   │   │   ├── dashboard/  # 儀表板頁面
│   │   │   │   │   ├── quiz-center/      # 測驗中心
│   │   │   │   │   ├── quiz-taking/      # 測驗作答
│   │   │   │   │   ├── quiz-result/      # 測驗結果
│   │   │   │   │   ├── ai-tutoring/       # AI 教學
│   │   │   │   │   ├── learning-analytics/ # 學習分析
│   │   │   │   │   └── ...
│   │   │   │   └── login/                # 登入頁面
│   │   │   └── service/  # 服務層
│   │   └── environments/ # 環境配置
│   └── README.md         # 前端說明文檔
│
├── backend/              # Flask 後端服務
│   ├── src/              # 業務邏輯
│   │   ├── quiz.py       # 測驗 API
│   │   ├── ai_teacher.py # AI 教學 API
│   │   ├── learning_analytics.py # 學習分析
│   │   ├── rag_sys/      # RAG 系統
│   │   └── ...
│   ├── tool/             # 工具腳本
│   │   ├── insert_mongodb.py      # 資料插入
│   │   ├── insert_test_school.py  # 測試資料
│   │   └── ...
│   ├── data/             # 資料目錄
│   │   └── materials/    # Markdown 教材
│   └── README.md         # 後端說明文檔
│
├── yolo/                 # YOLO 試卷切割系統
│   ├── train.py          # 模型訓練
│   ├── test.py           # 模型測試
│   ├── cut_exam_png.py   # 試卷切割
│   ├── test_dataset6/    # 訓練資料集
│   └── README.md         # YOLO 說明文檔
│
├── ocr/                  # OCR 文字識別系統
│   ├── ocr.py            # 主程式
│   ├── read.py           # 題目讀取
│   ├── gemini.py         # Gemini AI 整合
│   ├── flet_ui.py        # GUI 介面
│   ├── exam_img/         # 試卷圖片
│   └── README.md         # OCR 說明文檔
│
└── README.md             # 本文件（專案總體說明）
```

## 🚀 快速開始

### 前置需求

#### 系統需求
- **作業系統**: Windows 10+, Linux, macOS
- **Python**: 3.11+
- **Node.js**: >= 18.19.0 或 >= 20.9.0
- **npm**: >= 9

#### 資料庫與服務
- **MySQL**: 8.0+
- **MongoDB**: 6.0+
- **Redis**: 6.0+
- **Neo4j**: 5.0+ (可選，用於知識圖譜)

#### 外部服務
- **Google Gemini API**: 用於 AI 功能
- **Tesseract OCR**: 用於文字識別（OCR 系統需要）

### 安裝步驟

#### 1. 克隆專案

```bash
git clone <repository-url>
cd MIS_teach_all
```

#### 2. 後端設置

```bash
# 進入後端目錄
cd backend

# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 配置環境變數
# 複製並編輯 config.py，設定資料庫連線資訊
# 設定 api.env，配置 Google Gemini API 金鑰

# 初始化資料庫
python -c "from app import app, sqldb; from src.quiz import init_quiz_tables; from src.dashboard import init_calendar_tables; app.app_context().push(); init_quiz_tables(); init_calendar_tables()"

# 插入初始資料
python tool/insert_mongodb.py
python tool/insert_test_school.py
```

#### 3. 前端設置

```bash
# 進入前端目錄
cd frontend

# 安裝依賴
npm install

# 配置環境變數
# 編輯 src/environments/environment.dev.ts
# 設定後端 API URL
```

#### 4. YOLO 系統設置（可選）

```bash
# 進入 YOLO 目錄
cd yolo

# 創建虛擬環境
python -m venv yolov8-venv

# 啟動虛擬環境
yolov8-venv\Scripts\activate  # Windows
source yolov8-venv/bin/activate  # Linux/Mac

# 安裝依賴
pip install -r requirements.txt
pip install ultralytics
```

#### 5. OCR 系統設置（可選）

```bash
# 進入 OCR 目錄
cd ocr

# 安裝 Tesseract OCR
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract

# 創建虛擬環境
python -m venv ocr_venv

# 啟動虛擬環境
ocr_venv\Scripts\activate  # Windows
source ocr_venv/bin/activate  # Linux/Mac

# 安裝依賴
pip install -r requirements.txt
```

### 啟動系統

#### 啟動後端

```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 開發模式
python app.py

# 或使用 Flask CLI
flask run

# 生產模式（使用 Gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

後端預設運行在 `http://localhost:5000`

#### 啟動前端

```bash
cd frontend

# 開發模式
npm start
# 或
ng serve -o

# 生產構建
npm run build
```

前端預設運行在 `http://localhost:4200`

## 📖 使用指南

### 基本使用流程

#### 1. 使用者註冊與登入

1. 訪問前端應用 `http://localhost:4200`
2. 點擊「註冊」創建帳號
3. 檢查郵件完成驗證
4. 使用帳號密碼登入

#### 2. 進行測驗

1. 登入後進入「測驗中心」
2. 選擇測驗類型：
   - **知識測驗**: 從題庫中選擇題目
   - **歷屆試題**: 選擇學校、年份、系所
   - **AI 生成測驗**: 輸入概念，AI 自動生成題目
3. 設定測驗參數（題數、難度、領域等）
4. 開始測驗並作答
5. 提交後查看結果與分析

#### 3. AI 教學

1. 進入「AI 教學」頁面
2. 選擇或輸入要學習的概念
3. 系統會引導您完成五階段學習：
   - **核心概念確認**: 確認基礎理解
   - **相關概念引導**: 擴展相關知識
   - **應用理解**: 實際應用練習
   - **理解驗證**: 反向教學測試
   - **完成**: 學習完成
4. 可隨時查看筆記和學習進度

#### 4. 查看學習分析

1. 進入「學習分析」頁面
2. 查看學習趨勢圖表
3. 檢視弱點分析與建議
4. 使用 AI 診斷功能獲取個性化建議
5. 查看學習路徑推薦

#### 5. 瀏覽教材

1. 進入「教材」頁面
2. 選擇課程類別
3. 瀏覽 Markdown 格式教材
4. 使用搜尋功能查找特定內容

### 試卷處理流程（管理員）

#### 1. 使用 YOLO 切割試卷

```bash
cd yolo
python cut_exam_png.py
```

#### 2. 使用 OCR 識別文字

```bash
cd ocr
python ocr.py --gui  # GUI 模式
# 或
python ocr.py --print  # 命令行模式
```

#### 3. 上傳到資料庫

使用後端工具腳本將處理後的資料上傳到 MongoDB。

## 🔧 系統整合說明

### 前端與後端整合

- **通訊方式**: HTTP REST API
- **認證機制**: JWT Token
- **API 基礎 URL**: 在 `frontend/src/environments/environment.dev.ts` 中配置
- **CORS**: 後端已配置支援 localhost 和 ngrok 域名

### YOLO 與 OCR 整合

1. **YOLO 切割**: 使用訓練好的 YOLO 模型識別並切割試卷中的題目區域
2. **OCR 識別**: 對切割後的題目圖片進行 OCR 文字識別
3. **AI 分析**: 使用 Gemini AI 分析題目內容
4. **資料入庫**: 將處理後的資料存入 MongoDB

### RAG 系統整合

- **知識庫建構**: 使用 ChromaDB 儲存向量嵌入
- **PDF 處理**: 自動解析 PDF 教材並建立索引
- **語義檢索**: 在 AI 教學中使用 RAG 檢索相關知識
- **知識圖譜**: 使用 Neo4j 建立概念關聯（可選）

## 📚 詳細文檔

各子系統的詳細文檔請參考：

- [前端系統文檔](frontend/README.md) - Angular 前端開發指南
- [後端系統文檔](backend/README.md) - Flask 後端 API 文檔
- [YOLO 系統文檔](yolo/README.md) - 試卷切割系統說明
- [OCR 系統文檔](ocr/README.md) - 文字識別系統說明

## 🔌 API 端點總覽

### 身份驗證
- `POST /login` - 使用者登入
- `POST /register` - 使用者註冊
- `POST /login/logout` - 登出

### 測驗相關
- `POST /quiz/generate` - 生成測驗
- `POST /quiz/submit` - 提交測驗
- `GET /quiz/result/<quiz_id>` - 查詢測驗結果
- `POST /ai_quiz/generate` - AI 生成測驗

### AI 教學
- `POST /ai_teacher/chat` - AI 教學對話
- `GET /ai_teacher/session/<session_id>` - 查詢學習會話
- `POST /ai_teacher/start` - 開始學習會話

### 學習分析
- `GET /api/learning-analytics/overview` - 學習總覽
- `GET /api/learning-analytics/trends` - 學習趨勢
- `GET /api/learning-analytics/weak-points` - 弱點分析
- `POST /api/learning-analytics/ai-diagnosis` - AI 診斷

### 教材管理
- `GET /materials/list` - 教材列表
- `GET /materials/<filename>` - 教材內容

### 其他
- `GET /dashboard/user-info` - 使用者資訊
- `GET /api/news` - 新聞列表
- `POST /note` - 創建筆記
- `GET /note` - 查詢筆記

詳細 API 文檔請參考 [後端文檔](backend/README.md#api-文檔)。

## 🛠️ 開發指南

### 開發環境設置

1. **IDE 推薦**: 
   - VS Code（推薦，支援 Python 和 TypeScript）
   - PyCharm（Python 開發）
   - WebStorm（前端開發）

2. **版本控制**: Git
   - 使用 Git Flow 工作流程
   - 提交訊息遵循 Conventional Commits

3. **程式碼風格**:
   - **Python**: PEP 8，使用 `black` 格式化
   - **TypeScript**: Angular 風格指南，使用 Prettier
   - **HTML/CSS**: 使用 Prettier 和 ESLint

4. **推薦 VS Code 擴充功能**:
   - Python
   - Angular Language Service
   - ESLint
   - Prettier
   - GitLens
   - REST Client（API 測試）

### 資料庫管理

#### MySQL 操作

```bash
# 連線 MySQL
mysql -u root -p

# 使用資料庫
USE mis_teach;

# 查看資料表
SHOW TABLES;
```

#### MongoDB 操作

```bash
# 連線 MongoDB
mongo

# 使用資料庫
use MIS_Teach

# 查看集合
show collections

# 查詢題目
db.exam.find().limit(10)
```

#### Redis 操作

```bash
# 連線 Redis
redis-cli

# 查看所有鍵
KEYS *

# 查看特定鍵的值
GET <key>
```

### API 測試

#### 使用 curl

```bash
# 1. 登入獲取 Token
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# 回應範例：
# {"access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...", "refresh_token": "..."}

# 2. 使用 Token 訪問受保護的 API
curl -X GET http://localhost:5000/quiz/generate \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"template_id": "123", "count": 20}'

# 3. 提交測驗
curl -X POST http://localhost:5000/quiz/submit \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": "quiz_123",
    "answers": {
      "1": "A",
      "2": ["A", "B"],
      "3": "答案內容"
    }
  }'
```

#### 使用 Postman

1. 建立新的 Collection: "MIS_Teach API"
2. 設定環境變數：
   - `base_url`: `http://localhost:5000`
   - `token`: (登入後自動設定)
3. 建立請求：
   - 登入請求 → 使用 Tests 腳本自動儲存 Token
   - 其他請求 → 使用 `{{token}}` 變數

#### 使用 VS Code REST Client

建立 `api-test.http` 檔案：

```http
### 登入
POST http://localhost:5000/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}

### 獲取測驗
GET http://localhost:5000/quiz/generate?template_id=123&count=20
Authorization: Bearer {{token}}
```

### 除錯技巧

1. **後端除錯**: 使用 Flask 的 debug mode，查看詳細錯誤訊息
2. **前端除錯**: 使用瀏覽器開發者工具，查看 Console 和 Network
3. **資料庫除錯**: 檢查 SQL 查詢日誌和 MongoDB 操作日誌
4. **API 除錯**: 使用 Postman 測試 API，檢查請求和回應

## ❓ 常見問題

### 1. 後端無法啟動

**問題**: 資料庫連線失敗

**解決方案**:
- 檢查 MySQL、MongoDB、Redis 服務是否啟動
- 確認 `config.py` 中的連線資訊正確
- 檢查防火牆設定

### 2. 前端無法連接到後端

**問題**: CORS 錯誤或連線失敗

**解決方案**:
- 確認後端服務正在運行
- 檢查 `environment.dev.ts` 中的 API URL 設定
- 確認後端 CORS 配置正確

### 3. Token 刷新失敗

**問題**: "Token refresh failed: Invalid header padding"

**解決方案**:
- 清除瀏覽器 localStorage
- 重新登入獲取新 Token
- 檢查後端 Token 驗證邏輯

### 4. OCR 識別率低

**問題**: 文字識別不準確

**解決方案**:
- 提高圖片解析度
- 進行圖像預處理（去噪、對比度調整）
- 使用適當的 Tesseract 語言包

### 5. YOLO 檢測不準確

**問題**: 題目區域識別錯誤

**解決方案**:
- 增加訓練資料
- 調整模型參數
- 檢查標註品質

## 🔐 安全注意事項

1. **API 金鑰**: 不要將 API 金鑰提交到版本控制系統
2. **資料庫密碼**: 使用環境變數管理敏感資訊
3. **JWT Secret**: 確保安全密鑰足夠複雜
4. **CORS**: 生產環境中限制允許的來源域名
5. **輸入驗證**: 所有使用者輸入都應進行驗證和清理

## 📈 效能優化

### 後端優化

- **快取策略**: 使用 Redis 快取常用資料（題目列表、使用者資訊等）
- **資料庫優化**: 
  - 建立適當的索引
  - 使用連線池
  - 優化查詢語句
- **API 優化**:
  - 回應壓縮（gzip）
  - 分頁處理大量資料
  - 非同步處理長時間任務（Celery）
- **記憶體管理**: 及時釋放不需要的資源

### 前端優化

- **程式碼優化**:
  - 程式碼分割與懶加載
  - Tree-shaking 移除未使用程式碼
  - 使用 OnPush 變更檢測策略
- **資源優化**:
  - 圖片壓縮與 WebP 格式
  - CDN 加速靜態資源
  - 字體子集化
- **快取策略**:
  - HTTP 快取
  - Service Worker（PWA）
  - LocalStorage 快取
- **渲染優化**:
  - 虛擬滾動（長列表）
  - 防抖與節流
  - 圖片懶加載

### 資料庫優化建議

#### MySQL
```sql
-- 建立索引範例
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_quiz_user_id ON quizzes(user_id);
CREATE INDEX idx_answer_quiz_id ON answers(quiz_id);
```

#### MongoDB
```javascript
// 建立索引
db.exam.createIndex({ "school": 1, "year": 1, "department": 1 });
db.exam.createIndex({ "answer_type": 1 });
db.exam.createIndex({ "question_text": "text" }); // 全文索引
```

## 🗺️ 未來規劃

### 短期目標

- [ ] 完善單元測試覆蓋率
- [ ] 優化 API 回應時間
- [ ] 改進 UI/UX 設計
- [ ] 增加更多題型支援

### 中期目標

- [ ] PWA 支援（離線功能）
- [ ] 多語言支援
- [ ] 深色模式
- [ ] 行動應用（React Native）

### 長期目標

- [ ] 微服務架構重構
- [ ] 容器化部署（Docker/Kubernetes）
- [ ] GraphQL API
- [ ] 即時通訊（WebSocket）
- [ ] 機器學習模型優化

## 📝 更新日誌

### v1.0.0 (2024)

#### 新增功能
- ✅ 完整的測驗系統（10+ 種題型）
- ✅ AI 輔助教學（五階段學習流程）
- ✅ 學習分析與弱點診斷
- ✅ RAG 知識檢索系統
- ✅ YOLO 試卷切割
- ✅ OCR 文字識別
- ✅ LINE Bot 整合
- ✅ 教材管理系統
- ✅ 學習行事曆

#### 技術改進
- ✅ JWT 認證機制
- ✅ 多資料庫整合（MySQL, MongoDB, Redis, Neo4j）
- ✅ CORS 動態配置
- ✅ LaTeX 數學公式渲染
- ✅ Canvas 繪圖功能
- ✅ 響應式設計

#### 已知問題
- ⚠️ Neo4j 知識圖譜功能為可選，需要額外配置
- ⚠️ OCR 識別率依圖片品質而定
- ⚠️ YOLO 模型需要定期重新訓練以提升準確率

## 👥 貢獻指南

歡迎貢獻！請遵循以下步驟：

### 貢獻流程

1. **Fork 專案**: 在 GitHub 上 Fork 本專案
2. **創建分支**: 
   ```bash
   git checkout -b feature/AmazingFeature
   # 或
   git checkout -b fix/BugFix
   ```
3. **開發與測試**: 
   - 編寫程式碼
   - 確保通過現有測試
   - 添加新測試（如需要）
4. **提交更改**: 
   ```bash
   git commit -m 'feat: Add some AmazingFeature'
   # 或
   git commit -m 'fix: Fix some bug'
   ```
5. **推送分支**: 
   ```bash
   git push origin feature/AmazingFeature
   ```
6. **開啟 Pull Request**: 在 GitHub 上開啟 PR，描述變更內容

### 提交訊息規範

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文檔變更
- `style`: 程式碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 構建過程或輔助工具的變動

範例：
```
feat(quiz): Add support for drawing questions
fix(auth): Fix token refresh issue
docs(readme): Update installation instructions
```

### 程式碼審查

- 所有 PR 都需要通過程式碼審查
- 確保程式碼符合專案風格指南
- 添加適當的註解和文檔
- 確保沒有破壞性變更（或明確標註）

## 📄 授權

本專案採用 MIT License 授權。

## 📧 聯絡資訊

如有問題或建議，請聯繫開發團隊或提交 Issue。

---

**MIS_Teach 智慧學習平台** - 讓學習更智慧、更有效率！

