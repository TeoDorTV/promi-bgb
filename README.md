# PBB Fanzone (inoffizielle Fanseite)

Statische Seite (`index.html`), die ihre Daten aus `data.json` lädt.
Ein GitHub-Actions-Job holt stündlich News und Folgenbeschreibungen von joyn.de
und veröffentlicht die Seite über GitHub Pages.

## Einmalige Einrichtung (ca. 5 Minuten)

1. Auf github.com ein Konto anlegen/anmelden und ein **neues Repository** erstellen
   (z. B. `promi-bgb`, Sichtbarkeit: Public).
2. Diesen Ordner hochladen. Am einfachsten im Terminal im Projektordner:

   ```bash
   git init -b main
   git add .
   git commit -m "Erste Version"
   git remote add origin https://github.com/DEINNAME/promi-bgb.git
   git push -u origin main
   ```

3. Im Repository: **Settings → Pages → Build and deployment → Source: „GitHub Actions“** wählen.
4. Im Repository: **Actions → „Daten aktualisieren und Seite veröffentlichen“ → Run workflow**.
5. Nach ca. einer Minute ist die Seite unter `https://DEINNAME.github.io/promi-bgb/` erreichbar.

Danach läuft der Job jede Stunde von allein.

## Was automatisch aktualisiert wird

- **News** (neueste zuerst) und **Folgenbeschreibungen** (Tagebuch) aus Joyn
- **„Zuletzt aktualisiert“**, aber nur, wenn sich wirklich etwas geändert hat

## Was von Hand gepflegt wird (`data.json`)

| Feld | Inhalt |
|---|---|
| `cast[]` | Bewohner: `status` (`in`/`out`/`win`), `area` (`Haus`/`Garten`/`null`), `nominated` (true/false) |
| `noms[]` | Zeilen der Nominierungs-Tabelle (`tag`, `name`, `von`, `ergebnis`, `url`) |
| `diary_manual[]` | Eigene Tagebuch-Ergänzungen (z. B. Zusammenfassungen aus Artikeln) |
| `arch[]` | Archiv der früheren Staffeln |

Nominierungen und Auszüge werden bewusst **nicht** automatisch eingetragen, weil Joyn sie nur als Fließtext
beschreibt und ein falscher Treffer schlimmer wäre als ein verspäteter. Findet das Skript Stichwörter wie
„nominiert“, „Exit“ oder „Auszug“, landen sie unter `hinweise` in `data.json` und im Job-Log
(Actions → Lauf öffnen → „Daten von Joyn holen“). Dann `data.json` im GitHub-Editor anpassen (Stift-Symbol) – der nächste
Lauf veröffentlicht die Änderung. Das Skript überschreibt diese Felder nicht.

## Nominierungen & Auszüge eintragen (Admin-Seite)

Unter `https://DEINNAME.github.io/promi-bgb/admin.html` kannst du Nominierungen, Auszüge, Gewinner und Haus/Garten
per Klick eintragen und mit „Veröffentlichen“ live schalten (ca. 1–2 Minuten, bis die Seite neu gebaut ist).

Einmalig ein Token anlegen (damit nur du speichern kannst):

1. GitHub → Profilbild → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
2. **Repository access:** „Only select repositories“ → `promi-bgb`
3. **Permissions → Repository permissions → Contents: Read and write**
4. Token kopieren, auf `admin.html` unter „Verbindung zu GitHub“ einfügen, „Verbinden & laden“ klicken.

Das Token bleibt nur in deinem Browser. Die Admin-Seite ist öffentlich erreichbar, aber ohne Token kann niemand etwas ändern.
Nicht auf fremden Geräten speichern; bei Verlust das Token auf GitHub widerrufen.

## Lokal testen

```bash
python scripts/update.py      # Daten holen
python -m http.server 8765    # dann http://localhost:8765/index.html öffnen
```

(`index.html` per Doppelklick geht nicht, weil Browser `data.json` von `file://` nicht laden.)

## Hinweis

Inoffizielle Fanseite. Alle Infos und Bilder stammen von Sat.1 und Joyn, alle Rechte liegen bei den jeweiligen
Rechteinhabern. Die Fotos werden direkt von den Joyn-Servern eingebunden, nicht kopiert.
