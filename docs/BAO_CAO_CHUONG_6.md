# Chương 6. Đánh giá, hạn chế và hướng phát triển

Ngày cập nhật: 16/11/2026. Toàn bộ mã nguồn, bộ test và tài liệu đã tích hợp trên nhánh `main` (`3c7bd9a`) với GitHub Actions CI xanh và nghiệm thu clone sạch đạt yêu cầu.

## 6.1. Kết quả so với mục tiêu

Hệ thống FastAPI/PostgreSQL đã mã hóa `national_id`, `phone`, `address` bằng AES-256-GCM trước khi lưu. API chỉ trả plaintext sau khi kiểm tra quyền; truy vấn SQL thô thấy ciphertext/nonce cùng `key_version`. AAD gắn ID, field và phiên bản khóa. Kiểm thử trên `main` đạt **102 passed** (cả bản cài đặt chuẩn và bản clone sạch theo `README.md`); smoke PostgreSQL **19/19**; attack lab A1–A5 chạy trên DB demo thật và xác nhận dữ liệu được khôi phục. A6/A7/A8 được kiểm ở cấp module/API đúng phân công. Bản sửa lỗi UTF-8 của issue #6 đã được merge trên `main`, thêm test H1 và làm cho mọi lỗi giải mã theo hợp đồng trả `IntegrityFailure`.

Benchmark cho thấy overhead tăng theo số hàng, đặc biệt ở 10.000 hồ sơ (số đo ngày 15/11: INSERT từ 0,256266 s lên 1,085616 s; SELECT từ 0,017435 s lên 0,314231 s). Payload ba trường mẫu tăng 84 byte/hồ sơ do ba tag và ba nonce. Kết quả `n=100` có nhiễu đo nên không dùng để khẳng định mã hóa làm thao tác đọc nhanh hơn. Bảng, hai biểu đồ và bộ 6 ảnh chụp minh chứng nằm trong [Chương 5](TV3_BAO_CAO_CHUONG_5.md).

## 6.2. Giới hạn của kết luận

- Khi chỉ lộ DB mà không có khóa, ba trường nhạy cảm không xuất hiện dưới dạng rõ trong cột lưu trữ đã thử. Kết quả này không có nghĩa toàn bộ DB được che giấu: tên, ngành, ID, số hàng và độ dài ciphertext vẫn lộ.
- A4/A5 chứng minh ứng dụng phát hiện sửa/tráo trong các ca đã thử. Dữ liệu bị phá hỏng vẫn cần backup để khôi phục; AES-GCM không sửa lại byte bị ghi đè.
- A7 chứng minh replay cùng hàng/cùng field vẫn được chấp nhận. Không được trình bày AAD như cơ chế chống replay tổng quát.
- Khóa hoặc tiến trình API bị lộ thì dữ liệu có thể bị giải mã. Demo chưa có KMS, key rotation, phân quyền DB chi tiết, TLS công khai, audit log hoặc quản lý người dùng production.
- Benchmark đo thời gian trên một máy có tải nền và `payload_bytes` của ba field, không đo dung lượng bảng/index/WAL hoặc hiệu năng nhiều người dùng. Không suy ra SLA production từ ba lần chạy mỗi mức.

## 6.3. Trạng thái hoàn tất và bước chốt nộp cuối

1. PR #5, PR #7 và PR #8 đã được review/merge vào `main`; CI `pytest` đã bật bắt buộc trên `main` và chạy xanh.
2. Đã chạy nghiệm thu bản clone sạch từ `main` theo `README.md` (`102 passed`, `demo_client`, `attack_lab`, `benchmark`) và chụp đủ 6 ảnh minh chứng (Swagger, `psql`, `attack_lab`, `pytest`, GitHub Actions).
3. Bước cuối của nhóm trước khi nộp: xác nhận và đóng [issue #3](https://github.com/world-ender1/database-encryption-lab/issues/3), điền họ tên/MSSV 3 thành viên vào báo cáo/slide, tổng duyệt demo 12 phút và gắn tag `v1.0.0`.

Lịch sử Sprint 0 ban đầu có sai lệch trình tự nhưng toàn bộ sản phẩm tích hợp đã được kiểm chứng đầy đủ trên `main` mà không cần viết lại lịch sử commit.

## 6.4. Hướng phát triển

Một bản triển khai thực tế cần quản lý khóa bằng KMS hoặc vault và quy trình rotation có migration dữ liệu, dùng TLS và xác thực người dùng thay token tĩnh, kiểm soát quyền truy cập DB, backup/restore, giám sát và audit log. Nếu cần chống replay, hệ thống phải có phiên bản bản ghi hoặc bộ đếm đơn điệu được bảo vệ ở nơi không thể bị rollback cùng ciphertext. Tìm kiếm trên trường đã mã hóa cần thiết kế riêng, cân bằng giữa truy vấn và rò rỉ thông tin. Hiệu năng cần đo thêm trên nhiều máy, tải đồng thời, kích thước dữ liệu đa dạng và dung lượng lưu trữ thực tế.
