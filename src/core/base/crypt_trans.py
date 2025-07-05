##### 
import hashlib
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Tuple
import json # Für konsistentes Hashing von komplexeren Strukturen

# Typ-Variable für die Art des generierten Objekts (hier AbstractCard oder Derivate)
T = TypeVar('T')

# Annahme: AbstractCard existiert bereits, z.B. so:
class AbstractCard:
    """
    Stark vereinfachte Beispiel-AbstractCard für den CardGenerator.
    Wird später aus unseren OSI-Layern abgeleitet und komplexer.
    """
    def __init__(self, card_id: str, name: str, description: str, card_type: str, data: Dict[str, Any]):
        self.card_id = card_id
        self.name = name
        self.description = description
        self.card_type = card_type
        self.data = data
        self.flavour_profile: Dict[str, Any] = {} # Für Meta-Dress-Up

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Karte in ein Dictionary für Hashing oder Serialisierung."""
        return {
            "card_id": self.card_id,
            "name": self.name,
            "description": self.description,
            "card_type": self.card_type,
            "data": self.data,
            # Flavour-Profile nicht für den Hash verwenden, da es nur die Darstellung betrifft
        }

    def __repr__(self):
        return f"<Card: {self.name} ({self.card_type}) - ID: {self.card_id[:8]}...>"


# Die bereits definierte Basisklasse RandomGenerator
class RandomGenerator(ABC, Generic[T]):
    def __init__(self, seed: Optional[int] = None):
        self._seed = seed if seed is not None else self._generate_new_seed()
        self._rng = random.Random(self._seed)
        print(f"RandomGenerator initialized with seed: {self._seed}")

    @property
    def current_seed(self) -> int:
        return self._seed

    def _generate_new_seed(self) -> int:
        return random.randint(0, 2**32 - 1)

    @abstractmethod
    def generate(self, context: Optional[Dict[str, Any]] = None) -> T:
        pass

    def get_md5_hash(self, data: Any) -> str:
        """Generiert einen MD5-Hash der gegebenen Daten."""
        data_str = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.md5(data_str).hexdigest()

    def get_blake2b_hash(self, data: Any) -> str:
        """Generiert einen BLAKE2b-Hash der gegebenen Daten (kryptographisch stärker)."""
        data_str = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.blake2b(data_str).hexdigest()

    def set_seed(self, seed: int):
        self._seed = seed
        self._rng = random.Random(self._seed)
        print(f"RandomGenerator seed set to: {self._seed}")

    def get_random_element(self, collection: List[Any]) -> Any:
        if not collection:
            return None
        return self._rng.choice(collection)

    def get_random_int(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def _apply_perspective(self, generated_object: T, context: Dict[str, Any]) -> T:
        # Dies ist der Erweiterungspunkt für die Jans-Engine
        # Hier könnte Jans dynamisch Attribute oder Verhaltensweisen basierend auf Kontext injizieren.
        print(f"Applying perspective for context: {context} on object: {generated_object}")
        return generated_object


class CardGenerator(RandomGenerator[AbstractCard]):
    """
    Generiert AbstractCard-Instanzen basierend auf definierten Templates und dem Kontext.
    Verwaltet Szenario-IDs und Sicherheitsmarkierungen.
    """
    def __init__(self, seed: Optional[int] = None, card_templates: Optional[List[Dict[str, Any]]] = None):
        super().__init__(seed)
        self.card_templates = card_templates if card_templates is not None else self._load_default_templates()
        self.scenario_ids: Dict[str, str] = {} # Mapping von Szenario-Name zu MD5-Hash
        self.blake2_marked_processes: Dict[str, str] = {} # Mapping von Prozess-ID zu BLAKE2b-Hash + User-Empfinden

    def _load_default_templates(self) -> List[Dict[str, Any]]:
        """
        Lädt oder definiert Standard-Kartentemplates.
        In einer echten Anwendung kämen diese aus einer DB oder Konfigurationsdateien.
        """
        return [
            {"name": "RouterConfig", "description": "A router configuration file.", "card_type": "OSI_3_Routing", "data_template": {"ip": "dynamic", "routes": [], "status": "unknown"}},
            {"name": "WebsiteLogin", "description": "A login form for a website.", "card_type": "OSI_7_ApplicationAccess", "data_template": {"url": "dynamic", "fields": ["username", "password"], "method": "POST"}},
            {"name": "VulnerabilityCVE", "description": "A detected CVE on a system.", "card_type": "OSI_Security", "data_template": {"cve_id": "dynamic", "severity": "medium", "target_ip": "dynamic"}},
            {"name": "TelemetryStream", "description": "Live telemetry data from a sensor.", "card_type": "OSI_1_Physical", "data_template": {"sensor_id": "dynamic", "value": "dynamic", "timestamp": "dynamic"}},
        ]

    def generate(self, context: Optional[Dict[str, Any]] = None) -> AbstractCard:
        """
        Generiert eine AbstractCard basierend auf einem zufällig gewählten Template
        und dem gegebenen Kontext.
        """
        if not self.card_templates:
            raise ValueError("No card templates available to generate from.")

        chosen_template = self._rng.choice(self.card_templates)
        card_name = chosen_template["name"]
        card_type = chosen_template["card_type"]
        card_description = chosen_template["description"]
        data = self._populate_template_data(chosen_template["data_template"], context)

        # Generiere eine einzigartige Card ID, z.B. aus Hash der Daten + Seed
        card_id_data = {
            "template_name": card_name,
            "seed_prefix": self.current_seed,
            "random_suffix": self.get_random_int(0, 99999) # Fügt zusätzliche Varianz hinzu
        }
        card_id = self.get_md5_hash(card_id_data) # MD5 für schnelle, eindeutige ID

        new_card = AbstractCard(card_id, card_name, card_description, card_type, data)

        # Anwendung der Perspektivierung über die Basisklasse
        final_card = self._apply_perspective(new_card, context)

        # Optional: Szenario ID'ing für die erzeugte Karte
        if context and "scenario_name" in context:
            self.register_scenario_id(context["scenario_name"], final_card)

        # Optional: Markierung sicherheitsrelevanter Prozesse
        # Hier müsste die Logik für "Blake2-Markierung" basierend auf der Karte eingefügt werden.
        # Dies würde tiefergehende Analyse oder Nutzer-Input benötigen.
        # Beispiel: Wenn die Karte eine Vulnerability betrifft oder Daten exfiltriert.
        if final_card.card_type == "OSI_Security" and self.get_random_int(0, 100) > 70: # Zufällige Markierung als Beispiel
             # Hier kommt die Logik für das Nutzer-Empfinden rein
            user_perception = context.get("user_perception", "neutral") # Kann von UI oder Profil kommen
            if user_perception == "critical":
                process_id_example = f"process_{final_card.card_id[:8]}"
                self.mark_security_process_blake2(process_id_example, final_card.to_dict(), user_perception)

        return final_card

    def _populate_template_data(self, template_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Füllt dynamische Platzhalter in den Kartendaten."""
        populated_data = {}
        for key, value in template_data.items():
            if value == "dynamic":
                # Beispiel für dynamische Datenfüllung
                if key == "ip":
                    populated_data[key] = f"192.168.{self._rng.randint(1,254)}.{self._rng.randint(1,254)}"
                elif key == "url":
                    domains = ["example.com", "test.org", "api.cloud"]
                    subdomains = ["www", "dev", "app", "secure"]
                    populated_data[key] = f"https://{self._rng.choice(subdomains)}.{self._rng.choice(domains)}/login"
                elif key == "cve_id":
                    populated_data[key] = f"CVE-{self._rng.randint(2000, 2025)}-{self._rng.randint(1000, 99999)}"
                elif key == "value":
                    populated_data[key] = round(self._rng.uniform(0.0, 100.0), 2)
                elif key == "timestamp":
                    # Hier könnte eine realistischere Zeitgenerierung erfolgen
                    populated_data[key] = "2025-07-05T12:00:00Z"
                else:
                    populated_data[key] = f"dynamic_value_{self._rng.randint(0,100)}"
            else:
                populated_data[key] = value
        return populated_data

    # --- Plot-Erstellung (Szenario-Management) ---
    def create_scenario_plot(self, scenario_name: str, num_cards: int, context: Optional[Dict[str, Any]] = None) -> List[AbstractCard]:
        """
        Erstellt einen Plot (eine Abfolge von Karten) für ein benanntes Szenario.
        Die Abfolge ist reproduzierbar, wenn der Seed fest ist.
        """
        if scenario_name in self.scenario_ids:
            print(f"Warning: Scenario '{scenario_name}' already exists. Overwriting.")
        
        # Sicherstellen, dass der Seed für dieses Szenario gesetzt ist, wenn es neu ist
        # oder wenn wir Reproduzierbarkeit wünschen.
        # Hier könnte man einen Hash des Szenario-Namens als Seed verwenden,
        # um sicherzustellen, dass gleiche Szenario-Namen gleiche Abläufe erzeugen.
        scenario_seed_base = int(self.get_md5_hash(scenario_name)[:8], 16) % (2**32 -1)
        self.set_seed(scenario_seed_base) # Setze den RNG für diesen Plot

        plot_cards: List[AbstractCard] = []
        for i in range(num_cards):
            # Kontext kann für jede Karte im Plot angepasst werden
            current_card_context = context.copy() if context else {}
            current_card_context["scenario_step"] = i + 1
            current_card_context["scenario_name"] = scenario_name # Füge Szenario-Namen zum Kontext hinzu
            plot_cards.append(self.generate(context=current_card_context))
        
        # ID'ing des Szenarios über seinen MD5-Hash des Inhalts
        plot_content_hash = self.get_md5_hash([card.to_dict() for card in plot_cards])
        self.scenario_ids[scenario_name] = plot_content_hash
        print(f"Scenario '{scenario_name}' plot created with {num_cards} cards. MD5 ID: {plot_content_hash}")
        
        return plot_cards
    
    def register_scenario_id(self, scenario_name: str, card: AbstractCard):
        """Registriert eine Karte als Teil eines Szenarios. Hilfreich für Nachverfolgung."""
        # Dies ist eine einfache Registrierung. Komplexere Plots bräuchten einen Graphen.
        # Hier wird nur der Hash des Szenarios gespeichert, nicht die Karten selbst.
        # Die tatsächlichen Karten im Szenario wären im Django-Backend persistiert.
        if scenario_name not in self.scenario_ids:
             # Generiere einen Hash basierend auf dem Szenario-Namen für Konsistenz
            self.scenario_ids[scenario_name] = self.get_md5_hash(scenario_name)
        print(f"Card {card.card_id[:8]} added to scenario {scenario_name}")


    # --- Sicherheits-Implikation: Shebang Markierung (BLAKE2b) ---
    def mark_security_process_blake2(self, process_id: str, data: Dict[str, Any], user_perception: str):
        """
        Markiert einen Prozess als sicherheitsrelevant mit BLAKE2b-Hash und dem Nutzerempfinden.
        Simuliert die interne 'Shebang'-Markierung.
        """
        # Der Hash des relevanten Dateninhalts
        content_hash = self.get_blake2b_hash(data)
        
        # Die "Shebang"-Markierung basierend auf Nutzerempfinden
        # Dies ist der Kern der "Allegabilität": Wie der Nutzer den Prozess empfindet.
        if user_perception == "critical":
            allegation_tag = "#!BLAKE2B_CRITICAL_SECURITY_IMPLICATION"
        elif user_perception == "suspicious":
            allegation_tag = "#!BLAKE2B_SUSPICIOUS_ACTIVITY"
        elif user_perception == "neutral":
            allegation_tag = "#!BLAKE2B_OBSERVED_PROCESS"
        else:
            allegation_tag = "#!BLAKE2B_UNKNOWN_PERCEPTION"
            
        full_mark = f"{allegation_tag} {content_hash}"
        self.blake2_marked_processes[process_id] = full_mark
        print(f"Process '{process_id}' marked with BLAKE2b and perception '{user_perception}': {full_mark}")
        
        # Diese Markierung könnte dann z.B. in einem Logfile, einem Bericht
        # oder als Metadaten im Django-Backend persistiert werden.
        # Die Jans-Engine (TypeScript-Seite) könnte diese Markierungen dann
        # in der UI speziell hervorheben oder Warnungen auslösen.

    def get_security_mark(self, process_id: str) -> Optional[str]:
        """Gibt die Sicherheitsmarkierung für einen Prozess zurück."""
        return self.blake2_marked_processes.get(process_id)
# app_name/models.py (Hypothetisch für unser Django-Backend)

from django.db import models
import uuid

class HTP_Server(models.Model):
    """Repräsentiert eine Instanz des Hashtopolis Servers, mit dem wir interagieren."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text="Benutzerdefinierter Name für den Server.")
    base_url = models.URLField(help_text="URL zur Hashtopolis Server API (z.B. https://ht.example.com/api/v2/).")
    api_key = models.CharField(max_length=255, blank=True, null=True, help_text="API-Schlüssel für den Serverzugriff.")
    status = models.CharField(max_length=50, default="offline", help_text="Verbindungsstatus (offline, online, error).")
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class HTP_Agent(models.Model):
    """Repräsentiert einen Agenten, der mit einem Hashtopolis Server verbunden ist."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server = models.ForeignKey(HTP_Server, on_delete=models.CASCADE, related_name='agents')
    agent_id_ht = models.IntegerField(unique=True, blank=True, null=True, help_text="Interne ID des Agenten im Hashtopolis Server.")
    name = models.CharField(max_length=255, help_text="Name des Agenten (vom Hashtopolis Server gemeldet).")
    status = models.CharField(max_length=50, default="unknown", help_text="Status des Agenten (idle, cracking, offline, etc.).")
    hashrate = models.BigIntegerField(default=0, help_text="Aktuelle Hashrate des Agenten.")
    cpu_util = models.FloatField(default=0.0, help_text="CPU-Auslastung in Prozent.")
    gpu_util = models.FloatField(default=0.0, help_text="GPU-Auslastung in Prozent.")
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} on {self.server.name}"

class HTP_Hashlist(models.Model):
    """Repräsentiert eine Hashliste im Hashtopolis Server."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server = models.ForeignKey(HTP_Server, on_delete=models.CASCADE, related_name='hashlists')
    hashlist_id_ht = models.IntegerField(unique=True, blank=True, null=True, help_text="Interne ID der Hashliste im Hashtopolis Server.")
    name = models.CharField(max_length=255)
    hash_type = models.CharField(max_length=100, help_text="Typ des Hashes (z.B. 'MD5', 'WPA').")
    total_hashes = models.IntegerField(default=0)
    cracked_hashes = models.IntegerField(default=0)
    is_secret = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class HTP_Task(models.Model):
    """Repräsentiert eine Cracking-Aufgabe im Hashtopolis Server."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server = models.ForeignKey(HTP_Server, on_delete=models.CASCADE, related_name='tasks')
    task_id_ht = models.IntegerField(unique=True, blank=True, null=True, help_text="Interne ID der Aufgabe im Hashtopolis Server.")
    name = models.CharField(max_length=255)
    hashlist = models.ForeignKey(HTP_Hashlist, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    attack_mode = models.CharField(max_length=100, help_text="Art des Angriffs (z.B. 'dictionary', 'bruteforce').")
    status = models.CharField(max_length=50, default="created", help_text="Status der Aufgabe (created, running, finished, aborted).")
    progress = models.FloatField(default=0.0, help_text="Fortschritt in Prozent.")
    cracked_count = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class HTP_CrackedHash(models.Model):
    """Repräsentiert einen geknackten Hash von einer Hashtopolis Aufgabe."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(HTP_Task, on_delete=models.CASCADE, related_name='cracked_hashes')
    hash_value = models.CharField(max_length=255)
    plain_text = models.TextField(blank=True, null=True)
    agent = models.ForeignKey(HTP_Agent, on_delete=models.SET_NULL, null=True, blank=True)
    cracked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hash_value}:{self.plain_text[:20]}"
# app_name/models.py (Hypothetisch für unser Django-Backend)

from django.db import models
import uuid

class TransmissionDaemon(models.Model):
    """Repräsentiert eine Instanz des Transmission Daemons, den wir monitoren/steuern."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text="Benutzerdefinierter Name für den Daemon.")
    rpc_url = models.URLField(help_text="URL zur Transmission RPC API (z.B. http://localhost:9091/transmission/rpc).")
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True) # Speicherung für Demo, in Prod sicher
    status = models.CharField(max_length=50, default="offline", help_text="Verbindungsstatus (offline, online, error).")
    upload_speed = models.IntegerField(default=0, help_text="Aktuelle Upload-Geschwindigkeit in KB/s.")
    download_speed = models.IntegerField(default=0, help_text="Aktuelle Download-Geschwindigkeit in KB/s.")
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Torrent(models.Model):
    """Repräsentiert einen Torrent, der von einem Transmission Daemon verwaltet wird."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daemon = models.ForeignKey(TransmissionDaemon, on_delete=models.CASCADE, related_name='torrents')
    torrent_id_td = models.IntegerField(blank=True, null=True, help_text="Interne ID des Torrents im Transmission Daemon.")
    hash_string = models.CharField(max_length=40, unique=True, help_text="SHA1-Hash des Torrent-Metadatums.")
    name = models.CharField(max_length=255)
    size_bytes = models.BigIntegerField(default=0)
    download_dir = models.CharField(max_length=512, blank=True, null=True)
    status = models.CharField(max_length=50, help_text="Status des Torrents (downloading, seeding, stopped, etc.).")
    progress_ratio = models.FloatField(default=0.0, help_text="Fortschritt des Downloads (0.0 - 1.0).")
    upload_ratio = models.FloatField(default=0.0, help_text="Upload-Verhältnis (uploaded / downloaded).")
    peers_connected = models.IntegerField(default=0)
    added_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Peer(models.Model):
    """Repräsentiert einen Peer, mit dem ein Torrent verbunden ist."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE, related_name='peers')
    address = models.GenericIPAddressField()
    port = models.IntegerField()
    client_name = models.CharField(max_length=255, blank=True, null=True)
    upload_speed = models.IntegerField(default=0, help_text="Upload-Geschwindigkeit zu diesem Peer in KB/s.")
    download_speed = models.IntegerField(default=0, help_text="Download-Geschwindigkeit von diesem Peer in KB/s.")
    is_choked = models.BooleanField(default=False) # Ob wir choked sind
    is_interested = models.BooleanField(default=False) # Ob wir interested sind

    def __str__(self):
        return f"{self.address}:{self.port} ({self.torrent.name})"
