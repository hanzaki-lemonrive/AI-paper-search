#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PubMed 搜索模块
使用 pymed 库搜索 PubMed，支持 PMC 开放获取检测
"""

import re
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime


class PubMedSearcher:
    """PubMed 搜索器 - 使用 pymed 库"""

    def __init__(self, email: str, api_key: Optional[str] = None):
        """
        初始化 PubMed 搜索器

        Args:
            email: NCBI 要求的邮箱地址
            api_key: 可选的 NCBI API Key（提高速率限制）
        """
        self.email = email
        self.api_key = api_key

        # 速率限制：有 API Key 为 10 请求/秒，否则 3 请求/秒
        self.min_interval = 0.1 if api_key else 0.34
        self.last_request_time = 0

        try:
            from pymed import PubMed
            # pymed 只接受 email 参数
            self.pubmed = PubMed(email=email)
            # 如果有 API Key，可以手动设置到请求头
            if api_key:
                # pymed 库不直接支持 API key，但我们可以存储它供将来使用
                pass
        except ImportError:
            raise ImportError(
                "pymed 未安装。请运行: pip install pymed"
            )

    def _rate_limit_wait(self):
        """速率限制等待"""
        now = time.time()
        elapsed = now - self.last_request_time

        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        self.last_request_time = time.time()

    def search(
        self,
        query: str,
        max_results: int = 20,
        date_range: Optional[tuple] = None,
        has_free_full_text: bool = False
    ) -> List[Dict]:
        """
        搜索 PubMed

        Args:
            query: 查询字符串（支持 findpapers 格式或自然语言）
            max_results: 最大结果数
            date_range: 可选的 (起始年, 结束年) 元组
            has_free_full_text: 是否仅搜索免费全文

        Returns:
            论文字典列表（兼容 findpapers 格式）
        """
        # 转换查询格式
        search_query = self._convert_query_format(query)

        # 添加日期筛选
        if date_range:
            start_year, end_year = date_range
            search_query += f' AND ({start_year}:{end_year}[Date - Publication])'

        # 添加免费全文筛选
        if has_free_full_text:
            search_query += ' AND ("free full text"[Filter])'

        print(f"搜索查询: {search_query}")

        # 执行搜索
        self._rate_limit_wait()

        try:
            results = self.pubmed.query(search_query, max_results=max_results)
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

        # 处理结果
        papers = []
        for article in results:
            self._rate_limit_wait()

            try:
                paper_data = self._parse_article(article)
                if paper_data:
                    # 检查 PMC 可用性
                    pmid = paper_data.get('pmid', '')
                    if pmid:
                        paper_data['has_pmc'] = self._check_pmc_availability(pmid)
                    else:
                        paper_data['has_pmc'] = False

                    papers.append(paper_data)

            except Exception as e:
                print(f"解析文章失败: {e}")
                continue

        print(f"找到 {len(papers)} 篇论文")
        return papers

    def _convert_query_format(self, query: str) -> str:
        """
        转换 findpapers 格式到 PubMed 格式

        Examples:
            [machine learning] -> "machine learning"[All Fields]
            ["deep learning"] AND [AI] -> "deep learning"[All Fields] AND "AI"[All Fields]

        Args:
            query: findpapers 格式查询

        Returns:
            PubMed Entrez 格式查询
        """
        result = query

        # 替换 ["phrase search"] -> "phrase"[All Fields]
        result = re.sub(r'\["([^"]+)"\]', r'"\1"[All Fields]', result)

        # 替换 [single word] -> word[All Fields]
        result = re.sub(r'\[([^\]]+)\]', r'\1[All Fields]', result)

        return result

    def _parse_article(self, article) -> Dict:
        """
        解析 pymed 返回的文章对象

        Args:
            article: pymed.Article 对象

        Returns:
            findpapers 兼容格式的字典
        """
        # 基本元数据
        paper = {
            'title': '',
            'authors': [],
            'abstract': '',
            'publication_date': '',
            'doi': '',
            'keywords': [],
            'publication': {
                'title': '',
                'issn': '',
                'volume': '',
                'issue': '',
                'category': 'Journal'
            },
            'databases': ['PubMed'],
            'urls': [],
            'pmid': ''
        }

        # 标题
        if hasattr(article, 'title') and article.title:
            paper['title'] = article.title

        # 作者
        if hasattr(article, 'authors') and article.authors:
            authors = []
            for author in article.authors:
                if hasattr(author, 'lastname') and hasattr(author, 'firstname'):
                    name = f"{author.firstname} {author.lastname}"
                    authors.append(name)
                elif hasattr(author, 'lastname'):
                    authors.append(author.lastname)
            paper['authors'] = authors

        # 摘要
        if hasattr(article, 'abstract') and article.abstract:
            paper['abstract'] = article.abstract

        # 发表日期
        if hasattr(article, 'publication_date') and article.publication_date:
            try:
                # pymed 返回的是 datetime 对象
                if isinstance(article.publication_date, datetime):
                    paper['publication_date'] = article.publication_date.strftime('%Y-%m-%d')
                else:
                    paper['publication_date'] = str(article.publication_date)
            except Exception:
                paper['publication_date'] = ''

        # DOI
        if hasattr(article, 'doi') and article.doi:
            paper['doi'] = article.doi
            paper['urls'].append(f"https://doi.org/{article.doi}")

        # 关键词
        if hasattr(article, 'keywords') and article.keywords:
            paper['keywords'] = article.keywords

        # 期刊信息
        if hasattr(article, 'journal') and article.journal:
            paper['publication']['title'] = article.journal

        if hasattr(article, 'volume') and article.volume:
            paper['publication']['volume'] = article.volume

        if hasattr(article, 'issue') and article.issue:
            paper['publication']['issue'] = article.issue

        # ISSN
        if hasattr(article, 'issn') and article.issn:
            paper['publication']['issn'] = article.issn

        # PubMed ID
        if hasattr(article, 'pubmed_id') and article.pubmed_id:
            paper['pmid'] = str(article.pubmed_id)
            paper['urls'].append(f"https://pubmed.ncbi.nlm.nih.gov/{article.pubmed_id}/")

        # 确保 URLs 去重
        paper['urls'] = list(dict.fromkeys(paper['urls']))

        return paper

    def _check_pmc_availability(self, pmid: str) -> bool:
        """
        检查文章在 PubMed Central (PMC) 中是否可用

        Args:
            pmid: PubMed ID

        Returns:
            True 如果有 PMC 全文可用
        """
        url = "https://www.ncbi.nlm.nih.gov/pmc/utils/id/convert/v3.0/"
        params = {
            'ids': pmid,
            'format': 'json'
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # 检查是否有 PMCID
            records = data.get('records', [])
            if records and 'pmcid' in records[0]:
                return True

        except Exception:
            # 静默失败 - 大多数论文没有 PMC 版本是正常的
            pass

        return False


def test_search():
    """测试 PubMed 搜索功能"""
    print("=" * 60)
    print("PubMed 搜索测试")
    print("=" * 60)

    searcher = PubMedSearcher(
        email="paper-search@example.com",
        api_key=None
    )

    # 测试 1: 基础搜索
    print("\n【测试 1】基础搜索")
    papers = searcher.search(
        query="machine learning healthcare",
        max_results=3
    )

    print(f"\n找到 {len(papers)} 篇论文:")
    for idx, paper in enumerate(papers, 1):
        print(f"\n{idx}. {paper.get('title', 'N/A')}")
        print(f"   作者: {', '.join(paper.get('authors', [])[:3])}")
        print(f"   PMID: {paper.get('pmid', 'N/A')}")
        print(f"   PMC 可用: {'是' if paper.get('has_pmc') else '否'}")

    # 测试 2: 免费全文筛选
    print("\n" + "=" * 60)
    print("【测试 2】免费全文筛选")
    papers = searcher.search(
        query="cancer",
        max_results=5,
        has_free_full_text=True
    )

    print(f"\n找到 {len(papers)} 篇有免费全文的论文:")
    for idx, paper in enumerate(papers, 1):
        print(f"\n{idx}. {paper.get('title', 'N/A')}")
        print(f"   PMC 可用: {'是' if paper.get('has_pmc') else '否'}")

    # 测试 3: 查询格式转换
    print("\n" + "=" * 60)
    print("【测试 3】查询格式转换")
    test_queries = [
        "[AI] AND [healthcare]",
        '["machine learning"] OR [deep learning]',
        "[biology] AND [cancer]"
    ]

    for query in test_queries:
        converted = searcher._convert_query_format(query)
        print(f"\n  原始: {query}")
        print(f"  转换: {converted}")

    print("\n" + "=" * 60)
    print("✓ 测试完成")
    print("=" * 60)


if __name__ == '__main__':
    test_search()
