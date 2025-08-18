from enum import Enum


class DaplaRegion(str, Enum):
    """Dapla platforms/regions."""

    DAPLA_LAB = "DAPLA_LAB"
    BIP = "BIP"
    ON_PREM = "ON_PREM"
    CLOUD_RUN = "CLOUD_RUN"


class DaplaEnvironment(str, Enum):
    """Dapla lifecycle environment."""

    PROD = "PROD"
    TEST = "TEST"
    DEV = "DEV"


class DaplaService(str, Enum):
    """Dapla services."""

    DATADOC = "DATADOC"
    JUPYTERLAB = "JUPYTERLAB"
    VS_CODE = "VS_CODE"
    R_STUDIO = "R_STUDIO"
    KILDOMATEN = "KILDOMATEN"
