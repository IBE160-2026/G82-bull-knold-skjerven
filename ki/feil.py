"""Feilen `ki` hever. Kodene er de samme som i AD-10."""

KODER = frozenset(
    {"timeout", "format", "for_lite_innhold", "for_stor", "api_nokkel", "api_feil"}
)


class KIFeil(Exception):
    """Feil fra `ki`. `kode` er én av `KODER`. `detalj` er for logg, aldri filinnhold."""

    def __init__(self, kode, detalj=""):
        if kode not in KODER:
            raise ValueError(f"Ukjent feilkode for KIFeil: {kode!r}")
        self.kode = kode
        self.detalj = detalj
        super().__init__(f"{kode}: {detalj}" if detalj else kode)
