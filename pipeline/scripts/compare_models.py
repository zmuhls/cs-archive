#!/usr/bin/env python3
"""
Compare fine-tuned vs. base model on 50 challenging historical OCR pages.

Selects the hardest pages by difficulty score (illegible ratio, low contrast,
low sharpness, high repetition) and runs both models side-by-side.

Usage:
    python pipeline/scripts/compare_models.py
    python pipeline/scripts/compare_models.py --num-pages 10  # Quick test
"""

import argparse
import json
import os
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# Load .env if present (for TINKER_API_KEY)
def _load_dotenv(env_path: Path):
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TINKER_COOKBOOK = PROJECT_ROOT / "tinker-cookbook"
sys.path.insert(0, str(TINKER_COOKBOOK))

_load_dotenv(TINKER_COOKBOOK / ".env")

from tinker_cookbook.recipes.historical_ocr.inference import (
    DOCUMENT_TYPE_PROMPTS,
    DOCUMENT_TYPE_SYSTEM_PROMPTS,
)

# Checkpoint from training run
FINETUNED_CHECKPOINT = (
    "tinker://67f53233-befc-55cc-a564-c3410b7a2dbf:train:0/weights/final"
)

QUALITY_SIGNALS_PATH = TINKER_COOKBOOK / "data/nys_archives/quality_signals.csv"
OCR_TEXT_PATH = PROJECT_ROOT / "output/ocr/text"


def select_challenging_pages(signals_path: Path, num_pages: int = 50) -> pd.DataFrame:
    """Select the most challenging pages by composite difficulty score."""
    df = pd.read_csv(signals_path)

    df["difficulty_score"] = (
        df["illegible_ratio"] * 3
        + (1 - df["image_contrast"].fillna(0.5)) * 2
        + (df["repeated_phrases"] / df["repeated_phrases"].max())
        + (1 - df["image_sharpness"].fillna(0.5).clip(0, 1))
    )

    has_trans = df[df["has_transcription"] == True]
    return has_trans.nlargest(num_pages, "difficulty_score")


def load_ground_truth(pdf_name: str, page_num: int) -> str:
    """Load the ground truth OCR transcription for a page."""
    patterns = [
        f"{pdf_name}_qwen-vl-plus_page_{page_num}.txt",
        f"{pdf_name}_page_{page_num}.txt",
    ]

    for pattern in patterns:
        path = OCR_TEXT_PATH / pattern
        if path.exists():
            return path.read_text(encoding="utf-8")

    return ""


def compute_similarity(text_a: str, text_b: str) -> float:
    """Compute text similarity ratio (0-1)."""
    if not text_a.strip() or not text_b.strip():
        return 0.0
    return SequenceMatcher(None, text_a.strip(), text_b.strip()).ratio()


def compute_cer(reference: str, hypothesis: str) -> float:
    """Compute Character Error Rate using edit distance."""
    if not reference.strip():
        return 1.0 if hypothesis.strip() else 0.0

    ref = reference.strip()
    hyp = hypothesis.strip()

    # Levenshtein distance
    m, n = len(ref), len(hyp)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n] / max(m, 1)


def build_prompt(renderer, image_path: str, doc_type: str):
    """Build a ModelInput prompt for a document image."""
    system_prompt = DOCUMENT_TYPE_SYSTEM_PROMPTS.get(doc_type, DOCUMENT_TYPE_SYSTEM_PROMPTS["mixed"])
    user_prompt = DOCUMENT_TYPE_PROMPTS.get(doc_type, DOCUMENT_TYPE_PROMPTS["mixed"])

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "image", "image": image_path},
            {"type": "text", "text": user_prompt},
        ]},
    ]
    return renderer.build_generation_prompt(messages)


def sample_and_decode(client, tokenizer, prompt, params):
    """Run sampling and decode the response tokens."""
    result_future = client.sample(prompt, num_samples=1, sampling_params=params)
    result = result_future.result()
    if result.sequences:
        return tokenizer.decode(result.sequences[0].tokens, skip_special_tokens=True)
    return ""


def run_comparison(
    pages_df: pd.DataFrame,
    output_path: Path,
) -> pd.DataFrame:
    """Run both models on selected pages and compare outputs."""
    import tinker
    from tinker_cookbook import renderers, tokenizer_utils
    from tinker_cookbook.image_processing_utils import get_image_processor

    MODEL_NAME = "Qwen/Qwen3-VL-30B-A3B-Instruct"

    print("Initializing models...")

    # Set up renderer and tokenizer
    print("  Loading tokenizer and image processor...")
    tokenizer = tokenizer_utils.get_tokenizer(MODEL_NAME)
    image_processor = get_image_processor(MODEL_NAME)
    renderer = renderers.Qwen3VLRenderer(tokenizer, image_processor)

    # Initialize clients
    service = tinker.ServiceClient()

    print("  Creating base model client...")
    base_client = service.create_sampling_client(base_model=MODEL_NAME)

    print("  Creating fine-tuned model client...")
    ft_client = service.create_sampling_client(model_path=FINETUNED_CHECKPOINT)

    # Test connectivity on first image
    first_row = pages_df.iloc[0]
    test_prompt = build_prompt(renderer, first_row["image_path"], first_row["document_type"])
    test_params = tinker.SamplingParams(max_tokens=100, temperature=0.1)

    print(f"  Testing API on {first_row['pdf_name']} p{int(first_row['page_num'])}...")
    test_text = sample_and_decode(base_client, tokenizer, test_prompt, test_params)
    print(f"  Test response ({len(test_text)} chars): {test_text[:80]}...")
    if not test_text.strip():
        print("  WARNING: API returned empty text. Check model availability.")
        return pd.DataFrame()

    params = tinker.SamplingParams(max_tokens=4096, temperature=0.1)
    results = []
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, (_, row) in enumerate(tqdm(
            pages_df.iterrows(), total=len(pages_df), desc="Comparing models"
        )):
            pdf_name = row["pdf_name"]
            page_num = int(row["page_num"])
            doc_type = row["document_type"]
            image_path = row["image_path"]

            # Load ground truth
            ground_truth = load_ground_truth(pdf_name, page_num)
            if not ground_truth.strip():
                print(f"  Skipping {pdf_name} p{page_num}: no ground truth")
                continue

            # Build prompt once, use for both models
            prompt = build_prompt(renderer, image_path, doc_type)

            # Run base model
            try:
                base_text = sample_and_decode(base_client, tokenizer, prompt, params)
            except Exception as e:
                print(f"\n  BASE ERROR on {pdf_name} p{page_num}: {type(e).__name__}: {e}")
                base_text = ""

            # Run fine-tuned model
            try:
                finetuned_text = sample_and_decode(ft_client, tokenizer, prompt, params)
            except Exception as e:
                print(f"\n  FT ERROR on {pdf_name} p{page_num}: {type(e).__name__}: {e}")
                finetuned_text = ""

            # Log first few results verbosely
            if idx < 3:
                print(f"\n  [{pdf_name} p{page_num}]")
                print(f"    Base ({len(base_text)} chars): {base_text[:60]}")
                print(f"    FT   ({len(finetuned_text)} chars): {finetuned_text[:60]}")

            # Compute metrics
            base_sim = compute_similarity(ground_truth, base_text)
            ft_sim = compute_similarity(ground_truth, finetuned_text)
            base_cer = compute_cer(ground_truth, base_text)
            ft_cer = compute_cer(ground_truth, finetuned_text)

            result = {
                "pdf_name": pdf_name,
                "page_num": page_num,
                "document_type": doc_type,
                "difficulty_score": row["difficulty_score"],
                "base_similarity": base_sim,
                "finetuned_similarity": ft_sim,
                "similarity_delta": ft_sim - base_sim,
                "base_cer": base_cer,
                "finetuned_cer": ft_cer,
                "cer_delta": base_cer - ft_cer,  # Positive = fine-tuned is better
                "base_length": len(base_text),
                "finetuned_length": len(finetuned_text),
                "ground_truth_length": len(ground_truth),
            }
            results.append(result)

            # Write incremental JSONL
            entry = {
                **result,
                "base_text": base_text[:500],
                "finetuned_text": finetuned_text[:500],
                "ground_truth": ground_truth[:500],
            }
            f.write(json.dumps(entry) + "\n")
            f.flush()

    return pd.DataFrame(results)


def print_report(results_df: pd.DataFrame):
    """Print comparison summary report."""
    print("\n" + "=" * 70)
    print("MODEL COMPARISON REPORT")
    print("=" * 70)

    print(f"\nPages evaluated: {len(results_df)}")

    # Overall metrics
    print("\n--- Overall Metrics ---")
    print(f"{'Metric':<25} {'Base Model':>12} {'Fine-tuned':>12} {'Delta':>10}")
    print("-" * 60)

    avg_base_sim = results_df["base_similarity"].mean()
    avg_ft_sim = results_df["finetuned_similarity"].mean()
    avg_base_cer = results_df["base_cer"].mean()
    avg_ft_cer = results_df["finetuned_cer"].mean()

    print(
        f"{'Avg Similarity':.<25} {avg_base_sim:>11.1%} {avg_ft_sim:>11.1%} "
        f"{'+'if avg_ft_sim - avg_base_sim >= 0 else ''}{avg_ft_sim - avg_base_sim:>8.1%}"
    )
    print(
        f"{'Avg CER':.<25} {avg_base_cer:>11.1%} {avg_ft_cer:>11.1%} "
        f"{'+'if avg_base_cer - avg_ft_cer >= 0 else ''}{avg_base_cer - avg_ft_cer:>8.1%}"
    )

    # Win/loss
    ft_wins_sim = (results_df["similarity_delta"] > 0.01).sum()
    base_wins_sim = (results_df["similarity_delta"] < -0.01).sum()
    ties_sim = len(results_df) - ft_wins_sim - base_wins_sim

    print(f"\n--- Win/Loss (Similarity, >1% threshold) ---")
    print(f"Fine-tuned wins: {ft_wins_sim}")
    print(f"Base wins:       {base_wins_sim}")
    print(f"Ties:            {ties_sim}")

    # By document type
    print("\n--- By Document Type ---")
    by_type = results_df.groupby("document_type").agg(
        count=("page_num", "count"),
        base_sim=("base_similarity", "mean"),
        ft_sim=("finetuned_similarity", "mean"),
        base_cer=("base_cer", "mean"),
        ft_cer=("finetuned_cer", "mean"),
    )
    by_type["sim_delta"] = by_type["ft_sim"] - by_type["base_sim"]
    by_type["cer_delta"] = by_type["base_cer"] - by_type["ft_cer"]
    print(by_type.to_string(float_format=lambda x: f"{x:.3f}"))

    # Top improvements
    print("\n--- Top 5 Improvements (Fine-tuned > Base) ---")
    top_improvements = results_df.nlargest(5, "similarity_delta")
    for _, row in top_improvements.iterrows():
        print(
            f"  {row['pdf_name']} p{row['page_num']:>3} "
            f"({row['document_type']:<16}): "
            f"{row['base_similarity']:.1%} -> {row['finetuned_similarity']:.1%} "
            f"(+{row['similarity_delta']:.1%})"
        )

    # Worst regressions
    print("\n--- Top 5 Regressions (Base > Fine-tuned) ---")
    top_regressions = results_df.nsmallest(5, "similarity_delta")
    for _, row in top_regressions.iterrows():
        print(
            f"  {row['pdf_name']} p{row['page_num']:>3} "
            f"({row['document_type']:<16}): "
            f"{row['base_similarity']:.1%} -> {row['finetuned_similarity']:.1%} "
            f"({row['similarity_delta']:+.1%})"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Compare fine-tuned vs. base model on challenging pages"
    )
    parser.add_argument(
        "--num-pages",
        type=int,
        default=50,
        help="Number of challenging pages to test (default: 50)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSONL path (default: tinker-cookbook/data/nys_archives/comparison_results.jsonl)",
    )
    args = parser.parse_args()

    output_path = Path(
        args.output
        or str(TINKER_COOKBOOK / "data/nys_archives/comparison_results.jsonl")
    )

    print("=" * 70)
    print("Fine-tuned vs. Base Model Comparison")
    print("=" * 70)

    # Select pages
    print(f"\nSelecting {args.num_pages} most challenging pages...")
    pages_df = select_challenging_pages(QUALITY_SIGNALS_PATH, args.num_pages)
    print(f"Selected pages by document type:")
    print(pages_df["document_type"].value_counts().to_string())

    # Run comparison
    print(f"\nRunning inference on {len(pages_df)} pages (base + fine-tuned)...")
    start_time = time.time()
    results_df = run_comparison(pages_df, output_path)
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.0f}s ({elapsed / len(pages_df):.1f}s per page)")

    # Save results CSV
    csv_path = output_path.with_suffix(".csv")
    results_df.to_csv(csv_path, index=False)
    print(f"Results saved to {csv_path}")

    # Print report
    print_report(results_df)

    return 0


if __name__ == "__main__":
    sys.exit(main())
