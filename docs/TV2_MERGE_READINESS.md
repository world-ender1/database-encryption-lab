# Kiểm tra nhánh và chuẩn bị merge — TV2

Ngày kiểm tra: 15/11/2026 (Asia/Saigon). Repo: [world-ender1/database-encryption-lab](https://github.com/world-ender1/database-encryption-lab).

**Kết luận:** code ba thành viên đã đủ để chạy tích hợp và đã vượt qua các kiểm tra bên dưới. Phần kỹ thuật TV2 đã chuẩn bị trên nhánh local `integration/tv2-merge-prep`. Toàn bộ đồ án chưa thể đánh dấu hoàn tất: còn xác nhận hợp đồng, review/merge/CI trên GitHub, báo cáo chung và tổng duyệt.

## Các nhánh GitHub đã kiểm tra

| Nhánh | Commit | Kết quả |
|---|---|---|
| `main` | `692337a61f02a58dafb485be52d80ae2856557de` | Đã merge crypto và tài liệu TV1; chưa có API/DB TV2 |
| `feature/api-db` (bạn) | `0017e18b652a28f3025072cb0dec622ae9e8e39a` | CRUD/DB/Docker và tài liệu có sẵn; base còn crypto tạm, thiếu nghiệm thu với TV1/TV3 |
| `feature/crypto` | `2cfefa59d85a49e3b47daedf4f8a9852221a9e67` | AES-GCM thật; [PR #2](https://github.com/world-ender1/database-encryption-lab/pull/2) đã merge |
| `feature/crypto-docs` | `f7cf3a3d754772f83698c53bdee198603403b98c` | Thiết kế/giới hạn/test replay; [PR #4](https://github.com/world-ender1/database-encryption-lab/pull/4) đã merge |
| `feature/security-benchmark` | `3edd89bcbaba3b6adf93374b77cd30a0c0854030` | Có CI, fixture, test_security, attack_lab, benchmark, threat model và demo script; [PR #5](https://github.com/world-ender1/database-encryption-lab/pull/5) còn mở |
| `sprint0/skeleton` | `08a20eaddcb148a6eb7c252fd383b62106456272` | Mốc lịch sử; không dựng lại hoặc force-push |

Đã đọc refs bằng Git và PR/issue/check-runs bằng GitHub API có xác thực. PR #5 có check `pytest: success`, `mergeable=true`, `mergeable_state=blocked`, chưa có review. Không suy đoán lý do blocked: endpoint branch protection trả 404 nên chưa xác nhận được quy tắc; cần xem yêu cầu trên giao diện repo. Không có check-runs trên commit main nêu trên.

[Issue #3](https://github.com/world-ender1/database-encryption-lab/issues/3) đã ghi nhận TV2 đồng ý H1. H2–H5 vẫn thiếu nội dung và xác nhận đầy đủ. Bản [TV2_HOP_DONG_ISSUE_3.md](TV2_HOP_DONG_ISSUE_3.md) đã chuẩn bị phần của bạn; chưa đăng lên issue.

## Những việc đã hoàn thiện local

1. Tạo nhánh tích hợp từ `feature/api-db`, merge `origin/main`, rồi merge nhánh TV3. Giữ nguyên nhánh nguồn của bạn và tất cả nhánh GitHub.
2. Giải quyết hai xung đột add/add ở `requirements.txt` và `tests/conftest.py` bằng nguyên bản TV3. Giữ `python-dotenv` trực tiếp và fixture import app trong hàm.
3. Bỏ `WAIT_API`/xfail của TV3 sau khi chạy toàn bộ suite bằng `--runxfail` đạt. Test bảo mật giờ thất bại thật nếu có regression.
4. Thêm test bắt buộc của TV2: `test_sensitive_columns_store_only_crypto_output`, kiểm POST/PUT lưu chính xác đầu ra H1 vào H3 và truyền đúng ID/field. Chuyển sáu ca kiểm quyền route sang test_security; bỏ một test nonce trùng với TV3. Giữ hợp đồng lỗi danh sách nhiều hồ sơ hỏng ở test_api.
5. Bổ sung kiểm tra tag 16 byte và key_version vào smoke PostgreSQL. Cập nhật báo cáo Chương 3–4, Word/PPTX, kịch bản demo, PR draft và checklist cũ theo kết quả thật.

Các thay đổi trong test_security là phần chuẩn bị tích hợp để TV3 review, không ghi nhận là code tự viết thay TV3. Không sửa thuật toán/auth của TV1.

## Kết quả nghiệm thu

| Kiểm tra | Kết quả |
|---|---|
| Pytest Windows, Python 3.12.1 | **91 passed**, không xfail/skip |
| Pytest Linux trong image build mới, Python 3.12.16 | **91 passed**, không xfail/skip |
| Dependency check trong image | `pip check`: không có dependency lỗi |
| Docker Compose build + up --wait | DB/API healthy |
| Demo client | SV9001/SV9002 tạo 201, đọc 200 |
| PostgreSQL smoke | **19/19 đạt**, exit 0; xem [tv2_verification.json](tv2_verification.json) |
| Attack lab | **A1=401, A2=403, A3=True, A4=409, A5=409, Restore=200**, exit 0 |
| Benchmark | Đủ 100/1.000/10.000 bản ghi × plaintext/AES-GCM; exit 0 |

Cả hai lần pytest có một DeprecationWarning từ Starlette/AnyIO; không có lỗi test. Lần kiểm Linux đầu thiếu `.env.example` trong bản sao kiểm thử; sau khi bổ sung file mẫu, toàn bộ 91 test đạt. Không sửa test để bỏ qua lỗi đó.

Docker dùng project thử riêng, thư mục tạm, cổng tự chọn, khóa/token mới và volume riêng. Không dùng `.env` hay dữ liệu đang có của bạn. Các container thử được dừng sau khi lưu kết quả; volume thử được giữ lại. Lần chạy không phải nghiệm thu trên máy sạch độc lập: Windows đã có venv/Docker, image API được build với dependencies cài mới. Test Linux được chạy sau khi chép tests/scripts và `.env.example` vào container thử.

Bằng chứng: [log tích hợp](evidence/tv2_integration_runs.json), [CSV benchmark](evidence/benchmark_integration.csv), [môi trường và cách đọc kết quả](evidence/README.md). CSV là số đo tham khảo trên máy hiện tại; chưa thay biểu đồ/phân tích Chương 5 của TV3. Không có khóa/token/URL chứa mật khẩu trong bằng chứng.

## Thứ tự merge đề xuất

1. Hoàn tất nội dung và xác nhận H2–H5 tại issue #3; dùng bản nháp đã chuẩn bị. Review PR #5 theo [ghi chú](TV2_REVIEW_GHI_CHU.md), giải quyết yêu cầu GitHub đang blocked. TV1/TV3 review đúng phần họ phụ trách.
2. Merge PR #5 sau khi được duyệt. Trạng thái xfail ở PR riêng là giai đoạn chờ API; bản tích hợp tiếp theo phải bỏ marker và chạy đủ test.
3. Cập nhật nhánh local đã chuẩn bị bằng main mới, kiểm tra lại nếu có thay đổi, rồi push nhánh này và mở PR vào main bằng [PR draft](TV2_PR_DRAFT.md). Sau PR #5, phần source TV3 đã nằm trong base nên diff tập trung vào TV2 và sửa test tích hợp.

```powershell
git fetch origin
git switch integration/tv2-merge-prep
git merge origin/main
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
git push -u origin integration/tv2-merge-prep
```

Các lệnh trên là bước bàn giao tiếp theo, chưa push trong lần chuẩn bị này. Không cần force-push. Không đồng thời mở thêm PR trùng nội dung từ nhánh `feature/api-db` cũ. Nếu nhóm chọn đổi nhánh PR, giữ nguyên commit đã kiểm và kiểm diff trước khi push.

4. Gán TV1/TV3 review; yêu cầu CI trên đúng commit chuẩn bị merge, không dùng CI xanh của `3edd89b` thay cho CI bản ghép. Chỉ merge khi review/CI đạt.
5. Sau merge, kiểm trên main: Docker, demo, pytest, verify_tv2 và attack_lab. TV3 chủ trì máy sạch/release; cả nhóm ghép tài liệu và tổng duyệt.

## Việc chưa thể đánh dấu hoàn tất

- Chưa push nhánh chuẩn bị, mở PR TV2, đăng comment/approval hoặc merge remote trong đợt này.
- Chưa hoàn tất H2–H5 và xác nhận của tất cả thành viên trên issue.
- Tree TV3 chưa có Chương 5, biểu đồ benchmark và bằng chứng máy sạch/release; các sản phẩm đó cần TV3 hoàn thiện.
- Tên/MSSV, ghép Word/slide chung, ảnh demo và luyện trình bày cần bạn/cả nhóm cung cấp hoặc thực hiện.
- Replay cùng ô, lộ khóa/máy ứng dụng, token tĩnh/HTTP và metadata để rõ là các giới hạn thiết kế đã ghi; kết quả test không xóa bỏ các giới hạn này.
