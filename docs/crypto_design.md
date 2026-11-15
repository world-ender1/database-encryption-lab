# Thiết kế phần mật mã và xác thực

Tài liệu này mô tả thiết kế của bốn file do TV1 phụ trách: `app/key_manager.py`, `app/crypto_service.py`, `app/auth.py`, `scripts/init_env.py`. Giao diện của chúng là hợp đồng H1, ghi trong issue #3 “Hợp đồng H1–H5”. Mô hình đe dọa của cả hệ thống do TV3 viết trong `docs/threat_model.md`; ở đây chỉ bàn phần mật mã.

Quy ước: số trong ngoặc vuông như [2] trỏ tới mục Tài liệu tham khảo ở cuối; tên dạng `test_...` là test trong thư mục `tests/` kiểm khẳng định đứng trước nó. Mã kịch bản tấn công A1–A8 theo kế hoạch v4.

## 1. Phạm vi

Ứng dụng mã hóa ba trường của bảng `students` bằng AES-256-GCM trước khi ghi xuống PostgreSQL: `national_id` (số CCCD), `phone`, `address`. Cơ sở dữ liệu chỉ nhận ciphertext. Khóa nằm ở ứng dụng và không bao giờ được gửi xuống DB. Các cột còn lại (`student_id`, họ tên, ngành) lưu dạng rõ.

So với hai cách mã hóa khác (rút gọn từ ghi chú nghiên cứu W1-08, câu 6):

| | Mã hóa ổ đĩa | TDE (mã hóa trong DBMS) | Mã hóa tầng ứng dụng (dự án) |
|---|---|---|---|
| Ai mã hóa | Hệ điều hành | DBMS, khi ghi trang dữ liệu và log xuống đĩa [7] | Ứng dụng, từng trường, trước khi gửi xuống DB |
| Khóa ở đâu | Hệ điều hành | Trong DBMS [7] | File `.env` của ứng dụng, ngoài DB |
| Chống được | Mất ổ đĩa khi máy đang tắt | Mất file dữ liệu, file log, bản sao lưu [7] | Mọi trường hợp chỉ lấy được DB: bản dump, bản sao lưu, người quản trị DB, SQL injection đọc bảng |
| Người truy vấn được DB | Thấy dữ liệu rõ | Thấy dữ liệu rõ | Chỉ thấy ciphertext |

PostgreSQL bản cộng đồng không có TDE dựng sẵn. Tài liệu PostgreSQL xếp cách làm của dự án vào nhóm mã hóa phía client, trong đó dữ liệu chưa mã hóa không bao giờ xuất hiện trên máy chủ DB [6]. Dự án không dùng pgcrypto, vì với pgcrypto khóa phải gửi kèm câu SQL và có mặt trên máy chủ DB trong lúc truy vấn chạy [6]. OWASP nhắc rằng chọn mức mã hóa nào tùy vào mô hình đe dọa [3].

Đổi lại, không tìm kiếm, sắp xếp hay đánh index được trên ba cột mã hóa (`WHERE phone = ...` không dùng được), vì cùng một giá trị mã hóa hai lần cho hai ciphertext khác nhau (`test_c02_nonce_and_ciphertext_differ`).

## 2. Định dạng lưu trữ

`CryptoService.encrypt` trả về `EncryptedValue(ciphertext, nonce, key_version)`:

- `ciphertext`: phần mã hóa dài đúng bằng plaintext tính theo byte UTF-8 [2, §5.2.1.2], cộng tag 16 byte mà `AESGCM` gắn vào cuối [1].
- `nonce`: 12 byte, sinh mới ở mỗi lần mã hóa (mục 6). `AESGCM` không đưa nonce vào kết quả [1], nên nonce phải được lưu riêng.
- `key_version`: nhãn phiên bản khóa, hiện là `"v1"` (mục 3).

`test_h1_encrypted_value_layout` kiểm ba field này, nonce dài 12 byte và ciphertext dài hơn plaintext đúng 16 byte.

Theo hợp đồng H3 (TV2 là chủ, chốt ở issue #3), mỗi trường được lưu thành hai cột nhị phân: `<field>_ct` giữ `ciphertext`, `<field>_nonce` giữ `nonce`. Cả hàng dùng chung một cột `key_version`. Như vậy mỗi trường tốn thêm 28 byte so với plaintext: 16 byte tag và 12 byte nonce. Ví dụ số CCCD 12 chữ số được lưu thành `national_id_ct` 28 byte và `national_id_nonce` 12 byte.

AAD không được lưu. Lúc giải mã, ứng dụng dựng lại AAD từ chính hàng đang đọc (mục 4).

## 3. `key_version`

`key_version` cho biết hàng được mã hóa bằng khóa nào. Nhãn này có mặt ở hai chỗ:

- cột `key_version` của bảng, lưu dạng rõ vì không phải bí mật;
- trong AAD (mục 4), nên ciphertext chỉ hợp lệ với đúng nhãn đã dùng lúc mã hóa.

Mỗi `CryptoService` giữ một khóa và một nhãn: `CryptoService(key, key_version="v1")`. Khi nhãn của `EncryptedValue` khác nhãn của service, `decrypt` báo `IntegrityFailure` ngay, chưa cần tới khóa. `test_c05_wrong_key_version` kiểm cả hai hướng: nhãn trong dữ liệu bị đổi thành `v2`, và service mang nhãn `v2` đọc dữ liệu `v1`.

Bản demo chỉ có `v1` vì chỉ có một khóa và chưa có xoay khóa. Nhãn được đặt sẵn từ đầu để sau này thêm khóa mới mà không phải đổi schema hay định dạng dữ liệu đã lưu (mục 9).

## 4. Thiết kế AAD

AAD (additional authenticated data) là dữ liệu được xác thực nhưng không được mã hóa [1]. GCM đưa AAD vào GHASH khi tính tag [2, §7.1], nên chỉ cần sai một byte AAD là giải mã thất bại. Dự án dùng:

```text
AAD = UTF-8 của f"student:{student_id}|field:{field}|key:{key_version}"
```

Ba thành phần đều đã công khai trên cùng hàng (khóa chính, tên cột, cột `key_version`), nên không cần giấu. Đưa chúng vào AAD là để buộc ciphertext vào đúng vị trí của nó:

| Thành phần | Chặn được | Test |
|---|---|---|
| `student_id` | Chép ciphertext của sinh viên này sang hàng của sinh viên khác (A5) | `test_c05_wrong_aad[other_student]` |
| `field` | Tráo ciphertext giữa hai cột của cùng một hàng, ví dụ `phone` và `address` | `test_c05_wrong_aad[other_field]` |
| `key_version` | Sửa nhãn phiên bản khóa trong dữ liệu | `test_c05_wrong_key_version` |

Nếu AAD không có `student_id`, người có quyền ghi vào DB tráo được số CCCD giữa hai sinh viên mà API vẫn trả về như dữ liệu đúng.

Chuỗi AAD là một phần của H1: đổi dù một ký tự thì mọi dữ liệu đã lưu không giải mã được nữa. `test_h1_known_vector_matches_aad_contract` giữ chuỗi này bằng một vector tính sẵn (khóa, nonce, AAD và ciphertext cố định).

AAD không chặn được việc chép lại ciphertext cũ của chính ô đó. Xem mục 7.

## 5. Quản lý khóa

- `scripts/init_env.py` sinh khóa 32 byte bằng `secrets.token_bytes(32)` và ghi vào `.env` dưới dạng Base64, biến `ENCRYPTION_KEY_B64`. Token admin, token viewer và mật khẩu PostgreSQL cũng sinh bằng `secrets`, mỗi lần chạy ra giá trị mới (`test_each_run_generates_new_secrets`). Script không in giá trị bí mật ra màn hình (`test_output_is_ascii_and_has_no_secret`).
- `.env` nằm trong `.gitignore`, không được commit. OWASP khuyên để khóa ở chỗ khác với dữ liệu, chẳng hạn dữ liệu ở DB thì khóa ở hệ thống file [3]. Vì vậy bản dump hay bản sao lưu DB không chứa khóa.
- Khóa Base64 đi qua `decode_key` trước khi tạo `CryptoService` (theo H1, `dependencies.py` của TV2 gọi hàm này). Base64 sai, chuỗi rỗng, hoặc giải ra khác 32 byte thì báo `ValueError`, và thông báo lỗi không chứa khóa (`test_c06_bad_key_rejected`, `test_c06_error_message_does_not_leak_key`). `CryptoService` cũng tự từ chối khóa khác 32 byte, vì `AESGCM` chấp nhận cả khóa 16 và 24 byte [1] (`test_h1_key_must_be_32_bytes`).
- Mất khóa là mất dữ liệu. Ba trường đã lưu chỉ giải mã được bằng đúng khóa đó (`test_c03_wrong_key`), và dự án không sao lưu khóa ở đâu khác.
- Không chạy lại `init_env.py` khi DB còn dữ liệu. Script không ghi đè `.env` đã có (`test_existing_env_is_not_overwritten`). Muốn có khóa mới thì phải tự xóa `.env`, và khóa mới không giải mã được các hàng cũ (`IntegrityFailure`; theo H1, API trả 409 `integrity_failure`).

## 6. Giới hạn của nonce ngẫu nhiên 96 bit

Mỗi lần `encrypt` lấy nonce mới bằng `os.urandom(12)`, tức 96 bit ngẫu nhiên, đúng cách sinh IV ngẫu nhiên trong NIST SP 800-38D [2, §8.2.2]. Dùng lại nonce với cùng khóa làm lộ XOR của hai plaintext và cho phép làm giả tag [2, phụ lục A], [4]. Lỗi này đã gặp ngoài thực tế: năm 2016, nhóm Böck tìm thấy 184 máy chủ HTTPS dùng lại nonce AES-GCM [5]. NIST yêu cầu xác suất trùng nonce với một khóa không vượt quá 2^-32 [2, §8].

Với nonce ngẫu nhiên, NIST giới hạn tổng số lần mã hóa bằng một khóa ở mức 2^32 [2, §8.3]. Theo bài toán ngày sinh, sau `q` lần mã hóa xác suất trùng xấp xỉ `q^2 / 2^97`. Ở `q = 2^32`, xác suất này khoảng 2^-33, vẫn dưới ngưỡng.

Mỗi lần tạo sinh viên mã hóa 3 trường, nên một khóa đủ cho khoảng 1,43 tỉ lần tạo sinh viên (2^32 / 3), chưa tính các lần cập nhật. Bản demo chỉ có vài chục bản ghi. Hệ thống thật nên đếm số lần mã hóa theo `key_version` và xoay sang khóa mới trước khi chạm ngưỡng (mục 9). Dự án chưa đếm.

`test_c02_nonce_and_ciphertext_differ` kiểm rằng cùng một plaintext mã hóa hai lần cho hai nonce và hai ciphertext khác nhau. Đột biến M1 (dùng lại một nonce cố định) bị test này bắt (mục 10).

## 7. Replay cùng hàng (A7): giới hạn đã biết

Kịch bản: kẻ tấn công ghi được vào DB nhưng không có khóa. Kẻ đó lưu lại cặp `address_ct`, `address_nonce` của SV9001, chờ sinh viên đổi địa chỉ, rồi chép cặp cũ đè vào đúng hàng, đúng cột.

Kết quả: giá trị cũ vẫn giải mã thành công, không có `IntegrityFailure`. `test_c07_replay_same_row_is_still_accepted` ghi lại đúng hành vi này. Lý do là AAD chỉ gồm `student_id`, `field`, `key_version`; ba giá trị này không đổi giữa hai lần cập nhật, nên ciphertext cũ vẫn hợp lệ ở đúng ô đó. Tráo sang hàng hoặc cột khác thì bị chặn (mục 4), còn quay về giá trị cũ của chính ô đó thì không.

Thiết kế hiện tại **không** chống được replay. C07 vì vậy là test đặc tả: nó khẳng định replay được chấp nhận, và xanh ngay từ lần chạy đầu. Nếu sau này thiết kế chặn được replay, C07 sẽ đỏ, và phải sửa test cùng mục này.

Hướng khắc phục, chưa làm:

1. Thêm số phiên bản của hàng vào AAD, tăng số này sau mỗi lần cập nhật.
2. Kiểm số phiên bản ở nơi kẻ tấn công không sửa được. Nếu số này chỉ nằm trong chính hàng đó, kẻ có quyền ghi sẽ chép lại cả số cũ lẫn ciphertext cũ.

Cách này thêm tham số vào `encrypt` và `decrypt`, tức là đổi H1, nên nằm ngoài bản demo. Trong phạm vi hiện tại, rủi ro được giảm bằng cách hạn chế quyền ghi trực tiếp vào DB.

## 8. Xác thực bằng token

API dùng hai token tĩnh lấy từ `.env`: `ADMIN_TOKEN` (đọc và ghi) và `VIEWER_TOKEN` (chỉ đọc), gửi qua header `Authorization: Bearer <token>`. Thiếu token, sai token hoặc sai scheme thì trả 401 kèm `WWW-Authenticate: Bearer`; viewer gọi route ghi thì trả 403 (`test_auth_401_without_valid_token`, `test_auth_viewer_cannot_write`, `test_auth_admin_can_write`, `test_auth_reader_accepts_viewer_and_admin`).

Token được so bằng `secrets.compare_digest` thay cho `==`. Phép `==` có thể dừng ở ký tự khác nhau đầu tiên, nên về lý thuyết thời gian so sánh lộ ra số ký tự đầu đã khớp; `compare_digest` được thiết kế để không dừng sớm theo nội dung [8]. Hai chuỗi được đổi sang bytes trước khi so, vì với kiểu `str`, `compare_digest` chỉ nhận chuỗi toàn ASCII [8]. Nếu so trên `str`, client gửi token có ký tự ngoài ASCII sẽ làm hàm ném `TypeError` và API trả 500. So trên bytes thì token đó nhận 401 như mọi token sai (`test_auth_non_ascii_token_gives_401_not_500`).

Việc dùng `compare_digest` thay cho `==` không kiểm được bằng test chức năng, vì hai cách cho cùng kết quả đúng/sai (đột biến M13, mục 10). Phần này được kiểm bằng đọc code: `app/auth.py` chỉ so token ở hàm `_same`, và hàm này gọi `secrets.compare_digest` trên bytes.

Token tĩnh chỉ đủ cho demo. Token không hết hạn, không gắn với một người dùng cụ thể, và không thu hồi riêng được. Lộ token thì phải sinh token mới trong `.env` rồi khởi động lại API, vì `get_settings()` có cache (H4).

## 9. Xoay khóa (hướng mở rộng)

Chưa có trong bản demo. Cột `key_version` (mục 3) để sẵn chỗ cho việc này:

1. Thay một khóa bằng một keyring, ví dụ `{"v1": key1, "v2": key2}`; `KEY_VERSION` chỉ phiên bản hiện hành.
2. Mọi lần mã hóa mới (tạo, cập nhật) dùng khóa hiện hành và ghi `key_version` tương ứng.
3. Khi giải mã, chọn khóa theo cột `key_version` của hàng. AAD vẫn chứa nhãn đó.
4. Một job chạy nền đọc từng hàng còn `v1`, giải mã bằng `key1`, mã hóa lại bằng `key2` với nonce mới, rồi ghi `v2`.
5. Khi không còn hàng `v1`, bỏ `key1` khỏi keyring.

Cần xoay khóa khi khóa bị lộ hoặc nghi bị lộ, và khi số lần mã hóa bằng một khóa tiến gần 2^32 (mục 6, [2, §8.3]).

Việc này đổi `CryptoService.__init__` (nhận keyring thay vì một khóa) và H4 (thêm biến cho các khóa cũ), nên phải đi qua issue hợp đồng.

## 10. Kiểm chứng

Code được viết theo TDD. Với mỗi file, test được viết trước trên bản khung chỉ có chữ ký hàm, chạy để thấy đỏ đúng lý do, rồi mới viết code cho xanh. Ở PR AES-GCM, commit test `73f5fb8` (trên bản tạm: `3 failed, 20 passed`) đứng trước commit code `2cfefa5`. Hai test là test đặc tả nên xanh ngay: `test_h1_signatures` giữ chữ ký H1, và C07 ghi lại giới hạn replay.

Bảng test và yêu cầu (47 test trong 4 file):

| Mã | Yêu cầu | Test | Số test |
|---|---|---|---|
| H1 | Chữ ký hàm, các field của `EncryptedValue`, khóa đúng 32 byte, chuỗi AAD | `test_h1_*` trong `test_crypto.py` | 6 |
| C01 | Giải mã ra đúng dữ liệu (tiếng Việt, chuỗi rỗng, chữ số), kể cả bằng một service mới cùng khóa | `test_c01_*` | 4 |
| C02 | Mỗi lần mã hóa một nonce mới; ciphertext không chứa plaintext | `test_c02_*` | 2 |
| C03 | Sai khóa: `IntegrityFailure` (A6) | `test_c03_wrong_key` | 1 |
| C04 | Sửa ciphertext, tag hoặc nonce, kể cả cắt ngắn: `IntegrityFailure` | `test_c04_*` | 7 |
| C05 | Sai `student_id`, `field` hoặc `key_version`: `IntegrityFailure` (A5) | `test_c05_*` | 3 |
| C06 | `decode_key` từ chối khóa sai, thông báo lỗi không lộ khóa | `test_c06_*` trong `test_key_manager.py` | 7 |
| C07 | Replay cùng hàng vẫn được chấp nhận (A7, giới hạn) | `test_c07_replay_same_row_is_still_accepted` | 1 |
| Auth | 401 và 403 đúng chỗ; token ngoài ASCII trả 401; token lấy từ cấu hình | `test_auth_*` trong `test_auth.py` | 10 |
| Env | `.env` có đúng 8 biến H4, giá trị dùng được, không ghi đè, không in bí mật | các test trong `test_init_env.py` | 6 |

Kết quả ngày 14/11/2026, nhánh `feature/crypto-docs`:

- `python -m pytest tests/test_key_manager.py tests/test_crypto.py tests/test_auth.py tests/test_init_env.py -q`: `47 passed`. Toàn bộ chạy được khi chưa có file nào của TV2, TV3.
- Kiểm tra đột biến: một script cài lần lượt 18 lỗi vào 4 file, mỗi lần một lỗi, chạy lại 47 test rồi trả file về như cũ. 17/18 lỗi bị ít nhất một test bắt. Lỗi còn lại, M13, được kiểm bằng đọc code (mục 8). Script này hiện chỉ có trên máy TV1, chưa đưa vào repo.
- Độ phủ (pytest-cov, có đo nhánh): 100% cho cả 4 file, gồm 90 câu lệnh và 18 nhánh.

| Mã | Lỗi cài vào | Test bắt đầu tiên |
|---|---|---|
| M1 | Dùng lại một nonce cố định | `test_c02_nonce_and_ciphertext_differ` |
| M2 | Bỏ AAD | `test_h1_known_vector_matches_aad_contract` |
| M3 | Đổi định dạng AAD | `test_h1_known_vector_matches_aad_contract` |
| M4 | Bỏ kiểm tra `key_version` | `test_c05_wrong_key_version` |
| M5 | Bỏ kiểm tra độ dài nonce | `test_c04_tampered_nonce[empty]` |
| M6 | Không đổi `InvalidTag` thành `IntegrityFailure` | `test_c03_wrong_key` |
| M7 | Bỏ qua khóa truyền vào | `test_h1_known_vector_matches_aad_contract` |
| M8 | `CryptoService` nhận khóa khác 32 byte | `test_h1_key_must_be_32_bytes[16]` |
| M9 | Bỏ kiểm tra Base64 | `test_c06_bad_key_rejected[junk_char]` |
| M10 | `decode_key` nhận khóa dài hơn 32 byte | `test_c06_bad_key_rejected[33_bytes]` |
| M11 | Lộ khóa trong thông báo lỗi | `test_c06_error_message_does_not_leak_key` |
| M12 | So token trên `str`: token ngoài ASCII gây lỗi 500 | `test_auth_non_ascii_token_gives_401_not_500` |
| M13 | So token bằng `==` | Không test nào bắt (đã biết); kiểm bằng đọc code |
| M14 | Viewer được ghi | `test_auth_viewer_cannot_write` |
| M15 | Thiếu header `WWW-Authenticate` | `test_auth_401_without_valid_token[missing]` |
| M16 | Không có token vẫn đọc được | `test_auth_401_without_valid_token[missing]` |
| M17 | Ghi đè `.env` cũ | `test_existing_env_is_not_overwritten` |
| M18 | `DATABASE_URL` không khớp mật khẩu | `test_env_values_are_usable` |

Chạy lại độ phủ (cần cài `pytest-cov`, chưa có trong `requirements.txt`):

```bash
python -m pytest --cov=app --cov=scripts --cov-branch --cov-report=term-missing tests/test_key_manager.py tests/test_crypto.py tests/test_auth.py tests/test_init_env.py
```

## 11. Ngoài phạm vi

- KMS hoặc secret vault: khóa nằm trong file `.env` trên máy chạy ứng dụng. Triển khai thật nên giữ khóa trong một dịch vụ quản lý khóa.
- TLS: API trong demo chạy HTTP, nên token và dữ liệu đã giải mã đi trên đường truyền không được mã hóa.
- Máy chạy ứng dụng hoặc khóa đã bị chiếm: ai có khóa thì giải mã được mọi trường và tạo được ciphertext hợp lệ cho giá trị tùy ý. Không biện pháp nào trong tài liệu này chống được trường hợp đó.
- Độ dài plaintext: ciphertext dài bằng plaintext cộng 16 byte [1], [2, §5.2.1.2], nên độ dài plaintext (tính theo byte UTF-8) bị lộ. Số CCCD luôn 12 chữ số nên không lộ thêm gì; địa chỉ thì lộ độ dài. Muốn giấu phải đệm plaintext về độ dài cố định; dự án không làm.
- Metadata không mã hóa: `student_id`, họ tên, ngành, số lượng bản ghi.
- Replay cùng hàng (mục 7), đếm số lần mã hóa theo khóa (mục 6) và xoay khóa (mục 9).
- Tài khoản người dùng và token có thời hạn thay cho hai token tĩnh (mục 8).

## Quyết định chờ nhóm xác nhận

Ba câu hỏi mở từ nghiên cứu W1-08 đang theo quyết định mặc định dưới đây. Nhờ người review PR xác nhận hoặc đề xuất khác.

1. Replay cùng hàng: ghi là giới hạn, kèm hướng khắc phục (mục 7). Không đổi H1 trong bản demo.
2. Lộ độ dài plaintext: ngoài phạm vi, không đệm (mục 11).
3. NIST SP 800-38D sắp được sửa: tiếp tục trích bản 2007, kiểm lại trang CSRC trước khi nộp báo cáo (ghi chú ở [2]).

## Tài liệu tham khảo

[1] Tài liệu thư viện `cryptography`, lớp `AESGCM` (key, nonce, `encrypt`, `decrypt`, `associated_data`). https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM

[2] NIST SP 800-38D (11/2007), *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC*. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf. Trang CSRC (https://csrc.nist.gov/pubs/sp/800/38/d/final) có ghi chú ngày 06/03/2024 rằng NIST quyết định sửa tài liệu này. Kiểm lần cuối ngày 14/11/2026: bản 2007 vẫn là bản chính thức, chưa có bản nháp mới.

[3] OWASP, *Cryptographic Storage Cheat Sheet*, các mục *Where to Perform Encryption*, *Cipher Modes*, *Key Storage*. https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html

[4] A. Joux (2006), *Authentication Failures in NIST version of GCM*. https://csrc.nist.gov/csrc/media/projects/block-cipher-techniques/documents/bcm/comments/800-38-series-drafts/gcm/joux_comments.pdf

[5] H. Böck và cộng sự (2016), *Nonce-Disrespecting Adversaries: Practical Forgery Attacks on GCM in TLS*. https://eprint.iacr.org/2016/475

[6] Tài liệu PostgreSQL 17, mục *Encryption Options*. https://www.postgresql.org/docs/17/encryption-options.html

[7] Microsoft Learn, *Transparent Data Encryption (TDE)* (SQL Server). https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/transparent-data-encryption

[8] Tài liệu Python, `hmac.compare_digest` (tài liệu của `secrets.compare_digest` dẫn sang mục này). https://docs.python.org/3/library/hmac.html#hmac.compare_digest
