import sys
import time
import tarfile
import gzip
import logging
import requests
import feedparser
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import traceback

logger = logging.getLogger(__name__)

class ArxivScraper:
    """arXiv论文LaTeX源文件爬取器"""
    
    def __init__(self, output_dir: str = "arxiv_papers", max_workers: int = 5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def search_papers_by_date(self, date: str, category: str = "cs", max_results: int = 100) -> List[Dict]:
        papers = []
        try:
            base_url = 'http://export.arxiv.org/api/query'
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_str = date_obj.strftime('%Y%m%d')
            next_date_str = (date_obj + timedelta(days=1)).strftime('%Y%m%d')
            search_query = f'submittedDate:[{date_str}0000 TO {next_date_str}0000]'
            if category:
                search_query = f'cat:{category}* AND {search_query}'
            
            params = {
                'search_query': search_query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            logger.info(f"Querying arXiv API with params: {params}")
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            if hasattr(feed, 'bozo_exception') and feed.bozo_exception:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            for entry in feed.entries:
                try:
                    arxiv_id = entry.id.split('/')[-1].replace('v1', '').replace('v2', '').replace('v3', '') # Basic cleaning
                    if 'abs/' in arxiv_id:
                        arxiv_id = arxiv_id.split('abs/')[-1]

                    paper_info = {
                        'id': arxiv_id,
                        'title': entry.title.replace('\n', ' ').strip(),
                        'authors': [author.name for author in entry.authors],
                        'abstract': entry.summary,
                        'published': entry.published,
                    }
                    papers.append(paper_info)
                except Exception as e:
                    logger.warning(f"Error parsing a paper entry: {e}")
            logger.info(f"Found {len(papers)} papers for date: {date}, category: {category}")
        except Exception as e:
            logger.error(f"Failed to search papers: {e}")
            traceback.print_exc()
        return papers

    def get_paper_info(self, arxiv_id: str) -> Optional[Dict]:
        try:
            base_url = 'http://export.arxiv.org/api/query'
            params = {'id_list': arxiv_id, 'max_results': 1}
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            if feed.entries:
                entry = feed.entries[0]
                return {
                    'id': arxiv_id,
                    'title': entry.title.replace('\n', ' ').strip(),
                    'authors': [author.name for author in entry.authors],
                    'abstract': entry.summary,
                    'published': entry.published,
                }
            return {'id': arxiv_id, 'title': arxiv_id, 'authors': [], 'abstract': '', 'published': ''}
        except Exception as e:
            logger.warning(f"Failed to get info for {arxiv_id}: {e}")
            return {'id': arxiv_id, 'title': arxiv_id, 'authors': [], 'abstract': '', 'published': ''}

    def download_latex_source(self, paper_id: str, retry_times: int = 3) -> Optional[Path]:
        paper_id = paper_id.strip()
        safe_id = paper_id.replace('/', '_').replace('.', '_')
        paper_dir = self.output_dir / safe_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        source_url = f'https://arxiv.org/e-print/{paper_id}'
        
        for attempt in range(retry_times):
            try:
                logger.info(f"Downloading source for {paper_id} (Attempt {attempt + 1}/{retry_times})")
                response = self.session.get(source_url, timeout=60, stream=True)
                if response.status_code == 404:
                    logger.error(f"Source for {paper_id} not found (404).")
                    return None
                response.raise_for_status()
                content = response.content
                if not content:
                    logger.error(f"Downloaded content for {paper_id} is empty.")
                    return None
                
                file_path = self._save_and_identify_file(content, paper_dir, safe_id)
                if file_path:
                    if file_path.suffix in ['.gz', '.tar']:
                        self._extract_archive(file_path, paper_dir)
                    
                    if list(paper_dir.rglob('*.tex')):
                        logger.info(f"Successfully downloaded and extracted {paper_id}")
                        return paper_dir
                    else:
                        self._identify_latex_files(paper_dir)
                        if list(paper_dir.rglob('*.tex')):
                            return paper_dir
            except requests.exceptions.RequestException as e:
                logger.warning(f"Network error for {paper_id}: {e}")
            except Exception as e:
                logger.warning(f"Failed to download {paper_id}: {e}")
                traceback.print_exc()
            if attempt < retry_times - 1:
                time.sleep(2 ** attempt)
        logger.error(f"Giving up on downloading {paper_id} after {retry_times} attempts.")
        return None

    def _save_and_identify_file(self, content: bytes, paper_dir: Path, safe_id: str) -> Optional[Path]:
        try:
            if content.startswith(b'\x1f\x8b'):
                file_path = paper_dir / f'{safe_id}.gz'
            elif b'ustar' in content[257:262]:
                file_path = paper_dir / f'{safe_id}.tar'
            else:
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    if '\\documentclass' in text_content or '\\begin{document}' in text_content:
                        file_path = paper_dir / 'main.tex'
                    else:
                        file_path = paper_dir / f'{safe_id}.txt'
                except:
                    file_path = paper_dir / f'{safe_id}.bin'
            with open(file_path, 'wb') as f:
                f.write(content)
            return file_path
        except Exception as e:
            logger.error(f"Error saving file in {paper_dir}: {e}")
            return None

    def _extract_archive(self, archive_path: Path, extract_to: Path):
        try:
            if archive_path.suffix == '.gz':
                with gzip.open(archive_path, 'rb') as f_in:
                    decompressed_content = f_in.read()
                if b'ustar' in decompressed_content[257:262]:
                    temp_tar_path = extract_to / 'temp.tar'
                    with open(temp_tar_path, 'wb') as f_out:
                        f_out.write(decompressed_content)
                    with tarfile.open(temp_tar_path) as tar:
                        self._safe_extract(tar, extract_to)
                    temp_tar_path.unlink()
                else:
                    (extract_to / (archive_path.stem + '.tex')).write_bytes(decompressed_content)
            elif archive_path.suffix == '.tar':
                with tarfile.open(archive_path) as tar:
                    self._safe_extract(tar, extract_to)
            archive_path.unlink()
        except Exception as e:
            logger.error(f"Failed to extract {archive_path}: {e}")

    def _safe_extract(self, tar, path):
        for member in tar.getmembers():
            member_path = (path / member.name).resolve()
            if path.resolve() in member_path.parents:
                tar.extract(member, path)
            else:
                logger.warning(f"Skipping unsafe tar member: {member.name}")

    def _identify_latex_files(self, paper_dir: Path):
        for f in paper_dir.iterdir():
            if f.is_file() and f.suffix not in ['.tex', '.gz', '.tar']:
                try:
                    content = f.read_text(encoding='utf-8', errors='ignore')[:1000]
                    if '\\documentclass' in content:
                        f.rename(f.with_suffix('.tex'))
                except Exception:
                    continue

    def merge_tex_files(self, paper_dir: Path, output_file: Path = None, paper_info: Dict = None) -> Optional[Path]:
        if output_file is None:
            output_file = paper_dir / 'merged.tex'
        tex_files = list(paper_dir.rglob('*.tex'))
        if not tex_files:
            logger.warning(f"No .tex files found in {paper_dir}")
            return None
        
        tex_files.sort(key=lambda p: ('main' not in p.name.lower(), p.name))
        
        try:
            with open(output_file, 'w', encoding='utf-8', errors='ignore') as f_out:
                if paper_info:
                    f_out.write(f"% Paper ID: {paper_info.get('id', 'N/A')}\n")
                    f_out.write(f"% Title: {paper_info.get('title', 'N/A')}\n\n")
                
                for tex_file in tex_files:
                    f_out.write(f"\n\n% ========== SOURCE: {tex_file.relative_to(paper_dir)} ==========\n\n")
                    f_out.write(tex_file.read_text(encoding='utf-8', errors='ignore'))
            logger.info(f"Merged {len(tex_files)} files into {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to merge .tex files in {paper_dir}: {e}")
            return None