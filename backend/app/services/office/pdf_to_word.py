from pathlib import Path
import subprocess


def convert_pdf_to_word(input_file: Path, output_dir: Path) -> Path:
    """Convert PDF to DOCX through LibreOffice when the installed build supports it."""
    input_file = Path(input_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "soffice", "--headless", "--convert-to", "docx",
        "--outdir", str(output_dir), str(input_file)
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "LibreOffice conversion failed.")

    output_file = output_dir / f"{input_file.stem}.docx"
    if not output_file.exists():
        raise RuntimeError(
            "PDF to DOCX conversion was not produced by LibreOffice. "
            "Complex/scanned PDFs may require a dedicated PDF-to-Word engine."
        )
    return output_file
