# feat(api): complete encrypted student CRUD and integrated verification

Main đã có AES-GCM của TV1 nhưng chưa có API/DB. Thay đổi bổ sung FastAPI CRUD, PostgreSQL schema, Docker và dữ liệu demo; ba trường nhạy cảm được mã hóa trước lưu, giải mã khi đọc có quyền, dữ liệu hỏng trả 409 integrity_failure. Bản tích hợp đồng thời bật kiểm thử bảo mật bắt buộc sau khi API đã sẵn sàng.

## Phạm vi

- TV2: config, database/model, schemas, dependency H1, student service, routes, init_db, Docker/Compose, demo_client và test_api.
- Test hợp đồng lưu trữ kiểm POST/PUT lưu đúng đầu ra CryptoService; smoke PostgreSQL kiểm thêm tag và key_version.
- Dependencies và fixture lấy nguyên bản TV3 để giải quyết add/add. Bỏ WAIT_API sau tích hợp; test quyền và tamper nằm trong test_security, test API kiểm H2 bằng crypto giả ném IntegrityFailure. TV3 cần review phần tiếp nhận.
- Cập nhật api_db, Chương 3–4 (Markdown/Word), slide/PPTX, nội dung hợp đồng và bằng chứng.
- Đã ghép local bản sửa UTF-8 của TV1 từ PR #7; không đổi hợp đồng H1.

## Kiểm tra

Kết quả cũ ngày 15/11: 91 test Windows/Linux và benchmark gốc. Đợt tái kiểm ngày 16/11 trên bản ghép local mới:

- Windows Python 3.12.1: 102 passed, không xfail/skip. Chưa chạy lại pytest Linux trên commit mới; kết quả 91 test Linux thuộc lần 15/11.
- Docker build/up --wait: DB/API healthy. Demo SV9001/SV9002 tạo 201, đọc 200.
- verify_tv2: 19/19 đạt, exit 0 trên PostgreSQL 17.12.
- Attack lab mới: A1=401, A2=403 kèm DB/payload nguyên, A3=True cho ba field, A4/A5=409 đúng code, byte DB và payload được khôi phục.
- Benchmark ngày 15/11: đủ 100/1.000/10.000 bản ghi; bảng/biểu đồ trong Chương 5, CSV gốc không commit.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
docker compose up -d --build --wait
.\.venv\Scripts\python.exe -m scripts.demo_client
.\.venv\Scripts\python.exe -m scripts.verify_tv2
.\.venv\Scripts\python.exe -m scripts.attack_lab
```

Lần nghiệm thu dùng cấu hình/cổng/volume mới trong bản sao tạm; không chạm dữ liệu cũ. File docs/tv2_verification.json và docs/evidence lưu kết quả không có bí mật. Kết quả local không thay CI trên commit của PR này.

## Reviewer và điều kiện merge

Các mục code F1–F4 đã được sửa trên bản tích hợp local và có test chống pass giả; F8 đã xử lý bằng cách đưa số liệu/biểu đồ vào Chương 5, bỏ CSV trong Git. TV3 cần review phần file sở hữu; required pytest trên main và CI của đúng PR vẫn cần chủ repo xử lý trước merge. Bản draft này chưa phải xác nhận toàn bộ nhóm đã đạt DoD.

TV1 review mapping H1, auth và mô tả mật mã; TV3 review dependencies/fixture, test_security và H2/H3. Hoàn tất nội dung H2–H5 ở issue #3 theo docs/TV2_HOP_DONG_ISSUE_3.md.

Đề xuất review/merge PR #5 để đưa CI lên main, cập nhật/review/merge PR #7, rồi cập nhật nhánh integration/tv2-merge-prep theo main và mở PR này. Khi đó source TV1/TV3 đã nằm trong base, diff tập trung vào API/DB và sửa tích hợp. Giữ lịch sử commit, không force-push. Xem docs/TV2_MERGE_READINESS.md.

Replay cùng ô, lộ khóa/máy ứng dụng và metadata để rõ là giới hạn thiết kế. Chương 1–2/5–6 và biểu đồ đã có bản ghép local cần chủ phần việc xác nhận; nghiệm thu máy sạch, ảnh demo, tên/MSSV và tổng duyệt vẫn là việc bàn giao của nhóm.

---
Bản mô tả local; chưa tạo PR, gán reviewer hoặc đăng approval. Cập nhật kết quả CI và commit thực tế trước merge.
