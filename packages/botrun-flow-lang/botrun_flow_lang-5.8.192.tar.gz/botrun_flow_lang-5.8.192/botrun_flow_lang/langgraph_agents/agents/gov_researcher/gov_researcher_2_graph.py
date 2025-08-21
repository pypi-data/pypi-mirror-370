"""
台灣政府津貼補助 AI 專家：單一 Agent + 多工具架構實作

基於 LangGraph create_react_agent 的中央化 Prompt 管理架構，
專門用於台灣政府津貼補助諮詢服務。

Author: Generated with Claude Code
Date: 2025-01-28
"""

from datetime import datetime
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import uuid

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
import pytz

# 重用現有的搜尋功能
from botrun_flow_lang.langgraph_agents.agents.util.perplexity_search import (
    respond_with_perplexity_search,
)
from botrun_flow_lang.langgraph_agents.agents.util.tavily_search import (
    respond_with_tavily_search,
)
from botrun_flow_lang.langgraph_agents.agents.util.model_utils import (
    get_model_instance,
)
from botrun_flow_lang.langgraph_agents.agents.util.local_files import (
    generate_tmp_text_file,
    read_tmp_text_file,
)

from dotenv import load_dotenv

load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ============================================================================
# 全域模型設定 - 統一使用 Gemini 系列
# ============================================================================
DEFAULT_MODEL_NAME = "gemini-2.5-pro"
model = ChatGoogleGenerativeAI(
    model=DEFAULT_MODEL_NAME,
    temperature=0,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)

# if os.getenv("OPENROUTER_API_KEY") and os.getenv("OPENROUTER_BASE_URL"):
#     openrouter_model_name = "anthropic/claude-sonnet-4"
#     model = ChatOpenAI(
#         openai_api_key=os.getenv("OPENROUTER_API_KEY"),
#         openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
#         model_name=openrouter_model_name,
#         temperature=0,
#         max_tokens=64000,
#     )
# else:
#     model = ChatAnthropic(
#         model="claude-sonnet-4-20250514",
#         temperature=0,
#         max_tokens=64000,
#     )
# ============================================================================
# 提取文件的預設 Prompt 常數
# ============================================================================
LEGAL_EXTRACTION_PROMPT = """請詳細提取所有法律條文、法規、辦法、要點，格式：
- 你只會去除不重要的內容，但是你不會修改已經出現的內容
- 研究資料內容如果有表格，或是特殊格式，你會完整留存
```
# 相關法條彙整

## [法規名稱1]
[具體條文內容]
[適用說明]
**參考來源**: [該法條的官方網址]

## [法規名稱2]
[具體條文內容]
[適用說明]
**參考來源**: [該法條的官方網址]

```

研究資料內容：
{research_data}"""

FAQ_EXTRACTION_PROMPT = """如果內容中，有包含FAQ、常見問題、問答集，你會詳細記錄起來：
- 你只會去除不重要的內容，但是你不會修改已經出現的內容
- 研究資料內容如果有表格，或是特殊格式，你會完整留存
- 如果研究資料內容沒有特別包含FAQ、常見問題、問答集，你不需要自行產生內容，直接回傳"內容中沒有包含相關資訊"
```
# 常見問題彙整

## Q1: [問題]
A1: [回答]
**參考來源**: [該FAQ的官方網址]

## Q2: [問題]
A2: [回答]
**參考來源**: [該FAQ的官方網址]

```

研究資料內容：
{research_data}"""

CALCULATION_ANALYSIS_PROMPT = """今天的日期是 {current_date}
你是專業的津貼計算分析專家，你會從<使用者的原始提問>，以及<研究資料>中獲取資料，然後遵守 <四個步驟的分析>的方式，進行計算分析。請 step by step 完成精準計算和小心驗算。

<使用者的原始提問>
{user_input}
</使用者的原始提問>

<研究資料>
{research_data}
</研究資料>

<四個步驟的分析>
## Step001: 補助項目識別與分類
1. 將所有可申請補助按性質分類（生活津貼、醫療補助、教育補助、就業補助等）
2. 標記每項補助的法源依據、主管機關、申請期限
3. 辨識補助金額計算方式（例如：定額補助/補助的比例/補助級距）
4. 辨識補助金額的時間區間，例如：110-111年是補助XXXX金額，112-113年是補助YYYY金額，依此類推
5. 看清楚「年齡分流」準則，標記出不同年齡區塊中申請和流程的差異
6. **重要時間計算**：確定現在時間並理解時間定向
   - 記住西元2025年就是民國114年，以此類推
   - 使用者提問的時間定向：若使用者說1/1，代表是今年的1/1（除非特別說明去年、兩年前等）
7. 不同的補助，可能有不同的天數，也可能有相同的天數，要仔細查核

## Step002: 排斥條件深度檢查
1. 檢查「擇一申請」限制（如：不得同時領取A、B補助）
2. 分析「所得替代」關係（如：領取失業給付期間不得申請其他就業補助）
3. 確認「重複給付禁止」條款
4. 檢視「資格互斥」情況（如：某些補助限制已領取其他特定補助者）
5. 標示推薦申請順序與說明理由

## Step003: 多重身份優化計算
1. 列出使用者所有符合身份（身障、中低收、原住民、高齡等）
2. 計算各身份單獨申請vs.組合申請的總金額
3. 分析身份疊加的加成效果或限制（注意：需先用身份判定完正確的基礎級距，再計算加成效果）
4. 提供「最大化收益」的申請策略

## Step004: 精確金額計算與驗算
1. 使用官方公式逐項計算補助金額
2. 考慮所得級距、家庭人口數、地區差異等變數
    - 有時候級距描述會用排除法，比如若您不具備o資格或p資格，你就這個級距，這種情況要特別注意，要先去瞭解使用者具有哪些身份，符合或不符合哪些級距，每一個級距的條件，你都要用Step003的所有符合身份去進行查核
    - 有時候級距會用排除法，比如若您不是第m級或是第n級，你就是第x級，這種情況要特別注意，要先去瞭解使用者符合或不符合哪些級距，再用排除法來判斷，不見得一定是按照順序的排除，要注意身份，而不是順序
3. 計算年度總額上限限制
4. 提供計算過程的詳細步驟供驗證
5. 執行驗算checklist每項通過才可以提供給使用者

如需計算，請使用程式碼執行功能進行驗證，確保計算結果準確無誤。
</四個步驟的分析>"""

# ============================================================================
# 台灣津貼補助 Supervisor - 基於 design.md 的 TAIWAN_SUBSIDY_SUPERVISOR_PROMPT
# ============================================================================
TAIWAN_SUBSIDY_SUPERVISOR_PROMPT = """
你是台灣津貼補助 AI 專家，負責協調整個查詢流程。

**重要：每次開始新的查詢時，都必須先執行 Todo 管理流程**

## Todo 管理流程
1. **建立 Todo 清單**：執行 create_todos，參考 主要執行步驟（需建立為 Todo 項目）
2. **有序執行**：系統會自動確保前一步完成才能進行下一步
3. **完成標記**：每完成一個步驟立即用 complete_todo(todo_id) 標記完成，其中 todo_id 是創建時返回的 UUID
4. **進度追蹤**：每次 complete_todo(todo_id) 完都會有更新後的 todo list，依照它的回傳看看接下來要做的項目
5. **結束前必須檢查**：結束前必須確認 complete_todo(todo_id) 裡的 todo list 都已經執行完畢
6. **有工具就要用**：遇到那個步驟要請你執行工具，一定要執行工具取得回應，不要想當然的自己做回應

## 主要執行步驟（需建立為 Todo 項目）
請嚴格按照以下7個步驟執行，不得缺漏，不得跳過任何步驟：
- 步驟一：安全檢查
- 步驟二：5W1H分析檢查資訊完整性
- 步驟三：MECE原則拆解子問題
- 步驟四：執行 enhanced_web_search 工具，對多個子問題進行平行搜尋
- 步驟五：執行 extract_documents 工具，從步驟四取得之資訊，提取法條和FAQ
- 步驟六：執行 calculation_analysis 工具，針對使用者的原始問題，以及步驟五提取的資訊，進行計算分析
- 步驟七：回覆使用者

# 步驟一：安全檢查

首先判斷使用者問題是否符合台灣津貼補助查詢範圍。

## 通過標準 - 繼續執行下面步驟
- 明確提及特定津貼名稱、申請條件、金額、流程
- 包含具體津貼類別：農保、住宅補助、就業失業補助、勞保退休、國民年金、生育育兒、家庭兒少、長照身障、外籍照護、急難救助、特殊身分、環保節能等

## 不通過標準 - 直接回應，不執行後續步驟
- **親切引導回應**: 用詞籠統、資訊不足、一般打招呼（「你好」、「在嗎」、「可以幫我嗎」）
  回應："哈囉你好呀！我是津好康Bot，專門幫大家找臺灣各種津貼補助。有什麼想問的嗎？不要客氣，儘管問喔！😊"

- **防火牆婉拒回應**: 非津貼相關、政治八卦、惡意攻擊、混雜非津貼需求
  回應："謝謝你的提問！我很樂意幫忙，不過我是專門協助臺灣津貼與補助福利查詢的津好康🤖，對於[使用者問題領域]可能沒辦法給你最專業的建議。我的專長是幫您瞭解各種政府津貼補助，像是育兒津貼、老人補助等等。如果您有這方面的需求，我會很開心為你詳細說明喔！"

# 步驟二：5W1H分析檢查資訊完整性

用5W1H框架拆解問題，區分事實與推測：
- **Who**: 申請人身份（自己、家人、什麼身份別）  
- **What**: 具體津貼類別（參考12大津貼類別）
- **When**: 時間條件（申請時間、給付期間、年齡限制等）
- **Where**: 地域條件（居住地、戶籍地、工作地）
- **Why**: 申請目的（生活補助、醫療支援、就業協助等）
- **How**: 申請方式（線上、臨櫃、郵寄等）

## 臺灣津貼12大類別
1. 農民福利保險：農保、農民職災等相關補助
2. 住宅補助方案：租金補貼、購屋優惠貸款
3. 就業失業補助：失業給付、職訓津貼
4. 勞保退休保障：勞保給付、退休金制度
5. 國民年金給付：老年基本保障、遺屬年金
6. 生育育兒補助：生育津貼、育兒補助
7. 家庭兒少福利：弱勢家庭補助、兒少特別照顧
8. 長照身障服務：長照資源、身心障礙補助
9. 外籍人力照護：外籍看護補助、聘僱津貼
10. 急難救助資源：急難紓困、災害救助
11. 特殊身分補助：原住民、榮民福利
12. 環保節能優惠：節能減碳獎勵、綠能補助

## 事實與推測區分
- 使用者明確提到的為「事實」
- 你根據脈絡猜的為「推測」，必須標記為 (推測)
- 如果有關鍵的推測，要向使用者確認：
  範例："請問您是想幫自己申請，還是要幫家裡的長輩問的呢？確認身份後，我提供的資訊會更準確喔！"

如果資訊不完整需要確認，請向使用者提問，**等待回應後再繼續**。如果資訊完整，直接進入步驟三。

# 步驟三：MECE原則拆解子問題

**基於步驟二的5W1H分析結果**，將分析出的事實與推測資訊，轉換為一系列「相互獨立(Mutually Exclusive)、完全窮盡(Collectively Exhaustive)」的子問題。這是你最終要輸出的主要內容。

## 子問題建構原則
**原則1 - 整合5W1H分析**：子問題必須充分整合步驟二獲得的5W1H資訊：
- **Who資訊**：明確反映申請人身份（自己/家人/特定身份別）
- **What資訊**：具體津貼類別和相關細節
- **When資訊**：時間條件、年齡限制、申請期限
- **Where資訊**：地域條件（居住地、戶籍地差異）
- **Why資訊**：申請目的與使用者真實需求
- **How資訊**：申請管道與流程偏好

**原則2 - 保留細節與意圖**：子問題必須保留所有原始提問的數字、身份等細節，並反映其計算或查詢流程的真實意圖。如果使用者要求計算或具體金額、等數字相關的計算，子問題必須反映這個需求

**原則3 - 具體化搜尋目標**：每個子問題都必須是一個可以被獨立查詢、能找到具體答案的行動指令。

**原則4 - 轉換為搜尋關鍵字**：拆解完子問題後，**必須將每個子問題轉換為適合搜尋的關鍵字組合**：
- 移除問句形式（如「是否」、「如何」、「什麼」等疑問詞）
- 保留核心關鍵詞：津貼名稱、身份、地區、金額、條件等
- 用空格分隔關鍵詞，形成搜尋字串

**轉換範例**：
- 原子問題：「300億中央擴大租金補貼專案計畫針對單身青年（28歲）在台北市租屋的申請資格，特別是月薪42000元是否符合所得限制？」
- 轉換後搜尋關鍵字：「300億中央擴大租金補貼專案計畫 單身青年 台北市 租屋 月薪42000元」

**原則5 - 應用拆解策略**：
- **若問題涵蓋申請**，子問題應拆解為：[津貼名稱]的申請資格、申請流程與所需文件、受理機關與聯絡方式。
- **若問題涵蓋計算**，子問題應拆解為：[津貼名稱]的給付標準或費率、計算公式、在[使用者條件]下的可領取金額試算。
- **如果問題涉及計算**：需要拆解出「費率標準」「計算公式」「具體條件下的金額」等
- **如果問題涉及申請**：需要拆解出「申請資格」「申請流程」「所需文件」等
- **如果問題有多個條件**：每個條件都要在子問題中體現
- **如果問題要具體答案**：子問題必須能導向具體答案，而非籠統資訊
- **若問題涵蓋多個方案比較**，應使用MECE原則拆解，例如用「發放單位」作為分類基準 (如：中央級補助、地方政府加碼、勞保局給付)。

## 拆解範例
拆解「育兒相關的錢」可以用『發放單位』做MECE分類，確保不重疊也不遺漏：
- **分類1：中央政府發的錢** (例如：衛福部的0-6歲育兒津貼)
- **分類2：勞動部發的錢** (例如：就業保險的育嬰留職停薪津貼)
- **分類3：地方政府自己加碼的錢** (例如：臺北市的生育獎勵金、各縣市不同的加碼補助)

## 重要注意事項
津貼補助的適用辦法與條件都不一樣，常常有一些津貼可能會合併發放，但是他是不同的計算criteria，即便是相同的津貼發放準則，你也必須把裡面的辦法條列的子項目，獨立列出來作為計算標準和準則。

# 步驟四：執行 enhanced_web_search 工具，對多個子問題進行平行搜尋

**必須執行**：調用 enhanced_web_search 工具，傳遞步驟三建構的子問題列表。
- 優先搜尋 .gov.tw 官方網站
- 搜尋最新法規和FAQ
- 取得完整的搜尋結果

格式：enhanced_web_search(subtopics=[子任務1, 子任務2, 子任務3, ...])

# 步驟五：執行 extract_documents 工具，從步驟四取得之資訊，提取法條和FAQ

**必須執行**：調用 extract_documents 工具平行提取法條和FAQ，並合併為單一文件。
- research_data_file_path: enhanced_web_search 回傳的 file_path

# 步驟六：執行 calculation_analysis 工具，針對使用者的原始問題，以及步驟五提取的資訊，進行計算分析

**必須執行**：調用 calculation_analysis 工具進行專業分析。
- user_input: 使用者的原始提問
- research_data_file_paths: 傳入 extract_documents 回傳的文件路徑（列表中只有一個文件路徑）

# 步驟七：回覆使用者

基於前面所有分析結果，生成最終回應，要使用繁體中文，台灣用語。

## 回應原則（嚴格的零幻覺引證網址）
- 只能使用 enhanced_web_search 工具帶回來的搜尋結果和網址
- 千萬不要編造幻想的網址
- 直接貼引證網址，不要解釋、猜測或篡改
- **重要限制**：只列出 .gov.tw 網域的網址

## CLAER人本回應精神
1. Context Comprehension (情境理解)：傾聽、同理並回溯使用者情境
2. Lucid Solutions (清晰解決方案)：針對核心需求提供精準、客製化的正確資訊
3. Empathetic Anticipation (同理預判)：主動預判潛在需求，提供額外幫助
4. Accessible Interaction (親和互動)：語言溫暖親切，提供明確行動指引
5. Reliable Support (可靠支援)：強調資訊來源可靠性，提供心理支持

## 回應格式
[同理使用者感受，並進行主角側寫分析]

[emoji] **精準解決方案**
[基於計算分析工具提供的完整分析結果]

[emoji] **申請指引與風險提醒**
[具體申請步驟，如涉及計算則提供總金額試算與風險提醒]

[emoji] **官方資料來源**
[只列出 .gov.tw 的引證網址，一字不漏]

---

**重要提醒**：請嚴格按照上述7個步驟依序執行，不要跳過任何步驟。
"""


class TaiwanSubsidyConfigSchema(BaseModel):
    """台灣津貼補助 AI 專家配置 Schema - 可在 LangGraph UI 中設定"""

    prompt_template: str = Field(
        default=TAIWAN_SUBSIDY_SUPERVISOR_PROMPT,
        description="系統提示詞模板，這個是設定給最主要的 agent",
    )

    legal_extraction_prompt: str = Field(
        default=LEGAL_EXTRACTION_PROMPT,
        description="法條提取的提示詞模板，用於 extract_documents 工具中的法條提取部分，要注意要個留 {research_data}",
    )

    faq_extraction_prompt: str = Field(
        default=FAQ_EXTRACTION_PROMPT,
        description="FAQ提取的提示詞模板，用於 extract_documents 工具中的FAQ提取部分,要注意要個留 {research_data}",
    )

    calculation_analysis_prompt: str = Field(
        default=CALCULATION_ANALYSIS_PROMPT,
        description="計算分析的提示詞模板，用於 calculation_analysis 工具中的津貼計算分析部分,要注意要個留 {current_date}, {user_input}, {research_data}",
    )


# ============================================================================
# Pydantic 模型定義 - 重用現有的結構
# ============================================================================
class SearchResult(BaseModel):
    """搜尋結果結構"""

    subtopic: str
    content: str
    sources: List[str]


class Todo(BaseModel):
    """Todo 項目結構"""

    id: str
    title: str
    completed: bool = False
    order: int  # 執行順序 (1, 2, 3, ...)


# ============================================================================
# Todo 管理系統 - Memory 存儲
# ============================================================================

# 全域 Todo 存儲（使用 memory 存儲）
_todo_storage: Dict[str, Todo] = {}


# ============================================================================
# Todo 管理工具 - 內部輔助函數
# ============================================================================


def _get_todos_list() -> List[Dict[str, Any]]:
    """內部函數：獲取所有 Todo 的字典列表，按 order 排序"""
    if not _todo_storage:
        return []

    # 按順序排序
    sorted_todos = sorted(_todo_storage.values(), key=lambda x: x.order)

    result = []
    for todo in sorted_todos:
        result.append(
            {
                "id": todo.id,
                "title": todo.title,
                "completed": todo.completed,
                "order": todo.order,
            }
        )

    return result


# ============================================================================
# Todo 管理工具
# ============================================================================


@tool
def create_todos(todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create todo items from provided list

    Args:
        todos: List of todo dictionaries, each containing 'title' and 'order' fields
               Example: [{"title": "步驟一：安全檢查", "order": 1}, {"title": "步驟二：分析", "order": 2}]

    Returns:
        List of todo dictionaries sorted by order (小到大)
    """
    _todo_storage.clear()
    for todo_data in todos:
        title = todo_data.get("title", "")
        order = todo_data.get("order", 1)

        if not title:
            logging.warning(f"[create_todos] 跳過空白標題的 Todo (order: {order})")
            continue

        todo_id = str(uuid.uuid4())
        todo = Todo(id=todo_id, title=title, order=order)
        _todo_storage[todo_id] = todo
        logging.info(f"[create_todos] 創建 Todo: {todo_id} (順序:{order}) - {title}")

    # 回傳所有 todos
    result = _get_todos_list()
    logging.info(f"[create_todos] 創建完成，回傳 {len(result)} 個 Todo 項目")
    return result


@tool
def list_todos() -> List[Dict[str, Any]]:
    """List all todos

    Returns:
        List of todo dictionaries sorted by order (小到大)
    """
    if not _todo_storage:
        return []

    # 按順序排序
    sorted_todos = sorted(_todo_storage.values(), key=lambda x: x.order)

    result = []
    for todo in sorted_todos:
        result.append(
            {
                "id": todo.id,
                "title": todo.title,
                "completed": todo.completed,
                "order": todo.order,
            }
        )

    logging.info(f"[list_todos] 列出 {len(_todo_storage)} 個 Todo 項目")
    return result


def _can_execute_todo(todo_id: str) -> bool:
    """檢查 Todo 是否可以執行（檢查前序order是否完成）"""
    if todo_id not in _todo_storage:
        return False

    todo = _todo_storage[todo_id]

    # 如果已完成，當然可以執行（實際上已經執行過了）
    if todo.completed:
        return True

    # 檢查是否有前序order未完成
    current_order = todo.order

    # 檢查所有order小於當前order的todo是否都已完成
    for other_todo in _todo_storage.values():
        if other_todo.order < current_order and not other_todo.completed:
            return False

    return True


@tool
def get_todo(todo_id: str) -> Dict[str, Any]:
    """Get a specific todo by ID

    Args:
        todo_id: Todo ID

    Returns:
        Todo dictionary or empty dict if not found
    """
    if todo_id not in _todo_storage:
        logging.error(f"[get_todo] 找不到 Todo ID: {todo_id}")
        return {}

    todo = _todo_storage[todo_id]
    logging.info(f"[get_todo] 查詢 Todo: {todo_id}")

    return {
        "id": todo.id,
        "title": todo.title,
        "completed": todo.completed,
        "order": todo.order,
    }


@tool
def update_todo(todo_id: str, new_title: str) -> str:
    """Update a todo's title

    Args:
        todo_id: Todo ID
        new_title: 新的標題

    Returns:
        更新結果
    """
    if todo_id not in _todo_storage:
        return f"❌ 找不到 Todo ID: {todo_id}"

    old_title = _todo_storage[todo_id].title
    _todo_storage[todo_id].title = new_title

    logging.info(f"[update_todo] 更新 Todo {todo_id}: {old_title} -> {new_title}")
    return f"✏️ 已更新 Todo [{todo_id}]: {old_title} -> {new_title}"


@tool
def complete_todo(todo_id: str) -> List[Dict[str, Any]]:
    """Mark a todo as completed

    Args:
        todo_id: Todo ID

    Returns:
        List of todo dictionaries sorted by order (小到大)
    """
    if todo_id not in _todo_storage:
        logging.error(f"[complete_todo] 找不到 Todo ID: {todo_id}")
        return _get_todos_list()

    todo = _todo_storage[todo_id]
    if todo.completed:
        logging.info(f"[complete_todo] Todo [{todo_id}] 已經是完成狀態了")
        return _get_todos_list()

    # 檢查是否可以執行（前序order已完成）
    if not _can_execute_todo(todo_id):
        logging.warning(
            f"[complete_todo] 無法完成 Todo [Order {todo.order}]: 請先完成前面的步驟"
        )
        return _get_todos_list()

    _todo_storage[todo_id].completed = True
    logging.info(f"[complete_todo] 完成 Todo: {todo_id} - {todo.title}")

    return _get_todos_list()


@tool
def delete_todo(todo_id: str) -> List[Dict[str, Any]]:
    """Delete a todo

    Args:
        todo_id: Todo ID

    Returns:
        List of todo dictionaries sorted by order (小到大)
    """
    if todo_id not in _todo_storage:
        logging.error(f"[delete_todo] 找不到 Todo ID: {todo_id}")
        return _get_todos_list()

    todo = _todo_storage.pop(todo_id)
    logging.info(f"[delete_todo] 删除 Todo: {todo_id} - {todo.title}")
    return _get_todos_list()


@tool
def clear_all_todos() -> List[Dict[str, Any]]:
    """清理所有的 todos

    Returns:
        Empty list
    """
    count = len(_todo_storage)
    _todo_storage.clear()
    logging.info(f"[clear_all_todos] 清理了 {count} 個 Todo 項目")
    return []


# ============================================================================
# Worker Agents 工具定義
# ============================================================================


@tool
async def enhanced_web_search(
    subtopics: List[str], search_vendor: str = "tavily"
) -> Dict[str, Any]:
    """
    增強版網路搜尋工具 - 支援平行搜尋多個子任務

    Args:
        subtopics: 要搜尋的子任務列表
        search_vendor: 搜尋服務商 ("perplexity" 或 "tavily")

    Returns:
        包含搜尋結果和文件路徑的字典
        {
            "file_path": str,  # 搜尋結果寫入的文件路徑
            "research_result": str  # 格式化的搜尋結果內容
        }
    """
    logging.info(f"[enhanced_web_search] 開始搜尋 {len(subtopics)} 個子任務")

    async def search_single_subtopic(subtopic: str) -> SearchResult:
        """搜尋單一子任務"""
        try:
            content = ""
            sources = []
            search_query = subtopic
            domain_filter = ["*.gov.tw"]  # 優先官方網站

            # 根據搜尋服務商選擇不同的搜尋服務
            if search_vendor == "tavily":
                async for event in respond_with_tavily_search(
                    search_query,
                    "",  # 無前綴
                    [{"role": "user", "content": search_query}],
                    domain_filter,
                    False,  # 不stream
                    "sonar",
                ):
                    content += event.chunk
                    if event.raw_json and "sources" in event.raw_json:
                        sources = event.raw_json["sources"]
                    else:
                        sources = ["Tavily Search"]
            else:  # 預設使用 perplexity
                async for event in respond_with_perplexity_search(
                    search_query,
                    "",  # 無前綴
                    [{"role": "user", "content": search_query}],
                    domain_filter,
                    False,  # 不stream
                    "sonar",
                ):
                    content += event.chunk
                    sources = []

            return SearchResult(subtopic=subtopic, content=content, sources=sources)

        except Exception as e:
            logging.error(f"搜尋 '{subtopic}' 失敗: {e}")
            return SearchResult(
                subtopic=subtopic, content=f"搜尋失敗: {str(e)}", sources=[]
            )

    # 平行執行所有搜尋
    search_results = await asyncio.gather(
        *[search_single_subtopic(subtopic) for subtopic in subtopics]
    )

    # 結果彙整
    consolidated_result = "搜尋結果彙整:\n"
    for result in search_results:
        consolidated_result += f"子任務: {result.subtopic}\n"
        consolidated_result += f"內容: {result.content}\n"
        if result.sources:
            consolidated_result += f"來源: {', '.join(result.sources)}\n\n"

    # 將搜尋結果寫入文件
    try:
        file_path = await generate_tmp_text_file(consolidated_result)
        logging.info(f"[enhanced_web_search] 搜尋結果已寫入文件: {file_path}")
    except Exception as e:
        logging.error(f"[enhanced_web_search] 寫入文件失敗: {e}")
        file_path = f"Error: {str(e)}"

    logging.info(f"[enhanced_web_search] 搜尋完成，共 {len(search_results)} 個結果")

    return {"file_path": file_path, "research_result": consolidated_result}


@tool
async def extract_documents(
    research_data_file_path: str, config: RunnableConfig
) -> str:
    """
    文件提取工具 - 平行提取法條和FAQ，並合併為單一文件

    Args:
        research_data_file_path: enhanced_web_search 生成的文件路徑
        config: 包含 legal_extraction_prompt 和 faq_extraction_prompt 的配置

    Returns:
        合併後的文件路徑
    """
    logging.info("[extract_documents] 開始平行提取法條和FAQ文件")

    # 讀取研究資料文件
    try:
        research_data = await read_tmp_text_file(research_data_file_path)
        logging.info(
            f"[extract_documents] 成功讀取研究資料文件: {research_data_file_path}"
        )
    except Exception as e:
        logging.error(f"[extract_documents] 讀取文件失敗: {e}")
        return f"讀取研究資料失敗: {str(e)}"

    # 從配置中獲取提取 prompt 模板
    legal_extraction_template = config["configurable"].get(
        "legal_extraction_prompt", LEGAL_EXTRACTION_PROMPT
    )
    faq_extraction_template = config["configurable"].get(
        "faq_extraction_prompt", FAQ_EXTRACTION_PROMPT
    )

    # 創建 Gemini 模型實例
    extraction_model = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL_NAME,
        temperature=0,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )

    # 使用配置的模板格式化 prompt
    legal_prompt = legal_extraction_template.format(research_data=research_data)
    faq_prompt = faq_extraction_template.format(research_data=research_data)

    async def extract_legal():
        """提取法條內容"""
        try:
            response = extraction_model.invoke([HumanMessage(content=legal_prompt)])
            return response.content
        except Exception as e:
            logging.error(f"[extract_documents] 法條提取失敗: {e}")
            return f"法條提取失敗: {str(e)}"

    async def extract_faq():
        """提取FAQ內容"""
        try:
            response = extraction_model.invoke([HumanMessage(content=faq_prompt)])
            return response.content
        except Exception as e:
            logging.error(f"[extract_documents] FAQ提取失敗: {e}")
            return f"FAQ提取失敗: {str(e)}"

    # 平行執行法條和FAQ提取
    legal_content, faq_content = await asyncio.gather(extract_legal(), extract_faq())

    # 合併內容
    combined_content = f"""===== 法條檔案內容 =====
{legal_content}

===== FAQ檔案內容 =====
{faq_content}
"""

    try:
        # 將合併內容寫入文件
        combined_file_path = await generate_tmp_text_file(combined_content)
        logging.info(f"[extract_documents] 合併文件已寫入: {combined_file_path}")
        return combined_file_path
    except Exception as e:
        logging.error(f"[extract_documents] 寫入合併文件失敗: {e}")
        return f"寫入合併文件失敗: {str(e)}"


@tool
async def calculation_analysis(
    user_input: str, research_data_file_paths: List[str], config: RunnableConfig
) -> str:
    """
    津貼計算分析工具 - 基於使用者提問和多個文件進行數值分析

    Args:
        user_input: 使用者的原始提問
        research_data_file_paths: 多個文件路徑的列表，包含法條和FAQ文件
        config: 包含 calculation_analysis_prompt 的配置

    Returns:
        分析結果字串
    """
    logging.info("[calculation_analysis] 開始計算分析")

    # 讀取多個研究資料文件並合併
    combined_research_data = ""
    for file_path in research_data_file_paths:
        try:
            file_content = await read_tmp_text_file(file_path)
            combined_research_data += file_content
            logging.info(f"[calculation_analysis] 成功讀取研究資料文件: {file_path}")
        except Exception as e:
            logging.error(
                f"[calculation_analysis] 讀取文件失敗: {file_path}, 錯誤: {e}"
            )
            combined_research_data += f"\n\n===== 檔案: {file_path} (讀取失敗) =====\n"
            combined_research_data += f"錯誤: {str(e)}\n"

    if not combined_research_data.strip():
        return "所有研究資料文件讀取失敗"

    research_data = combined_research_data

    # 從配置中獲取計算分析 prompt 模板
    calculation_analysis_template = config["configurable"].get(
        "calculation_analysis_prompt", CALCULATION_ANALYSIS_PROMPT
    )

    # 使用支援程式碼執行的 Gemini 模型
    computation_model = ChatGoogleGenerativeAI(
        model=DEFAULT_MODEL_NAME,
        temperature=0,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
        thinking_budget=256,
        model_kwargs={
            "enable_code_execution": True,
        },
    )

    local_tz = pytz.timezone("Asia/Taipei")
    local_time = datetime.now(local_tz)
    current_date = local_time.strftime("%Y-%m-%d")

    # 使用配置的模板格式化 prompt
    prompt = calculation_analysis_template.format(
        current_date=current_date, user_input=user_input, research_data=research_data
    )

    try:
        response = computation_model.invoke([HumanMessage(content=prompt)])
        logging.info("[calculation_analysis] 計算分析完成")
        return response.content
    except Exception as e:
        logging.error(f"[calculation_analysis] 計算分析失敗: {e}")
        return f"計算分析失敗: {str(e)}"


# ============================================================================
# 單一 Agent 系統 - 中央化 Prompt 管理 + 多專業工具
# ============================================================================

# 台灣津貼補助專家 Agent - 集中所有專業知識
tools = [
    # Todo 管理工具
    create_todos,
    # list_todos,
    # get_todo,
    # update_todo,
    complete_todo,
    # delete_todo,
    # clear_all_todos,
    # 核心搜尋和分析工具
    enhanced_web_search,
    extract_documents,
    # write_text_file,
    calculation_analysis,
]

taiwan_subsidy_agent_graph = create_react_agent(
    model=model,
    tools=tools,
    prompt=TAIWAN_SUBSIDY_SUPERVISOR_PROMPT,  # 所有專業知識集中在這裡
    context_schema=TaiwanSubsidyConfigSchema,
    checkpointer=MemorySaver(),  # 如果要執行在 botrun_back 裡面，就不需要 firestore 的 checkpointer
)


def create_taiwan_subsidy_agent_graph(prompt: str):
    return create_react_agent(
        model=model,
        tools=tools,
        prompt=prompt,  # 所有專業知識集中在這裡
        context_schema=TaiwanSubsidyConfigSchema,
        checkpointer=MemorySaver(),  # 如果要執行在 botrun_back 裡面，就不需要 firestore 的 checkpointer
    )


if __name__ == "__main__":
    logging.info("台灣津貼補助單一 Agent 系統載入完成")
