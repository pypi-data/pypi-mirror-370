import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text: str) -> int:
    """
    tokenizer by tiktoken (openai)
    """
    token_count = len(enc.encode(text))
    return token_count