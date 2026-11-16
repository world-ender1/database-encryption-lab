# Tái kiểm TV1: coverage và mutation (16/11/2026)

Thực hiện trên `integration/tv2-merge-prep` sau khi ghép nhánh sửa issue #6. Python 3.12.1 trên Windows, `pytest-cov` cài trong venv phục vụ đo, không thêm vào dependencies chạy ứng dụng.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_key_manager.py tests/test_crypto.py tests/test_auth.py tests/test_init_env.py -q --cov=app.key_manager --cov=app.crypto_service --cov=app.auth --cov=scripts.init_env --cov-branch --cov-report=term-missing
```

| Module | Câu lệnh | Chưa chạy | Nhánh | Nhánh thiếu | Coverage |
|---|---:|---:|---:|---:|---:|
| `app/auth.py` | 28 | 0 | 8 | 0 | 100% |
| `app/crypto_service.py` | 38 | 0 | 6 | 0 | 100% |
| `app/key_manager.py` | 11 | 0 | 2 | 0 | 100% |
| `scripts/init_env.py` | 16 | 0 | 2 | 0 | 100% |
| **Tổng** | **93** | **0** | **18** | **0** | **100%** |

Kết quả: **48 passed**, một DeprecationWarning từ Starlette/AnyIO, không có test fail.

Để tái lập kiểm tra đột biến, chạy:

```powershell
.\.venv\Scripts\python.exe -m scripts.recheck_tv1_mutations
```

Script dùng bản sao tạm của `app/`, `scripts/`, `tests/` và `.env.example`; không sửa source đang làm. Mỗi mutant chạy cả 48 test riêng. [Kết quả JSON](tv1_mutation_recheck.json): **18/19 mutant bị test bắt**, M13 (`compare_digest` → `==`) sống sót như đã nêu trong thiết kế TV1. M13 cần kiểm bằng đọc code và review vì timing side channel không được chứng minh bằng functional test. Đây là lần tái kiểm độc lập từ mã hiện tại, không nhận là log gốc TDD của TV1.
