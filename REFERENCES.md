# References

This page lists the sources most directly relevant to TinyAMP. It is not intended as a comprehensive review of protein or peptide language modeling.

## Dataset

### Antimicrobial Peptide Database, APD6

Wang G, Schmidt C, Li X, Wang Z. **APD6: the antimicrobial peptide database is expanded to promote research and development by deploying an unprecedented information pipeline.** *Nucleic Acids Research.* 2026;54(D1):D363-D374. doi:[10.1093/nar/gkaf860](https://doi.org/10.1093/nar/gkaf860)

- APD: https://aps.unmc.edu/
- Downloads: https://aps.unmc.edu/downloads

TinyAMP's reported dataset was obtained from the APD natural-AMP download.

### Earlier APD reference

Wang G, Li X, Wang Z. **APD3: the antimicrobial peptide database as a tool for research and education.** *Nucleic Acids Research.* 2016;44(D1):D1087-D1093. doi:[10.1093/nar/gkv1278](https://doi.org/10.1093/nar/gkv1278)

## Transformer foundation

Vaswani A, Shazeer N, Parmar N, Uszkoreit J, Jones L, Gomez AN, Kaiser Ł, Polosukhin I. **Attention Is All You Need.** *Advances in Neural Information Processing Systems.* 2017;30. arXiv:[1706.03762](https://arxiv.org/abs/1706.03762)

TinyAMP uses the standard causal self-attention/Transformer building blocks established by this line of work.

## Educational implementation reference

Karpathy A. **nanoGPT.** GitHub repository. https://github.com/karpathy/nanoGPT

Karpathy A. **Let's build GPT: from scratch, in code, spelled out.** Educational lecture/code walkthrough, 2023. https://www.youtube.com/watch?v=kCc8FmEb1nY

These materials were used as educational references while learning causal Transformer implementation. TinyAMP's repository contains its own compact PyTorch implementation and does not import or depend on nanoGPT.

## Related peptide / AMP language-model work

### AMP-Designer / AMP-GPT

Wang J, Feng J, Kang Y, Pan P, Ge J, Wang Y, Wang M, Wu Z, Zhang X, Yu J, et al. **Discovery of antimicrobial peptides with notable antibacterial potency by an LLM-based foundation model.** *Science Advances.* 2025;11(10):eads8932. doi:[10.1126/sciadv.ads8932](https://doi.org/10.1126/sciadv.ads8932)

This work uses a much larger AMP-focused foundation-model workflow, including AMP-GPT, downstream conditioning/optimization, and experimental validation. TinyAMP does not attempt to reproduce that design-and-validation pipeline.

### BroadAMP-GPT

Li Y, Xu X, Zhang X, Xu Z, Zhao J, Zhu R, Wang Z, Ran W, Zhao W, Yan N, et al. **BroadAMP-GPT: AI-Driven generation of broad-spectrum antimicrobial peptides for combating multidrug-resistant ESKAPE pathogens.** *Gut Microbes.* 2025;17(1):2523811. doi:[10.1080/19490976.2025.2523811](https://doi.org/10.1080/19490976.2025.2523811)

BroadAMP-GPT combines GPT-based AMP generation with downstream screening and experimental validation. TinyAMP is smaller, trains only on the APD natural-AMP dataset, and focuses on evaluation methodology rather than therapeutic discovery.

### Peptide-GPT

Shah A, Guntuboina C, Barati Farimani A. **Peptide-GPT: Generative Design of Peptides using Generative Pre-trained Transformers and Bio-informatic Supervision.** arXiv preprint, 2024. arXiv:[2410.19222](https://arxiv.org/abs/2410.19222)

Peptide-GPT fine-tunes pretrained ProtGPT2 for property-specific peptide/protein generation and applies downstream bioinformatic filtering. TinyAMP instead trains a much smaller amino-acid-level Transformer from random initialization and studies data leakage, capacity, regularization, data scaling, and memorization.

## Scope of citation and novelty

TinyAMP does **not** claim to introduce Transformers, protein language modeling, or GPT-based antimicrobial-peptide generation. Its contribution is the project's specific educational and experimental framing: building a small model from scratch and systematically examining sequence context, similarity-aware evaluation, capacity scaling, overfitting, data scaling, and generation similarity on a small AMP dataset.

See [RELATED_WORK.md](RELATED_WORK.md) for a more explicit comparison and acknowledgment statement.
