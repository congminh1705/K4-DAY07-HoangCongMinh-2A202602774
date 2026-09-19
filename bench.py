"""Benchmark retrieval strategies for the library-policy corpus.

Run: ``python bench.py``
The only line an individual needs to change to compare a strategy is
``CHUNKER = HeadingChunker(...)`` below.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from src import Document, EmbeddingStore, FixedSizeChunker, RecursiveChunker, SentenceChunker, _mock_embed


DATA_DIR = Path("data/Thuvien")
# The group selected these ten source documents for the submitted benchmark.
# Other downloaded pages remain available as non-benchmark working material.
SELECTED_DOC_IDS = {
    "dich-vu-su-dung-phong-hop-nhom", "ftu-library-rules", "haui-library-policy",
    "huit-interlibrary-loan", "huit-library-faq", "huit-self-check",
    "quy-dinh-lam-the-ban-doc", "quy-trinh-lam-the-can-bo",
    "thu-tuc-thanh-toan-ra-truong", "vnua-library-borrowing",
}

BENCHMARKS = [
    {
        "query": "Người dùng được mượn tối đa bao nhiêu sách và trong bao lâu?",
        "gold_doc_id": "huit-library-faq",
        "answer_marker": "tối đa 3 quyển",
        "filter": {"audience": "student"},
    },
    {
        "query": "Sách tham khảo của VNUA được mượn bao nhiêu cuốn, trong bao lâu và gia hạn thế nào?",
        "gold_doc_id": "vnua-library-borrowing",
        "answer_marker": "5 cuốn/20 ngày",
        "filter": None,
    },
    {
        "query": "Dịch vụ mượn liên thư viện HUIT cho mượn bao nhiêu tài liệu và thời hạn bao lâu?",
        "gold_doc_id": "huit-interlibrary-loan",
        "answer_marker": "2 tài liệu/1 lần mượn",
        "filter": None,
    },
    {
        "query": "Sinh viên cần làm gì để hoàn tất thanh toán thư viện trước khi ra trường?",
        "gold_doc_id": "thu-tuc-thanh-toan-ra-truong",
        "answer_marker": "Trả sách đang mượn",
        "filter": {"audience": "student"},
    },
    {
        "query": "Gia hạn tài liệu tự động được thực hiện theo các bước nào?",
        "gold_doc_id": "huit-self-check",
        "answer_marker": "Chọn nút GIA HẠN",
        "filter": {"audience": "student"},
    },
]


def parse_markdown(path: Path) -> tuple[dict[str, str], str]:
    """Return simple YAML front matter and body without adding a YAML package."""
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", raw, flags=re.DOTALL)
    if not match:
        return {"doc_id": path.stem}, raw.strip()
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, match.group(2).strip()


class HeadingChunker:
    """Keep each Markdown heading and its section together when possible."""

    def __init__(self, chunk_size: int = 900) -> None:
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = re.split(r"(?m)(?=^#{1,6}\s+)", text.strip())
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            heading = section.splitlines()[0] if section.startswith("#") else ""
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            for child in self._fallback.chunk(section):
                # Every fragment retains its section label after recursive split.
                chunks.append(child if not heading or child.startswith(heading) else f"{heading}\n{child}")
        return chunks


def load_chunked_documents(chunker: object) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, body = parse_markdown(path)
        doc_id = metadata.get("doc_id", path.stem)
        if doc_id not in SELECTED_DOC_IDS:
            continue
        for index, chunk in enumerate(chunker.chunk(body)):  # type: ignore[attr-defined]
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={**metadata, "doc_id": doc_id, "chunk_index": index},
                )
            )
    return documents


def make_chunker(name: str) -> object:
    return {
        "heading": HeadingChunker(chunk_size=900),
        "fixed": FixedSizeChunker(chunk_size=900, overlap=100),
        "sentence": SentenceChunker(max_sentences_per_chunk=3),
        "recursive": RecursiveChunker(chunk_size=900),
    }[name]


def run_benchmark(strategy: str) -> list[str]:
    chunker = make_chunker(strategy)
    documents = load_chunked_documents(chunker)
    store = EmbeddingStore(collection_name="library_benchmark", embedding_fn=_mock_embed)
    store.add_documents(documents)
    lines = [
        f"Strategy: {chunker.__class__.__name__}",
        f"Loaded {len(documents)} chunks from {len(SELECTED_DOC_IDS)} selected documents.",
        "Embedding backend: mock (MD5-based; rankings are not semantic evidence).",
        "",
    ]

    for number, benchmark in enumerate(BENCHMARKS, start=1):
        metadata_filter = benchmark["filter"]
        results = store.search_with_filter(benchmark["query"], top_k=3, metadata_filter=metadata_filter)
        lines.append(f"Q{number}. {benchmark['query']}")
        lines.append(f"  filter={metadata_filter}; gold={benchmark['gold_doc_id']}; marker={benchmark['answer_marker']!r}")
        for rank, result in enumerate(results, start=1):
            marker_found = benchmark["answer_marker"].casefold() in result["content"].casefold()
            lines.append(
                f"  {rank}. score={result['score']:.3f} doc_id={result['metadata']['doc_id']} "
                f"chunk={result['metadata']['chunk_index']} marker={marker_found}"
            )
        if metadata_filter:
            unfiltered = store.search(benchmark["query"], top_k=3)
            lines.append("  A/B (without filter): " + ", ".join(result["metadata"]["doc_id"] for result in unfiltered))
        lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the library retrieval benchmark.")
    parser.add_argument("--strategy", choices=("heading", "fixed", "sentence", "recursive"), default="heading")
    parser.add_argument("--all", action="store_true", help="Run all four strategies for comparison.")
    parser.add_argument("--output", type=Path, default=Path("ket_qua_benchmark.txt"))
    args = parser.parse_args()

    strategies = ("heading", "fixed", "sentence", "recursive") if args.all else (args.strategy,)
    output: list[str] = []
    for strategy in strategies:
        if output:
            output.extend(["=" * 72, ""])
        output.extend(run_benchmark(strategy))

    report = "\n".join(output)
    print(report)
    args.output.write_text(report + "\n", encoding="utf-8")
    print(f"Saved benchmark output to {args.output}")


if __name__ == "__main__":
    main()
