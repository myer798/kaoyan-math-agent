# -*- coding: utf-8 -*-
"""
第 1 步：PDF → 高清 PNG 图片
把 config.PROCESS_YEARS 中每个年份的【真题】和【解析】逐页渲染成图片，
并生成清单 manifest.json 供第 2 步识别使用。
已存在的图片会自动跳过，可反复运行。

用法： python scripts/01_pdf_to_images.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymupdf  # noqa: E402
import config  # noqa: E402


def find_pdf(folder: Path, year: int) -> Path | None:
    """按年份前缀找 PDF，兼容两种命名：2022年...真题.pdf / 2025考研...真题.pdf"""
    hits = sorted(folder.glob(f"{year}*.pdf"))
    return hits[0] if hits else None


def main() -> None:
    manifest = []
    missing = []

    for year in config.PROCESS_YEARS:
        for kind, folder, label in (
            ("exam", config.EXAM_DIR, "真题"),
            ("sol", config.SOL_DIR, "解析"),
        ):
            pdf = find_pdf(folder, year)
            if pdf is None:
                missing.append(f"{year} {label}")
                print(f"[缺失] {year} 年{label} PDF 未找到")
                continue

            doc = pymupdf.open(pdf)
            for i in range(doc.page_count):
                image_name = f"{kind}_{year}_p{i + 1:02d}.png"
                out_path = config.IMG_DIR / image_name

                if not out_path.exists():
                    pix = doc[i].get_pixmap(dpi=config.DPI)
                    pix.save(out_path)

                manifest.append({
                    "image": image_name,
                    "year": year,
                    "kind": kind,          # exam=真题卷, sol=解析册
                    "page": i + 1,
                    "source_pdf": str(pdf),
                })
            print(f"[完成] {year} {label}：{doc.page_count} 页  <- {pdf.name}")
            doc.close()

    manifest_path = config.IMG_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("-" * 50)
    print(f"共生成 {len(manifest)} 张图片，清单：{manifest_path}")
    if missing:
        print("未找到的文件：" + "、".join(missing))


if __name__ == "__main__":
    main()
