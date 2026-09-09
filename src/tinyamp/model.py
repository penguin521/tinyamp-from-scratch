import math
import torch
import torch.nn as nn
import torch.nn.functional as F

AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
VOCAB = ["<BOS>", "<EOS>"] + AMINO_ACIDS
STOI = {token: i for i, token in enumerate(VOCAB)}
ITOS = {i: token for token, i in STOI.items()}
BOS_ID = STOI["<BOS>"]
EOS_ID = STOI["<EOS>"]
VOCAB_SIZE = len(VOCAB)


def model_config(name: str) -> dict:
    name = name.lower()
    if name == "small":
        return dict(block_size=64, embed_dim=64, num_heads=4, num_layers=2, dropout=0.10)
    if name == "medium":
        return dict(block_size=64, embed_dim=128, num_heads=4, num_layers=4, dropout=0.10)
    raise ValueError("model must be 'small' or 'medium'")


class CausalSelfAttention(nn.Module):
    def __init__(self, embed_dim, num_heads, block_size, dropout):
        super().__init__()
        if embed_dim % num_heads:
            raise ValueError("embed_dim must be divisible by num_heads")
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.query = nn.Linear(embed_dim, embed_dim, bias=False)
        self.key = nn.Linear(embed_dim, embed_dim, bias=False)
        self.value = nn.Linear(embed_dim, embed_dim, bias=False)
        self.output_projection = nn.Linear(embed_dim, embed_dim)
        self.attention_dropout = nn.Dropout(dropout)
        self.output_dropout = nn.Dropout(dropout)
        mask = torch.tril(torch.ones(block_size, block_size, dtype=torch.bool))
        self.register_buffer("causal_mask", mask.view(1, 1, block_size, block_size))

    def forward(self, x):
        b, t, c = x.shape
        q = self.query(x).view(b, t, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.key(x).view(b, t, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.value(x).view(b, t, self.num_heads, self.head_dim).transpose(1, 2)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        scores = scores.masked_fill(~self.causal_mask[:, :, :t, :t], float("-inf"))
        attention = self.attention_dropout(F.softmax(scores, dim=-1))
        out = attention @ v
        out = out.transpose(1, 2).contiguous().view(b, t, c)
        return self.output_dropout(self.output_projection(out))


class FeedForward(nn.Module):
    def __init__(self, embed_dim, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_dim, 4 * embed_dim),
            nn.GELU(),
            nn.Linear(4 * embed_dim, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, embed_dim, num_heads, block_size, dropout):
        super().__init__()
        self.ln1 = nn.LayerNorm(embed_dim)
        self.attention = CausalSelfAttention(embed_dim, num_heads, block_size, dropout)
        self.ln2 = nn.LayerNorm(embed_dim)
        self.feed_forward = FeedForward(embed_dim, dropout)

    def forward(self, x):
        x = x + self.attention(self.ln1(x))
        x = x + self.feed_forward(self.ln2(x))
        return x


class TinyAMPTransformer(nn.Module):
    def __init__(self, block_size=64, embed_dim=64, num_heads=4, num_layers=2, dropout=0.10):
        super().__init__()
        self.block_size = block_size
        self.config = dict(block_size=block_size, embed_dim=embed_dim, num_heads=num_heads,
                           num_layers=num_layers, dropout=dropout)
        self.token_embedding = nn.Embedding(VOCAB_SIZE, embed_dim)
        self.position_embedding = nn.Embedding(block_size, embed_dim)
        self.dropout = nn.Dropout(dropout)
        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, block_size, dropout)
            for _ in range(num_layers)
        ])
        self.final_layer_norm = nn.LayerNorm(embed_dim)
        self.lm_head = nn.Linear(embed_dim, VOCAB_SIZE, bias=False)
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, token_ids):
        _, t = token_ids.shape
        if t > self.block_size:
            raise ValueError(f"sequence length {t} exceeds context {self.block_size}")
        positions = torch.arange(t, device=token_ids.device)
        x = self.token_embedding(token_ids) + self.position_embedding(positions)
        x = self.dropout(x)
        for block in self.blocks:
            x = block(x)
        return self.lm_head(self.final_layer_norm(x))
