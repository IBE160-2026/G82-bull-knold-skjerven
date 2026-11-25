# Kilder for testdokumentene

Alle testdokumentene er korte forelesningsnotater om webutvikling, skrevet av
gruppa selv. Teksten står i `scripts/lag_testdokumenter.py`, og skriptet lager
filene:

    uv run --with reportlab==5.1.1 --with pillow==13.0.0 scripts/lag_testdokumenter.py

Endres en fil, endres hashen, og mock-svarene fra story 2.2 må lages på nytt.

| Fil | Type | Språk | Kilde | Lisens |
|-----|------|-------|-------|--------|
| `html-struktur-og-semantikk.pdf` | Tekst-PDF, 10 sider | norsk bokmål | laget av gruppa G82 | CC BY 4.0 |
| `css-layout-lysbilder.pdf` | Lysbilde-PDF, 11 liggende sider med lite tekst | norsk bokmål | laget av gruppa G82 | CC BY 4.0 |
| `http-skannet.pdf` | Skannet PDF, 2 sider, bare bilder uten tekstlag | norsk bokmål | laget av gruppa G82 | CC BY 4.0 |
| `universell-utforming.docx` | DOCX | norsk bokmål | laget av gruppa G82 | CC BY 4.0 |
| `javascript-og-dom.txt` | TXT, UTF-8 | engelsk | laget av gruppa G82 | CC BY 4.0 |

Den skannede PDF-en er simulert: skriptet tegner sidene som bilder med litt
skråstilling, grått papir og støy. Den kan byttes med en ekte skanning senere.

Fontene i den skannede PDF-en er Bitstream Vera, som følger med reportlab
(Bitstream Vera-lisensen). Bare bildene av teksten ligger i filen, ikke selve
fonten.

CC BY 4.0: <https://creativecommons.org/licenses/by/4.0/deed.no>
