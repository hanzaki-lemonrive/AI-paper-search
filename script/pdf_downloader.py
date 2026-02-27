#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF 下载管理器
多策略下载：PMC → Unpaywall → 直接链接 → 机构认证
"""

import time
import requests
from pathlib import Path
from typing import Optional, Dict
from urllib.parse import urlparse


class PDFDownloadManager:
    """多策略 PDF 下载管理器"""

    def __init__(
        self,
        output_dir: Path,
        user_agent: str = "Paper-Search-Assistant/1.0",
        timeout: int = 30,
        email: Optional[str] = None
    ):
        """
        初始化下载管理器

        Args:
            output_dir: PDF 保存目录
            user_agent: HTTP User-Agent 头
            timeout: 请求超时时间（秒）
            email: Email address for Unpaywall API (required)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = user_agent
        self.timeout = timeout
        self.email = email or "paper-search@example.com"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

    def download_paper_pdf(
        self,
        paper: Dict,
        pmid: Optional[str] = None,
        doi: Optional[str] = None,
        institution_credentials: Optional[Dict] = None
    ) -> Dict:
        """
        使用多策略下载 PDF

        策略顺序（优化后）：
        1. Unpaywall API（最可能找到免费版本）
        2. PubMed Central (PMC)
        3. 直接 PDF 链接
        4. 机构认证（如果提供）

        Args:
            paper: 论文元数据字典
            pmid: PubMed ID
            doi: DOI
            institution_credentials: 机构认证凭据（可选）

        Returns:
            下载结果字典
        """
        result = {
            'success': False,
            'source': None,
            'path': None,
            'error': None
        }

        # 策略 1: Unpaywall API（优先 - 比 PMC 覆盖更广）
        if doi:
            result = self._download_from_unpaywall(doi, paper)
            if result['success']:
                return result

        # 策略 2: PubMed Central (PMC)
        if pmid:
            result = self._download_from_pmc(pmid, paper)
            if result['success']:
                return result

        # 策略 3: 直接 PDF 链接
        result = self._download_direct_pdf(paper)
        if result['success']:
            return result

        # 策略 4: 机构认证（如果提供凭据）
        if institution_credentials:
            result = self._download_with_auth(paper, institution_credentials)
            if result['success']:
                return result

        # 所有策略都失败
        result['error'] = "无开放获取 PDF 可用（可能需要订阅）"
        return result

    def _download_from_pmc(self, pmid: str, paper: Dict) -> Dict:
        """从 PubMed Central 下载 PDF"""
        # 获取 PMCID
        pmcid = self._get_pmcid(pmid)
        if not pmcid:
            # 论文不在 PMC 中 - 这是正常的，不显示错误
            return {
                'success': False,
                'source': 'PMC',
                'error': 'Not in PMC'
            }

        # PMC PDF URL
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"

        try:
            filename = self._generate_filename(paper, 'pmc', pmid)
            filepath = self.output_dir / filename

            response = self.session.get(pdf_url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            # 检查是否是 PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                return {
                    'success': False,
                    'source': 'PMC',
                    'error': 'Non-PDF content'
                }

            # 保存 PDF
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"  ✓ PMC 下载成功: {filename}")
            return {
                'success': True,
                'source': 'PMC',
                'path': str(filepath)
            }

        except Exception:
            # 静默失败
            return {
                'success': False,
                'source': 'PMC',
                'error': 'Download failed'
            }

    def _get_pmcid(self, pmid: str) -> Optional[str]:
        """将 PMID 转换为 PMCID"""
        url = "https://www.ncbi.nlm.nih.gov/pmc/utils/id/convert/v3.0/"
        params = {
            'ids': pmid,
            'format': 'json'
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            records = data.get('records', [])
            if records:
                return records[0].get('pmcid')

        except Exception:
            # 静默失败 - 大多数论文不在 PMC 中
            pass

        return None

    def _download_from_unpaywall(self, doi: str, paper: Dict) -> Dict:
        """
        使用 Unpaywall API 下载 PDF

        Unpaywall 是合法的开放获取定位器
        """
        url = f"https://api.unpaywall.org/v2/{doi}"
        params = {
            'email': self.email  # Unpaywall 要求真实邮箱
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 检查是否有开放获取 PDF
            if data.get('is_oa') and data.get('best_oa_location'):
                oa_location = data['best_oa_location']
                pdf_url = oa_location.get('url_for_pdf')

                if pdf_url:
                    filename = self._generate_filename(paper, 'unpaywall', doi)
                    filepath = self.output_dir / filename

                    # 下载 PDF
                    pdf_response = self.session.get(
                        pdf_url,
                        stream=True,
                        timeout=self.timeout
                    )
                    pdf_response.raise_for_status()

                    # 检查内容类型
                    content_type = pdf_response.headers.get('Content-Type', '')
                    if 'pdf' not in content_type.lower():
                        return {
                            'success': False,
                            'source': 'Unpaywall',
                            'error': 'Non-PDF content'
                        }

                    # 保存
                    with open(filepath, 'wb') as f:
                        for chunk in pdf_response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"  ✓ Unpaywall 下载成功: {filename}")
                    return {
                        'success': True,
                        'source': 'Unpaywall',
                        'path': str(filepath)
                    }

            # 无开放获取版本 - 静默返回失败
            return {
                'success': False,
                'source': 'Unpaywall',
                'error': 'No OA version'
            }

        except Exception:
            # 静默失败
            return {
                'success': False,
                'source': 'Unpaywall',
                'error': 'API error'
            }

    def _download_direct_pdf(self, paper: Dict) -> Dict:
        """尝试从直接的 .pdf URL 下载"""
        for url in paper.get('urls', []):
            if '.pdf' in url.lower():
                try:
                    filename = self._generate_filename(paper, 'direct', '')
                    filepath = self.output_dir / filename

                    response = self.session.get(url, stream=True, timeout=self.timeout)

                    content_type = response.headers.get('Content-Type', '')
                    if 'pdf' in content_type.lower() or url.endswith('.pdf'):
                        response.raise_for_status()

                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        print(f"  ✓ 直接链接下载成功: {filename}")
                        return {
                            'success': True,
                            'source': 'Direct',
                            'path': str(filepath)
                        }
                except Exception:
                    continue

        return {
            'success': False,
            'source': 'Direct',
            'error': '无直接 PDF 链接'
        }

    def _download_with_auth(
        self,
        paper: Dict,
        credentials: Dict
    ) -> Dict:
        """
        使用机构认证下载

        这需要根据具体机构的认证系统定制
        """
        # 占位符实现 - 需要根据机构具体配置
        if 'ezproxy_url' in credentials:
            try:
                url = None
                for u in paper.get('urls', []):
                    if 'doi.org' in u or 'pubmed' in u:
                        url = u
                        break

                if not url:
                    return {
                        'success': False,
                        'source': 'Institution',
                        'error': '无合适的 URL'
                    }

                # 使用 EZProxy
                proxy_url = f"{credentials['ezproxy_url']}/{url}"

                response = self.session.get(
                    proxy_url,
                    auth=(
                        credentials.get('username', ''),
                        credentials.get('password', '')
                    ),
                    stream=True,
                    timeout=self.timeout
                )

                if 'application/pdf' in response.headers.get('Content-Type', ''):
                    filename = self._generate_filename(paper, 'institution', '')
                    filepath = self.output_dir / filename

                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"  ✓ 机构下载成功: {filename}")
                    return {
                        'success': True,
                        'source': 'Institution',
                        'path': str(filepath)
                    }

            except Exception as e:
                return {
                    'success': False,
                    'source': 'Institution',
                    'error': str(e)
                }

        return {
            'success': False,
            'source': 'Institution',
            'error': '未配置机构凭据'
        }

    def _generate_filename(self, paper: Dict, source: str, id_str: str) -> str:
        """生成安全的文件名"""
        doi = paper.get('doi', '')
        pmid = paper.get('pmid', '')
        title = paper.get('title', 'unknown')

        if doi:
            # 使用 DOI
            safe_doi = doi.replace('/', '_').replace('.', '_')
            return f"{safe_doi}.pdf"
        elif pmid:
            return f"PMID_{pmid}.pdf"
        elif id_str:
            return f"{source}_{id_str}.pdf"
        else:
            # 使用标题
            safe_title = "".join(
                c for c in title[:50]
                if c.isalnum() or c in (' ', '-', '_')
            ).strip()
            return f"{safe_title}.pdf"


def test_downloader():
    """测试 PDF 下载器"""
    print("=" * 60)
    print("PDF 下载器测试")
    print("=" * 60)

    from pathlib import Path
    import tempfile

    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as tmpdir:
        downloader = PDFDownloadManager(output_dir=Path(tmpdir))

        # 测试论文（已知有 PMC 的文章）
        test_paper = {
            'title': 'Test Paper',
            'doi': '10.1001/jama.2019.12345',  # 示例 DOI
            'pmid': '31234567',  # 示例 PMID
            'urls': ['https://pubmed.ncbi.nlm.nih.gov/31234567/']
        }

        print("\n【测试】PMC 下载（使用示例 PMID）")
        print(f"  输出目录: {tmpdir}")

        result = downloader.download_paper_pdf(
            paper=test_paper,
            pmid=test_paper['pmid']
        )

        print(f"\n结果:")
        print(f"  成功: {result['success']}")
        print(f"  来源: {result['source']}")
        print(f"  路径: {result.get('path', 'N/A')}")
        if result.get('error'):
            print(f"  错误: {result['error']}")

    print("\n" + "=" * 60)
    print("✓ 测试完成")
    print("=" * 60)


if __name__ == '__main__':
    test_downloader()
