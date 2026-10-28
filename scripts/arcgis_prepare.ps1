<#
.SYNOPSIS
    Skrypt do dynamicznego wyboru komponentów ArcGIS do pobrania i instalacji.
.PARAMETER Wersja
    Opcjonalny parametr pozwalający wskazać wersję bezpośrednio przy wywołaniu.
.PARAMETER Pro
    Przełącznik informujący, że wersja dotyczy ArcGIS Pro.
.PARAMETER path
    Ścieżka do zasobu sieciowego z instalatorami.
.NOTES
    Kod wyjścia: 0 = sukces, 1 = błąd (do odczytania np. przez subprocess w Pythonie).
#>
param(
    [Parameter(Mandatory=$false)]
    [string]$Wersja,
    [Parameter(Mandatory=$false)]
    [switch]$Pro,
    [Parameter(Mandatory=$true)]
    [string]$path
)

# Każdy nieobsłużony błąd kończy skrypt kodem 1 (zamiast wypisać błąd i iść dalej)
$ErrorActionPreference = 'Stop'
trap {
    Write-Host "BŁĄD: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# --- FUNKCJE POMOCNICZE ---
function Stop-ZBledem {
    param([string]$Komunikat)
    Write-Host "BŁĄD: $Komunikat" -ForegroundColor Red
    exit 1
}

function Invoke-Robocopy {
    # Kopiuje folder (z podfolderami) lub pojedynczy plik. Kody robocopy 0-7 = sukces, >=8 = błąd.
    param(
        [Parameter(Mandatory=$true)][string]$Zrodlo,
        [Parameter(Mandatory=$true)][string]$Cel,
        [string]$Plik,
        [switch]$Podkatalogi
    )
    $argumenty = @($Zrodlo, $Cel)
    if ($Plik) { $argumenty += $Plik }
    if ($Podkatalogi) { $argumenty += '/E' }
    # /Z tryb wznawialny, /MT wielowątkowo, /R /W ponowienia, reszta ogranicza ilość logów
    $argumenty += @('/Z', '/MT:8', '/R:3', '/W:5', '/NP', '/NFL', '/NDL', '/NJH')

    & robocopy @argumenty | Out-Host
    if ($LASTEXITCODE -ge 8) {
        throw "Robocopy zakończył się błędem (kod $LASTEXITCODE) dla: $Zrodlo"
    }
}

# --- KONFIGURACJA ŚCIEŻEK ---
$folderLokalnyBaza = "C:\Install_ArcGIS"
$folderSoftware = "$folderLokalnyBaza\Software"
$folderyLokalne = @(
    $folderSoftware,
    "$folderLokalnyBaza\Others"
)
$dyskSieciowy = $path


## 1. UTWORZENIE BAZOWYCH STRUKTUR FOLDERÓW LOKALNYCH
Write-Host "1. Tworzenie bazowej struktury folderów lokalnych" -ForegroundColor Cyan
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
Write-Host "2. Sprawdzanie połączenia z zasobem sieciowym" -ForegroundColor Cyan
if (-not (Test-Path $dyskSieciowy)) {
    Stop-ZBledem "Brak połączenia z zasobem lub ścieżka jest niedostępna: $dyskSieciowy"
}
Write-Host "Połączenie OK: $dyskSieciowy" -ForegroundColor Green
Write-Host ""


## 3. WYBÓR WERSJI DO INSTALACJI
Write-Host "3. Wybór wersji ArcGIS" -ForegroundColor Cyan

$sciezkaArcGISPro = Join-Path $dyskSieciowy "ArcGIS Pro"

# 1. User podał tylko przełącznik -Pro (bez wersji) -> przechodzi do wyboru wersji dla Pro
if ($Pro -and [string]::IsNullOrEmpty($Wersja)) {
    if (-not (Test-Path $sciezkaArcGISPro)) {
        Stop-ZBledem "Folder 'ArcGIS Pro' nie istnieje w zasobie: $sciezkaArcGISPro"
    }

    # @() gwarantuje tablicę również przy jednym wyniku
    $podfolderyWersji = @(Get-ChildItem -Path $sciezkaArcGISPro -Directory | Select-Object -ExpandProperty Name)

    if ($podfolderyWersji.Count -eq 0) {
        Stop-ZBledem "Brak wersji w folderze ArcGIS Pro."
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
        Stop-ZBledem "Nieprawidłowy wybór wersji."
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
    $elementyGlowne = @(Get-ChildItem -Path $dyskSieciowy | Select-Object -ExpandProperty Name)

    if ($elementyGlowne.Count -eq 0) {
        Stop-ZBledem "Zasób sieciowy jest pusty."
    }

    Write-Host "Dostępne pozycje w zasobie:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $elementyGlowne.Count; $i++) {
        Write-Host "[$i] $($elementyGlowne[$i])"
    }

    $wyborIndex = Read-Host "Wybierz numer pozycji"
    if ($wyborIndex -match '^\d+$' -and [int]$wyborIndex -lt $elementyGlowne.Count) {
        $wybranyElement = $elementyGlowne[[int]$wyborIndex]
    } else {
        Stop-ZBledem "Nieprawidłowy wybór."
    }

    $sciezkaWybranegoElementu = Join-Path $dyskSieciowy $wybranyElement
    $czyToProduktNadrzedny = $wybranyElement -match "Pro|ArcGIS Pro"

    if ($czyToProduktNadrzedny) {
        $podfolderyWersji = @(Get-ChildItem -Path $sciezkaWybranegoElementu -Directory | Select-Object -ExpandProperty Name)

        if ($podfolderyWersji.Count -eq 0) {
            Stop-ZBledem "Brak wersji w folderze $wybranyElement."
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
            Stop-ZBledem "Nieprawidłowy wybór wersji."
        }
    } else {
        $Wersja = $wybranyElement
        $sciezkaWybranejWersji = $sciezkaWybranegoElementu
    }
}

if (-not (Test-Path $sciezkaWybranejWersji)) {
    Stop-ZBledem "Wskazana ścieżka wersji nie istnieje (${sciezkaWybranejWersji})."
}

Write-Host "Wybrano wersję: ${Wersja}" -ForegroundColor Green
Write-Host ""

## 4. DYNAMICZNY WYBÓR KOMPONENTÓW Z FOLDERU SIECIOWEGO
Write-Host "4. Wybór komponentów do instalacji" -ForegroundColor Cyan

# Definiujemy rozszerzenia plików, które mają być pomijane na liście wyboru
$pomijaneRozszerzenia = @(".sha256", ".md5", ".txt")

# Pobieramy elementy i od razu filtrujemy te, które pasują do pomijanych rozszerzeń (jeśli są to pliki bezpośrednio w folderze wersji)
$dostepneKomponenty = @(Get-ChildItem -Path $sciezkaWybranejWersji | Where-Object {
    if ($_.PSIsContainer) {
        $true # Foldery zostawiamy zawsze
    } else {
        $pomijaneRozszerzenia -notcontains $_.Extension.ToLower()
    }
} | Select-Object -ExpandProperty Name)

if ($dostepneKomponenty.Count -eq 0) {
    Stop-ZBledem "Brak zawartości w folderze wybranej wersji lub wszystkie elementy zostały pominięte."
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
    Stop-ZBledem "Nie wybrano żadnych poprawnych komponentów."
}

Write-Host ""
Write-Host "Wybrano do pobrania następujące pozycje:" -ForegroundColor Green
$wybraneElementy | ForEach-Object { Write-Host " - $_" -ForegroundColor DarkGreen }
Write-Host ""

## 5. KONTROLA MIEJSCA NA DYSKU I KOPIOWANIE PLIKÓW BEZPOŚREDNIO DO SOFTWARE
Write-Host "5. Kontrola miejsca na dysku i kopiowanie plików komponentów do Software" -ForegroundColor Cyan

# 5a. Obliczenie potrzebnego miejsca (górne oszacowanie - robocopy pomija pliki już istniejące i niezmienione)
Write-Host "Obliczanie rozmiaru wybranych komponentów..." -ForegroundColor Yellow
$potrzebneBajty = [long]0
foreach ($element in $wybraneElementy) {
    $lokalizacjaZrodlowa = Join-Path $sciezkaWybranejWersji $element
    if (Test-Path -LiteralPath $lokalizacjaZrodlowa -PathType Container) {
        $suma = (Get-ChildItem -LiteralPath $lokalizacjaZrodlowa -Recurse -File | Measure-Object -Property Length -Sum).Sum
    } else {
        $suma = (Get-Item -LiteralPath $lokalizacjaZrodlowa).Length
    }
    $potrzebneBajty += [long]$suma
}

$korzenDysku = [System.IO.Path]::GetPathRoot($folderLokalnyBaza)
$wolneBajty = ([System.IO.DriveInfo]$korzenDysku).AvailableFreeSpace

Write-Host ("Potrzebne: {0} GB, wolne na {1}: {2} GB" -f [math]::Round($potrzebneBajty / 1GB, 2), $korzenDysku, [math]::Round($wolneBajty / 1GB, 2))
if ($potrzebneBajty -gt $wolneBajty) {
    Stop-ZBledem "Za mało wolnego miejsca na dysku $korzenDysku."
}
Write-Host ""

# 5b. Kopiowanie (robocopy: wznawianie, ponowienia, wielowątkowość, pomijanie niezmienionych plików)
foreach ($element in $wybraneElementy) {
    $lokalizacjaZrodlowa = Join-Path $sciezkaWybranejWersji $element

    Write-Host "Kopiowanie '$element' do $folderSoftware..." -ForegroundColor Cyan

    if (Test-Path -LiteralPath $lokalizacjaZrodlowa -PathType Container) {
        # Kopiujemy zawartość folderu komponentu bezpośrednio do Software (bez tworzenia podfolderu o nazwie komponentu)
        Invoke-Robocopy -Zrodlo $lokalizacjaZrodlowa -Cel $folderSoftware -Podkatalogi
    } else {
        # Jeśli to pojedynczy plik, kopiujemy go bezpośrednio do Software
        Invoke-Robocopy -Zrodlo $sciezkaWybranejWersji -Cel $folderSoftware -Plik $element
    }

    Write-Host "Skopiowano pomyślnie." -ForegroundColor Green
}

Write-Host ""
Write-Host "Kopiowanie wybranych komponentów zakończone." -ForegroundColor Cyan
Write-Host ""

## 6. KOPIOWANIE DODATKÓW PRZEDINSTALACYJNYCH I MODUŁÓW POWERSHELL
Write-Host "6. Kopiowanie pre-install add-ons oraz modułów DSC" -ForegroundColor Cyan

$zrodloAdds = Join-Path $dyskSieciowy "PreInstallWindowsAdds_ArcGIS"

# 1. Kopiowanie plików .exe oraz .msi do C:\Install_ArcGIS\Software
if (Test-Path $zrodloAdds) {
    Write-Host "Szukanie plików .exe oraz .msi w lokalizacji: $zrodloAdds" -ForegroundColor Yellow
    $plikiInstalacyjne = @(Get-ChildItem -Path $zrodloAdds -File | Where-Object { $_.Extension.ToLower() -in @(".exe", ".msi") })

    if ($plikiInstalacyjne.Count -gt 0) {
        foreach ($plik in $plikiInstalacyjne) {
            Write-Host "Kopiuje $($plik.Name)..." -ForegroundColor Cyan
            Copy-Item -LiteralPath $plik.FullName -Destination $folderSoftware -Force -ErrorAction Stop
            Write-Host "Skopiowano: $($plik.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "Brak plików .exe lub .msi w folderze dodatków." -ForegroundColor DarkYellow
    }
} else {
    Write-Host "OSTRZEŻENIE: Ścieżka z dodatkami nie istnieje: $zrodloAdds" -ForegroundColor Yellow
}

# 2. Kopiowanie modułów (m.in. ArcGIS) do lokalizacji PowerShell Modules (tylko 64-bit)
$zrodloModulu = Join-Path $zrodloAdds "PowershellDSC\Modules"
$katalogModulow = "C:\Program Files\WindowsPowerShell\Modules"
$modulyKopiowane = @()

if (Test-Path $zrodloModulu) {
    Write-Host "Kopiowanie modułów PowerShell do: $katalogModulow" -ForegroundColor Yellow

    if (-not (Test-Path $katalogModulow)) {
        New-Item -ItemType Directory -Path $katalogModulow -Force | Out-Null
    }

    $modulyKopiowane = @(Get-ChildItem -Path $zrodloModulu)
    foreach ($modul in $modulyKopiowane) {
        Write-Host "Kopiuje moduł $($modul.Name)..." -ForegroundColor Cyan
        Copy-Item -LiteralPath $modul.FullName -Destination $katalogModulow -Recurse -Force -ErrorAction Stop
    }
    Write-Host "Skopiowano moduły pomyślnie do: $katalogModulow" -ForegroundColor Green
} else {
    Write-Host "OSTRZEŻENIE: Ścieżka źródłowa modułów jest niedostępna: $zrodloModulu" -ForegroundColor Yellow
}

Write-Host ""

## 7. ODBLOKOWANIE SKOPIOWANYCH PLIKÓW (Zone.Identifier)
Write-Host "7. Odblokowywanie skopiowanych plików" -ForegroundColor Cyan

Write-Host "Odblokowywanie plików w: $folderSoftware" -ForegroundColor Yellow
Get-ChildItem -LiteralPath $folderSoftware -File -Recurse | Unblock-File

foreach ($modul in $modulyKopiowane) {
    $celModulu = Join-Path $katalogModulow $modul.Name
    if (Test-Path -LiteralPath $celModulu -PathType Container) {
        Write-Host "Odblokowywanie plików w: $celModulu" -ForegroundColor Yellow
        Get-ChildItem -LiteralPath $celModulu -File -Recurse | Unblock-File
    } elseif (Test-Path -LiteralPath $celModulu) {
        Unblock-File -LiteralPath $celModulu
    }
}

Write-Host ""
Write-Host "Przygotowanie zakończone pomyślnie!" -ForegroundColor Cyan
exit 0
