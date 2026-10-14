#!/usr/bin/env python3
"""Create an Outlook-compatible school lunch subscription from Skolmaten RSS."""
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import re
import xml.etree.ElementTree as ET

SOURCE = "https://skolmaten.se/api/4/rss/week/hovasskolan?locale=sv"
OUTPUT = Path("docs/skolmat.ics")

def clean(s):
    s = unescape(s or "")
    s = re.sub(r"<\s*br\s*/?\s*>", "\n", s, flags=re.I)
    s = re.sub(r"</(?:p|div|li)>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]*>", "", s)
    return [re.sub(r"\s+", " ", line).strip(" •-\t") for line in s.splitlines() if line.strip(" •-\t")]

def escape(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def fold(line):
    result = []
    current = ""
    for char in line:
        if len((current + char).encode("utf-8")) > 73:
            result.append(current)
            current = " " + char
        else:
            current += char
    result.append(current)
    return "\r\n".join(result)

def main():
    req = Request(SOURCE, headers={"User-Agent": "HovasskolanLunchCalendar/1.0", "Accept": "application/rss+xml, application/xml, text/xml"})
    with urlopen(req, timeout=30) as response:
        xml = response.read()
    root = ET.fromstring(xml)
    entries = {}
    for item in root.iter("item"):
        raw_date = item.findtext("pubDate", "")
        try:
            day = parsedate_to_datetime(raw_date).date()
        except (ValueError, TypeError, IndexError):
            continue
        if day.weekday() >= 5:
            continue
        dishes = clean(item.findtext("description", ""))
        if not dishes:
            continue
        entries[day] = dishes
    if not entries:
        raise RuntimeError("No dated school meals found. Existing ICS file will not be overwritten.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Hovasskolan Lunch//SV", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Hovåsskolan skollunch", "X-WR-CALDESC:Automatiskt hämtad skolmat från Skolmaten.se", "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:PT24H"]
    for day, dishes in sorted(entries.items()):
        title = " / ".join(dishes)
        description = "Hovåsskolan\\n" + "\\n".join(dishes) + "\\nKälla: https://skolmaten.se/hovasskolan"
        lines.extend(["BEGIN:VEVENT", f"UID:hovasskolan-lunch-{day.isoformat()}@ohel75.github.io", f"DTSTAMP:{stamp}", f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}", f"SUMMARY:{escape(title)}", f"DESCRIPTION:{escape(description)}", "TRANSP:TRANSPARENT", "END:VEVENT"])
    lines.append("END:VCALENDAR")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(("\r\n".join(fold(s) for s in lines) + "\r\n").encode("utf-8"))
    print(f"Wrote {len(entries)} school lunch days to {OUTPUT}")

if __name__ == "__main__":
    main()
