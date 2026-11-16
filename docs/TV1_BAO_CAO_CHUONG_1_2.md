# Chương 1–2. Mở đầu và cơ sở lý thuyết — bản ghép để TV1 rà soát

Ngày cập nhật: 16/11/2026. Đề tài: mã hóa dữ liệu nhạy cảm tại tầng ứng dụng trước khi lưu PostgreSQL. Bản này dùng dữ liệu giả và mô tả đúng mã nguồn đã tích hợp; TV1 cần xác nhận nội dung học thuật khi nộp.

## Chương 1. Mở đầu

### 1.1. Bối cảnh và vấn đề

Ứng dụng thường lưu thông tin cá nhân trong cơ sở dữ liệu. Nếu người tấn công chỉ lấy được bản sao DB hoặc quyền đọc SQL, cột ở dạng rõ cho phép họ đọc dữ liệu ngay. Đề tài xây dựng một hệ thống hồ sơ sinh viên giả lập để kiểm tra cách mã hóa ba trường nhạy cảm (`national_id`, `phone`, `address`) **trước** khi ghi vào PostgreSQL. `student_id`, họ tên và ngành học được giữ rõ theo thiết kế, giúp quan sát ranh giới bảo vệ thay vì gọi toàn bộ DB là đã được mã hóa.

### 1.2. Mục tiêu và câu hỏi nghiên cứu

1. Triển khai API CRUD với hai vai trò admin/viewer, lưu ba trường nhạy cảm dưới dạng ciphertext và nonce; người có quyền đọc vẫn nhận được plaintext qua API.
2. Kiểm tra tính bí mật khi chỉ đọc DB mà không có khóa, phát hiện sửa/tráo dữ liệu qua AES-256-GCM và AAD, đồng thời ghi rõ các trường hợp hệ thống không bảo vệ được.
3. Tự động kiểm thử hợp đồng H1–H5, mô phỏng A1–A8, đo overhead ghi/đọc và kích thước payload trên PostgreSQL thật.

Câu hỏi thực nghiệm là: “Mã hóa ở tầng ứng dụng thay đổi điều gì đối với dữ liệu nhìn thấy trong DB, khả năng phát hiện sửa dữ liệu, và chi phí xử lý?” Kết quả được giới hạn ở dữ liệu giả và môi trường demo cục bộ.

### 1.3. Phạm vi và phương pháp

FastAPI kiểm tra token, validate JSON và gọi `CryptoService` trước khi ghi bằng SQLAlchemy. PostgreSQL 17 lưu ciphertext và nonce dưới kiểu `BYTEA`; khóa được nạp từ `.env` ngoài bảng. Bộ test dùng pytest/SQLite cô lập; smoke, attack lab và benchmark dùng PostgreSQL thật trong Docker. Nhóm áp dụng TDD cho phần mật mã, review chéo theo chủ file và CI trên PR.

Thử nghiệm không triển khai TLS công khai, KMS, xoay khóa, migration, tìm kiếm trên ciphertext hay chống replay cùng ô. Demo dùng token tĩnh và HTTP loopback; không dùng dữ liệu cá nhân thật. Chi tiết kiến trúc và API ở [Chương 3–4](TV2_BAO_CAO_CHUONG_3_4.md); phép đo và giới hạn ở [Chương 5](TV3_BAO_CAO_CHUONG_5.md).

### 1.4. Đóng góp và cấu trúc báo cáo

TV1 phụ trách key/crypto/auth và thiết kế mật mã; TV2 phụ trách API/DB/Docker; TV3 phụ trách CI, security tests, attack lab và benchmark. Chương 2 giải thích AES-GCM và threat model; Chương 3–4 trình bày thiết kế/triển khai; Chương 5 là thực nghiệm; Chương 6 tổng hợp kết quả và hướng phát triển. Các vai trò này là phân công của kế hoạch, không thay cho xác nhận review trên GitHub.

## Chương 2. Cơ sở lý thuyết và mô hình đe dọa

### 2.1. Mã hóa có xác thực AES-256-GCM

AES-GCM là chế độ mã hóa có xác thực (AEAD). Với khóa 32 byte `K`, nonce 12 byte `N`, plaintext UTF-8 `P` và associated data `A`, hàm mã hóa tạo ciphertext kèm tag xác thực 16 byte; có thể viết ngắn là `(C, T) = AES-GCM-Encrypt(K, N, P, A)`. `N` không cần bí mật nhưng không được tái sử dụng với cùng khóa. Giải mã chỉ trả plaintext khi tag hợp lệ; sửa ciphertext, nonce hoặc AAD sẽ gây lỗi xác thực. Trong code, lỗi sai tag và plaintext giải mã không phải UTF-8 đều được chuẩn hóa thành `IntegrityFailure`, để API trả 409 `integrity_failure` thay vì lộ chi tiết nội bộ.

Mỗi lần `encrypt` sinh nonce bằng `os.urandom(12)`. Đây là nonce ngẫu nhiên; dự án không có bộ đếm hoặc sổ đăng ký bảo đảm duy nhất tuyệt đối. `EncryptedValue` giữ `ciphertext`, `nonce`, `key_version`; `CryptoService` từ chối khóa không đúng 32 byte và giải mã với key version không khớp.

### 2.2. Associated data ràng buộc ngữ cảnh

AAD có định dạng chính xác `student:{student_id}|field:{field}|key:{key_version}`. Nó không được mã hóa nhưng được tag bảo vệ. Khi chép cặp ciphertext/nonce của `SV9002` sang `SV9001` hoặc từ `phone` sang `national_id`, AAD khi giải mã khác AAD lúc mã hóa, nên giải mã thất bại. Ngược lại, AAD không chứa bộ đếm thay đổi bản ghi: chép lại ciphertext **cũ của chính cùng hàng/cùng field** vẫn có thể giải mã (A7). Đây là giới hạn đã được test C07 xác nhận.

### 2.3. Khóa và quyền truy cập

`scripts/init_env.py` sinh khóa AES 32 byte rồi mã hóa Base64 trong `.env`, cùng token admin/viewer và mật khẩu DB. `decode_key` từ chối Base64 sai hoặc khóa không đủ 32 byte. `.env` bị Git bỏ qua và Dockerfile không chép khóa vào image; mất khóa sẽ làm dữ liệu cũ không giải mã được. Admin được CRUD, viewer chỉ đọc; không có hoặc sai Bearer token trả 401, viewer ghi/xóa trả 403. Hai token tĩnh chỉ phù hợp demo cục bộ.

### 2.4. Threat model và ranh giới bảo vệ

Kẻ tấn công được xét gồm: người gọi API chưa xác thực; viewer vượt quyền; người có dump DB nhưng không có khóa; người có quyền sửa byte DB; và người gửi ID dạng SQL injection. Kịch bản A1–A8 và expected/actual nằm ở [Chương 5](TV3_BAO_CAO_CHUONG_5.md) và [threat model](threat_model.md). Bản dump vẫn lộ `student_id`, họ tên, ngành, số hàng và độ dài ciphertext. Nếu khóa hoặc máy ứng dụng bị chiếm, bảo vệ ở lớp này không còn; AES-GCM phát hiện việc sửa dữ liệu nhưng không tự phục hồi byte bị phá hỏng.

### 2.5. Cách kiểm chứng phần mật mã

Bốn file test TV1 kiểm H1/C01–C07, khóa, auth và init_env. Lịch sử commit test trước code của PR AES-GCM và PR sửa UTF-8 thể hiện hai vòng TDD cụ thể. Lần tái kiểm ngày 16/11 cho **48 passed**, coverage 100% dòng/nhánh trên 93 câu lệnh và 18 nhánh; 18/19 mutant do script tái kiểm độc lập bị test bắt. M13 thay `compare_digest` bằng `==` sống sót qua functional tests, vì vậy cần đọc code/review cho tính chất so sánh token. [Lệnh và bằng chứng](evidence/tv1_coverage_2026-11-16.md) ghi rõ phạm vi của con số này; không suy ra mọi tính chất bảo mật đều đã được chứng minh.

### 2.6. Tài liệu tham khảo kỹ thuật

Thiết kế và nguồn kỹ thuật chi tiết được ghi tại [crypto_design.md](crypto_design.md); API/schema ở [api_db.md](api_db.md); phép thử và số liệu ở [Chương 5](TV3_BAO_CAO_CHUONG_5.md). Khi xuất báo cáo nộp, nhóm cần chuẩn hóa trích dẫn thư viện `cryptography`, tài liệu PostgreSQL và kế hoạch nội bộ theo mẫu môn học.
