def chunk_text(text: str, max_chunk_size: int) -> list[str]:
    """Split text into chunks where each chunk's character length (including spaces)
    does not exceed max_chunk_size. Splits on whitespace and preserves whole words.
    If a single word is longer than max_chunk_size it will be placed in a chunk by itself.

    Args:
        text: The input string to split.
        max_chunk_size: Maximum allowed length of each chunk (must be positive).

    Returns:
        A list of chunks.
    """
    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size must be a positive integer")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    current_words: list[str] = []
    current_len = 0  # length of " ".join(current_words)

    for word in words:
        wlen = len(word)
        if not current_words:
            # start a new chunk with the current word
            current_words.append(word)
            current_len = wlen
        else:
            # length if we add this word including a space
            next_len = current_len + 1 + wlen
            if next_len <= max_chunk_size:
                current_words.append(word)
                current_len = next_len
            else:
                # flush current chunk and start a new one
                chunks.append(" ".join(current_words))
                current_words = [word]
                current_len = wlen

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks