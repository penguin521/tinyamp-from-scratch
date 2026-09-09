#!/usr/bin/env python
"""Analyze generated TinyAMP sequences against a family-aware split."""
import argparse, csv, json, statistics
from pathlib import Path
from tinyamp.data import load_split_csv
from tinyamp.metrics import summarize_sequences
from tinyamp.similarity import build_kmer_index, approximate_nearest_identity

def read_generated(path):
    with Path(path).open(encoding='utf-8',newline='') as h:
        rows=list(csv.DictReader(h))
    return [r['sequence'].strip().upper() for r in rows if r.get('sequence','').strip()]

def sim_summary(queries,references):
    index=build_kmer_index(references,3); values=[]
    for i,q in enumerate(queries,1):
        identity,_=approximate_nearest_identity(q,references,index=index,k=3,max_candidates=40); values.append(identity)
        if i%100==0 or i==len(queries): print(f'  {i}/{len(queries)}')
    return {'mean':statistics.mean(values),'median':statistics.median(values),'max':max(values),
            'ge80_fraction':sum(v>=.8 for v in values)/len(values),'ge90_fraction':sum(v>=.9 for v in values)/len(values)}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--generated',required=True); p.add_argument('--split',required=True); p.add_argument('--output',required=True); args=p.parse_args()
    generated=read_generated(args.generated); splits=load_split_csv(args.split)
    sets={k:set(v) for k,v in splits.items()}; result={'generated':summarize_sequences(generated),'exact_matches':{k:sum(s in sets[k] for s in generated) for k in sets},'similarity':{}}
    for name in ['train','val','test']:
        print(f'{name} similarity'); result['similarity'][name]=sim_summary(generated,splits[name])
    Path(args.output).write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
