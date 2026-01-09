"""Punto di ingresso del pacchetto per l'automazione useReq.

Questo file espone metadati leggeri e una riesportazione comoda del punto di ingresso CLI `main`,
cosi i chiamanti possono usare `from usereq import main` senza importare
involontariamente il comportamento completo del pacchetto.
"""

__version__ = "0.0.21"

from .cli import main  # riesportazione del punto di ingresso CLI

__all__ = ["__version__", "main"]
