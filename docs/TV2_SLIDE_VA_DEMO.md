# Slide và lời dẫn TV2 — 3 phút (mốc 2:00–5:00 của nhóm)

**Trạng thái:** dùng để chuẩn bị/luyện tập. Chỉ demo kết luận bảo mật sau khi TV1 thay crypto tạm bằng AES-GCM thật và các kiểm tra bắt buộc đạt.

## Slide 1 — Kiến trúc hệ thống (2:00–2:30)

- Client/Swagger → FastAPI → CryptoService → PostgreSQL.
- TV1: mật mã + auth; TV2: API + DB + Docker; TV3: kiểm thử bảo mật.
- Khóa nằm ngoài bảng students; API kiểm tra quyền trước khi trả dữ liệu rõ.

Lời dẫn: “Phần của em kết nối API với cơ sở dữ liệu. Ứng dụng nhận dữ liệu rõ, gọi dịch vụ mật mã cho ba trường nhạy cảm rồi mới lưu kết quả vào PostgreSQL. Khi đọc, API kiểm tra quyền rồi gọi giải mã. Module mật mã và kiểm tra token do thành viên 1 cung cấp theo giao diện chung.”

## Slide 2 — Luồng ghi và đọc (2:30–2:50)

- POST: admin → kiểm tra body → encrypt 3 field → commit → 201.
- GET: admin/viewer → đọc row → decrypt → 200.
- Trùng mã: 409 duplicate_student; lỗi xác thực dữ liệu: 409 integrity_failure.
- PUT giữ nguyên student_id, tạo nonce mới cho cả ba field.

Lời dẫn: “Cùng một API có hai đường xử lý. Khi ghi, ba trường được chuyển thành ciphertext và nonce. Khi đọc, các cặp này được đưa lại cho CryptoService với đúng mã sinh viên, tên trường và phiên bản khóa. Hồ sơ lỗi sẽ không được trả về như dữ liệu hợp lệ.”

## Chuyển sang Swagger — tạo và đọc (2:50–4:05)

Trước buổi trình bày, authorize bằng token admin khi chưa chia sẻ màn hình. Chọn một ID chưa tồn tại, ví dụ SV9003, và thay nếu đã được dùng. Dữ liệu mẫu:

```json
{
  "student_id": "SV9003",
  "full_name": "Le Van C",
  "major": "Computer Science",
  "national_id": "111122223333",
  "phone": "0900000003",
  "address": "Hue (fictional)"
}
```

1. Mở POST /students, Execute → chỉ vào 201 và body dữ liệu giả.
2. GET /students/SV9003 → chỉ vào 200 và dữ liệu khớp.
3. Giải thích ngắn: API được phép trả plaintext cho người đủ quyền.

Nếu POST trả 409 duplicate_student, dùng ID khác hoặc đọc hồ sơ demo đã chuẩn bị; không sửa/xóa dữ liệu lạ trên sân khấu. Không mở `.env` khi đang chiếu màn hình.

## Slide 3 / terminal — lưu trữ trong DB (4:05–4:40)

```powershell
docker compose exec -T db psql -U demo -d encryption_demo -c "SELECT student_id, full_name, major, encode(phone_ct, 'hex') AS phone_ct, octet_length(phone_nonce) AS nonce_bytes, key_version FROM students WHERE student_id='SV9003';"
```

- Tên/ngành vẫn rõ; phone_ct là BYTEA hiển thị hex; nonce dài 12 byte.
- Hex chỉ là biểu diễn: bằng chứng mật mã cần AES-GCM thật và kiểm thử.
- Đối chiếu mã sinh viên với hồ sơ vừa tạo trên Swagger.

Lời dẫn chỉ dùng **sau nghiệm thu AES-GCM**: “Đây là cùng hồ sơ vừa xem qua API. Tên và ngành được để rõ theo thiết kế, còn điện thoại được lưu dưới dạng ciphertext. PostgreSQL không giữ khóa trong bảng này. Kết quả không chỉ dựa vào việc nhìn thấy hex mà còn được kiểm tra bằng bộ test mật mã và thử nghiệm của nhóm.”

Khi luyện với bản tạm, phải nói thay bằng: “Đây mới là định dạng lưu trữ của luồng tích hợp; bản crypto tạm vẫn chứa plaintext nên chưa dùng để kết luận bảo mật.”

## Slide 4 — Kết quả và chuyển phần (4:40–5:00)

- CRUD và Docker đã có kiểm thử độc lập với thuật toán mã hóa.
- Hiện còn chờ AES-GCM thật; không dùng 73 passed / 3 xfailed làm bằng chứng an toàn.
- Chuyển TV3: thử 401/403, sửa dữ liệu, tráo hàng và khôi phục.

Lời dẫn: “Phần API và database cung cấp đường ghi/đọc cùng các mã lỗi ổn định. Tiếp theo, thành viên 3 sẽ kiểm tra hệ thống phản ứng ra sao khi truy cập sai quyền hoặc dữ liệu bị thay đổi.”

## Checklist chuẩn bị và tổng duyệt

- [ ] TV1 đã merge AES-GCM và gỡ các xfail tương ứng, smoke check không phát hiện plaintext.
- [ ] Docker DB/API healthy, `/docs` mở được, SV9001/SV9002 đã sẵn sàng cho TV3.
- [ ] Đã reset dữ liệu từ crypto tạm ở phạm vi demo được phép thay thế.
- [ ] Chọn ID demo chưa dùng, chuẩn bị JSON và câu SELECT trên.
- [ ] Authorize trước khi trình chiếu; tắt thông báo, tăng cỡ chữ terminal.
- [ ] Chụp ảnh dự phòng từ lần chạy thật, không lấy kết quả kỳ vọng làm kết quả đo.
- [ ] Tự bấm giờ 3 phút; chạy thử toàn nhóm 12 phút trên máy demo.

## Câu hỏi ngắn để luyện

**Tại sao API đọc được mà DB không nên đọc được field nhạy cảm?** API có khóa và đã xác thực người gọi; DB chỉ lưu đầu ra crypto theo thiết kế mục tiêu.

**Có phải mọi cột đều được mã hóa?** Không. Chỉ national_id, phone và address; ID, tên và ngành còn rõ.

**Tại sao xem hex chưa đủ?** Mọi byte, gồm cả plaintext, đều có thể chuyển sang hex.

**GET danh sách có một hồ sơ hỏng thì sao?** Trả 409 cả danh sách, kèm student_ids bị lỗi.

**Tại sao DELETE không giải mã?** Để admin vẫn dọn được hồ sơ hỏng hoặc dữ liệu từ bản crypto cũ.
