"""
Permite que os testes importem os modulos do projeto sem instalar nada.
Adiciona o diretorio raiz do projeto ao sys.path.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
