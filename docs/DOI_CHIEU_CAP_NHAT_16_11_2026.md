# Cập nhật đối chiếu kế hoạch và chuẩn bị merge — 16/11/2026

Phạm vi: so sánh GitHub sau `git fetch origin --prune` với [đợt đối chiếu 15/11](DOI_CHIEU_KE_HOACH_CA_NHOM.md), kiểm PR/issue qua GitHub API, ghép thử local và chạy pytest. Không push, merge hoặc sửa PR trên GitHub.

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

## Đánh giá trước merge

**Code có thể ghép về mặt xung đột và test local, nhưng chưa đủ điều kiện merge toàn bộ thành bản hoàn chỉnh trên GitHub.** Các điểm F1–F9 trong [đối chiếu 15/11](DOI_CHIEU_KE_HOACH_CA_NHOM.md) chưa được giải quyết bởi ba commit mới của PR #7. Trọng tâm còn lại:

1. **TV3:** sửa điều kiện kết luận attack lab A2/A4/A5/restore (F1–F3); tiếp nhận/review phần test tamper và test quyền đã chuẩn bị trong bản ghép (F4). PR #5 cần review thật và giải quyết trạng thái blocked.
2. **TV2:** chốt H2–H4 với TV1/TV3 trong issue #3, đưa API/DB và bản tích hợp lên PR, yêu cầu TV1/TV3 review. Chốt cùng TV3 cách lưu CSV benchmark (F8).
3. **TV1:** hoàn tất review PR #7 và bằng chứng mutation/coverage tái lập (F6); cùng chủ repo thiết lập required `pytest` trên `main` sau khi workflow được merge (F5). H5 cần TV3 xác nhận trong issue #3.
4. **Cả nhóm:** hoàn thiện Chương 1–2, 5–6, biểu đồ/slide chung, ảnh demo, nghiệm thu máy sạch và tổng duyệt trước khi gắn tag (F7). Sai lệch lịch sử Sprint 0 (F9) chỉ cần ghi nhận, không viết lại lịch sử.

Đường merge đề xuất: TV3 cập nhật/review PR #5 và merge để đưa CI lên `main`; TV1 cập nhật PR #7 với `main`, chờ CI và review rồi merge; sau đó TV2 cập nhật nhánh tích hợp, mở PR chứa API/DB và các sửa tích hợp, chạy CI trên đúng head commit và review theo chủ phần việc. Chạy lại PostgreSQL/demo/attack lab trên `main` sau merge; chỉ nghiệm thu release khi tài liệu và minh chứng cuối đủ. PR #7 có thể merge trước PR #5 nếu nhóm chấp nhận thiếu CI ở thời điểm đó, nhưng theo kế hoạch nên có check bắt buộc trước merge.
