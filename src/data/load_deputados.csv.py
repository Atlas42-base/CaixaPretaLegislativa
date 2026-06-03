from google.cloud import bigquery
from constants import ROOT, KEY_FILE

path = f"{ROOT}/credentials/{KEY_FILE}"
client = bigquery.Client.from_service_account_json(path)

query = """
SELECT *
FROM `caixapretalegislativa.congresso.deputados`
"""

df = client.query(query).to_dataframe()

print(df.to_csv(index=False))

#SELECT
#  sexo,
#  COUNT(*) AS total
#FROM `caixapretalegislativa.congresso.deputados`
#GROUP BY sexo
#ORDER BY total DESC