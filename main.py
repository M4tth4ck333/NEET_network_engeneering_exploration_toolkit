import sys
import os
import argparse
import time
import threading # Für den Hintergrund-Server

# Passe den Python-Pfad an, damit Module gefunden werden
# Gehe zwei Ebenen hoch von main.py -> zum Projekt-Root
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python_core'))
sys.path.append(os.path.join(project_root, 'src', 'exo_kernel'))
# Füge weitere Pfade hinzu, falls nötig, z.B. für external_bases/recon-ng
# sys.path.append(os.path.join(project_root, 'external_bases', 'recon-ng'))

# Importiere die Komponenten
from core_context_manager import CoreContextManager # Aus src/python_core
from api_server import DurgaAPIServer # Aus src/exo_kernel

# Dummy ConfigManager für diesen Test (kann später durch echte Implementierung ersetzt werden)
class DummyConfigManager:
    def get(self, key: str, default: Any = None) -> Any:
        # Hier könnten echte Konfigurationswerte stehen
        return default

def main():
    parser = argparse.ArgumentParser(description="NEET-OS Core System Launcher.")
    parser.add_argument('--mode', type=str, default='ui',
                        choices=['headless', 'ui', 'debug'],
                        help='Startmodus des Systems (headless, ui, debug).')
    parser.add_argument('--api-port', type=int, default=5000,
                        help='Port für den Flask API Server.')

    args = parser.parse_args()

    # Initialisiere den Dummy Config Manager
    config_manager = DummyConfigManager()

    # Initialisiere den CoreContextManager (Jan als ZNS)
    context_manager = None
    api_server_instance = None

    try:
        context_manager = CoreContextManager(config_manager)
        if not context_manager.initialize_component():
            print("Kritischer Fehler: System konnte nicht initialisiert werden. Beende.")
            sys.exit(1)
        
        # Starte den DurgaAPI Server im Hintergrund
        api_server_instance = DurgaAPIServer(context_manager, port=args.api_port)
        api_server_instance.start_in_background()

        print(f"\nNEET-OS gestartet im Modus: {args.mode}")
        print(f"System-Metadaten: {context_manager.get_component_metadata()}")
        print(f"API läuft auf http://localhost:{args.api_port}")

        if args.mode == 'ui':
            print("\nDas 'Die AST-GFX-API' (Frontend) sollte nun in Ihrem Browser unter")
            print(f"http://localhost:{args.api_port} verfügbar sein.")
            print("Drücken Sie Strg+C, um das System zu beenden.")
            # Halte das Hauptprogramm am Laufen, damit der Hintergrund-Server läuft
            while True:
                time.sleep(1) # Kurze Pause, um CPU-Auslastung zu reduzieren

        elif args.mode == 'headless' or args.mode == 'debug':
            print("System läuft im Headless-Modus. Bereit für Befehle oder Hintergrundaufgaben.")
            print("Drücken Sie Strg+C, um das System zu beenden.")
            # Hier könnten Hintergrundaufgaben gestartet werden
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nSystem durch Benutzer beendet (Strg+C).")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}", file=sys.stderr)
        if context_manager:
            context_manager.report_status(f"Unerwarteter Systemfehler: {e}", "FAIL")
        sys.exit(1)
    finally:
        if context_manager:
            context_manager.shutdown_component()
            print("NEET-OS erfolgreich heruntergefahren.")

if __name__ == "__main__":
    main()
