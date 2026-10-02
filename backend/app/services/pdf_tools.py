from pathlib import Path
import fitz


def merge_pdfs(paths: list[Path], output: Path):
    doc = fitz.open()
    for path in paths:
        src = fitz.open(path)
        doc.insert_pdf(src)
        src.close()
    doc.save(output, garbage=4, deflate=True)
    doc.close()


def split_pdf(path: Path, output_dir: Path, job_id: str) -> list[Path]:
    src = fitz.open(path)
    outputs = []
    for i in range(src.page_count):
        out = output_dir / f"{job_id}_page_{i+1}.pdf"
        single = fitz.open()
        single.insert_pdf(src, from_page=i, to_page=i)
        single.save(out, garbage=4, deflate=True)
        single.close()
        outputs.append(out)
    src.close()
    return outputs


def compress_pdf(path: Path, output: Path):
    src = fitz.open(path)
    src.save(output, garbage=4, clean=True, deflate=True)
    src.close()


def rotate_pdf(path: Path, output: Path, degrees: int):
    src = fitz.open(path)
    for page in src:
        page.set_rotation((page.rotation + degrees) % 360)
    src.save(output, garbage=4, deflate=True)
    src.close()
