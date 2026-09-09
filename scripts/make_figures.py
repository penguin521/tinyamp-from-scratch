#!/usr/bin/env python
from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'; FIGS=RESULTS/'figures'; FIGS.mkdir(exist_ok=True)

def read_csv(name):
    with (RESULTS/name).open(encoding='utf-8',newline='') as h: return list(csv.DictReader(h))

# Family-aware model comparison
rows=read_csv('experiment_summary.csv')
selected=[r for r in rows if r['figure_group']=='family_models']
plt.figure(figsize=(7,5))
plt.bar([r['label'] for r in selected],[float(r['test_perplexity']) for r in selected],
        yerr=[float(r['sd']) if r['sd'] else 0 for r in selected],capsize=6)
plt.ylabel('Family-aware test perplexity'); plt.title('TinyAMP Model Comparison'); plt.tight_layout()
plt.savefig(FIGS/'family_aware_models.png',dpi=180); plt.close()

# Data scaling
rows=read_csv('data_scaling.csv')
plt.figure(figsize=(8,5))
for model in ['Small','Medium']:
    sub=[r for r in rows if r['model']==model]
    plt.errorbar([int(r['fraction_pct']) for r in sub],[float(r['mean_test_perplexity']) for r in sub],
                 yerr=[float(r['sd']) for r in sub],marker='o',capsize=4,label=model)
plt.xlabel('Training data (%)'); plt.ylabel('Family-aware test perplexity'); plt.title('Training-Data Scaling'); plt.legend(); plt.tight_layout()
plt.savefig(FIGS/'data_scaling.png',dpi=180); plt.close()

# Dropout
rows=read_csv('dropout.csv')
plt.figure(figsize=(7,5))
plt.bar([f"dropout {r['dropout']}" for r in rows],[float(r['mean_test_perplexity']) for r in rows],
        yerr=[float(r['sd']) for r in rows],capsize=6)
plt.ylabel('Family-aware test perplexity'); plt.title('Medium Transformer Regularization'); plt.tight_layout()
plt.savefig(FIGS/'dropout.png',dpi=180); plt.close()

# Generation real vs generated property charts (separate figures)
gen=read_csv('generation_summary.csv')
for metric,title,ylabel,out in [
    ('mean_length','Sequence Length','Mean residues','generation_length.png'),
    ('hydrophobic_fraction','Hydrophobic Fraction','Mean fraction','generation_hydrophobic.png'),
    ('charge_balance','Charged-Residue Balance','Mean (K+R)-(D+E)','generation_charge.png')]:
    plt.figure(figsize=(6,5)); plt.bar([r['group'] for r in gen],[float(r[metric]) for r in gen])
    plt.ylabel(ylabel); plt.title(title); plt.tight_layout(); plt.savefig(FIGS/out,dpi=180); plt.close()
print(f'Wrote figures to {FIGS}')
