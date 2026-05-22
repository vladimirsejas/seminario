from src.database import Database


class EpidemiologyService:

    def __init__(self):

        self.database = Database()

    def load_data(self):

        path = "data/epidemiologia/DENGBR24.parquet"

        return self.database.read_parquet(path)

