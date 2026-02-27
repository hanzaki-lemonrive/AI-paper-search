#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scimago Journal Rank (SJR) 影响因子过滤器
使用本地 SQLite 数据库存储期刊指标
"""

import sqlite3
import csv
from pathlib import Path
from typing import Optional, List, Dict


class ImpactFactorFilter:
    """基于 Scimago Journal Rank 的影响因子过滤器"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化过滤器

        Args:
            db_path: SJR 数据库路径（默认：cache/sjr_metrics.db）
        """
        if db_path is None:
            # 默认路径：项目根目录下的 cache
            project_root = Path(__file__).parent.parent
            db_path = project_root / "cache" / "sjr_metrics.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """创建 SQLite 数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建期刊表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journals (
                issn TEXT PRIMARY KEY,
                eissn TEXT,
                title TEXT,
                sjr REAL,
                sjr_best_quartile TEXT,
                h_index INTEGER,
                total_docs INTEGER,
                country TEXT,
                areas TEXT,
                categories TEXT,
                year INTEGER
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_title
            ON journals(title)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sjr
            ON journals(sjr DESC)
        ''')

        conn.commit()
        conn.close()

    def import_sjr_csv(self, csv_path: Path, year: int = 2024):
        """
        从 SJR CSV 文件导入数据

        Args:
            csv_path: SJR CSV 文件路径
            year: 数据年份
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        imported = 0
        skipped = 0

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Use semicolon delimiter for SJR CSV files
                reader = csv.DictReader(f, delimiter=';')

                for row in reader:
                    try:
                        # Map CSV columns to database fields
                        issn = row.get('Issn', '') or ''
                        eissn = row.get('Eissn', '') or ''
                        title = row.get('Title', '') or ''
                        sjr_str = row.get('SJR', '') or '0'
                        sjr_quartile = row.get('SJR Best Quartile', '') or ''
                        h_index_str = row.get('H index', '') or '0'
                        total_docs_str = row.get('Total Docs. (2024)', '') or '0'
                        country = row.get('Country', '') or ''
                        areas = row.get('Areas', '') or ''
                        categories = row.get('Categories', '') or ''

                        # Clean SJR value (remove commas, convert to float)
                        sjr = float(sjr_str.replace(',', '').strip()) if sjr_str.strip() else 0.0

                        cursor.execute('''
                            INSERT OR REPLACE INTO journals
                            (issn, eissn, title, sjr, sjr_best_quartile,
                             h_index, total_docs, country, areas, categories, year)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            issn,
                            eissn,
                            title,
                            sjr,
                            sjr_quartile,
                            int(h_index_str) if h_index_str.isdigit() else 0,
                            int(total_docs_str.replace(',', '').strip()) if total_docs_str.strip() else 0,
                            country,
                            areas,
                            categories,
                            year
                        ))
                        imported += 1
                    except Exception as e:
                        skipped += 1
                        continue

            conn.commit()
            print(f"[OK] Imported SJR data ({year}):")
            print(f"  Success: {imported} journals")
            print(f"  Skipped: {skipped} rows")

        except Exception as e:
            print(f"[ERROR] Import failed: {e}")
        finally:
            conn.close()

    def get_journal_sjr(self, journal_name: str, issn: str = '') -> Optional[float]:
        """
        获取期刊的 SJR 分数

        Args:
            journal_name: 期刊名称
            issn: 可选的 ISSN（更精确的匹配）

        Returns:
            SJR 分数，如果未找到返回 None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 优先使用 ISSN 查询
        if issn:
            cursor.execute('''
                SELECT sjr FROM journals
                WHERE issn = ? OR eissn = ?
            ''', (issn, issn))

            result = cursor.fetchone()
            if result and result[0]:
                conn.close()
                return result[0]

        # 使用期刊名称模糊匹配
        cursor.execute('''
            SELECT sjr FROM journals
            WHERE title LIKE ?
            ORDER BY sjr DESC
            LIMIT 1
        ''', (f'%{journal_name}%',))

        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return result[0]

        return None

    def get_journal_quartile(self, journal_name: str, issn: str = '') -> str:
        """
        获取期刊的四分位数

        Returns:
            'Q1', 'Q2', 'Q3', 'Q4', 或 'Unknown'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if issn:
            cursor.execute('''
                SELECT sjr_best_quartile FROM journals
                WHERE issn = ? OR eissn = ?
            ''', (issn, issn))
        else:
            cursor.execute('''
                SELECT sjr_best_quartile FROM journals
                WHERE title LIKE ?
                LIMIT 1
            ''', (f'%{journal_name}%',))

        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return result[0]

        return 'Unknown'

    def filter_papers_by_sjr(
        self,
        papers: List[Dict],
        min_sjr: float = 1.0
    ) -> List[Dict]:
        """
        按 SJR 分数筛选论文

        Args:
            papers: 论文列表
            min_sjr: 最小 SJR 分数

        Returns:
            筛选后的论文列表（带有 SJR 信息）
        """
        filtered = []
        with_sjr = 0
        without_sjr = 0

        for paper in papers:
            # 获取期刊信息
            publication = paper.get('publication', {})
            journal_name = publication.get('title', '')
            issn = publication.get('issn', '')

            # 查找 SJR
            sjr_score = self.get_journal_sjr(journal_name, issn)
            quartile = self.get_journal_quartile(journal_name, issn)

            # 添加到论文数据
            paper['sjr_score'] = sjr_score
            paper['sjr_quartile'] = quartile

            if sjr_score is not None:
                with_sjr += 1

                # 筛选
                if sjr_score >= min_sjr:
                    filtered.append(paper)
            else:
                without_sjr += 1
                # 保留没有 SJR 数据的论文
                filtered.append(paper)

        print(f"[OK] SJR filter complete (min: {min_sjr}):")
        print(f"  With SJR data: {with_sjr} papers")
        print(f"  Without SJR data: {without_sjr} papers")
        print(f"  Final count: {len(filtered)} papers")

        return filtered

    def get_sjr_summary(self, papers: List[Dict]) -> Dict:
        """
        获取论文集的 SJR 统计摘要

        Returns:
            统计字典
        """
        scores = [
            p['sjr_score']
            for p in papers
            if p.get('sjr_score') is not None
        ]

        if not scores:
            return {
                'count': 0,
                'mean': None,
                'median': None,
                'max': None,
                'min': None
            }

        scores_sorted = sorted(scores)
        n = len(scores_sorted)

        return {
            'count': n,
            'mean': sum(scores) / n,
            'median': scores_sorted[n // 2],
            'max': scores_sorted[-1],
            'min': scores_sorted[0]
        }

    def list_top_journals(self, limit: int = 20, area: str = '') -> List[Dict]:
        """
        列出 SJR 最高的期刊

        Args:
            limit: 返回数量
            area: 可选的领域筛选

        Returns:
            期刊列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if area:
            cursor.execute('''
                SELECT title, issn, sjr, sjr_best_quartile, areas
                FROM journals
                WHERE areas LIKE ?
                ORDER BY sjr DESC
                LIMIT ?
            ''', (f'%{area}%', limit))
        else:
            cursor.execute('''
                SELECT title, issn, sjr, sjr_best_quartile, areas
                FROM journals
                ORDER BY sjr DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'title': row[0],
                'issn': row[1],
                'sjr': row[2],
                'quartile': row[3],
                'areas': row[4]
            }
            for row in rows
        ]


def test_filter():
    """测试影响因子过滤器"""
    print("=" * 60)
    print("影响因子过滤器测试")
    print("=" * 60)

    # 创建过滤器
    filter_engine = ImpactFactorFilter()

    # 检查数据库状态
    conn = sqlite3.connect(filter_engine.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM journals')
    count = cursor.fetchone()[0]
    conn.close()

    print(f"\n数据库状态:")
    print(f"  路径: {filter_engine.db_path}")
    print(f"  期刊数: {count}")

    if count == 0:
        print("\n⚠ 数据库为空，需要导入 SJR 数据")
        print("\n导入步骤:")
        print("  1. 访问 https://www.scimagojr.com/")
        print("  2. 点击 'Journal Rankings'")
        print("  3. 配置筛选条件，点击 'Export' → 'CSV'")
        print("  4. 保存到 cache/sjr_2024.csv")
        print("  5. 运行导入命令")
        print("\n导入命令:")
        print("  python -c \"from script.impact_filter import ImpactFactorFilter;")
        print("                f = ImpactFactorFilter();")
        print("                f.import_sjr_csv(Path('cache/sjr_2024.csv'), 2024)\"")
    else:
        # 列出顶级期刊
        print("\n【顶级期刊 (按 SJR)】")
        top_journals = filter_engine.list_top_journals(limit=10)

        for idx, journal in enumerate(top_journals, 1):
            print(f"\n{idx}. {journal['title']}")
            print(f"   SJR: {journal['sjr']}")
            print(f"   四分位: {journal['quartile']}")
            print(f"   领域: {journal['areas']}")

        # 测试论文筛选
        print("\n" + "=" * 60)
        print("【测试论文筛选】")

        test_papers = [
            {
                'title': 'Test Paper 1',
                'publication': {
                    'title': 'Nature',
                    'issn': '0028-0836'
                }
            },
            {
                'title': 'Test Paper 2',
                'publication': {
                    'title': 'Unknown Journal',
                    'issn': ''
                }
            }
        ]

        filtered = filter_engine.filter_papers_by_sjr(
            papers=test_papers,
            min_sjr=1.0
        )

        print(f"\n筛选结果:")
        for paper in filtered:
            print(f"  {paper['title']}:")
            print(f"    SJR: {paper.get('sjr_score', 'N/A')}")
            print(f"    四分位: {paper.get('sjr_quartile', 'N/A')}")

    print("\n" + "=" * 60)
    print("✓ 测试完成")
    print("=" * 60)


if __name__ == '__main__':
    import sqlite3
    test_filter()
