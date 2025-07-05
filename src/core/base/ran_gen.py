import hashlib
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

# Typ-Variable für die Art des generierten Objekts
T = TypeVar('T')

class RandomGenerator(ABC, Generic[T]):
    """
    Basisklasse für einen Zufallsgenerator mit Seed-Steuerung, Hashing und Perspektivierung.
    Ermöglicht das Generieren von Objekten vom Typ T.
    """
    def __init__(self, seed: Optional[int] = None):
        """
        Initialisiert den Generator mit einem optionalen Seed.
        Ein fixer Seed gewährleistet reproduzierbare Ergebnisse.
        """
        self._seed = seed if seed is not None else self._generate_new_seed()
        self._rng = random.Random(self._seed) # Interner RNG-Instanz
        print(f"RandomGenerator initialized with seed: {self._seed}")

    @property
    def current_seed(self) -> int:
        """Gibt den aktuellen Seed des Generators zurück."""
        return self._seed

    def _generate_new_seed(self) -> int:
        """Generiert einen neuen, zufälligen Seed."""
        return random.randint(0, 2**32 - 1) # Standard-Range für Seeds

    @abstractmethod
    def generate(self, context: Optional[Dict[str, Any]] = None) -> T:
        """
        Abstrakte Methode zur Generierung eines Objekts vom Typ T.
        Muss von Unterklassen implementiert werden.
        Der 'context' ermöglicht die 'Perspektivierung'.
        """
        pass

    def get_hash(self, data: Any) -> str:
        """
        Generiert einen SHA256-Hash der gegebenen Daten.
        Nützlich für die Integrität oder Einzigartigkeit von generierten Objekten.
        """
        if isinstance(data, dict):
            # Für Dictionaries: Sortiere Keys für konsistenten Hash
            data_str = str(sorted(data.items()))
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def set_seed(self, seed: int):
        """Setzt den Seed des Generators neu, um die Abfolge zu ändern."""
        self._seed = seed
        self._rng = random.Random(self._seed)
        print(f"RandomGenerator seed set to: {self._seed}")

    def get_random_element(self, collection: List[Any]) -> Any:
        """
        Wählt ein zufälliges Element aus einer Liste basierend auf dem internen RNG.
        """
        if not collection:
            return None
        return self._rng.choice(collection)

    def get_random_int(self, a: int, b: int) -> int:
        """
        Generiert eine zufällige Ganzzahl im Bereich [a, b] basierend auf dem internen RNG.
        """
        return self._rng.randint(a, b)

    def _apply_perspective(self, generated_object: T, context: Dict[str, Any]) -> T:
        """
        Interne Hilfsmethode zur Anwendung der "Perspektivierung" auf ein generiertes Objekt.
        Diese Methode könnte von der Jans-Engine dynamisch erweitert werden.
        """
        # Dies ist ein Platzhalter. Die eigentliche Logik für die Perspektivierung
        # hängt stark vom generierten Objekt und dem Kontext ab.
        # Beispiel: Wenn 'generated_object' eine Karte ist und 'context' eine Player-Rolle enthält,
        # könnte sich die Darstellung oder bestimmte Werte ändern.
        print(f"Applying perspective for context: {context} on object: {generated_object}")
        # Hier könnte die Jans-Engine Methoden injizieren, um das Objekt anzupassen.
        return generated_object
