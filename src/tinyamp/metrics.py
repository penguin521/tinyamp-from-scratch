from collections import Counter
import statistics

HYDROPHOBIC = set("AVILMFWY")
POSITIVE = set("KR")
NEGATIVE = set("DE")
AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")


def hydrophobic_fraction(sequence):
    if not sequence:
        return None
    return sum(aa in HYDROPHOBIC for aa in sequence) / len(sequence)


def charge_balance(sequence):
    return sum(aa in POSITIVE for aa in sequence) - sum(aa in NEGATIVE for aa in sequence)


def amino_acid_frequencies(sequences):
    counts = Counter()
    for seq in sequences:
        counts.update(seq)
    total = sum(counts.values())
    return {aa: (counts[aa] / total if total else 0.0) for aa in AMINO_ACIDS}


def summarize_sequences(sequences):
    nonempty = [s for s in sequences if s]
    lengths = [len(s) for s in nonempty]
    hydrophobic = [hydrophobic_fraction(s) for s in nonempty]
    charge = [charge_balance(s) for s in nonempty]
    return {
        "count": len(nonempty),
        "unique": len(set(nonempty)),
        "mean_length": statistics.mean(lengths) if lengths else None,
        "median_length": statistics.median(lengths) if lengths else None,
        "mean_hydrophobic_fraction": statistics.mean(hydrophobic) if hydrophobic else None,
        "mean_charge_balance": statistics.mean(charge) if charge else None,
    }
