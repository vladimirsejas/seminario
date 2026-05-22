import pysus

print("Baixando dados da dengue 2024...")

df = pysus.sinan(
    disease='DENG',
    year=2024
)

print("\nDOWNLOAD CONCLUÍDO")

print("\nPRIMEIRAS LINHAS:")
print(df.head())

print("\nCOLUNAS:")
print(df.columns)

print("\nTOTAL DE LINHAS:")
print(len(df))