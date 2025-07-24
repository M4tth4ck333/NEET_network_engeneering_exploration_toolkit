import abc
import threading
import time
import json
from typing import Dict, Any, List, Optional

# --- Basisklasse für alle zentralen Systemkomponenten (ZNSBase / SystemSphereBase) ---
class SystemSphereBase(abc.ABC):
    """
    Abstrakte Basisklasse für zentrale Komponenten des NEET-OS,
    die sowohl operative (Durga) als auch darstellende (Tesseract) Aspekte vereinen.
    Sie repräsentiert die grundlegende Essenz einer "Sphäre" im System.
    """
    _component_name: str = "UnnamedComponent"
    _component_version: str = "0.0.1"
    _component_type: str = "Base"

    # Grundlegende Farb-Codes für konsistente Ausgabe
    _COLORS = {
        "HEADER": '\033[95m',
        "OKBLUE": '\033[94m',
        "OKCYAN": '\033[96m',
        "OKGREEN": '\033[92m',
        "WARNING": '\033[93m',
        "FAIL": '\033[91m',
        "ENDC": '\033[0m',
        "BOLD": '\033[1m',
        "UNDERLINE": '\033[4m'
    }

    def __init__(self):
        """
        Initialisiert die Basisklasse.
        """
        # print-Statement hier entfernt, da es in der Unterklasse CoreContextManager
        # bereits eine spezifische Initialisierungsmeldung gibt, die den Singleton-Kontext berücksichtigt.
        pass

    def _colored_print(self, message: str, color: str = "") -> None:
        """
        Gibt eine Nachricht mit optionaler Farbformatierung aus.
        """
        color_code = self._COLORS.get(color.upper(), "")
        print(f"{color_code}{message}{self._COLORS['ENDC']}")

    def get_component_metadata(self) -> Dict[str, Any]:
        """
        Gibt Metadaten über diese Systemkomponente zurück.
        """
        return {
            "name": self._component_name,
            "version": self._component_version,
            "type": self._component_type,
            "description": self.__doc__.strip() if self.__doc__ else "No description provided."
        }

    @abc.abstractmethod
    def initialize_component(self) -> bool:
        """
        Abstrakte Methode zur Initialisierung spezifischer Komponentenlogik.
        Muss von Unterklassen implementiert werden.
        """
        pass

    @abc.abstractmethod
    def shutdown_component(self) -> bool:
        """
        Abstrakte Methode zum Herunterfahren und Aufräumen der Komponente.
        Muss von Unterklassen implementiert werden.
        """
        pass

    def report_status(self, status_message: str, level: str = "INFO") -> None:
        """
        Meldet den Status der Komponente an das System (z.B. an einen zentralen Logger).
        In einer realen Implementierung würde dies an einen zentralen Logger gesendet,
        der auch von Azure Monitor erfasst werden könnte.
        """
        formatted_message = f"[{self._component_name}][{level.upper()}]: {status_message}"
        color = "OKBLUE"
        if level.upper() == "WARNING":
            color = "WARNING"
        elif level.upper() == "FAIL" or level.upper() == "ERROR":
            color = "FAIL"
        elif level.upper() == "SUCCESS":
            color = "OKGREEN"
        self._colored_print(formatted_message, color=color)
        # Hier könnte auch eine Log-Nachricht an eine interne Log-Liste oder Datenbank gesendet werden

# --- Definition der AbstractCard (jedes Datenobjekt in deinem Metaverse) ---
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

# --- Definition der AbstractPlugin (jede ausführbare Komponente) ---
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

# --- Das Herzstück: CoreContextManager als Singleton und Erbe von SystemSphereBase ---
class CoreContextManager(SystemSphereBase): # Erbt jetzt von SystemSphereBase
    _instance = None
    _lock = threading.Lock() # Für Thread-Sicherheit bei Singleton-Initialisierung

    _component_name = "CoreContextManager"
    _component_type = "ZNSCore"
    _component_version = "0.2.1" # Version aktualisiert

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
        # Rufe den Konstruktor der Basisklasse nur einmal auf, wenn die Instanz neu ist
        if not self._initialized:
            super().__init__() # Initialisiere die SystemSphereBase
            self.core_context: Dict[str, Any] = {} # Das zentrale Daten-Dictionary
            self.cards: Dict[str, AbstractCard] = {} # Alle AbstractCard-Instanzen nach ID
            self.plugins: Dict[str, AbstractPlugin] = {} # Alle AbstractPlugin-Instanzen nach Name
            self.active_frontend_type: Optional[str] = None # "pywebview" oder "tkinter"
            self.db_connection: Optional[Any] = None # Verbindung zu Durga 2 (SQLAlchemy ORM)
            self._initialized = True # Markiert die Initialisierung als abgeschlossen
            self.report_status(f"CoreContextManager (Jan) initialisiert als {self._component_type}.", "INFO")
            
            self._system_status = {"initialized": False, "running": False, "message": "System not initialized."}
            self._logs: List[Dict[str, Any]] = [] # Einfache In-Memory-Logs
            self._devices: List[Dict[str, Any]] = [] # Simulierte Geräte
            self._scan_results: List[Dict[str, Any]] = [] # Simulierte Scan-Ergebnisse
            self._initialize_dummy_data() # Dummy-Daten laden

    def _initialize_dummy_data(self):
        """Initialisiert simulierte Daten für Demonstrationszwecke."""
        self._logs.append({"timestamp": time.time(), "level": "INFO", "message": "NEET-OS Core gestartet."})
        self._devices.append({"id": "dev_001", "name": "Simulated Router", "ip": "192.168.1.1", "os": "OpenWrt"})
        self._devices.append({"id": "dev_002", "name": "Simulated Server", "ip": "192.168.1.10", "os": "Ubuntu"})
        self._scan_results.append({
            "id": "scan_001",
            "scan_type": "network",
            "target": "192.168.1.0/24",
            "status": "completed",
            "results": ["Host 192.168.1.1 up", "Port 80 open on 192.168.1.10"]
        })
        self.report_status("Simulierte Daten geladen.", "INFO")

    def initialize_component(self) -> bool:
        """
        Initialisiert die Kernmodule des Systems.
        Hier würde der "Nativitan Loader" Module dynamisch laden und mit dem ZNS verbinden.
        """
        self.report_status("Starte Systeminitialisierung der Komponenten...", "INFO")
        try:
            # Beispiel für das Laden von Modulen (hier simuliert)
            # In einer realen Implementierung würden hier die tatsächlichen Module geladen
            # und ihre initialize_component() Methoden aufgerufen.
            # Jedes Plugin würde dann mit self.add_plugin() hinzugefügt.
            self.add_plugin(self._DummyWebFetcher("DummyWebFetcher", "Simulierter Web Fetcher"))
            self.add_plugin(self._DummyDOMParser("DummyDOMParser", "Simulierter DOM Parser"))
            # ... weitere Module laden und hinzufügen ...

            # Verbinde zu Durga 2 (ORM-Anbindung)
            self.connect_to_durga2()

            self._system_status["initialized"] = True
            self._system_status["running"] = True
            self._system_status["message"] = "NEET-OS Core initialisiert und läuft."
            self.report_status("NEET-OS Core erfolgreich initialisiert.", "SUCCESS")
            return True
        except Exception as e:
            self._system_status["message"] = f"Initialisierungsfehler: {e}"
            self.report_status(f"Fehler bei der Systeminitialisierung: {e}", "FAIL")
            return False

    def shutdown_component(self) -> bool:
        """
        Fährt die Kernmodule des Systems herunter und schließt die Datenbankverbindung.
        """
        self.report_status("Starte System-Shutdown der Komponenten...", "INFO")
        # Hier würde die Logik zum Herunterfahren der geladenen Module stehen
        for name, plugin_instance in self.plugins.items():
            # Annahme: Plugins haben keine shutdown_component, aber könnten sie haben
            self.report_status(f"Plugin '{name}' heruntergefahren.", "INFO")
        
        self.close_db_connection() # Datenbankverbindung schließen

        self._system_status["running"] = False
        self._system_status["message"] = "NEET-OS Core heruntergefahren."
        self.report_status("NEET-OS Core erfolgreich heruntergefahren.", "SUCCESS")
        return True

    def add_card(self, card: AbstractCard):
        """Fügt eine AbstractCard zum globalen Kontext hinzu und speichert sie in Durga 2."""
        if card.card_id in self.cards:
            self.report_status(f"Warnung: Karte mit ID '{card.card_id}' existiert bereits. Wird überschrieben.", "WARNING")
        self.cards[card.card_id] = card
        # Hier würde die Logik zum Speichern der Karte in Durga 2 (ORM) hinkommen
        # z.B. self.db_connection.session.add(card.to_orm_model())
        self.report_status(f"Karte '{card.card_type}' mit ID '{card.card_id}' hinzugefügt.", "INFO")

    def get_card(self, card_id: str) -> Optional[AbstractCard]:
        """Ruft eine AbstractCard anhand ihrer ID ab (aus dem Kontext oder Durga 2)."""
        card = self.cards.get(card_id)
        if not card:
            # Hier würde die Logik zum Abrufen der Karte aus Durga 2 (ORM) hinkommen
            # z.B. card = self.db_connection.session.query(CardModel).filter_by(id=card_id).first()
            self.report_status(f"Karte mit ID '{card_id}' nicht im In-Memory-Kontext gefunden. (Würde aus DB geladen)", "INFO")
        return card

    def add_plugin(self, plugin: AbstractPlugin):
        """Fügt ein AbstractPlugin zum Manager hinzu und setzt seinen Kontext."""
        if plugin.plugin_name in self.plugins:
            self.report_status(f"Warnung: Plugin '{plugin.plugin_name}' existiert bereits. Wird überschrieben.", "WARNING")
        plugin.set_core_context(self) # Übergibt den CoreContextManager an das Plugin
        self.plugins[plugin.plugin_name] = plugin
        self.report_status(f"Plugin '{plugin.plugin_name}' hinzugefügt.", "INFO")

    def get_plugin(self, plugin_name: str) -> Optional[AbstractPlugin]:
        """Ruft ein AbstractPlugin anhand seines Namens ab."""
        return self.plugins.get(plugin_name)

    def set_active_frontend(self, frontend_type: str):
        """Setzt den Typ des aktuell aktiven Frontends."""
        if frontend_type not in ["pywebview", "tkinter", "flask_json_canvas"]: # "flask_json_canvas" hinzugefügt
            raise ValueError("Ungültiger Frontend-Typ. Erlaubt sind 'pywebview', 'tkinter' oder 'flask_json_canvas'.")
        self.active_frontend_type = frontend_type
        self.report_status(f"Aktives Frontend auf '{frontend_type}' gesetzt.", "INFO")

    def connect_to_durga2(self, db_path: str = "db/durga2.sqlite"):
        """
        Stellt eine Verbindung zu Durga 2 her (SQLAlchemy ORM-Anbindung).
        (Platzhalter-Implementierung, später durch deine echte SQLAlchemy-Logik ersetzen)
        """
        try:
            # Hier würde die SQLAlchemy-Engine und Session-Setup hinkommen
            # import sqlalchemy
            # from sqlalchemy.orm import sessionmaker
            # self.db_engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
            # self.Session = sessionmaker(bind=self.db_engine)
            # self.db_connection = self.Session() # Dies wäre die Session
            self.db_connection = f"Simulierte SQLAlchemy-Verbindung zu {db_path}" # Dummy-Verbindung
            self.report_status(f"Verbunden mit Durga 2 Datenbank (simuliert): {db_path}", "OKGREEN")
        except Exception as e:
            self.report_status(f"Fehler beim Verbinden mit Durga 2: {e}", "FAIL")

    def close_db_connection(self):
        """Schließt die Verbindung zu Durga 2."""
        if self.db_connection:
            # if hasattr(self.db_connection, 'close'): self.db_connection.close()
            self.db_connection = None
            self.report_status("Verbindung zu Durga 2 geschlossen (simuliert).", "INFO")

    def get_system_status(self) -> Dict[str, Any]:
        """Gibt den aktuellen Systemstatus zurück."""
        return self._system_status

    def get_system_logs(self) -> List[Dict[str, Any]]:
        """Gibt die gesammelten System-Logs zurück."""
        # In einer realen App würden Logs aus einer DB oder einem zentralen Log-System kommen
        return self._logs

    def get_devices(self) -> List[Dict[str, Any]]:
        """Gibt simulierte Netzwerkgeräte zurück."""
        return self._devices

    def get_scan_results(self) -> List[Dict[str, Any]]:
        """Gibt simulierte Scan-Ergebnisse zurück."""
        return self._scan_results

    def execute_system_command(self, command: str) -> Dict[str, Any]:
        """
        Verarbeitet einen Befehl, der vom Frontend oder anderen Quellen kommt.
        Dies ist die "Chainmodule"-Logik.
        """
        self.report_status(f"Empfange Befehl: '{command}'", "OKBLUE")
        self._logs.append({"timestamp": time.time(), "level": "COMMAND", "message": f"Executing: {command}"})

        if command.lower() == "list devices":
            return {"status": "success", "message": "Simulierte Geräte gelistet.", "data_type": "devices", "payload": self.get_devices()}
        elif command.lower() == "show logs":
            return {"status": "success", "message": "System-Logs angezeigt.", "data_type": "logs", "payload": self.get_system_logs()}
        elif command.lower().startswith("scan "):
            target = command.split(" ", 1)[1]
            # Simulierte Scan-Logik
            new_scan = {
                "id": f"scan_{int(time.time())}",
                "scan_type": "quick_scan",
                "target": target,
                "status": "completed",
                "results": [f"Simulierter Port 80 offen auf {target}", f"Simulierter Ping zu {target} erfolgreich"]
            }
            self._scan_results.append(new_scan)
            self._logs.append({"timestamp": time.time(), "level": "INFO", "message": f"Simulierter Scan auf {target} abgeschlossen."})
            return {"status": "success", "message": f"Scan auf {target} abgeschlossen.", "data_type": "scan_results", "payload": new_scan}
        elif command.lower() == "clear logs":
            self._logs = [{"timestamp": time.time(), "level": "INFO", "message": "Logs durch Benutzer gelöscht."}]
            return {"status": "success", "message": "Logs gelöscht.", "data_type": "logs", "payload": self.get_system_logs()}
        elif command.lower() == "help":
            help_message = [
                "Verfügbare Befehle:",
                "  list devices    - Zeigt simulierte Netzwerkgeräte.",
                "  show logs       - Zeigt System-Logs.",
                "  scan <Ziel>     - Startet einen simulierten Netzwerk-Scan (z.B. 'scan 192.168.1.1').",
                "  clear logs      - Löscht die System-Logs.",
                "  help            - Zeigt diese Hilfe an."
            ]
            self._logs.extend([{"timestamp": time.time(), "level": "INFO", "message": msg} for msg in help_message])
            return {"status": "success", "message": "Hilfe angezeigt.", "data_type": "logs", "payload": self.get_system_logs()}
        else:
            self._logs.append({"timestamp": time.time(), "level": "ERROR", "message": f"Unbekannter Befehl: '{command}'"})
            return {"status": "error", "message": f"Unbekannter Befehl: '{command}'.", "data_type": "error", "payload": {}}

    # --- Dummy-Module für die Simulation des dynamischen Ladens (als Plugins) ---
    # Diese würden später echte Implementierungen von AbstractPlugin sein
    class _DummyWebFetcher(AbstractPlugin):
        def __init__(self, name, description):
            super().__init__(name, description)
        def run(self, arguments: Dict[str, Any]) -> Any:
            self.core_context.report_status(f"[{self.plugin_name}] Führe run-Methode aus mit {arguments}", "OKCYAN")
            return {"status": "success", "message": f"{self.plugin_name} processed request."}
    
    class _DummyDOMParser(AbstractPlugin):
        def __init__(self, name, description):
            super().__init__(name, description)
        def run(self, arguments: Dict[str, Any]) -> Any:
            self.core_context.report_status(f"[{self.plugin_name}] Führe run-Methode aus mit {arguments}", "OKCYAN")
            return {"status": "success", "message": f"{self.plugin_name} processed request."}

