# -*- coding: utf-8 -*-
"""
第 4 步：给每道题生成向量嵌入，建本地余弦检索索引。
- 调百炼 text-embedding-v3 把每道题的「题干+知识点」编码成向量
- 存为 data/index/vectors.json（含向量 + 原文，简单够用）

用法： python scripts/04_build_index.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI  # noqa: E402
import config  # noqa: E402

MAX_RETRY = 3


def embed_text(client: OpenAI, text: str) -> list[float]:
    text = text[:2000]  # 向量模型限长
    for attempt in range(MAX_RETRY):
        try:
            resp = client.embeddings.create(
                model=config.EMBED_MODEL, input=text
            )
            return resp.data[0].embedding
        except Exception as e:  # noqa: BLE001
            print(f"  [重试 {attempt+1}] {str(e)[:80]}")
            if attempt < MAX_RETRY - 1:
                time.sleep(2 ** attempt)
    return []


def main() -> None:
    if not config.VISION_API_KEY or config.VISION_API_KEY.startswith("请粘贴"):
        print("还没有配置百炼 API Key（向量模型也用百炼）！")
        sys.exit(1)

    qs = json.loads((config.Q_DIR / "all_questions.json").read_text(encoding="utf-8"))
    print(f"共 {len(qs)} 道题，开始生成向量 ...")

    client = OpenAI(api_key=config.VISION_API_KEY, base_url=config.VISION_BASE_URL)

    records = []
    for i, q in enumerate(qs, 1):
        # 把题目关键信息拼成一段文本用于嵌入
        embed_text_input = (
            f"题型:{q.get('qtype','')} 题号:{q.get('qno','')} "
            f"知识点:{','.join(q.get('topics',[]))} "
            f"题干:{q.get('content','')[:300]}"
        )
        vec = embed_text(client, embed_text_input)
        if vec:
            records.append({**q, "embedding": vec})
        else:
            records.append(q)  # 失败了也保留原题，只是没向量
        print(f"  [{i}/{len(qs)}] {q['year']}年 {q['qtype']} 第{q['qno']}题  向量维度:{len(vec)}")

    out = config.INDEX_DIR / "vectors.json"
    out.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    has_vec = sum(1 for r in records if r.get("embedding"))
    print(f"完成！{has_vec}/{len(records)} 道题有向量，索引：{out}")


if __name__ == "__main__":
    main()
