# Methods

This document describes the methods used for the results reported in TinyAMP 2.0. TinyAMP was developed iteratively, so some archived version scripts used slightly different training behavior; the consolidated scripts in this repository represent the final reusable workflow.

## 1. Study design

TinyAMP asks how much useful sequence structure a small autoregressive language model can learn from a relatively small antimicrobial-peptide dataset. The experiments were organized around five questions:

1. Does longer sequence context improve next-residue prediction over a bigram baseline?
2. How much does random sequence splitting benefit from closely related peptides appearing across train and test sets?
3. Does increasing Transformer capacity improve generalization after reducing near-neighbor leakage?
4. Can stronger regularization prevent the larger model from overfitting, or is training-data quantity a more important constraint?
5. Do independently trained models generate diverse peptide-like sequences without being dominated by exact reproduction of the training set?

The project is a sequence-modeling study. It does not test antimicrobial activity, toxicity, stability, structure, selectivity, or therapeutic utility.

## 2. Dataset and preprocessing

The reported experiments used the 2024 natural antimicrobial-peptide FASTA downloaded from the Antimicrobial Peptide Database (APD), locally named `naturalAMPs_APD2024a.fasta`.

The file contained 3,306 sequences. Cleaning was performed before splitting:

- sequences were uppercased and whitespace was removed;
- empty sequences were discarded;
- only the 20 standard amino-acid symbols `ACDEFGHIKLMNPQRSTVWY` were accepted;
- exact duplicate sequences were removed.

For the reported dataset, all 3,306 sequences were retained: no non-standard sequences or exact duplicates were removed.

See [DATASET.md](DATASET.md) for source, redistribution, and split details.

## 3. Tokenization

Sequences were modeled at single-amino-acid resolution. The vocabulary contains 22 tokens:

- 20 standard amino acids;
- `<BOS>` for beginning of sequence;
- `<EOS>` for end of sequence.

No BPE, learned tokenizer, pretrained protein vocabulary, or external embedding model was used.

## 4. Autoregressive objective

TinyAMP is trained as a causal next-token model. For a token sequence \(x_1, \ldots, x_T\), the model estimates the probability of each next token conditioned on the preceding tokens. Training minimizes categorical cross-entropy over non-padding targets.

Perplexity is reported as:

`perplexity = exp(mean cross-entropy loss)`

Lower perplexity indicates better next-token prediction under the evaluated distribution.

## 5. Bigram baseline

The baseline is a learned 22 × 22 next-token logit table implemented as an embedding layer. It contains 484 trainable parameters and conditions only on the immediately preceding token.

For the similarity-aware comparison, the bigram was trained for 2,000 optimization steps with AdamW and a learning rate of 0.05.

## 6. Transformer architecture

TinyAMP uses a decoder-only causal Transformer implemented directly with PyTorch modules. Each model contains:

- learned token embeddings;
- learned positional embeddings;
- causal multi-head self-attention;
- separate query, key, and value projections;
- pre-LayerNorm residual blocks;
- a feed-forward network with 4× hidden expansion;
- GELU activation;
- dropout;
- a final LayerNorm;
- a linear language-model head over the 22-token vocabulary.

### TinyAMP-Small

| Setting | Value |
|---|---:|
| Parameters | 106,624 |
| Context length | 64 tokens |
| Embedding dimension | 64 |
| Attention heads | 4 |
| Transformer blocks | 2 |
| Default dropout | 0.10 |

### TinyAMP-Medium

| Setting | Value |
|---|---:|
| Parameters | 805,632 |
| Context length | 64 tokens |
| Embedding dimension | 128 |
| Attention heads | 4 |
| Transformer blocks | 4 |
| Default dropout | 0.10 |

The project does not use pretrained model weights or transfer learning.

## 7. Sequence windows and masking

Each peptide is encoded with `<BOS>` and `<EOS>`. For Transformer training, encoded sequences are divided into windows of at most 64 input tokens. The target sequence is shifted by one token. Short windows are padded for batching, and padded target positions use an ignore index so they do not contribute to cross-entropy loss.

Long peptides can therefore contribute more than one 64-token training window.

## 8. Original random split

The first experiments used an exact sequence-level random 80/10/10 split with seed 42. This was useful as an initial baseline but later proved optimistic because highly similar APD peptides could appear in different partitions.

The original split contained:

- 2,644 training sequences;
- 330 validation sequences;
- 332 test sequences.

## 9. Similarity-aware split

To reduce obvious near-neighbor leakage, TinyAMP later introduced an approximate sequence-similarity split. Archived scripts referred to this as a "family-aware" split, but the public repository uses **similarity-aware** because the procedure does not define biological families.

### 9.1 Candidate discovery

A 3-mer inverted index was built over all cleaned sequences. For each sequence, candidate neighbors were ranked by the number of shared unique 3-mers. Up to 100 candidate neighbors per sequence were considered during clustering.

### 9.2 Pairwise alignment

Candidate pairs were globally aligned with a simple Needleman-Wunsch implementation using:

- match: +1;
- mismatch: -1;
- gap: -1.

Alignment identity was defined as exact aligned residue matches divided by alignment length.

### 9.3 Graph clustering

An undirected edge was created when a candidate pair had global-alignment identity ≥ 0.80. Connected components were formed with union-find. Entire components were then assigned to train, validation, or test so that no discovered component was split across partitions.

The resulting split contained:

- 2,113 connected components;
- 1,681 singleton components;
- largest component: 53 sequences;
- train: 2,644 sequences;
- validation: 331 sequences;
- test: 331 sequences.

### 9.4 Verification

Validation and test sequences were approximately re-queried against the training set using shared 3-mers followed by global alignment. Under this verification procedure, no validation or test sequence had a discovered training neighbor at ≥80% identity. Mean nearest-training identity was 0.564 for validation and 0.569 for test.

This method is deliberately described as **approximate**: candidate prefiltering can miss related pairs, and an 80% global-identity threshold is an operational criterion rather than a universal biological-family definition.

## 10. Transformer training

The main similarity-aware Transformer experiments used:

| Setting | Value |
|---|---:|
| Optimizer | AdamW |
| Learning rate | 3e-4 |
| Weight decay | 0.01 |
| Batch size | 128 windows |
| Maximum steps | 3,000 |
| Validation interval | 250 steps |
| Gradient clipping | 1.0 |
| Default dropout | 0.10 |

Training batches were sampled randomly from the training windows. The best model checkpoint was selected by lowest validation loss.

Later experiments used early stopping after six consecutive validation evaluations without improvement. Because validation was performed every 250 steps, this corresponds to a patience of up to approximately 1,500 additional training steps after the last improvement.

## 11. Repeated-seed experiment

To test whether the apparent Small-versus-Medium difference was reproducible, both models were trained with matched seeds:

- 42;
- 123;
- 2026.

Both architectures used the same similarity-aware split and the same best-validation checkpoint rule. Reported mean ± SD values use the arithmetic mean and sample standard deviation across these three runs. No formal hypothesis test was performed; the three-seed analysis is descriptive.

## 12. Dropout experiment

TinyAMP-Medium was evaluated with dropout 0.10 and 0.20. The 0.10 runs were reused from the repeated-seed experiment, and only the 0.20 models were newly trained. All other architecture, split, seed, optimizer, checkpoint-selection, and early-stopping settings were kept the same.

This isolates dropout as the intended experimental change.

## 13. Training-data scaling

Training-data scaling used nested, cluster-preserving subsets of the similarity-aware training partition. Validation and test sets remained fixed.

| Training fraction | Sequences | Similarity components |
|---|---:|---:|
| 25% | 661 | 436 |
| 50% | 1,322 | 874 |
| 75% | 1,983 | 1,306 |
| 100% | 2,644 | 1,693 |

Small and Medium were trained across the same three seeds at 25%, 50%, and 75%. The 100% results were reused from the repeated-seed experiment.

Because the subsets are nested, larger fractions contain the sequences/components from smaller fractions plus additional training components.

## 14. Generation

The final generation analysis used the three best-validation TinyAMP-Small checkpoints from the repeated-seed experiment.

For each training seed:

- 1,000 sequences were sampled;
- temperature = 1.0;
- generation started from `<BOS>`;
- sampling continued autoregressively until `<EOS>` or the maximum length;
- maximum generated length = 183 residues.

This produced 3,000 generation attempts in total.

## 15. Generated-sequence statistics

Generated sequences were compared with the complete 3,306-sequence APD dataset using:

### Length

Number of amino-acid residues in the decoded sequence.

### Amino-acid composition

Frequency of each of the 20 standard amino acids across pooled sequences.

### Hydrophobic-residue fraction

Fraction of residues belonging to:

`AVILMFWY`

This is a simple sequence-level descriptor, not a structural hydrophobicity calculation.

### Charged-residue balance

Defined as:

`(K + R) - (D + E)`

This is a simple residue-count balance and should not be interpreted as a molecular net charge at a specified pH.

### Diversity and exact matches

The analysis counted:

- unique generated sequences;
- duplicate generated outputs;
- exact matches to training sequences;
- exact matches to validation sequences;
- exact matches to test sequences;
- sequences generated independently by more than one model seed.

## 16. Approximate nearest-sequence analysis

Generated sequences were separately compared against training, validation, and test references. Candidate references were prefiltered by shared 3-mers, with up to 40 candidates globally aligned per generated sequence. The highest discovered global-alignment identity was recorded.

Because candidate filtering is approximate, these values are **approximate nearest-reference identities**, not guaranteed exhaustive nearest neighbors.

Similarity values should also not be compared naively across train, validation, and test because the training reference set is much larger (2,644 sequences) than validation or test (331 each). A larger reference set has more opportunities to contain a close neighbor.

## 17. Software and hardware

The reported experiments were run locally with:

- Python;
- PyTorch 2.13.0+cu126;
- CUDA-enabled training;
- NVIDIA GeForce RTX 3050 Laptop GPU with 4 GB VRAM.

The consolidated repository requires Python 3.10+ and lists PyTorch and Matplotlib as dependencies.

## 18. Reproducibility boundaries

The repository includes reusable implementations and compact result summaries, but it intentionally does not redistribute:

- the APD FASTA;
- trained checkpoint files;
- every intermediate artifact from the exploratory v0–v1.9 development folders.

The public scripts reproduce the final methods, while [PROJECT_HISTORY.md](PROJECT_HISTORY.md) documents how the experimental design evolved.
