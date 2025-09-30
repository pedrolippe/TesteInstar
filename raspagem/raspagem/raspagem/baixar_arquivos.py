import json
import requests

with open('noticias_tratadas.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

i = 0 #Cria um variável a qual estará no nome dos arquivos para evitar repetição

for noticia in dados:
    arquivos = noticia.pop('arquivos', []) #Pega a lista de dicionários 'arquivos'
    imagens = noticia.pop('imagens', []) #Pega a lista 'imagens'

    novas_imagens = [] #Cria uma nova lista para organizar as imagens
    novos_arquivos = [] #Cria uma nova lista para organizar os arquivos

    #DOWNLOAD DAS IMAGENS:
    for img in imagens: #Cria uma condição para cada imagem de forma individual
        try:
            resposta = requests.get(img, timeout=15) #Tenta acessar o link da imagem com tempo máximo de espera de 15segundos

            if resposta.status_code == 200: #Se a requisição for bem-sucedida:
                nome_imagem = f'img{i}.jpg' #Cria um nome para a imagem
                with open(nome_imagem, 'wb') as imagem: #Abre a variável no modo de escrita
                    imagem.write(resposta.content) #Armazena na variável o conteúdo obtido da imagem

                print(f'Baixado: {nome_imagem} ({img})') #Mostra a imagem baixada e sua URL
                novas_imagens.append(nome_imagem) #A lista de imagens recebe o nome do arquivo da imagem
                i += 1 #A variável 'i' recebe +1
            else: #Caso não seja bem-sucedida:
                print(f'Falha no download: {img}') #Mostra a url da imagem que deu erro
                novas_imagens.append(img) #A lista de imagens armazena a url da imagem

        except Exception as e: #Caso surja qualquer erro:
            print(f'Erro ao baixar imagem {img}: {e}') #Mostra a url da imagem e o erro de download
            novas_imagens.append(img) #A lista de imagens armazena a url da imagem

    # Download dos arquivos:
    for arquivo in arquivos: #Cria uma condição para baixar cada arquivo de forma individual
        nome = arquivo.get('nome')
        url_arquivo = arquivo.get('arquivo').replace('https://vilavalerio.es.gov.br', '') #Armazena a url do arquivo em uma variável

        try: #Cria uma condição de tentativa:
            if not url_arquivo.startswith('http'): #Se a url não começar com 'http':
                url_arquivo = 'https://vilavalerio.es.gov.br' + url_arquivo #Adiciona a url da prefeitura à url relativa

            resposta = requests.get(url_arquivo, timeout=15) #Faz uma requisição que pega o conteúdo da url do arquivo

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

    noticia['imagens'] = novas_imagens
    noticia['arquivos'] = novos_arquivos

with open('spiders/noticias_baixadas.json', 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)
