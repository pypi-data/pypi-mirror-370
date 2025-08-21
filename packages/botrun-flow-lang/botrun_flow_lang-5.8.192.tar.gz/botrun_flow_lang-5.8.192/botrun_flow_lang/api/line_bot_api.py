import os
import json
import time
import sys
import logging
import traceback
import asyncio
from collections import defaultdict, deque
from typing import Tuple
from pathlib import Path
from datetime import datetime
import pytz

from fastapi import APIRouter, HTTPException, Request, Depends
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
from linebot.v3.messaging import AsyncMessagingApi
from pydantic import BaseModel
from botrun_log import Logger, TextLogEntry

from botrun_flow_lang.langgraph_agents.agents.agent_runner import agent_runner, ChatModelEndEvent, OnNodeStreamEvent
from botrun_flow_lang.langgraph_agents.agents.search_agent_graph import (
    DEFAULT_RELATED_PROMPT,
    NORMAL_CHAT_PROMPT_TEXT,
    REQUIREMENT_PROMPT_TEMPLATE,
    SearchAgentGraph,
    DEFAULT_SEARCH_CONFIG,
    DEFAULT_MODEL_NAME
)
from botrun_flow_lang.langgraph_agents.agents.checkpointer.firestore_checkpointer import (
    AsyncFirestoreCheckpointer,
)
from botrun_flow_lang.utils.google_drive_utils import (
    authenticate_google_services,
    get_google_doc_mime_type,
    get_google_doc_content_with_service,
    create_sheet_if_not_exists,
    append_data_to_gsheet,
    get_sheet_content,
)
from botrun_flow_lang.api.auth_utils import verify_token


# 同時輸出到螢幕與本地 log 檔
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

# 建立 handlers 清單供 basicConfig 使用
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

handlers = [_console_handler]

# 透過環境變數 `IS_WRITE_LOG_TO_FILE` 決定是否寫入本地檔案
IS_WRITE_LOG_TO_FILE = os.getenv("IS_WRITE_LOG_TO_FILE", "false")
if IS_WRITE_LOG_TO_FILE == "true":
    default_log_path = Path.cwd() / "logs" / "app.log"
    log_file_path = Path(os.getenv("LINE_BOT_LOG_FILE", default_log_path))
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    _file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    _file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handlers.append(_file_handler)

# 使用 basicConfig 重新配置 root logger；force=True 可覆蓋先前設定 (Py≥3.8)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, handlers=handlers, force=True)

# 取得 module logger（會自動享有 root handlers）
# 如需調整本模組層級，可另行設定，但通常保持 INFO 即可。
logger = logging.getLogger(__name__)

# 常量定義
SUBSIDY_LINE_BOT_CHANNEL_SECRET = os.getenv("SUBSIDY_LINE_BOT_CHANNEL_SECRET", None)
SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN = os.getenv(
    "SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN", None
)
RATE_LIMIT_WINDOW = int(
    os.environ.get("SUBSIDY_LINEBOT_RATE_LIMIT_WINDOW", 60)
)  # 預設時間窗口為 1 分鐘 (60 秒)
RATE_LIMIT_COUNT = int(
    os.environ.get("SUBSIDY_LINEBOT_RATE_LIMIT_COUNT", 2)
)  # 預設在時間窗口內允許的訊息數量 2
LINE_MAX_MESSAGE_LENGTH = 5000

# 全局變數
# 用於追蹤正在處理訊息的使用者，避免同一使用者同時發送多條訊息造成處理衝突
_processing_users = set()
# 用於訊息頻率限制：追蹤每個使用者在時間窗口內發送的訊息時間戳記
# 使用 defaultdict(deque) 結構確保：1) 只記錄有發送訊息的使用者 2) 高效管理時間窗口內的訊息
_user_message_timestamps = defaultdict(deque)

# 初始化 subsidy_line_bot BigQuery Logger
try:
    subsidy_line_bot_bq_logger = Logger(
        db_type="bigquery",
        department=os.getenv("BOTRUN_LOG_DEPARTMENT", "subsidy_line_bot"),
        credentials_path=os.getenv(
            "BOTRUN_LOG_CREDENTIALS_PATH",
            "/app/botrun_flow_lang/keys/scoop-386004-e9c7b6084fb4.json",
        ),
        project_id=os.getenv("BOTRUN_LOG_PROJECT_ID", "scoop-386004"),
        dataset_name=os.getenv("BOTRUN_LOG_DATASET_NAME", "subsidy_line_bot"),
    )
except Exception as e:
    pass


# 初始化 FastAPI 路由器，設定 API 路徑前綴
router = APIRouter(prefix="/line_bot")

# 必要環境變數檢查
# 這裡先拿掉
# if SUBSIDY_LINE_BOT_CHANNEL_SECRET is None:
#     print("Specify SUBSIDY_LINE_BOT_CHANNEL_SECRET as environment variable.")
#     sys.exit(1)
# if SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN is None:
#     print("Specify SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN as environment variable.")
#     sys.exit(1)


async def log_to_bigquery(
    user_id: str,
    display_name: str,
    action_type: str,
    message: str,
    model: str,
    request: Request,
    resource_id: str = "",
    ):
    """
    使用 Botrun Logger 記錄訊息到 BigQuery

    Args:
        user_id (str): LINE 使用者 ID
        display_name (str): 使用者 Line 顯示名稱
        action_type (str): 事件類型
        message (str): 訊息內容
        model (str): 使用的模型
        request (Request): FastAPI request 物件，用於取得 IP 等資訊
        resource_id (str): 資源 ID 預設為空字串
    """
    start_time = time.time()

    try:
        # 取得 Line Server IP 位址
        line_server_ip = request.client.host
        tz = pytz.timezone("Asia/Taipei")

        # 建立文字記錄項目
        text_log = TextLogEntry(
            timestamp=datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%SZ"),
            domain_name=os.getenv("DOMAIN_NAME", ""),
            user_department=os.getenv("BOTRUN_LOG_DEPARTMENT", "subsidy_line_bot"),
            user_name=f"{display_name} ({user_id})",
            source_ip=f"{line_server_ip} (Line Server)",
            session_id="",
            action_type=action_type,
            developer="subsidy_line_bot_elan",
            action_details=message,
            model=model,
            botrun="subsidy_line_bot",
            user_agent="",
            resource_id=resource_id,
        )

        # 插入到 BigQuery
        subsidy_line_bot_bq_logger.insert_text_log(text_log)

        elapsed_time = time.time() - start_time
        logging.info(
            f"[BigQuery Logger] 記錄使用者 {display_name} ({user_id}) 的 {action_type} 訊息到 BigQuery 成功，耗時 {elapsed_time:.3f}s"
        )

    except Exception as e:
        elapsed_time = time.time() - start_time
        logging.error(
            f"[BigQuery Logger] 記錄使用者 {display_name} ({user_id}) 的 {action_type} 訊息到 BigQuery 失敗，耗時 {elapsed_time:.3f}s，錯誤: {e}"
        )


def get_prompt_from_google_doc(tag_name: str, fallback_prompt: str = ""):
    """
    從 Google 文件中提取指定標籤的內容
    優先從 Google 文件讀取，失敗時回退到指定的 fallback prompt

    Args:
        tag_name (str): 要搜尋的 XML 標籤名稱 (例如: 'system_prompt', 'related_prompt')
        fallback_prompt (str, optional): 當從 Google 文件讀取失敗時使用的回退內容

    Returns:
        str: 提取的內容或回退內容
    """
    try:
        # 檢查必要的環境變數是否存在
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FOR_BOTRUN_DOC")
        file_id = os.getenv("SUBSIDY_BOTRUN_DOC_FILE_ID")

        if not credentials_path or not file_id:
            raise ValueError("Missing required environment variables")

        # 嘗試從 Google 文件讀取
        drive_service, docs_service = authenticate_google_services(credentials_path)
        mime_type = get_google_doc_mime_type(file_id, drive_service)
        file_text = get_google_doc_content_with_service(
            file_id, mime_type, drive_service, with_decode=True
        )

        # 提取指定標籤的內容
        import re

        pattern = f"<{tag_name}>(.*?)</{tag_name}>"
        match = re.search(pattern, file_text, re.DOTALL)
        if match:
            logger.info(
                f"[Line Bot Webhook: subsidy_webhook] Successfully extracted {tag_name} from Google Docs"
            )
            if match.group(1).strip():
                return match.group(1).strip()
            else:
                return fallback_prompt
        logger.info(
            f"[Line Bot Webhook: subsidy_webhook] Failed to extract {tag_name} from Google Docs, return file text"
        )

        return fallback_prompt

    except Exception as e:
        logger.warning(
            f"[Line Bot Webhook: subsidy_webhook] Failed to load {tag_name} from Google Docs, using fallback. Error: {e}"
        )

        return fallback_prompt


def get_subsidy_api_system_prompt():
    """
    取得智津貼的系統提示
    優先從 Google 文件讀取，失敗時回退到本地檔案
    """
    current_dir = Path(__file__).parent
    fallback_prompt = (current_dir / "subsidy_api_system_prompt.txt").read_text(
        encoding="utf-8"
    )
    return get_prompt_from_google_doc("system_prompt", fallback_prompt)


def get_subsidy_bot_related_prompt():
    """
    取得智津貼的相關問題提示
    優先從 Google 文件讀取，失敗時使用預設的相關問題提示
    """
    return get_prompt_from_google_doc("related_prompt", DEFAULT_RELATED_PROMPT)


def get_subsidy_bot_normal_chat_prompt():
    """
    取得智津貼的正常聊天提示
    優先從 Google 文件讀取，失敗時使用預設的正常聊天提示
    """
    return get_prompt_from_google_doc("normal_chat_prompt", NORMAL_CHAT_PROMPT_TEXT)


def get_subsidy_bot_requirement_prompt():
    """
    取得智津貼的 requirement_prompt
    優先從 Google 文件讀取，失敗時使用預設的必要提示
    """
    return get_prompt_from_google_doc("requirement_prompt", REQUIREMENT_PROMPT_TEMPLATE)


def get_subsidy_bot_search_config() -> dict:
    return {
        **DEFAULT_SEARCH_CONFIG,
        "requirement_prompt": get_subsidy_bot_requirement_prompt(),
        "search_prompt": get_subsidy_api_system_prompt(),
        "normal_chat_prompt": get_subsidy_bot_normal_chat_prompt(),
        "related_prompt": get_subsidy_bot_related_prompt(),
        "domain_filter": ["*.gov.tw", "-*.gov.cn"],
        "user_prompt_prefix": "你是台灣人，你不可以講中國用語也不可以用簡體中文，禁止！你的回答內容不要用Markdown格式。",
        "stream": False,
    }


@router.post("/subsidy/webhook")
async def subsidy_webhook(request: Request):
    from linebot.v3.exceptions import InvalidSignatureError
    from linebot.v3.webhook import WebhookParser
    from linebot.v3.messaging import AsyncApiClient, Configuration

    signature = request.headers["X-Line-Signature"]
    if SUBSIDY_LINE_BOT_CHANNEL_SECRET is None:
        raise HTTPException(
            status_code=500, detail="SUBSIDY_LINE_BOT_CHANNEL_SECRET is not set"
        )
    if SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN is None:
        raise HTTPException(
            status_code=500, detail="SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN is not set"
        )
    parser = WebhookParser(SUBSIDY_LINE_BOT_CHANNEL_SECRET)
    configuration = Configuration(access_token=SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN)

    # get request body as text
    body = await request.body()
    body_str = body.decode("utf-8")
    body_json = json.loads(body_str)
    logging.info(
        "[Line Bot Webhook: subsidy_webhook] Received webhook: %s",
        json.dumps(body_json, indent=2, ensure_ascii=False),
    )

    try:
        events = parser.parse(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    start = time.time()
    env_name = os.getenv("ENV_NAME", "botrun-flow-lang-dev")
    subsidy_line_bot_graph = SearchAgentGraph(
        memory=AsyncFirestoreCheckpointer(env_name=env_name)
    ).graph
    logging.info(
        f"[Line Bot Webhook: subsidy_webhook] init graph took {time.time() - start:.3f}s"
    )

    responses = []
    async with AsyncApiClient(configuration) as async_api_client:
        line_bot_api = AsyncMessagingApi(async_api_client)
        for event in events:
            # 處理使用者傳送詢問訊息的事件
            if isinstance(event, MessageEvent) and isinstance(
                event.message, TextMessageContent
            ):
                response = await handle_message(
                    event,
                    line_bot_api,
                    RATE_LIMIT_WINDOW,
                    RATE_LIMIT_COUNT,
                    subsidy_line_bot_graph,
                    request,
                )
                responses.append(response)

            # 處理使用者藉由按讚反讚按鈕反饋的postback事件
            elif isinstance(event, PostbackEvent):
                await handle_feedback(event, line_bot_api, subsidy_line_bot_graph)
                responses.append("feedback_handled")

    return {"responses": responses}


async def get_user_display_name(user_id: str, line_bot_api: AsyncMessagingApi) -> str:
    """
    取得使用者的Line顯示名稱

    Args:
        user_id (str): 使用者ID
        line_bot_api (AsyncMessagingApi): LINE Bot API 客戶端

    Returns:
        user_display_name (str): 使用者的Line顯示名稱
    """
    try:
        user_profile = await line_bot_api.get_profile(user_id)
        return user_profile.display_name
    except Exception as e:
        logging.error(
            f"[Line Bot Webhook: get_user_display_name] 無法取得使用者 {user_id} 的顯示名稱: {str(e)}"
        )


async def handle_message(
    event: MessageEvent,
    line_bot_api: AsyncMessagingApi,
    rate_limit_window: int,
    rate_limit_count: int,
    line_bot_graph: SearchAgentGraph,
    request: Request,
):
    """處理 LINE Bot 的訊息事件

    處理使用者傳送的文字訊息，包括頻率限制檢查、訊息分段與回覆等操作

    Args:
        event (MessageEvent): LINE Bot 的訊息事件
        line_bot_api (AsyncMessagingApi): LINE Bot API 客戶端
        rate_limit_window (int): 訊息頻率限制時間窗口（秒）
        rate_limit_count (int): 訊息頻率限制數量
        line_bot_graph (SearchAgentGraph): LINE Bot 的 agent graph
        request (Request): FastAPI request 物件，用於記錄到 BigQuery
    """
    start = time.time()
    logging.info(
        "[Line Bot Webhook: handle_message] Enter handle_message for event type: %s",
        event.type,
    )
    from linebot.v3.messaging import (
        ReplyMessageRequest,
        TextMessage,
        FlexMessage,
        FlexBubble,
        FlexBox,
        FlexText,
        FlexButton,
        MessageAction,
        QuickReply,
        QuickReplyItem,
        PostbackAction,
    )

    # 已經移至常量部分定義
    user_id = event.source.user_id
    user_message = event.message.text
    display_name = await get_user_display_name(user_id, line_bot_api)
    logging.info(
        f"[Line Bot Webhook: handle_message] 收到來自 {display_name} ({user_id}) 的訊息"
    )

    # 背景記錄使用者訊息到 BigQuery (不等待完成，避免影響回應速度)
    asyncio.create_task(
        log_to_bigquery(
            user_id,
            display_name,
            "llm_input",
            user_message,
            DEFAULT_MODEL_NAME,
            request,
        )
    )

    if user_message.lower().strip() == "reset":
        env_name = os.getenv("ENV_NAME", "botrun-flow-lang-dev")
        await AsyncFirestoreCheckpointer(env_name=env_name).adelete_thread(user_id)
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="已清除記憶，請重新開始對話")],
            )
        )
        return {"message": "已清除記憶，請重新開始對話"}

    if user_id in _processing_users:
        logging.info(
            f"[Line Bot Webhook: handle_message] 使用者 {display_name} ({user_id}) 已有處理中的訊息，回覆等待提示"
        )
        reply_text = "您的上一條訊息正在處理中，請稍候再發送新訊息"
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )
        return {"message": reply_text}

    # 檢查使用者是否超過訊息頻率限制
    is_rate_limited, wait_seconds = check_rate_limit(
        user_id, rate_limit_window, rate_limit_count
    )
    if is_rate_limited:
        logging.info(
            f"[Line Bot Webhook: handle_message] 使用者 {display_name} ({user_id}) 超過訊息頻率限制，需等待 {wait_seconds} 秒"
        )

        # 回覆頻率限制提示
        window_minutes = rate_limit_window // 60
        wait_minutes = max(1, wait_seconds // 60)
        reply_text = f"您發送訊息的頻率過高，{window_minutes}分鐘內最多可發送{rate_limit_count}則訊息。請等待約 {wait_minutes} 分鐘後再試。"
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )
        return {"message": reply_text}

    # 標記使用者為處理中
    _processing_users.add(user_id)

    try:
        reply_text, related_questions = await get_reply_text(
            line_bot_graph, user_message, user_id, display_name, request
        )
        logging.info(
            f"[Line Bot Webhook: handle_message] Total response length: {len(reply_text)}"
        )

        # 將長訊息分段，每段不超過 LINE_MAX_MESSAGE_LENGTH
        message_chunks = []
        remaining_text = reply_text

        while remaining_text:
            # 如果剩餘文字長度在限制內，直接加入並結束
            if len(remaining_text) <= LINE_MAX_MESSAGE_LENGTH:
                message_chunks.append(remaining_text)
                logging.info(
                    f"[Line Bot Webhook: handle_message] Last chunk length: {len(remaining_text)}"
                )
                break

            # 確保分段大小在限制內
            safe_length = min(
                LINE_MAX_MESSAGE_LENGTH - 100, len(remaining_text)
            )  # 預留一些空間

            # 在安全長度內尋找最後一個完整句子
            chunk_end = safe_length
            for i in range(safe_length - 1, max(0, safe_length - 200), -1):
                if remaining_text[i] in "。！？!?":
                    chunk_end = i + 1
                    break

            # 如果找不到適合的句子結尾，就用空格或換行符號來分割
            if chunk_end == safe_length:
                for i in range(safe_length - 1, max(0, safe_length - 200), -1):
                    if remaining_text[i] in " \n":
                        chunk_end = i + 1
                        break
                # 如果還是找不到合適的分割點，就直接在安全長度處截斷
                if chunk_end == safe_length:
                    chunk_end = safe_length

            # 加入這一段文字
            current_chunk = remaining_text[:chunk_end]
            logging.info(
                f"[Line Bot Webhook: handle_message] Current chunk length: {len(current_chunk)}"
            )
            message_chunks.append(current_chunk)

            # 更新剩餘文字
            remaining_text = remaining_text[chunk_end:]

        logging.info(
            f"[Line Bot Webhook: handle_message] Number of chunks: {len(message_chunks)}"
        )
        for i, chunk in enumerate(message_chunks):
            logging.info(
                f"[Line Bot Webhook: handle_message] Chunk {i} length: {len(chunk)}"
            )

        # 創建訊息列表
        messages = []

        # 添加所有文字訊息區塊
        for i, chunk in enumerate(message_chunks):
            messages.append(TextMessage(text=chunk))

        # 添加相關問題按鈕
        question_bubble = None
        if related_questions:
            title = FlexText(
                text="以下是您可能想要了解的相關問題：",
                weight="bold",
                size="md",
                wrap=True,
            )
            buttons = [
                FlexButton(
                    action=MessageAction(label=q[:20], text=q),
                    style="secondary",
                    margin="sm",
                    height="sm",
                    scaling=True,
                    adjust_mode="shrink-to-fit",
                )
                for q in related_questions
            ]
            question_bubble = FlexBubble(
                body=FlexBox(
                    layout="vertical", spacing="sm", contents=[title, *buttons]
                )
            )

        # 以 Quick Reply 作為按讚反讚按鈕
        quick_reply = QuickReply(
            items=[
                QuickReplyItem(
                    action=PostbackAction(
                        label="津好康，真是棒👍🏻",
                        data="實用",
                        display_text="津好康，真是棒👍🏻",
                    )
                ),
                QuickReplyItem(
                    action=PostbackAction(
                        label="津可惜，不太實用😖",
                        data="不實用",
                        display_text="津可惜，不太實用😖",
                    )
                ),
            ]
        )

        if question_bubble:
            messages.append(FlexMessage(alt_text="相關問題", contents=question_bubble))

        messages[-1].quick_reply = quick_reply

        await line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
        )
    except Exception as e:
        logging.error(
            f"[Line Bot Webhook: handle_message] 處理使用者 {display_name} ({user_id}) 訊息時發生錯誤: {e}"
        )
        traceback.print_exc()
        reply_text = "很抱歉，處理您的訊息時遇到問題，請稍後再試"
        try:
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )
        except Exception as reply_error:
            logging.error(
                f"[Line Bot Webhook: handle_message] 無法發送錯誤回覆: {reply_error}"
            )
            traceback.print_exc()
    finally:
        logging.info(
            f"[Line Bot Webhook: handle_message] total elapsed {time.time() - start:.3f}s"
        )
        _processing_users.discard(user_id)
        logging.info(
            f"[Line Bot Webhook: handle_message] 使用者 {display_name} ({user_id}) 的訊息處理完成"
        )

    return {"message": reply_text}


def check_rate_limit(user_id: str, window: int, count: int) -> Tuple[bool, int]:
    """檢查使用者是否超過訊息頻率限制

    檢查使用者在指定時間窗口內發送的訊息數量是否超過限制。
    同時清理過期的時間戳記，以避免記憶體無限增長。

    Args:
        user_id (str): 使用者的 LINE ID
        window (int): 時間窗口（秒）
        count (int): 訊息數量限制

    Returns:
        Tuple[bool, int]: (是否超過限制, 需要等待的秒數)
        如果未超過限制，第二個值為 0
    """
    current_time = time.time()
    user_timestamps = _user_message_timestamps[user_id]

    # 清理過期的時間戳記（超過時間窗口的）
    while user_timestamps and current_time - user_timestamps[0] > window:
        user_timestamps.popleft()

    # 如果清理後沒有時間戳記，則從字典中移除該使用者的記錄
    if not user_timestamps:
        del _user_message_timestamps[user_id]
        # 如果使用者沒有有效的時間戳記，則直接添加新的時間戳記
        _user_message_timestamps[user_id].append(current_time)
        return False, 0

    # 檢查是否超過限制
    if len(user_timestamps) >= count:
        # 計算需要等待的時間
        oldest_timestamp = user_timestamps[0]
        wait_time = int(window - (current_time - oldest_timestamp))
        return True, max(0, wait_time)

    # 未超過限制，添加當前時間戳記
    user_timestamps.append(current_time)

    return False, 0


async def get_reply_text(
    line_bot_graph,
    line_user_message: str,
    user_id: str,
    display_name: str,
    request: Request,
) -> tuple[str, list]:
    """
    使用 agent_runner 處理使用者訊息並回傳回覆內容

    Args:
        line_bot_graph (SearchAgentGraph): LINE Bot 的 agent graph
        line_user_message (str): 使用者傳送的 LINE 訊息內容
        user_id (str): 使用者的 LINE ID
        display_name (str): 使用者的 Line 顯示名稱
        request (Request): FastAPI request 物件，用於記錄到 BigQuery

    Returns:
        tuple[str, list]: 包含回覆訊息和相關問題的元組
    """
    start_time = time.time()
    full_response = ""
    chat_model_events = []  # 收集 ChatModelEndEvent

    async for event_chunk in agent_runner(
        user_id,
        {"messages": [line_user_message]},
        line_bot_graph,
        extra_config=get_subsidy_bot_search_config(),
    ):
        if isinstance(event_chunk, OnNodeStreamEvent):
            # 處理串流文字事件
            full_response += event_chunk.chunk
        if isinstance(event_chunk, ChatModelEndEvent):
            # 收集 ChatModelEndEvent 待後續處理
            chat_model_events.append(event_chunk)

    # 迴圈結束後，處理所有收集到的 ChatModelEndEvent 並記錄到 BigQuery
    for event_chunk in chat_model_events:
        try:
            # 使用輔助函數處理事件資料
            ai_message_outputs = _extract_ai_message_outputs(event_chunk.raw_output, event_chunk.langgraph_node)
            inputs = _extract_input_messages(event_chunk.raw_input)
            
            # 處理節點名稱映射
            processed_node_name = event_chunk.langgraph_node
            if processed_node_name == 'extract':
                processed_node_name = 'requirement_node_extract'
            
            # 準備資源 ID
            resource_id = ""
            if event_chunk.usage_metadata:
                resource_id = json.dumps(event_chunk.usage_metadata, ensure_ascii=False)
            
            # 準備要記錄的訊息內容
            log_message_parts = []
            if ai_message_outputs:
                log_message_parts.append(ai_message_outputs)
            if inputs:
                inputs_text = "".join(inputs)
                log_message_parts.append(inputs_text)
            
            log_message = "".join(log_message_parts)

            logging.info(f"[Line Bot Webhook: get_reply_text - collect log info for BigQuery] langgraph_node: {processed_node_name}")
            logging.info(f"[Line Bot Webhook: get_reply_text - collect log info for BigQuery] model_name: {event_chunk.model_name}")
            logging.info(f"[Line Bot Webhook: get_reply_text - collect log info for BigQuery] resource_id: {resource_id}")
            logging.info(f"[Line Bot Webhook: get_reply_text - collect log info for BigQuery] ai_message_outputs: {ai_message_outputs}")
            for i, input in enumerate(inputs, start=1):
                logging.info(f"[Line Bot Webhook: get_reply_text - collect log info for BigQuery] inputs_{i}: {input}")

            logging.info(f"[Line Bot Webhook: get_reply_text - collect log info for BigQuery] log_message: {log_message}")
            
            # 異步記錄到 BigQuery
            asyncio.create_task(
                log_to_bigquery(
                    user_id=user_id,
                    display_name=display_name,
                    action_type=f"langgraph_agent_api-[{processed_node_name}]",
                    message=log_message,
                    model=event_chunk.model_name,
                    request=request,
                    resource_id=resource_id,
                )
            )
            
            logging.info(f"[Line Bot Webhook: get_reply_text] Logged ChatModelEndEvent to BigQuery for user {user_id}")
            
        except Exception as e:
            logging.error(f"[Line Bot Webhook: get_reply_text] Failed to log ChatModelEndEvent to BigQuery: {e}")

    # 記錄 LLM 輸出到 BigQuery
    asyncio.create_task(
        log_to_bigquery(
            user_id,
            display_name,
            "llm_output",
            full_response,
            DEFAULT_MODEL_NAME,
            request,
        )
    )

    if "</think>" in full_response:
        full_response = full_response.split("</think>", 1)[1].lstrip()

    full_response += "\n" + os.getenv("SUBSIDY_LINEBOT_FOOTNOTE", "")

    # 取得相關問題但不附加到回覆內容
    related_questions = []
    try:
        # 嘗試使用非同步方式取得 state（若 checkpointer 為非同步型別）
        try:
            state_obj = await line_bot_graph.aget_state(
                {"configurable": {"thread_id": user_id}}
            )
        except AttributeError:
            # 回退到同步方法
            state_obj = line_bot_graph.get_state(
                {"configurable": {"thread_id": user_id}}
            )

        # 根據返回型別（dict 或具備屬性）解析
        if isinstance(state_obj, dict):
            related_questions = state_obj.get("related_questions", [])
        elif hasattr(state_obj, "related_questions"):
            related_questions = getattr(state_obj, "related_questions", [])
        elif hasattr(state_obj, "values") and isinstance(state_obj.values, dict):
            related_questions = state_obj.values.get("related_questions", [])
    except Exception as e:
        logging.error(
            f"[Line Bot Webhook: get_reply_text] Failed to append related questions: {e}"
        )

    logging.info(
        f"[Line Bot Webhook: get_reply_text] total took {time.time() - start_time:.3f}s"
    )

    return full_response, related_questions


async def handle_feedback(
    event: PostbackEvent,
    line_bot_api: AsyncMessagingApi,
    subsidy_line_bot_graph,
):
    """處理使用者透過 Quick Reply 按鈕提供的回饋

    Args:
        event (PostbackEvent): LINE Bot 的 postback 事件
        line_bot_api (AsyncMessagingApi): LINE Bot API 客戶端
        subsidy_line_bot_graph: LINE Bot 的 graph 實例，用來取得對話歷史
    """
    try:
        user_id = event.source.user_id
        feedback_data = event.postback.data
        display_name = await get_user_display_name(user_id, line_bot_api)

        taiwan_tz = pytz.timezone("Asia/Taipei")
        current_time = datetime.now(taiwan_tz)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 從 graph state 中取得對話歷史
        config = {"configurable": {"thread_id": user_id}}
        try:
            from langchain_core.messages import HumanMessage, AIMessage

            state = await subsidy_line_bot_graph.aget_state(config)
            messages = state.values.get("messages", [])

            # 找到最新的使用者提問和 AI 回答
            latest_user_question = ""
            latest_ai_response = ""

            # 從後往前查找最新的對話
            for i in range(len(messages) - 1, -1, -1):
                message = messages[i]
                # 檢查是否為 AI 訊息且不是工具呼叫
                if isinstance(message, AIMessage) and not getattr(
                    message, "tool_calls", None
                ):
                    if not latest_ai_response:
                        latest_ai_response = str(message.content)
                elif isinstance(message, HumanMessage):
                    if not latest_user_question:
                        latest_user_question = str(message.content)
                    # 如果已經找到最新的使用者問題，就停止搜尋
                    if latest_ai_response:
                        break

        except Exception as e:
            logging.error(f"[Line Bot Webhook: handle_feedback] 無法取得對話歷史: {e}")
            latest_user_question = "無法取得"
            latest_ai_response = "無法取得"

        if "</think>" in latest_ai_response:
            latest_ai_response = latest_ai_response.split("</think>", 1)[1].lstrip()

        # 記錄詳細的回饋資訊
        logging.info(
            f"[Line Bot Webhook: handle_feedback] 回饋詳細資訊:\n"
            f"  建立時間: {formatted_time}\n"
            f"  使用者ID: {user_id}\n"
            f"  使用者Line顯示名稱: {display_name}\n"
            f"  使用者輸入: {latest_user_question}\n"
            f"  LineBot回應: {latest_ai_response}\n"
            f"  反饋: {feedback_data}"
        )

        # 先回覆使用者已收到回饋的訊息
        from linebot.v3.messaging import TextMessage, ReplyMessageRequest

        reply_text = "已收到您的回饋。"
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )

        # 使用 asyncio.create_task 在背景執行更新使用者回饋到 Google Sheet
        feedback_dict = {
            "建立時間": formatted_time,
            "使用者ID": user_id,
            "使用者Line顯示名稱": display_name,
            "使用者輸入": latest_user_question,
            "LineBot回應": latest_ai_response,
            "反饋": feedback_data,
        }
        asyncio.create_task(update_feedback_to_gsheet(feedback_dict))
    except Exception as e:
        logging.error(
            f"[Line Bot Webhook: handle_feedback] 處理使用者 {display_name} ({user_id}) 回饋時發生錯誤: {e}"
        )
        traceback.print_exc()


async def update_feedback_to_gsheet(feedback_data: dict):
    """更新回饋資料到 Google Sheets"""
    try:
        service_account_file = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_FOR_SUBSIDY_LINEBOT"
        )
        spreadsheet_id = os.getenv("SUBSIDY_LINEBOT_GSPREAD_ID")

        if not service_account_file:
            logging.error(
                "[Line Bot Webhook: update_feedback_to_gsheet] 環境變數 GOOGLE_APPLICATION_CREDENTIALS_FOR_SUBSIDY_LINEBOT 未設定"
            )
            return

        if not spreadsheet_id:
            logging.error(
                "[Line Bot Webhook: update_feedback_to_gsheet] 環境變數 SUBSIDY_LINEBOT_GSPREAD_ID 未設定"
            )
            return

        if not os.path.exists(service_account_file):
            logging.error(
                f"[Line Bot Webhook: update_feedback_to_gsheet] 服務帳戶檔案不存在: {service_account_file}"
            )
            return

        worksheet_name = "LineBot意見回饋"
        headers = [
            "建立時間",
            "使用者ID",
            "使用者Line顯示名稱",
            "使用者輸入",
            "LineBot回應",
            "反饋",
        ]

        success = create_sheet_if_not_exists(
            service_account_file=service_account_file,
            spreadsheet_id=spreadsheet_id,
            sheet_name=worksheet_name,
            headers=headers,
        )

        if not success:
            logging.error(
                "[Line Bot Webhook: update_feedback_to_gsheet] 無法建立或存取工作表"
            )
            return

        result = append_data_to_gsheet(
            service_account_file=service_account_file,
            spreadsheet_id=spreadsheet_id,
            sheet_name=worksheet_name,
            data_dict=feedback_data,
        )

        logging.info(
            f"[Line Bot Webhook: update_feedback_to_gsheet] 已成功將使用者回饋寫入 Google Sheet {worksheet_name}"
        )

    except Exception as e:
        logging.error(
            f"[Line Bot Webhook: update_feedback_to_gsheet] 將使用者回饋寫入 Google Sheet 時發生錯誤: {e}"
        )
        import traceback

        traceback.print_exc()


class MulticastMessage(BaseModel):
    message: str


@router.post("/subsidy/multicast_msg", dependencies=[Depends(verify_token)])
async def subsidy_multicast_msg(body: MulticastMessage):
    """
    透過 LINE Multicast API 將文字訊息一次推播給 Google Sheet「LineBot使用者ID表」中的所有使用者。

    請以 JSON 格式提供要推播的訊息：{ "message": "要推播的訊息" }
    """
    try:
        text = body.message
        if not text:
            raise HTTPException(status_code=400, detail="Request JSON must contain 'message'")

        # 檢查 Access Token
        if SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN is None:
            raise HTTPException(
                status_code=500, detail="SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN is not set"
            )

        # 取得 Google Sheet 設定
        service_account_file = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_FOR_SUBSIDY_LINEBOT"
        )
        spreadsheet_id = os.getenv("SUBSIDY_LINEBOT_GSPREAD_ID")
        if not service_account_file or not spreadsheet_id:
            raise HTTPException(status_code=500, detail="Google Sheet env vars not set")

        sheet_name = "LineBot使用者ID表"
        try:
            sheet_content = get_sheet_content(
                service_account_file, spreadsheet_id, sheet_name
            )
        except Exception as e:
            logging.error(
                f"[Line Bot Multicast] Failed to read Google Sheet: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to read user list from Google Sheet",
            )

        if "user_id" not in sheet_content:
            raise HTTPException(status_code=400, detail="Sheet missing 'user_id' column")

        user_ids = sheet_content.get("user_id", [])

        logging.info(f"[Line Bot Multicast] Retrieved {len(user_ids)} user_ids: {user_ids}")

        if not user_ids:
            raise HTTPException(status_code=400, detail="No user IDs to send")

        from linebot.v3.messaging import AsyncApiClient, Configuration, TextMessage, MulticastRequest

        configuration = Configuration(access_token=SUBSIDY_LINE_BOT_CHANNEL_ACCESS_TOKEN)
        async with AsyncApiClient(configuration) as async_api_client:
            line_bot_api = AsyncMessagingApi(async_api_client)
            CHUNK_SIZE = 500  # LINE Multicast 單次最多 500 個使用者
            for i in range(0, len(user_ids), CHUNK_SIZE):
                chunk_ids = user_ids[i : i + CHUNK_SIZE]
                multicast_request = MulticastRequest(
                    to=chunk_ids, messages=[TextMessage(text=text)]
                )
                await line_bot_api.multicast(multicast_request)

        logging.info(
            f"[Line Bot Multicast] Successfully sent multicast to {len(user_ids)} users"
        )

        return {"status": "ok", "sent_to": len(user_ids)}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"[Line Bot Multicast] Unexpected error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


def _extract_ai_message_outputs(raw_output, langgraph_node: str) -> str:
    """根據 langgraph_node 從 raw_output 中提取 AI 訊息輸出"""
    ai_message_outputs = ""
    
    try:
        if langgraph_node == "extract":
            if hasattr(raw_output, "tool_calls"):
                for tool_call in raw_output.tool_calls:
                    if tool_call.get("name") == "RequirementPromptInstructions":
                        args = tool_call.get("args", {})
                        ai_message_outputs = str(args)
                        break
        elif langgraph_node in ["search_node", "normal_chat_node"]:
            if hasattr(raw_output, "content"):
                ai_message_outputs = str(raw_output.content)
        elif langgraph_node == "related_node":
            if (hasattr(raw_output, "additional_kwargs") and "tool_calls" in raw_output.additional_kwargs):
                tool_calls = raw_output.additional_kwargs["tool_calls"]
                for tool_call in tool_calls:
                    if tool_call.get("function", {}).get("name") == "RelatedQuestionsInstructions":
                        arguments = json.loads(tool_call["function"]["arguments"])
                        related_questions = arguments.get("related_questions", [])
                        ai_message_outputs = "; ".join(related_questions)
                        break
    except Exception as e:
        logging.error(f"[Line Bot API] Failed to extract AI message outputs for {langgraph_node}: {e}")
    
    return ai_message_outputs


def _extract_input_messages(raw_input) -> list[str]:
    """從 raw_input 中提取所有輸入訊息"""
    inputs = []
    
    try:
        # 檢查 raw_input 是否為字典且包含 messages
        if isinstance(raw_input, dict) and "messages" in raw_input:
            messages = raw_input["messages"]
            ai_messages = []
            human_messages = []
            system_messages = []
            
            for msg in messages:
                for nested_msg in msg:
                    if hasattr(nested_msg, "__class__"):
                        msg_type = nested_msg.__class__.__name__
                        msg_content = str(getattr(nested_msg, "content", ""))
                        
                        if msg_type == "AIMessage":
                            ai_messages.append(msg_content)
                        elif msg_type == "HumanMessage":
                            human_messages.append(msg_content)
                        elif msg_type == "SystemMessage":
                            system_messages.append(msg_content)
            
            inputs = ai_messages + human_messages + system_messages
        else:
            # 如果 raw_input 不是預期的格式，嘗試轉換為字串
            inputs = [str(raw_input)] if raw_input is not None else []
    except Exception as e:
        logging.error(f"[Line Bot API] Failed to extract input messages: {e}")
        inputs = [str(raw_input)] if raw_input is not None else []
    
    return inputs
