# Cập nhật đối chiếu kế hoạch và chuẩn bị merge — 16/11/2026

Phạm vi: so sánh GitHub sau `git fetch origin --prune` với [đợt đối chiếu 15/11](DOI_CHIEU_KE_HOACH_CA_NHOM.md), kiểm PR/issue qua GitHub API, ghép thử local và chạy pytest. Không push, merge hoặc sửa PR trên GitHub.

> **Cập nhật sau lần kiểm này:** các mục code F1–F4 và bằng chứng F6/F8 đã được sửa tiếp trên nhánh tích hợp local. Xem mục “Trạng thái sau khi sửa” cuối tài liệu; các đoạn dưới giữ lại kết luận tại thời điểm audit ban đầu.

## Thay đổi mới

| Thành viên | Nhánh/PR hiện tại | Nhận xét |
|---|---|---|
| TV1 | `main` vẫn `692337a`; thêm [`fix/6-decrypt-utf8`, PR #7](https://github.com/world-ender1/database-encryption-lab/pull/7) tại `d6e3177` | Ba commit test → fix → docs sửa lỗi H1: ciphertext có tag hợp lệ nhưng plaintext không phải UTF-8 nay báo `IntegrityFailure`. Test mới có vector cố định. Chưa merge. |
| TV2 | `feature/api-db` vẫn `0017e18`; bản ghép local `integration/tv2-merge-prep` tại `0c09cda` | Không có commit mới trên nhánh GitHub, chưa có PR API/DB. CRUD/DB/Docker và Chương 3–4 vẫn theo kết quả kiểm 15/11. |
| TV3 | [`feature/security-benchmark`, PR #5](https://github.com/world-ender1/database-encryption-lab/pull/5) vẫn `3edd89b` | Không có commit mới. Check `pytest` trên PR #5 thành công nhưng PR vẫn `mergeable_state=blocked`; chưa có review được submit. Comment “ok” ngày 16/11 không phải approval. |

[Issue #3](https://github.com/world-ender1/database-encryption-lab/issues/3) vẫn mở, chưa có cập nhật sau 14/11; H2–H5 chưa được chốt trong issue. [Issue #6](https://github.com/world-ender1/database-encryption-lab/issues/6) vẫn mở vì PR #7 chưa merge. PR #7 `mergeable=true` nhưng `mergeable_state=blocked`, chưa có review và không có check run: workflow `tests.yml` hiện chỉ nằm trong PR #5, chưa ở `main`.

## Kiểm tra kỹ thuật mới

- Diff PR #7 chỉ có `app/crypto_service.py`, `tests/test_crypto.py`, `docs/crypto_design.md`. Thay đổi bắt `UnicodeDecodeError` và chuyển thành `IntegrityFailure`, đúng lỗi nêu trong issue #6; không đổi chữ ký H1.
- `git merge-tree --write-tree integration/tv2-merge-prep origin/fix/6-decrypt-utf8`: không có xung đột. Ghép thử trong worktree tạm bằng `git merge --no-commit --no-ff` cũng sạch; worktree đã dọn sau kiểm tra.
- Bản tích hợp hiện tại: `python -m pytest -q` → **91 passed**. Bản ghép thử thêm PR #7: **92 passed**. Chưa chạy lại PostgreSQL/Docker hoặc benchmark ngày 16/11; dùng kết quả ngày 15/11 trong đối chiếu trước cho các mục đó.

## Đối chiếu năm phản ánh về nhánh `feature/api-db`

| Phản ánh | Kết quả kiểm lại |
|---|---|
| 1. Chưa mở PR | **Đúng với GitHub.** `feature/api-db` chưa có PR; `integration/tv2-merge-prep` cũng chưa push/mở PR. |
| 2. Thiếu năm commit của `main` | **Đúng với nhánh GitHub:** `git log origin/feature/api-db..origin/main` liệt kê năm commit liên quan PR #2/#4. **Đã xử lý local:** `origin/main` là tổ tiên của `integration/tv2-merge-prep`. |
| 3. Xung đột với PR #5 ở hai file | **Đúng khi ghép ban đầu.** Bản tích hợp local đã giải quyết; `requirements.txt` và `tests/conftest.py` khớp nguyên bản TV3 (`git diff --exit-code` bằng 0). `origin/feature/security-benchmark` là tổ tiên của bản tích hợp. |
| 4. `docs/tv2_verification.json` là kết quả cũ | **Đúng trên `feature/api-db`:** ngày 13/11, `result=blocked_by_plaintext`. **Đã chạy lại local:** file trên bản tích hợp ghi 15/11, `result=pass`, 19/19 điều kiện đạt với AES-GCM thật. Chưa có kết quả mới trên GitHub/main. |
| 5. Tài liệu TV2 còn câu cũ | **Đúng trên `feature/api-db`:** Markdown vẫn gọi crypto là bản tạm. **Đã cập nhật local:** Markdown, Word và PowerPoint mô tả AES-GCM thật và kết quả 91 test; Word nhắc 73 passed/3 xfailed chỉ để nói rõ đó là kết quả cũ. Nhóm vẫn cần quyết định có giữ các file Word/PowerPoint trong repo và ghép báo cáo cuối. |

Vì vậy, năm phản ánh mô tả **nhánh TV2 trên GitHub** chính xác, nhưng mục 2–5 không còn là việc thiếu trên **bản ghép local**. Mục 1 và việc bàn giao/review các thay đổi local vẫn chưa xong.

## Đánh giá trước merge

**Code đủ để chạy demo trên bản tích hợp local; chưa sẵn sàng merge trên GitHub theo quy trình nhóm.** Lý do trực tiếp: PR #5/#7 còn blocked và chưa có review, nhánh tích hợp TV2 chưa có PR, CI chưa chạy trên đúng commit tích hợp. Các điểm F1–F9 trong [đối chiếu 15/11](DOI_CHIEU_KE_HOACH_CA_NHOM.md) chưa được giải quyết bởi ba commit mới của PR #7. Trọng tâm còn lại:

1. **TV3:** sửa điều kiện kết luận attack lab A2/A4/A5/restore (F1–F3); tiếp nhận/review phần test tamper và test quyền đã chuẩn bị trong bản ghép (F4). PR #5 cần review thật và giải quyết trạng thái blocked.
2. **TV2:** chốt H2–H4 với TV1/TV3 trong issue #3, đưa API/DB và bản tích hợp lên PR, yêu cầu TV1/TV3 review. F8 đã xử lý trong bản local sau audit: bỏ bản sao CSV và đưa bảng/biểu đồ vào Chương 5.
3. **TV1:** hoàn tất review PR #7 và bằng chứng mutation/coverage tái lập (F6); cùng chủ repo thiết lập required `pytest` trên `main` sau khi workflow được merge (F5). H5 cần TV3 xác nhận trong issue #3.
4. **Cả nhóm:** hoàn thiện Chương 1–2, 5–6, biểu đồ/slide chung, ảnh demo, nghiệm thu máy sạch và tổng duyệt trước khi gắn tag (F7). Đây là điều kiện hoàn tất đồ án/release, không phải bằng chứng code không chạy hay lý do bắt buộc hoãn mọi PR. Sai lệch lịch sử Sprint 0 (F9) chỉ cần ghi nhận, không viết lại lịch sử.

Đường merge đề xuất: TV3 cập nhật/review PR #5 và merge để đưa CI lên `main`; TV1 cập nhật PR #7 với `main`, chờ CI và review rồi merge; sau đó TV2 cập nhật nhánh tích hợp, mở PR chứa API/DB và các sửa tích hợp, chạy CI trên đúng head commit và review theo chủ phần việc. Chạy lại PostgreSQL/demo/attack lab trên `main` sau merge; chỉ nghiệm thu release khi tài liệu và minh chứng cuối đủ. PR #7 có thể merge trước PR #5 nếu nhóm chấp nhận thiếu CI ở thời điểm đó, nhưng theo kế hoạch nên có check bắt buộc trước merge.

## Trạng thái sau khi sửa trên nhánh tích hợp local

| Mục | Trạng thái mới |
|---|---|
| F1–F3 | Đã sửa attack lab: A2 so DB/payload; A4/A5 so `code=integrity_failure`, không lộ field nhạy cảm; restore so byte hàng và payload. 9 test chống pass giả/HTTP lỗi đạt. Chạy PostgreSQL cô lập ngày 16/11 đạt A1–A5; xem [log](evidence/merge_validation_2026-11-16.json). |
| F4 | Test tamper nằm trong `test_security.py`; test API giữ H2 bằng dependency crypto giả ném `IntegrityFailure`. Code local đã qua 102 test; TV3 vẫn cần review file sở hữu. |
| F5 | Workflow có trong bản tích hợp, nhưng required pytest trên `main` và CI/review của PR cuối vẫn cần chủ repo xử lý sau khi PR được đưa lên GitHub. |
| F6 | Đã tái kiểm 48 test TV1, coverage 100% dòng/nhánh và 18/19 mutant bị bắt bằng [script tái lập](../scripts/recheck_tv1_mutations.py). Đây là bằng chứng mới, không thay log TDD gốc của TV1. |
| F7 | Có bản ghép Chương 1–6 bằng Markdown/Word, Chương 5 có hai biểu đồ; cần chủ phần việc xác nhận, điền tên/MSSV, chụp ảnh từ PR/main cuối, nghiệm thu máy sạch và tổng duyệt. |
| F8 | Đã bỏ bản sao CSV khỏi Git; sáu hàng số liệu benchmark ngày 15/11, overhead và biểu đồ nằm ở [Chương 5](TV3_BAO_CAO_CHUONG_5.md). |
| F9 | Giữ nguyên lịch sử Sprint 0; không reset/force-push. |

`main` đã được fetch và merge kiểm tra, trả “Already up to date”; bản sửa PR #7 đã ghép vào local. **Code local chạy demo và test**, nhưng bản GitHub chưa có PR API/DB, PR #5/#7 còn cần review/merge; CI trên đúng head commit và nghiệm thu main cuối chưa có. Không gắn tag hoặc gọi đây là release.
