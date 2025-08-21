import tiktoken

def say_hello():
    print("Hello, world from llm_scratch_lab!")

class Tokenizer:
    """A simple tokenizer class using tiktoken."""
    
    def __init__(self, encoding_name="gpt2"):
        self.tokenizer = tiktoken.get_encoding(encoding_name)

    def tokenize(self, text):
        """Tokenizes the input text."""
        return self.tokenizer.encode(text)

    def detokenize(self, tokens):
        """Detokenizes the input tokens back to text."""
        return self.tokenizer.decode(tokens)