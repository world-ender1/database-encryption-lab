# Bản nháp báo cáo — Phần thành viên 2

Ngày cập nhật: 16/11/2026. Người thực hiện: [điền họ tên, MSSV].

Tài liệu mô tả bản tích hợp local `integration/tv2-merge-prep`: API/DB của TV2, AES-256-GCM của TV1 đã merge vào main và phần kiểm thử của TV3. Phần 4.5 được đối chiếu với mã TV1 và tài liệu `docs/crypto_design.md`; phần 4.6 ghi kết quả chạy thực tế. Nhóm cần review và ghép báo cáo cuối; chưa coi các kiểm tra local là PR đã được duyệt hoặc bản phát hành.

## Chương 3. Phân tích và thiết kế hệ thống

### 3.1. Bài toán và yêu cầu

Hệ thống quản lý một tập hồ sơ sinh viên giả lập gồm mã sinh viên, họ tên, ngành học, số định danh, số điện thoại và địa chỉ. Mục tiêu là nghiên cứu việc bảo vệ các trường nhạy cảm trước khi chúng được lưu vào PostgreSQL. Ba trường national_id, phone và address đi qua module mật mã ở tầng ứng dụng; student_id, full_name và major được giữ rõ để minh họa ranh giới bảo vệ.

Chức năng chính gồm tạo hồ sơ, đọc một hồ sơ, liệt kê hồ sơ, cập nhật toàn bộ thông tin có thể sửa và xóa hồ sơ. Người có vai trò admin được đọc và ghi; viewer chỉ được đọc. Mã sinh viên chỉ gồm chữ và số ASCII, dài từ 1 đến 16 ký tự. Dữ liệu đầu vào phải đủ trường, không chứa trường thừa và không vượt kích thước đã quy định.

Yêu cầu phi chức năng bao gồm triển khai lại được bằng Docker Compose, tách cấu hình khỏi mã nguồn, không ghi khóa/token vào log, báo lỗi ổn định để kiểm thử tự động và giữ nguyên các giao diện mà các thành viên đã thống nhất. Tất cả dữ liệu sử dụng trong thực nghiệm là dữ liệu giả.

### 3.2. Lựa chọn mã hóa ở tầng ứng dụng

Ứng dụng gọi CryptoService trước khi ghi các giá trị nhạy cảm xuống DB. Lựa chọn này phù hợp với câu hỏi nghiên cứu: khi một đối tượng chỉ đọc được bảng hoặc bản sao DB nhưng không có khóa, dữ liệu của các trường được bảo vệ phải khó đọc được nếu module AES-GCM được triển khai đúng. Khóa được nạp riêng qua cấu hình, không nằm trong bảng students.

Cách bố trí này đưa việc giải mã vào đường xử lý của API. API cần kiểm tra quyền trước khi trả dữ liệu rõ cho người dùng. Nó cũng tạo ra chi phí mã hóa/giải mã và làm mất khả năng truy vấn trực tiếp theo nội dung rõ của các cột được mã hóa. Trong phạm vi hiện tại, nhóm chưa thiết kế chỉ mục tìm kiếm trên ciphertext.

Ranh giới bảo vệ không bao gồm máy ứng dụng đã bị chiếm, khóa bị lộ hay người dùng hợp lệ đọc dữ liệu qua API. Tên, ngành, ID, số lượng hồ sơ và kích thước dữ liệu vẫn có thể quan sát được. Không thể kết luận toàn bộ DB được che giấu chỉ vì ba trường đã mã hóa.

### 3.3. Kiến trúc và phân chia trách nhiệm

Luồng hệ thống gồm bốn thành phần: client/Swagger, API FastAPI, CryptoService và PostgreSQL. Client gửi yêu cầu qua HTTP trên loopback. FastAPI gọi dependency xác thực của TV1, kiểm tra payload bằng Pydantic, rồi sử dụng student_service để chuyển đổi giữa dữ liệu API và đối tượng lưu trữ. SQLAlchemy chịu trách nhiệm tương tác với PostgreSQL.

TV1 cung cấp decode_key, CryptoService, EncryptedValue, IntegrityFailure, require_admin và require_reader theo H1. TV2 phụ trách cấu hình, phiên DB, model, schema API, mapping dữ liệu, route và Docker. TV3 dùng H2/H3 để xây test bảo mật, attack lab và benchmark. Việc tách trách nhiệm cho phép TV2 kiểm thử luồng ứng dụng với bản crypto tạm rồi chuyển sang bản thật mà không sửa route.

Khóa và token được sinh cục bộ, đặt trong .env bị Git bỏ qua. Cổng API mặc định 8000, cổng PostgreSQL công bố ra host là 55432. Trong mạng Compose, API kết nối service db qua cổng 5432. Cả hai cổng host đều chỉ bind 127.0.0.1.

### 3.4. Thiết kế lưu trữ

Bảng students có khóa chính student_id kiểu VARCHAR(16). Hai cột full_name và major lần lượt là VARCHAR(150) và VARCHAR(100). Mỗi trường nhạy cảm có một cặp cột BYTEA: national_id_ct/national_id_nonce, phone_ct/phone_nonce, address_ct/address_nonce. Cột key_version là VARCHAR(20). Mọi cột đều không cho NULL.

Theo hợp đồng H1 của thiết kế mục tiêu, ciphertext chứa cả tag xác thực 16 byte, nonce dài 12 byte và key_version xác định phiên bản khóa. Tầng TV2 không tự sinh nonce và không trực tiếp gọi AESGCM; toàn bộ thao tác này nằm trong CryptoService. Các tên cột được giữ ổn định để TV3 đọc bằng SQL trong thử nghiệm.

BYTEA biểu diễn dữ liệu nhị phân. Hàm encode(..., 'hex') chỉ chuyển byte sang ký tự hex để quan sát; một chuỗi rõ cũng có thể được biểu diễn bằng hex. Vì vậy, ảnh chụp cột hex chỉ chứng minh kiểu lưu trữ, không đủ chứng minh tính bí mật [1].

### 3.5. API và phân quyền

GET /health công khai để kiểm tra tiến trình còn phản hồi. POST /students yêu cầu admin và trả 201. GET /students và GET /students/{student_id} cho phép admin hoặc viewer và trả dữ liệu sau giải mã. PUT /students/{student_id} yêu cầu admin, nhận đủ 5 trường có thể sửa và trả 200. DELETE yêu cầu admin, trả 204 với body rỗng.

Thiếu hoặc sai token trả 401 kèm WWW-Authenticate: Bearer. Viewer thực hiện ghi trả 403. Không tìm thấy hồ sơ trả 404 với code not_found. Trùng mã trả 409 với code duplicate_student. Lỗi xác thực dữ liệu mã hóa trả 409 với code integrity_failure. Đầu vào sai schema trả 422.

GET danh sách áp dụng quy tắc trả lỗi toàn bộ nếu bất kỳ hồ sơ nào không giải mã được. API trả danh sách student_ids bị lỗi và không trả kèm các hồ sơ giải mã thành công. PUT không cho đổi student_id vì ID là thành phần dùng khi gọi crypto. DELETE không giải mã để admin có thể dọn hồ sơ hỏng hoặc dữ liệu từ bản crypto cũ.

### 3.6. Luồng tạo, đọc và cập nhật

Khi tạo, API kiểm tra quyền admin và schema, kiểm tra trùng mã, tạo đối tượng Student, rồi gọi encrypt ba lần với đúng student_id và tên field. Ciphertext và nonce được gán vào các cột tương ứng, phiên bản khóa được lưu cùng hàng. Sau commit, API chuyển hàng về StudentOut qua decrypt để trả dữ liệu rõ cho client được phép.

Khi đọc, API kiểm tra quyền reader, tìm hàng bằng khóa chính, dựng EncryptedValue từ từng cặp ciphertext/nonce và key_version, rồi gọi decrypt với đúng ID và tên trường. Hàng không tồn tại được xử lý riêng với lỗi dữ liệu không xác thực. Với bản AES-GCM mục tiêu, AAD gắn dữ liệu với ID, field và phiên bản khóa theo H1.

Khi cập nhật, API giữ nguyên ID, mã hóa lại cả ba trường nhạy cảm và cập nhật các trường rõ trong một giao dịch. Mỗi lần gọi crypto phải tạo nonce mới. Dữ liệu mã hóa được chuẩn bị xong trước khi gán lên hàng. Các câu truy vấn dùng ORM/tham số, không nối đầu vào người dùng vào SQL.

### 3.7. Giới hạn thiết kế

Hệ thống chỉ nạp một khóa hoạt động, chưa có keyring hay rotation. AAD không tự cung cấp trạng thái chống replay: dữ liệu cũ của cùng hàng và cùng field có thể vẫn hợp lệ. Token tĩnh không cung cấp quản trị danh tính đầy đủ. Schema hiện dùng create_all thay vì migration. Danh sách chưa phân trang và mọi vai trò reader có thể xem toàn bộ hồ sơ; đây là phạm vi demo đã chọn.

## Chương 4. Triển khai hệ thống

### 4.1. Môi trường và cấu trúc chương trình

Môi trường kiểm thử phần TV2 sử dụng Python 3.12, FastAPI 0.118.0, SQLAlchemy 2.0.49, psycopg 3.2.6, Pydantic Settings 2.10.1 và pytest 8.4.2. Dockerfile dùng python:3.12-slim; Compose dùng postgres:17. Phiên bản PostgreSQL thực tế được ghi trong docs/tv2_verification.json để tránh suy diễn từ tag image.

Các file chính gồm config.py, database.py, models.py, schemas.py, dependencies.py, student_service.py, main.py và init_db.py. scripts/demo_client.py chuẩn bị dữ liệu H5; tests/test_api.py kiểm tra hợp đồng API. requirements.txt và tests/conftest.py dùng nguyên bản TV3 tại commit 3edd89b; TV3 tiếp tục quản lý dependencies và fixture chung.

### 4.2. Cấu hình và kết nối DB

Settings đọc .env UTF-8 và biến môi trường, ưu tiên biến môi trường của tiến trình. get_settings có cache để tránh đọc lại cấu hình theo mỗi request. get_crypto lấy khóa qua decode_key và tạo CryptoService dùng chung. DB engine bật pool_pre_ping; SessionLocal không autoflush và không expire sau commit.

get_db cấp Session theo request và đóng khi xử lý xong. Khi POST gặp lỗi toàn vẹn DB, chương trình rollback trước khi truy vấn lại để phân biệt trùng mã do tranh chấp với lỗi ràng buộc khác. SQLAlchemy yêu cầu rollback sau lỗi flush để tiếp tục sử dụng Session [2]. Lỗi mật mã IntegrityFailure được xử lý riêng, không nhầm với IntegrityError của DB.

### 4.3. Triển khai module API

Pydantic định nghĩa StudentUpdate làm nền cho StudentPayload và StudentOut. StudentUpdate không có student_id, đồng thời cấm trường thừa nên PUT kèm ID bị từ chối. Route dùng dependency require_admin hoặc require_reader của TV1; phần TV2 không sao chép thuật toán kiểm tra token.

student_service là điểm duy nhất ánh xạ ba trường nhạy cảm sang H1. EncryptedValue được dựng theo đúng thứ tự ciphertext, nonce, key_version. Response model chỉ công khai các field của StudentOut, không gửi cấu hình, key, token, nonce hoặc ciphertext về client.

DELETE trả Response(status_code=204) tường minh để không sinh JSON null. GET danh sách sắp xếp theo student_id để kết quả có thứ tự xác định và gom ID lỗi trước khi trả 409. Không log payload hoặc token trong code API.

### 4.4. Docker và dữ liệu bền vững

Dockerfile cài dependencies rồi chép thư mục app. Khi khởi động, tiến trình chạy init_db để tạo bảng còn thiếu, sau đó exec Uvicorn. Compose tạo PostgreSQL trước; API phụ thuộc điều kiện service_healthy của DB. Healthcheck DB dùng pg_isready, healthcheck API gọi /health. Compose hỗ trợ chờ trạng thái khỏe qua depends_on và healthcheck [3].

Volume pgdata lưu dữ liệu PostgreSQL qua các lần dừng/tạo lại container. Lệnh docker compose down giữ volume; việc xóa volume không phải bước kiểm thử thường lệ. Mật khẩu trong .env phải phù hợp với volume đã khởi tạo. Khóa không được chép vào image; .dockerignore loại .env và Dockerfile chỉ chép app cùng manifest dependencies.

### 4.5. Module mật mã và xác thực — tích hợp phần TV1

Module sử dụng AES-256-GCM: khóa 32 byte, nonce 12 byte, ciphertext kèm tag 16 byte, AAD theo định dạng student:<id>|field:<field>|key:<version>. Tài liệu cryptography mô tả AESGCM giải mã thất bại khi ciphertext, key, nonce hoặc associated data sai; nonce không được tái sử dụng với cùng khóa [4].

PR #2 của TV1 đã thay bản tạm bằng AESGCM; PR #4 bổ sung tài liệu thiết kế và test replay. Bản sửa issue #6 đã được ghép vào nhánh tích hợp local: plaintext xác thực đúng nhưng không phải UTF-8 cũng chuyển thành IntegrityFailure. encrypt sinh nonce bằng os.urandom(12), mã hóa UTF-8 với AAD và trả EncryptedValue. decrypt kiểm key_version, độ dài nonce, dựng lại AAD rồi chuẩn hóa InvalidTag/UnicodeDecodeError thành IntegrityFailure để API trả 409. TV2 giữ nguyên interface và không sửa thuật toán của TV1.

AAD ràng buộc ciphertext với hàng, cột và phiên bản khóa; không chặn được việc chép lại ciphertext cũ của cùng ô. Test C07 ghi nhận giới hạn replay này. Nonce là ngẫu nhiên chứ không phải bộ đếm đảm bảo duy nhất; demo chưa có cơ chế đếm lần mã hóa hoặc xoay khóa. Chi tiết quản lý khóa và giới hạn được TV1 trình bày trong docs/crypto_design.md.

Xác thực dùng hai token tĩnh, HTTPBearer(auto_error=False) và secrets.compare_digest trên bytes. Token viewer được đọc nhưng không ghi; thiếu hoặc sai token trả 401. Khóa/token nằm trong .env, không nằm trong bảng students; lộ khóa, máy ứng dụng bị chiếm và replay cùng hàng nằm ngoài phạm vi bảo vệ. TV1 review nội dung này khi ghép báo cáo chung.

### 4.6. Kiểm thử và bằng chứng hiện có

Lần chạy tích hợp ngày 16/11/2026: 102 passed, không xfail/skip. Toàn bộ test chờ API của TV3 đã bỏ marker; thêm test công cụ kết luận attack lab và bản sửa UTF-8. Kết quả cũ 73 passed / 3 xfailed của bản crypto tạm không còn mô tả bản hiện tại. Đây là kết quả local; CI của PR tích hợp phải chạy riêng trên commit sẽ merge.

Bộ test API kiểm CRUD, bản ghi trùng, ID/độ dài dữ liệu sai, JSON lỗi, lỗi danh sách nhiều hồ sơ hỏng và lưu đúng đầu ra H1 cho cả POST/PUT. Test quyền từng route và nonce mới đặt trong test_security của TV3. Fixture SQLite cô lập DB từng test và override get_db. Kết quả này được phân biệt với kiểm thử end-to-end trên PostgreSQL.

Docker được build từ nguồn tích hợp, dùng cấu hình/khóa, cổng và volume thử nghiệm riêng. scripts/verify_tv2.py đạt 19/19 điều kiện, exit 0: schema BYTEA, CRUD/quyền/mã lỗi, không thấy plaintext trong ciphertext, tag 16 byte, nonce 12 byte, key_version và nonce mới sau PUT. File docs/tv2_verification.json ghi phiên bản PostgreSQL thực tế và thời điểm UTC. Smoke check chỉ kiểm các điều kiện đó, không phải chứng minh an toàn mật mã tổng quát.

Attack lab ngày 16/11 đạt A1=401, A2=403 và DB/payload nguyên, A3=True trên cả ba field, A4/A5=409 đúng `integrity_failure` và restore từng hàng/payload. Benchmark ngày 15/11 chạy đủ 100/1.000/10.000 bản ghi; sáu hàng số đo, biểu đồ và thảo luận nhiễu đã đưa vào Chương 5, CSV gốc không commit. Không dùng các lần chạy này để kết luận hệ thống production đã được kiểm toán.

### 4.7. Quy trình Git và bàn giao

Nhánh integration/tv2-merge-prep được tạo từ feature/api-db tại 0017e18, ghép origin/main tại 692337a và feature/security-benchmark tại 3edd89b. Hai xung đột dependencies/fixture được giải quyết bằng bản TV3. Nhánh nguồn của bạn và các nhánh GitHub được giữ nguyên trong lần chuẩn bị này. Nội dung PR và thứ tự merge nằm trong docs/TV2_PR_DRAFT.md và docs/TV2_MERGE_READINESS.md.

Issue #3 đã ghi nhận TV2 đồng ý H1 nhưng H2–H5 chưa đầy đủ; TV2 có bản nội dung chuẩn bị để nhóm xác nhận. PR #5 của TV3 và PR #7 của TV1 đang mở; code #7 đã ghép local nhưng chưa merge remote. Cần review, CI trên commit tích hợp và merge trên GitHub trước khi gọi là hoàn tất bàn giao. TV1/TV3 cần xác nhận nội dung Chương 1–2/5–6 đã chuẩn bị; TV2 điền thông tin cá nhân, luyện demo 3 phút và tổng duyệt cùng nhóm 12 phút.

## Tài liệu tham khảo

[1] PostgreSQL 17, Binary Data Types: https://www.postgresql.org/docs/17/datatype-binary.html

[2] SQLAlchemy 2.0, Session Basics: https://docs.sqlalchemy.org/en/20/orm/session_basics.html

[3] Docker Compose, Control startup and shutdown order: https://docs.docker.com/compose/how-tos/startup-order/

[4] cryptography, Authenticated encryption — AESGCM: https://cryptography.io/en/stable/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM

Các nguồn được đối chiếu ngày 14/11/2026. Hai tài liệu kế hoạch nhóm do người dùng cung cấp là nguồn yêu cầu và phân công nội bộ.
