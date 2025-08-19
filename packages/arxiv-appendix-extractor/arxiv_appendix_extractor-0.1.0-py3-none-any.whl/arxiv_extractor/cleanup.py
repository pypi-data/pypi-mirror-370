import json
import logging
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def run_cleanup(report_file: Path, papers_dir: Path, dry_run: bool, skip_confirmation: bool):
    """Reads the report and cleans up directories with no appendices."""
    if not report_file.exists():
        logger.error(f"Error: Report file not found at '{report_file}'")
        sys.exit(1)
    if not papers_dir.is_dir():
        logger.error(f"Error: Papers directory not found at '{papers_dir}'")
        sys.exit(1)

    logger.info(f"Loading report from: {report_file}")
    with open(report_file, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    dirs_to_delete = []
    logger.info("Scanning report for papers with no appendix sections...")
    for arxiv_id, result in report_data.items():
        if isinstance(result, dict) and result.get('status') == 'success' and result.get("total_sections") == 0:
            safe_id = arxiv_id.replace('/', '_').replace('.', '_')
            paper_path = papers_dir / safe_id
            if paper_path.exists():
                dirs_to_delete.append(paper_path)

    if not dirs_to_delete:
        logger.info("Scan complete. No directories to clean up.")
        return

    logger.info(f"Found {len(dirs_to_delete)} directories to be deleted:")
    for path in dirs_to_delete:
        print(f"  - {path}")

    if dry_run:
        logger.info("\nDry run is active. No files will be deleted.")
        return

    if not skip_confirmation:
        confirm = input(f"\nPermanently delete these {len(dirs_to_delete)} directories? [y/N]: ")
        if confirm.lower() != 'y':
            logger.info("Cleanup aborted by user.")
            return
    
    deleted_count = 0
    for path in dirs_to_delete:
        try:
            shutil.rmtree(path)
            logger.info(f"Deleted: {path}")
            deleted_count += 1
        except OSError as e:
            logger.error(f"Failed to delete {path}: {e}")
    logger.info(f"\nCleanup complete. Deleted {deleted_count}/{len(dirs_to_delete)} directories.")
