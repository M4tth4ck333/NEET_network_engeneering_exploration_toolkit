# Beispiel: src/core/base/durga_api_server.py
from flask import Flask, request, jsonify
from threading import Thread
# from python_core.core_context_manager import CoreContextManager # Importiere deinen Manager

class DurgaAPIServer:
    def __init__(self, context_manager: CoreContextManager, host: str = '0.0.0.0', port: int = 5000):
        self.app = Flask(__name__)
        self.context_manager = context_manager
        self.host = host
        self.port = port
        self._setup_routes()
        self.server_thread = None
        self.context_manager.report_status("DurgaAPI Server initialisiert.", "INFO")

    def _setup_routes(self):
        @self.app.route('/api/system/status', methods=['GET'])
        def get_status():
            status = self.context_manager.get_system_status() # Annahme: Eine Methode in CoreContextManager
            return jsonify(status)

        @self.app.route('/api/modules/execute', methods=['POST'])
        def execute_module_command():
            data = request.json
            command_type = data.get('command_type')
            params = data.get('params', {})
            
            result = self.context_manager.execute_system_command(command_type, params)
            return jsonify(result)

        # Beispiel für einen Endpunkt zum Abrufen von Blockchain-Daten
        @self.app.route('/api/blockchain/history', methods=['GET'])
        def get_blockchain_history():
            # Annahme: context_manager hat Zugriff auf Blockchain-Datenbank
            history = self.context_manager.get_blockchain_data(limit=100)
            return jsonify(history)

    def run_server(self):
        self.app.run(host=self.host, port=self.port)

    def start_in_background(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.daemon = True # Server-Thread beendet sich, wenn Hauptprogramm beendet
        self.server_thread.start()
        self.context_manager.report_status(f"DurgaAPI Server im Hintergrund gestartet auf {self.host}:{self.port}", "OKGREEN")

# In src/core/base/main.py (am Ende der main-Funktion, nach Initialisierung des context_manager):
# if __name__ == "__main__":
#     # ... (argparse, config_manager, context_manager.initialize_component)

#     if args.mode == 'ui':
#         from durga_api_server import DurgaAPIServer # Importieren Sie den Server
#         durga_api_server = DurgaAPIServer(context_manager)
#         durga_api_server.start_in_background() # Server starten

#         # Hier müsste nun der Code zum Starten von Jupyter/Voila etc. stehen,
#         # der sich mit diesem API-Server verbindet.
#         print("Bitte starten Sie nun Ihr Jupyter Notebook und verwenden Sie die API des DurgaServers.")
#         # Optional: Halten Sie das Hauptprogramm am Laufen, z.B. mit einer Endlosschleife
#         while True:
#             time.sleep(1)

#     # ... (headless mode, shutdown logic)