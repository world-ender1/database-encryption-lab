# Ghi chú review tích hợp của TV2

Ngày 14/11/2026. Đây là nhận xét từ source local, **chưa phải review hoặc approve PR trên GitHub**.

## H1 của TV1

Đã thấy đúng tên/chữ ký decode_key, CryptoService(key, key_version), encrypt(value, student_id, field), decrypt(ev, student_id, field), EncryptedValue(ciphertext, nonce, key_version), IntegrityFailure, require_admin và require_reader. TV2 đã gọi các interface này thay vì sao chép crypto/auth vào route.

**Chưa đủ điều kiện nghiệm thu crypto:**

1. `crypto_service.py` ghi rõ bản tạm; encrypt trả UTF-8 plaintext nối tag SHA-256 giả. Hàm khởi tạo chỉ kiểm tra chiều dài key, không sử dụng key để bảo vệ nội dung. Kiểm tra PostgreSQL xác nhận plaintext còn nằm trong cột nhạy cảm.
2. Ba test `test_h1_known_vector_matches_aad_contract`, `test_c02_ciphertext_hides_plaintext`, `test_c03_wrong_key` còn xfail. Khi triển khai AES-GCM, TV1 phải gỡ marker phù hợp; strict=True khiến XPASS bị xem là lỗi nên không chỉ thay thân hàm rồi bỏ qua test.
3. Bản tạm có thể để `UnicodeDecodeError` thoát ra nếu có dữ liệu UTF-8 sai nhưng tag giả được tính lại đúng. Không coi đây là triển khai đủ hợp đồng “mọi lỗi giải mã thành IntegrityFailure”. TV1 cần chuẩn hóa lỗi dữ liệu/tag/nonce/version khi viết bản thật.
4. Chưa thấy test C07 replay trong file hiện tại. Cần bổ sung và giải thích rằng replay cùng hàng/field có thể vẫn xác thực được.

Khi review PR thật: kiểm tra nonce mới 12 byte, key 32 byte, tag 16 byte, AAD đúng tuyệt đối, không log key, sai key/AAD/nonce/CT/version đều từ chối, không lộ plaintext trong CT, không đổi chữ ký H1.

## H2/H3 cho TV3

- `get_db` phải được override từ `app.database`, cùng đối tượng dependency route đang dùng.
- Bảng `students`, cột `*_ct`, `*_nonce`, `key_version` giữ nguyên. Bảng benchmark phải tách riêng.
- Thiếu/sai token 401, viewer ghi 403, ID sai 422.
- Dữ liệu hỏng trả 409 `integrity_failure`; GET danh sách trả cả nhóm ID hỏng, không trả danh sách một phần.
- POST trùng trả 409 `duplicate_student`; không nhầm với lỗi mật mã.
- PUT không nhận student_id trong body, mã hóa lại cả 3 field. DELETE có thể dọn hồ sơ hỏng.
- Attack lab phải giữ dữ liệu gốc và restore trong finally; sau restore GET trả 200.

`tests/conftest.py` và `requirements.txt` được tạo hỗ trợ TV2 vì repo chưa có. TV3 cần tiếp nhận, thêm CI và dependencies của benchmark; không có thay đổi vào file TV3 đã tồn tại.
