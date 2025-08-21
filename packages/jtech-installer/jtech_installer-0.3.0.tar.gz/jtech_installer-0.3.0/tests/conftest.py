"""
Arquivo de configuração para testes
"""

import sys
from pathlib import Path

# Adicionar src ao Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
