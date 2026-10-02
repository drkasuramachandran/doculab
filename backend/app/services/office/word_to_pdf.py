from pathlib import Path
import subprocess


def convert_word_to_pdf(input_file: Path, output_dir: Path) -> Path:
    input_file = Path(input_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "soffice", "--headless", "--convert-to", "pdf",
        "--outdir", str(output_dir), str(input_file)
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "LibreOffice conversion failed.")

    output_file = output_dir / f"{input_file.stem}.pdf"
    if not output_file.exists():
        raise RuntimeError("LibreOffice completed, but the PDF was not created.")
    return output_file
