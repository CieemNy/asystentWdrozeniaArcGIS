import os
import json
from .session import session

def scan_license_files(others_dir):
    """
    Skanuje podany katalog (np. 'others') w poszukiwaniu:
    - Licencji ArcGIS Server (.ecp)
    - Licencji ArcGIS Portal (.json)
    Zapisuje ścieżki do sesji i zwraca status.
    """
    found_licenses = {
        "server_license": "",
        "portal_license": ""
    }

    if not os.path.exists(others_dir):
        return found_licenses

    for file in os.listdir(others_dir):
        full_path = os.path.join(others_dir, file)
        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(file)[1].lower()

        # 1. Licencja Servera (.ecp)
        if ext == ".ecp":
            found_licenses["server_license"] = full_path

        # 2. Licencja Portalu (.json) z prostą walidacją
        elif ext == ".json" and _is_portal_license(full_path):
            found_licenses["portal_license"] = full_path

    if found_licenses["server_license"]:
        session["server_license"] = found_licenses["server_license"]

    if found_licenses["portal_license"]:
        session["portal_license"] = found_licenses["portal_license"]

    return found_licenses


def _is_portal_license(file_path):
    """Pomocnicza weryfikacja czy JSON jest licencją ArcGIS Portal."""
    filename = os.path.basename(file_path).lower()
    if "portal" in filename or "lic" in filename:
        return True

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            content_str = str(content).lower()
            if any(key in content_str for key in ["usertypes", "provisioning", "portal"]):
                return True
    except Exception:
        pass

    return False

def scan_installed_directory(base_dir="C:\\Install_ArcGIS"):
    """
    Przeszukuje katalog i rozdziela instalatory (.exe), wolumeny (.exe.001) oraz patche (.msp).
    """
    if not os.path.exists(base_dir):
        return session.detected_paths

    found = {
        "pro_installer": "",
        "windotnet_runtime": "",
        "webview2": "",
        "pro_patches": [],
        
        "portal_installer": "",
        "server_installer": "",
        "datastore_installer": "",
        "webadaptor_installer": "",

        "portal_volume": "",
        "server_volume": "",
        "datastore_volume": "",
        "webdeploy_installer": "",
        "dotnet_hosting": "",

        "portal_patches": [],
        "server_patches": [],
        "datastore_patches": []
    }

    for root, _, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            f_lower = file.lower()
            f_clean = f_lower.replace("_", "").replace("-", "").replace(" ", "")

            # --- 1. WOLUMENY .001 (Wymagane przez PowerShell DSC VolumePaths) ---
            if f_lower.endswith(".001"):
                if "portal" in f_clean:
                    found["portal_volume"] = full_path
                elif "server" in f_clean and "webadaptor" not in f_clean:
                    found["server_volume"] = full_path
                elif "datastore" in f_clean:
                    found["datastore_volume"] = full_path

            # --- 2. PATCHE (.msp) ---
            elif f_clean.endswith(".msp"):
                if "portal" in f_clean:
                    found["portal_patches"].append(full_path)
                elif "server" in f_clean:
                    found["server_patches"].append(full_path)
                elif "datastore" in f_clean:
                    found["datastore_patches"].append(full_path)
                elif "pro" in f_clean or "arcgispro" in f_clean:
                    found["pro_patches"].append(full_path)

            # --- 3. GłÓWNE INSTALATORY (.exe / .msi) ---
            elif f_clean.endswith(".exe") or f_clean.endswith(".msi"):

                if "webdeploy" in f_clean: 
                    found["webdeploy_installer"] = full_path
                # Pro & Dependencies
                elif "arcgispro" in f_clean and f_clean.endswith(".exe"):
                    found["pro_installer"] = full_path
                elif "dotnethosting" in f_clean:
                    found["dotnet_hosting"] = full_path
                elif "windowsdesktopruntime" in f_clean or "dotnet" in f_clean:
                    found["windotnet_runtime"] = full_path
                elif "webview2" in f_clean:
                    found["webview2"] = full_path
                
                # Enterprise
                elif "portal" in f_clean:
                    found["portal_installer"] = full_path
                elif "server" in f_clean and "webadaptor" not in f_clean:
                    found["server_installer"] = full_path
                elif "datastore" in f_clean:
                    found["datastore_installer"] = full_path
                elif "webadaptor" in f_clean:
                    found["webadaptor_installer"] = full_path

    found["portal_patches"].sort(key=os.path.getmtime)
    found["server_patches"].sort(key=os.path.getmtime)
    found["datastore_patches"].sort(key=os.path.getmtime)
    found["pro_patches"].sort(key=os.path.getmtime)
    session.update_paths(found)
    return session.detected_paths

def scan_certificate_files(others_dir):
    """
    Skanuje katalog 'others' w poszukiwaniu certyfikatów (.pfx, .p12, .cer, .crt).
    Przypisuje ścieżki do sesji na podstawie wzorców 'ags' oraz 'agp'.
    """
    cert_extensions = ('.pfx', '.p12', '.cer', '.crt')
    
    found_certs = {
        "server_certificate": "",
        "portal_certificate": "",
        "all_certificates": []
    }

    if not os.path.exists(others_dir):
        return found_certs

    for file in os.listdir(others_dir):
        full_path = os.path.join(others_dir, file)
        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(file)[1].lower()
        if ext in cert_extensions:
            found_certs["all_certificates"].append(full_path)
            fname_lower = file.lower()

            # 1. Certyfikat ArcGIS Server (ags)
            if "ags" in fname_lower or "server" in fname_lower:
                found_certs["server_certificate"] = full_path

            # 2. Certyfikat Portal for ArcGIS (agp)
            elif "agp" in fname_lower or "portal" in fname_lower:
                found_certs["portal_certificate"] = full_path

    # Zapis do sesji
    for key, val in found_certs.items():
        if val:
            session[key] = val

    return found_certs