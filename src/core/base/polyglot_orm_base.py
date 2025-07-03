# Dieser Code würde typischerweise in M4tth4ck333/jan_os/src/core/os/diagnostic.py liegen
# und von M4tth4ck333/jan_schroeder aus aufgerufen werden.

import subprocess
import os
import tempfile

class OsDiagnosticService:
    """
    Dienst zur Durchführung von OS-Basis-Checks mittels Tiny C Compiler.
    """
    def __init__(self, tcc_path: str):
        """
        Initialisiert den Diagnose-Dienst.
        :param tcc_path: Pfad zum ausführbaren Tiny C Compiler.
        """
        if not os.path.exists(tcc_path):
            raise FileNotFoundError(f"Tiny C Compiler not found at: {tcc_path}")
        self.tcc_path = tcc_path
        print(f"[OsDiagnosticService] Initialized with TCC at: {self.tcc_path}")

    def _compile_c_code(self, c_code: str, output_path: str) -> bool:
        """
        Kompiliert den gegebenen C-Code mit Tiny C.
        :param c_code: Der zu kompilierende C-Code als String.
        :param output_path: Pfad zur Ausgabedatei (Executable).
        :return: True bei Erfolg, False sonst.
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".c") as tmp_c_file:
                tmp_c_file.write(c_code)
                c_file_path = tmp_c_file.name
            
            # Beispiel: TCC aufrufen, um eine ausführbare Datei zu erstellen
            # '-o' für die Ausgabedatei
            # '-run' ist NICHT hier, da wir NUR kompilieren wollen
            command = [self.tcc_path, c_file_path, '-o', output_path]
            print(f"[OsDiagnosticService] Compiling C code: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[OsDiagnosticService] TCC Compilation Error: {e.stderr}")
            return False
        except Exception as e:
            print(f"[OsDiagnosticService] Unexpected Compilation Error: {e}")
            return False
        finally:
            if os.path.exists(c_file_path):
                os.remove(c_file_path) # Temporäre C-Datei aufräumen

    def _execute_c_program(self, program_path: str) -> tuple[int, str]:
        """
        Führt das kompilierte C-Programm aus und gibt den Rückgabewert und die Ausgabe zurück.
        :param program_path: Pfad zur ausführbaren C-Datei.
        :return: Tuple (return_code, stdout_output).
        """
        try:
            print(f"[OsDiagnosticService] Executing C program: {program_path}")
            result = subprocess.run([program_path], capture_output=True, text=True, check=True)
            return result.returncode, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[OsDiagnosticService] C Program Execution Error (Code {e.returncode}): {e.stderr}")
            return e.returncode, e.stderr.strip()
        except Exception as e:
            print(f"[OsDiagnosticService] Unexpected Execution Error: {e}")
            return -1, str(e)
        finally:
            if os.path.exists(program_path):
                os.remove(program_path) # Ausführbare Datei aufräumen

    def perform_self_induced_tcc_check(self) -> dict:
        """
        Führt einen Basis-Check mittels "Self-Induced Tiny CCC Chain" durch.
        Dieser Check testet eine einfache C-Funktion und die TCC-Fähigkeit.
        """
        print("[OsDiagnosticService] Starting self-induced Tiny CCC basis check...")
        
        # 1. Generiere einfachen C-Code
        # Dieser Code gibt eine feste Zeichenkette aus und testet printf
        # Bei Erfolg sollte "TCC_CHECK_OK" ausgegeben werden
        c_code_snippet = """
        #include <stdio.h>
        #include <stdlib.h> // Für EXIT_SUCCESS/EXIT_FAILURE

        int main() {
            printf("TCC_CHECK_OK\\n");
            return EXIT_SUCCESS;
        }
        """
        
        # Temporäre Pfade für die kompilierte Binärdatei
        with tempfile.NamedTemporaryFile(delete=False, suffix=".out") as tmp_exec_file:
            exec_path = tmp_exec_file.name

        # 2. Kompiliere den C-Code
        if not self._compile_c_code(c_code_snippet, exec_path):
            return {"status": "FAILED", "reason": "C compilation failed."}

        # 3. Führe die kompilierte Binärdatei aus
        return_code, output = self._execute_c_program(exec_path)

        # 4. Werte das Ergebnis aus
        if return_code == 0 and "TCC_CHECK_OK" in output:
            print("[OsDiagnosticService] Self-induced Tiny CCC check PASSED.")
            return {"status": "PASSED", "output": output, "return_code": return_code}
        else:
            print(f"[OsDiagnosticService] Self-induced Tiny CCC check FAILED (Code: {return_code}, Output: '{output}').")
            return {"status": "FAILED", "output": output, "return_code": return_code}

# --- Beispiel der Nutzung (würde typischerweise von jan_schroeder aufgerufen) ---
if __name__ == "__main__":
    # Ersetze dies durch den tatsächlichen Pfad zu deinem kompilierten TCC-Executable
    # Nach dem Forken von Tiny C musst du es kompilieren (z.B. `make` im Tiny C Verzeichnis).
    # tcc_executable_path = "/path/to/your/tiny_c_compiler/tcc"
    # Für Tests nehmen wir an, TCC ist im PATH oder wir nutzen einen Dummy
    
    # Dummy-Pfad für das Beispiel. Du musst hier den echten Pfad angeben!
    # Angenommen, du hast TCC in deinem jan_os Repo unter bin/tcc kompiliert
    dummy_tcc_path = "tcc" # Oder "./bin/tcc" wenn du es so kompilierst
    
    # Simuliere eine Dummy TCC-Installation, falls du noch keine hast
    # (Diese Zeilen NICHT im Produktivcode verwenden!)
    if not os.path.exists(dummy_tcc_path):
        print(f"Warning: TCC not found at '{dummy_tcc_path}'. Creating a dummy executable for demonstration.")
        # Erstelle ein Shell-Skript, das TCC simuliert
        with open(dummy_tcc_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("if [[ \"$*\" == *'-o'* && \"$*\" == *'.c'* ]]; then\n")
            f.write("  echo 'Simulating TCC compilation...'\n")
            f.write("  output_file=$(echo \"$*\" | sed -n 's/.*-o \\([^ ]*\\).*/\\1/p')\n")
            f.write("  echo '#!/bin/bash' > \"$output_file\"\n")
            f.write("  echo \"echo 'TCC_CHECK_OK'\" >> \"$output_file\"\n")
            f.write("  chmod +x \"$output_file\"\n")
            f.write("  exit 0\n")
            f.write("elif [[ \"$*\" == *'.c'* ]]; then\n")
            f.write("  echo 'Simulating TCC compilation for direct run...'\n")
            f.write("  echo 'TCC_CHECK_OK'\n")
            f.write("  exit 0\n")
            f.write("else\n")
            f.write("  echo 'Simulating TCC call, nothing to compile or run.'\n")
            f.write("  exit 0\n")
            f.write("fi\n")
        os.chmod(dummy_tcc_path, 0o755)
        print(f"Dummy TCC executable created at '{dummy_tcc_path}'. Remember to replace with real TCC!")

    try:
        os_checker = OsDiagnosticService(tcc_path=dummy_tcc_path) # Nutze den Dummy-Pfad
        check_result = os_checker.perform_self_induced_tcc_check()
        print("\n--- Basis Check Result ---")
        print(json.dumps(check_result, indent=2))

        # Test mit einer Fehlermeldung
        print("\n--- Testing a C compilation error (expected failure) ---")
        error_c_code = "int main() { printf(\"Hello\"; return 0; }" # Syntaxfehler
        with tempfile.NamedTemporaryFile(delete=False, suffix=".out") as tmp_exec_file_err:
            exec_path_err = tmp_exec_file_err.name
        
        compilation_error_check = os_checker._compile_c_code(error_c_code, exec_path_err)
        print(f"Compilation expected to fail: {not compilation_error_check}")

    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure Tiny C is compiled and the path is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Aufräumen des Dummy-TCCs, falls erstellt
        if os.path.exists(dummy_tcc_path) and "Dummy" in dummy_tcc_path: # Check, ob es unser Dummy ist
             os.remove(dummy_tcc_path)
             print(f"Cleaned up dummy TCC executable at '{dummy_tcc_path}'.")
