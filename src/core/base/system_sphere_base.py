# src/core/base/system_sphere_base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SystemSphereBase(ABC):
    """
    Abstrakte Basisklasse für zentrale Komponenten des NEET-OS,
    die sowohl operative (Durga) als auch darstellende (Tesseract) Aspekte vereinen.
    Sie repräsentiert die grundlegende Essenz einer "Sphäre" im System.
    """
    _component_name: str = "UnnamedComponent"
    _component_version: str = "0.0.1"
    _component_type: str = "Base"

    # Grundlegende Farb-Codes für konsistente Ausgabe (könnten auch in einem Config-Modul liegen)
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

    def __init__(self, context_manager: Optional[Any] = None):
        """
        Initialisiert die Basisklasse mit einem optionalen Kontext-Manager.
        Der Kontext-Manager könnte z.B. für globale Logs oder Konfigurationen zuständig sein.
        """
        self.context_manager = context_manager
        self._colored_print(f"[{self._component_name}] Initialisiert als {self._component_type} Komponente.", color="HEADER")

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

    @abstractmethod
    def initialize_component(self) -> bool:
        """
        Abstrakte Methode zur Initialisierung spezifischer Komponentenlogik.
        Muss von Unterklassen implementiert werden.
        """
        pass

    @abstractmethod
    def shutdown_component(self) -> bool:
        """
        Abstrakte Methode zum Herunterfahren und Aufräumen der Komponente.
        Muss von Unterklassen implementiert werden.
        """
        pass

    # Beispiel für eine gemeinsame Methode, die von beiden Seiten genutzt werden könnte
    def report_status(self, status_message: str, level: str = "INFO") -> None:
        """
        Meldet den Status der Komponente an das System (z.B. an einen zentralen Logger).
        """
        formatted_message = f"[{self._component_name}][{level.upper()}]: {status_message}"
        self._colored_print(formatted_message, color="OKBLUE" if level.upper() == "INFO" else "WARNING" if level.upper() == "WARNING" else "FAIL")
        if self.context_manager and hasattr(self.context_manager, 'log_system_event'):
            self.context_manager.log_system_event(self._component_name, status_message, level)

# Beispiel für die zukünftige Struktur der DurgaEngine und des Tesseract-Frontends
# (Diese Klassen würden in ihren jeweiligen Modulen definiert)

# class DurgaEngine(SystemSphereBase):
#     _component_name = "DurgaEngine"
#     _component_type = "CoreOrchestrator"
#     _component_version = "1.0.0"

#     def initialize_component(self) -> bool:
#         self._colored_print(f"[{self._component_name}] Initialisiere operative Module...", color="OKGREEN")
#         # Hier würde die Logik zum Laden der Datenbank, Pyrit, etc. stehen
#         return True

#     def shutdown_component(self) -> bool:
#         self._colored_print(f"[{self._component_name}] Fahre operative Module herunter...", color="WARNING")
#         # Hier würde die Logik zum Herunterfahren der Datenbank, Pyrit, etc. stehen
#         return True

#     # Spezifische DurgaEngine-Methoden (z.B. execute_command, manage_blockchain)
#     def execute_command(self, command: str) -> Dict[str, Any]:
#         self.report_status(f"Führe Befehl aus: {command}")
#         # ... Logik zur Befehlsausführung ...
#         return {"status": "success", "message": "Befehl ausgeführt."}

# class TesseractFrontend(SystemSphereBase):
#     _component_name = "TesseractFrontend"
#     _component_type = "UserInterface"
#     _component_version = "1.0.0"

#     def initialize_component(self) -> bool:
#         self._colored_print(f"[{self._component_name}] Initialisiere Benutzeroberfläche (Pandas/IPython)...", color="OKGREEN")
#         # Hier würde die Logik zum Einrichten der IPython-Hooks, Pandas-Anzeige etc. stehen
#         return True

#     def shutdown_component(self) -> bool:
#         self._colored_print(f"[{self._component_name}] Fahre Benutzeroberfläche herunter...", color="WARNING")
#         # Hier würde die Logik zum Aufräumen der UI-Ressourcen stehen
#         return True

#     # Spezifische TesseractFrontend-Methoden (z.B. display_data, handle_user_input)
#     def display_data_in_pandas(self, data: List[Dict[str, Any]], title: str) -> None:
#         self.report_status(f"Zeige Daten an: {title}")
#         # ... Logik zur Anzeige in Pandas DataFrame ...
#         pass

# Beispielnutzung der Basisklasse (kann nicht direkt instanziiert werden)
if __name__ == "__main__":
    print("Versuche, die abstrakte Basisklasse zu instanziieren...")
    try:
        # base_instance = SystemSphereBase() # Dies würde einen TypeError auslösen
        print("SystemSphereBase kann nicht direkt instanziiert werden, da sie abstrakt ist.")
    except TypeError as e:
        print(f"Erwarteter Fehler abgefangen: {e}")

    # Eine einfache Dummy-Implementierung für Testzwecke
    class DummyComponent(SystemSphereBase):
        _component_name = "DummyTestComponent"
        _component_type = "Test"

        def initialize_component(self) -> bool:
            self.report_status("Dummy-Komponente initialisiert.", level="INFO")
            return True

        def shutdown_component(self) -> bool:
            self.report_status("Dummy-Komponente heruntergefahren.", level="WARNING")
            return True

    print("\nTeste Dummy-Komponente:")
    dummy = DummyComponent()
    dummy.initialize_component()
    dummy.report_status("Ein wichtiger Statusbericht.", level="INFO")
    dummy.report_status("Ein Warnhinweis.", level="WARNING")
    dummy.report_status("Ein kritischer Fehler!", level="FAIL")
    dummy.shutdown_component()

    print("\nMetadaten der Dummy-Komponente:")
    print(dummy.get_component_metadata())