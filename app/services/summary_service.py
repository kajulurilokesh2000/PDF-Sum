from concurrent.futures import ThreadPoolExecutor
from openai import AzureOpenAI
from app.config import (
    AZURE_API_KEY,
    AZURE_API_BASE,
    AZURE_API_VERSION,
    AZURE_DEPLOYMENT_NAME,
    MAX_CHUNK_SIZE,
)
from app.prompts.summary_prompt import SUMMARY_PROMPT
from app.utils.text_chunker import chunk_text

openai_client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_API_BASE,
)


def summarize_text(text: str) -> str:
    """Return a concise summary of the input text.

    The text is split into chunks of up to MAX_CHUNK_SIZE. Each chunk is
    summarized (concurrently) and the chunk summaries are combined and
    summarized once more to produce the final summary.
    """
    if not text:
        return ""

    text_chunks = chunk_text(text, MAX_CHUNK_SIZE)
    if not text_chunks:
        return ""

    if len(text_chunks) == 1:
        return _summarize_chunk(text_chunks[0])

    # Summarize chunks concurrently (I/O-bound)
    max_workers = min(8, len(text_chunks))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        chunk_summaries = list(executor.map(_summarize_chunk, text_chunks))

    combined = "\n\n".join(chunk_summaries)
    return _summarize_chunk(combined)


def _summarize_chunk(chunk: str) -> str:
    """Summarize a single text chunk using the Azure OpenAI chat completion API."""
    response = openai_client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": chunk},
        ],
    )
    return response.choices[0].message.content