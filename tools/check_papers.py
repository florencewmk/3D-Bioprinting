"""Check archived paper bytes, inventory paths, and reference coverage."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "papers/catalog.json").read_text())
paths = set()
for paper in catalog["documents"]:
    relative = Path(paper["path"])
    assert not relative.is_absolute() and ".." not in relative.parts
    assert relative.parts[0] == "papers"
    assert paper["path"] not in paths
    paths.add(paper["path"])
    blob = (ROOT / relative).read_bytes()
    assert blob.startswith(b"%PDF-"), paper["path"]
    assert len(blob) == paper["bytes"], paper["path"]
    assert hashlib.sha256(blob).hexdigest() == paper["sha256"], paper["path"]
assert paths == {str(p.relative_to(ROOT)) for p in (ROOT / "papers").rglob("*.pdf")}
references = catalog["presentation_references"]
assert [r["number"] for r in references] == list(range(1, 11))
for reference in references:
    matches = [p["path"] for p in catalog["documents"] if reference["number"] in p["reference_numbers"]]
    assert reference["paths"] == matches
    assert reference["status"] == ("archived" if matches else "full_text_missing")
available = sum(r["status"] == "archived" for r in references)
print(f"PASS: {len(paths)} PDF files and SHA-256 hashes; {available}/10 main references archived; {10-available} full texts explicitly missing.")
