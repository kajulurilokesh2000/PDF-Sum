#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from PyPDF2 import PdfReader
from openai import AzureOpenAI
from app.config import AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION, AZURE_DEPLOYMENT_NAME, MAX_CHUNK_SIZE
from app.prompts.summary_prompt import SUMMARY_PROMPT
from app.utils.text_chunker import chunk_text

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages_text = (page.extract_text() for page in reader.pages)
    return "\n".join(filter(None, pages_text)).strip()

def _call_chat_completion(client: AzureOpenAI, content: str) -> str:
    resp = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": content}
        ]
    )
    try:
        return resp.choices[0].message.content
    except Exception as e:
        raise RuntimeError("Invalid response from Azure OpenAI") from e

def summarize_text(text: str) -> str:
    if not text:
        return ""
    client = AzureOpenAI(
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_API_BASE
    )
    chunks = chunk_text(text, MAX_CHUNK_SIZE)
    chunk_summaries = [_call_chat_completion(client, c) for c in chunks]
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    combined = "\n\n".join(chunk_summaries)
    return _call_chat_completion(client, combined)

def main():
    parser = argparse.ArgumentParser(description="PDF Summarizer CLI")
    parser.add_argument("pdf_file", help="Path to the PDF file to summarize")
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_file)
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        print(f"Error: '{args.pdf_file}' is not a valid PDF file", file=sys.stderr)
        sys.exit(1)

    print(f"Processing: {pdf_path.name}")
    print("-" * 50)
    try:
        print("Extracting text from PDF...")
        text = extract_text_from_pdf(str(pdf_path))
        if not text:
            print("No extractable text found in the PDF.", file=sys.stderr)
            sys.exit(1)
        print(f"Extracted {len(text)} characters\n")
        print("Generating summary...")
        summary = summarize_text(text)
        print("\n" + "=" * 50)
        print(summary)
        print("=" * 50)
        if args.output:
            out_path = Path(args.output)
            out_path.write_text(summary, encoding="utf-8")
            print(f"\nSummary saved to: {out_path}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()