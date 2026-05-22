from pysus.sinan import SINAN


class EpidemiologyService:

    def download_dengue_data(self):

        try:

            print("Conectando ao SINAN...")

            sinan = SINAN()

            print("Baixando dados da dengue...")

            df = sinan.load()

            print("Download concluído.")

            return df

        except Exception as error:

            print(f"Erro: {error}")

            return None


if __name__ == "__main__":

    service = EpidemiologyService()

    df = service.download_dengue_data()

    if df is not None:

        print("\nPrimeiras linhas:")
        print(df.head())

        print("\nColunas:")
        print(df.columns)

        print("\nTotal de registros:")
        print(len(df))