"""Export TV2 report and slides (no secrets or network access).

Install: .venv/Scripts/python -m pip install -r docs/requirements-export.txt
Run:     .venv/Scripts/python -m scripts.export_tv2_docs
The report source is docs/TV2_BAO_CAO_CHUONG_3_4.md.
Slide wording is below; detailed rehearsal notes are in TV2_SLIDE_VA_DEMO.md.
"""
import re
from pathlib import Path

from docx import Document
from docx.shared import Cm, Pt as WordPt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def export_report():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin, section.right_margin = Cm(2.5), Cm(2)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = WordPt(11)
    normal.paragraph_format.space_after = WordPt(7)
    normal.paragraph_format.line_spacing = 1.15
    for line in (DOCS / "TV2_BAO_CAO_CHUONG_3_4.md").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        heading = re.match(r"^(#{1,3}) (.*)", line)
        if heading:
            level = len(heading[1]) - 1
            if heading[2].startswith("Chương 4"):
                doc.add_page_break()
            doc.add_heading(heading[2], level=level)
        else:
            doc.add_paragraph(line)
    section.footer.paragraphs[0].text = "Database Encryption • TV2 • Bản tích hợp 15/11/2026"
    path = DOCS / "TV2_BAO_CAO_CHUONG_3_4.docx"
    doc.save(path)
    assert len(Document(path).paragraphs) > 50
    print("Created docs/TV2_BAO_CAO_CHUONG_3_4.docx")


NAVY = "13253C"
TEAL = "087E8B"
INK = "213547"
GRAY = "536477"
PALE = "F2F6FA"
AMBER = "9A5B00"


def rgb(color):
    return RGBColor.from_string(color)


def text_box(slide, x, y, w, h, text, size=22, color=INK, bold=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.03)
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = "Arial"
        p.font.size = Pt(size)
        p.font.color.rgb = rgb(color)
        p.font.bold = bold
        p.space_after = Pt(12)
    return shape


def block(slide, x, y, w, h, fill=PALE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.fill.background()
    return shape


def base(prs, number, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    text_box(slide, 0.55, 0.32, 12, 0.38, "DATABASE ENCRYPTION / THÀNH VIÊN 2", 13, TEAL, True)
    text_box(slide, 0.55, 0.95, 12.2, 0.75, title, 34, NAVY, True)
    text_box(slide, 0.58, 1.76, 12, 0.65, subtitle, 19, GRAY)
    text_box(slide, 0.55, 6.85, 11.5, 0.34,
             "Tích hợp local 15/11/2026 • AES-GCM + API + PostgreSQL • Chờ review/merge", 12, AMBER)
    text_box(slide, 12.1, 6.85, 0.65, 0.34, f"0{number}", 13, TEAL, True)
    return slide


def export_slides():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    slide = base(prs, 1, "API nối người dùng với dữ liệu", "2:00–2:30  |  Kiến trúc và ranh giới trách nhiệm")
    cards = [("CLIENT", "Swagger\nGửi / nhận JSON"),
             ("FASTAPI", "Auth + schema\nCRUD · TV2"),
             ("CRYPTO", "Encrypt / decrypt\nH1 · TV1"),
             ("POSTGRESQL", "students\nBYTEA + metadata")]
    for i, (title, content) in enumerate(cards):
        x = 0.6 + 3.2 * i
        block(slide, x, 2.8, 2.55, 2.05)
        text_box(slide, x + 0.15, 3.0, 2.25, 0.4, title, 19, TEAL, True)
        text_box(slide, x + 0.15, 3.65, 2.25, 1.1, content, 20)
        if i < 3:
            text_box(slide, x + 2.66, 3.55, 0.43, 0.55, "→", 27, TEAL)
    text_box(slide, 0.7, 5.25, 11.8, 1.1,
             "Khóa nằm ngoài bảng students.\nAPI kiểm tra quyền trước khi trả dữ liệu rõ.", 23, NAVY)
    slide.notes_slide.notes_text_frame.text = (
        "30 giây. Giải thích TV1 cung cấp auth/crypto; TV2 nối API và DB. "
        "Sơ đồ thể hiện luồng logic; CryptoService được gọi trong tiến trình API. "
        "AES-GCM của TV1 đã tích hợp; khóa nằm ngoài bảng students.")

    slide = base(prs, 2, "Một đường ghi, một đường đọc", "2:30–2:50  |  Sau đó chuyển Swagger: POST → GET (đến 4:05)")
    for y, title, content in [
        (2.7, "POST · admin", "Kiểm tra body → encrypt 3 field → commit → 201"),
        (4.1, "GET · admin / viewer", "Đọc row → decrypt đúng ID + field + version → 200"),
    ]:
        block(slide, 0.6, y, 12.1, 1.15)
        text_box(slide, 0.8, y + 0.12, 3.3, 0.85, title, 22, TEAL, True)
        text_box(slide, 4.15, y + 0.12, 8.3, 0.85, content, 22)
    text_box(slide, 0.7, 5.65, 11.9, 0.8,
             "Trùng mã → 409 duplicate_student   |   Dữ liệu hỏng → 409 integrity_failure", 20)
    slide.notes_slide.notes_text_frame.text = (
        "20 giây trên slide. Sau đó chuyển Swagger 75 giây: đã authorize trước khi chiếu màn hình. "
        "POST dữ liệu giả SV9003 nếu chưa tồn tại, chỉ vào 201. GET cùng ID, chỉ vào 200. "
        "JSON và lời dẫn đầy đủ trong docs/TV2_SLIDE_VA_DEMO.md. Không mở .env trên màn hình.")

    slide = base(prs, 3, "Cùng hồ sơ, hai cách quan sát", "4:05–4:40  |  Đối chiếu Swagger với psql")
    block(slide, 0.6, 2.7, 5.6, 2.75)
    block(slide, 6.65, 2.7, 6.05, 2.75)
    text_box(slide, 0.85, 2.9, 5.1, 0.5, "GIỮ RÕ", 23, TEAL, True)
    text_box(slide, 0.85, 3.65, 5.1, 1.45, "student_id\nfull_name · major", 25)
    text_box(slide, 6.9, 2.9, 5.55, 0.5, "ĐƯA QUA CRYPTOSERVICE", 23, TEAL, True)
    text_box(slide, 6.9, 3.65, 5.55, 1.45,
             "national_id · phone · address\nMỗi field: ciphertext + nonce", 24)
    text_box(slide, 0.7, 5.75, 11.95, 0.7,
             "Đã kiểm: tag 16 byte · nonce 12 byte · không thấy plaintext trong ciphertext.", 22, AMBER, True)
    slide.notes_slide.notes_text_frame.text = (
        "35 giây. Chạy SELECT của kịch bản Markdown để hiển thị cùng student_id. "
        "Tên/ngành rõ theo thiết kế, phone_ct là BYTEA, nonce 12 byte. "
        "Bản tích hợp đã đạt 19 điều kiện smoke PostgreSQL và test mật mã. "
        "Hex chỉ là biểu diễn; kết luận dựa thêm vào test và attack lab. Replay cùng ô vẫn là giới hạn.")

    slide = base(prs, 4, "Kết quả hiện tại và bước bàn giao", "4:40–5:00  |  Chuyển TV3 kiểm thử tấn công và khôi phục")
    block(slide, 0.6, 2.7, 5.8, 2.9)
    block(slide, 6.8, 2.7, 5.9, 2.9)
    text_box(slide, 0.85, 2.95, 5.3, 0.5, "ĐÃ KIỂM TRA", 23, TEAL, True)
    text_box(slide, 0.85, 3.65, 5.3, 1.75,
             "Pytest: 91 passed, 0 xfail\nPostgreSQL: 19/19 đạt\nAttack lab + restore: đạt", 22)
    text_box(slide, 7.05, 2.95, 5.4, 0.5, "BÀN GIAO", 23, AMBER, True)
    text_box(slide, 7.05, 3.65, 5.4, 1.75,
             "Chốt H2–H5 ở issue #3\nReview + CI + merge PR\nGhép báo cáo, luyện demo", 22)
    text_box(slide, 0.7, 5.9, 11.8, 0.6,
             "Bằng chứng: docs/tv2_verification.json  •  Không suy diễn test API thành an toàn mật mã", 18, GRAY)
    slide.notes_slide.notes_text_frame.text = (
        "20 giây. Kết quả local ngày 15/11/2026: 91 test đạt, không xfail; PostgreSQL 19/19. "
        "Attack lab A1=401, A2=403, A3=True, A4/A5=409, Restore=200. Chưa merge GitHub. "
        "Chuyển TV3: quyền, tamper, tráo hàng, restore. Tổng phần TV2 3 phút gồm demo Swagger/psql.")

    for slide in prs.slides:
        for shape in slide.shapes:
            assert shape.left >= 0 and shape.top >= 0
            assert shape.left + shape.width <= prs.slide_width
            assert shape.top + shape.height <= prs.slide_height
    path = DOCS / "TV2_HE_THONG.pptx"
    prs.save(path)
    assert len(Presentation(path).slides) == 4
    print("Created docs/TV2_HE_THONG.pptx (4 slides with speaker notes)")


if __name__ == "__main__":
    export_report()
    export_slides()
