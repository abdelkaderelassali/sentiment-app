"""Pont temporaire pour conserver `python src/predict.py` et les anciens imports.

La logique métier se trouve désormais dans sentiment_app.predict.
"""

import sys

import sentiment_app.predict as _implementation

if __name__ == "__main__":
    raise SystemExit(_implementation.main())

# En mode import, les anciens clients obtiennent le module canonique lui-même.
# Cela garde notamment MODELE et le cache modifiables pendant les tests hérités.
sys.modules[__name__] = _implementation
