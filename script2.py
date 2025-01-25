import pandas as pd
import requests
import unicodedata

# Função para verificar se uma URL é válida
def is_valid_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # Tentar com HEAD primeiro
        response = requests.head(url, headers=headers, timeout=10)
        if response.status_code in [200, 301, 302]:
            return True
    except requests.RequestException:
        pass
    
    # Se HEAD falhar, tentar com GET
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code in [200, 301, 302]
    except requests.RequestException:
        return False

# Função para gerar a URL com base na regra proposta
def generate_url(nome_municipio, uf):
    # Remover acentos e caracteres especiais
    nome_municipio = ''.join(
        c for c in unicodedata.normalize('NFD', nome_municipio)
        if unicodedata.category(c) != 'Mn' and (c.isalnum() or c == ' ')
    )
    # Substituir espaços por "-" e deixar em minúsculas
    nome_municipio = nome_municipio.replace(" ", "-").lower()
    uf = uf.lower()
    # Gerar a URL
    return f"https://{nome_municipio}.{uf}.gov.br"

# Carregar o arquivo CSV
file_path = 'municipios_com_sites.csv'
data = pd.read_csv(file_path)

# Iterar sobre todas as linhas do DataFrame e preencher os sites faltantes
for index, row in data.iterrows():
    if pd.isna(row['site_institucional']):
        nome_municipio = row['mun_nome']
        uf = row['mun_uf']
        print(f"\nProcessando: {nome_municipio} - {uf}")

        # Gerar a URL com base na regra
        generated_url = generate_url(nome_municipio, uf)
        print(f"URL gerada: {generated_url}")

        # Verificar se a URL é válida
        if is_valid_url(generated_url):
            print(f"URL encontrada e válida: {generated_url}")
            data.at[index, 'site_institucional'] = generated_url
        else:
            print(f"URL gerada não é válida: {generated_url}")

# Salvar o arquivo atualizado
data.to_csv('municipios_com_sites_atualizado.csv', index=False)
print("\nArquivo atualizado salvo como 'municipios_com_sites_atualizado.csv'")

