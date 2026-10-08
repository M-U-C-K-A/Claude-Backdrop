package tui

// Renders two screens of the interface, in Ayu Dark and Ayu Light, to ANSI
// files: the source of the terminal picture in the README
// (docs/readme/src/ansi2svg.py turns them into SVG). Skipped unless
// CAPTURE_OUT names the folder to write to.

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/charmbracelet/lipgloss"
	"github.com/muesli/termenv"

	"github.com/M-U-C-K-A/claude-code/internal/backdrop"
)

func TestCaptureScreens(t *testing.T) {
	out := os.Getenv("CAPTURE_OUT")
	if out == "" {
		t.Skip("set CAPTURE_OUT to render the README screens")
	}
	// A support folder with the four paintings listed, as after an install.
	dir := t.TempDir()
	t.Setenv("CLAUDE_BACKDROP_DIR", dir)
	var manifest []backdrop.Image
	for _, p := range backdrop.Gallery {
		file := p.ID + ".jpg"
		if err := os.MkdirAll(filepath.Join(dir, "gallery"), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(dir, "gallery", file), []byte("jpeg"), 0o644); err != nil {
			t.Fatal(err)
		}
		manifest = append(manifest, backdrop.Image{ID: p.ID, Title: p.Title, File: file})
	}
	data, _ := json.Marshal(manifest)
	if err := os.WriteFile(filepath.Join(dir, "gallery", "manifest.json"), data, 0o644); err != nil {
		t.Fatal(err)
	}
	b := backdrop.New("/Applications/Claude.app")

	lipgloss.SetColorProfile(termenv.TrueColor)
	defer lipgloss.SetHasDarkBackground(true)
	for _, theme := range []string{"dark", "light"} {
		lipgloss.SetHasDarkBackground(theme == "dark")
		m := newModel(b)
		m.width, m.height = 112, 30
		m.st = &backdrop.Status{AppFound: true, AppVersion: "2.9939.2", Loader: backdrop.LoaderCurrent, HashOK: true, Config: m.cfg}
		for name, scr := range map[string]screen{"home": scrHome, "settings": scrSettings} {
			m.scr = scr
			m.cursor[scrSettings] = 3
			if err := os.WriteFile(filepath.Join(out, name+"-"+theme+".ansi"), []byte(m.View()), 0o644); err != nil {
				t.Fatal(err)
			}
		}
	}
}
