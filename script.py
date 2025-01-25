import pandas as pd
import requests
from urllib.parse import quote
import re

# Função para verificar se o site existe
def verificar_site(url):
    try:
        print(f"Verificando: {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"Site válido: {url}")
            return True
        else:
            print(f"Site inválido (status {response.status_code}): {url}")
    except requests.RequestException as e:
        print(f"Erro ao verificar {url}: {e}")
    return False

# Função para construir a URL
def construir_url(nome_municipio, uf):
    nome_formatado = re.sub(r'[^a-zA-Z0-9]', '', nome_municipio.lower().replace(" ", ""))
    uf_formatado = uf.lower()
    url = f"https://{nome_formatado}.{uf_formatado}.gov.br"
    print(f"Construída URL: {url}")
    return url

# Ler o arquivo CSV
arquivo_csv = "municipios_ibge.csv"
print(f"Lendo o arquivo: {arquivo_csv}")
dados = pd.read_csv(arquivo_csv)

# Criar uma nova coluna para o site
sites = []
sites_validados = 0

print("Iniciando a validação dos sites...")

for index, row in dados.iterrows():
    nome_municipio = row["mun_nome"]
    uf = row["mun_uf"]
    print(f"Processando município {index + 1}/{len(dados)}: {nome_municipio} ({uf})")
    url = construir_url(nome_municipio, uf)

    if verificar_site(url):
        sites.append(url)
        sites_validados += 1
    else:
        sites.append(None)

# Adicionar a coluna ao DataFrame
dados["site_institucional"] = sites

# Salvar o novo CSV
output_csv = "municipios_com_sites.csv"
print(f"Salvando os resultados no arquivo: {output_csv}")
dados.to_csv(output_csv, index=False)

print("Processo concluído!")
print(f"Total de sites validados: {sites_validados}")

