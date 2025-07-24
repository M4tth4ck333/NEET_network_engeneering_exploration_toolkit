import cmd2
import os
from typing import Dict, Any, List, Optional

# Importiere den CoreContextManager
# Annahme: src/python_core/core_context_manager.py ist im PYTHONPATH
from python_core.core_context_manager import CoreContextManager

class NEETShell(cmd2.Cmd):
    """
    NEET-OS Interaktive Kommandozeilen-Shell (BusyBox-ähnlich).
    Dies ist der CLI-basierte Jan, der direkt mit dem CoreContextManager interagiert.
    """
    # Überladene cmd2-Attribute
    intro = "\n🌐 Willkommen im NEET-OS Sphärischen Klassenzimmer (Jan CLI) 🌐\nType 'help' for commands.\n"
    prompt = "NEET-OS> "
    
    # Farben für die Shell-Ausgabe
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

    def __init__(self, core_context_manager: CoreContextManager):
        super().__init__()
        self.core_context_manager = core_context_manager
        
        # Deaktiviere cmd2-eigene Pager, da wir oft direkte Ausgabe wollen
        self.poutput("NEETShell initialisiert. Verwende 'status' und 'logs' zum Start.")
        self.core_context_manager.report_status("NEETShell initialisiert und bereit.", "INFO")

    def _colored_output(self, message: str, color: str = "") -> None:
        """Gibt eine Nachricht mit optionaler Farbformatierung über poutput aus."""
        color_code = self._COLORS.get(color.upper(), "")
        self.poutput(f"{color_code}{message}{self._COLORS['ENDC']}")

    # --- CLI Commands (do_ Methoden) ---

    @cmd2.with_argparser(cmd2.Cmd2ArgumentParser(description="Zeigt den aktuellen Systemstatus von Jan (ZNS)."))
    def do_status(self, _):
        """Zeigt den aktuellen Systemstatus von Jan (ZNS)."""
        status_data = self.core_context_manager.get_system_status()
        self._colored_output("\n--- System Status (Jan als ZNS) ---", "HEADER")
        self._colored_output(json.dumps(status_data, indent=2), "OKBLUE")

    @cmd2.with_argparser(cmd2.Cmd2ArgumentParser(description="Zeigt die System Logs aus der Datenbank."))
    def do_logs(self, _):
        """Zeigt die System Logs aus der Datenbank."""
        logs = self.core_context_manager.get_system_logs()
        self._colored_output("\n--- System Logs ---", "HEADER")
        if not logs:
            self._colored_output("Keine Logs verfügbar.", "WARNING")
            return
        
        # Ausgabe formatieren (Pandas wird im Backend gemacht, hier nur einfache Textausgabe)
        for log in logs:
            timestamp = log.get('timestamp', 'N/A')
            level = log.get('level', 'INFO')
            component = log.get('component', 'System')
            message = log.get('message', 'No message')
            color = "OKGREEN"
            if level == "WARNING": color = "WARNING"
            elif level == "ERROR" or level == "FAIL": color = "FAIL"
            elif level == "COMMAND": color = "OKCYAN"
            
            self._colored_output(f"[{timestamp}] [{level}] [{component}]: {message}", color)

    @cmd2.with_argparser(cmd2.Cmd2ArgumentParser(description="Zeigt gespeicherte Netzwerkgeräte."))
    def do_devices(self, _):
        """Zeigt gespeicherte Netzwerkgeräte."""
        devices = self.core_context_manager.get_devices()
        self._colored_output("\n--- Netzwerkgeräte ---", "HEADER")
        if not devices:
            self._colored_output("Keine Geräte verfügbar.", "WARNING")
            return
        
        for dev in devices:
            self._colored_output(f"ID: {dev.get('id')}, Name: {dev.get('name')}, IP: {dev.get('ip')}, OS: {dev.get('os')}", "OKBLUE")

    scan_parser = cmd2.Cmd2ArgumentParser(description="Startet einen simulierten Netzwerk-Scan.")
    scan_parser.add_argument('target', help='Das Ziel des Scans (z.B. 192.168.1.1 oder example.com)')

    @cmd2.with_argparser(scan_parser)
    def do_scan(self, args):
        """Startet einen simulierten Netzwerk-Scan."""
        result = self.core_context_manager.execute_system_command(f"scan {args.target}")
        self._colored_output(f"\n--- Scan Ergebnis für {args.target} ---", "HEADER")
        self._colored_output(json.dumps(result, indent=2), "OKGREEN" if result.get('status') == 'success' else "FAIL")

    @cmd2.with_argparser(cmd2.Cmd2ArgumentParser(description="Löscht alle System Logs aus der Datenbank."))
    def do_clear_logs(self, _):
        """Löscht alle System Logs aus der Datenbank."""
        result = self.core_context_manager.execute_system_command("clear logs")
        self._colored_output(json.dumps(result, indent=2), "OKGREEN" if result.get('status') == 'success' else "FAIL")


    @cmd2.with_argparser(cmd2.Cmd2ArgumentParser(description="Zeigt die verfügbaren Plugins an."))
    def do_plugins(self, _):
        """Zeigt die verfügbaren Plugins an."""
        self._colored_output("\n--- Verfügbare Plugins ---", "HEADER")
        if not self.core_context_manager.plugins:
            self._colored_output("Keine Plugins registriert.", "WARNING")
            return
        for name, plugin in self.core_context_manager.plugins.items():
            self._colored_output(f"  - {name} (Typ: {plugin.description})", "OKBLUE") # description nutzen
            # Hier könnte man auch plugin.get_metadata() aufrufen, wenn es eine solche Methode hat
        
    # --- Beispiel für einen einfachen OS-Befehl (BusyBox-like) ---
    ls_parser = cmd2.Cmd2ArgumentParser(description="Listet den Inhalt eines Verzeichnisses auf.")
    ls_parser.add_argument('path', nargs='?', default='.', help='Pfad zum Verzeichnis (Standard: .)')
    @cmd2.with_argparser(ls_parser)
    def do_ls(self, args):
        """Listet den Inhalt eines Verzeichnisses auf."""
        try:
            items = os.listdir(args.path)
            self._colored_output(f"Inhalt von '{args.path}':", "HEADER")
            for item in sorted(items):
                item_path = os.path.join(args.path, item)
                if os.path.isdir(item_path):
                    self._colored_output(f"  [DIR] {item}", "OKCYAN")
                else:
                    self._colored_output(f"  [FILE] {item}", "OKGREEN")
        except FileNotFoundError:
            self._colored_output(f"Fehler: Verzeichnis '{args.path}' nicht gefunden.", "FAIL")
        except Exception as e:
            self._colored_output(f"Fehler beim Auflisten von '{args.path}': {e}", "FAIL")

    # --- CLI Helper Commands ---
    def default(self, inp):
        """Standardaktion für unbekannte Befehle."""
        if inp.startswith('!'): # Erlaube Shell-Befehle mit '!' Präfix
            os.system(inp[1:])
        else:
            self._colored_output(f"Unbekannter Befehl: {inp}. Tippen Sie 'help' für eine Liste der Befehle.", "WARNING")

    def postcmd(self, stop, line):
        """Wird nach jeder Befehlsausführung aufgerufen."""
        if not stop: # Wenn das Shell nicht beendet wurde
            self.core_context_manager.report_status(f"CLI-Befehl ausgeführt: '{line}'", "INFO")
        return stop

