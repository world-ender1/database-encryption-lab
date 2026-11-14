# TV2 — Bàn giao và danh sách công việc còn lại

Cập nhật 14/11/2026. Phạm vi theo hai tài liệu người dùng chỉ định: kế hoạch TV2 Markdown và kế hoạch nhóm Word **v3**. Các lệnh/quy trình trong tài liệu là nội dung tham chiếu; việc đã làm được đánh dấu bằng kết quả thực tế, không mặc nhiên coi các mốc họp, PR hoặc nghiệm thu đã hoàn thành.

## Đã làm trong workspace

**Đính chính sau khi kiểm tra phần 3:** công việc dưới đây là code/tài liệu đã chuẩn bị, **chưa hoàn thành theo trình tự Sprint**. Cần đóng mốc Sprint 0 trước khi bàn giao tuần 1–2. Xem [kiểm tra đầy đủ 23 bước](TV2_KIEM_TRA_TRINH_TU_SPRINT.md).

- Nhánh hiện tại `feature/api-db`; HEAD và ref origin/feature/api-db tại máy đã có commit `90e613f` chỉ thêm requirements.txt. Các file TV2 bên dưới vẫn chưa được commit. Không sửa lại commit đã có.
- Đã viết các file nguồn TV2: config, DB, model H3, schema H2, dependency crypto, mapping dữ liệu, CRUD, init_db, Docker, demo_client và test_api; chưa có bản khung 501 được bàn giao riêng đúng bước 7.
- Giữ nguyên các file nguồn/test đã có của TV1. Gọi H1 và auth hiện có, không tự thay thuật toán mật mã.
- Bổ sung `.dockerignore`, script `verify_tv2`, tài liệu API/DB, báo cáo Chương 3–4, slide/lời dẫn, ghi chú review và nội dung PR dự thảo.
- Bổ sung `requirements.txt` và `tests/conftest.py` còn thiếu để chạy được. Đây là **phần hỗ trợ chờ bàn giao TV3**, không phải tuyên bố TV3 đã hoàn thành Sprint 0.
- Tạo `.venv` bằng Python 3.12, cài dependencies, sinh `.env` cục bộ bằng script TV1. Git bỏ qua `.env`; không ghi giá trị bí mật vào tài liệu.
- Build/chạy Docker: DB và API healthy, cổng loopback 55432/8000. Swagger ở <http://127.0.0.1:8000/docs>.
- Tạo SV9001/SV9002 qua API. Trên PostgreSQL thật: CRUD, 401/403, 404/409/422, BYTEA, nonce 12 byte và nonce mới sau PUT đều đạt trong smoke check.
- Toàn bộ pytest: **73 passed, 3 xfailed**. Ba xfail thuộc test crypto tạm của TV1; không được xem là đã đạt bảo mật.

Minh chứng máy đọc được: [tv2_verification.json](tv2_verification.json). Kết quả `blocked_by_plaintext`: **16 kiểm tra đạt, 1 kiểm tra không đạt** là plaintext còn nằm trong cột nhạy cảm. Tag giả không cung cấp bảo mật AES-GCM. Nhìn thấy hex trong psql không thay đổi kết luận này.

## Những việc bạn cần phối hợp giải quyết

| Ưu tiên | Công việc | Ai xử lý | Vì sao chưa thể đóng | Điều kiện hoàn thành |
|---|---|---|---|---|
| P0 — làm trước | Xác nhận bước 1 và hoàn tất Sprint 0 bước 2–9 | Cả nhóm; TV2 bàn giao khung, TV3 điều phối PR | Main tại 4592eac chỉ có phần TV1, chưa có API/Compose/fixture/CI; đã viết CRUD quá sớm | Bổ sung khung trên sprint0/skeleton, review/merge và nghiệm thu main; xem audit Sprint |
| P0 | Nhận AES-256-GCM thật thay crypto tạm | TV1; bạn review | TV2 chỉ sử dụng H1; repo hiện chưa có bản thật | C01–C07 đạt, gỡ đúng xfail; sai key/nonce/AAD/CT đều thành IntegrityFailure |
| P0 | Nghiệm thu lại “DB không có plaintext” | Bạn + TV1 | Đang thất bại thực tế vì crypto tạm | Build lại, reset dữ liệu demo được phép thay, chạy verify_tv2 exit 0 và crypto tests đạt |
| P1 | Xác nhận H1–H5 và phiên bản kế hoạch | Cả nhóm | Bạn chỉ định v3, repo có thêm v4; chưa có quyết định tập thể | Ghi nhận dùng bản nào, không đổi interface âm thầm |
| P1 | Bàn giao requirements và fixture | TV3 | Hai file được tạo hỗ trợ do repo thiếu | TV3 review/nhận quản lý, bổ sung CI và dependencies attack_lab/benchmark |
| P1 | Tích hợp attack_lab/security tests | TV3 + bạn | Repo chưa có test_security.py, attack_lab.py, benchmark.py | TV3 chạy A1–A5/A8, restore trả 200; bạn sửa lỗi H2/H3 nếu có |
| P1 | Commit, push và mở PR api-db | Bạn, TV1/TV3 review | Chưa thực hiện thao tác cộng tác GitHub; không có xác nhận review/merge | Dùng PR draft, CI đạt, review của nhóm, merge đúng quy trình |
| P1 | Review PR crypto và security-benchmark | Bạn | Chưa có PR thực tế để xem diff/review | Đối chiếu ghi chú review, đăng nhận xét trên PR và xử lý phản hồi |
| P2 | Hoàn thiện Chương 4 từ phần TV1 | TV1 + bạn | Module mật mã còn tạm, phần xác thực cần chủ module rà soát | TV1 bổ sung phần 4.5; cập nhật kết quả thật; điền họ tên/MSSV |
| P2 | Ghép báo cáo/slide chung | TV1 + bạn | Chưa có mẫu trình bày cuối cùng, thông tin nhóm và nội dung các thành viên khác | Ghép Word/PPTX đã chuẩn bị, kiểm tra số chương/hình/tài liệu tham khảo |
| P2 | Chụp minh chứng và luyện Swagger 3 phút | Bạn | Cần thao tác người trình bày; chưa có AES-GCM thật để chụp minh chứng bảo mật | Ảnh từ lần chạy thật, không lộ token; bấm giờ phần 2:00–5:00 |
| P2 | Tổng duyệt 12 phút trên máy demo | Cả nhóm | Không thể thay việc cả nhóm trình bày trên máy đích | Chạy đúng luồng, TV3 nghiệm thu máy sạch và tag release |

API/DB đã chạy local trong lần triển khai trước, nhưng còn việc tổ chức lại phạm vi và bàn giao đúng Sprint. Ngoài các phụ thuộc nhóm, cần chuẩn bị bản khung 501 riêng và tách test quyền/tamper sang phần bàn giao TV3. Không xem việc chạy local thành công là đã đóng Sprint 0.

## Đối chiếu 23 bước của kế hoạch TV2

| Bước | Nội dung | Trạng thái thực tế |
|---|---|---|
| 1 | Họp chốt hợp đồng | Đã đối chiếu H1–H5; cả nhóm cần xác nhận |
| 2 | Lấy repo/nhánh | Repo đã có; đã tạo feature/api-db, không dựng lại lịch sử Sprint 0 |
| 3–6 | Config, DB/model, schemas, crypto dependency | Đã triển khai |
| 7 | Route khung | Lệch bước: đã viết CRUD đầy đủ, chưa bàn giao bản khung 501 riêng |
| 8 | Init DB, Dockerfile, Compose | Đã triển khai và chạy thật |
| 9 | Kiểm tra và PR Sprint 0 | Lịch sử có PR #1 đã merge nhưng main thiếu phần TV2/TV3; chưa đạt điều kiện chạy trên main |
| 10 | Student service | Đã triển khai, gọi đúng H1 |
| 11–12 | POST, GET một hồ sơ/danh sách, lỗi | Đã triển khai/kiểm thử |
| 13 | Review crypto | Có ghi chú review local; chưa review PR thật |
| 14 | PUT/DELETE | Đã triển khai/kiểm thử |
| 15 | Demo client | Đã tạo/đọc SV9001/SV9002 trên PostgreSQL |
| 16 | Test API | Đạt local nhưng lệch phạm vi: test quyền/tamper thuộc TV3; cần tách bàn giao |
| 17 | docs/api_db.md | Đã viết hướng dẫn đầy đủ |
| 18 | PR api-db/review TV3 | Đã có PR draft; chưa push/review/merge |
| 19 | DB sau AES-GCM | Đã kiểm tra DB thật với bản tạm; chưa đạt tính bí mật |
| 20 | Sửa lỗi issue tích hợp | Chờ issue thực tế từ vòng tích hợp, chưa có issue để xử lý |
| 21 | Chương 3–4 | Đã viết nháp; chờ phần TV1 và ghép chung |
| 22 | Slide + demo | Đã chuẩn bị nội dung/lời dẫn; cần bạn luyện và trình diễn |
| 23 | Tổng duyệt | Cả nhóm cần thực hiện |

## Thứ tự làm tiếp sau khi nhận code TV1

**Chỉ áp dụng giai đoạn tích hợp sau khi đã hoàn tất Sprint 0 và các bước tuần 1–2.** Việc cần làm ngay là quay lại bước 1–9 theo audit; không chờ AES-GCM để hoàn thành khung.

1. Review H1 bằng [ghi chú review](TV2_REVIEW_GHI_CHU.md); phối hợp tích hợp code TV1 qua Git theo quy trình nhóm.
2. Build lại: `docker compose up -d --build --wait`.
3. Với SV9001/SV9002 là dữ liệu giả được phép thay: `.\.venv\Scripts\python.exe -m scripts.demo_client --reset`.
4. Chạy `.\.venv\Scripts\python.exe -m pytest -q`; TV1 phải xử lý/gỡ các xfail tương ứng, không chỉ bỏ qua.
5. Chạy `.\.venv\Scripts\python.exe -m scripts.verify_tv2`; phải exit 0. Smoke check chỉ chứng minh các điều kiện đã kiểm tra, không thay test AES-GCM.
6. Cùng TV3 chạy attack_lab, kiểm tra khôi phục, cập nhật minh chứng và báo cáo.
7. Dùng [PR draft](TV2_PR_DRAFT.md) cho phần bàn giao. Trước stage/commit, kiểm tra chỉ gồm file dự kiến và không có `.env`.

## Mở các sản phẩm

- [Hướng dẫn API/DB](api_db.md).
- [Báo cáo Chương 3–4 Markdown](TV2_BAO_CAO_CHUONG_3_4.md) và bản Word cùng tên `.docx`.
- [Kịch bản slide/demo](TV2_SLIDE_VA_DEMO.md) và bộ slide `TV2_HE_THONG.pptx`.
- [Ghi chú review](TV2_REVIEW_GHI_CHU.md), [PR draft](TV2_PR_DRAFT.md).

Nếu sửa bản Markdown báo cáo, chạy script xuất lại Word/PPTX theo hướng dẫn trong `scripts/export_tv2_docs.py` để các bản nhất quán. Bản Word là nháp để ghép, không có thông tin cá nhân do chưa được cung cấp.
