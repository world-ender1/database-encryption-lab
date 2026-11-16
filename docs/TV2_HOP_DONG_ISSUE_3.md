# Nội dung TV2 chuẩn bị cho issue #3

Ngày 15/11/2026. Đây là bản nháp để đưa vào [issue H1–H5](https://github.com/world-ender1/database-encryption-lab/issues/3), chưa đăng lên GitHub. TV2 đã được ghi nhận đồng ý H1 trong issue; phần dưới ghi rõ H2–H5 theo code hiện có, không thay sự xác nhận của TV1/TV3.

## H2 — API

| Method | Endpoint | Dependency | Thành công |
|---|---|---|---|
| GET | `/health` | Công khai | 200 `{"status":"ok"}` |
| POST | `/students` | `require_admin` | 201 `StudentOut` |
| GET | `/students` | `require_reader` | 200 danh sách `StudentOut`, sắp theo ID |
| GET | `/students/{student_id}` | `require_reader` | 200 `StudentOut` |
| PUT | `/students/{student_id}` | `require_admin` | 200 `StudentOut` |
| DELETE | `/students/{student_id}` | `require_admin` | 204, body rỗng |

POST nhận `student_id`, `full_name`, `major`, `national_id`, `phone`, `address`. PUT nhận đủ năm trường còn lại, cấm `student_id` và trường thừa. `student_id` theo `^[A-Za-z0-9]{1,16}$`; năm trường lần lượt có giới hạn độ dài 1–150, 1–100, 1–32, 1–32, 1–255.

Thiếu/sai token hoặc sai scheme: 401 kèm `WWW-Authenticate: Bearer`. Viewer ghi: 403. Sai body hoặc ID: 422. Không có hồ sơ: 404 `not_found`. Trùng ID: 409 `duplicate_student`. Không xác thực được dữ liệu mã hóa: 409 `integrity_failure`. Các lỗi nghiệp vụ có `detail` và `code`; lỗi integrity có thêm `student_ids`. GET danh sách có bất kỳ hồ sơ hỏng sẽ trả 409 cho cả danh sách, không trả dữ liệu của hồ sơ hợp lệ. DELETE không giải mã để vẫn xóa được hồ sơ hỏng.

## H3 — PostgreSQL

| Cột | Kiểu | Ràng buộc |
|---|---|---|
| `student_id` | VARCHAR(16) | PRIMARY KEY, NOT NULL |
| `full_name` | VARCHAR(150) | NOT NULL |
| `major` | VARCHAR(100) | NOT NULL |
| `national_id_ct`, `national_id_nonce` | BYTEA | NOT NULL |
| `phone_ct`, `phone_nonce` | BYTEA | NOT NULL |
| `address_ct`, `address_nonce` | BYTEA | NOT NULL |
| `key_version` | VARCHAR(20) | NOT NULL |

Bảng `students`. Tên công khai giữ nguyên: `app.database.Base`, `app.database.get_db`, `app.models.Student`, `app.main.app`. TV2 lưu đúng ciphertext/nonce do H1 trả về; không tự sinh nonce hay tag. Ciphertext kèm tag 16 byte; nonce 12 byte; khóa nằm ngoài DB. PUT mã hóa lại cả ba trường.

## H4 — Cấu hình

Giữ đúng tám biến TV1 liệt kê trong issue:

| Biến | Nơi dùng |
|---|---|
| `DATABASE_URL` | SQLAlchemy trên host; Compose ghi đè cho API thành `postgresql+psycopg://demo:<POSTGRES_PASSWORD>@db:5432/encryption_demo` |
| `ENCRYPTION_KEY_B64` | `decode_key` → `get_crypto`, khóa 32 byte |
| `KEY_VERSION` | Crypto và metadata; mặc định `v1` |
| `ADMIN_TOKEN`, `VIEWER_TOKEN` | Auth của TV1 |
| `POSTGRES_PASSWORD` | PostgreSQL và URL nội bộ API |
| `API_PORT` | Cổng host/API scripts, mặc định 8000 |
| `DB_PORT` | Cổng host PostgreSQL, mặc định 55432; phải khớp URL host |

Năm field `Settings`: `database_url`, `encryption_key_b64`, `key_version`, `admin_token`, `viewer_token`. Biến môi trường ưu tiên hơn `.env`; hai hàm `get_settings`/`get_crypto` có cache. Đổi cấu hình cần khởi động lại API. Compose chỉ bind cổng vào 127.0.0.1. Không đổi khóa của DB đang cần giữ dữ liệu.

## H5 — Dữ liệu demo và fixture tích hợp

`python -m scripts.demo_client` tạo SV9001/SV9002, bỏ qua trùng ID và kiểm tra GET. `--reset` chỉ xóa hai ID đó rồi tạo lại, dùng khi chúng là dữ liệu giả được phép thay.

| ID | Họ tên | Ngành | national_id | phone | address |
|---|---|---|---|---|---|
| SV9001 | Nguyen Van A | Computer Science | 012345678901 | 0901234567 | Ha Noi (fictional) |
| SV9002 | Tran Thi B | Information Security | 098765432109 | 0912345678 | Da Nang (fictional) |

Đã tích hợp nguyên bản fixture của TV3: `client`, `admin_headers`, `viewer_headers`, `sample_student`, thêm `db_session` để kiểm H3. Fixture ép SQLite trong bộ nhớ và cấu hình test trước import app; app được import trong fixture, không kết nối PostgreSQL thật. TV3 xác nhận phần sở hữu fixture.

Hai xung đột dependencies/fixture đã xử lý bằng bản TV3: có `python-dotenv==1.1.0`, giữ `psycopg[binary]==3.2.6` đã được TV1 kiểm trên máy họ. Đề nghị TV1/TV3 xác nhận H2–H5 ở issue trước khi đóng hợp đồng. Replay cùng hàng vẫn là giới hạn; không đổi H1 để bổ sung chống replay trong lần tích hợp này.
