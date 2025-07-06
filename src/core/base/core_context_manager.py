# basi/core_context_manager.py

import abc
import threading
from typing import Dict, Any, Optional

# Definition der AbstractCard (jedes Datenobjekt in deinem Metaverse)
class AbstractCard(abc.ABC):
    """
    Basisklasse für alle Datenobjekte im NEET_network_engeneering_exploration_toolkit.
    "Alles ist ein Objekt für sich."
    """
    def __init__(self, card_id: str, card_type: str, data: Dict[str, Any]):
        self.card_id = card_id  # Eindeutige ID der Karte
        self.card_type = card_type # Typ der Karte (z.B. "Host", "Port", "DNS_Record", "Website")
        self.data = data # Die eigentlichen Daten der Karte
        self._graph_data_ready = False # Initialer Zustand für den Graphen-Getter

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Gibt die Daten der Karte als Dictionary zurück.
        Implementiere dies in Unterklassen.
        """
        pass

    @abc.abstractmethod
    def update(self, new_data: Dict[str, Any]):
        """
        Aktualisiert die Daten der Karte.
        Implementiere dies in Unterklassen, um Zustandsänderungen zu verwalten.
        """
        pass

    def _prepare_graph_data(self) -> Optional[Dict[str, Any]]:
        """
        Interne Methode, um Graphen-Daten für den impliziten Getter vorzubereiten.
        Wird von Unterklassen überschrieben, um spezifische Graphen-Daten zu liefern.
        """
        return None # Standardmäßig keine Graphen-Daten

    def get_graph_data(self) -> Optional[Dict[str, Any]]:
        """
        Der "implizite Getter", der Graphen-Daten zur Verfügung stellt.
        "Die Klassen selbst werden es uns schicken buhahahaha."
        Wird von der Jans-Engine oder Graphen-Modulen abgefragt.
        """
        if self._graph_data_ready:
            return self._prepare_graph_data()
        return None

    def mark_graph_data_ready(self):
        """Setzt ein Flag, das anzeigt, dass Graphen-Daten für diese Karte bereit sind."""
        self._graph_data_ready = True

# Definition der AbstractPlugin (jede ausführbare Komponente)
class AbstractPlugin(abc.ABC):
    """
    Basisklasse für alle ausführbaren Plugins im NEET_network_engeneering_exploration_toolkit.
    """
    def __init__(self, plugin_name: str, description: str):
        self.plugin_name = plugin_name
        self.description = description
        self.core_context = None # Wird vom CoreContextManager gesetzt

    def set_core_context(self, core_context: 'CoreContextManager'):
        """Setzt den CoreContextManager für das Plugin."""
        self.core_context = core_context

    @abc.abstractmethod
    def run(self, arguments: Dict[str, Any]) -> Any:
        """
        Führt die Logik des Plugins aus.
        Implementiere dies in Unterklassen.
        """
        pass

# Das Herzstück: CoreContextManager als Singleton
class CoreContextManager:
    _instance = None
    _lock = threading.Lock() # Für Thread-Sicherheit bei Singleton-Initialisierung

    def __new__(cls):
        """
        Implementiert das Singleton-Muster.
        Stellt sicher, dass nur eine Instanz des CoreContextManager existiert.
        """
        if cls._instance is None:
            with cls._lock:
                # Doppelte Prüfung, falls mehrere Threads gleichzeitig hierher kommen
                if cls._instance is None:
                    cls._instance = super(CoreContextManager, cls).__new__(cls)
                    cls._instance._initialized = False # Initialisierungs-Flag
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.core_context: Dict[str, Any] = {} # Das zentrale Daten-Dictionary
            self.cards: Dict[str, AbstractCard] = {} # Alle AbstractCard-Instanzen nach ID
            self.plugins: Dict[str, AbstractPlugin] = {} # Alle AbstractPlugin-Instanzen nach Name
            self.active_frontend_type: Optional[str] = None # "pywebview" oder "tkinter"
            self.db_connection: Optional[Any] = None # Verbindung zu Durga 2
            self._initialized = True # Markiert die Initialisierung als abgeschlossen
            print("CoreContextManager initialisiert.")

    def add_card(self, card: AbstractCard):
        """Fügt eine AbstractCard zum globalen Kontext hinzu."""
        if card.card_id in self.cards:
            print(f"Warnung: Karte mit ID '{card.card_id}' existiert bereits. Wird überschrieben.")
        self.cards[card.card_id] = card
        # Hier könntest du auch die Karte direkt in Durga 2 speichern
        print(f"Karte '{card.card_type}' mit ID '{card.card_id}' hinzugefügt.")

    def get_card(self, card_id: str) -> Optional[AbstractCard]:
        """Ruft eine AbstractCard anhand ihrer ID ab."""
        return self.cards.get(card_id)

    def add_plugin(self, plugin: AbstractPlugin):
        """Fügt ein AbstractPlugin zum Manager hinzu."""
        if plugin.plugin_name in self.plugins:
            print(f"Warnung: Plugin '{plugin.plugin_name}' existiert bereits. Wird überschrieben.")
        plugin.set_core_context(self) # Übergibt den CoreContextManager an das Plugin
        self.plugins[plugin.plugin_name] = plugin
        print(f"Plugin '{plugin.plugin_name}' hinzugefügt.")

    def get_plugin(self, plugin_name: str) -> Optional[AbstractPlugin]:
        """Ruft ein AbstractPlugin anhand seines Namens ab."""
        return self.plugins.get(plugin_name)

    def set_active_frontend(self, frontend_type: str):
        """Setzt den Typ des aktuell aktiven Frontends."""
        if frontend_type not in ["pywebview", "tkinter"]:
            raise ValueError("Ungültiger Frontend-Typ. Erlaubt sind 'pywebview' oder 'tkinter'.")
        self.active_frontend_type = frontend_type
        print(f"Aktives Frontend auf '{frontend_type}' gesetzt.")

    def connect_to_durga2(self, db_path: str = "db/durga2.sqlite"):
        """
        Stellt eine Verbindung zu Durga 2 her.
        (Platzhalter-Implementierung, später durch deine echte Durga 2 Logik ersetzen)
        """
        # Hier würde die spezifische Verbindungslogik für Durga 2 hinkommen.
        # Für den Anfang könnte es eine SQLite-Verbindung sein.
        try:
            import sqlite3
            self.db_connection = sqlite3.connect(db_path)
            print(f"Verbunden mit Durga 2 Datenbank unter: {db_path}")
        except ImportError:
            print("sqlite3 nicht gefunden. Kann keine Verbindung zu Durga 2 herstellen.")
        except Exception as e:
            print(f"Fehler beim Verbinden mit Durga 2: {e}")

    def close_db_connection(self):
        """Schließt die Verbindung zu Durga 2."""
        if self.db_connection:
            self.db_connection.close()
            print("Verbindung zu Durga 2 geschlossen.")

    # Hier können später weitere Kernfunktionen hinzugefügt werden,
    # z.B. für Event-Handling, Logging, Konfigurationsmanagement.

# Hilfsfunktion, um die CoreContextManager-Instanz zu erhalten
def get_core_context() -> CoreContextManager:
    """Gibt die Singleton-Instanz des CoreContextManager zurück."""
    return CoreContextManager()
