<#
.SYNOPSIS
    Skrypt do dynamicznego wyboru komponentów ArcGIS do pobrania i instalacji.
.PARAMETER Wersja
    Opcjonalny parametr pozwalający wskazać wersję bezpośrednio przy wywołaniu.
.PARAMETER Pro
    Przełącznik informujący, że wersja dotyczy ArcGIS Pro.
#>
param(
    [Parameter(Mandatory=$false)]
    [string]$Wersja,
    [Parameter(Mandatory=$false)]
    [switch]$Pro,
    [Parameter(Mandatory=$true)]
    [string]$path
)

# --- KONFIGURACJA ŚCIEŻEK ---
$folderLokalnyBaza = "C:\Install_ArcGIS"
$folderyLokalne = @(
    "$folderLokalnyBaza\Software",
    "$folderLokalnyBaza\Others"
)
$dyskSieciowy = $path


## 1. UTWORZENIE BAZOWYCH STRUKTUR FOLDERÓW LOKALNYCH
Write-Host "--- 1. Tworzenie bazowej struktury folderów lokalnych ---" -ForegroundColor Cyan
foreach ($sciezka in $folderyLokalne) {
    if (-not (Test-Path $sciezka)) {
        New-Item -ItemType Directory -Path $sciezka -Force | Out-Null
        Write-Host "Utworzono: $sciezka" -ForegroundColor Green
    } else {
        Write-Host "Folder już istnieje: $sciezka" -ForegroundColor Yellow
    }
}
Write-Host ""


## 2. SPRAWDZENIE POŁĄCZENIA DO ZASOBU SIECIOWEGO
Write-Host "--- 2. Sprawdzanie połączenia z zasobem sieciowym ---" -ForegroundColor Cyan
if (-not (Test-Path $dyskSieciowy)) {
    Write-Host "BŁĄD: Brak połączenia z zasobem lub ścieżka jest niedostępna: $dyskSieciowy" -ForegroundColor Red
    exit
}
Write-Host "Połączenie OK: $dyskSieciowy" -ForegroundColor Green
Write-Host ""


## 3. WYBÓR WERSJI DO INSTALACJI
Write-Host "--- 3. Wybór wersji ArcGIS ---" -ForegroundColor Cyan

$sciezkaArcGISPro = Join-Path $dyskSieciowy "ArcGIS Pro"

# 1. User podał tylko przełącznik -Pro (bez wersji) -> przechodzi do wyboru wersji dla Pro
if ($Pro -and [string]::IsNullOrEmpty($Wersja)) {
    if (-not (Test-Path $sciezkaArcGISPro)) {
        Write-Host "BŁĄD: Folder 'ArcGIS Pro' nie istnieje w zasobie: $sciezkaArcGISPro" -ForegroundColor Red
        exit
    }

    $podfolderyWersji = Get-ChildItem -Path $sciezkaArcGISPro -Directory | Select-Object -ExpandProperty Name
    
    if ($podfolderyWersji.Count -eq 0) {
        Write-Host "BŁĄD: Brak wersji w folderze ArcGIS Pro." -ForegroundColor Red
        exit
    }

    Write-Host "Dostępne wersje dla ArcGIS Pro:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $podfolderyWersji.Count; $i++) {
        Write-Host "[$i] $($podfolderyWersji[$i])"
    }
    
    $wyborWersjiIndex = Read-Host "Wybierz numer wersji ArcGIS Pro"
    if ($wyborWersjiIndex -match '^\d+$' -and [int]$wyborWersjiIndex -lt $podfolderyWersji.Count) {
        $Wersja = $podfolderyWersji[[int]$wyborWersjiIndex]
        $sciezkaWybranejWersji = Join-Path $sciezkaArcGISPro $Wersja
    } else {
        Write-Host "BŁĄD: Nieprawidłowy wybór wersji." -ForegroundColor Red
        exit
    }
}
# 2. User podał -Pro oraz -Wersja -> przechodzi od razu do komponentów
elseif ($Pro -and -not [string]::IsNullOrEmpty($Wersja)) {
    $sciezkaWybranejWersji = Join-Path $sciezkaArcGISPro $Wersja
    Write-Host "Użyto parametrów: ArcGIS Pro, wersja ${Wersja}" -ForegroundColor Green
}
# 3. User podał samą wersję standardową (bez -Pro)
elseif (-not [string]::IsNullOrEmpty($Wersja)) {
    $sciezkaWybranejWersji = Join-Path $dyskSieciowy $Wersja
    Write-Host "Użyto parametru: wersja standardowa ${Wersja}" -ForegroundColor Green
}
# 4. Brak parametrów -> tryb w pełni interaktywny
else {
    $elementyGlowne = Get-ChildItem -Path $dyskSieciowy | Select-Object -ExpandProperty Name

    if ($elementyGlowne.Count -eq 0) {
        Write-Host "BŁĄD: Zasób sieciowy jest pusty." -ForegroundColor Red
        exit
    }

    Write-Host "Dostępne pozycje w zasobie:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $elementyGlowne.Count; $i++) {
        Write-Host "[$i] $($elementyGlowne[$i])"
    }

    $wyborIndex = Read-Host "Wybierz numer pozycji"
    if ($wyborIndex -match '^\d+$' -and [int]$wyborIndex -lt $elementyGlowne.Count) {
        $wybranyElement = $elementyGlowne[[int]$wyborIndex]
    } else {
        Write-Host "BŁĄD: Nieprawidłowy wybór." -ForegroundColor Red
        exit
    }

    $sciezkaWybranegoElementu = Join-Path $dyskSieciowy $wybranyElement
    $czyToProduktNadrzedny = $wybranyElement -match "Pro|ArcGIS Pro"

    if ($czyToProduktNadrzedny) {
        $podfolderyWersji = Get-ChildItem -Path $sciezkaWybranegoElementu -Directory | Select-Object -ExpandProperty Name
        
        if ($podfolderyWersji.Count -eq 0) {
            Write-Host "BŁĄD: Brak wersji w folderze $wybranyElement." -ForegroundColor Red
            exit
        }

        Write-Host "Dostępne wersje dla '$wybranyElement':" -ForegroundColor Cyan
        for ($i = 0; $i -lt $podfolderyWersji.Count; $i++) {
            Write-Host "[$i] $($podfolderyWersji[$i])"
        }
        
        $wyborWersjiIndex = Read-Host "Wybierz numer wersji"
        if ($wyborWersjiIndex -match '^\d+$' -and [int]$wyborWersjiIndex -lt $podfolderyWersji.Count) {
            $Wersja = $podfolderyWersji[[int]$wyborWersjiIndex]
            $sciezkaWybranejWersji = Join-Path $sciezkaWybranegoElementu $Wersja
        } else {
            Write-Host "BŁĄD: Nieprawidłowy wybór wersji." -ForegroundColor Red
            exit
        }
    } else {
        $Wersja = $wybranyElement
        $sciezkaWybranejWersji = $sciezkaWybranegoElementu
    }
}

if (-not (Test-Path $sciezkaWybranejWersji)) {
    Write-Host "BŁĄD: Wskazana ścieżka wersji nie istnieje (${sciezkaWybranejWersji})." -ForegroundColor Red
    exit
}

Write-Host "Wybrano wersję: ${Wersja}" -ForegroundColor Green
Write-Host ""

## 4. DYNAMICZNY WYBÓR KOMPONENTÓW Z FOLDERU SIECIOWEGO
Write-Host "--- 4. Wybór komponentów do instalacji ---" -ForegroundColor Cyan

# Definiujemy rozszerzenia plików, które mają być pomijane na liście wyboru
$pomijaneRozszerzenia = @(".sha256", ".md5", ".txt")

# Pobieramy elementy i od razu filtrujemy te, które pasują do pomijanych rozszerzeń (jeśli są to pliki bezpośrednio w folderze wersji)
$dostepneKomponenty = Get-ChildItem -Path $sciezkaWybranejWersji | Where-Object {
    if ($_.PSIsContainer) {
        $true # Foldery zostawiamy zawsze
    } else {
        $pomijaneRozszerzenia -notcontains $_.Extension.ToLower()
    }
} | Select-Object -ExpandProperty Name

if ($dostepneKomponenty.Count -eq 0) {
    Write-Host "BŁĄD: Brak zawartości w folderze wybranej wersji lub wszystkie elementy zostały pominięte." -ForegroundColor Red
    exit
}

Write-Host "Znalezione komponenty/pliki dla wersji ${Wersja}:" -ForegroundColor Cyan
for ($i = 0; $i -lt $dostepneKomponenty.Count; $i++) {
    Write-Host "[$i] $($dostepneKomponenty[$i])"
}

Write-Host "Podaj numery komponentów do pobrania, oddzielając je przecinkami (np. 0,2,3) lub wpisz 'all' dla wszystkich:" -ForegroundColor Yellow
$wyborKomponentow = Read-Host "Twój wybór"

$wybraneElementy = @()

if ($wyborKomponentow -eq 'all') {
    $wybraneElementy = $dostepneKomponenty
} else {
    $indeksy = $wyborKomponentow -split ',' | ForEach-Object { $_.Trim() }
    foreach ($idx in $indeksy) {
        if ($idx -match '^\d+$' -and [int]$idx -lt $dostepneKomponenty.Count) {
            $wybraneElementy += $dostepneKomponenty[[int]$idx]
        }
    }
}

if ($wybraneElementy.Count -eq 0) {
    Write-Host "BŁĄD: Nie wybrano żadnych poprawnych komponentów." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Wybrano do pobrania następujące pozycje:" -ForegroundColor Green
$wybraneElementy | ForEach-Object { Write-Host " - $_" -ForegroundColor DarkGreen }
Write-Host ""

## 5. KOPIOWANIE PLIKÓW BEZPOŚREDNIO DO SOFTWARE
Write-Host "--- 5. Kopiowanie plików komponentów bezpośrednio do Software ---" -ForegroundColor Cyan

$folderSoftware = "$folderLokalnyBaza\Software"

foreach ($element in $wybraneElementy) {
    $lokalizacjaZrodlowa = Join-Path $sciezkaWybranejWersji $element

    Write-Host "Kopiowanie '$element' do $folderSoftware..." -ForegroundColor Cyan
    
    if (Test-Path -PathType Container $lokalizacjaZrodlowa) {
        # Kopiujemy zawartość folderu komponentu bezpośrednio do Software (bez tworzenia podfolderu o nazwie komponentu)
        Copy-Item -Path "$lokalizacjaZrodlowa\*" -Destination $folderSoftware -Recurse -Force
    } else {
        # Jeśli to pojedynczy plik, kopiujemy go bezpośrednio do Software
        Copy-Item -Path $lokalizacjaZrodlowa -Destination $folderSoftware -Force
    }
    
    Write-Host "Skopiowano pomyślnie." -ForegroundColor Green
}

Write-Host ""
Write-Host "Proces przygotowania i kopiowania wybranego zestawu komponentów został zakończony!" -ForegroundColor Cyan

## 6. KOPIOWANIE DODATKÓW PRZEDINSTALACYJNYCH I MODUŁÓW POWERSHELL
Write-Host "--- 6. Kopiowanie pre-install add-ons oraz modułów DSC ---" -ForegroundColor Cyan

# Korzystamy z wcześniej zdefiniowanej zmiennej $dyskSieciowy
$zrodloAdds = Join-Path $dyskSieciowy "PreInstallWindowsAdds_ArcGIS"
$folderSoftware = "C:\Install_ArcGIS\Software"

# 1. Kopiowanie plików .exe oraz .msi do C:\Install_ArcGIS\Software
if (Test-Path $zrodloAdds) {
    Write-Host "Szukanie plików .exe oraz .msi w lokalizacji: $zrodloAdds" -ForegroundColor Yellow
    $plikiInstalacyjne = Get-ChildItem -Path $zrodloAdds -File | Where-Object { $_.Extension.ToLower() -in @(".exe", ".msi") }

    if ($plikiInstalacyjne.Count -gt 0) {
        foreach ($plik in $plikiInstalacyjne) {
            Write-Host "Kopiuje $($plik.Name)..." -ForegroundColor Cyan
            Copy-Item -Path $plik.FullName -Destination $folderSoftware -Force
            Write-Host "Skopiowano: $($plik.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "Brak plików .exe lub .msi w folderze dodatków." -ForegroundColor DarkYellow
    }
} else {
    Write-Host "OSTRZEŻENIE: Ścieżka z dodatkami nie istnieje: $zrodloAdds" -ForegroundColor Yellow
}

# 2. Kopiowanie modułu ArcGIS do lokalizacji PowerShell Modules
$zrodloModulu = Join-Path $zrodloAdds "PowershellDSC\Modules"
$doceloweFolderyModulow = @(
    "C:\Program Files\WindowsPowerShell\Modules",
    "C:\Program Files (x86)\WindowsPowerShell\Modules"
)

if (Test-Path $zrodloModulu) {
    Write-Host "Kopiowanie modułów PowerShell..." -ForegroundColor Yellow
    
    foreach ($sciezkaModuluDocelowa in $doceloweFolderyModulow) {
        if (-not (Test-Path $sciezkaModuluDocelowa)) {
            New-Item -ItemType Directory -Path $sciezkaModuluDocelowa -Force | Out-Null
        }

        $modulyDoKopiowania = Get-ChildItem -Path $zrodloModulu
        foreach ($modul in $modulyDoKopiowania) {
            Write-Host "Kopiuje moduł $($modul.Name) do $sciezkaModuluDocelowa..." -ForegroundColor Cyan
        }

        Copy-Item -Path "$zrodloModulu\*" -Destination $sciezkaModuluDocelowa -Recurse -Force
        Write-Host "Skopiowano moduły pomyślnie do: $sciezkaModuluDocelowa" -ForegroundColor Green
    }
} else {
    Write-Host "OSTRZEŻENIE: Ścieżka źródłowa modułów jest niedostępna: $zrodloModulu" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Kopiowanie dodatków i modułów zakończone pomyślnie!" -ForegroundColor Cyan