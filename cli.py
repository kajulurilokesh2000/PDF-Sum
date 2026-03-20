#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from PyPDF2 import PdfReader
from app.config import AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION, AZURE_DEPLOYMENT_NAME, MAX_CHUNK_SIZE
from app.prompts.summary_prompt import SUMMARY_PROMPT
from app.utils.text_chunker import chunk_text
from openai import AzureOpenAI

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def summarize_text(text: str) -> str:
    """Generate summary using Azure OpenAI."""
    client = AzureOpenAI(
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_API_BASE
    )
    
    chunks = chunk_text(text, MAX_CHUNK_SIZE)
    
    if len(chunks) == 1:
        return _summarize_chunk(client, text)
    
    chunk_summaries = [_summarize_chunk(client, chunk) for chunk in chunks]
    combined = "\n\n".join(chunk_summaries)
    return _summarize_chunk(client, combined)

def _summarize_chunk(client: AzureOpenAI, text: str) -> str:
    """Summarize a single chunk of text."""
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="PDF Summarizer CLI")
    parser.add_argument("pdf_file", help="Path to the PDF file to summarize")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    
    if not pdf_path.exists():
        print(f"Error: File '{args.pdf_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    if not pdf_path.suffix.lower() == ".pdf":
        print("Error: Only PDF files are allowed", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing: {pdf_path.name}")
    print("-" * 50)
    
    try:
        print("Extracting text from PDF...")
        text = extract_text_from_pdf(str(pdf_path))
        print(f"Extracted {len(text)} characters")
        print()
        
        print("Generating summary...")
        summary = summarize_text(text)
        print()
        print("=" * 50)
        print(summary)
        print("=" * 50)
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(summary)
            print(f"\nSummary saved to: {args.output}")
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
