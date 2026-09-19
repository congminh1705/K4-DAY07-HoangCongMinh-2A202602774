# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hoàng Công Minh - 02774
**Nhóm:** G19
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai embedding có hướng gần nhau trong không gian vector, nên hai đoạn văn có ý nghĩa hoặc ngữ cảnh gần nhau. Điểm cao không nhất thiết có nghĩa hai câu dùng cùng các từ.

**Ví dụ có độ tương tự CAO:**
- Câu A: “Sinh viên có thể gia hạn thời hạn mượn sách trực tuyến.”
- Câu B: “Người học được phép kéo dài kỳ hạn mượn tài liệu qua hệ thống thư viện.”
- Tại sao tương đồng: Hai câu diễn đạt cùng quy định về gia hạn mượn tài liệu, dù dùng từ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: “Thư viện yêu cầu trả sách đúng hạn.”
- Câu B: “Học bổng được xét dựa trên kết quả học tập.”
- Tại sao khác: Hai câu nói về hai dịch vụ đại học khác nhau và không cùng mục đích thông tin.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine đo góc giữa các vector nên tập trung vào hướng ngữ nghĩa và ít bị ảnh hưởng bởi độ lớn vector. Điều này phù hợp với embedding văn bản, nơi hai đoạn cùng nghĩa nên gần nhau về hướng dù độ dài hoặc độ lớn biểu diễn có thể khác.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)`
> *Đáp án:* **23 chunks.** Kết quả cũng khớp khi chạy `FixedSizeChunker` của repo.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng thành `ceil((10000 - 100) / (500 - 100)) = ceil(24.75) = 25` chunks. Overlap lớn hơn giúp giữ ngữ cảnh nằm ở ranh giới giữa hai chunk, nên truy xuất ít bỏ sót thông tin liên tục hơn; đổi lại cần lưu trữ và xử lý nhiều chunk hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết câu, nhờ đó dấu câu vẫn nằm trong chunk. Text rỗng hoặc chỉ có khoảng trắng trả về `[]`; giới hạn câu mỗi chunk được ép tối thiểu là 1. Giải pháp chưa phân biệt chính xác chữ viết tắt như `TS.`/`v.v.` hoặc dấu chấm trong số thập phân.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán ưu tiên tách theo đoạn, dòng, câu, từ rồi đến ký tự; các mảnh liền kề được gom lại tới gần `chunk_size` để tránh chunk vụn. Khi mảnh vẫn quá dài, hàm đệ quy dùng separator nhỏ hơn. Base case là mảnh đã đủ ngắn, không còn separator, hoặc separator rỗng thì cắt theo kích thước cố định.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Store giữ record trong bộ nhớ gồm id, content, metadata đã sao chép và embedding. `search` embed query, tính dot product với embedding từng record, sắp xếp giảm dần rồi lấy top-k; với embedding chuẩn hóa, dot product tương đương cosine similarity.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Metadata được lọc trước khi tính điểm, để top-k chỉ cạnh tranh giữa các chunk hợp lệ. `delete_document` loại toàn bộ record có `metadata['doc_id']` khớp và trả về trạng thái có xóa được record nào hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k, đánh số từng chunk kèm `doc_id`, rồi đưa vào prompt dưới phần Context. Prompt buộc LLM chỉ dùng ngữ cảnh và trích dẫn `[1]`, `[2]`; nếu không có kết quả, agent trả thông báo thay vì gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
pytest tests/ -v
======================== 42 passed, 1 warning in 0.06s ========================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên gia hạn sách trực tuyến. | Người học kéo dài hạn mượn tài liệu qua thư viện. | Cao | -0.059 | Không |
| 2 | Thư viện yêu cầu trả sách đúng hạn. | Học bổng xét theo kết quả học tập. | Thấp | 0.029 | Có |
| 3 | Mượn liên thư viện tối đa hai tài liệu. | Dịch vụ liên thư viện cho phép mượn hai tài liệu. | Cao | -0.039 | Không |
| 4 | Thanh toán ra trường cần trả sách. | Sinh viên cần hoàn tất công nợ sách trước tốt nghiệp. | Cao | -0.085 | Không |
| 5 | Phòng học nhóm mở cho sinh viên. | Gia hạn sách thực hiện trên thiết bị tự động. | Thấp | -0.027 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Các cặp cùng nghĩa ở 1, 3 và 4 lại có điểm âm. Đây là giới hạn dự kiến của `MockEmbedder`: nó sinh vector từ MD5 của chuỗi, không biểu diễn ngữ nghĩa. Vì vậy, các kết quả này chỉ xác minh công thức cosine/pipeline; đánh giá ngữ nghĩa phải dùng multilingual embedding thật.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Giới hạn mượn sách của người dùng? | FAQ HUIT, nhưng chunk top-1 không chứa dòng “tối đa 3 quyển/10 ngày”. | 0.303 | Có cùng tài liệu nhưng **không** trả lời được. | Không thể ground đáp án từ chunk này. |
| 2 | Mượn sách tham khảo VNUA? | Thủ tục thanh toán ra trường HUST, sai nguồn. | 0.415 | Không. | Không thể trả lời theo ngữ cảnh. |
| 3 | Mượn liên thư viện HUIT? | FAQ HUIT, sai mục; không có mức 2 tài liệu/20 ngày. | 0.345 | Không. | Không thể trả lời theo ngữ cảnh. |
| 4 | Thanh toán thư viện trước khi ra trường? | Quy định làm thẻ bạn đọc, sai quy trình. | 0.338 | Không. | Không thể trả lời theo ngữ cảnh. |
| 5 | Các bước gia hạn tự động? | Hướng dẫn tự động HUIT, nhưng chunk top-1 không có bước “Chọn nút GIA HẠN”. | 0.252 | Có cùng tài liệu nhưng **không** trả lời được. | Không thể ground đáp án từ chunk này. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **0 / 5** theo tiêu chí nghiêm ngặt: chunk phải chứa thông tin trả lời (không chỉ đúng `doc_id`).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Đúng tài liệu chưa đủ: section được truy xuất phải thực sự chứa số liệu hoặc bước trả lời. Metadata filter thu hẹp ứng viên theo đối tượng, nhưng không thể thay thế embedding có ngữ nghĩa; benchmark dùng mock phải được xem là kiểm thử pipeline, không phải thước đo retrieval thực tế.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 4 / 10 |
| **Tổng phần cá nhân** | **54 / 60** |
