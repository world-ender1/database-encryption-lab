# Chương 6. Đánh giá, hạn chế và hướng phát triển — bản ghép nhóm

Ngày cập nhật: 16/11/2026. Các con số dưới đây là kết quả local trên commit tích hợp; cần chạy CI và nghiệm thu lại trên `main` sau khi các PR được review/merge.

## 6.1. Kết quả so với mục tiêu

Hệ thống FastAPI/PostgreSQL đã mã hóa `national_id`, `phone`, `address` bằng AES-256-GCM trước khi lưu. API chỉ trả plaintext sau khi kiểm tra quyền; truy vấn SQL thô thấy ciphertext/nonce cùng `key_version`. AAD gắn ID, field và phiên bản khóa. Bản tích hợp ngày 16/11 có **102 test đạt**; smoke PostgreSQL **19/19**; attack lab A1–A5 chạy trên DB demo thật và xác nhận dữ liệu được khôi phục. A6/A7/A8 được kiểm ở cấp module/API đúng phân công. Bản sửa lỗi UTF-8 của issue #6 đã được ghép local, thêm test H1 và làm cho mọi lỗi giải mã theo hợp đồng trả `IntegrityFailure`.

Benchmark ngày 15/11 cho thấy overhead tăng theo số hàng, đặc biệt ở 10.000 hồ sơ: INSERT từ 0,256266 s lên 1,085616 s; SELECT từ 0,017435 s lên 0,314231 s. Payload ba trường mẫu tăng 84 byte/hồ sơ do ba tag và ba nonce. Kết quả `n=100` có nhiễu đo nên không dùng để khẳng định mã hóa làm thao tác đọc nhanh hơn. Bảng và hai biểu đồ nằm trong [Chương 5](TV3_BAO_CAO_CHUONG_5.md).

## 6.2. Giới hạn của kết luận

- Khi chỉ lộ DB mà không có khóa, ba trường nhạy cảm không xuất hiện dưới dạng rõ trong cột lưu trữ đã thử. Kết quả này không có nghĩa toàn bộ DB được che giấu: tên, ngành, ID, số hàng và độ dài ciphertext vẫn lộ.
- A4/A5 chứng minh ứng dụng phát hiện sửa/tráo trong các ca đã thử. Dữ liệu bị phá hỏng vẫn cần backup để khôi phục; AES-GCM không sửa lại byte bị ghi đè.
- A7 chứng minh replay cùng hàng/cùng field vẫn được chấp nhận. Không được trình bày AAD như cơ chế chống replay tổng quát.
- Khóa hoặc tiến trình API bị lộ thì dữ liệu có thể bị giải mã. Demo chưa có KMS, key rotation, phân quyền DB chi tiết, TLS công khai, audit log hoặc quản lý người dùng production.
- Benchmark đo thời gian trên một máy có tải nền và `payload_bytes` của ba field, không đo dung lượng bảng/index/WAL hoặc hiệu năng nhiều người dùng. Không suy ra SLA production từ ba lần chạy mỗi mức.
- Test local và môi trường Docker cô lập chưa thay cho CI/review trên commit PR cuối hoặc nghiệm thu clone sạch từ `main`.

## 6.3. Việc cần xác nhận trước bản nộp cuối

1. TV1/TV2/TV3 chốt H1–H5 trên [issue #3](https://github.com/world-ender1/database-encryption-lab/issues/3), review theo phần sở hữu và merge các PR. `pytest` phải chạy trên đúng commit sẽ merge; chủ repo bật required status check theo kế hoạch khi workflow đã ở `main`.
2. Tạo PR chứa API/DB và sửa tích hợp local, tránh PR trùng nội dung TV3. Chạy lại pytest, demo, smoke, attack lab trên `main` sau merge; lưu log của đúng commit.
3. Nghiệm thu clone sạch, chụp ảnh Swagger, `psql`, attack lab, pytest và GitHub Actions từ bản cuối; che khóa và token. Hoàn tất tên/MSSV, thống nhất Word/PowerPoint, luyện demo 12 phút rồi mới tạo tag `v1.0.0`.

Các mục trên là điều kiện quy trình và sản phẩm nộp; chúng không phủ nhận kết quả chạy được của code local. Lịch sử Sprint 0 đã lệch kế hoạch nhưng không cần dựng lại commit hoặc force-push.

## 6.4. Hướng phát triển

Một bản triển khai thực tế cần quản lý khóa bằng KMS hoặc vault và quy trình rotation có migration dữ liệu, dùng TLS và xác thực người dùng thay token tĩnh, kiểm soát quyền truy cập DB, backup/restore, giám sát và audit log. Nếu cần chống replay, hệ thống phải có phiên bản bản ghi hoặc bộ đếm đơn điệu được bảo vệ ở nơi không thể bị rollback cùng ciphertext. Tìm kiếm trên trường đã mã hóa cần thiết kế riêng, cân bằng giữa truy vấn và rò rỉ thông tin. Hiệu năng cần đo thêm trên nhiều máy, tải đồng thời, kích thước dữ liệu đa dạng và dung lượng lưu trữ thực tế.
