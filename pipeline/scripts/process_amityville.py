#!/usr/bin/env python3
"""
Process Amityville-Records.pdf using Qwen VL Plus model.

This script processes the 665-page Amityville PDF with:
- Verbose logging showing progress for each page
- Stamp noise filtering (removes duplicate microfilm stamps)
- qwen/qwen-vl-plus model for OCR

Run with: python scripts/process_amityville.py
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from ocr import QwenVLOCR
from pdf2image import convert_from_path, pdfinfo_from_path
from loguru import logger

# Configure logging - more verbose
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
)
logger.add(
    str(PROJECT_ROOT / "logs" / "amityville_processing_{time}.log"),
    rotation="10 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
)


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def estimate_remaining(elapsed: float, completed: int, total: int) -> str:
    """Estimate remaining time based on progress."""
    if completed == 0:
        return "calculating..."
    avg_per_page = elapsed / completed
    remaining_pages = total - completed
    remaining_seconds = avg_per_page * remaining_pages
    return format_duration(remaining_seconds)


async def process_amityville(run_id: Optional[str] = None):
    """Process Amityville-Records.pdf with verbose logging.

    Args:
        run_id: Optional run identifier for versioning. If not provided, uses timestamp.
    """

    print("=" * 70)
    print("AMITYVILLE RECORDS PROCESSING")
    print("Model: qwen/qwen-vl-plus (historical documents with stamp filtering)")
    print("=" * 70)
    print()

    # Initialize OCR with run_id for versioning
    # Enable stamp filtering - this is a microfilm scan
    ocr = QwenVLOCR(config_path="ocr_config.yaml", run_id=run_id, enable_stamp_filtering=True)
    ocr.model = "qwen/qwen-vl-plus"
    logger.info(f"Initialized OCR with model: {ocr.model}")
    logger.info(f"Run ID: {ocr.run_id}")
    logger.info("Document type: HISTORICAL DOCUMENT (mixed administrative records)")
    logger.info("Stamp noise filtering: ENABLED (microfilm scan with duplicate stamps)")

    pdf_path = PROJECT_ROOT / "raw" / "scans" / "NYS Archives" / "A4456" / "Amityville-Records.pdf"

    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        print(f"ERROR: PDF not found at {pdf_path}")
        return

    # Get page count
    try:
        pdf_info = pdfinfo_from_path(str(pdf_path))
        total_pages = pdf_info["Pages"]
    except Exception as e:
        logger.warning(f"Could not get page count: {e}")
        total_pages = 665  # Known count

    print(f"PDF: {pdf_path.name}")
    print(f"Total pages: {total_pages}")
    print(f"Estimated time: {format_duration(total_pages * 8)}  (assuming ~8s per page)")
    print()
    print("-" * 70)
    print()

    # Track progress
    start_time = time.time()
    results = []
    successful = 0
    failed = 0

    # Process in chunks to avoid memory issues
    CHUNK_SIZE = 10  # Process 10 pages at a time

    try:
        print("Processing pages in chunks (converting + OCR together)...")
        print(f"Chunk size: {CHUNK_SIZE} pages")
        print()

        # Process pages in chunks
        for chunk_start in range(1, total_pages + 1, CHUNK_SIZE):
            chunk_end = min(chunk_start + CHUNK_SIZE - 1, total_pages)

            logger.info(f"Converting pages {chunk_start}-{chunk_end}...")
            print(f"  Converting pages {chunk_start}-{chunk_end}...", end=" ", flush=True)

            convert_start = time.time()
            images = convert_from_path(
                str(pdf_path),
                dpi=300,
                first_page=chunk_start,
                last_page=chunk_end
            )
            convert_time = time.time() - convert_start
            print(f"done ({convert_time:.1f}s)")

            # Process each page in this chunk
            for i, image in enumerate(images):
                page_num = chunk_start + i
                page_start = time.time()

                # Save temporary image
                temp_path = ocr.output_dir / "temp" / f"{pdf_path.stem}_page_{page_num}.jpg"
                temp_path.parent.mkdir(exist_ok=True)
                image.save(temp_path, 'JPEG', quality=95)

                logger.debug(f"Page {page_num}: Saved temp image ({temp_path.stat().st_size / 1024:.1f} KB)")

                # Process the image
                try:
                    logger.info(f"Page {page_num}/{total_pages}: Sending to API...")

                    result = await ocr.process_image(temp_path, document_type="historical_document")
                    result["page_number"] = page_num
                    result["source_pdf"] = str(pdf_path)
                    result["series"] = "A4456"

                    page_time = time.time() - page_start
                    elapsed = time.time() - start_time
                    remaining = estimate_remaining(elapsed, page_num, total_pages)

                    if result.get("status") == "success":
                        successful += 1
                        text_len = result.get("text_length", 0)
                        confidence = result.get("confidence", 0)

                        logger.info(
                            f"Page {page_num}/{total_pages}: SUCCESS "
                            f"({text_len} chars, {confidence:.1%} confidence, {page_time:.1f}s)"
                        )
                        print(
                            f"    [{page_num:3d}/{total_pages}] ✓ {text_len:5d} chars | "
                            f"conf: {confidence:.0%} | {page_time:.1f}s | "
                            f"ETA: {remaining}"
                        )
                    else:
                        failed += 1
                        error = result.get("error", "unknown error")
                        logger.warning(f"Page {page_num}/{total_pages}: FAILED - {error}")
                        print(f"    [{page_num:3d}/{total_pages}] ✗ FAILED: {error}")

                    results.append(result)

                except Exception as e:
                    failed += 1
                    page_time = time.time() - page_start
                    logger.error(f"Page {page_num}/{total_pages}: EXCEPTION - {e}")
                    print(f"    [{page_num:3d}/{total_pages}] ✗ ERROR: {e}")

                    results.append({
                        "status": "error",
                        "page_number": page_num,
                        "source_pdf": str(pdf_path),
                        "series": "A4456",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })

                finally:
                    # Clean up temp file
                    if temp_path.exists():
                        temp_path.unlink()

                # Progress checkpoint every 50 pages
                if page_num % 50 == 0:
                    elapsed = time.time() - start_time
                    print()
                    print(f"  --- Checkpoint: {page_num}/{total_pages} pages ---")
                    print(f"      Elapsed: {format_duration(elapsed)}")
                    print(f"      Success rate: {successful}/{page_num} ({successful/page_num:.1%})")
                    print(f"      Avg per page: {elapsed/page_num:.1f}s")
                    print()

            # Free memory after each chunk
            del images

        # Combine all pages
        logger.info("Combining all pages into complete document...")
        ocr._combine_pdf_results(pdf_path, results)

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"\nFATAL ERROR: {e}")
        raise

    # Final summary
    total_time = time.time() - start_time
    print()
    print("=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print()
    print(f"  Total pages:    {len(results)}")
    print(f"  Successful:     {successful} ({successful/len(results):.1%})")
    print(f"  Failed:         {failed}")
    print(f"  Total time:     {format_duration(total_time)}")
    print(f"  Avg per page:   {total_time/len(results):.1f}s")
    print()

    # Calculate total characters transcribed
    total_chars = sum(r.get("text_length", 0) for r in results if r.get("status") == "success")
    avg_confidence = sum(r.get("confidence", 0) for r in results if r.get("status") == "success")
    if successful > 0:
        avg_confidence /= successful

    print(f"  Total chars:    {total_chars:,}")
    print(f"  Avg confidence: {avg_confidence:.1%}")
    print()

    # Save report
    report = {
        "source": str(pdf_path),
        "model": ocr.model,
        "total_pages": len(results),
        "successful_pages": successful,
        "failed_pages": failed,
        "total_characters": total_chars,
        "average_confidence": round(avg_confidence, 3),
        "processing_time_seconds": round(total_time, 1),
        "avg_seconds_per_page": round(total_time / len(results), 2),
        "timestamp": datetime.now().isoformat()
    }

    report_path = PROJECT_ROOT / "output" / "ocr" / "reports" / "amityville_processing_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  Report: {report_path}")
    print(f"  Output: output/ocr/text/Amityville-Records_*.txt")
    print()
    print("=" * 70)

    logger.info(f"Processing complete: {successful}/{len(results)} pages successful in {format_duration(total_time)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process Amityville Records PDF")
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run identifier for versioning (prevents overwriting). If not provided, uses timestamp."
    )

    args = parser.parse_args()
    asyncio.run(process_amityville(run_id=args.run_id))
