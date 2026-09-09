# Project history

TinyAMP was developed iteratively rather than designed as a fixed benchmark from the start. Each version answered a question raised by the previous experiment. This history is included because the progression itself is part of the project: the evaluation became more rigorous as weaknesses were discovered.

The consolidated 2.0 repository is the public-facing version. The older version numbers below refer to the local development experiments.

## v0 / v0.1 — Bigram baseline

**Question:** Can a minimal next-residue model learn useful sequence statistics?

A 22 × 22 learned bigram table was trained on the APD sequences. It conditions only on the immediately preceding token.

**Result:** random-split test perplexity = **17.49**.

**Why it mattered:** this established a deliberately weak baseline against which a contextual model could be evaluated.

## v1 — Small causal Transformer

**Question:** Does longer sequence context improve peptide modeling?

A 106,624-parameter decoder-only Transformer was implemented directly in PyTorch with a 64-token context window.

**Result:** random-split test perplexity = **10.44**, substantially below the bigram baseline.

**Next concern:** good perplexity alone did not show whether the model was learning broader peptide structure or exploiting closely related sequences across the random split.

## v1.1 — First generation and memorization analysis

**Question:** Do sampled sequences resemble the source distribution, and are they exact training copies?

Generation was analyzed for length, composition, hydrophobic-residue fraction, charged-residue balance, diversity, exact duplicates, and approximate nearest-training similarity.

**Finding:** broad sequence statistics matched the APD dataset closely and exact duplicates were rare, but some generated sequences were highly similar to training peptides.

**Next concern:** high similarity could represent memorization, or it could reflect redundancy/family structure already present in APD.

## v1.2 — Generated versus naturally held-out similarity

**Question:** Is generated-to-training similarity unusually high compared with real held-out APD peptides?

Generated, validation, and test sequences were each compared against the random-split training set.

**Finding:** naturally held-out validation/test peptides were much more similar to training than generated sequences. Random splitting had placed many close sequence relatives across partitions.

**Key lesson:** exact duplicate checks were insufficient, and random sequence splitting was an important methodological weakness.

## v1.3 — Similarity-aware split

**Question:** Can evaluation reduce obvious near-neighbor leakage?

Sequences were approximately clustered using shared 3-mer candidate retrieval, Needleman-Wunsch global alignment, an operational ≥80% identity edge threshold, and connected components.

The split contained 2,113 components, including 1,681 singletons. Whole components were assigned to train/validation/test.

**Finding:** held-out mean nearest-training identity dropped to ~0.56, with no discovered validation/test sequence at ≥80% identity to training under the same approximate verification procedure.

TinyAMP-Small test perplexity increased from **10.44** on the random split to **12.59** on the harder split.

**Terminology note:** development scripts called this "family-aware," but the public project calls it **similarity-aware** because it is not a curated biological-family partition.

## v1.4 — Bigram control and Medium scaling

**Questions:**

1. Does context still beat the bigram on the harder split?
2. Does increasing model capacity help?

The family/similarity-aware bigram reached **17.22** test perplexity, while Small reached **12.59**.

An 805,632-parameter Medium Transformer was also trained. Its final 3,000-step checkpoint had test perplexity **21.00**, apparently much worse than Small.

**Next concern:** validation loss showed that Medium had peaked much earlier, so the final checkpoint was not a fair representation of the larger model.

## v1.5 — Best-checkpoint evaluation

**Question:** Was Medium actually worse, or simply overtrained?

The saved best-validation Medium checkpoint from step 750 was evaluated without retraining.

**Result:** test perplexity = **12.25**, versus **21.00** for the final checkpoint.

**Key lesson:** the larger model could fit the dataset rapidly and required validation-based checkpoint selection.

**Next concern:** a single favorable run could be random variation.

## v1.6 — Repeated seeds

**Question:** Is the apparent Medium advantage reproducible?

Small and Medium were trained using matched seeds 42, 123, and 2026 with the same best-validation model-selection rule.

**Results:**

- Small: **12.68 ± 0.15** test perplexity;
- Medium: **12.62 ± 0.17**;
- Medium won only 1/3 paired seeds.

Medium reached its best validation checkpoint at step ~917 on average, compared with ~2,500 for Small.

**Key lesson:** the larger architecture overfit much sooner and did not provide a reproducible generalization advantage.

## v1.7 — Dropout regularization

**Question:** Can stronger dropout unlock the Medium model's additional capacity?

Medium dropout was increased from 0.10 to 0.20 while keeping the rest of the repeated-seed setup fixed.

**Results:**

- dropout 0.10: **12.62 ± 0.17**;
- dropout 0.20: **12.73 ± 0.33**.

The best checkpoint moved later by ~167 steps on average, but test performance did not improve.

**Key lesson:** stronger dropout affected overfitting dynamics but did not solve the generalization plateau.

## v1.8 — Training-data scaling

**Question:** Is performance more limited by training data than by parameter count?

Small and Medium were trained on nested, cluster-preserving 25%, 50%, 75%, and 100% fractions of the similarity-aware training set.

**Results:**

| Training fraction | Small | Medium |
|---|---:|---:|
| 25% | 15.46 ± 0.20 | 16.54 ± 0.06 |
| 50% | 14.08 ± 0.19 | 14.02 ± 0.23 |
| 75% | 13.25 ± 0.10 | 13.36 ± 0.06 |
| 100% | 12.68 ± 0.15 | 12.62 ± 0.17 |

Both architectures improved monotonically with more training data. From 25% to 100%, Small improved 18.0% and Medium improved 23.7%.

**Key lesson:** additional training data was the most consistent source of improved generalization. Medium appeared especially data-hungry.

## v1.9 — Final generation analysis

**Question:** What do the validation-selected Small models generate under the improved experimental setup?

The three Small checkpoints from v1.6 generated 1,000 sequences each.

**Results:**

- 3,000/3,000 outputs were unique;
- 2 exact training matches;
- 0 exact validation/test matches;
- mean generated length 33.21 versus 34.40 in the real dataset;
- mean hydrophobic-residue fraction 0.407 versus 0.405;
- mean approximate nearest-training identity 0.449;
- 3.4% of generated sequences had an approximate training neighbor at ≥80% identity.

**Key lesson:** generation was not dominated by exact memorization and reproduced broad dataset-level statistics, while a small high-similarity tail remained.

## v2.0 — Consolidation

**Goal:** turn the experimental sequence into a coherent, reproducible public project.

The 2.0 repository:

- consolidates reusable model/data/similarity code under `src/tinyamp/`;
- provides command-line scripts for training, split construction, generation, and analysis;
- summarizes the completed experiments in compact CSV files and figures;
- documents methods, results, dataset provenance, limitations, references, and related work;
- removes raw APD data and local model checkpoints from the public package.

No new biological claim is introduced by v2.0; it is a documentation and reproducibility release built from the v0–v1.9 experiments.

## Overall development lesson

The project began as "train a small Transformer on peptide sequences" and evolved into a study of **how evaluation choices change the conclusions of a small biological language-model experiment**.

The strongest final observations are:

- contextual modeling clearly beats a bigram baseline;
- random splitting can substantially overstate generalization when related biological sequences cross partitions;
- increasing model size does not reliably help when data are limited;
- larger models overfit earlier;
- additional training data improves both architectures consistently;
- generated sequences can reproduce broad source-distribution statistics without being dominated by exact training copies.
