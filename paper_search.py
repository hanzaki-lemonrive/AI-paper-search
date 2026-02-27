#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Paper Search Minimal CLI
Optimized for AI agent consumption (e.g., Copaw)

Core functionality:
- Multi-database paper search (arXiv, PubMed, ACM)
- PDF download
- JSON output for easy parsing
- Clean status codes
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from findpapers import search as findpapers_search
    import arxiv
except ImportError as e:
    print(json.dumps({
        "status": "error",
        "error": f"Import failed: {e}",
        "message": "Install dependencies: pip install findpapers arxiv"
    }, ensure_ascii=False))
    sys.exit(1)

# Import new PubMed modules
try:
    from script.pubmed_searcher import PubMedSearcher
    from script.pdf_downloader import PDFDownloadManager
    from script.impact_filter import ImpactFactorFilter
    from config.config import get_config
except ImportError as e:
    print(f"Warning: PubMed modules not available: {e}")


class PaperSearch:
    """Minimal paper search for AI agents"""

    def __init__(self, query, output_dir=None, limit=10, limit_per_database=None,
                 enable_pdf_download=True, export_unavailable=True,
                 pubmed_mode=False, min_sjr=None, free_only=False, date_range=None):
        """
        Initialize search

        Args:
            query: Findpapers format query (e.g., '[AI] AND [healthcare]')
            output_dir: Output directory path
            limit: Total paper limit
            limit_per_database: Per-database limit (enables multi-db search)
            enable_pdf_download: Whether to download PDFs
            export_unavailable: Whether to export unavailable papers list
            pubmed_mode: Use specialized PubMed searcher
            min_sjr: Minimum SJR score for impact factor filtering
            free_only: Only retrieve papers with free full text
            date_range: Optional (start_year, end_year) tuple
        """
        self.query = query.strip()
        self.limit = limit
        self.limit_per_database = limit_per_database
        self.enable_pdf_download = enable_pdf_download
        self.export_unavailable = export_unavailable
        self.pubmed_mode = pubmed_mode
        self.min_sjr = min_sjr
        self.free_only = free_only
        self.date_range = date_range
        self.results = None

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = PROJECT_ROOT / "papers" / f"search_{timestamp}"

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_file = self.output_dir / "results.json"
        self.pdf_dir = self.output_dir / "pdfs"
        self.pdf_dir.mkdir(exist_ok=True)
        self.unavailable_file = self.output_dir / "unavailable_papers.md"

        # Load configuration
        self.config = get_config()

    def search(self):
        """Search papers using findpapers or PubMed mode"""
        try:
            if self.pubmed_mode:
                # Use specialized PubMed searcher
                print("使用 PubMed 搜索模式...")

                searcher = PubMedSearcher(
                    email=self.config.ncbi_email,
                    api_key=self.config.ncbi_api_key
                )

                papers = searcher.search(
                    query=self.query,
                    max_results=self.limit,
                    date_range=self.date_range,
                    has_free_full_text=self.free_only
                )

                self.results = {
                    'papers': papers,
                    'number_of_papers': len(papers),
                    'number_of_papers_by_database': {'PubMed': len(papers)}
                }

                # Apply impact factor filtering if specified
                if self.min_sjr is not None and self.min_sjr > 0:
                    self._filter_by_impact_factor()

            else:
                # Use existing findpapers search
                findpapers_search(
                    query=self.query,
                    outputpath=str(self.json_file),
                    limit=self.limit,
                    limit_per_database=self.limit_per_database,
                )

                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.results = json.load(f)

            return True

        except Exception as e:
            self.results = {
                "status": "error",
                "error": str(e)
            }
            return False

    def _filter_by_impact_factor(self):
        """Filter papers by minimum SJR score"""
        if not self.results or 'papers' not in self.results:
            return

        try:
            filter_engine = ImpactFactorFilter()

            # 检查数据库是否为空
            import sqlite3
            conn = sqlite3.connect(filter_engine.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM journals')
            count = cursor.fetchone()[0]
            conn.close()

            if count == 0:
                print("\n⚠ SJR 数据库为空，无法进行影响因子筛选")
                print("\n💡 快速设置:")
                print("  运行: python script/setup_sjr.py")
                print("  或查看: PUBMED_GUIDE.md 中的 'SJR 数据设置' 章节")
                print("\n继续搜索（不进行影响因子筛选）...\n")
                return

            papers = self.results.get('papers', [])

            filtered = filter_engine.filter_papers_by_sjr(
                papers=papers,
                min_sjr=self.min_sjr
            )

            self.results['papers'] = filtered
            self.results['number_of_papers'] = len(filtered)

            # Print summary
            summary = filter_engine.get_sjr_summary(filtered)
            if summary['count'] > 0:
                print(f"\n✓ SJR 筛选完成 (最小: {self.min_sjr}):")
                print(f"  平均: {summary['mean']:.2f}")
                print(f"  中位数: {summary['median']:.2f}")
                print(f"  最高: {summary['max']:.2f}")
                print(f"  最低: {summary['min']:.2f}")

        except Exception as e:
            print(f"\n⚠ 影响因子过滤失败: {e}")
            print(f"  提示: 运行 python script/setup_sjr.py 设置 SJR 数据")

    def _download_pdfs(self):
        """Download PDFs for arXiv and PubMed papers"""
        if not self.results or 'papers' not in self.results:
            return 0

        papers = self.results.get('papers', [])
        downloaded = 0

        # Check if using PubMed mode
        if self.pubmed_mode:
            # Use enhanced PDF downloader
            print("\n下载 PDFs...")
            downloader = PDFDownloadManager(output_dir=self.pdf_dir)

            # Prepare institution credentials if configured
            institution_credentials = None
            if self.config.institutional_proxy:
                institution_credentials = {
                    'ezproxy_url': self.config.institutional_proxy,
                    'username': self.config.institution_username,
                    'password': self.config.institution_password
                }

            for idx, paper in enumerate(papers, 1):
                print(f"  [{idx}/{len(papers)}] {paper.get('title', 'N/A')[:60]}...")

                result = downloader.download_paper_pdf(
                    paper=paper,
                    pmid=paper.get('pmid', ''),
                    doi=paper.get('doi', ''),
                    institution_credentials=institution_credentials
                )

                if result['success']:
                    paper['pdf_path'] = result['path']
                    paper['pdf_downloaded'] = True
                    paper['pdf_source'] = result['source']
                    downloaded += 1
                else:
                    paper['pdf_downloaded'] = False
                    paper['pdf_error'] = result.get('error', 'Unknown error')

            print(f"\n✓ 下载完成: {downloaded}/{len(papers)} 篇")
        else:
            # Use existing arXiv download logic
            for paper in papers:
                # Try arXiv URLs
                for url in paper.get('urls', []):
                    if 'arxiv.org' in url:
                        arxiv_id = url.split('/')[-1]
                        try:
                            search = arxiv.Search(id_list=[arxiv_id])
                            for result in search.results():
                                pdf_path = self.pdf_dir / f"{arxiv_id}.pdf"
                                result.download_pdf(filename=str(pdf_path))

                                # Add PDF path to paper data
                                paper['pdf_path'] = str(pdf_path)
                                paper['pdf_downloaded'] = True
                                downloaded += 1
                                break
                        except Exception:
                            paper['pdf_downloaded'] = False
                        break
                else:
                    # No arXiv URL found, mark as not downloaded
                    paper['pdf_downloaded'] = False

        return downloaded

    def _export_unavailable_papers(self):
        """Export list of papers that couldn't be downloaded"""
        if not self.results or 'papers' not in self.results:
            return 0

        papers = self.results.get('papers', [])
        unavailable = [p for p in papers if not p.get('pdf_downloaded', False)]

        if not unavailable:
            return 0

        # Create markdown file
        content = f"# 无法下载的论文列表\n\n"
        content += f"**查询：** {self.query}\n"
        content += f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**总计：** {len(papers)} 篇\n"
        content += f"**已下载：** {len(papers) - len(unavailable)} 篇\n"
        content += f"**无法下载：** {len(unavailable)} 篇\n\n"
        content += "---\n\n"

        for idx, paper in enumerate(unavailable, 1):
            content += f"## {idx}. {paper.get('title', 'N/A')}\n\n"

            # Basic info
            content += f"- **年份：** {paper.get('publication_date', '')[:4] if paper.get('publication_date') else 'N/A'}\n"
            content += f"- **数据库：** {', '.join(paper.get('databases', ['N/A']))}\n"

            # Authors
            authors = paper.get('authors', [])
            if authors:
                content += f"- **作者：** {', '.join(authors[:10])}" + ("..." if len(authors) > 10 else "") + "\n"

            # Keywords
            keywords = paper.get('keywords', [])
            if keywords:
                content += f"- **关键词：** {', '.join(keywords[:15])}" + ("..." if len(keywords) > 15 else "") + "\n"

            # Impact factor (期刊信息)
            publication = paper.get('publication', {})
            if publication:
                content += f"- **期刊/会议：** {publication.get('title', 'N/A')}\n"
                content += f"- **类型：** {publication.get('category', 'N/A')}\n"

            # URLs
            urls = paper.get('urls', [])
            if urls:
                content += f"- **链接：**\n"
                for url in urls[:5]:  # Limit to 5 URLs
                    content += f"  - {url}\n"
                if len(urls) > 5:
                    content += f"  - ... (共 {len(urls)} 个链接)\n"

            # Abstract/Summary
            abstract = paper.get('abstract', '')
            if abstract:
                # Limit abstract length
                if len(abstract) > 800:
                    abstract = abstract[:800] + "..."
                content += f"\n**摘要：**\n{abstract}\n"

            # DOI
            doi = paper.get('doi', '')
            if doi:
                content += f"\n- **DOI：** {doi}\n"

            content += "\n---\n\n"

        # Add summary at the end
        content += "\n## 说明\n\n"
        content += "以下数据库的论文通常需要机构订阅才能下载全文：\n"
        content += "- PubMed: 生物医学文献数据库\n"
        content += "- medRxiv: 医学预印本\n"
        content += "- ACM Digital Library: 计算机科学文献\n"
        content += "- IEEE: 工程技术文献\n"
        content += "- Scopus: 多学科文献数据库\n\n"
        content += "建议：\n"
        content += "1. 联系所在图书馆获取访问权限\n"
        content += "2. 使用 Sci-Hub 等开放获取资源\n"
        content += "3. 直接联系作者索取全文\n"

        # Write to file
        with open(self.unavailable_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return len(unavailable)

    def get_result(self):
        """Get formatted result for agent consumption"""
        if not self.results:
            return {
                "status": "error",
                "error": "No results"
            }

        papers = self.results.get('papers', [])
        total = len(papers)

        return {
            "status": "success",
            "query": self.query,
            "total": total,
            "output_dir": str(self.output_dir),
            "json_file": str(self.json_file),
            "pdf_dir": str(self.pdf_dir),
            "pdfs_downloaded": sum(1 for p in papers if p.get('pdf_downloaded')),
            "by_database": self.results.get('number_of_papers_by_database', {}),
            "papers": [
                {
                    "title": p.get('title', ''),
                    "authors": p.get('authors', [])[:5],
                    "year": p.get('publication_date', '')[:4] if p.get('publication_date') else '',
                    "abstract": p.get('abstract', '')[:500] + '...' if p.get('abstract') else '',
                    "database": p.get('databases', ['Unknown'])[0] if p.get('databases') else 'Unknown',
                    "urls": p.get('urls', []),
                    "pdf_path": p.get('pdf_path', None),
                    "pdf_downloaded": p.get('pdf_downloaded', False)
                }
                for p in papers
            ]
        }

    def run(self):
        """Execute full search pipeline"""
        success = self.search()

        if success and self.enable_pdf_download:
            self._download_pdfs()

        if self.export_unavailable:
            unavailable_count = self._export_unavailable_papers()
            if unavailable_count > 0:
                print(f"Exported {unavailable_count} unavailable papers to: {self.unavailable_file}")

        return self.get_result()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Paper Search Minimal CLI - For AI agent consumption',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('query', help='Search query in findpapers format (e.g., "[AI] AND [healthcare]")')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-l', '--limit', type=int, default=10, help='Total paper limit (default: 10)')
    parser.add_argument('--limit-per-db', type=int, help='Per-database limit (enables multi-db search)')
    parser.add_argument('--no-pdf', action='store_true', help='Skip PDF download')
    parser.add_argument('--no-export-unavailable', action='store_true', help='Skip exporting unavailable papers list')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')

    # PubMed mode options
    parser.add_argument('--pubmed-mode', action='store_true',
                       help='Use specialized PubMed searcher with enhanced features')
    parser.add_argument('--min-sjr', type=float,
                       help='Minimum SJR score for impact factor filtering (e.g., 1.5)')
    parser.add_argument('--free-only', action='store_true',
                       help='Only retrieve papers with free full text available')
    parser.add_argument('--date-range', nargs=2, type=int, metavar=('START', 'END'),
                       help='Filter by publication year range (e.g., --date-range 2020 2024)')

    args = parser.parse_args()

    # Validate date range
    date_range = None
    if hasattr(args, 'date_range') and args.date_range:
        if args.date_range[0] > args.date_range[1]:
            print("Error: Start year must be less than or equal to end year")
            sys.exit(1)
        date_range = tuple(args.date_range)

    # Run search
    searcher = PaperSearch(
        query=args.query,
        output_dir=args.output,
        limit=args.limit,
        limit_per_database=getattr(args, 'limit_per_db', None),
        enable_pdf_download=not args.no_pdf,
        export_unavailable=not args.no_export_unavailable,
        pubmed_mode=getattr(args, 'pubmed_mode', False),
        min_sjr=getattr(args, 'min_sjr', None),
        free_only=getattr(args, 'free_only', False),
        date_range=date_range
    )

    result = searcher.run()

    # Output
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {result['status']}")
        print(f"Total papers: {result.get('total', 0)}")
        print(f"Output: {result.get('output_dir', 'N/A')}")
        if result.get('by_database'):
            print("By database:")
            for db, count in result['by_database'].items():
                print(f"  {db}: {count}")

    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
