#Está importando as bibliotecas utilizada para o tratamento
from datetime import datetime as dt
import json
from bs4 import BeautifulSoup as bs

#Abre o arquivo JSON no modo de leitura
with open('vilaValerio.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

    #Cria um loop que percorre cada elemento dentro de 'dados'
    for noticias in dados:
        #Atribuindo valores às variáveis que serão tratadas
        titulo = (noticias.pop('titulo') or '').replace(' ', '')
        texto = (noticias.pop('texto') or '').replace(' ', '')
        data = noticias.pop('data').replace('\r\n', '').strip() #Remove as tags e os espaços extras
        dataAtualizacao = (noticias.pop('dataAtualizacao') or '').replace('\r\n', '').strip()
        imagens = noticias.pop('imagens') or []
        arquivos = noticias.pop('arquivos') or {}

        #Chaves com os valores tratados:
        #Manda o conteúdo para o BeautifulSoup e retorna com os espaços removidos
        noticias['titulo'] = bs(titulo, 'html.parser').get_text(strip=True)
        #Manda para o Datetime a data no formato do JSON e retorna formatada
        noticias['data'] = dt.strptime(data, '%d/%m/%Y %Hh%M').strftime('%Y-%m-%d %H:%M:%S') if data else None
        noticias['dataAtualizacao'] = dt.strptime(dataAtualizacao, '%d/%m/%Y %Hh%M').strftime('%Y-%m-%d %H:%M:%S') if dataAtualizacao else None
        noticias['texto'] = bs(texto, 'html.parser').get_text(strip=True)

        #Crie uma condição para o tratamento das imagens
        if 'data:image' in ' '.join(imagens): #Acessa a lista, juntando todas as strings
            noticias['imagens'] = [] #Se tiver 'data:image' na string retorna []
        else:
            noticias['imagens'] = ['https://vilavalerio.es.gov.br' + img for img in imagens] #Senão retorna a URL da imagem

        #Cria uma lista de dicionários com uma condição para tratar os arquivos
        noticias['arquivos'] = [{
            'nome': arq['nome'].strip(), #Pega o nome e aplica o strip para remover os espaços que estiverem sobrando
            'arquivo': 'https://vilavalerio.es.gov.br' + arq['arquivo'] #Adiciona a URL do site aos arquivos
        } for arq in arquivos #Percorre cada elemento da lista de dicionários 'arquivos'
        if arq.get('nome') and arq['nome'].strip()] #Remove os espaços do nome e verifica se não ficou uma chave vazia.

with open('noticias_tratadas.json', 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)