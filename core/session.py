class SessionState:
    """Przechowuje stan sesji, wykryte instalatory (.exe), wolumeny (.exe.001), patche (.msp) oraz licencje (.ecp/.json)."""
    def __init__(self):
        self.detected_paths = {
            # ArcGIS Pro
            "pro_installer": "",
            "windotnet_runtime": "",
            "dotnet_hosting": "",
            "webview2": "",
            "pro_patches": [],
            
            # ArcGIS Enterprise Instalatory (.exe)
            "portal_installer": "",
            "server_installer": "",
            "datastore_installer": "",
            "webadaptor_installer": "",
            "webdeploy_installer": "",

            # ArcGIS Enterprise Wolumeny (.exe.001) -> dla DSC VolumePaths
            "portal_volume": "",
            "server_volume": "",
            "datastore_volume": "",

            # ArcGIS Enterprise Patche (.msp)
            "portal_patches": [],
            "server_patches": [],
            "datastore_patches": [],

            # Licencje ArcGIS Enterprise
            "server_license": "",
            "portal_license": "",

            # Certyfikaty (.pfx / .p12 / .cer)
            "server_certificate": "",
            "portal_certificate": "",
            "all_certificates": []
        }

    def update_paths(self, new_paths: dict):
        """Aktualizuje ścieżki w sesji."""
        for key, value in new_paths.items():
            self.detected_paths[key] = value

    def get(self, key, default=""):
        val = self.detected_paths.get(key, default)
        return val if val else default

    def set(self, key, value):
        """Umożliwia zapis: session.set('klucz', wartosc)"""
        self.detected_paths[key] = value

    def __getitem__(self, key):
        """Umożliwia odczyt: session['klucz']"""
        return self.get(key)

    def __setitem__(self, key, value):
        """Umożliwia zapis: session['klucz'] = wartosc"""
        self.set(key, value)

session = SessionState()