from dataclasses import dataclass, field
from typing import List
DEFAULT_INCLUDE = ["*.py","*.js","*.ts","*.jsx","*.tsx","*.json","*.yml","*.yaml","*.md","*.mdx","*.html","*.css",".env","*.toml","*.ini","*.tf"]
DEFAULT_EXCLUDE = ["node_modules/**","dist/**","build/**",".git/**",".venv/**","__pycache__/**"]
@dataclass
class Config:
    path: str
    mode: str = "scan"
    dry_run: bool = False
    include: List[str] = field(default_factory=lambda: DEFAULT_INCLUDE.copy())
    exclude: List[str] = field(default_factory=lambda: DEFAULT_EXCLUDE.copy())
    backup: bool = False
    llm_provider: str = "none"
    model: str = "gpt-4o-mini"
    max_chars: int = 400_000
