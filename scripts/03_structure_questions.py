# -*- coding: utf-8 -*-
"""
第 3 步：把 OCR 得到的按页 Markdown 合并、拆分为结构化题库 JSON。
流程：
  a) 同一年份的「真题」和「解析」各合并成一个大 Markdown
  b) 调 DeepSeek 把合并后的文本拆成一道道题，输出 JSON 数组
  c) 每道题包含：year / qtype / qno / content / answer / analysis / topics
  d) 全部年份合并成 data/questions/all_questions.json

用法： python scripts/03_structure_questions.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI  # noqa: E402
import config  # noqa: E402

# ---- 合并某年份某类型的全部页 Markdown ----
def merge_year(year: int, kind: str) -> str:
    prefix = f"{kind}_{year}_p"
    files = sorted(config.OCR_DIR.glob(f"{prefix}*.md"))
    parts = []
    for f in files:
        txt = f.read_text(encoding="utf-8").strip()
        if txt:
            parts.append(txt)
    return "\n\n".join(parts)


STRUCTURE_PROMPT = """你是一个数学题库结构化助手。下面给你某年考研数学（一）的{kind}文本（Markdown+LaTeX）。
请把里面的题目逐道拆开，输出为 JSON 数组。每道题包含字段：
- qtype：题型，从 {{填空题, 选择题, 解答题, 证明题}} 中选一个
- qno：题号（如 "1"、"2(1)"、"(3)"）
- content：题干，保留 LaTeX（$...$、$$...$$）
- answer：答案（解析文本里才有，真题卷没有就留空字符串）
- analysis：解析过程（解析文本里才有，真题卷没有就留空字符串）
- topics：知识点列表（2-5个关键词，如 ["极限","洛必达法则"]）

规则：
1. 同一道题在真题和解析里都会出现，不要重复输出。
2. 如果当前给的是真题卷，answer/analysis 留空；如果是解析册，请把答案和解析填上。
3. 只输出 JSON 数组，不要加任何说明文字、不要用 ```json 包裹。
4. content/answer/analysis 里的 LaTeX 保持原样，不要转义。"""

MAX_RETRY = 3


def structure_year(client: OpenAI, year: int) -> list:
    """合并真题+解析，调模型拆题。"""
    exam_text = merge_year(year, "exam")
    sol_text = merge_year(year, "sol")

    # 分两次调用：先拆真题题干，再拆解析答案，最后按题号合并
    questions = {}

    # --- 真题卷：只拆题干 ---
    if exam_text.strip():
        raw = call_llm(client, exam_text, "真题卷（只有题目，没有答案解析）")
        for q in raw:
            key = q.get("qno", "").strip()
            questions[key] = {
                "year": year,
                "qtype": q.get("qtype", ""),
                "qno": key,
                "content": q.get("content", ""),
                "answer": "",
                "analysis": "",
                "topics": q.get("topics", []),
            }

    # --- 解析册：按页分批拆答案+解析，避免输出超长被截断 ---
    for page_file in sorted(config.OCR_DIR.glob(f"sol_{year}_p*.md")):
        page_text = page_file.read_text(encoding="utf-8").strip()
        if not page_text:
            continue
        raw = call_llm(client, page_text, "解析册某一页（含答案和详细解析过程）")
        for q in raw:
            key = q.get("qno", "").strip()
            if key in questions:
                # 同一题可能跨页，拼接内容（取非空者）
                if q.get("answer") and not questions[key]["answer"]:
                    questions[key]["answer"] = q["answer"]
                if q.get("analysis"):
                    if questions[key]["analysis"]:
                        questions[key]["analysis"] += "\n" + q["analysis"]
                    else:
                        questions[key]["analysis"] = q["analysis"]
                if q.get("topics"):
                    questions[key]["topics"] = list(
                        set(questions[key]["topics"] + q["topics"])
                    )
            else:
                questions[key] = {
                    "year": year,
                    "qtype": q.get("qtype", ""),
                    "qno": key,
                    "content": q.get("content", ""),
                    "answer": q.get("answer", ""),
                    "analysis": q.get("analysis", ""),
                    "topics": q.get("topics", []),
                }

    return list(questions.values())


def call_llm(client: OpenAI, text: str, kind_desc: str) -> list:
    """调用 DeepSeek 拆题，返回 list[dict]。"""
    prompt = STRUCTURE_PROMPT.format(kind=kind_desc)

    for attempt in range(MAX_RETRY):
        try:
            resp = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text[:12000]},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content.strip()
            # 模型可能返回 {"questions": [...]} 或直接 [...]
            obj = json.loads(raw)
            results: list[dict] = []
            if isinstance(obj, list):
                candidates = obj
            elif isinstance(obj, dict):
                # 找第一个 list 类型的 value
                candidates = None
                for k in ("questions", "data", "items", "result", "list"):
                    if k in obj and isinstance(obj[k], list):
                        candidates = obj[k]
                        break
                if candidates is None:
                    # 把所有 list 值拼起来
                    candidates = [v for v in obj.values() if isinstance(v, list)]
                    candidates = [x for sub in candidates for x in sub]
            else:
                candidates = []
            for item in candidates:
                if isinstance(item, dict) and ("content" in item or "qno" in item):
                    results.append(item)
            return results
        except Exception as e:  # noqa: BLE001
            print(f"    [重试 {attempt+1}/{MAX_RETRY}] {str(e)[:100]}")
            if attempt < MAX_RETRY - 1:
                time.sleep(2 ** attempt)
    print("    [警告] 该批次解析失败，跳过")
    return []


def main() -> None:
    if not config.LLM_API_KEY or config.LLM_API_KEY.startswith("请粘贴"):
        print("还没有配置 DeepSeek API Key！")
        print(f"    请编辑：{config.ROOT / '.env'}")
        sys.exit(1)

    client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)

    all_q = []
    for year in config.PROCESS_YEARS:
        print(f"[处理] {year} 年 ...")
        qs = structure_year(client, year)
        print(f"    拆出 {len(qs)} 道题")
        # 存单年文件方便检查
        (config.Q_DIR / f"questions_{year}.json").write_text(
            json.dumps(qs, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        all_q.extend(qs)

    out = config.Q_DIR / "all_questions.json"
    out.write_text(json.dumps(all_q, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-" * 50)
    print(f"共 {len(all_q)} 道题，已保存到 {out}")


if __name__ == "__main__":
    main()
