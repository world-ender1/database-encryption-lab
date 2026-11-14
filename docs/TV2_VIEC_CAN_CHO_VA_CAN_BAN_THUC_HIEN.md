# TV2 — Công việc cần chờ thành viên khác hoặc cần bạn thực hiện

Cập nhật: 14/11/2026.

Phạm vi: phần 3 của `Ke_hoach_thuc_hien_TV2.md` và kế hoạch nhóm v3 do bạn cung cấp. Danh sách dựa trên lần kiểm tra repo gần nhất; chưa xác minh cập nhật mới trên GitHub. Code CRUD, báo cáo và slide đã được chuẩn bị local, nhưng chưa được nghiệm thu theo đúng thứ tự Sprint.

**Thứ tự ưu tiên: hoàn tất Sprint 0 trước, rồi tuần 1 → tuần 2 → tuần 3 → tuần 4. Không cần chờ AES-GCM thật để làm khung và API bằng crypto tạm.**

## 1. Sprint 0 — Cần giải quyết trước tiên

### [ ] 1.1. Xác nhận hợp đồng H1–H5 với cả nhóm

- **Bước trong kế hoạch:** 1.
- **Cần ai:** bạn, TV1 và TV3; TV3 chủ trì.
- **Đã có:** mã và tài liệu đã được đối chiếu theo H1–H5.
- **Còn thiếu:** xác nhận của cả ba; repo có tài liệu v4 trong khi yêu cầu ban đầu chỉ định v3.
- **Bạn cần làm:** thống nhất phiên bản kế hoạch và xác nhận giao diện crypto/auth, API, tên bảng/cột, biến cấu hình, fixture.
- **Xong khi:** H1–H5 được ghi lại và cả ba đồng ý. Việc đọc tài liệu không thay cho sự đồng ý của nhóm.

### [ ] 1.2. Nhận hoặc thống nhất phần khung của TV3

- **Bước liên quan:** 3–9, phụ thuộc Sprint 0 chung.
- **Cần ai:** TV3.
- **Đã có:** tôi đã tạo hỗ trợ `requirements.txt` và `tests/conftest.py` để chạy thử local. Ở lần kiểm tra gần nhất, `requirements.txt` đã nằm trong commit `90e613f` trên nhánh `feature/api-db` và ref remote tại máy.
- **Còn thiếu:** TV3 tiếp nhận/review hai file này và cung cấp CI, `tests/__init__.py`, `scripts/__init__.py` theo kế hoạch.
- **Bạn cần làm:** bàn giao phần hỗ trợ cho TV3, thống nhất cách đưa vào nhánh chung; không ghi nhận chúng là phần việc riêng đã hoàn thành của TV2.
- **Xong khi:** dependencies/fixture thống nhất, fixture override đúng `app.database.get_db`, CI chạy được trên bộ khung chung.

### [ ] 1.3. Phối hợp bổ sung và nghiệm thu Sprint 0 trên main

- **Bước trong kế hoạch:** 2, 7–9.
- **Cần ai:** bạn bàn giao phần TV2; TV3 điều phối PR; cả nhóm review.
- **Đã biết:** commit `4592eac` mang tên merge PR Sprint 0 nhưng tree tại mốc đó chỉ có phần TV1, chưa có API/Docker TV2 và khung TV3.
- **Còn thiếu:** bản khung TV2 riêng với `/health` trả 200, CRUD tạm trả 501 và gắn auth; PR bổ sung đủ phần nhóm rồi nghiệm thu trên main.
- **Bạn cần phối hợp:** thống nhất cập nhật `sprint0/skeleton` và PR bổ sung với TV3. Giữ nguyên lịch sử PR đã merge; không reset hoặc force-push để tạo lại lịch sử.
- **Xong khi:** PR bổ sung được review/merge, main có đủ khung và `docker compose up` cho `/health` = 200.
- **Lưu ý:** chuẩn bị/tách bản khung local là việc tôi có thể tiếp tục làm; phần cần nhóm là đồng bộ nhánh chung, review, merge và xác nhận nghiệm thu. Các việc này chưa được thực hiện trong lần tạo danh sách này.

## 2. Tuần 1 — Phụ thuộc review phần TV1

### [ ] 2.1. Review PR crypto của TV1

- **Bước trong kế hoạch:** 13, sau bước 10–12.
- **Cần ai:** TV1 cung cấp PR; bạn là người review theo phân công.
- **Đã có:** ghi chú đọc source local tại `docs/TV2_REVIEW_GHI_CHU.md`.
- **Còn thiếu:** review/nhận xét trên PR thực tế. Ghi chú local không được coi là đã approve PR.
- **Nội dung kiểm tra:** H1 không đổi; không log khóa; lỗi giải mã được chuẩn hóa thành `IntegrityFailure`.
- **Xong khi:** đã approve hoặc để lại nhận xét trên PR crypto, đúng điều kiện bước 13.

## 3. Tuần 2 — Phụ thuộc TV3 và quy trình PR

### [ ] 3.1. Chốt fixture và bàn giao test quyền/tamper cho TV3

- **Bước trong kế hoạch:** 16.
- **Cần ai:** TV3.
- **Đã có:** các test local chạy được, nhưng tôi đã đưa test quyền/tamper vào `tests/test_api.py`, lệch phân công của bước 16.
- **Cần thống nhất:** chuyển phần kiểm tra quyền/tamper phù hợp sang bộ test do TV3 phụ trách; chốt fixture trước khi tích hợp. Test nonce mới hiện dùng thêm `db_session`, ngoài các fixture H5 được nêu trong kế hoạch.
- **Xong khi:** `test_api.py` đúng phạm vi TV2, các test bàn giao được TV3 tiếp nhận và bộ kiểm thử tích hợp chạy đạt.
- **Lưu ý:** tôi có thể chuẩn bị phần tách test và chạy kiểm tra local; cần TV3 xác nhận để tránh chồng sửa file của họ.

### [ ] 3.2. Bàn giao code qua PR api-db

- **Bước trong kế hoạch:** 18; chỉ thực hiện sau các bước trước.
- **Cần ai:** bạn, TV1 và TV3.
- **Đã có:** code local và `docs/TV2_PR_DRAFT.md`. Commit requirements hiện có không chứa toàn bộ code API.
- **Còn thiếu:** commit/push phần TV2 đúng phạm vi, PR, CI và review/merge. Chưa có bằng chứng các mốc này đã hoàn tất.
- **Bạn cần phối hợp:** xác định đúng repo/nhánh, bàn giao PR cho TV1 và TV3 review, xử lý phản hồi.
- **Xong khi:** PR api-db được merge theo quy trình nhóm.
- **Lưu ý:** tôi có thể hỗ trợ chuẩn bị commit hoặc thao tác Git khi được giao; không thể tự thay sự phê duyệt của reviewer.

### [ ] 3.3. Review PR security-benchmark của TV3

- **Bước trong kế hoạch:** 18, khi được gán review.
- **Cần ai:** TV3 cung cấp PR; bạn review.
- **Cần kiểm tra:** dùng đúng H2/H3, không đổi tên bảng/cột; test không phụ thuộc chi tiết nội bộ ngoài hợp đồng; có khôi phục dữ liệu sau thử nghiệm.
- **Xong khi:** đã review PR thực tế và xử lý các phản hồi liên quan TV2.

## 4. Tuần 3 — Cần crypto thật và bộ kiểm thử tích hợp

### [ ] 4.1. Nhận AES-256-GCM thật từ TV1

- **Bước liên quan:** điều kiện trước bước 19.
- **Cần ai:** TV1.
- **Hiện trạng:** `CryptoService` tại lần kiểm tra gần nhất vẫn là bản tạm Sprint 0; đầu ra còn chứa plaintext. Ba test crypto còn xfail.
- **TV1 cần bàn giao:** AES-256-GCM đúng H1; xử lý lỗi giải mã; hoàn thiện C01–C07; gỡ marker xfail tương ứng khi bản thật đã sẵn sàng.
- **Xong khi:** code thật được tích hợp, kiểm thử mật mã đạt và H1 không bị thay đổi ngoài thỏa thuận.
- **Lưu ý:** tôi không thay module này trong phần việc TV2. Crypto tạm vẫn được phép dùng cho triển khai khung và API trước giai đoạn nghiệm thu này.

### [ ] 4.2. Nghiệm thu lại PostgreSQL sau khi có crypto thật

- **Bước trong kế hoạch:** 19.
- **Cần chờ:** mục 4.1 và các mốc tích hợp trước đó.
- **Đã có:** Docker/API chạy được; kiểm tra PostgreSQL đã ghi `blocked_by_plaintext` trong `docs/tv2_verification.json`.
- **Sau khi nhận TV1:** build lại, xử lý dữ liệu demo từ crypto tạm trong phạm vi được phép thay, chạy lại pytest và `scripts.verify_tv2`.
- **Xong khi:** các kiểm tra đạt, cột nhạy cảm không chứa plaintext; kết quả được ghi lại từ lần chạy với AES-GCM thật. Nhìn thấy chuỗi hex chưa đủ chứng minh mã hóa.
- **Lưu ý:** tôi có thể chạy lại các kiểm tra này khi đầu vào đã sẵn sàng; hiện chưa thể đóng bước bằng kết quả crypto tạm.

### [ ] 4.3. Tích hợp attack lab và xử lý issue của TV3

- **Bước trong kế hoạch:** 20 và Definition of Done TV2.
- **Cần ai:** TV3 cung cấp `test_security.py`, `attack_lab.py` và kết quả/issue liên quan API/DB.
- **Còn thiếu:** tại lần kiểm tra gần nhất, các file này chưa có trong working tree đang dùng.
- **Cần làm khi có:** chạy kịch bản theo H2/H3, kiểm tra API trả 200 sau restore; sửa lỗi TV2 bằng PR nhỏ có test tái hiện.
- **Xong khi:** TV3 chạy được attack lab trên hệ thống, lỗi thuộc TV2 được xử lý và review.
- **Phạm vi:** benchmark và Chương 5 do TV3 phụ trách; TV2 hỗ trợ tích hợp, không nhận thay toàn bộ phần đó.

### [ ] 4.4. Hoàn thiện và gửi Chương 3–4

- **Bước trong kế hoạch:** 21.
- **Cần ai:** TV1 cung cấp phần module mã hóa/xác thực và ghép báo cáo; bạn cung cấp họ tên/MSSV, yêu cầu trình bày của nhóm.
- **Đã có:** bản nháp Markdown và Word trong `docs/TV2_BAO_CAO_CHUONG_3_4.*`.
- **Còn thiếu:** nội dung TV1 cho phần 4.5, số liệu nghiệm thu sau tích hợp, thông tin cá nhân và bản ghép chung.
- **Xong khi:** phần TV2 được cập nhật bằng kết quả thật và gửi TV1 để ghép báo cáo. Chưa có việc gửi tài liệu cho thành viên khác từ phía tôi.

## 5. Tuần 4 — Cần bạn và cả nhóm trực tiếp thực hiện

### [ ] 5.1. Chuẩn bị minh chứng và demo Swagger/psql

- **Bước trong kế hoạch:** 22.
- **Cần ai:** bạn; chờ hệ thống đã nghiệm thu crypto thật.
- **Đã có:** `docs/TV2_HE_THONG.pptx` và `docs/TV2_SLIDE_VA_DEMO.md`.
- **Bạn cần làm:** cập nhật slide theo kết quả mới, authorize trước khi trình chiếu, demo POST/GET, đối chiếu cùng hồ sơ trong psql và chuẩn bị ảnh dự phòng từ lần chạy thật.
- **Xong khi:** thao tác được trên máy demo, giải thích đúng phạm vi bảo vệ, không đưa token/key lên màn hình.
- **Lưu ý:** slide hiện ghi rõ crypto tạm; chưa dùng để khẳng định hệ thống đã có bảo mật AES-GCM.

### [ ] 5.2. Luyện phần trình bày 3 phút

- **Bước trong kế hoạch:** 23.
- **Cần ai:** bạn.
- **Cần làm:** tự trình bày và bấm giờ phần 2:00–5:00; luyện trả lời câu hỏi về API, schema, quyền, ciphertext và giới hạn.
- **Xong khi:** bạn thực hiện được phần của mình trong 3 phút. Tôi có thể hỗ trợ kịch bản và luyện hỏi đáp, nhưng không thay việc bạn trực tiếp tổng duyệt.

### [ ] 5.3. Tổng duyệt cả nhóm 12 phút

- **Bước trong kế hoạch:** 23.
- **Cần ai:** cả ba thành viên; TV3 điều phối phần máy demo/nghiệm thu.
- **Cần làm:** chạy trọn luồng thuyết trình, chuyển phần TV1 → TV2 → TV3, thử demo và phương án dự phòng trên máy đích.
- **Xong khi:** cả nhóm tổng duyệt thành công; báo cáo, slide và kết quả demo nhất quán.

## 6. Việc tôi vẫn có thể tiếp tục làm, không nên coi là đang chờ người khác

Các việc dưới đây là phần khắc phục local còn lại sau khi phát hiện làm sai trình tự. Chúng cần được thực hiện trong giai đoạn phù hợp, không đẩy toàn bộ cho bạn:

- Bảo toàn code đã viết và chuẩn bị riêng gói Sprint 0 với CRUD 501, đúng phạm vi TV2.
- Kiểm tra bản khung, chuẩn bị mô tả commit/PR Sprint 0 và bằng chứng local.
- Chuẩn bị nội dung tách test quyền/tamper để TV3 tiếp nhận.
- Đưa lại phần CRUD theo từng mốc sau khi Sprint 0 được chốt.
- Chạy lại kiểm thử, xử lý lỗi TV2 và cập nhật tài liệu khi nhận đủ code từ TV1/TV3.

**Lần tạo file này chỉ tổng hợp công việc; chưa thực hiện các bước khắc phục local trên, chưa đổi nhánh, commit, push hoặc liên hệ thành viên khác.**

## 7. Nội dung ngắn để bạn trao đổi với nhóm

> Mình là TV2. Phần API/DB đã có bản chuẩn bị local, nhưng cần hoàn tất Sprint 0 đúng kế hoạch trước. Nhờ cả nhóm xác nhận H1–H5 và bản kế hoạch đang dùng. TV3 giúp chốt dependencies, fixture, CI và điều phối PR bổ sung khung vào main; mình sẽ bàn giao khung TV2 riêng. Sau đó mình làm tiếp các mốc CRUD. Khi TV1 có PR crypto/AES-GCM thật, gửi mình review và tích hợp để nghiệm thu lại PostgreSQL. Phần test quyền/tamper cần bàn giao TV3 theo đúng phân công.

Đoạn trên là bản nháp để bạn sử dụng; tôi chưa gửi tin nhắn này cho bất kỳ ai.

## Tài liệu liên quan

- [Đối chiếu đủ 23 bước và sai lệch trình tự](TV2_KIEM_TRA_TRINH_TU_SPRINT.md)
- [Ghi chú review TV1/TV3](TV2_REVIEW_GHI_CHU.md)
- [Hướng dẫn API và DB](api_db.md)
- [Kịch bản demo](TV2_SLIDE_VA_DEMO.md)
