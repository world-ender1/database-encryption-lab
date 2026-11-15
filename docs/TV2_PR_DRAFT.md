# feat(api): complete encrypted student CRUD and integrated verification

Main đã có AES-GCM của TV1 nhưng chưa có API/DB. Thay đổi bổ sung FastAPI CRUD, PostgreSQL schema, Docker và dữ liệu demo; ba trường nhạy cảm được mã hóa trước lưu, giải mã khi đọc có quyền, dữ liệu hỏng trả 409 integrity_failure. Bản tích hợp đồng thời bật kiểm thử bảo mật bắt buộc sau khi API đã sẵn sàng.

## Phạm vi

- TV2: config, database/model, schemas, dependency H1, student service, routes, init_db, Docker/Compose, demo_client và test_api.
- Test hợp đồng lưu trữ kiểm POST/PUT lưu đúng đầu ra CryptoService; smoke PostgreSQL kiểm thêm tag và key_version.
- Dependencies và fixture lấy nguyên bản TV3 để giải quyết add/add. Bỏ WAIT_API sau tích hợp; chuyển test quyền từng route sang test_security, bỏ test nonce trùng. Phần này cần TV3 review.
- Cập nhật api_db, Chương 3–4 (Markdown/Word), slide/PPTX, nội dung hợp đồng và bằng chứng.
- Module crypto/auth của TV1 giữ nguyên theo main đã merge.

## Kiểm tra

Ngày 15/11/2026 trên bản ghép local:

- Windows Python 3.12.1: 91 passed, không xfail/skip.
- Linux image Python 3.12.16 cài dependencies mới: 91 passed; pip check đạt. Có một DeprecationWarning Starlette/AnyIO ở mỗi môi trường.
- Docker build/up --wait: DB/API healthy. Demo SV9001/SV9002 tạo 201, đọc 200.
- verify_tv2: 19/19 đạt, exit 0 trên PostgreSQL 17.12.
- Attack lab: A1=401, A2=403, A3=True, A4=409, A5=409, Restore=200.
- Benchmark: đủ 100/1.000/10.000 bản ghi; CSV/log trong docs/evidence.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
docker compose up -d --build --wait
.\.venv\Scripts\python.exe -m scripts.demo_client
.\.venv\Scripts\python.exe -m scripts.verify_tv2
.\.venv\Scripts\python.exe -m scripts.attack_lab
```

Lần nghiệm thu dùng cấu hình/cổng/volume mới trong bản sao tạm; không chạm dữ liệu cũ. File docs/tv2_verification.json và docs/evidence lưu kết quả không có bí mật. Kết quả local không thay CI trên commit của PR này.

## Reviewer và điều kiện merge

Audit kế hoạch bổ sung phát hiện tiêu chí tự kết luận của attack_lab còn thiếu (A2 giữ dữ liệu, A4/A5 kiểm code, restore kiểm nội dung). Cần TV3 sửa/review theo docs/DOI_CHIEU_KE_HOACH_CA_NHOM.md; bàn giao test tamper còn trong test_api, chốt lưu CSV và required pytest trước nghiệm thu cuối. Bản draft này chưa phải xác nhận toàn bộ nhóm đã đạt DoD.

TV1 review mapping H1, auth và mô tả mật mã; TV3 review dependencies/fixture, test_security và H2/H3. Hoàn tất nội dung H2–H5 ở issue #3 theo docs/TV2_HOP_DONG_ISSUE_3.md.

Đề xuất merge PR #5 đã review trước, cập nhật nhánh integration/tv2-merge-prep theo main rồi dùng PR này. Khi đó source TV3 đã nằm trong base và diff tập trung vào API/DB cùng thay đổi test tích hợp. Giữ lịch sử commit, không force-push. Xem docs/TV2_MERGE_READINESS.md.

Replay cùng ô, lộ khóa/máy ứng dụng và metadata để rõ là giới hạn thiết kế. Chương 5/biểu đồ benchmark, nghiệm thu máy sạch, tên/MSSV, ghép báo cáo và tổng duyệt vẫn là việc bàn giao của nhóm.

---
Bản mô tả local; chưa tạo PR, gán reviewer hoặc đăng approval. Cập nhật kết quả CI và commit thực tế trước merge.
