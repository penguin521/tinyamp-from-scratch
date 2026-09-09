# Dataset

TinyAMP uses natural antimicrobial-peptide sequences from the **Antimicrobial Peptide Database (APD)** maintained by the University of Nebraska Medical Center.

## Dataset used

The reported experiments used the 2024 natural AMP FASTA downloaded from the APD site.

| Item | Value |
|---|---|
| Local filename used during development | `naturalAMPs_APD2024a.fasta` |
| Raw FASTA sequences | 3,306 |
| Sequences retained after cleaning | 3,306 |
| Non-standard sequences removed | 0 |
| Exact duplicates removed | 0 |

The APD6 publication reports 3,306 natural AMPs in the refined database dataset as of March 2025. The official APD site should be treated as the authoritative source for current database content.

## Source

Official APD site:

https://aps.unmc.edu/

Official downloads page:

https://aps.unmc.edu/downloads

Primary database citation used by TinyAMP:

> Wang G, Schmidt C, Li X, Wang Z. APD6: the antimicrobial peptide database is expanded to promote research and development by deploying an unprecedented information pipeline. *Nucleic Acids Research.* 2026;54(D1):D363-D374. doi:10.1093/nar/gkaf860.

See [REFERENCES.md](REFERENCES.md) for the full reference list.

## Why the FASTA is not included in this repository

TinyAMP does **not** redistribute the APD FASTA. Users should obtain the dataset directly from the official APD source and follow the database's current terms, attribution, and citation guidance.

This also avoids creating a stale fork of a database that may be updated independently of this repository.

## Cleaning procedure

The cleaning step performs four checks:

1. strip surrounding whitespace;
2. convert sequence symbols to uppercase;
3. retain only non-empty sequences composed entirely of the 20 standard amino acids;
4. remove exact duplicate sequences while preserving one copy.

Accepted amino-acid alphabet:

`ACDEFGHIKLMNPQRSTVWY`

For the dataset used in the reported experiments, these filters did not remove any of the 3,306 sequences.

## Original random split

The earliest TinyAMP experiments used a sequence-level random split with seed 42:

- train: 2,644;
- validation: 330;
- test: 332.

This split was later retained only as a baseline because many held-out peptides were highly similar to training peptides.

## Final similarity-aware split

The final evaluation split was created to reduce obvious near-neighbor leakage.

The procedure used:

- unique 3-mer candidate indexing;
- up to 100 candidate neighbors per sequence during clustering;
- Needleman-Wunsch global alignment;
- an operational edge threshold of ≥80% aligned identity;
- connected components that were assigned intact to train, validation, or test.

Resulting component statistics:

| Statistic | Value |
|---|---:|
| Total connected components | 2,113 |
| Singleton components | 1,681 |
| Largest component | 53 sequences |

Final split:

| Split | Sequences |
|---|---:|
| Train | 2,644 |
| Validation | 331 |
| Test | 331 |
| Total | 3,306 |

Approximate post-split verification found no validation or test sequence with a discovered training neighbor at ≥80% identity using the same candidate-prefilter/alignment strategy.

## Why this is called "similarity-aware" rather than "family-aware"

Earlier development scripts used the phrase *family-aware split*. The public documentation uses **similarity-aware split** because:

- the grouping is based on an operational sequence-identity threshold;
- 3-mer candidate filtering is approximate;
- the method does not use curated AMP family annotations;
- sequence identity alone does not establish a biological family relationship.

The split is intended to make evaluation harder and reduce obvious near-duplicate leakage, not to provide a definitive homology partition.

## Data-scaling subsets

The data-scaling experiment used nested subsets of the training partition while holding validation and test fixed. Whole similarity components were added together so discovered components were not split across subset boundaries.

| Fraction | Training sequences | Components |
|---|---:|---:|
| 25% | 661 | 436 |
| 50% | 1,322 | 874 |
| 75% | 1,983 | 1,306 |
| 100% | 2,644 | 1,693 |

## Reproducing the split

After downloading the APD FASTA, the consolidated script can recreate the operational split:

```bash
python scripts/make_similarity_split.py \
  --fasta path/to/naturalAMPs_APD2024a.fasta \
  --output family_aware_split.csv
```

The historical output filename retains `family_aware_split.csv` for compatibility with the development versions. In documentation, it should be interpreted as the similarity-aware split described above.

## Dataset limitations relevant to interpretation

APD is a curated AMP database rather than a random sample of all possible peptides. Its natural sequences contain related peptide groups and dataset-specific biases. TinyAMP therefore learns the distribution represented by this source dataset.

The project does not include a matched non-AMP control dataset, activity labels per generated sequence, minimum inhibitory concentration targets, toxicity labels, or structural measurements. Consequently, the language-model results should not be interpreted as an AMP activity classifier or validated design pipeline.
