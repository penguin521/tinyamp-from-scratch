# Results

TinyAMP was developed as a sequence of controlled experiments. Each stage was motivated by a limitation or question raised by the previous one. The main finding is that **sequence context clearly improves peptide modeling, while increasing training-data quantity/diversity was more consistently useful than simply increasing model capacity**.

Throughout this document, the final split is called **similarity-aware**. Some archived scripts used the term "family-aware," but the clustering procedure is sequence-similarity based and should not be interpreted as curated biological-family annotation.

## 1. Longer sequence context improved next-token modeling

The first comparison used an 80/10/10 random sequence split.

| Model | Parameters | Test loss | Test perplexity |
|---|---:|---:|---:|
| Bigram | 484 | 2.8617 | 17.49 |
| TinyAMP-Small | 106,624 | 2.3459 | 10.44 |

Under the random split, TinyAMP-Small reduced test perplexity by approximately 40% relative to the bigram baseline.

**Interpretation:** information beyond the immediately preceding residue is useful for modeling these peptide sequences.

## 2. Random splitting produced strong near-neighbor overlap

The random split initially appeared successful, but sequence-similarity analysis showed that many validation and test peptides had close training relatives.

### Random split: held-out → nearest training sequence

| Split | Mean identity | Median identity | ≥80% | ≥90% |
|---|---:|---:|---:|---:|
| Validation | 0.706 | 0.783 | 47.9% | 30.6% |
| Test | 0.700 | 0.756 | 45.5% | 31.3% |

This made the random-split perplexity an optimistic measure of generalization to more distinct peptide sequences.

## 3. Similarity-aware splitting made evaluation harder

The approximate ≥80%-identity graph clustering produced:

- 2,113 components;
- 1,681 singleton components;
- largest component: 53 sequences;
- 2,644 training sequences;
- 331 validation sequences;
- 331 test sequences.

Approximate held-out verification produced:

| Split | Mean | Median | Maximum | Discovered ≥80% training neighbor |
|---|---:|---:|---:|---:|
| Validation | 0.564 | 0.600 | 0.795 | 0/331 |
| Test | 0.569 | 0.594 | 0.794 | 0/331 |

A single-seed TinyAMP-Small run reached test perplexity **12.59** on this split, compared with **10.44** on the original random split.

**Interpretation:** some of the apparent random-split performance was attributable to closely related sequences crossing split boundaries. The model still generalized, but the harder split exposed a meaningful performance penalty.

## 4. The contextual model still beat the bigram on the harder split

Using the same similarity-aware split:

| Model | Parameters | Test loss | Test perplexity |
|---|---:|---:|---:|
| Bigram | 484 | 2.8462 | 17.22 |
| TinyAMP-Small, single run | 106,624 | 2.5330 | 12.59 |

The Small Transformer reduced perplexity by 26.9% relative to the bigram on the similarity-aware test set.

**Interpretation:** the advantage of sequence context was not explained solely by random-split near-neighbor leakage.

## 5. A larger model overfit much faster

TinyAMP-Medium increased capacity from 106,624 to 805,632 parameters. In the first Medium run, validation performance peaked early while training loss continued to decrease.

| Medium checkpoint | Step | Test perplexity |
|---|---:|---:|
| Best validation checkpoint | 750 | 12.25 |
| Final checkpoint | 2,999 | 21.00 |

The final checkpoint made the larger model look substantially worse than Small, but selecting the best validation checkpoint recovered most of that performance.

**Interpretation:** checkpoint selection matters, especially for the larger model. The 805K-parameter model had enough capacity to fit the training set aggressively and overfit long before the 3,000-step budget was exhausted.

## 6. The apparent Medium advantage was not reproducible across seeds

Both Small and Medium were then trained with the same validation-based selection rule for seeds 42, 123, and 2026.

| Model | Seed 42 | Seed 123 | Seed 2026 | Mean ± SD |
|---|---:|---:|---:|---:|
| Small | 12.51 | 12.76 | 12.78 | **12.68 ± 0.15** |
| Medium | 12.64 | 12.79 | 12.44 | **12.62 ± 0.17** |

Medium was better in only one of the three matched seeds. Its mean test perplexity was only ~0.5% lower than Small.

The best-validation step differed much more strongly:

- Small mean best step: ~2,500;
- Medium mean best step: ~917.

**Interpretation:** increasing capacity from 106K to 806K parameters did not produce a consistent generalization improvement on this dataset, but it consistently accelerated fitting and overfitting.

With only three seeds, these results are descriptive rather than a formal significance test.

## 7. Stronger dropout delayed overfitting but did not improve average performance

TinyAMP-Medium was compared at dropout 0.10 and 0.20.

| Dropout | Mean test perplexity | SD | Mean best step |
|---|---:|---:|---:|
| 0.10 | **12.62** | 0.17 | 917 |
| 0.20 | 12.73 | 0.33 | 1,083 |

Dropout 0.20 produced a later best checkpoint by approximately 167 steps on average, but mean test perplexity worsened by ~0.8% and variability increased.

Seed-level comparison:

- seed 42: 12.64 → 13.03;
- seed 123: 12.79 → 12.78;
- seed 2026: 12.44 → 12.37.

**Interpretation:** stronger dropout had a measurable regularizing effect on training dynamics but did not unlock a reliable generalization advantage for the larger model.

## 8. More training data improved both architectures consistently

The clearest performance trend in TinyAMP came from increasing the amount of similarity-aware training data while keeping validation and test fixed.

| Training fraction | N train | Small | Medium |
|---|---:|---:|---:|
| 25% | 661 | 15.46 ± 0.20 | 16.54 ± 0.06 |
| 50% | 1,322 | 14.08 ± 0.19 | 14.02 ± 0.23 |
| 75% | 1,983 | 13.25 ± 0.10 | 13.36 ± 0.06 |
| 100% | 2,644 | **12.68 ± 0.15** | **12.62 ± 0.17** |

From 25% to 100% of the training set:

- Small improved by 18.0%;
- Medium improved by 23.7%.

The architecture gap changed with data quantity:

| Training fraction | Small | Medium | Relative Medium change | Medium seed wins |
|---|---:|---:|---:|---:|
| 25% | 15.46 | 16.54 | -7.0% | 0/3 |
| 50% | 14.08 | 14.02 | +0.4% | 2/3 |
| 75% | 13.25 | 13.36 | -0.8% | 1/3 |
| 100% | 12.68 | 12.62 | +0.5% | 1/3 |

At 25% data, the larger model was clearly disadvantaged. As more training data became available, Medium caught up, but it still did not establish a reproducible advantage over Small.

**Interpretation:** within the tested range, data quantity/diversity was a more reliable lever than additional model capacity. Medium also appeared more data-hungry than Small.

## 9. Generated sequences reproduced broad dataset statistics

The three independently trained best-validation Small models each generated 1,000 sequences at temperature 1.0, producing 3,000 outputs total.

### Dataset-level sequence statistics

| Property | Real APD | Generated, pooled |
|---|---:|---:|
| Mean length | 34.40 | 33.21 |
| Median length | 29 | 28 |
| Hydrophobic-residue fraction | 0.405 | 0.407 |
| Charged-residue balance `(K+R)-(D+E)` | 3.44 | 3.27 |

Broad statistics such as sequence length and hydrophobic-residue fraction were close to the source distribution.

These similarities are evidence that the model learned dataset-level sequence statistics. They are **not** evidence that generated peptides are antimicrobial.

## 10. Generation was highly diverse with very low exact training duplication

Across 3,000 generation attempts:

- 3,000 were non-empty;
- 3,000 were unique;
- 2 exactly matched a training sequence;
- 0 exactly matched a validation sequence;
- 0 exactly matched a test sequence;
- 0 generated sequences were shared across independently trained model seeds.

Exact training duplication was therefore approximately 0.07% of generated outputs.

**Interpretation:** straightforward exact memorization was rare and did not dominate sampling.

## 11. A small tail of generated sequences remained close to training examples

Approximate nearest-reference global-alignment identity was:

| Reference set | Mean | Median | Maximum | ≥80% | ≥90% |
|---|---:|---:|---:|---:|---:|
| Train | 0.449 | 0.405 | 1.000 | 3.4% | 0.4% |
| Validation | 0.377 | 0.364 | 0.786 | 0.0% | 0.0% |
| Test | 0.387 | 0.368 | 0.846 | 0.1% | 0.0% |

The training maximum of 1.000 reflects the two exact training matches. Most generated sequences were substantially below the 80% identity threshold, although a small high-similarity tail remained.

The higher nearest-training similarity should not be interpreted in isolation as a memorization statistic because the training reference set contains 2,644 sequences, while validation and test contain 331 each. Searching a larger reference set creates more opportunities to find a close neighbor.

## 12. Generation behavior was reasonably stable across training seeds

| Seed | Mean length | Hydrophobic fraction | Charge balance | Mean nearest-train identity | Unique |
|---|---:|---:|---:|---:|---:|
| 42 | 32.98 | 0.410 | 3.26 | 0.443 | 100% |
| 123 | 32.86 | 0.412 | 2.87 | 0.455 | 100% |
| 2026 | 33.80 | 0.399 | 3.69 | 0.450 | 100% |

Length, hydrophobic fraction, and nearest-training identity were similar across independently trained models. Charged-residue balance varied more noticeably.

## 13. Main conclusions

The experiments support four main conclusions:

1. **Sequence context matters.** A causal Transformer consistently modeled AMP sequences better than a bigram baseline.
2. **Split design matters.** Random sequence splitting produced substantial near-neighbor overlap and optimistic test performance.
3. **Bigger was not reliably better.** Increasing the Transformer from 106K to 806K parameters greatly accelerated overfitting but did not produce a reproducible generalization gain.
4. **More data helped consistently.** Both architectures improved monotonically as more similarity-aware training data was added, with the larger model benefiting especially strongly from increased data.

The generation analysis adds a fifth observation: independently trained Small models generated diverse sequences with broad statistics similar to the source dataset and very low exact training duplication.

## 14. What these results do not show

TinyAMP does not demonstrate that generated sequences:

- kill bacteria;
- are selective for bacteria over host cells;
- have favorable toxicity or hemolysis profiles;
- are stable in biological environments;
- adopt useful structures;
- are synthetically practical;
- are therapeutically useful.

Those questions require additional computational predictors and, ultimately, experimental validation that are outside the scope of this project.
