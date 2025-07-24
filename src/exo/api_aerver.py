# src/exo-kernel/api_server.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # Wichtig für Frontend-Zugriff
from threading import Thread
import os
import pandas as pd # Importiere Pandas

# Annahme: CoreContextManager (Jan) ist verfügbar und initialisiert
# from python_core.core_context_manager import CoreContextManager
# from core.base.system_sphere_base import SystemSphereBase # Für Typ-Hints und Basis-Methoden

class DurgaAPIServer:
    def __init__(self, context_manager: 'CoreContextManager', host: str = '0.0.0.0', port: int = 5000):
        self.app = Flask(__name__, static_folder='../tesseract-ui/public') # Statische Dateien aus dem Frontend-Ordner
        CORS(self.app) # Ermöglicht Cross-Origin-Requests vom Frontend
        self.context_manager = context_manager
        self.host = host
        self.port = port
        self._setup_routes()
        self.server_thread = None
        self.context_manager.report_status(f"DurgaAPI Server initialisiert auf {host}:{port}.", "INFO")

    def _setup_routes(self):
        # Serve the frontend HTML
        @self.app.route('/')
        def serve_index():
            return send_from_directory(self.app.static_folder, 'index.html')

        # API-Endpunkt für den Systemstatus
        @self.app.route('/api/system/status', methods=['GET'])
        def get_system_status():
            status = self.context_manager.get_system_status() # Annahme: Methode in CoreContextManager
            return jsonify(status)

        # API-Endpunkt zum Abrufen von Logs (mit Pandas-Formatierung)
        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            logs_raw = self.context_manager.get_system_logs() # Annahme: Methode in CoreContextManager
            if not logs_raw:
                return jsonify({"status": "success", "data": []})
            
            # Pandas nutzen, um Logs zu einem DataFrame zu verarbeiten
            df_logs = pd.DataFrame(logs_raw)
            # Optional: Zeitstempel formatieren
            if 'timestamp' in df_logs.columns:
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Rückgabe als JSON (Pandas DataFrame kann direkt zu JSON serialisiert werden)
            return jsonify({"status": "success", "data": df_logs.to_dict(orient='records')})

        # API-Endpunkt zum Ausführen von CLI-Befehlen (wie in der Django-App)
        @self.app.route('/api/execute_command', methods=['POST'])
        def execute_cli_command():
            data = request.json
            command = data.get('command')
            if not command:
                return jsonify({"status": "error", "message": "No command provided."}), 400
            
            # Rufe die Methode im CoreContextManager auf, die den Befehl verarbeitet
            result = self.context_manager.execute_system_command(command)
            return jsonify(result)

        # Beispiel: API-Endpunkt für Scan-Ergebnisse
        @self.app.route('/api/scan_results', methods=['GET'])
        def get_scan_results():
            scan_data_raw = self.context_manager.get_scan_results() # Annahme: Methode in CoreContextManager
            if not scan_data_raw:
                return jsonify({"status": "success", "data": []})
            
            df_scan = pd.DataFrame(scan_data_raw)
            # Beispiel: Konvertiere JSON-Spalten, wenn nötig
            # if 'result_data' in df_scan.columns:
            #     df_scan['result_data_summary'] = df_scan['result_data'].apply(lambda x: json.dumps(x) if x else None)
            
            return jsonify({"status": "success", "data": df_scan.to_dict(orient='records')})


    def run_server(self):
        self.app.run(host=self.host, port=self.port)

    def start_in_background(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.daemon = True # Server-Thread beendet sich, wenn Hauptprogramm beendet
        self.server_thread.start()
        self.context_manager.report_status(f"DurgaAPI Server im Hintergrund gestartet auf {self.host}:{self.port}", "OKGREEN")

# --- Integration in main.py (konzeptionell) ---
# In main.py:
# from src.exo_kernel.api_server import DurgaAPIServer
# from python_core.core_context_manager import CoreContextManager # CoreContextManager muss von SystemSphereBase erben

# def main():
#     # ... (argparse, config_manager, setup_python_path)

#     context_manager = CoreContextManager(config_manager)
#     if not context_manager.initialize_component():
#         print("Kritischer Fehler: System konnte nicht initialisiert werden. Beende.")
#         sys.exit(1)

#     # Starte den API-Server
#     api_server = DurgaAPIServer(context_manager, port=5000) # Port 5000 ist Standard für Flask
#     api_server.start_in_background()
#     print(f"NEET-OS API läuft auf http://{api_server.host}:{api_server.port}")

#     # Wenn im UI-Modus, halten Sie das Hauptprogramm am Laufen
#     if args.mode == 'ui':
#         print("Frontend-App sollte nun über den Browser unter der API-URL erreichbar sein.")
#         # Halte das Hauptprogramm am Laufen, damit der Hintergrund-Server läuft
#         try:
#             while True:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print("\nSystem durch Benutzer beendet.")
#     elif args.mode == 'headless' or args.mode == 'debug':
#         print("System läuft im Headless-Modus. Bereit für Befehle oder Hintergrundaufgaben.")
#         # ... (Logik für Headless-Betrieb)
#         try:
#             while True:
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print("\nSystem durch Benutzer beendet.")
#     
#     # ... (finally block für shutdown_component)