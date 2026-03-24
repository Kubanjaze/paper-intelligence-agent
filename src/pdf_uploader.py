"""
pdf_uploader.py — Files API: upload PDF once, return file_id, cleanup on exit.
"""
import os

import anthropic


def upload_pdf(path: str) -> str:
    """Upload PDF via Files API. Returns file_id."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with open(path, "rb") as f:
        uploaded = client.beta.files.upload(
            file=(os.path.basename(path), f, "application/pdf"),
        )
    return uploaded.id


def delete_file(file_id: str) -> None:
    """Clean up uploaded file after session. Called in finally block."""
    try:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        client.beta.files.delete(file_id)
    except Exception as exc:
        print(f"Warning: could not delete file {file_id}: {exc}")
