#!/usr/bin/env python
import argparse, csv, random
from pathlib import Path
import torch
import torch.nn.functional as F
from tinyamp.model import TinyAMPTransformer, BOS_ID, EOS_ID, ITOS
from tinyamp.metrics import hydrophobic_fraction, charge_balance

@torch.no_grad()
def sample(model, device, n, temperature, max_length, seed):
    generator=torch.Generator(device=device).manual_seed(seed)
    outputs=[]
    for _ in range(n):
        tokens=torch.tensor([[BOS_ID]],device=device)
        residues=[]
        for _ in range(max_length):
            logits=model(tokens[:,-model.block_size:])[:,-1,:] / temperature
            logits[:, BOS_ID] = float('-inf')
            next_id=int(torch.multinomial(F.softmax(logits,dim=-1),1,generator=generator))
            if next_id == EOS_ID: break
            token=ITOS[next_id]
            if len(token)==1: residues.append(token)
            tokens=torch.cat([tokens,torch.tensor([[next_id]],device=device)],dim=1)
        outputs.append(''.join(residues))
    return outputs

def main():
    p=argparse.ArgumentParser(); p.add_argument('--checkpoint',required=True); p.add_argument('--output',required=True)
    p.add_argument('--n',type=int,default=1000); p.add_argument('--temperature',type=float,default=1.0)
    p.add_argument('--max-length',type=int,default=183); p.add_argument('--seed',type=int,default=42); args=p.parse_args()
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    ckpt=torch.load(args.checkpoint,map_location=device,weights_only=False)
    model=TinyAMPTransformer(**ckpt['config']).to(device); model.load_state_dict(ckpt['model_state_dict']); model.eval()
    outputs=sample(model,device,args.n,args.temperature,args.max_length,args.seed+900000)
    with Path(args.output).open('w',newline='',encoding='utf-8') as h:
        w=csv.writer(h); w.writerow(['sequence','length','hydrophobic_fraction','charge_balance'])
        for s in outputs: w.writerow([s,len(s),hydrophobic_fraction(s),charge_balance(s)])
    print(f'generated {len(outputs)} sequences; unique={len(set(outputs))}')

if __name__ == '__main__': main()
