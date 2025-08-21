import torch
import torch.nn as nn

class LayerNormalization(nn.Module):
    """Layer normalization for stabilizing training."""
    def __init__(self, embedding_dimension, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(embedding_dimension))
        self.bias = nn.Parameter(torch.zeros(embedding_dimension))

    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        normalized_x = (x - mean) / torch.sqrt(var + self.eps)
        return self.weight * normalized_x + self.bias
    

class GELU(nn.Module):
    """Gaussian Error Linear Unit activation function."""
    def forward(self, x):
        """Applies the GELU activation function."""
        return 0.5 * x * (1 + torch.tanh(torch.sqrt(torch.tensor(2.0 / torch.pi)) * (x + 0.044715 * torch.pow(x, 3))))
    

class FeedForward(nn.Module):
    """Feed-forward network with GELU activation."""
    def __init__(self, config):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(config["embedding_dimension"], 4 * config["embedding_dimension"]),
            GELU(),
            nn.Linear(4 * config["embedding_dimension"], config["embedding_dimension"])
        )

    def forward(self, x):
        return self.layers(x)