# ==== FILE: arxiv_appendix_extractor/src/arxiv_extractor/pipeline.py (Final Corrected Version) ====
import json
import logging
import sys
import traceback # 引入traceback用于详细错误记录
from typing import Dict, Tuple

# 顶层导入依然保留
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

from .scraper import ArxivScraper
from .extractor import ImprovedAppendixExtractor, _to_jsonable

logger = logging.getLogger(__name__)

def get_best_html_url(arxiv_id: str, timeout: int = 5) -> Tuple[str, str]:
    """Tries ar5iv first, then falls back to arxiv.org."""
    if not requests:
        return f"https://arxiv.org/html/{arxiv_id}", "arxiv"
        
    ar5iv_url = f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
    try:
        response = requests.head(ar5iv_url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            logger.debug(f"[{arxiv_id}] Using ar5iv URL.")
            return ar5iv_url, "ar5iv"
    except requests.RequestException:
        logger.warning(f"[{arxiv_id}] ar5iv check failed. Falling back to arxiv.org.")
    
    return f"https://arxiv.org/html/{arxiv_id}", "arxiv"

def process_single_paper(arxiv_id: str, papers_output_dir: str, max_workers_per_scraper: int) -> Tuple[str, Dict]:
    """A self-contained function to process one paper, designed for parallel execution."""
    
    from pathlib import Path

    try:
        scraper = ArxivScraper(output_dir=papers_output_dir, max_workers=max_workers_per_scraper)
        extractor = ImprovedAppendixExtractor()

        paper_dir = scraper.download_latex_source(arxiv_id)
        if not paper_dir:
            raise RuntimeError("Failed to download source files.")
        
        paper_info = scraper.get_paper_info(arxiv_id)
        safe_id = arxiv_id.replace('/', '_').replace('.', '_')
        merged_tex_path = paper_dir / f"{safe_id}_merged.tex"
        merged_file = scraper.merge_tex_files(paper_dir, output_file=merged_tex_path, paper_info=paper_info)
        
        if not merged_file:
            raise RuntimeError("Failed to merge .tex files.")

        html_url, html_source = get_best_html_url(arxiv_id)
        extraction_result = extractor.extract(str(merged_file), html_url=html_url)
        result_dict = _to_jsonable(extraction_result)
        result_dict['status'] = 'success'
        result_dict['html_source_used'] = html_source
        return arxiv_id, result_dict

    except Exception as e:
        error_str = str(e)
        tb_str = traceback.format_exc()
        full_error_message = f"{error_str}\n--- TRACEBACK ---\n{tb_str}"
        
        stage = "unknown"
        if 'download' in error_str.lower(): stage = "download"
        elif 'merge' in error_str.lower(): stage = "merge"
        elif 'extract' in error_str.lower(): stage = "extract"
        
        return arxiv_id, {
            "status": "failed",
            "stage": stage,
            "error_message": full_error_message 
        }