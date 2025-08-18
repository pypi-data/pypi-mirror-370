# core/token_manager.py

import logging

class TokenManager:
    """
    Manages token usage across summarization jobs for both Groq and OpenAI API.
    Tracks per-file and global usage to avoid exceeding model token limits.
    
    Note:
        - Use `set_token_estimator()` to assign a tokenizer function compatible with your LLM.
        - Called by summarizer or chunker before each LLM API call.
    """

    def __init__(self, max_tokens_global=8000):  # Default max token budget
        self.max_tokens = max_tokens_global
        self.used_tokens = 0
        self.usage_log = {}  # {file_id: token_count}
        self.token_estimator = None  # Function: str -> int

    def set_token_estimator(self, estimator_func):  # Set custom tokenizer function
        """
        Sets the function used to estimate tokens from a string.
        Examples:
            For Groq (LLaMA3/Mixtral): Use basic word/char count
            For OpenAI: Use `tiktoken`-based function
        """
        self.token_estimator = estimator_func


    # def groq_token_estimator(text):
        # return len(text) // 4  # Approx 1 token ≈ 4 characters

    # import tiktoken

    # encoding = tiktoken.encoding_for_model("gpt-4")  # or "gpt-3.5-turbo"

    # def openai_token_estimator(text):
    #     return len(encoding.encode(text))  # Accurate token count



    def estimate(self, text):  # Estimate token count using selected tokenizer
        if not self.token_estimator:
            raise ValueError("Token estimator not set. Use set_token_estimator().")
        return self.token_estimator(text)

    def add_usage(self, file_id, text):  # Adds usage to budget and logs it
        tokens = self.estimate(text)
        if not self.can_process(tokens):
            raise RuntimeError(f"Exceeded global token limit. Can't process {file_id} ({tokens} tokens).")
        self.used_tokens += tokens
        self.usage_log[file_id] = self.usage_log.get(file_id, 0) + tokens
        logging.info(f"✅ Processed {file_id} using {tokens} tokens.")
        return tokens

    def can_process(self, tokens):  # Checks if more tokens can be processed
        return (self.used_tokens + tokens) <= self.max_tokens

    def get_total_used(self):
        return self.used_tokens

    def get_remaining(self):
        return self.max_tokens - self.used_tokens

    def get_log(self):
        return self.usage_log
