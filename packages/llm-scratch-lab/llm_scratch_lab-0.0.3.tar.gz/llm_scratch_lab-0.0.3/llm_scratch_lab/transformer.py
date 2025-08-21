import torch.nn as nn

from llm_scratch_lab.attention import MultiHeadAttention
from llm_scratch_lab.model_utils import FeedForward, LayerNormalization

class TransformerBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.attention = MultiHeadAttention(
            d_input=config["embedding_dimension"],
            d_output=config["embedding_dimension"],
            num_heads=config["num_heads"],
            context_length=config["context_length"]
        )

        self.feed_forward = FeedForward(config)
        self.layer_normalization1 = LayerNormalization(config["embedding_dimension"])
        self.layer_normalization2 = LayerNormalization(config["embedding_dimension"])

    def forward(self, x):
        # Shortcut connection for attention block
        shortcut = x
        x = self.layer_normalization1(x)
        x = self.attention(x)   # Shape [batch_size, num_tokens, emb_size]
        x = x + shortcut  # Add the original input back

        # Shortcut connection for feed-forward block
        shortcut = x
        x = self.layer_normalization2(x)
        x = self.feed_forward(x)
        x = x + shortcut  # Add the original input back

        return x