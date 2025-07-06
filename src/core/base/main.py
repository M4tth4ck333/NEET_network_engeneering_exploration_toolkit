# datei: src/core/base/main.py
import sys
import os

# Füge das Projekt-Stammverzeichnis zum Python-Pfad hinzu
# Gehe zwei Ebenen hoch (von main.py -> python_core -> src -> n33t_recon_ng)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, 'external_bases', 'recon-ng')) # Pfad zu recon-ng's Wurzel


# Beispiel-Imports, sobald der PYTHONPATH gesetzt ist:

# 1. Importiere deinen CoreContextManager:
from python_core.core_context_manager import CoreContextManager

# 2. Importiere etwas aus weirdolib-ng:
from core.weirdolib_ng.my_weirdo_function import some_weirdo_method

# 3. Importiere etwas aus Project Chronos (nach pybind11-Kompilierung):
# Annahme: Deine pybind11-Kompilierung legt die .so-Datei direkt in core/chronos_core ab
try:
    from core.chronos_core import chronos_core_module # Der Name, den du in pybind11 gibst
    result_chronos = chronos_core_module.add(5, 7)
    print(f"Chronos result: {result_chronos}")
except ImportError as e:
    print(f"Fehler beim Laden von Project Chronos: {e}. Stelle sicher, dass es kompiliert wurde!")

# 4. Importiere etwas aus AlienPimp:
from core.alienpimp.cloner import PokeballWebsiteCloner

# 5. Importiere etwas aus recon-ng (da recon-ng/ ist jetzt im PYTHONPATH)
try:
    from recon.core.framework import ReconDotNG
    # Beispiel: framework = ReconDotNG()
    print("recon-ng erfolgreich importiert.")
except ImportError as e:
    print(f"Fehler beim Laden von recon-ng: {e}. Stelle sicher, dass der Pfad korrekt ist.")

# Initialisiere deinen CoreContextManager
context_manager = CoreContextManager()
# ... weitere Initialisierung
