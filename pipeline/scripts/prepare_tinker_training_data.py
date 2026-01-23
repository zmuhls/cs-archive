#!/usr/bin/env python3
"""
Prepare training data for Tinker historical OCR fine-tuning.

Extracts PDF pages as images, loads existing OCR transcriptions, computes
quality signals, and exports stratified train/test JSONL files.

Usage:
    python scripts/prepare_tinker_training_data.py
    python scripts/prepare_tinker_training_data.py --skip-extraction  # Use existing images
    python scripts/prepare_tinker_training_data.py --dpi 200  # Lower resolution
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
from pdf2image import convert_from_path
from PIL import Image
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# Add tinker-cookbook to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TINKER_COOKBOOK = PROJECT_ROOT / "tinker-cookbook"
sys.path.insert(0, str(TINKER_COOKBOOK))

from tinker_cookbook.recipes.historical_ocr.validate import (
    QualitySignals,
    compute_quality_signals,
)

# Configuration
PDF_CONFIGS = {
    "A4645/South-Kortright-Roll-13.pdf": {
        "document_type": "meeting_minutes",
        "description": "Handwritten 1800s school district meeting minutes",
    },
    "A4456/Amityville-Records.pdf": {
        "document_type": "mixed",
        "description": "Mixed typed and handwritten administrative records",
    },
    "B0594/District-Notecard-Records.pdf": {
        "document_type": "notecard",
        "description": "Index cards with typed headers and handwritten entries",
    },
    "B0494/District-Consolidation-Data_100-116.pdf": {
        "document_type": "table",
        "description": "Typed tabular consolidation data",
    },
}

# Paths
NYS_ARCHIVES_PATH = PROJECT_ROOT / "raw/scans/NYS Archives"
OCR_OUTPUT_PATH = PROJECT_ROOT / "output/ocr/text"
OUTPUT_BASE = TINKER_COOKBOOK / "data/nys_archives"


def extract_pdf_pages(pdf_path: Path, output_dir: Path, dpi: int = 300) -> list[Path]:
    """Extract all pages from a PDF as PNG images.

    Args:
        pdf_path: Path to source PDF
        output_dir: Directory to save images
        dpi: Resolution for extraction

    Returns:
        List of output image paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_name = pdf_path.stem

    # Check if already extracted
    existing = sorted(output_dir.glob(f"page_*.png"))
    if existing:
        print(f"  Found {len(existing)} existing images for {pdf_name}")
        return existing

    print(f"  Extracting pages from {pdf_name} at {dpi} DPI...")
    images = convert_from_path(str(pdf_path), dpi=dpi)

    output_paths = []
    for i, image in enumerate(tqdm(images, desc=f"  Saving {pdf_name}")):
        page_num = i + 1
        output_path = output_dir / f"page_{page_num}.png"
        image.save(output_path, "PNG")
        output_paths.append(output_path)

    return output_paths


def load_transcriptions(ocr_dir: Path, pdf_name: str) -> dict[int, str]:
    """Load existing OCR transcriptions for a PDF.

    Args:
        ocr_dir: Directory containing OCR text files
        pdf_name: Name of PDF (without extension)

    Returns:
        Dict mapping page number to transcription text
    """
    transcriptions = {}

    # Try multiple naming patterns
    patterns = [
        f"{pdf_name}_qwen-vl-plus_page_*.txt",  # Amityville, South-Kortright, etc.
        f"{pdf_name}_page_*.txt",  # District-Consolidation tables
    ]

    txt_files = []
    for pattern in patterns:
        txt_files.extend(ocr_dir.glob(pattern))

    for txt_path in txt_files:
        # Extract page number
        match = re.search(r"page[_-]?(\d+)", txt_path.stem, re.IGNORECASE)
        if match:
            page_num = int(match.group(1))
            transcriptions[page_num] = txt_path.read_text(encoding="utf-8")

    return transcriptions


def compute_all_signals(
    images: list[Path],
    transcriptions: dict[int, str],
    pdf_name: str,
    document_type: str,
) -> pd.DataFrame:
    """Compute quality signals for all pages.

    Args:
        images: List of image paths
        transcriptions: Dict of page_num -> transcription text
        pdf_name: Name of PDF
        document_type: Document type classification

    Returns:
        DataFrame with quality signals per page
    """
    rows = []

    for image_path in tqdm(images, desc=f"  Computing signals for {pdf_name}"):
        # Extract page number from filename
        match = re.search(r"page[_-]?(\d+)", image_path.stem, re.IGNORECASE)
        if not match:
            continue
        page_num = int(match.group(1))

        transcription = transcriptions.get(page_num, "")

        # Compute quality signals
        try:
            image = Image.open(image_path)
            signals = compute_quality_signals(transcription, image)
        except Exception as e:
            print(f"  Warning: Error processing page {page_num}: {e}")
            signals = compute_quality_signals(transcription)

        rows.append({
            "pdf_name": pdf_name,
            "document_type": document_type,
            "page_num": page_num,
            "image_path": str(image_path),
            "has_transcription": bool(transcription.strip()),
            **signals.to_dict(),
        })

    return pd.DataFrame(rows)


def export_training_jsonl(
    signals_df: pd.DataFrame,
    transcriptions_by_pdf: dict[str, dict[int, str]],
    output_path: Path,
    include_needs_review: bool = False,
) -> int:
    """Export training data to JSONL format.

    Args:
        signals_df: DataFrame with quality signals
        transcriptions_by_pdf: Dict of pdf_name -> {page_num: text}
        output_path: Output JSONL path
        include_needs_review: Whether to include flagged pages

    Returns:
        Number of samples exported
    """
    # Filter to pages with transcriptions
    df = signals_df[signals_df["has_transcription"]].copy()

    # Optionally exclude pages needing review
    if not include_needs_review:
        df = df[df["needs_review"] == False]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    exported = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            pdf_name = row["pdf_name"]
            page_num = row["page_num"]

            trans = transcriptions_by_pdf.get(pdf_name, {}).get(page_num)
            if not trans or not trans.strip():
                continue

            entry = {
                "image_path": row["image_path"],
                "transcription": trans,
                "document_type": row["document_type"],
                "pdf_name": pdf_name,
                "page_num": page_num,
            }
            f.write(json.dumps(entry) + "\n")
            exported += 1

    return exported


def create_stratified_split(
    data_path: Path,
    train_path: Path,
    test_path: Path,
    test_fraction: float = 0.1,
    random_state: int = 42,
) -> tuple[int, int]:
    """Create stratified train/test split.

    Args:
        data_path: Path to full JSONL data
        train_path: Output path for training data
        test_path: Output path for test data
        test_fraction: Fraction for test set
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (train_count, test_count)
    """
    # Load all data
    with open(data_path, "r") as f:
        all_data = [json.loads(line) for line in f]

    if len(all_data) < 10:
        print(f"  Warning: Only {len(all_data)} samples, skipping split")
        return 0, 0

    # Stratify by document type
    doc_types = [d["document_type"] for d in all_data]

    train_data, test_data = train_test_split(
        all_data,
        test_size=test_fraction,
        stratify=doc_types,
        random_state=random_state,
    )

    # Save splits
    with open(train_path, "w") as f:
        for entry in train_data:
            f.write(json.dumps(entry) + "\n")

    with open(test_path, "w") as f:
        for entry in test_data:
            f.write(json.dumps(entry) + "\n")

    return len(train_data), len(test_data)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare training data for Tinker historical OCR"
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Skip PDF extraction, use existing images",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PDF extraction (default: 300)",
    )
    parser.add_argument(
        "--include-flagged",
        action="store_true",
        help="Include pages flagged for review in training data",
    )
    parser.add_argument(
        "--test-fraction",
        type=float,
        default=0.1,
        help="Fraction of data for test set (default: 0.1)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Tinker Training Data Preparation")
    print("=" * 60)

    # Create output directories
    images_dir = OUTPUT_BASE / "images"
    training_dir = OUTPUT_BASE / "training"
    images_dir.mkdir(parents=True, exist_ok=True)
    training_dir.mkdir(parents=True, exist_ok=True)

    # Process each PDF
    all_images = {}
    all_transcriptions = {}
    all_signals = []

    for rel_path, config in PDF_CONFIGS.items():
        pdf_path = NYS_ARCHIVES_PATH / rel_path
        pdf_name = pdf_path.stem
        document_type = config["document_type"]

        print(f"\n[{pdf_name}] {config['description']}")

        # Check PDF exists
        if not pdf_path.exists():
            print(f"  SKIP: PDF not found at {pdf_path}")
            continue

        # Extract images
        pdf_images_dir = images_dir / pdf_name
        if args.skip_extraction:
            existing = sorted(pdf_images_dir.glob("page_*.png"))
            if existing:
                all_images[pdf_name] = existing
                print(f"  Using {len(existing)} existing images")
            else:
                print(f"  No existing images found, extracting...")
                all_images[pdf_name] = extract_pdf_pages(
                    pdf_path, pdf_images_dir, args.dpi
                )
        else:
            all_images[pdf_name] = extract_pdf_pages(
                pdf_path, pdf_images_dir, args.dpi
            )

        # Load transcriptions
        trans = load_transcriptions(OCR_OUTPUT_PATH, pdf_name)
        all_transcriptions[pdf_name] = trans
        print(f"  Loaded {len(trans)} transcriptions")

        # Compute quality signals
        signals_df = compute_all_signals(
            all_images[pdf_name], trans, pdf_name, document_type
        )
        all_signals.append(signals_df)

    # Combine all signals
    if not all_signals:
        print("\nERROR: No data processed")
        return 1

    combined_signals = pd.concat(all_signals, ignore_index=True)

    # Save quality signals CSV
    signals_path = OUTPUT_BASE / "quality_signals.csv"
    combined_signals.to_csv(signals_path, index=False)
    print(f"\n[Quality Signals] Saved to {signals_path}")

    # Print summary statistics
    print("\n" + "=" * 60)
    print("Quality Signal Summary")
    print("=" * 60)

    summary = combined_signals.groupby("document_type").agg({
        "page_num": "count",
        "has_transcription": "sum",
        "needs_review": "sum",
        "illegible_ratio": "mean",
        "empty": "sum",
    }).rename(columns={"page_num": "total_pages"})
    summary["review_rate"] = summary["needs_review"] / summary["total_pages"]
    print(summary.to_string())

    # Export training JSONL
    print("\n" + "=" * 60)
    print("Exporting Training Data")
    print("=" * 60)

    full_data_path = training_dir / "all_data.jsonl"
    num_exported = export_training_jsonl(
        combined_signals,
        all_transcriptions,
        full_data_path,
        include_needs_review=args.include_flagged,
    )
    print(f"Exported {num_exported} samples to {full_data_path}")

    # Create train/test split
    train_path = training_dir / "train.jsonl"
    test_path = training_dir / "test.jsonl"
    train_count, test_count = create_stratified_split(
        full_data_path,
        train_path,
        test_path,
        test_fraction=args.test_fraction,
    )
    print(f"Split: {train_count} training, {test_count} test")

    # Final summary
    print("\n" + "=" * 60)
    print("Output Files")
    print("=" * 60)
    print(f"Images:          {images_dir}/")
    print(f"Quality signals: {signals_path}")
    print(f"All data:        {full_data_path}")
    print(f"Training data:   {train_path}")
    print(f"Test data:       {test_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
