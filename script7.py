import pandas as pd
import requests
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

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

# Função para gerar a URL com variantes http, https, "www" e tratamento especial para cidades compostas
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
    nome_municipio_primeiro_nome = nome_municipio.split(" ")[0].lower()  # Apenas o primeiro nome

    return [
        # URLs padrão
        f"https://{nome_municipio_hifen}.{uf}.gov.br",
        f"http://{nome_municipio_hifen}.{uf}.gov.br",
        f"https://{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"http://{nome_municipio_sem_espaco}.{uf}.gov.br",
        # URLs com "www"
        f"https://www.{nome_municipio_hifen}.{uf}.gov.br",
        f"http://www.{nome_municipio_hifen}.{uf}.gov.br",
        f"https://www.{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"http://www.{nome_municipio_sem_espaco}.{uf}.gov.br",
        # URLs com apenas o primeiro nome
        f"https://www.{nome_municipio_primeiro_nome}.{uf}.gov.br",
        f"http://www.{nome_municipio_primeiro_nome}.{uf}.gov.br",
        # URLs de transparência
        f"https://transparencia.{nome_municipio_hifen}.{uf}.gov.br",
        f"http://transparencia.{nome_municipio_hifen}.{uf}.gov.br",
        f"https://transparencia.{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"http://transparencia.{nome_municipio_sem_espaco}.{uf}.gov.br",
        # URLs de prefeitura
        f"https://prefeitura{nome_municipio_hifen}.{uf}.gov.br",
        f"http://prefeitura{nome_municipio_hifen}.{uf}.gov.br",
        f"https://prefeitura{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"http://prefeitura{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"https://prefeiturade{nome_municipio_hifen}.{uf}.gov.br",
        f"http://prefeiturade{nome_municipio_hifen}.{uf}.gov.br",
        f"https://prefeiturade{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"http://prefeiturade{nome_municipio_sem_espaco}.{uf}.gov.br",
        # URLs de transparência com "www"
        f"https://www.transparencia.{nome_municipio_hifen}.{uf}.gov.br",
        f"http://www.transparencia.{nome_municipio_hifen}.{uf}.gov.br",
        f"https://www.transparencia.{nome_municipio_sem_espaco}.{uf}.gov.br",
        f"http://www.transparencia.{nome_municipio_sem_espaco}.{uf}.gov.br",
    ]

# Função para buscar a URL pelo navegador caso todas as outras tentativas falhem
def search_with_browser(nome_municipio, uf):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executar em segundo plano
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        search_query = f"site prefeitura {nome_municipio} {uf}"
        print(f"\nBuscando no navegador: {search_query}")
        driver.get('https://www.mojeek.com/')

        # Localizar a barra de pesquisa e realizar a busca
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)  # Esperar carregar os resultados

        # Capturar o primeiro link nos resultados
        results = driver.find_elements(By.CSS_SELECTOR, 'a.result-link')
        if results:
            first_url = results[0].get_attribute('href')
            print(f"Primeiro link encontrado: {first_url}")
            return first_url
        else:
            print("Nenhum link encontrado nos resultados da pesquisa.")
    except Exception as e:
        print(f"Erro ao buscar com navegador: {e}")
    finally:
        driver.quit()

    return None

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

        # Tentar com o navegador se nenhuma URL for válida
        if not valid_url:
            valid_url = search_with_browser(nome_municipio, uf)

        # Salvar a URL válida ou registrar falha
        if valid_url and is_valid_url(valid_url):
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

