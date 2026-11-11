#!/usr/bin/env python
"""Vérifie le livrable du TP 4 comme le fera le correcteur.

Usage, à la racine du dépôt, après « python -m build » :
    python scripts/verifier_livrable.py

Contrôles : les deux fichiers de dist/, le nom de la roue, sa version, son contenu, le journal des
versions, l'étiquette Git, puis installation dans un environnement NEUF, tests/test_paquet.py et commande.
Écrit le rapport dans docs/livrable-tp4.txt. Ce rapport n'est PAS commité (il est dans .gitignore) :
il se joint à la release GitHub, avec les deux fichiers de dist/. Le commiter déplacerait le dernier
commit hors de l'étiquette v1.0.0.
Code de retour : 0 si tout est conforme, 1 sinon. Aucune dépendance hors bibliothèque standard.
"""
import os
import platform
import subprocess
import sys
import tempfile
import tomllib
import venv
import zipfile
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DIST = RACINE / "dist"
RAPPORT = RACINE / "docs" / "livrable-tp4.txt"
AVIS = "Produit cassé et service injoignable, à fuir"
lignes: list[str] = []
echecs = 0


def noter(ok: bool, quoi: str, detail: str = "") -> bool:
    global echecs
    echecs += not ok
    lignes.append(f"[{'OK' if ok else 'ÉCHEC'}] {quoi}{' : ' + detail if detail else ''}")
    print(lignes[-1])
    return ok


def lancer(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    # VERIFICATION_LIVRABLE rend les tests du paquet obligatoires : un test ignoré ne prouve rien
    env = {**os.environ, "VERIFICATION_LIVRABLE": "1"}
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=False)


def main() -> int:
    projet = tomllib.loads((RACINE / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    nom, version = projet["name"].replace("-", "_"), projet["version"]
    lignes.append(f"Livrable TP 4 : {projet['name']} {version}, vérifié le {datetime.now().astimezone():%Y-%m-%d %H:%M %z}, "
                  f"Python {platform.python_version()}, {platform.system()}")

    # 1. Les deux fichiers de dist/
    roue = DIST / f"{nom}-{version}-py3-none-any.whl"
    source = DIST / f"{nom}-{version}.tar.gz"
    noter(roue.exists(), "roue présente", roue.name)
    noter(source.exists(), "distribution source présente", source.name)
    autres = sorted(p.name for p in DIST.glob("*") if p not in (roue, source)) if DIST.exists() else []
    noter(not autres, "aucun autre fichier dans dist/", ", ".join(autres) or "")
    if not roue.exists():
        return terminer()

    # 2. Contenu de la roue
    with zipfile.ZipFile(roue) as z:
        noms = z.namelist()
        points = z.read(f"{nom}-{version}.dist-info/entry_points.txt").decode() if \
            f"{nom}-{version}.dist-info/entry_points.txt" in noms else ""
    noter(any(n.endswith(".joblib") for n in noms), "modèle embarqué dans la roue")
    noter("sentiment =" in points, "commande « sentiment » déclarée")
    noter(not any("/tests/" in n or n.startswith("tests/") for n in noms), "pas de tests dans la roue")

    # 3. Journal des versions et étiquette Git
    journal = RACINE / "CHANGELOG.md"
    noter(journal.exists() and f"[{version}]" in journal.read_text(encoding="utf-8"),
          "CHANGELOG.md décrit cette version", f"[{version}]")
    etiquettes = lancer(["git", "tag", "--points-at", "HEAD"], RACINE).stdout.split()
    noter(f"v{version}" in etiquettes, "étiquette Git sur le dernier commit", f"v{version}")

    # 4. Installation dans un environnement neuf, hors des sources
    with tempfile.TemporaryDirectory() as tmp:
        dossier = Path(tmp)
        venv.create(dossier / "env", with_pip=True)
        binaires = dossier / "env" / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaires / ("python.exe" if sys.platform == "win32" else "python")
        r = lancer([str(python), "-m", "pip", "install", "-q", str(roue), "pytest"], dossier)
        if not noter(r.returncode == 0, "installation de la roue dans un environnement neuf",
                     r.stderr.strip().splitlines()[-1] if r.returncode else ""):
            return terminer()
        r = lancer([str(python), "-m", "pytest", "-q", "-p", "no:cacheprovider", str(RACINE / "tests" / "test_paquet.py")], dossier)
        bilan = (r.stdout.strip().splitlines() or ["(aucune sortie)"])[-1]
        noter(r.returncode == 0 and "skipped" not in bilan, "tests lancés sur le paquet installé", bilan)
        commande = binaires / ("sentiment.exe" if sys.platform == "win32" else "sentiment")
        r = lancer([str(commande), "--json", AVIS], dossier)
        erreur = (r.stderr.strip().splitlines() or [""])[-1]   # la dernière ligne d'une trace dit l'essentiel
        noter(r.returncode == 0 and '"label"' in r.stdout, "commande installée", r.stdout.strip() or erreur)
    return terminer()


def terminer() -> int:
    lignes.append(f"Bilan : {'CONFORME' if echecs == 0 else f'{echecs} point(s) non conforme(s)'}")
    print(lignes[-1])
    RAPPORT.parent.mkdir(exist_ok=True)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Rapport : {RAPPORT.relative_to(RACINE)}")
    return 0 if echecs == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
