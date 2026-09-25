import subprocess
import threading

def run_interactive_powershell(script_path, on_finished_callback):
    """
    Otwiera interaktywne okno PowerShell z UPRAWNIENIAMI ADMINISTRATORA (UAC Elevation).
    Opcja -Wait sprawia, że proces nadrzędny czeka na zamknięcie okna admina.
    """
    def worker():
        try:
            # Konstruujemy komendę Start-Process z parametrem -Verb RunAs (wymuszenie Admina)
            ps_command = (
                f"Start-Process powershell.exe "
                f"-ArgumentList '-NoExit -ExecutionPolicy Bypass -File \"{script_path}\"' "
                f"-Verb RunAs -Wait"
            )
            
            cmd = [
                "powershell.exe",
                "-Command",
                ps_command
            ]
            
            # Uruchamiamy proces wyskakujący
            process = subprocess.Popen(cmd)
            process.wait() # Czekamy, aż użytkownik zamknie okno z prawami administratora
            
            # Kod wyjścia 0 oznacza, że okno z prawami admina zostało otwarte i zamknięte
            if process.returncode == 0:
                on_finished_callback(True, "Skrypt PowerShell został zakończony pomyślnie.")
            else:
                on_finished_callback(
                    False, 
                    "Anulowano uruchomienie (odrzucono monit UAC) lub wystąpił błąd w PowerShellu."
                )
        except Exception as e:
            on_finished_callback(False, f"Błąd uruchamiania konsoli: {e}")

    # Uruchomienie w osobnym wątku GUI
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()