import torch.nn as nn
import torch

class SelfAttention(nn.Module):
    """Self-attention mechanism for processing input tensors."""
    def __init__(self, d_input, d_output):
        super().__init__()
        self.W_query = nn.Linear(torch.rand(d_input, d_output))
        self.W_key = nn.Linear(torch.rand(d_input, d_output))
        self.W_value = nn.Linear(torch.rand(d_input, d_output))

    def forward(self, input_tensor):
        """
        Forward pass for self-attention mechanism.
        
        Args:
            input_tensor (torch.Tensor): Input tensor of shape (batch_size, seq_length, d_input).
            This input is the sum of token and position embeddings.
        Returns:
            torch.Tensor: Context vector of shape (batch_size, seq_length, d_output).
        """
        keys = input_tensor @ self.W_key
        queries = input_tensor @ self.W_query
        values = input_tensor @ self.W_value
        attention_scores = queries @ keys.T
        attention_weights = torch.softmax(attention_scores / keys.shape[-1] ** 0.5, dim=-1)
        context_vector = attention_weights @ values
        return context_vector
    

class MultiHeadAttention(nn.Module):
    """
    Multi-head attention mechanism for processing input tensors.

    This combines a Causal Self-Attention mechanism with multiple heads to allow the model to jointly attend to information from different representation subspaces.
    """
    def __init__(self, d_input, d_output, num_heads, context_length, qkv_bias=False):
        super().__init__()
        assert d_output % num_heads == 0, "Output dimension must be divisible by number of heads."

        self.d_input = d_input
        self.d_output = d_output
        self.num_heads = num_heads
        self.context_length = context_length
        self.qkv_bias = qkv_bias #variable to control whether to use bias in the linear layers
        self.head_dim = d_output // num_heads

        self.W_query = nn.Linear(self.d_input, self.d_output, bias=qkv_bias)
        self.W_key = nn.Linear(self.d_input, self.d_output, bias=qkv_bias)
        self.W_value = nn.Linear(self.d_input, self.d_output, bias=qkv_bias)
        self.output = nn.Linear(self.d_output, self.d_output)

        # Create a mask to prevent attention to future tokens
        self.register_buffer("mask", torch.triu(torch.ones(context_length, context_length), diagonal=1))

    def forward(self, input_tensor):
        batch_size, num_tokens, embedding_dim = input_tensor.shape

        # project input tensor to queries, keys, and values
        keys = self.W_key(input_tensor)
        queries = self.W_query(input_tensor)
        values = self.W_value(input_tensor)

        # Split the embeddings into multiple heads (reshape and transpose)
        keys = keys.view(batch_size, num_tokens, self.num_heads, self.head_dim)
        queries = queries.view(batch_size, num_tokens, self.num_heads, self.head_dim)
        values = values.view(batch_size, num_tokens, self.num_heads, self.head_dim)

        key = keys.transpose(1, 2)
        queries = queries.transpose(1, 2)
        values = values.transpose(1, 2)

        # Calculate attention scores (scaled dot-product attention)
        attention_scores = queries @ key.transpose(2, 3) # Dot product for each head

        # mask the future tokens
        mask_bool = self.mask.bool()[:num_tokens, :num_tokens]

        # Apply the mask to the attention scores
        attention_scores.masked_fill_(mask_bool, -torch.inf)

        attention_weights = torch.softmax(attention_scores / keys.shape[-1]**0.5, dim=-1)


        context_vector = (attention_weights @ values).transpose(1, 2)  # Combine heads back to original shape

        context_vector = context_vector.contiguous().view(batch_size, num_tokens, self.d_output)
        context_vector = self.output(context_vector)  # Final linear layer to combine heads
        return context_vector