import pandas as pd

# Carregar o arquivo CSV
file_path = 'municipios_com_sites_atualizado.csv'  # Substitua pelo caminho do arquivo
data = pd.read_csv(file_path)

# Contar quantos municípios têm o site preenchido
site_preenchido_count = data['site_institucional'].notna().sum()

# Exibir o resultado
print(f"Quantidade de municípios com o site preenchido: {site_preenchido_count}")

