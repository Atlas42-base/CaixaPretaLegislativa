import pandas as pd
import requests

from datetime import datetime
from google.cloud import bigquery
from tqdm import tqdm

from constants import PROJECT_ID

def _load_data_deputados_geral() -> pd.DataFrame:
    """Extrai dados da tabela geral de deputados, disponível em https://dadosabertos.camara.leg.br/api/v2/deputados"""
    
    # LOAD DATA - deputados
    url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
    response = requests.get(url)
    data = response.json()
    df_ = pd.DataFrame(data['dados'])
    
    features_deputado = ['id', 'nome', 'siglaPartido', 'idLegislatura', 'siglaUf'] # all: ['id', 'uri', 'nome', 'siglaPartido', 'uriPartido', 'siglaUf', 'idLegislatura', 'urlFoto', 'email']
    df = df_[features_deputado]

    return df

def _load_data_deputados_individual(lista_ids : list) -> pd.DataFrame:
    """Extrai tabelas individuais de cada deputado a partir dos ids"""

    atributos_individuais_deputados = ['id', 'nomeCivil', 'cpf', 'sexo', 'dataNascimento', 'dataFalecimento', 'ufNascimento', 'municipioNascimento', 'escolaridade']
    # all features: ['id', 'uri', 'nomeCivil', 'ultimoStatus', 'cpf', 'sexo', 'urlWebsite', 'redeSocial', 'dataNascimento', 'dataFalecimento', 'ufNascimento', 'municipioNascimento', 'escolaridade']

    for idx, id_ in enumerate(tqdm(lista_ids)):
    
        try: 
            url_ = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_}"
            response_ = requests.get(url_)
            data_ = response_.json()
            data_slice_ = {k : data_['dados'][k] for k in atributos_individuais_deputados}
            df_ = pd.DataFrame(data_slice_, index=[0])
        
            if idx > 0:
                df_ =  pd.concat([df_prev, df_])
            
            df_prev = df_
        
        except:
            continue

    df = df_.reset_index(drop=True)

    return df

def merge_data() -> pd.DataFrame:

    df_geral = _load_data_deputados_geral()
    ids_deputados = df_geral["id"].unique()

    df_individual = _load_data_deputados_individual(ids_deputados)

    df_completo = pd.merge(df_geral,
                            df_individual,
                            on='id',
                            how='outer')
    
    # EDIT
    df_completo["dataNascimento"] = pd.to_datetime(df_completo["dataNascimento"], errors="coerce")
    df_completo["dataFalecimento"] = pd.to_datetime(df_completo["dataFalecimento"], errors="coerce")

    return df_completo


if __name__ == "__main__":

    df_completo = merge_data()

    client = bigquery.Client(
        project=PROJECT_ID
    )

    table_id = (
        f"{PROJECT_ID}.congresso.deputados"
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job = client.load_table_from_dataframe(
        df_completo,
        table_id,
        job_config=job_config
    )

    job.result()

    print("Upload concluído")