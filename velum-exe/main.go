// VELUM — uruchamiacz dla Windows.
// Gra (velum-rzym.html) jest wbudowana w plik .exe. Przy starcie zapisuje się w
// %LOCALAPPDATA%\VELUM i otwiera w trybie aplikacji przeglądarki Edge/Chrome
// (osobne okno bez paska adresu). Gdy żadnej z nich nie ma — w domyślnej przeglądarce.
package main

import (
	_ "embed"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

//go:embed velum-rzym.html
var gra []byte

func przegladarki() []string {
	var l []string
	for _, zm := range []string{"ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"} {
		baza := os.Getenv(zm)
		if baza == "" {
			continue
		}
		l = append(l,
			filepath.Join(baza, "Microsoft", "Edge", "Application", "msedge.exe"),
			filepath.Join(baza, "Google", "Chrome", "Application", "chrome.exe"),
		)
	}
	return l
}

func main() {
	katalog := filepath.Join(os.Getenv("LOCALAPPDATA"), "VELUM")
	if os.Getenv("LOCALAPPDATA") == "" {
		katalog = filepath.Join(os.TempDir(), "VELUM")
	}
	_ = os.MkdirAll(katalog, 0o755)
	plik := filepath.Join(katalog, "velum-rzym.html")
	if err := os.WriteFile(plik, gra, 0o644); err != nil {
		plik = filepath.Join(os.TempDir(), "velum-rzym.html")
		_ = os.WriteFile(plik, gra, 0o644)
	}
	adres := (&url.URL{Scheme: "file", Path: "/" + strings.ReplaceAll(plik, `\`, "/")}).String()

	for _, p := range przegladarki() {
		if _, err := os.Stat(p); err == nil {
			profil := filepath.Join(katalog, "profil")
			cmd := exec.Command(p, "--app="+adres, "--window-size=1120,860", "--user-data-dir="+profil, "--no-first-run", "--autoplay-policy=no-user-gesture-required")
			if cmd.Start() == nil {
				return
			}
		}
	}
	_ = exec.Command("rundll32", "url.dll,FileProtocolHandler", plik).Start()
}
