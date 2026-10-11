"""Render the release guide using markdown-it-py (development only)."""
from pathlib import Path
from markdown_it import MarkdownIt
root=Path(__file__).resolve().parents[1]
page=root/'docs/index.html'
content=page.read_text(encoding='utf-8')
marker='<section id="replicate">'
link='<p><a href="quickstart.html">NEW: v0.1.0 configurable starter kit — follow the release quickstart</a></p>'
if link not in content:
    page.write_text(content.replace(marker, marker+link),encoding='utf-8')
body=MarkdownIt().render((root/'docs/QUICKSTART.md').read_text(encoding='utf-8'))
(root/'docs/quickstart.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v0.1.0 Starter Kit — Quickstart</title><link rel="stylesheet" href="site.css"><style>main{max-width:960px;padding-bottom:60px}h1{font-size:44px;letter-spacing:-1px}h2{font-size:30px;margin-top:48px}li{color:#afbed0}pre,pre code{white-space:pre-wrap}</style></head><body><header><a href="index.html">Architecture showcase</a><a href="https://github.com/Pratik2895/ai-data-agent/releases/tag/v0.1.0">Download v0.1.0</a></header><main>'+body+'</main></body></html>',encoding='utf-8')
