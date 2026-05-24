import logging
from src.database import Database

logger = logging.getLogger(__name__)

COLUNAS_UTEIS = [
    "DT_NOTIFIC",
    "SG_UF_NOT",
    "ID_MUNICIP",
    "CS_SEXO",
    "NU_IDADE_N",
    "CS_GESTANT",
    "CS_RACA",
    "CLASSI_FIN",
    "EVOLUCAO",
    "HOSPITALIZ",
    "DT_OBITO",
    "MUNICIPIO",
    "UF",
]


class EpidemiologyService:

    def __init__(self):
        self.database = Database()
        self.path = "data/epidemiologia/DENGBR24.parquet"

    def load_data(self):
        logger.info(f"Carregando {len(COLUNAS_UTEIS)} colunas do parquet...")
        return self.database.read_parquet(self.path, columns=COLUNAS_UTEIS)