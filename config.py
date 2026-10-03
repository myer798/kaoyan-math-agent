# -*- coding: utf-8 -*-
"""项目总配置：所有脚本共用。密钥只从同目录下的 .env 文件读取。"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env", encoding="utf-8")

# ---- 原始 PDF 所在文件夹（可选：仅当你想重新处理真题时才需要）----
EXAM_DIR = Path(os.getenv("EXAM_DIR", ""))
SOL_DIR = Path(os.getenv("SOL_DIR", ""))

# ---- 处理年份 ----
# 试点：先做近 5 年跑通全流程；跑通后把 PROCESS_YEARS 改成 ALL_YEARS 即可全量处理
PILOT_YEARS = [2022, 2023, 2024, 2025, 2026]
ALL_YEARS = list(range(1987, 2027))
PROCESS_YEARS = PILOT_YEARS

# ---- 视觉识别 + 向量模型：阿里云百炼（OpenAI 兼容模式）----
VISION_API_KEY = os.getenv("VISION_API_KEY", "")
VISION_BASE_URL = os.getenv(
    "VISION_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
VISION_MODEL = os.getenv("VISION_MODEL", "qwen-vl-max")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-v3")

# ---- 出题文本模型：DeepSeek ----
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# ---- 工作目录 ----
DATA = ROOT / "data"
IMG_DIR = DATA / "images"
OCR_DIR = DATA / "ocr"          # 视觉模型识别出的 Markdown
Q_DIR = DATA / "questions"      # 结构化题库 JSON
INDEX_DIR = DATA / "index"      # 向量索引
OUT_DIR = ROOT / "output"
PAPER_DIR = OUT_DIR / "papers"
WEB_DIR = OUT_DIR / "web"
for _p in (IMG_DIR, OCR_DIR, Q_DIR, INDEX_DIR, PAPER_DIR, WEB_DIR):
    _p.mkdir(parents=True, exist_ok=True)

# ---- 识别参数 ----
DPI = 200          # PDF 渲染分辨率，200DPI 对公式识别性价比最高
