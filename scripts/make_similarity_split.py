#!/usr/bin/env python
"""Build and verify TinyAMP's approximate >=80%-identity similarity-aware split."""
import argparse, csv, random, statistics
from collections import Counter
from pathlib import Path
from tinyamp.data import read_fasta, clean_sequences
from tinyamp.similarity import build_kmer_index, kmers, global_alignment_identity, approximate_nearest_identity

class UnionFind:
    def __init__(self, n): self.parent=list(range(n)); self.rank=[0]*n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]; x = self.parent[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b: return
        if self.rank[a] < self.rank[b]: a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]: self.rank[a] += 1

def verify(queries, training, max_candidates=100):
    index=build_kmer_index(training,3); values=[]
    for i,q in enumerate(queries,1):
        identity,_=approximate_nearest_identity(q,training,index=index,k=3,max_candidates=max_candidates)
        values.append(identity)
        if i%100==0 or i==len(queries): print(f'  verify {i}/{len(queries)}')
    return {'mean':statistics.mean(values),'median':statistics.median(values),'max':max(values),
            'ge_threshold':sum(x>=.80 for x in values)}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--fasta', required=True); p.add_argument('--output', required=True)
    p.add_argument('--threshold', type=float, default=.80); p.add_argument('--seed', type=int, default=42)
    p.add_argument('--max-candidates', type=int, default=100); args=p.parse_args()
    sequences, stats = clean_sequences(read_fasta(args.fasta)); n=len(sequences)
    index=build_kmer_index(sequences,3); pairs=set()
    for i,seq in enumerate(sequences):
        counts=Counter()
        for kmer in kmers(seq,3):
            for j in index.get(kmer,[]):
                if j != i: counts[j]+=1
        for j,_ in counts.most_common(args.max_candidates): pairs.add((min(i,j),max(i,j)))
    uf=UnionFind(n); edges=0
    print(f'aligning {len(pairs):,} candidate pairs...')
    for k,(i,j) in enumerate(pairs,1):
        if global_alignment_identity(sequences[i],sequences[j]) >= args.threshold:
            uf.union(i,j); edges+=1
        if k%25000==0 or k==len(pairs): print(f'  {k:,}/{len(pairs):,} | qualifying edges {edges:,}')
    groups={}
    for i in range(n): groups.setdefault(uf.find(i),[]).append(i)
    clusters=list(groups.values()); rng=random.Random(args.seed); rng.shuffle(clusters); clusters.sort(key=len,reverse=True)
    targets={'train':.8*n,'val':.1*n,'test':.1*n}; counts={s:0 for s in targets}; assigned={}; tolerance=max(5,int(.02*n))
    records=[]
    for cid,cluster in enumerate(clusters):
        size=len(cluster); eligible=[s for s in targets if counts[s]+size <= targets[s]+tolerance]
        if not eligible: eligible=list(targets)
        split=max(eligible,key=lambda s:(targets[s]-counts[s])/targets[s])
        for i in cluster: assigned[i]=split
        counts[split]+=size; records.append((cid,cluster,split))
    cluster_id={i:cid for cid,c,_ in records for i in c}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as h:
        w=csv.writer(h); w.writerow(['sequence_index','sequence','length','cluster_id','split'])
        for i,seq in enumerate(sequences): w.writerow([i,seq,len(seq),cluster_id[i],assigned[i]])
    cluster_out=out.with_name(out.stem+'_clusters.csv')
    with cluster_out.open('w',newline='',encoding='utf-8') as h:
        w=csv.writer(h); w.writerow(['cluster_id','size','split'])
        for cid,c,split in records: w.writerow([cid,len(c),split])
    train=[sequences[i] for i in range(n) if assigned[i]=='train']; val=[sequences[i] for i in range(n) if assigned[i]=='val']; test=[sequences[i] for i in range(n) if assigned[i]=='test']
    print('cleaning:',stats); print('split counts:',counts)
    print('clusters:',len(clusters),'singletons:',sum(len(c)==1 for c in clusters),'largest:',max(map(len,clusters)))
    print('validation -> train verification'); val_v=verify(val,train,args.max_candidates)
    print('test -> train verification'); test_v=verify(test,train,args.max_candidates)
    print('validation:',val_v); print('test:',test_v)
    print('Note: candidate filtering makes this an approximate similarity-aware split, not a curated biological-family split.')
if __name__=='__main__': main()
