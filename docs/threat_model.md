# Threat Model – Mã hóa dữ liệu nhạy cảm ở tầng ứng dụng

## 1. Tài sản cần bảo vệ
- **Dữ liệu nhạy cảm trong hồ sơ sinh viên** (dữ liệu giả lập cho demo): `national_id` (CCCD giả), `phone`, `address` lưu trong bảng `students` của PostgreSQL.
- **Khóa mật mã**: `ENCRYPTION_KEY_B64` (AES-256, 32 byte) nạp từ `.env` ngoài database.
- **Thông tin xác thực API**: `ADMIN_TOKEN` (toàn quyền CRUD) và `VIEWER_TOKEN` (chỉ đọc).

Dữ liệu không mã hóa theo thiết kế: `student_id` (khóa chính, định dạng `^[A-Za-z0-9]{1,16}$`), `full_name`, `major`, và metadata `key_version`.

## 2. Giả định về kẻ tấn công (Threat Actors)
1. **Kẻ tấn công bên ngoài / chưa xác thực**: gọi HTTP API không có token hoặc dùng token giả.
2. **Người dùng bị giới hạn quyền (`viewer`)**: có `VIEWER_TOKEN` hợp lệ nhưng tìm cách tạo, sửa hoặc xóa hồ sơ.
3. **Kẻ tấn công có bản dump database hoặc quyền truy cập SQL thô**: đọc được bảng `students` nhưng không có khóa `ENCRYPTION_KEY_B64` trên máy ứng dụng.
4. **Kẻ tấn công có quyền sửa dữ liệu trong database**: thay đổi byte của ciphertext/tag/nonce hoặc tráo cột mã hóa giữa các bản ghi/cột.
5. **Kẻ tấn công gửi input dạng SQL injection** qua API (`student_id`).

## 3. Ma trận kịch bản kiểm thử (A1–A8)

| Mã | Kịch bản tấn công | Mục tiêu bảo vệ | Cách kiểm chứng | Kết quả kỳ vọng | Nơi kiểm chứng |
|---|---|---|---|---|---|
| **A1** | Gọi API đọc/ghi không có hoặc sai Bearer token | Không rò rỉ dữ liệu qua API chưa xác thực | `GET /students`, `GET /students/SV9001` không token / token sai | HTTP `401` + `WWW-Authenticate: Bearer` | `tests/test_security.py`, `scripts/attack_lab.py` |
| **A2** | Dùng `VIEWER_TOKEN` thực hiện thao tác ghi/xóa | Phân quyền RBAC tách đọc và ghi | Viewer gọi `POST`, `PUT`, `DELETE /students/SV9001` | HTTP `403`, dữ liệu DB giữ nguyên | `tests/test_security.py`, `scripts/attack_lab.py` |
| **A3** | Lộ bản dump DB / truy vấn SQL thô | Bí mật (confidentiality) cho 3 trường nhạy cảm | Kiểm tra `*_ct` và `*_nonce` trong `students` | Không chứa plaintext; có tag 16 byte + nonce 12 byte | `tests/test_security.py`, `scripts/attack_lab.py` |
| **A4** | Sửa 1 byte ciphertext, tag hoặc nonce trong DB | Phát hiện giả mạo (integrity/authenticity) | Flip 1 bit trong `national_id_ct` hoặc `phone_nonce` rồi `GET` | HTTP `409` (`code="integrity_failure"`), không trả plaintext hỏng | `tests/test_security.py`, `scripts/attack_lab.py` |
| **A5** | Tráo ciphertext + nonce giữa 2 sinh viên hoặc 2 cột | Gắn chặt ciphertext với ngữ cảnh bản ghi/trường qua AAD | Copy `national_id_ct/nonce` từ `SV9002` sang `SV9001` rồi `GET` | HTTP `409` (`code="integrity_failure"`) do sai AAD | `tests/test_security.py`, `scripts/attack_lab.py` |
| **A6** | Giải mã bằng khóa AES khác | Cô lập khóa giữa các môi trường | Giải mã `EncryptedValue` với `OTHER_KEY` | Ném `IntegrityFailure` | `tests/test_crypto.py` (TV1) |
| **A7** | Ghi đè lại cặp `ciphertext + nonce` cũ của **cùng** bản ghi và **cùng** cột | Minh họa giới hạn chống rollback/replay | Ghi lại ciphertext cũ của `SV9001`/`address` rồi giải mã | **Vẫn giải mã được** (giới hạn thiết kế, không phải lỗi) | `tests/test_crypto.py` (C07), `docs/crypto_design.md` |
| **A8** | Gửi chuỗi dạng SQL injection vào `student_id` | Ngăn input bất hợp lệ trước khi chạm DB | `GET /students/SV9001' OR '1'='1` và `POST` tương ứng | HTTP `422` (Pydantic/FastAPI validation), số bản ghi không đổi | `tests/test_security.py` |

## 4. Ranh giới bảo vệ và những gì giải pháp KHÔNG chống được
- **Rò rỉ metadata**: `student_id`, `full_name`, `major`, số lượng bản ghi và độ dài ciphertext vẫn quan sát được từ bản dump DB (`len(ciphertext) = len(utf8(plaintext)) + 16`).
- **Máy ứng dụng hoặc khóa bị chiếm**: Nếu kẻ tấn công lấy được `ENCRYPTION_KEY_B64` (hoặc chiếm quyền tiến trình FastAPI), mọi dữ liệu được mã hóa bởi khóa đó đều có thể bị giải mã.
- **Tấn công phá hoại (availability)**: AES-GCM **phát hiện** việc sửa ciphertext (`409`), không tự phục hồi dữ liệu bị ghi đè nếu không có backup.
- **Replay cùng hàng/cùng cột (A7)**: AAD có dạng `student:{student_id}|field:{field}|key:{key_version}` nên ngăn tráo chéo hàng/cột (A5), nhưng không chứa monotonic counter hay version của bản ghi để chống ghi lại dữ liệu cũ của chính hàng đó.
- **Tìm kiếm trên trường mã hóa**: Vì mỗi lần mã hóa sinh nonce ngẫu nhiên mới, không thể truy vấn `WHERE national_id_ct = ...` hoặc `LIKE` trực tiếp bằng SQL chuẩn.
- **Phạm vi triển khai**: Token tĩnh trong `.env`, HTTP loopback và `create_all()` chỉ phục vụ demo cục bộ; môi trường production cần TLS, KMS/Vault, xoay khóa (key rotation) và kiểm toán truy cập.
