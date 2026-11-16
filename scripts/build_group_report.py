"""Assemble the six checked chapters into Markdown and a reviewable Word draft.

Install optional export packages from docs/requirements-export.txt, then run:
    python -m scripts.build_group_report
"""
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

DOCS = Path(__file__).resolve().parents[1] / "docs"
SOURCES = (
    "TV1_BAO_CAO_CHUONG_1_2.md",
    "TV2_BAO_CAO_CHUONG_3_4.md",
    "TV3_BAO_CAO_CHUONG_5.md",
    "BAO_CAO_CHUONG_6.md",
)
COVER = (
    "# BÁO CÁO ĐỒ ÁN: MÃ HÓA DỮ LIỆU NHẠY CẢM TRONG CƠ SỞ DỮ LIỆU\n\n"
    "Môn: Mật mã và An toàn thông tin\n\n"
    "Nhóm 3 thành viên: TV1 [họ tên, MSSV]; TV2 [họ tên, MSSV]; TV3 [họ tên, MSSV]\n\n"
    "Bản ghép để nhóm rà soát, 16/11/2026. Chưa phải bản nghiệm thu trên main.\n\n"
)


def plain(text: str) -> str:
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("**", "").replace("`", "").replace("  ", " ").strip()


def assemble() -> Path:
    parts = [COVER]
    for name in SOURCES:
        source = (DOCS / name).read_text(encoding="utf-8")
        lines = source.splitlines()
        if name in ("TV3_BAO_CAO_CHUONG_5.md", "BAO_CAO_CHUONG_6.md"):
            # These files start with the actual chapter heading.
            lines[0] = "#" + lines[0]
        else:
            # The first line identifies a multi-chapter source draft.
            lines = lines[1:]
        parts.append("\n".join(lines).strip() + "\n")
    path = DOCS / "BAO_CAO_TONG_HOP.md"
    path.write_text("\n\n".join(parts), encoding="utf-8")
    return path


def add_table(doc: Document, lines: list[str]) -> None:
    rows = [[plain(cell) for cell in line.strip().strip("|").split("|")]
            for line in lines]
    rows = [row for row in rows if not all(re.fullmatch(r":?-+:?", cell) for cell in row)]
    if not rows:
        return
    columns = max(len(row) for row in rows)
    table = doc.add_table(rows=1, cols=columns)
    table.style = "Table Grid"
    for col, value in enumerate(rows[0]):
        table.rows[0].cells[col].text = value
    for row in rows[1:]:
        cells = table.add_row().cells
        for col, value in enumerate(row):
            cells[col].text = value
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(8 if columns >= 7 else 9)
    doc.add_paragraph()


def export_docx(markdown_path: Path) -> Path:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin = section.right_margin = Cm(2.2)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    in_code = False
    table_lines: list[str] = []
    chapter_count = 0
    for line in lines:
        if line.startswith("|"):
            table_lines.append(line)
            continue
        if table_lines:
            add_table(doc, table_lines)
            table_lines = []
        if not line.strip():
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            paragraph = doc.add_paragraph(line)
            for run in paragraph.runs:
                run.font.name = "Consolas"
                run.font.size = Pt(8)
            continue
        image = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line.strip())
        if image:
            path = DOCS / image.group(2)
            if path.exists():
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(str(path), width=Cm(15))
                doc.add_paragraph(image.group(1), style="Caption")
            continue
        heading = re.match(r"^(#{1,6}) (.*)", line)
        if heading:
            title = plain(heading.group(2))
            if title.startswith("Chương ") and len(heading.group(1)) == 2:
                if chapter_count:
                    doc.add_page_break()
                chapter_count += 1
                doc.add_heading(title, level=1)
            else:
                doc.add_heading(title, level=min(len(heading.group(1)), 3))
            continue
        if line.startswith("- "):
            doc.add_paragraph(plain(line[2:]), style="List Bullet")
        elif re.match(r"^\d+\. ", line):
            doc.add_paragraph(plain(re.sub(r"^\d+\. ", "", line)), style="List Number")
        else:
            doc.add_paragraph(plain(line))
    if table_lines:
        add_table(doc, table_lines)
    section.footer.paragraphs[0].text = "Database Encryption • Bản ghép nhóm 16/11/2026 • Chờ review/CI/main"
    path = DOCS / "BAO_CAO_TONG_HOP.docx"
    doc.save(path)
    assert len(Document(path).paragraphs) > 100
    return path


def main() -> None:
    markdown = assemble()
    word = export_docx(markdown)
    print(f"Created {markdown.name} and {word.name}")


if __name__ == "__main__":
    main()
