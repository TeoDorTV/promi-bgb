#!/usr/bin/env python3
"""Holt News und Folgenbeschreibungen von joyn.de und schreibt sie in data.json.

Nur Standardbibliothek, laeuft lokal und in GitHub Actions.
Manuell gepflegte Felder (cast, noms, diary_manual, arch) bleiben unveraendert.
Nominierungen/Auszuege werden NICHT automatisch eingetragen. Treffer auf
Stichwoerter landen als "hinweise" in data.json und im Log zur manuellen Pruefung.
"""
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "https://www.joyn.de"
BTS = BASE + "/bts/serien/promi-big-brother"
MEDIATHEK = BASE + "/serien/promi-big-brother"
DATA = Path(__file__).resolve().parent.parent / "data.json"
SEASON_START = "2026-09-01"
UA = {"User-Agent": "Mozilla/5.0 (Fanseite-Updater)"}
KEYWORDS = re.compile(
    r"nominier|\bExit\b|Exit-Liste|Auszug|muss gehen|verl.sst das Haus|ausgezogen|ist raus|rausgew",
    re.I,
)
EVERGREEN = re.compile(r"sendetermine|livestream|gewinner|siegerin|cast|so-stimmst-du-ab|luxus-haus")


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def meta(page, key):
    m = re.search(r'(?:property|name)="%s" content="([^"]*)"' % re.escape(key), page)
    return html.unescape(m.group(1)) if m else ""


def long_description(page):
    best = ""
    for m in re.finditer(r'"description":"((?:[^"\\]|\\.)*)"', page):
        try:
            txt = json.loads('"' + m.group(1) + '"')
        except ValueError:
            continue
        txt = html.unescape(re.sub(r"<[^>]+>", " ", txt)).strip()
        if len(txt) > len(best):
            best = txt
    short = meta(page, "og:description")
    return best if len(best) > len(short) else short


def berlin(dt_utc):
    """UTC -> Europe/Berlin ohne tzdata (Sommerzeit: letzter So Maerz bis letzter So Oktober)."""
    def last_sunday(year, month):
        d = datetime(year, month, 31, 1, tzinfo=timezone.utc)
        return d - timedelta(days=(d.weekday() + 1) % 7)
    y = dt_utc.year
    summer = last_sunday(y, 3) <= dt_utc < last_sunday(y, 10)
    return dt_utc + timedelta(hours=2 if summer else 1)


def slugs(page, pattern):
    seen = []
    for s in re.findall(pattern, page):
        if s not in seen:
            seen.append(s)
    return seen


def fetch_news():
    page = get(BTS)
    items = []
    for slug in slugs(page, r'/bts/serien/promi-big-brother/((?!kandidaten/)[a-z0-9\-/]+-\d+)'):
        if EVERGREEN.search(slug):
            continue
        url = BTS + "/" + slug
        try:
            art = get(url)
        except Exception as e:  # einzelne Fehler ignorieren
            print("WARN", url, e, file=sys.stderr)
            continue
        pub = meta(art, "article:published_time")
        if not pub or pub[:10] < SEASON_START:
            continue
        dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
        loc = berlin(dt.astimezone(timezone.utc))
        title = meta(art, "og:title")
        items.append({
            "iso": dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M"),
            "date": loc.strftime("%d.%m.%Y, %H:%M Uhr"),
            "title": title,
            "text": meta(art, "og:description"),
            "url": url,
        })
    items.sort(key=lambda n: n["iso"], reverse=True)
    return items[:12]


def fetch_episodes():
    page = get(MEDIATHEK)
    eps = []
    for slug in slugs(page, r'/serien/promi-big-brother/(2026-\d+-tag-\d+-[a-z0-9\-]+)'):
        url = MEDIATHEK + "/" + slug
        try:
            ep = get(url)
        except Exception as e:
            print("WARN", url, e, file=sys.stderr)
            continue
        n = int(re.search(r"-tag-(\d+)-", slug).group(1))
        raw = meta(ep, "og:title").split("|")[0]
        title = re.sub(r"^.*?Tag \d+:\s*", "", raw).strip()
        if not title:
            title = slug.split("-", 4)[-1].replace("-", " ").capitalize()
        eps.append({"day": n, "title": title, "text": long_description(ep), "url": url})
    eps.sort(key=lambda e: e["day"], reverse=True)
    return eps


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    old = {k: data.get(k) for k in ("news", "episodes", "hinweise")}

    fresh = fetch_news()
    by_url = {n["url"]: n for n in data["news"] if n.get("iso")}
    by_url.update({n["url"]: n for n in fresh})  # frische Daten ueberschreiben alte
    merged = sorted(by_url.values(), key=lambda n: n["iso"], reverse=True)
    data["news"] = merged[:15]
    data["episodes"] = fetch_episodes() or data["episodes"]

    hinweise = []
    for e in data["episodes"]:
        if KEYWORDS.search(e["title"] + " " + e["text"]):
            hinweise.append({"text": "Folge Tag %d: %s" % (e["day"], e["title"]), "url": e["url"]})
    for n in data["news"]:
        if KEYWORDS.search(n["title"] + " " + n["text"]):
            hinweise.append({"text": n["title"], "url": n["url"]})
    data["hinweise"] = hinweise

    new = {k: data.get(k) for k in old}
    if new != old:
        now = berlin(datetime.now(timezone.utc))
        data["updated"] = now.strftime("%d.%m.%Y, %H:%M Uhr")
        print("Aenderungen, updated =", data["updated"])
    else:
        print("Keine Aenderungen")
    if hinweise:
        print("HINWEISE zur manuellen Pruefung (Nominierung/Exit?):")
        for h in hinweise:
            print(" -", h["text"], h["url"])
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
