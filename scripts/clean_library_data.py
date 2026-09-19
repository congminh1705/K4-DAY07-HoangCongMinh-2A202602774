#!/usr/bin/env python3
"""Làm sạch các file markdown trong data/thu-vien/

Loại bỏ:
- Thanh điều hướng menu đầu trang (navbar, breadcrumb, login form)
- Footer bản quyền và thông tin liên hệ cuối trang
- Các dòng trống liên tiếp sinh ra từ HTML
Giữ lại:
- Khối YAML Front Matter
- Tiêu đề và toàn bộ các điều khoản, quy định, số liệu, mốc thời gian
"""

import re
from pathlib import Path

TARGET_DIR = Path("data/Thuvien")

def clean_content(stem: str, body: str) -> str:
    # 1. Thay thế khoảng trắng vô hình \u00a0 và chuẩn hóa ngắt dòng
    text = body.replace("\u00a0", " ").replace("\r\n", "\n")

    # 2. Xóa các dòng trống thừa: chỉ giữ tối đa 1 dòng trống giữa các đoạn văn
    lines = text.split("\n")
    cleaned_lines = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_blank and cleaned_lines:
                cleaned_lines.append("")
                prev_blank = True
        else:
            cleaned_lines.append(line.rstrip())
            prev_blank = False

    return "\n".join(cleaned_lines).strip()


def main():
    md_files = sorted(TARGET_DIR.glob("*.md"))
    if not md_files:
        print(f"Không tìm thấy file .md nào trong {TARGET_DIR}")
        return

    print(f"Bắt đầu dọn dòng trống thừa cho {len(md_files)} tài liệu trong {TARGET_DIR}...")
    for path in md_files:
        raw = path.read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        if len(parts) < 3:
            continue

        front_matter = parts[1].strip()
        body = parts[2].strip()

        # Dọn dòng trống, giữ nguyên 100% nội dung gốc
        cleaned_body = clean_content(path.stem, body)

        clean_doc = f"---\n{front_matter}\n---\n\n{cleaned_body}\n"
        path.write_text(clean_doc, encoding="utf-8")

        lines_before = len(raw.splitlines())
        lines_after = len(clean_doc.splitlines())
        print(f"  ✓ {path.name:35} {lines_before:4d} dòng -> {lines_after:4d} dòng")

    print("\nHoàn tất dọn sạch toàn bộ dòng trống thừa!")


if __name__ == "__main__":
    main()
