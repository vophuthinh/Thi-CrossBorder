#!/usr/bin/env python3
"""
evaluate.py — Chấm điểm findings theo đáp án chuẩn.
Usage: python3 evaluate.py --truth fixtures/ground_truth.json --pred out/findings.json
"""
import argparse
import json
import sys
from collections import defaultdict


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_finding(pred: dict, truth: dict) -> bool:
    """Check if prediction matches a ground truth finding."""
    # Match by type + evidence overlap
    if pred.get("type") != truth.get("type"):
        return False
    # Check evidence_refs overlap
    pred_refs = set(pred.get("evidence_refs", []))
    truth_refs = set(truth.get("evidence_refs", []))
    if pred_refs & truth_refs:
        return True
    # Fallback: match by type + amount + date
    if (pred.get("amount_cents") == truth.get("amount_cents") and
            pred.get("occurred_at") == truth.get("occurred_at")):
        return True
    return False


def evaluate(truth_findings: list, pred_findings: list):
    """Run precision/recall/F1 evaluation."""
    # Group by type
    truth_by_type = defaultdict(list)
    for t in truth_findings:
        truth_by_type[t["type"]].append(t)

    pred_by_type = defaultdict(list)
    for p in pred_findings:
        pred_by_type[p["type"]].append(p)

    all_types = sorted(set(list(truth_by_type.keys()) + list(pred_by_type.keys())))

    results = {}
    total_tp = 0
    total_fn = 0
    total_fp = 0
    label_correct = 0
    label_total = 0

    missed = []
    extra = []

    for ftype in all_types:
        truths = truth_by_type.get(ftype, [])
        preds = pred_by_type.get(ftype, [])

        matched_truth = set()
        matched_pred = set()

        for ti, t in enumerate(truths):
            for pi, p in enumerate(preds):
                if pi not in matched_pred and match_finding(p, t):
                    matched_truth.add(ti)
                    matched_pred.add(pi)
                    # Check label
                    label_total += 1
                    if p.get("label") == t.get("label"):
                        label_correct += 1
                    break

        tp = len(matched_truth)
        fn = len(truths) - tp
        fp = len(preds) - len(matched_pred)

        total_tp += tp
        total_fn += fn
        total_fp += fp

        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0

        results[ftype] = {"TP": tp, "FN": fn, "FP": fp, "P": p, "R": r, "F1": f1}

        # Track missed/extra
        for ti, t in enumerate(truths):
            if ti not in matched_truth:
                missed.append(t)
        for pi, p in enumerate(preds):
            if pi not in matched_pred:
                extra.append(p)

    return results, total_tp, total_fn, total_fp, label_correct, label_total, missed, extra


def print_results(results, total_tp, total_fn, total_fp, label_correct, label_total, missed, extra):
    """Print evaluation results in formatted table."""
    print("\n" + "=" * 75)
    print(f"{'TYPE':<35} {'TP':>3} {'FN':>3} {'FP':>3} {'P':>6} {'R':>6} {'F1':>6}")
    print("-" * 75)

    for ftype, r in sorted(results.items()):
        print(f"{ftype:<35} {r['TP']:>3} {r['FN']:>3} {r['FP']:>3} "
              f"{r['P']:>6.2f} {r['R']:>6.2f} {r['F1']:>6.2f}")

    print("-" * 75)
    total = total_tp + total_fn
    tp_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    tp_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    tp_f1 = 2 * tp_p * tp_r / (tp_p + tp_r) if (tp_p + tp_r) > 0 else 0
    print(f"{'TOTAL':<35} {total_tp:>3} {total_fn:>3} {total_fp:>3} "
          f"{tp_p:>6.2f} {tp_r:>6.2f} {tp_f1:>6.2f}")
    print(f"\nTỔNG: khớp {total_tp}/{total} | báo thừa (FP) {total_fp} | "
          f"nhãn đúng {label_correct}/{label_total}")

    if missed:
        print("\n[BỎ SÓT]")
        for m in missed:
            print(f"  - {m.get('finding_id', '?')} {m['type']} "
                  f"${m.get('amount_cents', 0)/100:.2f} :: {m.get('title_vi', m.get('title_en', ''))}")

    if extra:
        print("\n[BÁO THỪA]")
        for e in extra[:10]:  # Show max 10
            print(f"  - {e.get('finding_id', '?')} {e['type']} "
                  f"${e.get('amount_cents', 0)/100:.2f} :: {e.get('title_vi', e.get('title_en', ''))}")

    print("\n" + "=" * 75)
    if total_tp == total and total_fp == 0 and label_correct == label_total:
        print("✅ PERFECT SCORE!")
    elif total_fn > 0:
        print(f"⚠️  Missing {total_fn} findings — improve detectors")
    if total_fp > 0:
        print(f"⚠️  {total_fp} false positives — tighten rules")


def main():
    parser = argparse.ArgumentParser(description="Evaluate findings against ground truth")
    parser.add_argument("--truth", required=True, help="Path to ground_truth.json")
    parser.add_argument("--pred", required=True, help="Path to predicted findings.json")
    args = parser.parse_args()

    truth = load_json(args.truth)
    pred = load_json(args.pred)

    # Handle if findings are wrapped in a dict
    if isinstance(truth, dict):
        truth = truth.get("findings", truth.get("ground_truth", []))
    if isinstance(pred, dict):
        pred = pred.get("findings", [])

    results, tp, fn, fp, lc, lt, missed, extra = evaluate(truth, pred)
    print_results(results, tp, fn, fp, lc, lt, missed, extra)

    # Exit with error if not perfect
    if fn > 0 or fp > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
