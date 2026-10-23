import subprocess
import threading

def run_interactive_powershell(script_path, on_finished_callback):
    def worker():
        try:
            # Przygotowanie argumentów dla procesu uruchamianego jako administrator
            escaped_path = script_path.replace("'", "''")

            ps_command = (
                f"$p = Start-Process powershell.exe "
                f"-ArgumentList @('-NoExit', '-ExecutionPolicy', 'Bypass', "
                f"'-File', '\"{escaped_path}\"') "
                f"-Verb RunAs -Wait -PassThru; "
                f"exit $p.ExitCode"
            )

            # Uruchomienie procesu pośredniczącego bez widocznego okna
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-WindowStyle", "Hidden",
                    "-Command", ps_command
                ],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            process.wait()

            if process.returncode == 0:
                on_finished_callback(
                    True,
                    "Skrypt PowerShell został zakończony pomyślnie."
                )
            else:
                on_finished_callback(
                    False,
                    "Skrypt zakończył się błędem lub anulowano monit UAC."
                )

        except Exception as e:
            on_finished_callback(False, f"Błąd uruchamiania konsoli: {e}")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
