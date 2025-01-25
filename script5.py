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
        response = requests.head(url, headers=headers, timeout=20, allow_redirects=True)
        if response.status_code in [200, 301, 302]:
            return True
    except requests.RequestException as e:
        print(f"Erro na verificação HEAD para {url}: {e}")
    
    # Se HEAD falhar, tentar com GET
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        if response.status_code in [200, 301, 302]:
            return True
        print(f"GET para {url} retornou status {response.status_code}")
    except requests.RequestException as e:
        print(f"Erro na verificação GET para {url}: {e}")
    
    return False

# Função para gerar a URL com variantes http e https
def generate_url_variants(nome_municipio, uf):
    # Remover acentos e caracteres especiais
    nome_municipio = ''.join(
        c for c in unicodedata.normalize('NFD', nome_municipio)
        if unicodedata.category(c) != 'Mn' and (c.isalnum() or c == ' ')
    )
    uf = uf.lower()

    # Gerar variantes de URL com e sem hifenização
    nome_municipio_hifen = nome_municipio.replace(" ", "-").lower()
    nome_municipio_sem_espaco = nome_municipio.replace(" ", "").lower()

    return [
        f"https://{nome_municipio_hifen}.{uf}.gov.br",
        f"http://{nome_municipio_hifen}.{uf}.gov.br",
        f"https://{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"http://{nome_municipio_sem_espaco}.{uf}.gov.br"
    ]

# Carregar o arquivo CSV
file_path = 'municipios_com_sites.csv'
data = pd.read_csv(file_path)

# Lista para salvar URLs que falharam
failed_urls = []

total_sites_identificados = 0

# Iterar sobre todas as linhas do DataFrame e preencher os sites faltantes
for index, row in data.iterrows():
    if pd.isna(row['site_institucional']):
        nome_municipio = row['mun_nome']
        uf = row['mun_uf']
        print(f"\nProcessando: {nome_municipio} - {uf}")

        # Gerar as variantes de URL
        url_variants = generate_url_variants(nome_municipio, uf)
        valid_url = None

        # Testar cada variante
        for url in url_variants:
            print(f"Testando URL: {url}")
            if is_valid_url(url):
                valid_url = url
                break

        # Salvar a URL válida ou registrar falha
        if valid_url:
            print(f"URL encontrada e válida: {valid_url}")
            data.at[index, 'site_institucional'] = valid_url
            total_sites_identificados += 1
        else:
            print(f"Nenhuma URL válida encontrada para: {nome_municipio}")
            failed_urls.append(f"{nome_municipio} - {uf}")

# Salvar o arquivo atualizado
data.to_csv('municipios_com_sites_atualizado.csv', index=False)
print("\nArquivo atualizado salvo como 'municipios_com_sites_atualizado.csv'")

# Salvar as URLs que falharam para análise posterior
if failed_urls:
    with open('failed_urls.txt', 'w') as f:
        for item in failed_urls:
            f.write(item + "\n")
    print("\nArquivo 'failed_urls.txt' salvo com os municípios que não tiveram URLs validadas.")

# Exibir o total de sites identificados
print(f"\nTotal de sites identificados: {total_sites_identificados}")

