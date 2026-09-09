from pathlib import Path
import csv
import random
import torch

AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")
VOCAB = ["<BOS>", "<EOS>"] + list("ACDEFGHIKLMNPQRSTVWY")
STOI = {token: i for i, token in enumerate(VOCAB)}
BOS_ID = STOI["<BOS>"]
EOS_ID = STOI["<EOS>"]
IGNORE_INDEX = -100


def read_fasta(path):
    path = Path(path)
    sequences, current = [], []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current:
                    sequences.append("".join(current))
                    current = []
            else:
                current.append(line)
    if current:
        sequences.append("".join(current))
    return sequences


def clean_sequences(sequences):
    cleaned, seen = [], set()
    stats = {"input": len(sequences), "empty": 0, "nonstandard": 0, "duplicates": 0}
    for sequence in sequences:
        sequence = sequence.strip().upper().replace(" ", "")
        if not sequence:
            stats["empty"] += 1
            continue
        if not set(sequence).issubset(AMINO_ACIDS):
            stats["nonstandard"] += 1
            continue
        if sequence in seen:
            stats["duplicates"] += 1
            continue
        seen.add(sequence)
        cleaned.append(sequence)
    stats["kept"] = len(cleaned)
    return cleaned, stats


def load_split_csv(path):
    splits = {"train": [], "val": [], "test": []}
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            split = row["split"].strip().lower()
            if split not in splits:
                raise ValueError(f"unexpected split: {split}")
            splits[split].append(row["sequence"].strip().upper())
    return splits


def random_split(sequences, seed=42, train_fraction=0.8, val_fraction=0.1):
    seqs = list(sequences)
    random.Random(seed).shuffle(seqs)
    n_train = int(len(seqs) * train_fraction)
    n_val = int(len(seqs) * val_fraction)
    return {"train": seqs[:n_train], "val": seqs[n_train:n_train+n_val], "test": seqs[n_train+n_val:]}


def encode(sequence):
    return [BOS_ID] + [STOI[aa] for aa in sequence] + [EOS_ID]


def build_windows(sequences, block_size=64):
    xs, ys = [], []
    for sequence in sequences:
        tokens = encode(sequence)
        for start in range(0, len(tokens) - 1, block_size):
            chunk = tokens[start:start + block_size + 1]
            x, y = chunk[:-1], chunk[1:]
            pad = block_size - len(x)
            if pad:
                x = x + [EOS_ID] * pad
                y = y + [IGNORE_INDEX] * pad
            xs.append(x); ys.append(y)
    return torch.tensor(xs, dtype=torch.long), torch.tensor(ys, dtype=torch.long)
