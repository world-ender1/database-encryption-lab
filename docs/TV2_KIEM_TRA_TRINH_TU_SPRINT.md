# Ghi chú về bản lưu lịch sử

Tài liệu bên dưới ghi nhận lần kiểm tra ngày 14/11/2026, trước khi fetch các cập nhật GitHub. Trạng thái hiện tại ngày 15/11/2026 nằm trong [TV2_MERGE_READINESS.md](TV2_MERGE_READINESS.md). AES-GCM đã merge trên main, TV3 đã có PR #5 và bản ghép local đã được chuẩn bị. Không áp dụng lại đề xuất hạ CRUD về 501 hoặc dựng lại Sprint 0 trong bản lưu này; giữ nguyên lịch sử Git và hoàn tất các điều kiện nghiệm thu còn thiếu trên bản tích hợp.

---

# Kiểm tra lại trình tự Sprint — TV2

Ngày 14/11/2026. Đối chiếu phần 3 của `g:/transfer C D/cho downloads/Ke_hoach_thuc_hien_TV2.md` với working tree và các Git ref đang có tại máy. Chưa fetch hoặc xác minh trạng thái PR/CI hiện thời trên GitHub trong lần kiểm tra này.

## Kết luận

**Chưa làm đúng trình tự Sprint.** Lần triển khai trước đã viết trước phần chức năng tuần 1–2 và tài liệu tuần 3–4 trên `feature/api-db`, khi chưa xác nhận các điều kiện hoàn thành bước 1 và bước 9. Kết quả test/API local không thay thế các điều kiện này.

Quy định trong kế hoạch: “Làm lần lượt từ Bước 1 đến Bước 23. Mỗi bước có điều kiện ‘Xong khi’; chưa đạt thì chưa sang bước sau.” Người dùng đã xác nhận phải tuân thủ trình tự này. Từ đây, phần đã viết trước chỉ được coi là bản chuẩn bị, chưa phải các Sprint đã được nghiệm thu.

## Bằng chứng Git

- `origin/main` và `main` tại máy: `4592eac`, merge PR #1 từ `sprint0/skeleton`.
- Tree của commit đó có module crypto/auth/key_manager, init_env và test TV1; **không có** main.py, config.py, database.py, models.py, schemas.py, dependencies.py, init_db.py, Dockerfile, compose.yaml, requirements.txt, tests/conftest.py hoặc workflow CI.
- Vì vậy có commit mang tên merge Sprint 0, nhưng nội dung tại mốc này chưa đáp ứng “trên main, docker compose up cho /health = 200”. Không được đánh dấu bước 9 xong chỉ dựa vào tên PR.
- HEAD `feature/api-db` và ref `origin/feature/api-db` tại máy: `90e613f`, nội dung commit chỉ thêm requirements.txt. Đây là cập nhật đã có sau lần triển khai trước; không sửa/xóa commit này trong lượt kiểm tra.
- Các file TV2 được tạo trước đó vẫn là untracked, chưa nằm trong commit `90e613f`.

## Đối chiếu đủ 23 bước

“Đã có code” dưới đây là trạng thái chuẩn bị local, không phải xác nhận đã đi qua các mốc theo đúng thứ tự.

| Bước | Yêu cầu | Kết quả đối chiếu |
|---|---|---|
| 1 | Cả nhóm chốt H1–H5 | Đã đọc/đối chiếu, chưa có bằng chứng cả ba đồng ý. Chưa xác nhận xong. |
| 2 | Làm Sprint 0 trên sprint0/skeleton | Repo có sẵn nhưng tôi đã tạo feature/api-db để triển khai. Lệch nhánh của giai đoạn đầu. |
| 3 | __init__.py, config.py | Đã viết theo H4; chưa bàn giao trong commit Sprint 0. |
| 4 | database.py, models.py | Đã viết đúng tên bảng/cột H3; chưa bàn giao trong commit Sprint 0. |
| 5 | schemas.py | Đã viết POST/PUT/Out, cấm trường thừa, kiểm tra ID; chưa bàn giao Sprint 0. |
| 6 | dependencies.py | Đã gọi decode_key/CryptoService; chưa bàn giao Sprint 0. |
| 7 | main.py khung: /health 200, CRUD 501, gắn auth | Hiện main.py là CRUD hoàn chỉnh. Chưa có bản khung 501 được bàn giao riêng. |
| 8 | init_db.py, Dockerfile, compose.yaml | Đã viết/chạy local, nhưng với CRUD đầy đủ; chưa có nghiệm thu riêng của bản khung. |
| 9 | Push nhánh chung, review/merge PR, main chạy /health | PR #1 có trong lịch sử nhưng thiếu phần TV2/TV3. Main tại ref đã kiểm tra không có Compose/API. Chưa đạt. |
| 10 | Tạo feature/api-db từ main đã đạt Sprint 0; student_service | Đã có code nhưng tạo nhánh khi main chưa đủ khung. Làm sớm. |
| 11 | POST/GET một hồ sơ, lỗi; thao tác qua Swagger | API đã được kiểm tra bằng client tự động. Chưa có bằng chứng demo Swagger trực tiếp; làm trước gate Sprint 0. |
| 12 | GET danh sách và 409 toàn bộ khi hỏng | Đã viết/kiểm thử local, chưa đóng bước theo tiến trình. |
| 13 | Review PR crypto TV1 | Có ghi chú source local; chưa có review/approve PR thực tế. Chưa đạt. |
| 14 | PUT/DELETE | Đã viết/kiểm thử trước khi hoàn thành bước 13. |
| 15 | demo_client SV9001/SV9002 | Đã chạy local, là công việc làm trước mốc. |
| 16 | test_api dùng fixture TV3; không chứa test quyền/tamper | Test đạt nhưng phạm vi lệch: có test quyền/tamper; tự tạo conftest và thêm db_session. Cần tách bàn giao đúng người phụ trách. |
| 17 | api_db.md | Có tài liệu, nhưng trạng thái tiến độ cần sửa theo audit này. |
| 18 | PR api-db merge; review PR TV3 | Chưa có bằng chứng. Commit requirements không phải PR/commit toàn bộ API. |
| 19 | PostgreSQL sau khi có AES-GCM thật | Đã thử với bản crypto tạm, không đáp ứng điều kiện bước 19. Plaintext vẫn còn. |
| 20 | Sửa issue bằng PR nhỏ | Chưa có issue thực tế để đối chiếu; không coi là đã hoàn thành. |
| 21 | Nháp Chương 3–4, ghép phần TV1, gửi TV1 | Có bản nháp làm trước; chưa ghép/gửi theo quy trình. |
| 22 | Slide và demo Swagger/psql | Có slide/lời dẫn làm trước; chưa xác nhận trình diễn theo yêu cầu. |
| 23 | Luyện 3 phút, tổng duyệt nhóm 12 phút | Chưa thực hiện. |

## Sai lệch cần khắc phục

1. **Trình tự:** quay lại xác nhận bước 1 và hoàn tất gói Sprint 0 trước khi bàn giao CRUD. Không đánh dấu các tuần sau đã hoàn thành dựa trên sản phẩm chuẩn bị trước.
2. **File của TV3:** requirements.txt, conftest.py là phần hỗ trợ đã tạo vượt phân công. TV3 cần nhận/kiểm tra phần này và bổ sung CI, tests/__init__.py, scripts/__init__.py. Không đưa các file này vào commit mang tên phần việc riêng của TV2 mà chưa thống nhất.
3. **Test bước 16:** các test `test_every_route_requires_token`, `test_viewer_can_read_but_cannot_write`, `test_failed_decryption_blocks_entire_list_and_allows_delete`, `test_demo_client_fails_when_reset_is_denied` chứa kiểm tra quyền/tamper. Cần bàn giao nội dung phù hợp cho TV3; không tự ghi đè test_security.py của họ. Test PUT nonce mới dùng thêm fixture db_session cũng cần thống nhất với TV3 hoặc dùng cách kiểm tra không mở rộng H5.
4. **Lời khuyên tên nhánh/commit:** feature/api-db phù hợp từ bước 10, không phải nhánh bàn giao đầu tiên của TV2. Lời khuyên trước đó thiếu điều kiện Sprint 0 và cần được thay bằng hướng dẫn dưới đây.

## Trình tự bàn giao đúng từ trạng thái hiện tại

### A. Đóng Sprint 0 trước

- Xác nhận với TV1/TV3 rằng H1–H5 đã chốt (bước 1); xác nhận tài liệu dùng làm chuẩn nếu khác bản v3 người dùng cung cấp.
- Bảo toàn code CRUD đã viết ở trạng thái riêng trước khi chuẩn bị bản khung. Không reset/force-push nhánh hiện tại vì đã có commit requirements và ref remote.
- Chuẩn bị phần TV2 trên `sprint0/skeleton` từ trạng thái đã đồng bộ với nhóm. Bản main.py của Sprint 0 chỉ có /health và CRUD 501 gắn auth như bước 7.
- File TV2 bàn giao: app/__init__.py, config.py, database.py, models.py, schemas.py, dependencies.py, main.py, init_db.py, Dockerfile, compose.yaml. Nếu bổ sung .dockerignore thì ghi rõ vào mô tả phạm vi.
- TV3 cung cấp dependencies/fixture/CI. Kiểm tra bản khung độc lập: config đọc được v1, Docker lên, /health 200, thiếu/sai token 401, viewer ghi 403, token có quyền gọi CRUD nhận 501.
- Commit phần TV2: `chore(api): sprint 0 skeleton - config, schema, docker`.
- Do PR #1 đã merge khi thiếu phần TV2/TV3, TV3 cần điều phối một PR bổ sung Sprint 0 vào main. Không viết lại lịch sử PR #1 để giả lập đã làm đúng từ đầu.
- Chỉ khi main đủ phần ba người, kiểm tra đạt và PR bổ sung được review/merge mới đóng bước 9.

### B. Tuần 1, rồi tuần 2

- Đồng bộ main đã đủ Sprint 0; giữ lịch sử feature/api-db đã có và tích hợp main theo quy trình nhóm, không chạy lại lệnh tạo nhánh cùng tên hoặc force-push tùy tiện.
- Đưa lại student_service, POST/GET và lỗi theo bước 10–12; làm review PR crypto ở bước 13.
- Sau đó bàn giao PUT/DELETE, demo_client, test_api đúng phạm vi và api_db theo bước 14–17.
- Bước 18 mới dùng commit `feat(api): persist encrypted students and expose role-protected CRUD` và PR feature/api-db. Không gộp bản nháp báo cáo/slide vào commit khung Sprint 0.
- Không phải chờ AES-GCM thật để viết API; bản crypto tạm được kế hoạch cho phép trong Sprint 0 và tuần 1–2. Điều kiện chờ ở đây là hoàn thành mốc trước, không phải thay đổi thiết kế của kế hoạch.

### C. Tuần 3–4

- Sau khi có AES-GCM thật và tích hợp, thực hiện lại bước 19; kết quả test crypto tạm không thay thế nghiệm thu này.
- Xử lý issue, hoàn thiện/ghép báo cáo, demo và tổng duyệt lần lượt bước 20–23. Các tài liệu đang có là bản nháp để tái sử dụng.

## Phạm vi của lần kiểm tra này

Đã đọc kế hoạch, kiểm tra lịch sử/tree Git và phạm vi test, tạo audit và sửa tài liệu trạng thái. Không thay mã ứng dụng, không chuyển nhánh, không reset/rebase/commit/push, không đổi dữ liệu DB. Không chạy lại pytest vì lượt này chỉ kiểm tra quy trình và cập nhật tài liệu. Kết quả 73 passed / 3 xfailed là từ lần triển khai trước, không phải kết quả nghiệm thu Sprint 0 mới.
