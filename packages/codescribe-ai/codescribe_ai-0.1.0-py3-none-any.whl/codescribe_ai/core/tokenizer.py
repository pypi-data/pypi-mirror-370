def estimate_tokens(text):  # Estimates number of tokens in a text (mocked for now)
    """
    Simulates token estimation (1 token ≈ 4 characters) — useful if `tiktoken` is unavailable.

    Note:
        This function is used inside `chunk_code()` to split code logically by token budget.
    """
    return len(text) // 4


def chunk_code(code_str, max_tokens=512):  # Chunks large code strings into token-limited chunks
    """
    Splits a long code string into smaller chunks that fit within the specified max_tokens.

    Notes:
        - Uses naive line-by-line accumulation (can be replaced with AST/semantic chunking).
        - Calls `estimate_tokens()` internally to track token count.
        - Tested by `test_chunking_respects_token_limit()` in tests/test_tokenizer.py.
    """
    chunks = []
    current_chunk = []
    current_tokens = 0

    for line in code_str.splitlines():
        line_tokens = estimate_tokens(line)
        if current_tokens + line_tokens > max_tokens:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_tokens = line_tokens
        else:
            current_chunk.append(line)
            current_tokens += line_tokens

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks
