from llm_scratch_lab.tokenizer import Tokenizer
from llm_scratch_lab.models.gpt import GPTModel

import torch

# Define the configuration for the GPT model
GPT_CONFIG_124M = {
    "vocabulary_size": 50257,       # Vocabulary size
    "context_length": 1024,         # Context length
    "embedding_dimension": 768,     # Embedding dimension
    "num_heads": 12,                # Number of attention heads
    "num_layers": 12,               # Number of layers
    "qkv_bias": False               # Query-Key-Value bias
}

class GPTLab:
    """A class representing a GPT Lab environment."""

    def __init__(self):
        self.__tokens__ = None
        self.__token_tensor__ = None
        self.config = GPT_CONFIG_124M
        self.tokenizer = Tokenizer(encoding_name="gpt2")
        self.model = GPTModel(self.config)
    
    def __tensorize_tokens__(self, tokens, with_batch_dim=True):
        """Converts tokens to a tensor format."""
        tensor = torch.tensor(tokens, dtype=torch.long)
        if with_batch_dim:
            tensor = tensor.unsqueeze(0)  # Add batch dimension
        return tensor

    def run(self, text, with_manual_seed=False):
        """Runs the GPT model with the provided text input."""
        if with_manual_seed:
            torch.manual_seed(123)
            print("Manual seed set to 123 for reproducibility.")

        print("Tokenizing the input text: ", text)
        self.__tokens__ = self.tokenizer.tokenize(text)
        print("Tokenized Tokens:", self.__tokens__)

        print("\nConverting tokens to PyTorch tensor...")
        self.__token_tensor__ = self.__tensorize_tokens__(self.__tokens__)
        print("Tensor Tokens:", self.__token_tensor__)

        print("\nRunning the GPT model...")
        
        max_tokens = 10
        for _ in range(max_tokens):

            token_cond = self.__token_tensor__[:, -self.config["context_length"]:]

            with torch.no_grad():
                logits = self.model(token_cond)

            logits = logits[:, -1, :]

            next_token = torch.argmax(logits, dim=-1, keepdim=True)  # Get the next token
            self.__token_tensor__ = torch.cat((self.__token_tensor__, next_token), dim=1)

        decoded_text = self.tokenizer.detokenize(self.__token_tensor__.squeeze(0).tolist())
        print("\nGenerated Output Tokens:", self.__token_tensor__)
        print("Decoded text:", decoded_text)