"""Build one 12-minute group deck from verified local results and charts.

Install docs/requirements-export.txt, then run ``python -m scripts.export_group_slides``.
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

from scripts.export_tv2_docs import AMBER, GRAY, NAVY, TEAL, block, text_box

DOCS = Path(__file__).resolve().parents[1] / "docs"


def slide_base(prs, number, title, subtitle, owner):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    text_box(slide, 0.55, 0.3, 12.0, 0.35,
             f"DATABASE ENCRYPTION / {owner}", 13, TEAL, True)
    text_box(slide, 0.55, 0.92, 12.1, 0.72, title, 32, NAVY, True)
    text_box(slide, 0.58, 1.72, 12.0, 0.45, subtitle, 17, GRAY)
    text_box(slide, 0.58, 6.86, 11.5, 0.3,
             "Bản ghép local 16/11/2026 • Chờ review, CI và nghiệm thu main", 11, AMBER)
    text_box(slide, 12.15, 6.86, 0.55, 0.3, f"{number:02}", 12, TEAL, True)
    return slide


def notes(slide, message):
    slide.notes_slide.notes_text_frame.text = message


def main():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)

    slide = slide_base(prs, 1, "Mã hóa dữ liệu nhạy cảm trong PostgreSQL",
                       "Demo 12 phút • FastAPI + AES-256-GCM + PostgreSQL", "CẢ NHÓM")
    block(slide, 0.8, 2.55, 11.7, 2.85)
    text_box(slide, 1.1, 2.86, 11.0, 1.05,
             "Ba trường được mã hóa trước khi lưu:\nnational_id • phone • address", 27, NAVY, True)
    text_box(slide, 1.1, 4.34, 10.9, 0.7,
             "TV1: mật mã  |  TV2: API/DB  |  TV3: tấn công thử và benchmark", 20, TEAL)
    notes(slide, "0:00–0:30, TV1. Giới thiệu bài toán và dữ liệu giả. "
          "Điền họ tên/MSSV của nhóm trước khi xuất bản cuối.")

    slide = slide_base(prs, 2, "TV1 • Mật mã và AAD", "0:30–2:00 | Điều gì được bảo vệ?", "TV1")
    for i, (heading, body) in enumerate((
        ("KHÓA", "AES-256\n32 byte, ngoài DB"),
        ("NONCE", "12 byte ngẫu nhiên\nmỗi lần encrypt"),
        ("TAG", "16 byte\nphát hiện sửa dữ liệu"),
        ("AAD", "ID + field + version\nngăn tráo chéo"),
    )):
        x = 0.6 + 3.15 * i
        block(slide, x, 2.7, 2.7, 2.25)
        text_box(slide, x + 0.17, 2.94, 2.35, 0.4, heading, 20, TEAL, True)
        text_box(slide, x + 0.17, 3.58, 2.35, 1.05, body, 18)
    text_box(slide, 0.78, 5.46, 11.7, 0.7,
             "A7: ciphertext cũ cùng hàng/cùng field vẫn hợp lệ — giới hạn replay.", 22, AMBER, True)
    notes(slide, "TV1 giải thích AES-GCM, AAD student:<id>|field:<field>|key:<version>, "
          "sai tag hoặc UTF-8 thì IntegrityFailure. Nêu rõ A7 là giới hạn, không nói đã chống replay.")

    slide = slide_base(prs, 3, "TV2 • Luồng ghi và đọc", "2:00–3:00 | Kiến trúc ứng dụng", "TV2")
    for i, (heading, body) in enumerate((
        ("CLIENT", "Swagger\nJSON + token"),
        ("FASTAPI", "Auth + validate\nCRUD"),
        ("CRYPTO", "Encrypt/decrypt\n3 trường"),
        ("POSTGRESQL", "BYTEA + nonce\nkey_version"),
    )):
        x = 0.6 + 3.15 * i
        block(slide, x, 2.65, 2.65, 2.2)
        text_box(slide, x + 0.17, 2.93, 2.32, 0.4, heading, 18, TEAL, True)
        text_box(slide, x + 0.17, 3.55, 2.32, 1.0, body, 18)
        if i < 3:
            text_box(slide, x + 2.7, 3.46, 0.42, 0.55, "→", 27, TEAL)
    text_box(slide, 0.78, 5.37, 11.6, 0.75,
             "POST: admin → encrypt → DB  |  GET: reader → decrypt → JSON", 22, NAVY, True)
    notes(slide, "TV2: chỉ rõ khóa không nằm trong DB. API kiểm quyền trước khi trả plaintext. "
          "POST/GET/PUT/DELETE và mã lỗi theo H2.")

    slide = slide_base(prs, 4, "TV2 • Demo Swagger và SQL", "3:00–5:00 | Cùng hồ sơ, hai góc nhìn", "TV2")
    block(slide, 0.7, 2.6, 5.75, 2.8)
    block(slide, 6.88, 2.6, 5.75, 2.8)
    text_box(slide, 0.94, 2.9, 5.25, 0.45, "SWAGGER • người có quyền", 19, TEAL, True)
    text_box(slide, 0.94, 3.65, 5.25, 1.35,
             "POST → 201\nGET → 200, thấy phone rõ", 23)
    text_box(slide, 7.12, 2.9, 5.2, 0.45, "PSQL • chỉ có bản DB", 19, TEAL, True)
    text_box(slide, 7.12, 3.65, 5.2, 1.35,
             "national_id_ct: hex\nnonce: 12 byte", 23)
    text_box(slide, 0.82, 5.72, 11.5, 0.58,
             "Smoke PostgreSQL: 19/19 đạt • Test tích hợp: 102 passed", 21, NAVY, True)
    notes(slide, "TV2: authorize trước khi chia sẻ màn hình. Dùng ID demo chưa tồn tại. "
          "Ảnh/log dự phòng cần lấy từ commit main cuối; không mở .env. "
          "Đầu ra SQL demo đã lưu ở docs/evidence/psql_ciphertext_2026-11-16.txt.")

    slide = slide_base(prs, 5, "TV3 • Ma trận A1–A8", "5:00–6:00 | Expected và actual", "TV3")
    cases = (
        ("A1", "Không token", "401"), ("A2", "Viewer DELETE", "403, hàng nguyên"),
        ("A3", "Đọc DB thô", "Ciphertext"), ("A4", "Sửa ciphertext", "409 integrity_failure"),
        ("A5", "Tráo hàng", "409 integrity_failure"), ("A6", "Sai khóa", "IntegrityFailure"),
        ("A7", "Replay cùng ô", "Vẫn giải mã • giới hạn"), ("A8", "ID kiểu SQL", "422, DB nguyên"),
    )
    for i, (code, attack, result) in enumerate(cases):
        col, row = i % 2, i // 2
        x, y = 0.7 + 6.15 * col, 2.35 + 1.0 * row
        block(slide, x, y, 5.78, 0.78)
        text_box(slide, x + 0.12, y + 0.13, 0.68, 0.48, code, 18, AMBER if code == "A7" else TEAL, True)
        text_box(slide, x + 0.82, y + 0.13, 2.2, 0.48, attack, 16)
        text_box(slide, x + 3.03, y + 0.13, 2.6, 0.48, result, 15, NAVY, True)
    notes(slide, "TV3: A1–A5 chạy bằng attack_lab; A6/A7 từ test_crypto; A8 từ security test. "
          "A7 là kết quả giới hạn, không gọi là phòng chống thành công.")

    slide = slide_base(prs, 6, "TV3 • Tấn công thử và khôi phục", "6:00–8:00 | PostgreSQL demo cô lập", "TV3")
    block(slide, 0.76, 2.55, 11.72, 3.25)
    text_box(slide, 1.0, 2.82, 11.15, 2.7,
             "A1: 401  |  A2: 403, DB và payload nguyên\n"
             "A3: 3 field không chứa plaintext\n"
             "A4/A5: 409 đúng integrity_failure\n"
             "Sau mỗi phép sửa: byte DB và JSON khôi phục đúng", 22, NAVY)
    notes(slide, "TV3 chạy python -m scripts.attack_lab trên SV9001/SV9002 dữ liệu giả. "
          "Script kiểm code lỗi, nội dung sau restore và trả exit 1 nếu sai. "
          "Không reset dữ liệu khác, không hiển thị token/khóa.")

    for number, title, image, note in (
        (7, "Benchmark • INSERT", "benchmark_insert.png",
         "8:00–9:00. Giải thích median 3 lần sau warmup; thời gian AES gồm mã hóa và ghi."),
        (8, "Benchmark • SELECT", "benchmark_select.png",
         "9:00–10:00. Thời gian AES gồm đọc và giải mã. n=100 nhiễu đo, không kết luận AES nhanh hơn."),
    ):
        slide = slide_base(prs, number, title,
                           "Plaintext so với AES-256-GCM • n = 100 / 1.000 / 10.000", "TV3")
        slide.shapes.add_picture(str(DOCS / "figures" / image), Inches(0.64), Inches(2.22), width=Inches(7.7))
        block(slide, 8.7, 2.65, 3.9, 2.82)
        if number == 7:
            text_box(slide, 8.95, 2.93, 3.35, 2.15,
                     "n=10.000\nPlain: 0,256 s\nAES: 1,086 s\n+323,6%", 19, NAVY, True)
        else:
            text_box(slide, 8.95, 2.93, 3.35, 2.15,
                     "n=10.000\nPlain: 0,017 s\nAES: 0,314 s\n+1.702,3%", 19, NAVY, True)
        notes(slide, note + " Payload tăng 84 byte/hồ sơ; đây không phải số đo dung lượng đĩa.")

    slide = slide_base(prs, 9, "Giới hạn và kết luận", "10:00–12:00 | Cả nhóm và hỏi đáp", "CẢ NHÓM")
    block(slide, 0.7, 2.54, 5.8, 3.35)
    block(slide, 6.84, 2.54, 5.8, 3.35)
    text_box(slide, 0.98, 2.86, 5.2, 0.45, "ĐÃ CHỨNG MINH", 19, TEAL, True)
    text_box(slide, 0.98, 3.6, 5.2, 1.9,
             "3 field mã hóa trước DB\nSửa/tráo bị phát hiện\nCode demo chạy trên PostgreSQL", 20)
    text_box(slide, 7.12, 2.86, 5.2, 0.45, "CẦN NÓI RÕ", 19, AMBER, True)
    text_box(slide, 7.12, 3.6, 5.2, 1.9,
             "Metadata vẫn lộ\nLộ khóa/máy API: mất bảo vệ\nA7 replay cùng ô vẫn hợp lệ", 20)
    notes(slide, "Cả nhóm: tổng kết đúng phạm vi, không gọi demo là production. "
          "Nêu CI/review/main và nghiệm thu máy sạch trước tag. Dành thời gian trả lời câu hỏi.")

    for slide in prs.slides:
        for shape in slide.shapes:
            if (shape.left < 0 or shape.top < 0 or
                    shape.left + shape.width > prs.slide_width or
                    shape.top + shape.height > prs.slide_height):
                raise ValueError("A slide element exceeds slide bounds")
    path = DOCS / "SLIDE_TONG_HOP.pptx"
    prs.save(path)
    print(f"Created {path.name}: {len(prs.slides)} slides with speaker notes")


if __name__ == "__main__":
    main()
