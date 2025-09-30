import json
import requests

with open('noticias_tratadas.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

i = 0

for noticia in dados:
    arquivos = noticia.pop('arquivos', [])

    novos_arquivos = []

    for arquivo in arquivos:
        nome = arquivo.get('nome')
        url_arquivo = arquivo.get('arquivo').replace('https://vilavalerio.es.gov.br', '')

        try:
            if not url_arquivo.startswith('http'):
                url_arquivo = 'https://vilavalerio.es.gov.br' + url_arquivo

            resposta = requests.get(url_arquivo, timeout=15)

            if resposta.status_code == 200:
                nome_arquivo = f'{i}.pdf'
                with open(nome_arquivo, 'wb') as arquivo_pdf:
                    arquivo_pdf.write(resposta.content)

                print(f"Baixado: {i}.pdf ({nome})")

                novos_arquivos.append({
                    'nome': nome,
                    'arquivo': nome_arquivo
                })
                i += 1
            else:
                print(f'Falha no download: ({url_arquivo}')
                novos_arquivos.append({
                    'nome': nome,
                    'arquivo': url_arquivo
                })

        except Exception as e:
            print(f'Erro ao baixar {url_arquivo}: {e}')
            novos_arquivos.append({
                'nome': nome,
                'arquivo': url_arquivo
            })

    noticia['arquivos'] = novos_arquivos

with open('spiders/noticias_baixadas.json', 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)
