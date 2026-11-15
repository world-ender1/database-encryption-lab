# TV2 — Trạng thái công việc sau tích hợp

Cập nhật 15/11/2026. Nguồn hiện tại: [báo cáo kiểm tra nhánh và nghiệm thu](TV2_MERGE_READINESS.md). Các ghi chú ngày 14/11 về việc còn chờ crypto/TV3 đã được thay thế bằng trạng thái này.

Đối chiếu toàn bộ kế hoạch mới nhất: [bảng cả nhóm và phương án xử lý](DOI_CHIEU_KE_HOACH_CA_NHOM.md). Còn test gây tamper trong test_api cần bàn giao TV3 hoặc đổi thành dependency giả; phần sửa test_security local cần TV3 tiếp nhận. Attack lab cần siết tiêu chí tự kiểm trước khi đóng nghiệm thu cuối.

## Phần kỹ thuật đã chuẩn bị

- Config, DB/model, schema, mapping H1, CRUD H2, lỗi 404/409/422, Docker và demo client đầy đủ.
- Lấy AES-GCM thật từ main; tích hợp source TV3 trên nhánh local `integration/tv2-merge-prep`.
- Giải quyết hai xung đột bằng dependencies/fixture của TV3. Bỏ WAIT_API; chuyển test quyền từng route sang test_security; bỏ test nonce trùng TV3.
- Bổ sung `test_sensitive_columns_store_only_crypto_output` cho POST/PUT theo Definition of Done TV2. Giữ test lỗi toàn danh sách và xóa hồ sơ hỏng để kiểm H2.
- Pytest: 91 passed, không xfail/skip; PostgreSQL: 19/19 điều kiện đạt; attack lab và benchmark chạy thành công.
- Cập nhật Chương 3–4, Word/PPTX, kịch bản demo; có [hợp đồng TV2](TV2_HOP_DONG_ISSUE_3.md), [PR draft](TV2_PR_DRAFT.md), [ghi chú review](TV2_REVIEW_GHI_CHU.md).

## Đối chiếu 23 bước

| Bước | Trạng thái |
|---|---|
| 1 | TV2 đã đồng ý H1; H2–H5 có bản chuẩn bị, còn xác nhận nhóm ở issue #3 |
| 2 | Repo/nhánh đã có; giữ nguyên lịch sử Sprint 0 |
| 3–8 | Đủ code; CRUD hoàn chỉnh, không hạ về khung 501 |
| 9 | Nghiệm thu bản ghép local đạt; main GitHub chưa có API/DB |
| 10–12 | Student service, POST/GET đã có test |
| 13 | Đã xác minh GitHub: TV2 hvlchv APPROVED PR #2/#4; cả hai đã merge |
| 14–17 | PUT/DELETE, demo client, test API, api_db.md đã chuẩn bị |
| 18 | Bản ghép/PR draft sẵn sàng; còn push, PR, reviewer và CI trên commit sẽ merge |
| 19 | PostgreSQL thật đạt, có tv2_verification.json |
| 20 | Bộ tích hợp TV3 đạt; chưa thấy lỗi CRUD trong phạm vi kiểm tra |
| 21 | Chương 3–4 cập nhật theo source TV1; chờ tên/MSSV và ghép chung |
| 22 | Slide/kịch bản 3 phút cập nhật; cần thao tác/chụp ảnh trên máy demo |
| 23 | Bạn luyện 3 phút; cả nhóm tổng duyệt 12 phút |

## Việc còn lại

1. Hoàn tất issue #3: đưa nội dung H2–H5 đã chuẩn bị lên issue, để TV1/TV3 xác nhận. Chưa đăng thay bạn.
2. Review PR #5 và giải quyết trạng thái GitHub blocked; chưa có review tại lần kiểm tra.
3. Làm theo thứ tự trong TV2_MERGE_READINESS; reviewer TV3 xem thay đổi test_security.
4. CI chạy trên đúng commit sẽ merge, rồi nghiệm thu lại main. Kết quả local không thay CI/review.
5. TV3 hoàn thiện Chương 5, biểu đồ/diễn giải benchmark, kiểm máy sạch và release. CSV trong evidence là số đo tham khảo.
6. Điền tên/MSSV, ghép báo cáo/slide với TV1; luyện demo và tổng duyệt.

Không cần dựng lại lịch sử Sprint 0 hoặc viết lại crypto. Không reset dữ liệu hiện có để hoàn tất các việc trên; chỉ reset SV9001/SV9002 khi đó là dữ liệu demo được phép thay.
