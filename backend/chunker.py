import tiktoken
from config import config

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def chunk_novel(novel_text: str) -> list[dict]:
    """
    Split novel into fixed-size chunks with overlap.
    Returns list of {chunk_id, chunk_text, start_char, end_char}
    """
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(novel_text)
    chunks = []
    chunk_id = 0
    start_idx = 0
    
    while start_idx < len(tokens):
        end_idx = min(start_idx + config.CHUNK_SIZE_TOKENS, len(tokens))
        chunk_tokens = tokens[start_idx:end_idx]
        chunk_text = encoding.decode(chunk_tokens)
        
        # Calculate character positions for reference
        if chunk_id == 0:
            start_char = 0
        else:
            start_char = len(encoding.decode(tokens[:start_idx]))
        end_char = len(encoding.decode(tokens[:end_idx]))
        
        chunks.append({
            "chunk_id": chunk_id,
            "chunk_text": chunk_text,
            "start_char": start_char,
            "end_char": end_char,
            "token_count": len(chunk_tokens)
        })
        
        chunk_id += 1
        start_idx = end_idx - config.CHUNK_OVERLAP_TOKENS
        
        if start_idx >= len(tokens) - config.CHUNK_OVERLAP_TOKENS:
            break
    
    return chunks
