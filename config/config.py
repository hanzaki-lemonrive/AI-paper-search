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
                print(f"✓ 已加载配置文件: {env_path}")
            except ImportError:
                print(f"⚠ 警告：python-dotenv 未安装，无法加载 .env 文件")
                print(f"  安装: pip install python-dotenv")
            except Exception as e:
                print(f"⚠ 警告：加载 .env 文件失败: {e}")

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
            print(f"  ✓ API Key: 已配置 (长度: {len(self.openai_api_key)})")
            print(f"  ✓ API Base: {api_base}")
        else:
            print(f"  ✗ API Key: 未配置")

        if self.ollama_base_url:
            print(f"  ✓ Ollama: {self.ollama_base_url}")

        # findpapers 配置
        print("\n【findpapers 扩展数据库】")
        if self.ieee_api_token:
            print(f"  ✓ IEEE API: 已配置")
        else:
            print(f"  ✗ IEEE API: 未配置（仅使用免费数据库）")

        if self.scopus_api_token:
            print(f"  ✓ Scopus API: 已配置")
        else:
            print(f"  ✗ Scopus API: 未配置（仅使用免费数据库）")

        # 代理设置
        if self.findpapers_proxy:
            print(f"\n【代理设置】")
            print(f"  ✓ 代理: {self.findpapers_proxy}")

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
    print("✓ 配置测试完成")
    print("="*60)
