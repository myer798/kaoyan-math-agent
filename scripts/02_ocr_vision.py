# -*- coding: utf-8 -*-
"""
第 2 步：调用视觉大模型，把每页图片逐页识别成 Markdown + LaTeX。
- 输入：data/images 里的 PNG（清单 manifest.json）
- 输出：data/ocr/{图片名}.md，每页一个文件
- 已识别过的页自动跳过；识别失败自动重试，可反复运行。

用法： python scripts/02_ocr_vision.py
"""
import base64
import io
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI  # noqa: E402
from PIL import Image  # noqa: E402
import config  # noqa: E402

MAX_SIDE = 1800          # 图片最长边限制（像素），兼顾清晰度与费用
WORKERS = 3              # 并发识别页数
MAX_RETRY = 4

PROMPT_COMMON = """你是“阅卷级”数学文档识别专家。请把这张考研数学（一）{doc_type}页面逐字转写为 Markdown。
严格遵守：
1. 所有数学内容一律用 LaTeX：行内公式用 $...$，独立成行的公式用 $$...$$；
   矩阵用 \\begin{{pmatrix}}，分段函数用 \\begin{{cases}}，上下限、求和积分等要完整。
2. 完整保留结构：大题标题（如“一、选择题”）、题号（1. 2. …）、选项 A. B. C. D.、小问 (1)(2)。
3. {extra}
4. 只转写图片中真实存在的内容：不要解题、不要补全、不要省略、不要写任何说明评论。
5. 忽略页眉页脚和页码；若本页没有任何题目内容（纯封面/空白），只输出 EMPTY。
6. 直接输出 Markdown 正文，不要用代码块包裹，不要输出“识别结果”之类的前缀。"""

PROMPTS = {
    "exam": PROMPT_COMMON.format(
        doc_type="真题卷", extra="这是题目卷，只有题干和选项，没有答案。"
    ),
    "sol": PROMPT_COMMON.format(
        doc_type="解析册",
        extra="每题的【答案】与【解析】（或【解】）标记必须原样保留，多小题的答案分别对应。",
    ),
}


def image_to_data_url(path: Path) -> str:
    """读取图片，必要时等比缩小，转成 JPEG data URL。"""
    im = Image.open(path).convert("RGB")
    if max(im.size) > MAX_SIDE:
        ratio = MAX_SIDE / max(im.size)
        im = im.resize((int(im.width * ratio), int(im.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def check_key() -> None:
    if not config.VISION_API_KEY or config.VISION_API_KEY.startswith("请粘贴"):
        print("还没有配置百炼 API Key！")
        print("请用记事本打开这个文件，把百炼 Key 粘到 VISION_API_KEY= 后面：")
        print(f"    {config.ROOT / '.env'}")
        sys.exit(1)


def ocr_one(client: OpenAI, task: dict) -> tuple[str, str, bool]:
    """识别单页，返回 (图片名, 状态信息, 是否成功)。"""
    stem = Path(task["image"]).stem
    out_path = config.OCR_DIR / f"{stem}.md"
    if out_path.exists():
        return task["image"], "跳过（已识别）", True

    data_url = image_to_data_url(config.IMG_DIR / task["image"])
    prompt = PROMPTS[task["kind"]]

    last_err = ""
    for attempt in range(1, MAX_RETRY + 1):
        try:
            resp = client.chat.completions.create(
                model=config.VISION_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }],
                temperature=0.0,
            )
            text = resp.choices[0].message.content.strip()
            if text == "EMPTY":
                text = ""
            out_path.write_text(text, encoding="utf-8")
            return task["image"], f"OK（{len(text)}字）", True
        except Exception as e:  # noqa: BLE001
            last_err = str(e)[:200]
            if attempt < MAX_RETRY:
                time.sleep(2 ** attempt)  # 2s,4s,8s…
    return task["image"], f"失败：{last_err}", False


def main() -> None:
    check_key()
    manifest = json.loads((config.IMG_DIR / "manifest.json").read_text(encoding="utf-8"))

    client = OpenAI(api_key=config.VISION_API_KEY, base_url=config.VISION_BASE_URL)

    todo = [
        t for t in manifest
        if not (config.OCR_DIR / f"{Path(t['image']).stem}.md").exists()
    ]
    print(f"共 {len(manifest)} 页，其中 {len(manifest) - len(todo)} 页已识别，本次识别 {len(todo)} 页")

    ok, fail = 0, []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(ocr_one, client, t): t for t in todo}
        for i, fut in enumerate(as_completed(futures), 1):
            image, status, success = fut.result()
            print(f"[{i}/{len(todo)}] {image}  {status}")
            if success:
                ok += 1
            else:
                fail.append(image)

    print("-" * 50)
    print(f"本次成功 {ok} 页，失败 {len(fail)} 页")
    if fail:
        print("失败页（重新运行本脚本即可重试）：" + "、".join(fail))


if __name__ == "__main__":
    main()
