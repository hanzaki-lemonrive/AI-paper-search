#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
论文检索助手 - 主脚本

功能：
1. 从查询文件读取搜索查询
2. 使用 findpapers 进行多数据库检索
3. 下载论文 PDF
4. 保存检索结果（JSON + PDF）

作者：Nova & 仲清
创建时间：2026-02-22
更新时间：2026-02-22（移除邮件通知）
"""

import sys
import os
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# 确保使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from findpapers import search as findpapers_search
    import arxiv
except ImportError as e:
    print(f"错误：导入模块失败: {e}")
    print("请确保已安装所有依赖：pip install findpapers arxiv")
    sys.exit(1)


class PaperResearchAssistant:
    """论文检索助手主类"""

    def __init__(self, query_file=None, query=None, output_dir=None, limit=10, limit_per_database=None):
        """
        初始化助手

        参数:
            query_file: 查询文件路径
            query: 直接查询字符串（优先级高于 query_file）
            output_dir: 输出目录
            limit: 检索论文数量限制（总数量）
            limit_per_database: 每个数据库的检索数量限制（None = 无限制）
        """
        # DEBUG MARKER: v3 - added limit_per_database
        import sys
        print(f"[DEBUG] PaperResearchAssistant.__init__ called with limit_per_database", file=sys.stderr)
        self.query = None
        self.output_dir = Path(output_dir) if output_dir else None
        self.limit = limit
        self.limit_per_database = limit_per_database
        self.results = None

        # 读取查询
        if query:
            self.query = query.strip()
        elif query_file:
            self.query = self._read_query_file(query_file)
        else:
            raise ValueError("必须提供 query 或 query_file 参数")

        if not self.query:
            raise ValueError("查询内容不能为空")

        # 设置输出目录
        if not self.output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = PROJECT_ROOT / "papers" / f"search_{timestamp}"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"="*60)
        print(f"论文检索助手")
        print(f"="*60)
        print(f"查询: {self.query}")
        print(f"输出目录: {self.output_dir}")
        print(f"数量限制: {self.limit}")
        print(f"="*60)

    def _read_query_file(self, query_file):
        """读取查询文件"""
        query_path = PROJECT_ROOT / "queries" / query_file
        if not query_path.exists():
            query_path = Path(query_file)

        if not query_path.exists():
            raise FileNotFoundError(f"查询文件不存在: {query_file}")

        with open(query_path, 'r', encoding='utf-8') as f:
            query = f.read().strip()

        print(f"从文件读取查询: {query_path}")
        return query

    def search_papers(self):
        """使用 findpapers 检索论文"""
        print("\n[1/3] 开始检索论文...")
        print(f"数据库: arXiv, PubMed, ACM (免费)")
        print(f"查询格式: {self.query}")

        try:
            # 输出文件路径
            output_file = str(self.output_dir / "results.json")

            # 调用 findpapers
            findpapers_search(
                query=self.query,
                outputpath=output_file,
                limit=self.limit,
                limit_per_database=self.limit_per_database,
                # 可以指定数据库
                # databases=['arxiv', 'pubmed'],
            )

            # 读取结果
            with open(output_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)

            num_papers = self.results.get('number_of_papers', 0)
            print(f"\n检索完成！找到 {num_papers} 篇论文")
            print(f"结果保存至: {output_file}")

            return True

        except Exception as e:
            print(f"\n错误：检索失败 - {e}")
            return False

    def download_pdfs(self):
        """下载论文 PDF"""
        if not self.results:
            print("错误：没有检索结果，请先运行 search_papers()")
            return False

        print(f"\n[2/3] 开始下载 PDF...")

        papers = self.results.get('papers', [])
        downloaded = 0
        failed = 0

        # 创建 PDF 保存目录
        pdf_dir = self.output_dir / "pdfs"
        pdf_dir.mkdir(exist_ok=True)

        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown')
            print(f"\n[{i}/{len(papers)}] {title}")

            # 尝试从不同来源下载
            pdf_url = None
            filename = None

            # 1. 检查 arXiv URL
            for url in paper.get('urls', []):
                if 'arxiv.org' in url:
                    arxiv_id = url.split('/')[-1]
                    try:
                        # 使用 arxiv 库下载
                        search = arxiv.Search(id_list=[arxiv_id])
                        for result in search.results():
                            pdf_filename = pdf_dir / f"{arxiv_id}.pdf"
                            result.download_pdf(filename=str(pdf_filename))
                            print(f"  ✓ 已下载: {pdf_filename.name}")
                            downloaded += 1
                            break
                    except Exception as e:
                        print(f"  ✗ arXiv 下载失败: {e}")
                        failed += 1
                    break
            else:
                # 非 arXiv 论文，尝试直接 URL 下载
                for url in paper.get('urls', []):
                    if '.pdf' in url:
                        print(f"  ⚠ PDF URL: {url}")
                        print(f"  ℹ 请手动下载（需要机构权限或订阅）")
                        break
                else:
                    print(f"  ⚠ 未找到 PDF 下载链接")

        print(f"\n下载完成！")
        print(f"  成功: {downloaded} 篇")
        print(f"  失败/需手动: {failed} 篇")

        return downloaded > 0

    def generate_summary(self):
        """生成检索结果摘要"""
        if not self.results:
            return None

        papers = self.results.get('papers', [])
        summary = {
            'query': self.query,
            'total': len(papers),
            'by_database': self.results.get('number_of_papers_by_database', {}),
            'papers': []
        }

        for paper in papers[:10]:  # 只显示前 10 篇
            summary['papers'].append({
                'title': paper.get('title', ''),
                'authors': paper.get('authors', [])[:3],  # 只显示前 3 个作者
                'year': paper.get('publication_date', '')[:4] if paper.get('publication_date') else '',
                'database': paper.get('databases', ['Unknown'])[0] if paper.get('databases') else 'Unknown'
            })

        return summary

    def show_completion_summary(self):
        """显示完成摘要和文件位置"""
        print(f"\n{'='*60}")
        print(f"✓ 所有任务完成！")
        print(f"{'='*60}")

        summary = self.generate_summary()

        print(f"\n📊 检索统计")
        print(f"{'─'*40}")
        print(f"  总数: {summary['total']} 篇")

        for db, count in summary['by_database'].items():
            print(f"  {db}: {count} 篇")

        print(f"\n📁 文件位置")
        print(f"{'─'*40}")
        print(f"  结果目录: {self.output_dir}")
        print(f"  JSON文件: {self.output_dir / 'results.json'}")
        print(f"  PDF目录: {self.output_dir / 'pdfs'}")

        print(f"\n💡 打开文件夹")
        print(f"{'─'*40}")
        print(f"  文件资源管理器中打开:")
        print(f"  {self.output_dir}")

        # 尝试自动打开文件夹
        try:
            if sys.platform == 'win32':
                os.startfile(self.output_dir)
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(self.output_dir)])
            else:
                subprocess.run(['xdg-open', str(self.output_dir)])
            print(f"\n  ✓ 已自动打开文件夹")
        except Exception as e:
            print(f"\n  ℹ 如需手动打开，复制上述路径")

        print(f"\n{'='*60}\n")

    def run(self, open_folder=True):
        """运行完整流程

        参数:
            open_folder: 是否自动打开结果文件夹
        """
        print(f"\n开始执行检索流程...")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 1. 检索
            if not self.search_papers():
                return False

            # 2. 下载 PDF
            self.download_pdfs()

            # 3. 显示完成摘要
            self.show_completion_summary()

            return True

        except KeyboardInterrupt:
            print(f"\n\n中断：用户取消操作")
            return False
        except Exception as e:
            print(f"\n\n错误：{e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='论文检索助手 - 多数据库论文检索和下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从查询文件检索
  python paper_research.py -q test_query.txt

  # 直接指定查询（注意格式）
  python paper_research.py --query '[\"AI\"] AND [\"healthcare\"]'

  # 指定输出目录和数量
  python paper_research.py -q test_query.txt -o papers/my_search -l 20

  # 禁用邮件通知
  python paper_research.py -q test_query.txt --no-notify

查询格式:
  - 术语用方括号: [\"machine learning\"]
  - 布尔运算符大写: AND, OR, AND NOT
  - 示例: [\"AI\"] AND [\"deep learning\"] OR [\"neural networks\"]
        """
    )

    parser.add_argument(
        '-q', '--query-file',
        help='查询文件路径（保存在 queries/ 目录下）'
    )

    parser.add_argument(
        '--query',
        help='直接指定查询字符串'
    )

    parser.add_argument(
        '-o', '--output-dir',
        help='输出目录（默认：papers/search_TIMESTAMP）'
    )

    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=10,
        help='检索论文数量限制（默认：10）'
    )

    parser.add_argument(
        '--limit-per-database',
        type=int,
        default=None,
        help='每个数据库的检索数量限制（默认：无限制，可从多个数据库获取更多结果）'
    )

    parser.add_argument(
        '--no-notify',
        action='store_true',
        help='禁用邮件通知'
    )

    args = parser.parse_args()

    # 验证参数
    if not args.query_file and not args.query:
        parser.print_help()
        print("\n错误：必须提供 -q/--query-file 或 --query 参数")
        sys.exit(1)

    try:
        # 创建助手并运行
        assistant = PaperResearchAssistant(
            query_file=args.query_file,
            query=args.query,
            output_dir=args.output_dir,
            limit=args.limit,
            limit_per_database=args.limit_per_database
        )

        success = assistant.run()
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
