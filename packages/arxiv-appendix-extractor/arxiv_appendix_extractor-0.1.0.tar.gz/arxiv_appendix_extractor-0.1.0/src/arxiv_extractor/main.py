import argparse
import json
import logging
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Import the core logic from other modules in the package
from .scraper import ArxivScraper
from .pipeline import process_single_paper
from .cleanup import run_cleanup

PROGRESS_FILE = "progress.json"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

def load_progress(path: Path) -> dict:
    progress_path = path / PROGRESS_FILE
    if progress_path.exists():
        with open(progress_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_progress(path: Path, data: dict):
    progress_path = path / PROGRESS_FILE
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_pipeline_cli():
    """CLI entry point for the main extractor pipeline."""
    setup_logging()
    logger = logging.getLogger("arxiv-extractor")
    
    parser = argparse.ArgumentParser(description="Refactored pipeline with resumability, parallelism, and smart features.")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--ids', nargs='+', help="A list of arXiv IDs.")
    mode_group.add_argument('--date', help="A date to process in YYYY-MM-DD format.")
    
    parser.add_argument('--category', default='cs', help="arXiv category for date-based search.")
    parser.add_argument('--max-papers', type=int, default=1000, help="Max papers to process.")
    parser.add_argument('--output-dir', default="pipeline_output_refactored", help="Directory for all outputs.")
    parser.add_argument('--final-output-file', default="final_appendix_results.json", help="Name of the final JSON report.")
    parser.add_argument('--workers', type=int, default=4, help="Number of parallel processes.")
    args = parser.parse_args()

    output_path = Path(args.output_dir)
    papers_path = output_path / "papers"
    output_path.mkdir(exist_ok=True)

    progress = load_progress(output_path)
    
    scraper_for_search = ArxivScraper(output_dir=str(papers_path))
    ids_to_process = args.ids if args.ids else [p['id'] for p in scraper_for_search.search_papers_by_date(args.date, args.category, args.max_papers)]
    
    new_ids = [pid for pid in ids_to_process if pid not in progress]
    logger.info(f"Total papers: {len(ids_to_process)}. Already processed: {len(progress)}. New to process: {len(new_ids)}.")

    if not new_ids:
        logger.info("No new papers to process.")
        return

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_single_paper, pid, str(papers_path), 1): pid for pid in new_ids}
        for future in as_completed(futures):
            arxiv_id = futures[future]
            try:
                _, result = future.result()
                progress[arxiv_id] = result
                save_progress(output_path, progress)
                status = result.get('status', 'failed')
                logger.info(f"[{arxiv_id}] Processed with status: {status}")
            except Exception as exc:
                logger.critical(f"[{arxiv_id}] Worker process crashed: {exc}")
                progress[arxiv_id] = {"status": "failed", "stage": "pipeline_crash", "error_message": str(exc)}
                save_progress(output_path, progress)

    final_report_path = output_path / args.final_output_file
    save_progress(output_path, progress)
    logger.info(f"Pipeline complete. Final report at {final_report_path}")

def run_cleanup_cli():
    """CLI entry point for the cleanup utility."""
    setup_logging()
    parser = argparse.ArgumentParser(description="Clean up paper source directories with no appendix sections.")
    parser.add_argument('--report-file', required=True, type=Path, help="Path to the final JSON report file.")
    parser.add_argument('--papers-dir', required=True, type=Path, help="Path to the base directory of paper sources.")
    parser.add_argument('--dry-run', action='store_true', help="Simulate cleanup without deleting.")
    parser.add_argument('-y', '--yes', action='store_true', help="Skip confirmation prompt.")
    args = parser.parse_args()
    
    run_cleanup(args.report_file, args.papers_dir, args.dry_run, args.yes)