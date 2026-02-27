#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理模块

安全地加载环境变量和配置信息，不硬编码敏感信息
"""

import os
from pathlib import Path
from typing import Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    """配置类"""

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置

        参数:
            env_file: .env 文件路径（相对于项目根目录）
        """
        # 尝试加载 .env 文件
        if env_file:
            env_path = PROJECT_ROOT / env_file
        else:
            # 默认查找 .env 文件
            env_path = PROJECT_ROOT / "config" / ".env"

        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                print(f"[OK] Loaded config file: {env_path}")
            except ImportError:
                print(f"[INFO] Warning: python-dotenv not installed, cannot load .env file")
                print(f"  安装: pip install python-dotenv")
            except Exception as e:
                print(f"[INFO] Warning: Failed to load .env file: {e}")

    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API Key（兼容多个提供商）"""
        return os.getenv('OPENAI_API_KEY')

    @property
    def openai_api_base(self) -> Optional[str]:
        """OpenAI API Base URL"""
        return os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')

    @property
    def openai_api_version(self) -> Optional[str]:
        """Azure OpenAI API 版本"""
        return os.getenv('OPENAI_API_VERSION')

    @property
    def ollama_base_url(self) -> Optional[str]:
        """Ollama 服务地址"""
        return os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

    @property
    def ieee_api_token(self) -> Optional[str]:
        """IEEE API Token"""
        return os.getenv('FINDPAPERS_IEEE_API_TOKEN')

    @property
    def scopus_api_token(self) -> Optional[str]:
        """Scopus API Token"""
        return os.getenv('FINDPAPERS_SCOPUS_API_TOKEN')

    @property
    def findpapers_proxy(self) -> Optional[str]:
        """findpapers 代理设置"""
        return os.getenv('FINDPAPERS_PROXY')

    # ========== PubMed / NCBI 配置 ==========
    @property
    def ncbi_api_key(self) -> Optional[str]:
        """NCBI API Key（可选，提高速率限制从 3 到 10 请求/秒）"""
        return os.getenv('NCBI_API_KEY')

    @property
    def ncbi_email(self) -> Optional[str]:
        """NCBI 要求的邮箱地址"""
        return os.getenv('NCBI_EMAIL', 'paper-search@example.com')

    # ========== 影响因子筛选配置 ==========
    @property
    def min_sjr_score(self) -> float:
        """最小 Scimago Journal Rank 分数（0 = 不筛选）"""
        return float(os.getenv('MIN_SJR_SCORE', '0'))

    @property
    def sjr_db_path(self) -> str:
        """SJR 数据库路径"""
        default_path = PROJECT_ROOT / "cache" / "sjr_metrics.db"
        return os.getenv('SJR_DB_PATH', str(default_path))

    # ========== PDF 下载选项 ==========
    @property
    def enable_unpaywall(self) -> bool:
        """启用 Unpaywall API（合法的开放获取定位器）"""
        return os.getenv('ENABLE_UNPAYWALL', 'true').lower() == 'true'

    @property
    def institutional_proxy(self) -> Optional[str]:
        """机构 EZProxy URL（用于认证访问）"""
        return os.getenv('INSTITUTIONAL_PROXY')

    @property
    def institution_username(self) -> Optional[str]:
        """机构访问用户名"""
        return os.getenv('INSTITUTION_USERNAME')

    @property
    def institution_password(self) -> Optional[str]:
        """机构访问密码"""
        return os.getenv('INSTITUTION_PASSWORD')

    def get_llm_config(self, provider: str = 'auto') -> dict:
        """
        获取 LLM 配置（用于 PaperQA）

        参数:
            provider: 提供商 ('auto', 'openai', 'zhipu', 'ollama')

        返回:
            配置字典
        """
        config = {}

        if provider == 'auto':
            # 自动检测可用的 LLM
            if self.openai_api_key:
                provider = 'openai'
            elif self.openai_api_base and 'bigmodel' in self.openai_api_base:
                provider = 'zhipu'
            else:
                provider = 'ollama'

        if provider == 'openai':
            config = {
                'llm': 'gpt-3.5-turbo',  # 或 gpt-4
                'api_key': self.openai_api_key,
            }
            if self.openai_api_base:
                config['api_base'] = self.openai_api_base

        elif provider == 'zhipu':
            config = {
                'llm': 'glm-4',
                'api_key': self.openai_api_key,
                'api_base': self.openai_api_base or 'https://open.bigmodel.cn/api/paas/v4/',
            }

        elif provider == 'ollama':
            config = {
                'llm': 'qwen2.5',  # 或其他模型
                'api_base': self.ollama_base_url,
            }

        return config

    def is_paperqa_available(self) -> bool:
        """检查 PaperQA 是否可用"""
        return bool(self.openai_api_key or self.ollama_base_url)

    def print_status(self):
        """打印配置状态"""
        print("\n" + "="*60)
        print("配置状态")
        print("="*60)

        # LLM 配置
        print("\n【LLM 配置】")
        if self.openai_api_key:
            api_base = self.openai_api_base or 'OpenAI'
            print(f"  [OK] API Key: Configured (length: {len(self.openai_api_key)})")
            print(f"  [OK] API Base: {api_base}")
        else:
            print(f"  [X] API Key: Not configured")

        if self.ollama_base_url:
            print(f"  [OK] Ollama: {self.ollama_base_url}")

        # findpapers 配置
        print("\n[findpapers Extended Databases]")
        if self.ieee_api_token:
            print(f"  [OK] IEEE API: Configured")
        else:
            print(f"  [X] IEEE API: Not configured (using free databases only)")

        if self.scopus_api_token:
            print(f"  [OK] Scopus API: Configured")
        else:
            print(f"  [X] Scopus API: Not configured (using free databases only)")

        # 代理设置
        if self.findpapers_proxy:
            print(f"\n[Proxy Settings]")
            print(f"  [OK] Proxy: {self.findpapers_proxy}")

        # PubMed 配置
        print("\n[PubMed / NCBI Configuration]")
        if self.ncbi_email:
            print(f"  [OK] NCBI Email: {self.ncbi_email}")
        if self.ncbi_api_key:
            print(f"  [OK] NCBI API Key: Configured")
        else:
            print(f"  [INFO] NCBI API Key: Not configured (using default rate limit)")

        # 影响因子配置
        print("\n[Impact Factor Filtering]")
        if self.min_sjr_score > 0:
            print(f"  [OK] Minimum SJR Score: {self.min_sjr_score}")
        else:
            print(f"  [X] SJR Filtering: Disabled")

        # PDF 下载配置
        print("\n[PDF Download Options]")
        if self.enable_unpaywall:
            print(f"  [OK] Unpaywall API: Enabled")
        if self.institutional_proxy:
            print(f"  [OK] Institutional Access: Configured")

        print("\n" + "="*60)


# 全局配置实例
_config = None


def get_config(env_file: Optional[str] = None) -> Config:
    """
    获取配置实例（单例模式）

    参数:
        env_file: .env 文件路径

    返回:
        Config 实例
    """
    global _config
    if _config is None:
        _config = Config(env_file)
    return _config


if __name__ == '__main__':
    """测试配置加载"""
    import sys

    # 测试默认配置
    config = get_config()
    config.print_status()

    # 测试 LLM 配置
    print("\n【LLM 配置测试】")
    for provider in ['auto', 'openai', 'zhipu', 'ollama']:
        llm_config = config.get_llm_config(provider)
        print(f"\n{provider}:")
        for key, value in llm_config.items():
            if key == 'api_key' and value:
                value = f"{value[:8]}...{value[-4:]}"
            print(f"  {key}: {value}")

    print("\n" + "="*60)
    print("[OK] Configuration test complete")
    print("="*60)
