import logging
import pandas as pd

logger = logging.getLogger(__name__)


class RiskEngine:

    # Colunas confirmadas no DENGBR24.parquet
    COL_UF        = "SG_UF_NOT"
    COL_MUNICIPIO = "ID_MUNICIP"
    COL_DATA      = "DT_NOTIFIC"
    COL_SEXO      = "CS_SEXO"
    COL_IDADE     = "NU_IDADE_N"
    COL_EVOLUCAO  = "EVOLUCAO"
    COL_CLASSI    = "CLASSI_FIN"

    def data_quality_report(self, df):
        try:
            total = len(df)
            report = {
                "total_registros": total,
                "total_colunas": len(df.columns),
                "duplicatas": int(df.duplicated().sum()),
                "nulos_por_coluna": df.isnull().sum().to_dict(),
            }
            logger.info("Relatório de qualidade gerado.")
            return report
        except Exception as e:
            logger.error(f"Erro em data_quality_report: {e}")
            return None

    def top_cities(self, df, n=10):
        try:
            result = (
                df.groupby(self.COL_MUNICIPIO)
                  .size()
                  .sort_values(ascending=False)
                  .head(n)
                  .reset_index()
            )
            result.columns = ["municipio", "casos"]
            return result
        except Exception as e:
            logger.error(f"Erro em top_cities: {e}")
            return None

    def top_states(self, df, n=27):
        try:
            result = (
                df.groupby(self.COL_UF)
                  .size()
                  .sort_values(ascending=False)
                  .head(n)
                  .reset_index()
            )
            result.columns = ["estado", "casos"]
            return result
        except Exception as e:
            logger.error(f"Erro em top_states: {e}")
            return None

    def temporal_evolution(self, df):
        try:
            df = df.copy()
            df["mes"] = df[self.COL_DATA].astype(str).str[:6]  # YYYYMM
            result = (
                df.groupby("mes")
                  .size()
                  .reset_index()
                  .sort_values("mes")
            )
            result.columns = ["mes", "casos"]
            return result
        except Exception as e:
            logger.error(f"Erro em temporal_evolution: {e}")
            return None

    def cases_by_sex(self, df):
        try:
            result = (
                df.groupby(self.COL_SEXO)
                  .size()
                  .reset_index()
            )
            result.columns = ["sexo", "casos"]
            return result
        except Exception as e:
            logger.error(f"Erro em cases_by_sex: {e}")
            return None

    def cases_by_age_group(self, df):
        try:
            df = df.copy()
            df["idade_anos"] = df[self.COL_IDADE].astype(str).apply(self._parse_idade)
            bins   = [0, 10, 20, 30, 40, 50, 60, 70, 200]
            labels = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"]
            df["faixa_etaria"] = pd.cut(df["idade_anos"], bins=bins, labels=labels, right=False)
            result = (
                df.groupby("faixa_etaria", observed=True)
                  .size()
                  .reset_index()
            )
            result.columns = ["faixa_etaria", "casos"]
            return result
        except Exception as e:
            logger.error(f"Erro em cases_by_age_group: {e}")
            return None

    def deaths_by_state(self, df):
        try:
            obitos = df[df[self.COL_EVOLUCAO].astype(str).isin(["2", "3"])]
            result = (
                obitos.groupby(self.COL_UF)
                      .size()
                      .sort_values(ascending=False)
                      .reset_index()
            )
            result.columns = ["estado", "obitos"]
            return result
        except Exception as e:
            logger.error(f"Erro em deaths_by_state: {e}")
            return None

    def classification_summary(self, df):
        try:
            result = (
                df.groupby(self.COL_CLASSI)
                  .size()
                  .sort_values(ascending=False)
                  .reset_index()
            )
            result.columns = ["classificacao", "casos"]
            return result
        except Exception as e:
            logger.error(f"Erro em classification_summary: {e}")
            return None

    def _parse_idade(self, valor):
        try:
            s = str(int(float(valor)))
            unidade = int(s[0])
            num = int(s[1:])
            if unidade == 1:
                return num
            elif unidade == 2:
                return num / 12
            else:
                return 0
        except Exception:
            return None