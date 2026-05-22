from src.epidemiology_service import EpidemiologyService


service = EpidemiologyService()

df = service.load_data()

print(df.head())

print(df.columns)

print(len(df))