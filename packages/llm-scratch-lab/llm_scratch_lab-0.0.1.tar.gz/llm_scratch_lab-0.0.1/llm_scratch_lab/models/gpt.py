import torch
import torch.nn as nn

from llm_scratch_lab.transformer import TransformerBlock
from llm_scratch_lab.model_utils import LayerNormalization

class GPTModel(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.__token_embedding__ = nn.Embedding(self.config["vocabulary_size"], self.config["embedding_dimension"]) # Token embedding layer
        self.__position_embedding__ = nn.Embedding(self.config["context_length"], self.config["embedding_dimension"]) # Position embedding layer
        # Dropout is optional

        # Initialize transformer blocks
        self.transformer_blocks = nn.Sequential(
            *[TransformerBlock(config) for _ in range(self.config["num_layers"])]
        )

        # Final layer to project the output to vocabulary size
        self.final_normalization = LayerNormalization(self.config["embedding_dimension"])
        self.output_layer = nn.Linear(self.config["embedding_dimension"], self.config["vocabulary_size"])


    
    def forward(self, input_tensor):
        """
        Forward pass for the GPT model.

        Args:
            input_tensor (torch.Tensor): Input tensor of shape (batch_size, seq_length) containing token indices.
        Returns:
            TBD
        """
        _, seq_length = input_tensor.shape

        # Retrieves the meanings of the input tokens (words)
        token_embeddings = self.__token_embedding__(input_tensor) # Token embedding lookup.

        # Retrieves the positions of the input tokens
        position_embeddings = self.__position_embedding__(torch.arange(seq_length, device=input_tensor.device)) # Position embedding lookup
        
        x = token_embeddings + position_embeddings # Combine token and position embeddings

        x = self.transformer_blocks(x) # Pass through transformer blocks
        x = self.final_normalization(x) # Final normalization layer
        logits = self.output_layer(x) # logic vector for each token in the vocabulary
        return logits