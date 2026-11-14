# feat(api): persist student fields through CryptoService and expose protected CRUD

> Bản dự thảo cho **bước 18**, chưa dùng làm PR Sprint 0. Kiểm tra lại phần 3 cho thấy main chưa có đủ khung TV2/TV3; phải hoàn tất bước 1–9 trước. Xem [audit Sprint](TV2_KIEM_TRA_TRINH_TU_SPRINT.md). Các file hỗ trợ TV3 và test quyền/tamper cần tách bàn giao trước khi chốt phạm vi PR này.

Repo đã có H1/auth của TV1 nhưng chưa có phần API và DB. Thay đổi bổ sung cấu hình H4, schema students H3, mapping thông qua CryptoService, các route H2, khởi tạo DB và Docker Compose. POST/GET/PUT/DELETE hoạt động với lỗi 404/409/422 ổn định; mọi route sinh viên gắn dependency quyền tương ứng.

## Phạm vi

- Các file sở hữu TV2 trong app, Dockerfile, compose.yaml, demo_client, test_api và api_db.md.
- `.dockerignore`, script smoke check PostgreSQL, tài liệu báo cáo/slide và bàn giao TV2.
- Phần hỗ trợ cần TV3 review/nhận quản lý: requirements.txt và tests/conftest.py do repo chưa có. Công cụ xuất Word/PPTX có dependencies riêng trong docs/requirements-export.txt.
- Không thay module crypto, key_manager, auth, init_env và các test sẵn có của TV1.

## Kiểm tra

```powershell
.\.venv\Scripts\python.exe -m pytest -q
docker compose up -d --build --wait
.\.venv\Scripts\python.exe -m scripts.demo_client
.\.venv\Scripts\python.exe -m scripts.verify_tv2
```

Kết quả ngày 14/11/2026: 73 passed, 3 xfailed (crypto tạm của TV1); Docker api/db healthy; demo_client tạo và đọc hai hồ sơ. Smoke PostgreSQL: 16 điều kiện đạt, điều kiện không chứa plaintext **không đạt**, report `blocked_by_plaintext`, exit 2. Xem docs/tv2_verification.json.

## Giới hạn cần reviewer biết

CryptoService hiện vẫn là bản tạm Sprint 0. PR này hoàn thiện tích hợp TV2, **chưa phải bản phát hành có bảo mật AES-GCM**. Sau khi TV1 thay bản thật, cần reset dữ liệu demo từ bản tạm, chạy lại crypto suite và smoke check. Chưa có attack_lab/CI của TV3 để xác nhận nghiệm thu toàn nhóm.

`.env` đã được kiểm tra Git bỏ qua; tài liệu và minh chứng không chứa key/token. Cổng chỉ bind loopback, build context loại `.env`.

## Người review dự kiến

TV1: H1/auth và mapping mã hóa. TV3: H2/H3/H4, fixtures/dependencies và tích hợp kiểm thử. Chưa gán reviewer hoặc gửi PR thực tế.
