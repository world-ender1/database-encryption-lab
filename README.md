# database-encryption-lab

Đồ án môn **Mật mã & An toàn thông tin**: minh họa mã hóa dữ liệu nhạy cảm ở tầng ứng dụng trước khi lưu vào PostgreSQL. Hệ thống FastAPI quản lý hồ sơ sinh viên giả lập, mã hóa 3 trường (`national_id`, `phone`, `address`) bằng **AES-256-GCM** kèm AAD gắn `student_id`, `field` và `key_version`, đồng thời kiểm chứng bằng bộ test bảo mật, mô phỏng tấn công và benchmark hiệu năng.

> **Cảnh báo an toàn**: Dự án chỉ sử dụng dữ liệu giả lập trong môi trường Docker cục bộ. **Không** commit `.env`, khóa AES, token hoặc DB dump lên GitHub. **Không** chạy lại `scripts/init_env.py` để ghi đè khóa nếu database cũ còn dữ liệu (dữ liệu cũ sẽ không giải mã được và trả `409`).

## 1. Yêu cầu môi trường
- Python 3.12+
- Docker & Docker Compose v2

## 2. Cài đặt

### Linux / macOS
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Khởi tạo cấu hình & chạy dịch vụ
1. Sinh file `.env` cục bộ (gồm `ENCRYPTION_KEY_B64`, `ADMIN_TOKEN`, `VIEWER_TOKEN`, `POSTGRES_PASSWORD`, `DATABASE_URL`):
   ```bash
   python scripts/init_env.py
   ```
2. Khởi chạy PostgreSQL 17 và FastAPI qua Docker Compose:
   ```bash
   docker compose up -d --build
   docker compose ps
   ```
3. Mở Swagger UI tại `http://127.0.0.1:8000/docs` (hoặc kiểm tra `http://127.0.0.1:8000/health`).
4. Nạp dữ liệu demo giả lập (`SV9001`, `SV9002`):
   ```bash
   python -m scripts.demo_client
   ```

## 4. Kiểm thử, mô phỏng tấn công & benchmark
- Chạy bộ unit / API / security tests (sử dụng SQLite trong bộ nhớ):
  ```bash
  python -m pytest -q
  ```
- Chạy kịch bản mô phỏng tấn công A1–A5 trên PostgreSQL demo (tự khôi phục dữ liệu sau khi thử):
  ```bash
  python -m scripts.attack_lab
  ```
- Chạy benchmark so sánh plaintext vs AES-256-GCM (tạo `benchmark_results.csv`, đã nằm trong `.gitignore`):
  ```bash
  python -m scripts.benchmark
  ```

## 5. Quan sát ciphertext trực tiếp trong PostgreSQL
```bash
docker compose exec db psql -U demo -d encryption_demo -c "SELECT student_id, full_name, encode(national_id_ct, 'hex') AS ciphertext_hex, encode(national_id_nonce, 'hex') AS nonce_hex, key_version FROM students ORDER BY student_id;"
```

Dừng container (giữ dữ liệu volume):
```bash
docker compose down
```

## 6. Tài liệu chi tiết
- Thiết kế mật mã & AAD: [docs/crypto_design.md](docs/crypto_design.md)
- Thiết kế API & PostgreSQL: [docs/api_db.md](docs/api_db.md)
- Threat Model (A1–A8 & giới hạn): [docs/threat_model.md](docs/threat_model.md)
- Kịch bản Demo 12 phút: [docs/demo_script.md](docs/demo_script.md)
