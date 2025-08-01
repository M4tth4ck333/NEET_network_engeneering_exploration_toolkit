import sys
import os
import argparse
import time

# 1. SETUP: Bleibt wie es ist.
# ----------------------------------------------------
def setup_environment():
    """Kapselt die Pfad-Konfiguration."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    sys.path.append(os.path.join(project_root, 'src'))
    sys.path.append(os.path.join(project_root, 'external_bases', 'recon-ng'))
    print("INFO: Environment paths configured.")

# 2. CORE LOGIC: Die main-Funktion als Herzstück
# ----------------------------------------------------
def main():
    """Definiert den Haupt-Lebenszyklus der Anwendung."""
    
    # --- A) INITIALIZATION PHASE ---
    setup_environment()
    
    # argparse für Start-Argumente (z.B. --mode api)
    parser = argparse.ArgumentParser(description="NEET Durga Framework")
    parser.add_argument('--mode', type=str, default='cli', choices=['cli', 'api', 'gui'], help='Execution mode')
    args = parser.parse_args()

    # Importiere den Manager, NACHDEM der Pfad gesetzt wurde
    from python_core.core_context_manager import CoreContextManager
    
    context_manager = CoreContextManager()
    print("INFO: CoreContextManager instantiated.")

    # Der Context Manager sollte die Module laden.
    # Dies ist flexibler als statische Imports hier.
    context_manager.discover_and_load_modules() 
    
    # --- B) EXECUTION PHASE ---
    if args.mode == 'api':
        # Starte den Durga API Server, den wir besprochen haben
        from python_core.durga_api_server import DurgaAPIServer
        api_server = DurgaAPIServer(context_manager)
        api_server.start_in_background()
        
        # Halte das Hauptprogramm am Laufen
        print("INFO: API server running in background. Main thread is idle.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nINFO: Shutdown signal received.")

    elif args.mode == 'cli':
        # Hier könnte eine interaktive Kommandozeile starten
        print("INFO: CLI mode started. (Implement interactive shell here)")
        # Beispiel: context_manager.start_cli_shell()
        pass

    else: # gui mode
        print("INFO: GUI mode selected. (Tauri/WebUI startup logic goes here)")
        # Beispiel: context_manager.start_gui()
        pass

    # --- C) SHUTDOWN PHASE ---
    # Diese wird nach dem Verlassen des try-Blocks oder am Ende der Funktion aufgerufen
    print("INFO: Initiating graceful shutdown...")
    context_manager.shutdown()
    print("INFO: Shutdown complete.")


# 3. ENTRY POINT
# ----------------------------------------------------
if __name__ == "__main__":
    main()