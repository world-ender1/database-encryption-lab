# Tóm tắt dự án: Database Encryption

> Tóm tắt từ `Ke_hoach_Database_Encryption_3_thanh_vien_v4.docx`. Đọc file này trong khoảng 5 phút để nắm dự án làm gì trước khi đọc tài liệu đầy đủ.

---

## 1. Dự án này là gì?

Đây là **đồ án môn Mật mã & An toàn thông tin** cho nhóm 3 người, làm trong 4 tuần.

**Đề tài:** mã hóa dữ liệu nhạy cảm trước khi lưu vào cơ sở dữ liệu PostgreSQL, và việc mã hóa do **ứng dụng** làm chứ không phải do database tự làm.

Nói ngắn gọn: nhóm xây một hệ thống quản lý hồ sơ sinh viên nhỏ. Khi lưu hồ sơ, các thông tin nhạy cảm được mã hóa bằng **AES-256-GCM** rồi mới ghi xuống database. Sau đó nhóm **tự tấn công thử** hệ thống của mình để chứng minh mã hóa bảo vệ được gì, không bảo vệ được gì, và **đo xem** mã hóa làm hệ thống chậm đi bao nhiêu.

> Nhóm **tự viết toàn bộ mã nguồn từ đầu**. Hiện tại thư mục `C:\mat ma` mới có tài liệu kế hoạch; mã nguồn sẽ xuất hiện sau Sprint 0 (ngày 1–2).

---

## 2. Bài toán mẫu

Hệ thống lưu hồ sơ sinh viên với **dữ liệu giả**, không dùng thông tin thật của ai.

| Trường | Ví dụ | Lưu trong DB |
|---|---|---|
| `student_id` | SV9001 | Dạng rõ (khóa chính) |
| `full_name` | Nguyen Van A | Dạng rõ |
| `major` | Computer Science | Dạng rõ |
| `national_id` (CCCD giả) | 012345678901 | **Mã hóa** |
| `phone` | 0901234567 | **Mã hóa** |
| `address` | Ha Noi (fictional) | **Mã hóa** |

Ba trường đầu cố ý để dạng rõ, để khi mở database ra thấy ngay sự khác biệt giữa dữ liệu thường và dữ liệu đã mã hóa.

---

## 3. Hệ thống hoạt động thế nào?

### Khi lưu một hồ sơ (POST)

```
Người dùng (Swagger hoặc script demo_client)
   │  gửi JSON hồ sơ + token admin
   ▼
API FastAPI
   │  1. Kiểm tra token: admin mới được ghi
   │  2. Kiểm tra dữ liệu hợp lệ
   │  3. Gọi CryptoService mã hóa riêng từng trường nhạy cảm   ◄── khóa AES đọc từ file .env
   │     (mỗi lần mã hóa sinh một nonce mới)                        (khóa KHÔNG nằm trong DB)
   ▼
PostgreSQL
   lưu: tên, ngành ở dạng rõ + ciphertext, nonce, key_version cho 3 trường nhạy cảm
```

### Khi đọc một hồ sơ (GET)

1. API kiểm tra token (admin hoặc viewer đều được đọc).
2. Lấy ciphertext và nonce từ database.
3. Giải mã. AES-GCM tự kiểm tra dữ liệu có bị sửa không.
4. Nếu đúng: trả hồ sơ đã giải mã. Nếu dữ liệu bị sửa hoặc bị tráo: trả lỗi **409**, không trả dữ liệu hỏng.

### Cùng một hồ sơ, hai góc nhìn (minh họa)

| Ai nhìn | Thấy `phone` là |
|---|---|
| Người có token gọi API | `0901234567` |
| Người mở thẳng database | `9c41e07b...` (chuỗi hex vô nghĩa) |

---

## 4. Các khái niệm cần biết

| Thuật ngữ | Giải thích ngắn |
|---|---|
| **Plaintext / Ciphertext** | Dữ liệu gốc / dữ liệu sau khi mã hóa |
| **AES-256-GCM** | Thuật toán mã hóa đối xứng, khóa 256 bit. Chế độ GCM vừa giấu nội dung vừa phát hiện được dữ liệu bị sửa |
| **Key (khóa)** | 32 byte bí mật dùng để mã hóa và giải mã. Mất khóa là mất dữ liệu vĩnh viễn; lộ khóa là lộ dữ liệu |
| **Nonce** | 12 byte ngẫu nhiên, mỗi lần mã hóa một nonce mới. Không cần giữ bí mật nhưng không được dùng lại với cùng khóa |
| **Tag** | 16 byte “dấu kiểm tra” gắn sau ciphertext. Sửa dù 1 byte là tag không khớp, giải mã thất bại |
| **AAD** | Thông tin gắn kèm khi mã hóa, không bị giấu nhưng được kiểm tra. Ở đây AAD gồm mã sinh viên + tên trường, nên không thể chép ciphertext của sinh viên này sang sinh viên khác |
| **key_version** | Nhãn phiên bản khóa (v1), chuẩn bị cho việc đổi khóa sau này |
| **Admin / Viewer** | Hai vai trò: admin được thêm, sửa, xóa; viewer chỉ được đọc |

---

## 5. API của hệ thống

| Lệnh | Đường dẫn | Ai được dùng | Kết quả |
|---|---|---|---|
| GET | `/health` | Ai cũng được | 200, kiểm tra hệ thống sống |
| POST | `/students` | admin | 201, tạo hồ sơ |
| GET | `/students` | admin, viewer | 200, danh sách (có hồ sơ bị sửa → 409 cả danh sách) |
| GET | `/students/{id}` | admin, viewer | 200 hoặc 404 |
| PUT | `/students/{id}` | admin | 200, cập nhật (không đổi được mã sinh viên) |
| DELETE | `/students/{id}` | admin | 204, xóa |

Mã lỗi chung:
- **401**: thiếu hoặc sai token.
- **403**: viewer cố ghi/xóa.
- **409**: kèm `code` để phân biệt `duplicate_student` (trùng mã) và `integrity_failure` (dữ liệu mã hóa bị sửa).
- **422**: mã sinh viên sai định dạng (chỉ nhận chữ và số, tối đa 16 ký tự).

---

## 6. Nhóm sẽ chứng minh điều gì?

### Tấn công thử (trên database demo của chính nhóm)

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| A1 | Gọi API không có token | 401, bị chặn |
| A2 | Viewer cố xóa hồ sơ | 403, dữ liệu còn nguyên |
| A3 | Lấy được bản sao database (dump) | Chỉ thấy ciphertext, không đọc được CCCD |
| A4 | Sửa 1 byte ciphertext trong DB | API phát hiện, trả 409 |
| A5 | Tráo ciphertext giữa 2 sinh viên | AAD không khớp, trả 409 |
| A6 | Giải mã bằng khóa sai | Thất bại |
| A7 | Chép lại ciphertext **cũ** vào đúng hàng đó | **Vẫn giải mã được**: đây là giới hạn, không phải thành công |
| A8 | Nhập ID có ký tự kiểu SQL injection | 422, database không bị ảnh hưởng |

Script tấn công tự khôi phục dữ liệu gốc sau mỗi lần thử.

### Đo hiệu năng (benchmark)

So sánh lưu dữ liệu dạng rõ và dạng mã hóa với 100, 1.000 và 10.000 bản ghi, mỗi mức chạy 3 lần. Đo thời gian ghi, thời gian đọc và dung lượng tăng thêm. Kết quả xuất ra file CSV và vẽ biểu đồ.

---

## 7. Mã hóa bảo vệ được gì, không bảo vệ được gì?

**Bảo vệ được:**
- Lộ bản sao database nhưng không lộ khóa: 3 trường nhạy cảm không đọc được.
- Ai đó sửa hoặc tráo dữ liệu mã hóa trong DB: hệ thống phát hiện.

**Không bảo vệ được:**
- Tên, ngành, số lượng bản ghi vẫn lộ (vì không mã hóa).
- Máy chạy ứng dụng bị chiếm, hoặc khóa bị lộ: mất bảo vệ.
- Chép lại ciphertext cũ vào đúng hàng cũ (replay, A7).
- Không tìm kiếm trực tiếp được kiểu `WHERE phone = ...` trên cột đã mã hóa.
- Đây là bản demo: token tĩnh, chạy cục bộ, chưa có hệ thống quản lý khóa (KMS) hay xoay khóa.

---

## 8. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.12 |
| Web API | FastAPI (có giao diện thử Swagger tại `http://127.0.0.1:8000/docs`) |
| Truy cập DB | SQLAlchemy 2 |
| Database | PostgreSQL 17 |
| Mã hóa | Thư viện `cryptography`, AES-256-GCM |
| Chạy môi trường | Docker Compose (DB + API) |
| Kiểm thử | pytest; GitHub Actions tự chạy test mỗi khi có PR |

---

## 9. Ai làm gì? (theo bản phân công v4)

| Thành viên | Phụ trách | Sản phẩm chính |
|---|---|---|
| **TV1** – Mật mã, Khóa & Xác thực | Tạo và quản trị repo (chủ repo, branch protection); module mã hóa AES-GCM, sinh và nạp khóa, kiểm tra token admin/viewer; ghép báo cáo và slide | `crypto_service.py`, `key_manager.py`, `auth.py`, `init_env.py`, test C01–C07, `crypto_design.md`; Chương 1–2 |
| **TV2** – Database & API | Database, API CRUD, Docker | Phần còn lại của `app/`, `Dockerfile`, `compose.yaml`, `demo_client.py`, `test_api.py`, `api_db.md`; Chương 3–4 |
| **TV3** – Bảo mật, Benchmark, CI; trưởng nhóm kỹ thuật | CI, kiểm thử bảo mật, tấn công thử, đo hiệu năng, nghiệm thu, gắn tag | `conftest.py`, `test_security.py`, `attack_lab.py`, `benchmark.py`, CI, README, `threat_model.md`; Chương 5 |

Cách phối hợp: ngày 1–2 cả nhóm làm **Sprint 0** trên một nhánh chung. Cả nhóm chốt 5 “hợp đồng” (tên hàm, API, tên bảng/cột, biến cấu hình, dữ liệu demo) và đẩy lên một bộ khung chạy được bằng một PR duy nhất. Sau đó mỗi người làm phần của mình song song, không phải chờ nhau. Mỗi người chỉ dựa vào hợp đồng, không dựa vào file của người khác: ai cũng chạy được test của mình khi chưa có file của hai người còn lại; chỉ các điểm ghép (PR Sprint 0, review, nghiệm thu chung) mới cần nhau.

### Lịch 4 tuần

| Tuần | Nội dung |
|---|---|
| 1 | Sprint 0; mỗi người làm phần lõi của mình |
| 2 | Hoàn thiện, mở PR, review chéo, merge vòng 1 |
| 3 | Chạy tấn công thử và benchmark trên PostgreSQL thật, sửa lỗi |
| 4 | Slide, báo cáo, tổng duyệt demo |

---

## 10. Sản phẩm cuối cùng phải nộp

- Repository GitHub có README, chạy được trên máy sạch, gắn tag `v1.0.0`.
- Bộ test tự động chạy xanh trên GitHub Actions.
- Ảnh minh chứng: Swagger, ciphertext trong database, kết quả tấn công A1–A5.
- File CSV và biểu đồ benchmark từ số liệu đo thật.
- Báo cáo 6 chương: mở đầu, lý thuyết, thiết kế, triển khai, thử nghiệm, đánh giá và hạn chế.
- Buổi demo 12 phút: TV1 giải thích AES-GCM, TV2 demo API và database, TV3 demo tấn công và benchmark, cả nhóm trình bày giới hạn và trả lời câu hỏi.

---

## 11. Đọc tiếp ở đâu?

| Muốn biết | Đọc |
|---|---|
| Toàn bộ kế hoạch chi tiết | `Ke_hoach_Database_Encryption_3_thanh_vien_v4.docx` |
| Phân công và 5 hợp đồng | Mục 02 của file trên |
| Cài đặt môi trường | Mục 03 |
| Việc riêng của từng người | Mục 04 (TV1), 05 (TV2), 06 (TV3) |
| Các bước làm theo thứ tự của từng người | `Ke_hoach_thuc_hien_TV1.md`, `Ke_hoach_thuc_hien_TV2.md`, `Ke_hoach_thuc_hien_TV3.md` |
| Câu hỏi giảng viên hay hỏi | Mục 9.3 |
