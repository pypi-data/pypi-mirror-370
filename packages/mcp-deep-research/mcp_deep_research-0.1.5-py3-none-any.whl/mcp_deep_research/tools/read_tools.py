from .fetcher import url2md
from .md_handler import article_md_handler

async def read_paper(url: str, cdp_endpoint: str) -> str:
    """接收论文URL，返回格式化后的Markdown内容"""
    ori_paper = await url2md(url=url, re_md=True, cdp_endpoint=cdp_endpoint, timeout=10000)
    return article_md_handler(ori_paper)