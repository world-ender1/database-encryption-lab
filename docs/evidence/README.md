# Bằng chứng nghiệm thu tích hợp TV2

Ngày 15/11/2026. Các file chỉ chứa kết quả và dữ liệu giả; không chứa cấu hình bí mật.

- `../tv2_verification.json`: thời điểm UTC, PostgreSQL 17.12 và 19 kiểm tra smoke đạt.
- `tv2_integration_runs.json`: stdout/mã thoát của demo_client, verify_tv2, attack_lab và benchmark; tất cả exit 0.
- `benchmark_integration.csv`: bản sao số đo thật từ benchmark_results.csv trong môi trường thử riêng, đưa vào đây để có thể review dù file gốc được gitignore.

Môi trường: Windows host, Python 3.12.1; CPU Intel Core i7-12700H, 14 cores/20 logical processors. Docker Engine 29.6.2 chạy PostgreSQL 17.12 (Debian) và API Python 3.12.16. API build từ python:3.12-slim với requirements.txt của TV3; test Linux 91 passed, pip check đạt. API/DB trên Docker, benchmark chạy từ Python host qua loopback. Không coi đây là số đo trên máy chuyên dụng không tải nền.

Benchmark TV3 đo 100/1.000/10.000 bản ghi, một lần warmup bỏ khỏi thống kê và ba lần đo lấy trung vị. insert bao gồm tạo dữ liệu và mã hóa ở chế độ AES-GCM; read bao gồm giải mã. payload_bytes cộng byte ba field và nonce/tag, không đo dung lượng bảng/index/WAL trên đĩa. Ba field thêm tổng cộng 84 byte/hồ sơ (3 × (16 + 12)).

Ở n=100, thời gian đọc AES-GCM có thể thấp hơn plaintext trong mẫu này do nhiễu đo ở mức mili giây; không kết luận mã hóa làm đọc nhanh hơn. TV3 cần chạy/diễn giải riêng, bổ sung cấu hình máy đầy đủ và biểu đồ trong Chương 5.

Tái chạy trên dữ liệu demo riêng:

```powershell
docker compose up -d --build --wait
.\.venv\Scripts\python.exe -m scripts.demo_client
.\.venv\Scripts\python.exe -m scripts.verify_tv2
.\.venv\Scripts\python.exe -m scripts.attack_lab
.\.venv\Scripts\python.exe -m scripts.benchmark
```

Các lệnh dùng .env ở thư mục chạy; lần nghiệm thu này thực hiện trên bản sao tạm có .env/volume/cổng riêng, không tác động dữ liệu repo đang có. Để tái tạo cùng mức cô lập, dùng bản clone riêng, tạo .env mới và project Compose riêng, đổi API_PORT/DB_PORT cùng DATABASE_URL nếu cổng đang được dùng. Chỉ chạy attack_lab với SV9001/SV9002 là dữ liệu giả được phép thử.
