from openai import AzureOpenAI
from app.config import AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION, AZURE_DEPLOYMENT_NAME, MAX_CHUNK_SIZE
from app.prompts.summary_prompt import SUMMARY_PROMPT
from app.utils.text_chunker import chunk_text

client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_API_BASE
)

def summarize_text(text: str) -> str:
    chunks = chunk_text(text, MAX_CHUNK_SIZE)
    
    if len(chunks) == 1:
        return _summarize_chunk(text)
    
    chunk_summaries = [_summarize_chunk(chunk) for chunk in chunks]
    combined = "\n\n".join(chunk_summaries)
    return _summarize_chunk(combined)

def _summarize_chunk(text: str) -> str:
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
