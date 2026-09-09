# Related work and acknowledgments

## Positioning TinyAMP

TinyAMP is **not** presented as the first Transformer, protein language model, peptide generator, or GPT-style antimicrobial-peptide model. Those ideas predate this project.

The purpose of TinyAMP is narrower: implement a small causal sequence model from random initialization and use it to investigate **evaluation methodology in a small biological dataset**, especially:

- context versus a bigram baseline;
- near-neighbor leakage across train/test splits;
- small-versus-medium capacity scaling;
- overfitting and checkpoint selection;
- dropout regularization;
- training-data scaling;
- repeated-seed variability;
- generation diversity and similarity to source sequences.

That combination of questions is the project's main framing, rather than a claim of architectural novelty or validated peptide discovery.

## Related AMP and peptide language models

### AMP-Designer / AMP-GPT

Wang et al. developed AMP-Designer around an AMP-focused language-model foundation model (AMP-GPT), trained on a much larger peptide corpus and combined with prompt tuning, property prediction, optimization, and experimental validation.

TinyAMP differs in purpose and scale:

- TinyAMP trains from random initialization on 3,306 APD natural AMP sequences;
- it uses 106K- and 806K-parameter models rather than a foundation-model-scale workflow;
- it does not optimize generated sequences for a target organism or MIC;
- it does not perform wet-lab validation;
- its central focus is how split design, data quantity, model capacity, and memorization affect evaluation.

Reference: Wang J et al., *Science Advances* (2025), doi:10.1126/sciadv.ads8932.

### BroadAMP-GPT

BroadAMP-GPT combines GPT-based generation, multi-stage computational screening, and experimental validation to discover broad-spectrum AMP candidates.

TinyAMP does not attempt to reproduce this therapeutic design workflow. The TinyAMP generation analysis asks only whether a small sequence model reproduces broad statistical properties of its source dataset and how closely generated outputs resemble reference sequences.

Reference: Li Y et al., *Gut Microbes* (2025), doi:10.1080/19490976.2025.2523811.

### Peptide-GPT

Peptide-GPT fine-tunes pretrained ProtGPT2 for property-specific peptide/protein generation and applies bioinformatic/structural filtering.

TinyAMP instead:

- uses single-amino-acid tokens;
- trains from random initialization;
- uses no pretrained protein model;
- is orders of magnitude smaller;
- studies generalization and dataset structure rather than property-conditioned generation.

Reference: Shah A, Guntuboina C, Barati Farimani A., arXiv:2410.19222 (2024).

## Architectural foundations

TinyAMP uses standard decoder-only Transformer ideas: causal self-attention, learned embeddings, residual connections, LayerNorm, feed-forward blocks, and autoregressive next-token prediction. These concepts derive from the Transformer/GPT literature and are not claimed as original contributions.

The foundational architecture reference is:

> Vaswani A et al. *Attention Is All You Need.* NeurIPS 2017.

## Educational implementation references

Andrej Karpathy's educational GPT materials, including `nanoGPT` and the "Let's build GPT" walkthrough, were consulted while learning how causal Transformers are implemented in PyTorch.

TinyAMP's implementation is maintained as its own small codebase for this project. It does not import or depend on nanoGPT, and its peptide data pipeline, similarity-aware split, experimental comparisons, and analysis code are specific to TinyAMP.

Acknowledging educational references is intentional: the project claims independent implementation and experimentation, not invention of the underlying Transformer architecture.

## Dataset acknowledgment

TinyAMP relies on the Antimicrobial Peptide Database (APD) maintained at the University of Nebraska Medical Center. The APD dataset is not redistributed in this repository. Users should obtain the data from the official APD site and cite the database appropriately.

Primary reference:

> Wang G, Schmidt C, Li X, Wang Z. *APD6: the antimicrobial peptide database is expanded to promote research and development by deploying an unprecedented information pipeline.* Nucleic Acids Research. 2026;54(D1):D363-D374. doi:10.1093/nar/gkaf860.

## AI-assisted development disclosure

ChatGPT was used during the development of TinyAMP as a coding and writing assistant for activities including experiment planning, debugging, refactoring, interpretation checks, and documentation drafting.

The experiments reported in the project were run locally by the project author, and the resulting outputs were reviewed and used to decide the next experimental steps. Responsibility for the repository, reported numbers, interpretation, and any errors remains with the project author.

This disclosure is included to make the development process transparent; AI assistance is not presented as independent scientific validation.

## What TinyAMP claims

A defensible one-sentence description is:

> TinyAMP is an independently implemented educational peptide language-model project that studies how sequence context, similarity-aware evaluation, model capacity, data quantity, and memorization affect a small autoregressive Transformer trained on natural AMP sequences.

## What TinyAMP does not claim

TinyAMP does not claim:

- invention of Transformers or GPT-style protein/peptide modeling;
- state-of-the-art AMP generation;
- discovery of experimentally active antimicrobial peptides;
- novelty of using autoregressive models on amino-acid sequences;
- biological validation of generated sequences.

For formal citations, see [REFERENCES.md](REFERENCES.md).
