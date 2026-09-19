# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G19
**Thành viên:** Đinh Quang Lâm - 02875; Đào Quang Cảnh - 02542; Hoàng Công Minh - 02774
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

### Phân công vai trò

| Thành viên | Vai trò | Công việc chính | Sản phẩm phụ trách |
|---|---|---|---|
| Đinh Quang Lâm — 02875 | Data / Corpus | Chốt 10 tài liệu; kiểm tra nguồn công khai, YAML front matter, `sources.csv` và các trường `audience`/`category`. | `REPORT_NHOM` mục 1 — Lựa chọn tài liệu |
| Đào Quang Cảnh — 02542 | Queries / Evaluation | Viết đúng 5 benchmark query, gold answer và marker đáp án; thiết kế câu A/B cần `metadata_filter={"audience": "student"}`; kiểm tra kết quả ở cấp nội dung chunk. | `REPORT_NHOM` mục 3 — Câu hỏi và chất lượng truy xuất |
| Hoàng Công Minh — 02774 | Strategy / Benchmark | So sánh baseline; xây dựng chunker theo heading; chạy `bench.py`; phân tích A/B metadata filter và failure case. | `REPORT_NHOM` mục 2 và mục 4 — Chiến lược, benchmark và demo |

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

**Người phụ trách:** Đinh Quang Lâm (02875) — Data / Corpus.

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và dịch vụ thư viện đại học

**Tại sao nhóm chọn chủ đề này?**
> Các quy định thư viện có nguồn công khai, cấu trúc rõ và chứa nhiều thông tin có thể kiểm chứng như đối tượng phục vụ, thời hạn mượn, quy trình làm thẻ và cách sử dụng cơ sở vật chất. Chủ đề cũng phù hợp để đánh giá tác dụng của metadata `audience` và so sánh các chiến lược chunking trên văn bản quy định có nhiều mục.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Nội quy Thư viện Đại học Ngoại thương | https://hcmc.ftu.edu.vn/thu-vien/tin-tuc-thu-vien/noi-quy-thu-vien/ | 2026-09-19 / 2026-08-10 | 4.218 | `audience=all`, `category=rules`, `language=vi` |
| 2 | Nội quy Thư viện Đại học Công nghiệp Hà Nội | https://lib.haui.edu.vn/opac80/ChinhSach.aspx | 2026-09-19 / `not-stated` | 7.832 | `audience=all`, `category=policy`, `language=vi` |
| 3 | Quy định sử dụng Thư viện HUIT | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 / `not-stated` | 13.345 | `audience=all`, `category=policy`, `language=vi` |
| 4 | Mượn trả tài liệu VNUA | https://infolib.vnua.edu.vn/dich-vu/muon-tra-tai-lieu | 2026-09-19 / `not-stated` | 1.457 | `audience=all`, `category=borrowing`, `language=vi` |
| 5 | Dịch vụ sử dụng phòng họp nhóm HUST | https://library.hust.edu.vn/vi/node/1362 | 2026-09-19 / `not-stated` | 1.717 | `audience=student`, `category=facility`, `language=vi` |
| 6 | Mượn trả tài liệu đọc tại chỗ HUST | https://library.hust.edu.vn/vi/node/1300 | 2026-09-19 / `not-stated` | 1.761 | `audience=student`, `category=circulation`, `language=vi` |
| 7 | Quy trình làm thẻ thư viện cho cán bộ giảng viên HUST | https://library.hust.edu.vn/vi/node/1034 | 2026-09-19 / `not-stated` | 1.298 | `audience=faculty`, `category=service`, `language=vi` |
| 8 | Quy định làm thẻ bạn đọc thư viện HUST | https://library.hust.edu.vn/vi/node/305 | 2026-09-19 / `not-stated` | 1.479 | `audience=student`, `category=service`, `language=vi` |
| 9 | Thủ tục thanh toán ra trường tại thư viện HUST | https://library.hust.edu.vn/vi/node/61 | 2026-09-19 / `not-stated` | 2.344 | `audience=student`, `category=graduation`, `language=vi` |
| 10 | Quy định phòng đọc tự chọn HUST | https://library.hust.edu.vn/vi/node/57 | 2026-09-19 / `not-stated` | 2.160 | `audience=all`, `category=facility`, `language=vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi | `haui-library-policy` | Định danh duy nhất, liên kết chunk với tài liệu gốc và hỗ trợ đối chiếu benchmark. |
| `title` | Chuỗi | `Nội quy Thư viện Đại học Công nghiệp Hà Nội` | Hiển thị nguồn dễ hiểu và bổ sung ngữ cảnh chủ đề cho kết quả. |
| `source_url` | URL | `https://lib.haui.edu.vn/opac80/ChinhSach.aspx` | Truy vết và kiểm chứng thông tin tại nguồn công khai. |
| `retrieved_at` | Ngày `YYYY-MM-DD` | `2026-09-19` | Cho biết thời điểm thu thập để đánh giá độ mới của dữ liệu. |
| `document_version` | Chuỗi/ngày | `2026-08-10`, `not-stated` | Phân biệt phiên bản hoặc minh bạch khi nguồn không công bố phiên bản. |
| `audience` | Enum | `student`, `faculty`, `all` | Lọc tài liệu theo đúng nhóm người dùng trước khi similarity search. |
| `department` | Chuỗi | `library` | Giới hạn truy xuất theo đơn vị phụ trách khi corpus mở rộng. |
| `category` | Enum | `policy`, `facility`, `service` | Lọc theo loại nhu cầu hoặc dịch vụ thư viện. |
| `language` | Mã ngôn ngữ | `vi` | Hỗ trợ chọn tài liệu đúng ngôn ngữ truy vấn. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

**Người phụ trách:** Hoàng Công Minh (02774) — Strategy / Benchmark.

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `haui-library-policy.md` | FixedSizeChunker (`fixed_size`) | 15 | 494,1 | Trung bình; có thể cắt giữa điều khoản |
| `haui-library-policy.md` | SentenceChunker (`by_sentences`) | 29 | 253,0 | Tốt ở câu hoàn chỉnh, nhưng dễ tách sai chữ viết tắt |
| `haui-library-policy.md` | RecursiveChunker (`recursive`) | 19 | 387,5 | Tốt; ưu tiên ranh giới đoạn và câu |
| `huit-library-usage-policy.md` | FixedSizeChunker (`fixed_size`) | 26 | 492,0 | Trung bình; chunk đều nhưng không theo mục |
| `huit-library-usage-policy.md` | SentenceChunker (`by_sentences`) | 37 | 343,9 | Khá; giữ dấu câu nhưng có chunk dài |
| `huit-library-usage-policy.md` | RecursiveChunker (`recursive`) | 32 | 397,5 | Tốt; cân bằng kích thước và ranh giới nội dung |
| `thu-tuc-thanh-toan-ra-truong.md` | FixedSizeChunker (`fixed_size`) | 4 | 499,5 | Trung bình; có thể cắt giữa các bước |
| `thu-tuc-thanh-toan-ra-truong.md` | SentenceChunker (`by_sentences`) | 3 | 663,7 | Giữ câu nhưng vượt kích thước mục tiêu |
| `thu-tuc-thanh-toan-ra-truong.md` | RecursiveChunker (`recursive`) | 5 | 398,0 | Tốt; các bước tương đối mạch lạc |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 3 — Hoàng Công Minh**
- **Loại chiến lược:** Custom `HeadingChunker`
- **Cấu hình:** `chunk_size=500`, không overlap ở cấp section, `RecursiveChunker` làm fallback cho section dài.
- **Mô tả & lý do chọn cho chủ đề này:** Tôi tách văn bản tại tiêu đề Markdown, `Chương`, `Điều`, mục đánh số và `Bước`, vì các tài liệu thư viện là quy định và thủ tục đã được người viết chia sẵn thành những đơn vị ngữ nghĩa. Cách chia này hạn chế việc cắt ngang một điều khoản như fixed-size. Nếu một mục dài hơn 500 ký tự, chiến lược hạ xuống `RecursiveChunker` và gắn lại tiêu đề vào từng mảnh con để các chunk sau không mất chủ đề.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    HEADING = re.compile(
        r"^(?:#{1,6}\s+|Chương\s+|Điều\s+|\d+\.\s+|Bước\s+\d+[:.]?)",
        re.I,
    )

    def __init__(self, chunk_size=500):
        self.chunk_size = chunk_size
        self.fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text):
        sections, heading, content = [], "", []
        for line in text.splitlines():
            line = line.strip()
            if self.HEADING.match(line):
                if heading or content:
                    sections.append((heading, "\n".join(content).strip()))
                heading, content = line, []
            elif line:
                content.append(line)
        if heading or content:
            sections.append((heading, "\n".join(content).strip()))

        chunks = []
        for heading, content in sections:
            section = f"{heading}\n{content}".strip()
            if len(section) <= self.chunk_size:
                chunks.append(section)
            else:
                for piece in self.fallback.chunk(content):
                    chunks.append(f"{heading}\n{piece}".strip())
        return chunks
```
- **Kết quả riêng:** Tạo 137 chunk từ 10 tài liệu và đạt `2/10` với `MockEmbedder`. Q3 lấy đúng chunk chứa yêu cầu ảnh làm thẻ cán bộ ở top-1; 1/5 câu có chunk chứa đáp án trong top-3.
- **Điểm mạnh:** Giữ cấu trúc điều khoản/quy trình, bảo toàn tiêu đề khi phải chia nhỏ và cho phép truy vết chunk về đúng mục nguồn.
- **Điểm yếu:** Các dòng `Bước` có thể bị tách quá nhỏ, làm tăng số chunk và khiến nhiều section cùng tài liệu cạnh tranh trong top-k. Hiệu quả retrieval hiện chưa thể đánh giá chắc chắn vì benchmark đang dùng mock embedding không có ngữ nghĩa.

**Thành viên 1 — Đinh Quang Lâm**
- **Loại chiến lược:** `FixedSizeChunker`
- **Cấu hình:** `chunk_size=500`, `overlap=50`.
- **Mô tả & lý do chọn:** Lâm chọn fixed-size làm đường cơ sở vì thuật toán đơn giản, tốc độ nhanh và tạo các chunk có kích thước tương đối đồng đều. Overlap 50 ký tự giúp giữ lại một phần ngữ cảnh ở ranh giới giữa hai chunk, phù hợp để so sánh với recursive và heading chunking.
- **Code sử dụng:**
```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(content)
```
- **Kết quả riêng:** Tạo 80 chunk từ 10 tài liệu và đạt `1/10` với `MockEmbedder`. Q3 có chunk chứa đáp án trong top-3 nhưng không đứng top-1.
- **Điểm mạnh:** Ít chunk nhất, dễ triển khai, kích thước ổn định và có overlap để giảm mất ngữ cảnh tại ranh giới.
- **Điểm yếu:** Có thể cắt giữa câu, bước hoặc điều khoản; không tận dụng cấu trúc tự nhiên của văn bản quy định.

**Thành viên 2 — Đào Quang Cảnh**
- **Loại chiến lược:** `RecursiveChunker`
- **Cấu hình:** `chunk_size=500`, separator ưu tiên `["\n\n", "\n", ". ", " ", ""]`.
- **Mô tả & lý do chọn:** Cảnh chọn recursive chunking vì chiến lược này ưu tiên ranh giới đoạn, dòng và câu trước khi phải cắt cứng theo ký tự. Cách làm phù hợp với tài liệu thư viện có nhiều đoạn quy định và danh sách, đồng thời giảm nguy cơ cắt ngang ý so với fixed-size.
- **Code sử dụng:**
```python
chunker = RecursiveChunker(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=500,
)
chunks = chunker.chunk(content)
```
- **Kết quả riêng:** Tạo 87 chunk từ 10 tài liệu và đạt `1/10` với `MockEmbedder`. Q3 có chunk chứa đáp án trong top-3 nhưng chưa đứng top-1.
- **Điểm mạnh:** Giữ ranh giới ngữ nghĩa tốt hơn fixed-size, gom các mảnh nhỏ để hạn chế chunk vụn và có fallback khi văn bản không chứa separator.
- **Điểm yếu:** Không nhận biết trực tiếp cấu trúc `Chương`/`Điều`/`Bước`; kết quả retrieval vẫn bị chi phối mạnh bởi mock embedding.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Đinh Quang Lâm | Fixed size (500, overlap 50) | 1 | Ít chunk nhất (80), đơn giản và ổn định | Cắt giữa điều khoản/bước; chunk đúng ở Q3 chỉ đứng top-2/3 |
| Đào Quang Cảnh | Recursive (500) | 1 | Ưu tiên ranh giới đoạn/câu, chỉ tạo 87 chunk | Không tận dụng trực tiếp cấu trúc `Điều`/`Bước`; Q3 chưa ở top-1 |
| Hoàng Công Minh | Heading + recursive fallback | 2 | Q3 đúng ở top-1; giữ tiêu đề cho từng section | Tạo 137 chunk nhỏ, tăng cạnh tranh giữa các section cùng tài liệu |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Trong lần chạy bằng mock embedding, HeadingChunker đạt điểm cao nhất (2/10) vì giữ mục “Thủ tục và địa điểm đăng ký” nguyên vẹn và đưa đáp án Q3 lên top-1. Tuy nhiên chênh lệch này chưa đủ để kết luận về retrieval ngữ nghĩa: mock embedding là nhiễu và HeadingChunker tạo nhiều chunk hơn, nên cần chạy lại bằng embedding đa ngôn ngữ thật trước khi chọn chiến lược triển khai.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

**Người phụ trách:** Đào Quang Cảnh (02542) — Queries / Evaluation.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Theo HUST, đến nhận phòng học nhóm muộn quá bao lâu thì lịch đặt phòng bị hủy? | Nếu đến muộn quá 15 phút, thư viện có quyền hủy lịch và cấp phòng cho nhóm khác. | `dich-vu-su-dung-phong-hop-nhom` — mục “3. Thực hiện” |
| 2 | Khi mượn tài liệu đọc tại chỗ ở HUST, mỗi lần được lấy tối đa bao nhiêu quyển và phải trả ở đâu, lúc nào? | Mỗi lần lấy tối đa 2 quyển; tài liệu phải được trả trước 17h30 tại phòng 411. | `muon-tra-tai-lieu-inhouse` — “Quy trình mượn” và “Quy trình trả” |
| 3 | Ảnh làm thẻ thư viện cho cán bộ HUST phải đáp ứng yêu cầu gì? | Ảnh tối thiểu 300 pixel, tỷ lệ 1x1, nền trắng và gửi tới `tttts@hust.edu.vn`. | `quy-trinh-lam-the-can-bo` — mục “2. Thủ tục và địa điểm đăng ký” |
| 4 | Theo HaUI, sinh viên được mượn tối đa bao nhiêu tài liệu và trong thời gian bao lâu? | Mỗi lần tối đa 5 tài liệu; tài liệu tham khảo tối đa 15 ngày và giáo trình tối đa một học kỳ. | `haui-library-policy` — Điều 5 “Quy định mượn trả tài liệu” |
| 5 | Tôi cần làm gì để hoàn tất thủ tục công nợ tại thư viện? | Kiểm tra tài khoản/email, trả sách và xử lý vi phạm, kiểm tra lại tài khoản rồi đề nghị cán bộ phòng mượn khóa tài khoản. | `thu-tuc-thanh-toan-ra-truong` — mục sinh viên xét tốt nghiệp; lọc `audience=student` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Nhận phòng nhóm muộn | Heading | Không | Mock embedding xếp các chunk cùng chủ đề thư viện gần như ngẫu nhiên. |
| 2 | Mượn tài liệu in-house | Heading | Không | Top-1 đúng tài liệu nhưng sai section, minh họa vì sao không thể chỉ chấm theo `doc_id`. |
| 3 | Ảnh làm thẻ cán bộ | Heading + filter `faculty` | Có | Chunk chứa `300 Pixel` đứng top-1. |
| 4 | Thời hạn mượn của sinh viên HaUI | Heading | Không | Có tài liệu HaUI ở top-3 nhưng chunk không chứa đáp án. |
| 5 | Hoàn tất công nợ thư viện | Heading + filter `student` | Không | Filter loại tài liệu `all`/`faculty`, nhưng mock embedding vẫn chọn sai chunk sinh viên. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Filter giúp rõ nhất ở câu 3: chỉ còn tài liệu `faculty` và chunk chứa yêu cầu ảnh đứng top-1. Ở câu 5, A/B cho thấy filter `student` loại toàn bộ kết quả `all` và `faculty`, nhưng chưa bảo đảm top-3 có đáp án vì `MockEmbedder` không biểu diễn ngữ nghĩa; filter cải thiện tập ứng viên chứ không thể sửa chất lượng embedding.

### Failure case và đề xuất cải thiện

**Failure case:** Ở câu 2, HeadingChunker trả `muon-tra-tai-lieu-inhouse` ở top-1 nên nếu chỉ chấm theo `doc_id` sẽ bị coi là đúng. Tuy nhiên chunk được lấy chỉ chứa “Bước 5: Nhận tài liệu...” và không chứa “tối đa 2 quyển” hoặc “trả trước 17h30 tại phòng 411”, nên agent không đủ căn cứ trả lời.

**Nguyên nhân:** Các bước của cùng một quy trình bị tách thành nhiều chunk nhỏ; mock cosine chỉ tạo xếp hạng giả ngẫu nhiên và không ưu tiên chunk chứa số liệu cần thiết.

**Đề xuất:** Gom toàn bộ “Quy trình mượn” và “Quy trình trả” thành một section, hoặc thêm overlap/parent heading cho các bước con; dùng embedding đa ngôn ngữ thật và cân nhắc hybrid search theo từ khóa để tăng khả năng tìm đúng số liệu, thời gian và số phòng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Người phụ trách tổng hợp:** Hoàng Công Minh (02774) — Strategy / Benchmark; cả ba thành viên cùng trình bày phần việc của mình.

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Đúng `doc_id` chưa có nghĩa là đúng chunk: Q2 trả đúng tài liệu in-house ở top-1 nhưng section không chứa con số cần trả lời.
> - Metadata filter loại hiệu quả tài liệu sai đối tượng, nhưng không thể bù cho embedding không hiểu ngữ nghĩa.
> - Heading chunking giữ cấu trúc quy định tốt hơn, đổi lại tăng từ 80–87 chunk lên 137 chunk và làm các section cùng chủ đề cạnh tranh nhau.

**Bài học rút ra khi so sánh trong nhóm:**
> Fixed-size tạo ít chunk nhưng có thể cắt giữa điều khoản; recursive giữ ranh giới tự nhiên tốt hơn; heading giữ đúng cấu trúc nghiệp vụ nhưng dễ tạo nhiều mảnh nhỏ. Vì vậy phải chấm ở mức nội dung chứa đáp án và quan sát cả số chunk/độ mạch lạc, không chỉ nhìn score hoặc `doc_id`.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ dùng embedding đa ngôn ngữ thật, bổ sung tìm kiếm từ khóa/BM25 cho các con số và tên phòng, đồng thời gom các `Bước` liên tiếp vào một section thay vì tách quá nhỏ. Với câu Q2, có thể dùng overlap hoặc giữ toàn bộ “Quy trình mượn/trả” trong cùng một chunk để đáp án không bị chia qua hai mảnh.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 2 / 10 |
| Thuyết trình (Demo) | Chưa tự chấm / 5 |
| **Tổng phần nhóm** | **27 / 40 + điểm demo** |