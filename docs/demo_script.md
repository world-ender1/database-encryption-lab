# Kịch bản Demo & Thuyết trình (12 phút)

## 1. Chuẩn bị trước buổi demo
1. Đảm bảo Docker đang chạy và các container đều `healthy`:
   ```bash
   docker compose up -d --build
   docker compose ps
   ```
2. Nạp dữ liệu mẫu (`SV9001`, `SV9002`) trước:
   ```bash
   python -m scripts.demo_client --reset
   ```
3. Mở sẵn:
   - Tab trình duyệt tới `http://127.0.0.1:8000/docs` (Swagger UI).
   - Terminal 1 (chạy `pytest`, `attack_lab`, `benchmark`).
   - Terminal 2 (mở sẵn `psql` để chiếu ciphertext dạng HEX).
4. **An toàn trình chiếu**: phóng to chữ terminal, tắt thông báo máy tính, **tuyệt đối không mở file `.env`** hoặc chiếu `ADMIN_TOKEN`/`ENCRYPTION_KEY_B64` lên màn hình. Chuẩn bị ảnh chụp kết quả dự phòng nếu máy gặp sự cố.

---

## 2. Timeline chi tiết (12 phút)

### Phần 1 (0:00 – 2:00) | TV1: Kiến trúc & Cơ chế AES-256-GCM
- **Trình bày**: Slide kiến trúc 4 khối (`Client → FastAPI → AES-256-GCM → PostgreSQL`) và vị trí Key Store ngoài DB.
- **Điểm nhấn cần nói**:
  - Mã hóa tầng ứng dụng bảo vệ dữ liệu ngay trước khi rời app xuống DB, khác với TDE/FDE.
  - AES-256-GCM là AEAD: vừa bảo mật (confidentiality) vừa xác thực toàn vẹn (16-byte tag).
  - Nonce 12 byte sinh ngẫu nhiên mới mỗi lần ghi (`os.urandom(12)`), không tái sử dụng với cùng khóa.
  - AAD (`student:{id}|field:{field}|key:{key_version}`) gắn chặt ciphertext với đúng sinh viên và đúng trường.

### Phần 2 (2:00 – 5:00) | TV2: Demo CRUD qua Swagger & Kiểm tra PostgreSQL
- **Thao tác**:
  1. Trên Swagger (`http://127.0.0.1:8000/docs`), bấm **Authorize** và dán `ADMIN_TOKEN`.
  2. Gọi `GET /students/SV9001` → trả về HTTP `200` với đầy đủ thông tin rõ (app đã giải mã cho đúng quyền).
  3. Chuyển sang Terminal 2 chạy truy vấn DB thô:
     ```bash
     docker compose exec db psql -U demo -d encryption_demo -c "SELECT student_id, full_name, encode(national_id_ct, 'hex') AS nid_ct_hex, encode(national_id_nonce, 'hex') AS nonce_hex, key_version FROM students ORDER BY student_id;"
     ```
- **Điểm nhấn cần nói**:
  - Người dùng hợp lệ nhận plaintext qua API, nhưng trong DB các cột `national_id_ct`, `phone_ct`, `address_ct` chỉ là `BYTEA` không đọc được.
  - Các cột `full_name`, `major` giữ dạng rõ theo phạm vi thiết kế.

### Phần 3 (5:00 – 8:00) | TV3: Thực nghiệm tấn công có kiểm soát (`attack_lab`)
- **Thao tác** trên Terminal 1:
  ```bash
  python -m scripts.attack_lab
  ```
- **Kết quả kỳ vọng trên màn hình**:
  - `[A1] Missing bearer token -> 401`
  - `[A2] Viewer attempts DELETE -> 403 | row still there: True`
  - `[A3] DB contains ciphertext, not the plaintext: True`
  - `[A4] Tampered 1 ciphertext byte -> 409`
  - `[A5] Swapped fields between students -> 409`
  - `[Restore] legitimate read -> 200`
- **Điểm nhấn cần nói**:
  - A1/A2 chứng minh mã hóa đi kèm phân quyền API; mã hóa không thay thế access control.
  - A4/A5 chứng minh tag GCM + AAD chặn sửa byte ciphertext và chặn tráo ciphertext giữa `SV9002` sang `SV9001` (`409 integrity_failure`).
  - Script chỉ tác động DB demo cục bộ và tự khôi phục bản ghi về trạng thái ban đầu trong khối `finally`.

### Phần 4 (8:00 – 10:00) | TV3: Kết quả Benchmark (`benchmark_results.csv`)
- **Thao tác**:
  - Chiếu bảng số liệu thực tế từ `benchmark_results.csv` (100, 1.000, 10.000 bản ghi) và 2 biểu đồ INSERT / SELECT latency.
- **Điểm nhấn cần nói**:
  - Đo trực tiếp qua SQLAlchemy (1 lần warmup bỏ qua, lấy median 3 lần đo) để tách chi phí mã hóa + DB khỏi overhead HTTP.
  - Với mỗi trường nhạy cảm, dữ liệu tăng thêm 16 byte tag + 12 byte nonce (28 byte/trường).
  - Nếu ở mẫu nhỏ (n=100) xuất hiện nhiễu khiến chênh lệch dao động, giải thích trung thực do cache/CPU/IO chứ không kết luận mã hóa làm nhanh hơn.

### Phần 5 (10:00 – 12:00) | Cả nhóm: Giới hạn, Kết luận & Hỏi đáp
- **Các giới hạn bắt buộc nêu rõ**:
  1. **Replay cùng hàng/cùng cột (A7)**: GCM không ngăn kẻ có quyền ghi DB chép đè lại cặp `(ct, nonce)` cũ của chính `SV9001` (cùng AAD) — đã minh họa bằng test `C07`.
  2. **Lộ khóa / chiếm máy app**: Mất `ENCRYPTION_KEY_B64` là mất tính bí mật; mất khóa vĩnh viễn là mất khả năng giải mã.
  3. **Không `LIKE` / tìm kiếm trực tiếp** trên cột đã mã hóa ngẫu nhiên.
  4. **Demo cục bộ**: chưa tích hợp KMS/Vault, TLS và xoay khóa đa phiên bản (`key_version` mới ở mức metadata).
