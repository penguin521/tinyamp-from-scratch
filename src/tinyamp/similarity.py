from collections import Counter, defaultdict


def kmers(sequence, k=3):
    if len(sequence) < k:
        return set()
    return {sequence[i:i+k] for i in range(len(sequence)-k+1)}


def build_kmer_index(sequences, k=3):
    index = defaultdict(list)
    for idx, sequence in enumerate(sequences):
        for kmer in kmers(sequence, k):
            index[kmer].append(idx)
    return index


def global_alignment_identity(a, b):
    """Needleman-Wunsch global identity; match +1, mismatch/gap -1."""
    n, m = len(a), len(b)
    if n == 0 and m == 0:
        return 1.0
    if n == 0 or m == 0:
        return 0.0
    score = [[0]*(m+1) for _ in range(n+1)]
    trace = [[0]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1): score[i][0], trace[i][0] = -i, 1
    for j in range(1, m+1): score[0][j], trace[0][j] = -j, 2
    for i in range(1, n+1):
        for j in range(1, m+1):
            diag = score[i-1][j-1] + (1 if a[i-1] == b[j-1] else -1)
            up = score[i-1][j] - 1
            left = score[i][j-1] - 1
            best = max(diag, up, left)
            score[i][j] = best
            trace[i][j] = 0 if best == diag else (1 if best == up else 2)
    i, j, matches, aligned = n, m, 0, 0
    while i > 0 or j > 0:
        direction = trace[i][j]
        if i > 0 and j > 0 and direction == 0:
            matches += int(a[i-1] == b[j-1]); i -= 1; j -= 1
        elif i > 0 and (j == 0 or direction == 1):
            i -= 1
        else:
            j -= 1
        aligned += 1
    return matches / aligned if aligned else 0.0


def candidate_indices(query, references, index, k=3, max_candidates=40):
    counts = Counter()
    for kmer in kmers(query, k):
        for idx in index.get(kmer, []):
            counts[idx] += 1
    if counts:
        return [idx for idx, _ in counts.most_common(max_candidates)]
    return sorted(range(len(references)), key=lambda i: abs(len(references[i])-len(query)))[:10]


def approximate_nearest_identity(query, references, index=None, k=3, max_candidates=40):
    if index is None:
        index = build_kmer_index(references, k)
    candidates = candidate_indices(query, references, index, k, max_candidates)
    best_identity, best_idx = -1.0, None
    for idx in candidates:
        identity = global_alignment_identity(query, references[idx])
        if identity > best_identity:
            best_identity, best_idx = identity, idx
    return best_identity, best_idx
