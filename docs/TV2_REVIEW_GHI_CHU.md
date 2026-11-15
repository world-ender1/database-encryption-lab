# Ghi chú review TV1/TV3 từ TV2

Ngày 15/11/2026. Kết quả đọc source và chạy test local; chưa đăng review/approve lên GitHub.

## TV1 — PR #2/#4 đã merge

- CryptoService, EncryptedValue, decode_key và auth giữ H1; TV2 truyền đúng ID, field và key_version.
- AES-GCM dùng khóa 32 byte, nonce 12 byte, AAD đã chốt. Có known vector, wrong key, nonce/tag/ciphertext/AAD và replay cùng ô.
- Replay là giới hạn đã biết. Tài liệu TV2 đã đối chiếu docs/crypto_design.md.
- Không sửa thân module TV1. 47 test TV1 nằm trong bộ tích hợp.

## TV3 — PR #5

Nguồn: [PR #5](https://github.com/world-ender1/database-encryption-lab/pull/5), commit `3edd89bcbaba3b6adf93374b77cd30a0c0854030`.

- Tên bảng/cột, route/mã lỗi phù hợp H2/H3. Fixture import app khi chạy và override get_db bằng SQLite riêng.
- attack_lab dùng try/finally để khôi phục dữ liệu. Benchmark có warmup và ba lần đo lấy trung vị; payload_bytes là dữ liệu ba field, không phải dung lượng bảng trên đĩa.
- CI của TV3 là success nhưng 14 test gắn WAIT_API/xfail không strict. Trước tích hợp lỗi thiếu API bị xfail; sau tích hợp XPASS vẫn xanh. Bản chuẩn bị đã bỏ marker và chạy pytest bình thường: 91 passed.
- Hai xung đột add/add là requirements.txt và tests/conftest.py; đã chọn nguyên bản TV3, có python-dotenv trực tiếp.
- Chuyển sáu ca kiểm quyền từng route từ test_api sang test_security. Bỏ một test nonce trùng TV3; thêm một test mapping H1/H3 TV2 cho POST/PUT. Tổng số test vẫn là 91.
- Test danh sách nhiều hồ sơ hỏng và DELETE hồ sơ hỏng giữ ở TV2 để kiểm H2; TV3 kiểm các cơ chế tamper/swap/AAD.
- PostgreSQL smoke: 19/19. Attack lab: A1=401, A2=403, A3=True, A4=409, A5=409, Restore=200.

## Điều kiện trước duyệt merge

1. TV3 review phần bỏ WAIT_API và test quyền chuyển sang; TV1 review mapping H1/mô tả mật mã.
2. Hoàn tất H2–H5 tại issue #3; có bản nháp TV2_HOP_DONG_ISSUE_3.md.
3. CI chạy lại trên commit sẽ merge. PR #5 có mergeable=true, mergeable_state=blocked và chưa có review. Endpoint branch protection trả 404 nên chưa xác nhận được quy tắc bảo vệ; xem yêu cầu trên giao diện GitHub.
4. Chưa thấy Chương 5, biểu đồ benchmark hoặc bằng chứng nghiệm thu máy sạch trong tree TV3. Đây là việc hoàn thiện đồ án, không phải lỗi CRUD.

Chi tiết bằng chứng và giới hạn kiểm tra: TV2_MERGE_READINESS.md, docs/evidence.