# Kế hoạch thực hiện – TV1: Mật mã, Khóa & Xác thực (làm theo TDD)

> Nguồn: `Ke_hoach_Database_Encryption_3_thanh_vien_v4.docx` (bản 4: việc của mỗi người làm và kiểm được độc lập; bản 3: nhóm tự viết mã nguồn).
> Nhánh: `sprint0/skeleton` (ngày 1–2), sau đó `feature/crypto`. Thời gian: 4 tuần.
> Repo: https://github.com/world-ender1/database-encryption-lab (Private, TV1 là chủ, tài khoản `world-ender1`).
> Làm lần lượt từ Bước 0 đến Bước 22. Mỗi bước có điều kiện “Xong khi”; chưa đạt thì chưa sang bước sau.
> Mọi bước có code đều làm theo TDD: **viết test trước, thấy test đỏ, rồi mới viết code cho xanh** (mục 3).
> Mọi đoạn code, số test và kết quả đỏ/xanh trong file này đã được chạy thử với Python 3.12, cryptography 50, FastAPI 0.162.

---

## 1. Vai trò

TV1 viết module mã hóa AES-256-GCM cho 3 trường nhạy cảm (`national_id`, `phone`, `address`), phần sinh và nạp khóa, và phần xác thực token admin/viewer cho API. Ngoài code, TV1 viết Chương 1–2 của báo cáo và ghép báo cáo, slide của cả nhóm.

TV1 còn là **chủ repo** (việc này chuyển từ TV3 sang): tạo repo, mời TV2 và TV3 làm collaborator, bật và chỉnh branch protection cho `main`. Repo nằm trên tài khoản cá nhân nên chỉ chủ repo sửa được Settings; TV3 cần đổi gì trong Settings thì báo TV1.

### File TV1 sở hữu (chỉ TV1 sửa)

| File | Nội dung |
|---|---|
| `app/key_manager.py` | `decode_key()`: giải mã Base64, kiểm tra đúng 32 byte |
| `app/crypto_service.py` | `EncryptedValue`, `IntegrityFailure`, `CryptoService.encrypt/decrypt` |
| `app/auth.py` | `require_admin`, `require_reader`: trả 401/403 |
| `scripts/init_env.py` | Sinh `.env` cục bộ theo H4 |
| `.env.example` | Mẫu `.env`, không có giá trị thật |
| `tests/test_key_manager.py` | C06: `decode_key` (7 test) |
| `tests/test_crypto.py` | Hợp đồng H1 và C01–C05 (23 test), thêm C07 ở tuần 2 |
| `tests/test_auth.py` | 401/403 của `require_reader`, `require_admin` (10 test) |
| `tests/test_init_env.py` | `init_env.py` và `.env.example` (6 test) |
| `docs/crypto_design.md` | Thiết kế mã hóa, `key_version`, giới hạn nonce, replay, key rotation |

`tests/test_security.py` của TV3 kiểm lại 401/403 ở mức API thật; `tests/test_auth.py` của TV1 kiểm riêng `auth.py` trên một app nhỏ, không cần DB.

### Hợp đồng liên quan

**H1 – Mật mã & xác thực** (TV1 là chủ; TV2, TV3 dùng). Sau Sprint 0 không đổi nếu chưa có issue được cả ba đồng ý. `tests/test_crypto.py` và `tests/test_auth.py` là bản “chạy được” của H1: muốn biết hành vi chính xác thì đọc test.

```python
# app.key_manager
key = decode_key(encoded_key: str) -> bytes   # Base64 sai / khác 32 byte: raise ValueError

# app.crypto_service
crypto = CryptoService(key: bytes, key_version: str = "v1")
ev = crypto.encrypt(value: str, student_id: str, field: str)
# ev.ciphertext: bytes (dữ liệu + tag 16 byte); ev.nonce: bytes (12 byte); ev.key_version: str
value = crypto.decrypt(ev: EncryptedValue, student_id: str, field: str)
# Sai key/nonce/AAD/ciphertext: raise IntegrityFailure
# AAD = UTF8(f"student:{student_id}|field:{field}|key:{key_version}")

# app.auth (FastAPI dependency, dùng với Depends)
require_admin    # thiếu/sai token → 401; token viewer → 403
require_reader   # admin hoặc viewer; thiếu/sai token → 401
```

**H4 – Cấu hình `.env`** (TV2 là chủ; TV1 dùng cho `init_env.py`, `.env.example`, `auth.py`):
`DATABASE_URL`, `POSTGRES_PASSWORD`, `ENCRYPTION_KEY_B64`, `KEY_VERSION`, `ADMIN_TOKEN`, `VIEWER_TOKEN`, `API_PORT` (8000), `DB_PORT` (55432).

### Cần gì từ người khác

| Cần gì | Từ ai | Khi nào |
|---|---|---|
| Tên tài khoản GitHub để mời collaborator | TV2, TV3 | Sáng ngày 1 (Bước 0) |
| Tên job CI (`pytest`) đã chạy lần đầu, để bật “Require status checks” | TV3 | Ngày 2 (Bước 7) |
| Chốt tên field H4 `admin_token`, `viewer_token` trong `Settings` (cho `auth.py`). Chỉ cần chốt tên, **không chờ file** `config.py`: `auth.py` không import nó lúc import | TV2 | Họp Sprint 0 (Bước 1) |
| `cryptography`, `fastapi` có trong `requirements.txt` | TV3 | Sprint 0 |
| Review PR crypto | TV2 | Tuần 1–2 |
| Chương 3–4 (TV2), Chương 5 (TV3) để ghép báo cáo | TV2, TV3 | Cuối tuần 3 |

---

## 2. Lịch tổng quát

| Thời gian | Bước | Mốc |
|---|---|---|
| Ngày 1–2 (Sprint 0) | 0–7 | Repo đã tạo; khung TV1 và 4 file test nằm trên `sprint0/skeleton` (43 passed, 3 xfailed); PR Sprint 0 merge |
| Tuần 1 (ngày 3–7) | 8–11 | AES-GCM thật (đỏ → xanh, 46 passed), kiểm tra đột biến đạt, PR crypto mở |
| Tuần 2 | 12–15 | C07, `crypto_design.md`, review PR api-db; PR crypto đã merge |
| Tuần 3 | 16–19 | Kiểm tra trên PostgreSQL, sửa lỗi (test tái hiện trước), nháp Chương 1–2 |
| Tuần 4 | 20–22 | Slide, ghép báo cáo và slide, tổng duyệt |

---

## 3. Cách làm TDD

Mỗi bước có code đi theo một chu kỳ:

1. **Đỏ** – Viết test trước. Tạo file code dạng *skeleton*: đủ import, class, chữ ký hàm, thân hàm chỉ có `raise NotImplementedError`. Chạy test và xem nó đỏ **đúng lý do**: `NotImplementedError` hoặc `AssertionError`. Nếu thấy `ImportError`, `SyntaxError` hay `ERROR collecting` thì là đỏ sai lý do: sửa skeleton hoặc test trước đã.
2. **Xanh** – Viết code vừa đủ để test xanh. Không viết thêm chức năng mà chưa có test đòi.
3. **Dọn** – Sửa cho gọn (tên biến, comment, bỏ code thừa), chạy lại, vẫn phải xanh.

Quy tắc:

- Test nào cũng phải được thấy đỏ ít nhất một lần. Test chưa từng đỏ có thể là test không kiểm gì.
- Không sửa test để nó xanh. Test chỉ đổi khi H1 đổi (qua issue).
- Luôn chạy `python -m pytest` từ thư mục gốc repo (không gõ `pytest` trần) để import được `app` và `scripts`.
- Commit khi xanh. Ngoại lệ có chủ đích: Bước 9 commit riêng phần test đỏ trên nhánh chưa push, để lịch sử cho thấy test có trước code.
- Ghi lại dòng kết quả đỏ và xanh của mỗi bước vào ghi chú cá nhân; dùng cho báo cáo (phần kiểm thử).

**Bản tạm và `xfail`.** Sprint 0 chỉ có bản tạm (chưa mã hóa thật) để TV2, TV3 làm song song. Ba test chỉ đạt được với AES-GCM thật được đánh dấu `xfail(strict=True)`: pytest ghi `xfailed` chứ không báo lỗi, nên CI vẫn xanh. `strict=True` nghĩa là nếu test bỗng đạt thì pytest báo lỗi, buộc phải gỡ marker. Bước 9 gỡ marker: đó chính là bước đỏ của AES-GCM.

**Bốn lớp kiểm chứng** để biết chắc code đúng:

| Lớp | Kiểm cái gì | Ở bước |
|---|---|---|
| Test đơn vị (TDD) | Code làm đúng hợp đồng H1, H4 | 3–6, 9 |
| Kiểm tra đột biến (`tmp_mutants.py`) | Test đủ mạnh: cố ý cài 18 lỗi vào code, test phải bắt được 17 (lỗi thứ 18 kiểm bằng đọc code) | 10 |
| Coverage | Không có dòng/nhánh nào của TV1 mà test không chạy qua (mục tiêu 100%) | 10 |
| CI + `test_security.py` (TV3) + chạy thật trên PostgreSQL | Code của TV1 chạy đúng khi ghép với API và DB | 7, 11, 16 |

---

## 4. Các bước theo thứ tự

> Ngày 1–7 (Bước 0–11) đã được tách thành đầu việc W1-00…W1-12, có checklist và tiêu chí hoàn thành, trong `Ke_hoach_TV1_tuan_1.md`. Script kiểm tra đột biến `tmp_mutants.py` nằm ở mục 5 của file đó.

### Sprint 0 (ngày 1–2)

#### Bước 0. Tạo repo (sáng ngày 1, trước họp)

- [x] Tạo repo `world-ender1/database-encryption-lab`, Private, không có README tự sinh.
- [x] Đẩy `README.md` tạm và `.gitignore` (nội dung theo Bước 1 cũ của TV3) lên `main` bằng commit `chore: init repository`; tạo và push nhánh `sprint0/skeleton`.
- [x] Bật branch protection cho `main`: bắt buộc PR, 1 review. Mục “CI pass” bật ở Bước 7, sau khi CI của TV3 chạy lần đầu.
- [ ] Mời TV2, TV3 vào Settings → Collaborators (cần tên tài khoản GitHub của hai bạn).

Trên máy TV1, repo nằm ở `C:\mat ma\database-encryption-lab`. Riêng repo này đã cấu hình để git dùng token của tài khoản `world-ender1` (lấy từ `gh auth token --user world-ender1`), nên không cần đổi tài khoản đang active trong `gh`.

**Xong khi:** TV2, TV3 clone được repo và thấy nhánh `sprint0/skeleton`.

#### Bước 1. Họp chốt hợp đồng (cả nhóm, TV3 chủ trì)

- [ ] Trình bày H1: chữ ký hàm, khi nào raise `IntegrityFailure`, chuỗi AAD.
- [ ] Chốt tên field dùng trong AAD: đúng `"national_id"`, `"phone"`, `"address"`.
- [ ] Chốt với TV2: `app/config.py` cung cấp `get_settings()` (có cache), `Settings` có field viết thường `admin_token`, `viewer_token`, `encryption_key_b64`, `key_version`, `database_url`. Báo TV2: `auth.py` chỉ gọi `get_settings()` khi chạy (qua `get_token_settings()`), không import lúc import, nên TV1 không chờ `config.py`.
- [ ] Chốt với TV2 định dạng `DATABASE_URL`: `postgresql+psycopg://demo:<POSTGRES_PASSWORD>@127.0.0.1:<DB_PORT>/encryption_demo`.
- [ ] Báo TV3 thêm `cryptography` vào `requirements.txt`.
- [ ] Báo nhóm: TV1 làm TDD, PR Sprint 0 có thêm 4 file test của TV1; 3 test `xfail` (chờ AES-GCM) sẽ hiện trong CI là `xfailed`, không phải lỗi.

**Xong khi:** cả ba thống nhất H1–H5, có ghi lại (issue hoặc file ghi chú chung).

#### Bước 2. Lấy repo và chuyển sang nhánh chung

TV1 tạo repo ở Bước 0 nên đã có sẵn bản trên máy; chỉ cần:

```bash
cd "C:\mat ma\database-encryption-lab"
git switch sprint0/skeleton
py -3 -m venv .venv
```

Máy khác thì clone: `git clone https://github.com/world-ender1/database-encryption-lab.git`.

**Xong khi:** đang ở nhánh `sprint0/skeleton`, venv đã tạo.

#### Bước 3. `app/key_manager.py` (TDD)

**3a. Đỏ** – viết test, rồi skeleton:

```python
# tests/test_key_manager.py
import base64

import pytest

from app.key_manager import decode_key

KEY = bytes(range(32))


def b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def test_c06_valid_key_decodes_to_32_bytes():
    assert decode_key(b64(KEY)) == KEY


@pytest.mark.parametrize(
    "bad",
    ["not-base64!!", "", b64(bytes(16)), b64(bytes(33)), b64(KEY) + "!"],
    ids=["not_base64", "empty", "16_bytes", "33_bytes", "junk_char"],
)
def test_c06_bad_key_rejected(bad):
    with pytest.raises(ValueError):
        decode_key(bad)


def test_c06_error_message_does_not_leak_key():
    bad = b64(b"SECRET-KEY-16B!!")
    with pytest.raises(ValueError) as exc:
        decode_key(bad)
    assert bad not in str(exc.value)
    assert "SECRET" not in str(exc.value)
```

```python
# app/key_manager.py  (SKELETON – bước đỏ)
KEY_SIZE = 32


def decode_key(encoded_key: str) -> bytes:
    """Giải mã ENCRYPTION_KEY_B64. Sai Base64 hoặc khác 32 byte: raise ValueError."""
    raise NotImplementedError
```

`python -m pytest tests/test_key_manager.py -q` → **`7 failed`**, cả 7 đều `NotImplementedError`.

Vì sao có từng test: `33_bytes` bắt lỗi viết `<` thay cho `!=`; `junk_char` (key đúng + một ký tự rác) bắt lỗi quên `validate=True`, vì không có nó Base64 tự bỏ ký tự rác và trả key như bình thường; test cuối bắt việc lộ key trong thông báo lỗi.

**3b. Xanh:**

```python
# app/key_manager.py
import base64
import binascii

KEY_SIZE = 32


def decode_key(encoded_key: str) -> bytes:
    """Giải mã ENCRYPTION_KEY_B64. Sai Base64 hoặc khác 32 byte: raise ValueError."""
    try:
        key = base64.b64decode(encoded_key, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("ENCRYPTION_KEY_B64 không phải Base64 hợp lệ") from exc
    if len(key) != KEY_SIZE:
        raise ValueError(f"Key phải đúng {KEY_SIZE} byte, nhận được {len(key)} byte")
    return key
```

**Xong khi:** đã thấy `7 failed` (đỏ đúng lý do), sau đó `python -m pytest tests/test_key_manager.py -q` → `7 passed`.

#### Bước 4. `app/crypto_service.py` – bản tạm (TDD)

**4a. Đỏ** – viết toàn bộ test hợp đồng H1, rồi skeleton.

```python
# tests/test_crypto.py
import dataclasses
import inspect

import pytest

from app.crypto_service import CryptoService, EncryptedValue, IntegrityFailure

KEY = bytes(range(32))
OTHER_KEY = bytes(32)

# Bản tạm Sprint 0 chưa mã hóa thật nên 3 test đánh dấu dưới đây chưa thể đạt.
# strict=True: nếu test bỗng đạt thì pytest báo lỗi, buộc phải gỡ marker.
# Gỡ marker ở W1-09 – đó là bước "đỏ" trước khi viết AES-GCM.
needs_real_crypto = pytest.mark.xfail(strict=True, reason="Bản tạm Sprint 0 chưa mã hóa thật – gỡ ở W1-09")


@pytest.fixture
def crypto():
    return CryptoService(KEY, "v1")


def flip(data: bytes, pos: int) -> bytes:
    out = bytearray(data)
    out[pos] ^= 0x01
    return bytes(out)


# ---------- H1: hình dạng hợp đồng ----------

def test_h1_signatures():
    init = inspect.signature(CryptoService.__init__).parameters
    assert list(init) == ["self", "key", "key_version"]
    assert init["key_version"].default == "v1"
    assert list(inspect.signature(CryptoService.encrypt).parameters) == ["self", "value", "student_id", "field"]
    assert list(inspect.signature(CryptoService.decrypt).parameters) == ["self", "ev", "student_id", "field"]


def test_h1_encrypted_value_layout(crypto):
    ev = crypto.encrypt("Ha Noi", "SV9001", "address")
    assert [f.name for f in dataclasses.fields(EncryptedValue)] == ["ciphertext", "nonce", "key_version"]
    assert len(ev.nonce) == 12
    assert len(ev.ciphertext) == len("Ha Noi".encode("utf-8")) + 16
    assert ev.key_version == "v1"
    with pytest.raises(dataclasses.FrozenInstanceError):
        ev.nonce = bytes(12)


@pytest.mark.parametrize("size", [16, 31, 33])
def test_h1_key_must_be_32_bytes(size):
    with pytest.raises(ValueError):
        CryptoService(bytes(size))


@needs_real_crypto
def test_h1_known_vector_matches_aad_contract(crypto):
    # AES-256-GCM, key = bytes(range(32)), nonce = bytes(range(12)),
    # AAD = b"student:SV9001|field:address|key:v1", plaintext = "Ha Noi".
    # Ciphertext + tag tính sẵn; đổi định dạng AAD là test này đỏ.
    ev = EncryptedValue(bytes.fromhex("0f63f655aa8ccd733631070afa0ddf496bfbad142ec5"), bytes(range(12)), "v1")
    assert crypto.decrypt(ev, "SV9001", "address") == "Ha Noi"


# ---------- C01: mã hóa rồi giải mã ra đúng dữ liệu ----------

@pytest.mark.parametrize("text", ["Hà Nội – Phường Giả Lập", "", "012345678901"],
                         ids=["vietnamese", "empty", "digits"])
def test_c01_roundtrip(crypto, text):
    ev = crypto.encrypt(text, "SV9001", "address")
    assert crypto.decrypt(ev, "SV9001", "address") == text


def test_c01_new_instance_with_same_key_can_decrypt(crypto):
    ev = crypto.encrypt("0901234567", "SV9001", "phone")
    assert CryptoService(KEY, "v1").decrypt(ev, "SV9001", "phone") == "0901234567"


# ---------- C02: mỗi lần mã hóa một nonce mới, không lộ plaintext ----------

def test_c02_nonce_and_ciphertext_differ(crypto):
    a = crypto.encrypt("0901234567", "SV9001", "phone")
    b = crypto.encrypt("0901234567", "SV9001", "phone")
    assert a.nonce != b.nonce
    assert a.ciphertext != b.ciphertext


@needs_real_crypto
def test_c02_ciphertext_hides_plaintext(crypto):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    assert b"012345678901" not in ev.ciphertext


# ---------- C03: sai key ----------

@needs_real_crypto
def test_c03_wrong_key(crypto):  # A6
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        CryptoService(OTHER_KEY, "v1").decrypt(ev, "SV9001", "national_id")


# ---------- C04: dữ liệu lưu bị sửa ----------

@pytest.mark.parametrize("mutate", [
    lambda ct: flip(ct, 0),    # byte đầu ciphertext
    lambda ct: flip(ct, -1),   # byte cuối của tag
    lambda ct: ct[:10],        # bị cắt, ngắn hơn tag
    lambda ct: b"",            # rỗng
], ids=["first_byte", "last_tag_byte", "truncated", "empty"])
def test_c04_tampered_ciphertext(crypto, mutate):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(dataclasses.replace(ev, ciphertext=mutate(ev.ciphertext)), "SV9001", "national_id")


@pytest.mark.parametrize("mutate", [
    lambda n: flip(n, 0),
    lambda n: n[:11],
    lambda n: b"",
], ids=["flipped", "11_bytes", "empty"])
def test_c04_tampered_nonce(crypto, mutate):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(dataclasses.replace(ev, nonce=mutate(ev.nonce)), "SV9001", "national_id")


# ---------- C05: sai AAD (tráo hàng, tráo cột, sai key_version) ----------

@pytest.mark.parametrize("sid, field", [("SV9002", "national_id"), ("SV9001", "phone")],
                         ids=["other_student", "other_field"])
def test_c05_wrong_aad(crypto, sid, field):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(ev, sid, field)


def test_c05_wrong_key_version(crypto):
    ev = crypto.encrypt("012345678901", "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        crypto.decrypt(dataclasses.replace(ev, key_version="v2"), "SV9001", "national_id")
    with pytest.raises(IntegrityFailure):
        CryptoService(KEY, "v2").decrypt(ev, "SV9001", "national_id")
```

Vì sao có những test không có trong bảng C01–C06 ban đầu (mỗi test bắt một lỗi thật mà test cũ bỏ lọt, đã thử bằng kiểm tra đột biến):

| Test | Bắt lỗi gì |
|---|---|
| `test_h1_known_vector_matches_aad_contract` | Đổi định dạng chuỗi AAD. Roundtrip vẫn đúng nên các test khác không thấy, nhưng dữ liệu cũ trong DB sẽ không giải mã được nữa |
| `test_c01_new_instance_with_same_key_can_decrypt` | Code tự sinh key ngẫu nhiên thay vì dùng key truyền vào: cùng một instance vẫn giải mã được, nhưng khởi động lại API là mất dữ liệu |
| `test_c04_tampered_nonce[empty]` | Quên kiểm tra độ dài nonce: AESGCM ném `ValueError` (không phải `InvalidTag`) với nonce dưới 8 byte, API sẽ trả 500 thay vì 409 |
| `test_h1_key_must_be_32_bytes[16]` | Quên kiểm tra 32 byte trong `CryptoService`: AESGCM nhận cả key 16 byte (AES-128) mà không báo lỗi |
| Vế thứ hai của `test_c05_wrong_key_version` | Bỏ kiểm tra `key_version`: service `v2` giải mã được dữ liệu `v1` vì AAD lấy `key_version` từ chính `ev` |

```python
# app/crypto_service.py  (SKELETON – bước đỏ)
from dataclasses import dataclass

NONCE_SIZE = 12
TAG_SIZE = 16


class IntegrityFailure(Exception):
    """Giải mã thất bại: sai key, nonce, AAD hoặc dữ liệu đã bị sửa."""


@dataclass(frozen=True)
class EncryptedValue:
    ciphertext: bytes
    nonce: bytes
    key_version: str


class CryptoService:
    def __init__(self, key: bytes, key_version: str = "v1") -> None:
        raise NotImplementedError

    def encrypt(self, value: str, student_id: str, field: str) -> EncryptedValue:
        raise NotImplementedError

    def decrypt(self, ev: EncryptedValue, student_id: str, field: str) -> str:
        raise NotImplementedError
```

`python -m pytest tests/test_crypto.py -q` → **`3 failed, 1 passed, 3 xfailed, 16 errors`**, tất cả do `NotImplementedError`:

- `1 passed` là `test_h1_signatures`: skeleton đã đúng chữ ký. Đây là test giữ hợp đồng, xanh ngay là bình thường.
- `16 errors`: fixture `crypto` gọi `CryptoService(...)` bị lỗi ngay lúc chuẩn bị test; pytest tính là *error*, vẫn là đỏ đúng lý do.

**4b. Xanh** – bản tạm: đúng chữ ký H1 nhưng **chưa mã hóa thật**. “Tag” SHA-256 tính trên nonce + AAD + dữ liệu giúp vẫn raise `IntegrityFailure` khi dữ liệu bị sửa hoặc bị tráo hàng, nên TV2 chạy được API và TV3 viết được test 409 ngay tuần 1.

```python
# app/crypto_service.py  (BẢN TẠM SPRINT 0)
# BẢN TẠM SPRINT 0 – KHÔNG MÃ HÓA THẬT – KHÔNG DÙNG ĐỂ DEMO
import hashlib
import hmac
import os
from dataclasses import dataclass

NONCE_SIZE = 12
TAG_SIZE = 16


class IntegrityFailure(Exception):
    """Giải mã thất bại: sai key, nonce, AAD hoặc dữ liệu đã bị sửa."""


@dataclass(frozen=True)
class EncryptedValue:
    ciphertext: bytes
    nonce: bytes
    key_version: str


class CryptoService:
    def __init__(self, key: bytes, key_version: str = "v1") -> None:
        if len(key) != 32:
            raise ValueError("Key phải đúng 32 byte")
        self.key_version = key_version

    @staticmethod
    def _aad(student_id: str, field: str, key_version: str) -> bytes:
        return f"student:{student_id}|field:{field}|key:{key_version}".encode("utf-8")

    @staticmethod
    def _fake_tag(nonce: bytes, aad: bytes, data: bytes) -> bytes:
        return hashlib.sha256(nonce + aad + data).digest()[:TAG_SIZE]

    def encrypt(self, value: str, student_id: str, field: str) -> EncryptedValue:
        nonce = os.urandom(NONCE_SIZE)
        data = value.encode("utf-8")
        aad = self._aad(student_id, field, self.key_version)
        return EncryptedValue(data + self._fake_tag(nonce, aad, data), nonce, self.key_version)

    def decrypt(self, ev: EncryptedValue, student_id: str, field: str) -> str:
        if ev.key_version != self.key_version or len(ev.ciphertext) < TAG_SIZE:
            raise IntegrityFailure("Authentication failed")
        data, tag = ev.ciphertext[:-TAG_SIZE], ev.ciphertext[-TAG_SIZE:]
        aad = self._aad(student_id, field, ev.key_version)
        if not hmac.compare_digest(tag, self._fake_tag(ev.nonce, aad, data)):
            raise IntegrityFailure("Authentication failed")
        return data.decode("utf-8")
```

**Xong khi:** đã thấy đỏ như trên, sau đó `python -m pytest tests/test_crypto.py -q -rx` → `20 passed, 3 xfailed`, và 3 test `XFAIL` đúng là `test_h1_known_vector_matches_aad_contract`, `test_c02_ciphertext_hides_plaintext`, `test_c03_wrong_key`.

#### Bước 5. `app/auth.py` (TDD)

**Không cần `app/config.py` của TV2.** `auth.py` chỉ cần hai giá trị `admin_token`, `viewer_token` (tên field H4 đã chốt ở Bước 1), không cần cả file. Hàm `get_token_settings()` trong `auth.py` import `app.config` **trong thân hàm**, nên import `app.auth` và chạy test không cần `config.py`; lúc chạy thật hàm này gọi `get_settings()` của TV2. Test dùng một app FastAPI nhỏ và `dependency_overrides` để thay `get_token_settings`, nên không cần `.env`, DB hay `config.py`. (Bản đầu của kế hoạch import thẳng `app.config` và bắt TV1 chờ TV2; đã sửa ngày 13/11/2026.)

**5a. Đỏ:**

```python
# tests/test_auth.py
import sys
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import get_token_settings, require_admin, require_reader

ADMIN = "admin-token-123"
VIEWER = "viewer-token-456"


@pytest.fixture
def client():
    # App nhỏ chỉ để thử auth; không cần DB, không đọc .env, không cần app/config.py của TV2.
    app = FastAPI()

    @app.get("/read")
    def read(role: str = Depends(require_reader)):
        return {"role": role}

    @app.delete("/write")
    def write(role: str = Depends(require_admin)):
        return {"role": role}

    app.dependency_overrides[get_token_settings] = lambda: SimpleNamespace(admin_token=ADMIN, viewer_token=VIEWER)
    return TestClient(app)


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("headers", [
    {},
    bearer("sai-token"),
    {"Authorization": "Basic YWRtaW46YWRtaW4="},
    {"Authorization": "Bearer "},
    bearer(ADMIN[:-1]),
], ids=["missing", "wrong_token", "basic_scheme", "empty_token", "admin_prefix"])
def test_auth_401_without_valid_token(client, headers):
    for r in (client.get("/read", headers=headers), client.delete("/write", headers=headers)):
        assert r.status_code == 401
        assert r.headers["www-authenticate"] == "Bearer"


def test_auth_reader_accepts_viewer_and_admin(client):
    assert client.get("/read", headers=bearer(VIEWER)).json() == {"role": "viewer"}
    assert client.get("/read", headers=bearer(ADMIN)).json() == {"role": "admin"}


def test_auth_viewer_cannot_write(client):
    assert client.delete("/write", headers=bearer(VIEWER)).status_code == 403


def test_auth_admin_can_write(client):
    r = client.delete("/write", headers=bearer(ADMIN))
    assert r.status_code == 200
    assert r.json() == {"role": "admin"}


def test_auth_non_ascii_token_gives_401_not_500(client):
    r = client.get("/read", headers={"Authorization": "Bearer t\u00e9st".encode("latin-1")})
    assert r.status_code == 401


def test_auth_tokens_come_from_app_config(monkeypatch):
    # Lúc chạy thật, token lấy từ app.config.get_settings() (H4, TV2).
    # Dùng module giả thay app.config nên test không cần file config.py của TV2.
    fake_config = ModuleType("app.config")
    fake_config.get_settings = lambda: SimpleNamespace(admin_token=ADMIN, viewer_token=VIEWER)
    monkeypatch.setitem(sys.modules, "app.config", fake_config)
    settings = get_token_settings()
    assert (settings.admin_token, settings.viewer_token) == (ADMIN, VIEWER)
```

```python
# app/auth.py  (SKELETON – bước đỏ)
from typing import Literal, Protocol

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

Role = Literal["admin", "viewer"]
_bearer = HTTPBearer(auto_error=False)


class TokenSettings(Protocol):
    """Hai field H4 mà auth cần. `Settings` của TV2 có sẵn hai field này."""

    admin_token: str
    viewer_token: str


def get_token_settings() -> TokenSettings:
    raise NotImplementedError


def require_reader(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: TokenSettings = Depends(get_token_settings),
) -> Role:
    raise NotImplementedError


def require_admin(role: Role = Depends(require_reader)) -> Role:
    raise NotImplementedError
```

`python -m pytest tests/test_auth.py -q` → **`10 failed`**, đều `NotImplementedError`. Có thể kèm `1 warning` (`StarletteDeprecationWarning` về `httpx`) – cảnh báo của thư viện, không phải lỗi.

`test_auth_non_ascii_token_gives_401_not_500` là test dẫn tới quyết định so sánh trên **bytes**: `secrets.compare_digest` trên hai `str` có ký tự ngoài ASCII sẽ ném `TypeError` → API trả 500.

`test_auth_tokens_come_from_app_config` giữ đường chạy thật: `get_token_settings()` phải lấy token từ `app.config.get_settings()`. Test đặt một module giả vào `sys.modules["app.config"]`, nên vẫn chạy khi chưa có `config.py` của TV2.

**5b. Xanh:**

- `HTTPBearer(auto_error=False)` để tự quyết định mã lỗi, không phụ thuộc phiên bản FastAPI.
- So token bằng `secrets.compare_digest` trên bytes.
- `get_token_settings()` import `app.config` trong thân hàm.

```python
# app/auth.py
import secrets
from typing import Literal, Protocol

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

Role = Literal["admin", "viewer"]
_bearer = HTTPBearer(auto_error=False)


class TokenSettings(Protocol):
    """Hai field H4 mà auth cần. `Settings` của TV2 có sẵn hai field này."""

    admin_token: str
    viewer_token: str


def get_token_settings() -> TokenSettings:
    """Lấy token từ cấu hình H4 (`app.config` của TV2).

    Import trong thân hàm: import `app.auth` không cần `config.py`, nên TV1 viết và test
    `auth.py` độc lập với TV2. Test thay hàm này bằng `dependency_overrides`.
    """
    from app.config import get_settings

    return get_settings()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _same(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def require_reader(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: TokenSettings = Depends(get_token_settings),
) -> Role:
    if creds is None:
        raise _unauthorized()
    if _same(creds.credentials, settings.admin_token):
        return "admin"
    if _same(creds.credentials, settings.viewer_token):
        return "viewer"
    raise _unauthorized()


def require_admin(role: Role = Depends(require_reader)) -> Role:
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return role
```

Test hành vi không phân biệt được `compare_digest` với `==` (khác nhau ở thời gian so sánh, không ở kết quả), nên phần này kiểm bằng đọc code:
`python -c "s = open('app/auth.py', encoding='utf-8').read(); assert 'compare_digest' in s and 'auto_error=False' in s; print('ok')"` → `ok`.

Cách TV2 dùng (để ghi vào H1 cho rõ):

```python
@app.delete("/students/{student_id}", status_code=204, dependencies=[Depends(require_admin)])
@app.get("/students", dependencies=[Depends(require_reader)])
```

Muốn thay token trong test (của bất kỳ ai): override `app.auth.get_token_settings`, không override `get_settings`. `conftest.py` của TV3 đặt biến môi trường trước khi import app nên không cần sửa gì.

**Xong khi:** đã thấy `10 failed`, sau đó `python -m pytest tests/test_auth.py -q` → `10 passed`; lệnh kiểm tĩnh in `ok`; không có `app/config.py` mà `python -c "import app.auth"` vẫn chạy.

#### Bước 6. `scripts/init_env.py` và `.env.example` (TDD)

Không ghi đè `.env` đã có: key mới không giải mã được dữ liệu cũ, và mật khẩu mới không khớp volume DB đã tạo.

TDD dẫn tới một thay đổi thiết kế so với bản cũ: `main()` nhận tham số `env_path` (mặc định là `.env` ở gốc repo) để test ghi vào thư mục tạm, không đụng `.env` thật.

**6a. Đỏ:**

```python
# tests/test_init_env.py
from pathlib import Path

import pytest
from dotenv import dotenv_values

from app.key_manager import decode_key
from scripts import init_env

H4 = {"DATABASE_URL", "POSTGRES_PASSWORD", "ENCRYPTION_KEY_B64", "KEY_VERSION",
      "ADMIN_TOKEN", "VIEWER_TOKEN", "API_PORT", "DB_PORT"}
SECRETS = ("ENCRYPTION_KEY_B64", "ADMIN_TOKEN", "VIEWER_TOKEN", "POSTGRES_PASSWORD")
ENV_EXAMPLE = Path(__file__).resolve().parent.parent / ".env.example"


@pytest.fixture
def env_file(tmp_path):
    path = tmp_path / ".env"
    assert init_env.main(path) == 0
    return path


def test_env_has_exactly_h4_vars(env_file):
    assert set(dotenv_values(env_file)) == H4


def test_env_values_are_usable(env_file):
    e = dotenv_values(env_file)
    assert len(decode_key(e["ENCRYPTION_KEY_B64"])) == 32
    assert (e["KEY_VERSION"], e["API_PORT"], e["DB_PORT"]) == ("v1", "8000", "55432")
    assert e["DATABASE_URL"] == (
        f"postgresql+psycopg://demo:{e['POSTGRES_PASSWORD']}@127.0.0.1:55432/encryption_demo")
    assert e["ADMIN_TOKEN"] != e["VIEWER_TOKEN"]
    assert all(len(e[k]) >= 32 for k in ("ADMIN_TOKEN", "VIEWER_TOKEN", "POSTGRES_PASSWORD"))


def test_existing_env_is_not_overwritten(env_file, capsys):
    before = env_file.read_bytes()
    assert init_env.main(env_file) == 0
    assert env_file.read_bytes() == before
    assert "already exists" in capsys.readouterr().out


def test_each_run_generates_new_secrets(tmp_path):
    a, b = tmp_path / "a.env", tmp_path / "b.env"
    init_env.main(a)
    init_env.main(b)
    ea, eb = dotenv_values(a), dotenv_values(b)
    assert all(ea[k] != eb[k] for k in SECRETS)


def test_output_is_ascii_and_has_no_secret(tmp_path, capsys):
    path = tmp_path / ".env"
    init_env.main(path)
    out = capsys.readouterr().out
    assert out.isascii()
    e = dotenv_values(path)
    assert not any(e[k] in out for k in SECRETS)


def test_env_example_has_h4_vars_without_real_values():
    example = dotenv_values(ENV_EXAMPLE)
    assert set(example) == H4
    assert all(example[k].startswith("<") for k in SECRETS)
```

```python
# scripts/init_env.py  (SKELETON – bước đỏ)
"""Sinh .env cục bộ cho demo. Không ghi đè nếu .env đã tồn tại."""
import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def main(env_path: Path = ENV_PATH) -> int:
    raise NotImplementedError


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
```

Chưa tạo `.env.example`. `python -m pytest tests/test_init_env.py -q` → **`3 failed, 3 errors`**: 5 test do `NotImplementedError`, `test_env_example_...` do `AssertionError` (chưa có file).

`test_output_is_ascii_and_has_no_secret` giữ hai yêu cầu: thông báo `print` không dấu (trên Windows, khi output bị chuyển hướng như pipe hay CI, Python dùng bảng mã cp1252 và in tiếng Việt có dấu sẽ lỗi `UnicodeEncodeError`), và không in key/token ra màn hình. Comment trong code vẫn viết tiếng Việt bình thường.

**6b. Xanh:**

```python
# scripts/init_env.py
"""Sinh .env cục bộ cho demo. Không ghi đè nếu .env đã tồn tại."""
import base64
import secrets
import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
API_PORT = 8000
DB_PORT = 55432


def main(env_path: Path = ENV_PATH) -> int:
    if env_path.exists():
        print(".env already exists - kept as is (a new key could not decrypt existing data).")
        return 0
    pg_password = secrets.token_urlsafe(24)
    lines = [
        f"ENCRYPTION_KEY_B64={base64.b64encode(secrets.token_bytes(32)).decode('ascii')}",
        "KEY_VERSION=v1",
        f"ADMIN_TOKEN={secrets.token_urlsafe(32)}",
        f"VIEWER_TOKEN={secrets.token_urlsafe(32)}",
        f"POSTGRES_PASSWORD={pg_password}",
        f"API_PORT={API_PORT}",
        f"DB_PORT={DB_PORT}",
        f"DATABASE_URL=postgresql+psycopg://demo:{pg_password}@127.0.0.1:{DB_PORT}/encryption_demo",
    ]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Created .env - do NOT commit this file.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
```

```dotenv
# .env.example  (được commit, không có giá trị thật)
ENCRYPTION_KEY_B64=<chay python scripts/init_env.py de sinh>
KEY_VERSION=v1
ADMIN_TOKEN=<sinh tu dong>
VIEWER_TOKEN=<sinh tu dong>
POSTGRES_PASSWORD=<sinh tu dong>
API_PORT=8000
DB_PORT=55432
DATABASE_URL=postgresql+psycopg://demo:<POSTGRES_PASSWORD>@127.0.0.1:55432/encryption_demo
```

Trên Windows file `.env` được ghi với dấu xuống dòng CRLF; đã thử: Docker Compose và `python-dotenv` đều đọc đúng giá trị.

**Xong khi:** đã thấy `3 failed, 3 errors`, sau đó `python -m pytest tests/test_init_env.py -q` → `6 passed`; chạy thật `python scripts/init_env.py` ở gốc repo tạo `.env`, chạy lần 2 không đổi gì; `git check-ignore .env` in ra `.env`.

#### Bước 7. Push lên nhánh chung và review PR Sprint 0

```bash
python -m pytest tests/test_key_manager.py tests/test_crypto.py tests/test_auth.py tests/test_init_env.py -q   # 43 passed, 3 xfailed
git add app/key_manager.py app/crypto_service.py app/auth.py scripts/init_env.py .env.example
git add tests/test_key_manager.py tests/test_crypto.py tests/test_auth.py tests/test_init_env.py
git status                       # chỉ có 9 file của TV1, không có .env, không có tmp_*.py
git commit -m "chore(crypto): sprint 0 skeleton – H1 interface, auth, init_env, tests"
git pull --rebase origin sprint0/skeleton
git push origin sprint0/skeleton
```

- [ ] Review PR Sprint 0 do TV3 mở: TV2 có dùng `decode_key` trong `dependencies.py` không; route khung có gắn `require_admin`/`require_reader` không.
- [ ] Khi CI của TV3 đã chạy lần đầu trên PR: Settings → Branches → rule của `main` → bật “Require status checks to pass”, chọn job `pytest`.

**Xong khi:** PR Sprint 0 đã merge vào `main` trước hết ngày 2; trên `main` test của TV1 cho `43 passed, 3 xfailed`; rule của `main` có yêu cầu check `pytest`.

### Tuần 1 (ngày 3–7)

#### Bước 8. Tạo nhánh và nghiên cứu (nửa ngày)

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/crypto
```

- [ ] AES và AEAD/GCM: tính bí mật + tag xác thực 16 byte, nonce 12 byte, AAD.
- [ ] Đọc tài liệu `AESGCM` của thư viện `cryptography`; ghi chú yêu cầu không dùng lại nonce với cùng key.
- [ ] Đọc NIST SP 800-38D phần giới hạn số lần mã hóa khi dùng nonce ngẫu nhiên (dùng ở Bước 13).

#### Bước 9. Thay bản tạm bằng AES-256-GCM (TDD)

**9a. Đỏ** – trong `tests/test_crypto.py`, xóa khối comment + dòng `needs_real_crypto = pytest.mark.xfail(...)` và 3 dòng `@needs_real_crypto`. Không sửa gì khác.

`python -m pytest tests/test_crypto.py -q -rf` → **`3 failed, 20 passed`**, mỗi test đỏ một lý do khác nhau:

| Test | Lý do đỏ trên bản tạm |
|---|---|
| `test_h1_known_vector_matches_aad_contract` | `IntegrityFailure`: bản tạm không giải mã được ciphertext AES-GCM thật |
| `test_c02_ciphertext_hides_plaintext` | `AssertionError`: ciphertext của bản tạm chứa nguyên plaintext |
| `test_c03_wrong_key` | `DID NOT RAISE`: bản tạm không dùng key nên sai key vẫn giải mã được |

Commit phần đỏ trên máy (chưa push) để lịch sử cho thấy test có trước code:

```bash
git add tests/test_crypto.py
git commit -m "test(crypto): require real AES-GCM (remove xfail on H1 vector, C02, C03)"
```

**9b. Xanh** – thay toàn bộ file bằng bản thật; **giữ nguyên** `EncryptedValue`, `IntegrityFailure`, `_aad` và chữ ký các hàm:

```python
# app/crypto_service.py
import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE = 32
NONCE_SIZE = 12


class IntegrityFailure(Exception):
    """Giải mã thất bại: sai key, nonce, AAD hoặc dữ liệu đã bị sửa."""


@dataclass(frozen=True)
class EncryptedValue:
    ciphertext: bytes
    nonce: bytes
    key_version: str


class CryptoService:
    def __init__(self, key: bytes, key_version: str = "v1") -> None:
        if len(key) != KEY_SIZE:  # AESGCM nhận cả key 16/24 byte nên phải tự chặn
            raise ValueError("Key phải đúng 32 byte")
        self._aes = AESGCM(key)
        self.key_version = key_version

    @staticmethod
    def _aad(student_id: str, field: str, key_version: str) -> bytes:
        return f"student:{student_id}|field:{field}|key:{key_version}".encode("utf-8")

    def encrypt(self, value: str, student_id: str, field: str) -> EncryptedValue:
        nonce = os.urandom(NONCE_SIZE)  # nonce mới cho MỖI lần mã hóa
        ct = self._aes.encrypt(nonce, value.encode("utf-8"),
                               self._aad(student_id, field, self.key_version))
        return EncryptedValue(ct, nonce, self.key_version)

    def decrypt(self, ev: EncryptedValue, student_id: str, field: str) -> str:
        if ev.key_version != self.key_version:
            raise IntegrityFailure("Không có key cho phiên bản này")
        if len(ev.nonce) != NONCE_SIZE:  # nonce dưới 8 byte: AESGCM ném ValueError chứ không phải InvalidTag
            raise IntegrityFailure("Nonce sai độ dài")
        try:
            pt = self._aes.decrypt(ev.nonce, ev.ciphertext,
                                   self._aad(student_id, field, ev.key_version))
        except InvalidTag as exc:
            raise IntegrityFailure("Authentication failed") from exc
        return pt.decode("utf-8")
```

`python -m pytest tests/test_crypto.py -q` → `23 passed`.

**9c. Dọn:**

- [ ] Không còn `_fake_tag`, dòng cảnh báo bản tạm, `import hashlib`/`hmac`.
- [ ] Không in key, plaintext ra log hay thông báo lỗi.
- [ ] Mọi lỗi giải mã đều thành `IntegrityFailure` để TV2 chỉ bắt một loại lỗi và trả 409.

```bash
python -m pytest -q          # cả repo: không có failed
git add app/crypto_service.py
git commit -m "feat(crypto): AES-256-GCM implementation"
```

**Xong khi:** đã thấy `3 failed` đúng 3 test ở bảng trên, sau đó `23 passed`; `git log --oneline -2` cho commit `test(crypto)` nằm dưới commit `feat(crypto)`.

#### Bước 10. Kiểm tra độ mạnh của test

Test xanh chưa chắc đã kiểm đủ. Bước này chứng minh bộ test bắt được lỗi thật.

- [ ] Kiểm tra đột biến: `python tmp_mutants.py` (script ở mục 5 của `Ke_hoach_TV1_tuan_1.md`, khoảng 25 giây). Script lần lượt cài 18 lỗi điển hình vào 4 file của TV1 (dùng lại nonce, bỏ AAD, bỏ `validate=True`, viewer được ghi, ghi đè `.env`…), chạy test, rồi trả lại file gốc. Kết quả phải là `KET QUA: DAT`: 17 lỗi `BI BAT`, riêng M13 (`==` thay cho `compare_digest`) `SONG SOT (da biet)` vì đã kiểm bằng đọc code ở Bước 5.
- [ ] Coverage (chỉ cài trên máy, không thêm vào `requirements.txt`):
  ```bash
  python -m pip install pytest-cov
  python -m pytest --cov=app --cov=scripts --cov-branch --cov-report=term-missing tests/test_key_manager.py tests/test_crypto.py tests/test_auth.py tests/test_init_env.py
  ```
  4 dòng `app\key_manager.py`, `app\crypto_service.py`, `app\auth.py`, `scripts\init_env.py` đều `100%`. Máy bật Smart App Control sẽ in cảnh báo `Couldn't import C tracer` – coverage tự chuyển sang bộ đo viết bằng Python, kết quả vẫn đúng.
- [ ] Có lỗi sống sót ngoài M13, hoặc coverage dưới 100%: viết thêm test theo đúng chu kỳ (test đỏ trên code có lỗi, xanh trên code thật), chạy lại.

**Xong khi:** `tmp_mutants.py` in `KET QUA: DAT`; coverage 100% cho 4 file.

#### Bước 11. Mở PR crypto

```bash
python -m pytest -q                 # test của TV2/TV3 trên main vẫn phải xanh
git status                          # sạch: không có .env, không có tmp_*.py
git push -u origin feature/crypto
```

Mô tả PR:

```markdown
Title: feat(crypto): AES-256-GCM for sensitive fields
## Thay đổi
- Files: app/crypto_service.py, tests/test_crypto.py
- Interface: H1 giữ nguyên so với Sprint 0 (chỉ thay thân hàm)
- tests/test_crypto.py: gỡ xfail của 3 test cần mã hóa thật (H1 vector, C02, C03)
## Cách kiểm tra
- python -m pytest tests/test_crypto.py -q → 23 passed
- Làm theo TDD: commit test(crypto) (đỏ: 3 failed trên bản tạm) nằm trước commit feat(crypto) (xanh)
- Kiểm tra đột biến: 17/17 lỗi cài vào bị test bắt; M13 (== thay compare_digest) kiểm bằng đọc code
- Coverage app/crypto_service.py: 100% dòng và nhánh
## Lưu ý cho cả nhóm
- Dữ liệu demo tạo bằng bản crypto tạm sẽ trả 409 sau khi merge PR này:
  chạy python -m scripts.demo_client --reset
## Bảo mật
- Đã kiểm tra .env không được commit: YES
- Không có token/key trong screenshot/log: YES
## Người review
- TV2
```

**Xong khi:** PR mở, CI xanh, đã gán TV2 review.

### Tuần 2

#### Bước 12. Test C07 – replay cùng hàng (A7)

Test này **chứng minh một giới hạn**: GCM vẫn chấp nhận ciphertext cũ nếu được chép lại đúng hàng, đúng cột. Đây là *test đặc tả* (ghi lại hành vi đã có), nên xanh ngay từ lần chạy đầu – ngoại lệ có chủ đích của quy tắc “thấy đỏ trước”, vì nó không dẫn dắt code mới.

```python
# tests/test_crypto.py  (thêm vào cuối file)
def test_c07_replay_same_row_is_still_accepted(crypto):  # A7 – GIỚI HẠN
    old = crypto.encrypt("Địa chỉ cũ", "SV9001", "address")
    _current = crypto.encrypt("Địa chỉ mới", "SV9001", "address")
    # Người có quyền ghi DB chép lại (ciphertext, nonce) cũ vào đúng hàng/cột:
    assert crypto.decrypt(old, "SV9001", "address") == "Địa chỉ cũ"
```

**Xong khi:** C07 pass (`tests/test_crypto.py` → `24 passed`), có comment giải thích đây là giới hạn.

#### Bước 13. Viết `docs/crypto_design.md`

1. **Phạm vi**: mã hóa tầng ứng dụng cho 3 trường; khác gì mã hóa ổ đĩa và mã hóa trong DBMS.
2. **Định dạng lưu trữ**: `*_ct` = ciphertext + tag 16 byte; `*_nonce` = 12 byte. Mỗi trường tốn thêm 28 byte so với plaintext.
3. **`key_version`**: là gì, nằm ở đâu (cột trong bảng và trong AAD), vì sao MVP chỉ có `v1`.
4. **Thiết kế AAD**: vì sao gắn `student_id`, `field`, `key_version`; AAD ngăn tráo ciphertext giữa hàng (A5) và giữa cột.
5. **Quản lý khóa**: sinh bằng `secrets`, nằm trong `.env` ngoài DB; mất khóa là mất dữ liệu; không chạy lại `init_env.py` khi DB còn dữ liệu.
6. **Giới hạn nonce ngẫu nhiên 96 bit**: NIST SP 800-38D giới hạn khoảng 2^32 lần mã hóa cho một key khi nonce sinh ngẫu nhiên; demo nằm rất xa mức này.
7. **Replay (A7)**: kịch bản, kết quả C07, hướng khắc phục (đưa số phiên bản của hàng vào AAD và lưu ở nơi kẻ tấn công không sửa được).
8. **Xác thực token**: vì sao dùng `compare_digest` trên bytes, vì sao token tĩnh chỉ đủ cho demo.
9. **Key rotation tương lai**: keyring `{v1: key1, v2: key2}`, mã hóa mới bằng key mới nhất, job mã hóa lại dữ liệu cũ.
10. **Kiểm chứng**: cách làm TDD, bảng test ↔ yêu cầu, kết quả kiểm tra đột biến và coverage (lấy từ Bước 10).
11. **Ngoài phạm vi**: KMS/secret vault, TLS, khi máy ứng dụng hoặc khóa đã bị chiếm.

**Xong khi:** đủ 11 mục; TV2 hoặc TV3 đọc qua không thấy chỗ khó hiểu.

#### Bước 14. Review PR `feature/api-db` của TV2

- [ ] Không có `AESGCM` hay `os.urandom` ngoài `app/crypto_service.py`.
- [ ] `student_service.py` truyền đúng `student_id` và tên field ở cả encrypt lẫn decrypt.
- [ ] `key_version` lưu vào cột và đưa lại vào `EncryptedValue` khi đọc.
- [ ] PUT mã hóa lại cả 3 trường bằng nonce mới.
- [ ] `IntegrityFailure` được bắt và trả 409 với `code: integrity_failure`, không thành 500.
- [ ] Mỗi route gắn đúng `require_admin` (POST, PUT, DELETE) hoặc `require_reader` (GET); `/health` không gắn.
- [ ] `dependencies.py` dùng `decode_key()`; không log key hay token.

**Xong khi:** đã để lại nhận xét trên PR api-db.

#### Bước 15. PR nhỏ cho C07 và tài liệu

```bash
git switch main && git pull --ff-only origin main
git switch -c feature/crypto-docs
git add tests/test_crypto.py docs/crypto_design.md
git commit -m "docs(crypto): design notes and replay limitation test"
git push -u origin feature/crypto-docs
```

**Xong khi:** PR crypto (Bước 11) và PR này đều đã merge (mốc Vòng 1).

### Tuần 3

#### Bước 16. Kiểm tra trên PostgreSQL thật

```bash
git switch main && git pull --ff-only origin main
docker compose up -d --build
python -m scripts.demo_client
docker compose exec db psql -U demo -d encryption_demo -c "SELECT student_id, encode(national_id_ct, 'hex') AS ct_hex, encode(national_id_nonce, 'hex') AS nonce_hex, key_version FROM students;"
```

- [ ] `ct_hex` không chứa CCCD dạng rõ; `nonce_hex` dài 24 ký tự hex.
- [ ] Nếu GET trả 409 ngay sau khi merge AES-GCM: dữ liệu cũ tạo bằng bản tạm. Chạy `python -m scripts.demo_client --reset`.

#### Bước 17. Xử lý issue TV3 báo (test tái hiện trước)

- [ ] Mỗi lỗi: viết test tái hiện lỗi trước, chạy thấy **đỏ**; sửa code cho **xanh**; rồi mới mở PR nhỏ, chỉ trong file của TV1.
- [ ] Sửa trong `crypto_service.py`, `key_manager.py`, `auth.py` hay `init_env.py` thì chạy lại `python tmp_mutants.py`; mẫu đột biến nào báo `KHONG AP DUOC` vì code đã đổi thì cập nhật mẫu.
- [ ] Nếu phải đổi H1: mở issue, chờ TV2 và TV3 đồng ý rồi mới sửa (cả test lẫn code).

#### Bước 18. Phản biện bảo mật

- [ ] Đối chiếu kết quả A3, A4, A5 của TV3 với thiết kế AAD.
- [ ] Viết đoạn giải thích A6 và A7 cho nhật ký thực nghiệm (mục 8.7) và báo cáo; không viết A7 là “đã chống được”.

#### Bước 19. Nháp báo cáo

- [ ] Chương 1 (Mở đầu): bối cảnh, câu hỏi nghiên cứu (mục 1.1), mục tiêu, phạm vi.
- [ ] Chương 2 (Cơ sở lý thuyết): các mức mã hóa, AES/GCM, key, nonce, AAD; threat model lấy từ `docs/threat_model.md` của TV3.
- [ ] Phần module mã hóa và xác thực trong Chương 4 (gửi TV2 để ghép vào chương), kèm phần kiểm chứng: TDD, kiểm tra đột biến, coverage.

**Xong khi:** gửi nháp cho cả nhóm trước cuối tuần 3.

### Tuần 4

#### Bước 20. Slide và luyện phản biện

- [ ] Slide phần 0:00–2:00: sơ đồ kiến trúc, key/nonce/tag/AAD, ví dụ cùng plaintext ra hai ciphertext khác nhau.
- [ ] Luyện 8 câu hỏi ở mục 9.3 (ECB, nonce, nonce có bí mật không, sửa ciphertext, lộ key, `WHERE phone = ...`, mật khẩu dùng Argon2id, replay).

#### Bước 21. Ghép báo cáo và slide

- [ ] Nhận Chương 3–4 (TV2), Chương 5 (TV3); cả nhóm viết Chương 6.
- [ ] Thống nhất văn phong, đánh số hình/bảng, tài liệu tham khảo (mục 12.2).
- [ ] Ghép slide của 3 người thành một bộ, thống nhất mẫu.
- [ ] Kiểm tra không có key, token, nội dung `.env` trong báo cáo và slide.

#### Bước 22. Tổng duyệt

- [ ] Chạy thử phần nói của mình đúng 2 phút.
- [ ] Cả nhóm chạy demo 12 phút trên máy demo (TV3 chuẩn bị).

---

## 5. Definition of Done – TV1

- [ ] Test của TV1 (`test_key_manager`, `test_crypto`, `test_auth`, `test_init_env`) đạt trên CI; C01–C07 đều có.
- [ ] Mỗi test đã được thấy đỏ trước khi xanh (trừ `test_h1_signatures` và C07, đã giải thích ở Bước 4 và 12); kết quả đỏ/xanh có trong ghi chú.
- [ ] `python tmp_mutants.py` in `KET QUA: DAT`; coverage 100% dòng và nhánh cho 4 file code của TV1.
- [ ] `auth.py` trả 401 khi thiếu/sai token, 403 khi viewer ghi (TV1 kiểm trong `test_auth.py`, TV3 kiểm lại trong `test_security.py`).
- [ ] Interface H1 không đổi so với Sprint 0.
- [ ] `init_env.py` sinh đủ biến H4 và không ghi đè `.env` cũ.
- [ ] Không có key hardcode hay key bị commit.
- [ ] `crypto_design.md` giải thích rõ `key_version`.
- [ ] Báo cáo và slide đã ghép xong, không lộ secret.

## 6. Rủi ro

| Rủi ro | Dấu hiệu | Cách xử lý |
|---|---|---|
| Test xanh nhưng không kiểm gì | Viết code xong test xanh ngay, chưa từng thấy đỏ | Luôn chạy bước đỏ với skeleton; Bước 10 kiểm tra đột biến |
| Đỏ sai lý do | `ImportError`, `SyntaxError`, `ERROR collecting` ở bước đỏ | Sửa skeleton/test cho tới khi đỏ vì `NotImplementedError`/`AssertionError` |
| TV2 truyền tên field khác lúc encrypt và decrypt | GET trả 409 dù dữ liệu không bị sửa | Chốt tên field ở Bước 1; kiểm ở Bước 14 |
| Chạy lại `init_env.py` hoặc sửa `.env` khi DB còn dữ liệu | 409, hoặc DB báo sai mật khẩu | Script đã chặn ghi đè (có test); khôi phục `.env` cũ |
| Dữ liệu tạo bằng bản tạm còn trong DB | 409 sau khi merge AES-GCM | Ghi chú trong PR; chạy `python -m scripts.demo_client --reset` |
| `config.py` của TV2 đặt tên field khác | `auth.py` lỗi AttributeError | Chốt tên field ở Bước 1 |
| Smart App Control chặn thư viện trên máy TV1 | `An Application Control policy has blocked this file` | Xem ghi chú W1-01 trong `Ke_hoach_TV1_tuan_1.md`; không tắt Smart App Control |
| Lỡ commit `.env` hoặc key | GitHub secret scanning cảnh báo | Sinh key mới, gỡ secret khỏi repo và lịch sử, báo cả nhóm |
| TV2, TV3 nộp chương trễ | Tuần 4 không kịp ghép | Hạn nháp cuối tuần 3; nhắc từ giữa tuần 3 |
