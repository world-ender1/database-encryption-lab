# Đối chiếu kế hoạch cả nhóm và thử nghiệm A1–A8

Ngày 15/11/2026. Source tích hợp đã kiểm: `9eb7bbc` trên `integration/tv2-merge-prep`. Các nhánh GitHub chưa thay đổi ở lần fetch của đợt audit này.

**Kết luận:** hành vi ứng dụng đạt các tình huống A1–A8 theo phạm vi kế hoạch. Tuy nhiên, chưa đủ điều kiện nói mọi phần đã hoàn thiện: attack lab còn thiếu điều kiện tự kiểm, phân công test chưa khớp hoàn toàn, một số sản phẩm và nghiệm thu cuối chưa có bằng chứng. Có thể tiếp tục dùng bản ghép local để nghiệm thu; chưa nên đánh dấu hoàn tất đồ án hoặc gắn release.

## 1. Căn cứ đánh giá

- Kế hoạch chung: `docs/ke-hoach/Ke_hoach_Database_Encryption_3_thanh_vien_v4.docx`; đã đọc cả các bảng, trọng tâm mục 2, 4–8, 10, 12.
- Kế hoạch riêng: ba file `Ke_hoach_thuc_hien_TV1.md`, `Ke_hoach_thuc_hien_TV2.md`, `Ke_hoach_thuc_hien_TV3.md` cùng thư mục. Các bản này dẫn chiếu v4 ngày 13/11/2026. Không có file kế hoạch v3 độc lập trong tree đã kiểm nên không khẳng định đối chiếu riêng từng câu của v3.
- Đọc source/test, bằng chứng PostgreSQL/benchmark; chạy bổ sung A6/A7/A8, probe logic pass/fail của lab bằng mock và kiểm tra PostgreSQL với điều kiện chặt hơn.
- Đọc GitHub refs, PR/reviews, issue #3, trạng thái bảo vệ main và remote tags. Không đăng comment, sửa settings, push, approve hoặc merge remote.

“Đạt kỹ thuật” nói về hành vi đã kiểm. “Chưa có bằng chứng” không đồng nghĩa thành viên chưa làm trên máy riêng. Checkbox chưa tick trong kế hoạch không được dùng riêng để kết luận chưa hoàn thành.

## 2. Ma trận attack theo đúng kế hoạch

TV3 bước 15 quy định A6/A7 lấy từ C03/C07 của TV1, A8 lấy từ test_security. Vì vậy attack_lab.py chỉ chạy A1–A5 là **đúng phân công**, không phải thiếu ba kịch bản.

| Mã | Kỳ vọng | Bằng chứng đã kiểm | Kết luận |
|---|---|---|---|
| A1 | Không token → 401 | API thật: 401, WWW-Authenticate=Bearer; suite có sai token/scheme | Đạt phạm vi đã thử |
| A2 | Viewer DELETE → 403, dữ liệu nguyên vẹn | API thật 403; toàn bộ hàng trước/sau bằng nhau; GET trả payload gốc | Hành vi đạt; script còn thiếu điều kiện F1 |
| A3 | Raw SQL không thấy plaintext ở cột nhạy cảm | Smoke 19/19; audit kiểm cả ba field của SV9001/SV9002, độ dài tag/nonce | Đạt kiểm tra raw SQL; không phải thử phá AES hay chứng minh tuyệt đối tính bí mật |
| A4 | Sửa CT → 409 integrity_failure; restore=200 | Hàm a4 thật: đúng status/code; hàng khôi phục đúng byte, GET đúng payload; restore cả khi HTTP ném lỗi | Hành vi đạt; script còn F2/F3 |
| A5 | Tráo CT+nonce → 409 integrity_failure; restore=200 | Hàm a5 thật: đúng status/code; cả hai hàng/payload khôi phục; thử thêm lỗi HTTP | Hành vi đạt; script còn F2/F3 |
| A6 | Sai khóa → IntegrityFailure | Chạy lại test_c03_wrong_key: đạt | Đạt mức module như kế hoạch; không tuyên bố đã đổi khóa API đang chạy |
| A7 | Ciphertext cũ cùng ô vẫn giải mã được | Chạy lại test_c07_replay_same_row_is_still_accepted: đạt | **Giới hạn đã xác nhận**, không phải đã chống replay |
| A8 | ID kiểu SQL → 422, DB không đổi | Hai ca test_security đạt; GET/POST trên PostgreSQL thật cũng 422, toàn bộ hàng không đổi | Đạt phạm vi ID theo H2; không gọi là kiểm toán mọi dạng SQL injection |

Bằng chứng mới: [17 điều kiện PostgreSQL đạt](evidence/attack_postgresql_audit.json), [probe điều kiện pass/fail](evidence/attack_gate_audit.json), [metadata và bốn test A6/A7/A8](evidence/plan_audit_metadata.json). Bốn test gồm A6, A7 và hai biến thể A8. Probe mock kiểm **công cụ kết luận**, không chứng minh ứng dụng thật đã trả sai hoặc mất dữ liệu.

Bộ 91 test Windows/Linux từ lần nghiệm thu trước vẫn áp dụng vì đợt audit này không sửa source/test ứng dụng. Các kiểm tra bổ sung không thay ảnh và nhật ký cuối theo mục 8.7/10.2.

## 3. Những điểm còn lệch và cách xử lý

### F1 — A2 bỏ qua điều kiện dữ liệu còn nguyên trong giá trị trả về

`scripts/attack_lab.py:a2` in row_exists nhưng chỉ trả HTTP status; main chỉ so c2==403. Probe DELETE=403, GET=404 vẫn trả 403 dù in row still there: False. Các bước sau có thể bắt lại một số lỗi, nhưng tiêu chí của chính A2 chưa đầy đủ.

**TV3 xử lý:** trả kết quả chứa cả status và kiểm dữ liệu; chỉ đạt nếu 403, đọc lại 200 và payload/row không đổi. Thêm test 403 nhưng GET 404 hoặc dữ liệu đã đổi. Không cần đổi H1–H5.

### F2 — A4/A5 chấp nhận mọi 409, chưa kiểm code lỗi

Hàm _status bỏ body. Probe phản hồi 409 với code duplicate_student vẫn được a4/a5 trả về như kết quả mong đợi; response.json không được gọi. H2 và kế hoạch chung mục 2.3/5.8 yêu cầu tamper phải là integrity_failure.

**TV3 xử lý:** kiểm status=409 và code=integrity_failure, response không chứa dữ liệu nhạy cảm; thêm test 409 sai code, thiếu code hoặc body không phải JSON. Ứng dụng hiện đã trả đúng khi thử thật; điểm yếu nằm ở công cụ kiểm chứng.

### F3 — Kiểm chứng restore của script chưa đủ mạnh

Code có finally và audit thật đã chứng minh restore hoạt động cả khi HTTP lỗi. Nhưng script chỉ kiểm GET SV9001=200 ở cuối; chưa so payload trước/sau, chưa ghi restore riêng từng A4/A5, chưa xác nhận SV9002 nguyên vẹn. Đây là thiếu độ mạnh của bằng chứng, không phải lỗi restore quan sát được.

**TV3 xử lý:** snapshot hàng/cột liên quan, sau từng finally so sánh byte và GET/payload; thêm test gây lỗi HTTP. Giữ cấu trúc khôi phục hiện có.

### F4 — Phân công file/test còn lệch

Kế hoạch TV2 bước 16 ghi test tamper thuộc TV3. `test_failed_decryption_blocks_entire_list_and_allows_delete` trong test_api vẫn sửa trực tiếp phone_ct thành bytes rỗng. Lần chuẩn bị trước giữ nó vì kiểm H2, nhưng cách gây lỗi vẫn là tamper nên chưa khớp phân công chặt.

Bản ghép cũng đã sửa test_security để bỏ xfail và nhận sáu ca quyền route. Đây là việc vòng 2 cần làm, nhưng file thuộc TV3 và chưa có xác nhận tiếp nhận trên PR/issue. Nhánh local chưa thay cho bàn giao quyền sở hữu.

**Phương án A, khuyến nghị:** TV3 nhận test tamper và test quyền trong commit/PR vòng 2; TV2 giữ CRUD, mapping H1/H3 và mã lỗi. **Phương án B:** TV2 dùng dependency crypto giả ném IntegrityFailure để kiểm H2; chỉ test_security sửa DB. Ghi nhận lựa chọn trên PR.

### F5 — Chưa thấy pytest là check bắt buộc của main

GitHub trả main protected=true nhưng required_status_checks có enforcement_level=off, contexts=[] và checks=[]. API rulesets trả danh sách rỗng. TV1 bước 7 và kế hoạch chung mục 7.6 yêu cầu check pytest bắt buộc. Đây là bằng chứng cụ thể hơn lần trước chỉ gặp 404 ở endpoint protection; chưa suy ra được toàn bộ quy tắc review của repo.

**TV1/chủ repo xử lý:** sau khi workflow lên main, cấu hình required pytest và review PR, kiểm lại trước merge/release. Không bỏ qua trạng thái blocked của PR #5. Lần audit này không tự đổi settings.

### F6 — Bằng chứng TDD/mutation/coverage TV1 chưa tái lập đầy đủ

Có commit test 73f5fb8 trước code 2cfefa5. crypto_design.md ghi 17/18 mutant bị bắt, M13 kiểm bằng đọc code, coverage 100%. Tuy nhiên tmp_mutants.py, kế hoạch tuần 1 được dẫn chiếu và báo cáo coverage/mutation gốc chưa có trong tree. Máy audit chưa cài coverage; không coi mô tả là số đo đã chạy lại.

**TV1 xử lý:** bàn giao script/ghi chú cùng kết quả, hoặc phụ lục có commit/lệnh chạy để tái lập. Đây là thiếu bằng chứng theo kế hoạch riêng, không chứng minh thuật toán sai.

### F7 — Thiếu sản phẩm báo cáo/demo và nghiệm thu cuối

- TV1: chưa thấy Chương 1–2, slide riêng và bộ báo cáo/slide ghép. crypto_design không tự thay đủ các sản phẩm này.
- TV2: Chương 3–4, Word/PPTX đã có; còn tên/MSSV, TV1 xác nhận phần mật mã, ảnh Swagger/psql, luyện 3 phút và ghép chung.
- TV3: có source, số đo/log, threat model và demo script; chưa thấy Chương 5, hai biểu đồ INSERT/SELECT, bảng overhead, slide tấn công/benchmark và ảnh bước 15–20. Metadata benchmark thiếu RAM/OS chi tiết.
- Chung: chưa có Chương 6 ghép, báo cáo sáu chương, slide thống nhất, nhật ký/ảnh đầy đủ, nghiệm thu máy sạch, tag v1.0.0 và tổng duyệt 12 phút. Remote tags đang rỗng.

**Phương án:** dùng mục 2 làm phần chữ nhật ký 8.7; chụp ảnh từ buổi chạy thật. TV1 viết/ghép Chương 1–2/6, TV2 bàn giao Chương 3–4, TV3 viết Chương 5 và vẽ đồ thị số đo thật. Nêu nhiễu đo, nhất là overhead đọc âm ở mẫu 100; không kết luận mã hóa nhanh hơn. Nghiệm thu máy sạch sau merge để lấy bộ minh chứng cuối rồi tag.

### F8 — Cách lưu CSV ở bản chuẩn bị cần chốt lại

TV3 bước 16 ghi không commit benchmark_results.csv, đưa số liệu vào báo cáo. Lượt chuẩn bị trước thêm bản sao `docs/evidence/benchmark_integration.csv`; dù không trùng tên bị gitignore, đây vẫn là CSV benchmark trong Git, chưa có quyết định nhóm về ngoại lệ.

**Phương án A, theo sát kế hoạch:** giữ CSV ngoài Git, đưa bảng/biểu đồ vào báo cáo, bỏ bản sao khỏi tree bằng commit mới, không rewrite lịch sử chung. **Phương án B:** nhóm đồng ý lưu dữ liệu đo đã loại bí mật trong evidence để tái lập. Không dùng đổi tên file để coi là đã tuân thủ. Audit giữ nguyên bằng chứng và nêu rõ lựa chọn.

### F9 — Sprint 0 lệch lịch sử, không dựng lại commit

Tree PR #1 tại 4592eac thiếu API/Docker TV2 và CI/fixture TV3 dù kế hoạch yêu cầu đủ khung trước tách nhánh. Code hiện đã bù nhưng chưa merge main. Hợp đồng và các review API/TV3 còn dở.

**Phương án:** giữ lịch sử, ghi nhận sai lệch; hoàn tất hợp đồng, review và nghiệm thu main hiện tại. Không hạ CRUD về 501, reset hay force-push để tạo lại Sprint 0.

## 4. Đối chiếu từng bước TV1

| Bước | Yêu cầu | Trạng thái |
|---|---|---|
| 0, 2 | Repo/nhánh/cộng tác | Repo có; TV2 đọc được private repo; chưa kiểm được mọi lời mời. Required pytest còn F5 |
| 1 | H1–H5 | Issue #3 có H1 và đồng ý TV2; chưa chốt đủ H2–H5 |
| 3–6 | Key, crypto, auth, init_env | Code và bốn file test đầy đủ; hiện AES-GCM thật. Chưa có đủ nhật ký đỏ/xanh ban đầu |
| 7 | Sprint 0 và CI | Lệch lịch sử F9, check bắt buộc F5 |
| 8–9 | Nghiên cứu/AES-GCM/TDD | Code/tài liệu khớp; có commit test trước code |
| 10 | Mutation/coverage | Có mô tả, thiếu nguồn/báo cáo tái lập F6 |
| 11, 15 | PR crypto/docs | #2/#4 đã merge; **TV2 hvlchv đã APPROVED cả hai** |
| 12–13 | C07, crypto_design | Có, mô tả đúng giới hạn |
| 14 | TV1 review API | Chưa có PR TV2 để xác nhận hoàn tất |
| 16–18 | PostgreSQL/sửa lỗi/phản biện | Bản ghép có bằng chứng thật; chưa ghi nhận TV1 tự nghiệm thu/đóng toàn bộ đầu việc |
| 19 | Chương 1–2, crypto Chương 4 | Có tài liệu crypto; chưa thấy Chương 1–2, còn review phần ghép Chương 4 |
| 20–22 | Slide/ghép/tổng duyệt | Chưa có bằng chứng hoàn tất F7 |

## 5. Đối chiếu từng bước TV2

| Bước | Yêu cầu | Trạng thái |
|---|---|---|
| 1–2 | Hợp đồng/repo | Đã đồng ý H1; bản H2–H5 chuẩn bị nhưng chưa đăng/chốt |
| 3–6 | Config/DB/model/schemas/crypto dependency | Khớp H2–H4; code/test và nghiệm thu thật |
| 7–9 | Khung/Docker/Sprint 0 | Docker hiện đạt; lịch sử lệch F9, không cần hạ CRUD |
| 10–12 | Mapping, POST/GET/list/lỗi | Đạt bộ test và smoke PostgreSQL |
| 13 | Review crypto | **Đã làm:** APPROVED PR #2/#4 trên GitHub |
| 14–15 | PUT/DELETE/demo | Đạt: nonce mới, PUT cấm ID, DELETE 204, hai hồ sơ demo đọc được |
| 16 | Test API và mapping | Mapping đã bổ sung; còn test gây tamper cần F4 |
| 17 | api_db.md | Có đủ cấu hình/schema/API/cách chạy/giới hạn |
| 18 | PR API/review TV3 | Có draft/nhánh ghép; chưa PR API, PR #5 chưa review |
| 19–20 | DB thật/lỗi tích hợp | Đạt phạm vi thử; không phát hiện lỗi CRUD, còn vấn đề công cụ/quy trình |
| 21–22 | Chương 3–4/slide/demo | Có Markdown/Word/PPTX; còn thông tin cá nhân, xác nhận/ghép và ảnh |
| 23 | Luyện/tổng duyệt | Chưa có bằng chứng, cần người trình bày thực hiện |

## 6. Đối chiếu từng bước TV3

| Bước | Yêu cầu | Trạng thái |
|---|---|---|
| 1–2 | Repo/điều phối hợp đồng | Nhánh/PR có, issue #3 chưa đủ |
| 3–5 | Dependencies/CI/fixture | File có, chạy trên bản ghép; fixture lazy import đúng |
| 6 | Sprint 0 | Lệch F9; workflow chưa trên main hiện tại |
| 7–8 | Threat model/test_security | Đủ A1–A5/A8; nhánh gốc xfail, bản ghép đã bỏ |
| 9, 11 | Lab/thử ghép | Chạy thật đạt; còn điều kiện kết luận F1–F3 |
| 10 | Benchmark đúng thiết kế | Hai bảng, ba mức n, warmup, median ba lần, đo DB; payload_bytes đúng phạm vi |
| 12 | README | Đủ mục chính; chưa có nghiệm thu clone sạch cuối cùng |
| 13 | PR vòng 1/review API | PR #5 mở, CI success, chưa review; chưa PR API |
| 14, 17 | Bỏ xfail/PR vòng 2 | Chuẩn bị local, chưa PR/bàn giao TV3 F4 |
| 15 | A1–A8/ảnh/nhật ký | Có kết quả; audit bổ sung actual; thiếu ảnh và nhật ký cuối Chương 5 |
| 16 | Benchmark/cấu hình/đồ thị | Có số đo; thiếu hai đồ thị, overhead, RAM/OS chi tiết; xử lý F8 |
| 18 | Chương 5 | Chưa thấy sản phẩm trong repo |
| 19 | Demo script | Có timeline/lời dẫn; chưa có bộ ảnh dự phòng |
| 20 | Slide attack/benchmark | Chưa thấy; cần ma trận A1–A8, đồ thị và overhead |
| 21–23 | Máy sạch/tag/tổng duyệt | Chưa có bằng chứng; remote chưa tag |

## 7. Nghiệm thu kế hoạch chung

| Mục | Đánh giá |
|---|---|
| 1: bài toán/ranh giới | Khớp: ba field, dữ liệu giả, metadata rõ, giới hạn replay/key/app |
| 2: phân công/H1–H5 | Interface chạy khớp; chốt hợp đồng và phân công còn F4/F9 |
| 3: setup | Host/container chạy; chưa phải máy sạch clone main |
| 4–5: TV1/TV2 | Lõi chức năng khớp; bàn giao còn ở bảng trên |
| 6: bảo mật/benchmark | Hành vi đạt; công cụ cần F1–F3, ảnh/biểu đồ còn thiếu |
| 7: Git/CI/release | PR1/2/4 merge; PR5 chưa; API local; F5 và chưa tag |
| 8: attack/nhật ký | A1–A8 có kết quả đúng cấp kiểm; còn nhật ký cuối/ảnh |
| 9: demo | Có script/slide TV2; thiếu slide TV1/TV3, ảnh và rehearsal |
| 10: DoD nhóm | **Chưa đạt đầy đủ:** review/CI/main/máy sạch/ảnh/báo cáo |
| 11: hướng dẫn lỗi | Có trong kế hoạch/README/api_db; không thấy yêu cầu code mới bắt buộc |
| 12: báo cáo | Có tài liệu module và Chương 3–4; chưa đủ sáu chương/slide chung |

## 8. Phương án kết hợp tiếp theo

**A — khuyến nghị, bám phân công:** giữ nhánh ghép local để nghiệm thu. TV3 xử lý F1–F4 trong test/lab và review; TV2 hoàn tất H2–H5/PR; TV1 cấu hình required pytest, cung cấp F6. Sau review/merge, chạy CI/PostgreSQL trên main. Hoàn thiện tài liệu/ảnh/đồ thị, nghiệm thu máy sạch rồi tag. Không cần viết lại ứng dụng hoặc đổi H1.

**B — PR tích hợp chung:** nhóm thống nhất nhận các commit trên integration/tv2-merge-prep, chỉ rõ phần từng người review, đưa sửa F1–F4 vào PR này, chốt lưu CSV và tránh PR trùng #5. Vẫn cần CI/review và điều kiện phát hành. Một PR không tự thay xác nhận chủ file. Kế hoạch cho phép merge không theo thứ tự; “PR #5 trước” ở hướng dẫn cũ là đề xuất thuận tiện, không bắt buộc.

Đợt audit này bổ sung kết quả và đối chiếu, không tự nhận viết Chương 1–2/5 hoặc sửa module TV1/TV3. **Chưa push/merge/tag** vì điều kiện “khớp và hoàn thiện hết” chưa thỏa mãn. Mỗi phần còn lệch đã có chủ xử lý, phương án và tiêu chí kiểm lại ở trên.
