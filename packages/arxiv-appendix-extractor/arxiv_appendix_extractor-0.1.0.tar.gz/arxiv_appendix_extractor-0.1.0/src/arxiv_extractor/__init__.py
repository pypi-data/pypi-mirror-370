# This file makes 'arxiv_extractor' a Python package.

__version__ = "0.1.0"

from .scraper import ArxivScraper
from .extractor import ImprovedAppendixExtractor
from .pipeline import process_single_paper
from .cleanup import run_cleanup

# You can define what gets imported when someone does 'from arxiv_extractor import *'
__all__ = [
    "ArxivScraper",
    "ImprovedAppendixExtractor",
    "process_single_paper",
    "run_cleanup",
]