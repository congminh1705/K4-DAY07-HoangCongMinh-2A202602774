#!/usr/bin/env python3
"""Script kiểm tra nghiệm thu Checkpoint 2 theo chuẩn Lab 07 L3A"""

import csv
import re
from pathlib import Path

TARGET_DIR = Path("data/Thuvien")
REQ = ["doc_id", "title", "source_url", "retrieved_at", "document_version", "audience"]

def main():
    if not TARGET_DIR.exists():
        print(f"Thư mục {TARGET_DIR} không tồn tại!")
        return

    mds = sorted(TARGET_DIR.glob("*.md"))
    sources_path = TARGET_DIR / "sources.csv"
    
    if not sources_path.exists():
        print(f"Không tìm thấy {sources_path}!")
        return

    with sources_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    ids = []
    auds = {}
    print("=== DANH SÁCH TÀI LIỆU ===")
    for p in mds:
        raw = p.read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        if len(parts) < 3:
            print(f"{p.name:42} THIEU FRONTMATTER")
            continue
            
        fm = {}
        for line in parts[1].splitlines():
            m = re.match(r"^(\w+):\s*\"?([^\"]+)\"?\s*$", line.strip())
            if m:
                fm[m.group(1)] = m.group(2).strip()

        doc_id = fm.get("doc_id", "").strip('"')
        audience = fm.get("audience", "").strip('"')
        ids.append(doc_id)
        auds[audience] = auds.get(audience, 0) + 1

        is_ok = all(k in fm for k in REQ) and doc_id == p.stem
        status = "OK" if is_ok else "THIEU METADATA"
        print(f"{p.name:42} {status}")

    print("\n=== KẾT QUẢ CHECKPOINT 2 ===")
    print(f"Số file  : {len(mds)} (chuẩn yêu cầu: 5-10 file)")
    csv_match = "khop" if sorted(r.get("doc_id", "") for r in rows) == sorted(ids) else "LECH"
    print(f"CSV      : {csv_match}")
    print(f"Audience : {auds}")
    
    if len(auds) >= 2:
        print("Audience phân hóa tốt (đủ điều kiện làm metadata filter) ✓")
    else:
        print("Cần có ít nhất 2 nhóm audience khác nhau!")

if __name__ == "__main__":
    main()
