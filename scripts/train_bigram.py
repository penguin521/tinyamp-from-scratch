#!/usr/bin/env python
import argparse, json, math, random
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from tinyamp.data import load_split_csv, encode
from tinyamp.model import VOCAB_SIZE

class BigramLanguageModel(nn.Module):
    def __init__(self):
        super().__init__(); self.next_token_logits=nn.Embedding(VOCAB_SIZE,VOCAB_SIZE)
    def forward(self, token_ids): return self.next_token_logits(token_ids)

def pairs(sequences):
    x=[]; y=[]
    for sequence in sequences:
        tokens=encode(sequence); x.extend(tokens[:-1]); y.extend(tokens[1:])
    return torch.tensor(x,dtype=torch.long),torch.tensor(y,dtype=torch.long)

def evaluate(model,x,y,device):
    model.eval()
    with torch.no_grad(): return F.cross_entropy(model(x.to(device)),y.to(device)).item()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--split',required=True); p.add_argument('--seed',type=int,default=42)
    p.add_argument('--steps',type=int,default=2000); p.add_argument('--lr',type=float,default=.05); p.add_argument('--output-dir',required=True)
    args=p.parse_args(); random.seed(args.seed); torch.manual_seed(args.seed)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); splits=load_split_csv(args.split)
    train_x,train_y=pairs(splits['train']); val_x,val_y=pairs(splits['val']); test_x,test_y=pairs(splits['test'])
    model=BigramLanguageModel().to(device); opt=torch.optim.AdamW(model.parameters(),lr=args.lr)
    for step in range(args.steps):
        model.train(); loss=F.cross_entropy(model(train_x.to(device)),train_y.to(device)); opt.zero_grad(); loss.backward(); opt.step()
        if step%200==0 or step==args.steps-1: print(f'step {step:4d} train {loss.item():.4f} val {evaluate(model,val_x,val_y,device):.4f}')
    losses={'train':evaluate(model,train_x,train_y,device),'val':evaluate(model,val_x,val_y,device),'test':evaluate(model,test_x,test_y,device)}
    result={'parameters':sum(p.numel() for p in model.parameters()),'loss':losses,'perplexity':{k:math.exp(v) for k,v in losses.items()}}
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True); (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    torch.save(model.state_dict(),out/'bigram.pt'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
