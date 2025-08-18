"""Constants used in validate ssb name standard."""

from dapla_metadata.datasets.dataset_parser import SUPPORTED_DATASET_FILE_SUFFIXES

SUCCESS = "Suksess"

NAME_STANDARD_SUCCESS = "Filene dine er i samsvar med SSB-navnestandarden"

NAME_STANDARD_VIOLATION = "Det er oppdaget brudd på SSB-navnestandard:"

MISSING_BUCKET_NAME = "Filnavn mangler bøttenavn ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_VERSION = "Filnavn mangler versjon, hvis ikke filen er nyeste versjon kan dette være brudd på navnestandarden ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#versjonering-av-datasett"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_DATA_STATE = "Mappe for datatilstand mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_DATASET_SHORT_NAME = "Filnavn mangler datasett kortnavn ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"

INVALID_SYMBOLS = "Filnavn inneholder ulovlige tegn ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"

PATH_IGNORED = "Ignorert, mappen er ikke underlagt krav til navnestandard."
FILE_IGNORED = f"Ignorert, kun datasett med {', '.join(SUPPORTED_DATASET_FILE_SUFFIXES.keys())} filendelser valideres foreløpig."

FILE_DOES_NOT_EXIST = "Filen eksisterer ikke. Validerer uansett."

BUCKET_NAME_UNKNOWN = "Kan ikke validere bøttenavn"

SSB_NAMING_STANDARD_REPORT = "SSB navnestandard rapport"
SSB_NAMING_STANDARD_REPORT_SUCCESS_RATE = "Suksess rate"
SSB_NAMING_STANDARD_REPORT_RESULT_BEST = "🚀 Fantastisk! 🎉\n"
SSB_NAMING_STANDARD_REPORT_RESULT_GOOD = (
    "✅ Bra jobba! Fortsatt litt rom for forbedring. 😊\n"
)
SSB_NAMING_STANDARD_REPORT_RESULT_AVERAGE = (
    "⚠️ Ikke verst! Men det er noen feil å fikse. 🔧\n"
)
SSB_NAMING_STANDARD_REPORT_RESULT_LOW = "❌ Mye å forbedre! Ta en grundig sjekk. 🛠️\n"
SSB_NAMING_STANDARD_REPORT_RESULT_NO_SCORE = "👀 Ingen filer ble validert\n"
SSB_NAMING_STANDARD_REPORT_FILES = "Antall filer validert"
SSB_NAMING_STANDARD_REPORT_SUCCESS = "Antall filer som følger SSB navnestandard"
SSB_NAMING_STANDARD_REPORT_VIOLATIONS = "Antall filer som bryter SSB navnestandard"

IGNORED_FOLDERS = [
    "temp",
    "oppdrag",
    "konfigurasjon",
    "logg",
    "tidsserier",
    "migrert",
]
