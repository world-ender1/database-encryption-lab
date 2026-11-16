# Nội dung slide chung — bản nghiệm thu 12 phút

Nguồn để xuất PPTX: `python -m scripts.export_group_slides`. Nội dung sử dụng kết quả nghiệm thu trên nhánh `main` ngày 16/11/2026 (kèm slide 10–12 dự phòng ảnh chụp thực tế). Chưa điền họ tên/MSSV ở Slide 1 vì nhóm cần tự điền thông tin cá nhân trước khi trình bày.

| Slide | Người, thời lượng | Nội dung trên slide | Lời dẫn chính |
|---|---|---|---|
| 1 | TV1, 0:00–0:30 | Đề tài, ba trường mã hóa, phân công | Dữ liệu demo là giả; khóa ngoài DB. |
| 2 | TV1, 0:30–2:00 | Khóa 32 byte; nonce 12 byte; tag 16 byte; AAD ID/field/version; A7 | Sai tag/AAD bị phát hiện; replay cùng ô vẫn hợp lệ. |
| 3 | TV2, 2:00–3:00 | Client → FastAPI → CryptoService → PostgreSQL | POST mã hóa trước lưu; GET kiểm quyền rồi giải mã. |
| 4 | TV2, 3:00–5:00 | Swagger POST/GET và SQL ciphertext | Chỉ xem màn hình sau khi đã authorize; không mở `.env`. SQL cho thấy hex/nonce, thêm test xác nhận đó là ciphertext. |
| 5 | TV3, 5:00–6:00 | Ma trận A1–A8 expected/actual | A1–A5 lab; A6/A7 test crypto; A8 test security. A7 là giới hạn. |
| 6 | TV3, 6:00–8:00 | Attack lab 401/403/409, kiểm DB/API restore | Chạy trên SV9001/SV9002 giả; script trả exit khác 0 nếu sai code hoặc mất dữ liệu. |
| 7 | TV3, 8:00–9:00 | [INSERT chart](figures/benchmark_insert.png) | n=10.000: 0,256 s → 1,086 s; +323,6%. |
| 8 | TV3, 9:00–10:00 | [SELECT chart](figures/benchmark_select.png) | n=10.000: 0,017 s → 0,314 s; +1.702,3%. n=100 có nhiễu đo. |
| 9 | Cả nhóm, 10:00–12:00 | Đạt/giới hạn/hỏi đáp | Ba field bảo vệ khỏi bản DB không khóa; metadata, lộ khóa và replay còn là giới hạn. |
| 10 | Phụ lục | Ảnh chụp Swagger POST 201 & GET 200 | Ảnh dự phòng đã che token. |
| 11 | Phụ lục | Ảnh chụp `psql` HEX & `attack_lab` A1–A5 | Ảnh dự phòng minh họa DB ciphertext và restore. |
| 12 | Phụ lục | Ảnh chụp `pytest` (`102 passed`) & GitHub Actions CI | Bằng chứng kiểm thử tự động trên `main`. |

Bộ ảnh minh chứng nằm tại `docs/evidence/screenshots/`. Nhóm chỉ cần điền họ tên/MSSV ở Slide 1 và tổng duyệt 12 phút trước khi gắn tag `v1.0.0`.
