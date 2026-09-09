#!/usr/bin/env python
import argparse, json, math, random
from pathlib import Path
import torch
import torch.nn.functional as F
from tinyamp.data import load_split_csv, build_windows, IGNORE_INDEX
from tinyamp.model import TinyAMPTransformer, model_config, VOCAB_SIZE, VOCAB


def evaluate(model, x, y, device, batch_size=256):
    model.eval(); total_loss = 0.0; total_tokens = 0
    with torch.no_grad():
        for start in range(0, len(x), batch_size):
            xb, yb = x[start:start+batch_size].to(device), y[start:start+batch_size].to(device)
            logits = model(xb)
            loss = F.cross_entropy(logits.reshape(-1, VOCAB_SIZE), yb.reshape(-1),
                                   ignore_index=IGNORE_INDEX, reduction="sum")
            tokens = int((yb != IGNORE_INDEX).sum())
            total_loss += loss.item(); total_tokens += tokens
    return total_loss / total_tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", required=True)
    parser.add_argument("--model", choices=["small", "medium"], default="small")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--eval-interval", type=int, default=250)
    parser.add_argument("--patience", type=int, default=6)
    parser.add_argument("--dropout", type=float, default=None)
    args = parser.parse_args()

    random.seed(args.seed); torch.manual_seed(args.seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = model_config(args.model)
    if args.dropout is not None: config["dropout"] = args.dropout
    splits = load_split_csv(args.split)
    train_x, train_y = build_windows(splits["train"], config["block_size"])
    val_x, val_y = build_windows(splits["val"], config["block_size"])
    test_x, test_y = build_windows(splits["test"], config["block_size"])

    model = TinyAMPTransformer(**config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    generator = torch.Generator(device="cpu").manual_seed(args.seed + 100000)
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output / "best.pt"
    best_val, best_step, stale = float("inf"), None, 0
    history = []

    print(f"device={device} parameters={sum(p.numel() for p in model.parameters()):,}")
    for step in range(args.steps):
        model.train()
        idx = torch.randint(0, len(train_x), (args.batch_size,), generator=generator)
        xb, yb = train_x[idx].to(device), train_y[idx].to(device)
        logits = model(xb)
        loss = F.cross_entropy(logits.reshape(-1, VOCAB_SIZE), yb.reshape(-1), ignore_index=IGNORE_INDEX)
        optimizer.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); optimizer.step()
        if step % args.eval_interval == 0 or step == args.steps - 1:
            val_loss = evaluate(model, val_x, val_y, device)
            improved = val_loss < best_val
            if improved:
                best_val, best_step, stale = val_loss, step, 0
                torch.save({"model_state_dict": model.state_dict(), "config": config, "vocab": VOCAB,
                            "seed": args.seed, "training_step": step, "validation_loss": val_loss}, checkpoint_path)
            else:
                stale += 1
            history.append({"step": step, "train_batch_loss": loss.item(), "val_loss": val_loss, "best": improved})
            print(f"step {step:4d} train {loss.item():.4f} val {val_loss:.4f} best {best_val:.4f}@{best_step}")
            if stale >= args.patience:
                print("early stopping")
                break

    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    metrics = {split: evaluate(model, x, y, device) for split, x, y in [
        ("train", train_x, train_y), ("val", val_x, val_y), ("test", test_x, test_y)]}
    result = {"model": args.model, "seed": args.seed, "parameters": sum(p.numel() for p in model.parameters()),
              "best_step": best_step, "loss": metrics, "perplexity": {k: math.exp(v) for k, v in metrics.items()},
              "history": history}
    (output / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"best_step": best_step, "test_loss": metrics["test"], "test_perplexity": math.exp(metrics["test"])}, indent=2))

if __name__ == "__main__": main()
