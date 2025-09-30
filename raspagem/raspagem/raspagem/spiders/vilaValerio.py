'''
// - Procura o elemento em todas as chaves da estrutura, ou seja, qualquer lugar do documento
./ - Acessa um elemento específico dentro do nó
.// - Procura o elemento dentro do nó atual, ou seja, do ponto em que você está

yield - é um retorno de chamada
def - função
parse - é chamado para manipular a resposta baixada por cada uma das requisições feitas
response.follow - basicamente cria uma solicitação
callback - busca a URL fornecida e a analisa
'''

import scrapy

class VilavalerioSpider(scrapy.Spider):
    name = "vilaValerio"
    allowed_domains = ["vilavalerio.es.gov.br"] #Domínios permitidos
    #Cria uma 'lista' de links e acessa as urls com o valor de 1 a 22.
    start_urls = [f"https://vilavalerio.es.gov.br/Noticias?page={i}" for i in range(1, 23)]

    custom_settings = {
        'USER_AGENTS_LIST': [ #Cria agentes que simulam o acesso de outro computador/navegador, evitando bloqueio
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 Chrome/110.0.5481.65 Mobile Safari/537.36',
        ],
        'DEFAULT_REQUEST_HEADERS': { #Cabeçalhos padrão
            'Accept-Language': 'pt-BR,pt;q=0.9', #Linguagem aceita (Português)
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', #Conteúdo aceito. Aceita prioritariamente elementos html e xhtml
        },
        'DOWNLOAD_DELAY': 1, #Cria um delay de um segundo entre um requisição e outra
        'RANDOMIZE_DOWNLOAD_DELAY': True, #Cria um atraso aleatório entre as requisições
        'AUTOTHROTTLE_ENABLED': True, #Ajusta automaticamente a velocidade das requisições
        'RETRY_ENABLED': True, #Caso ocorra algum erro, tenta novamente
        'RETRY_TIMES': 5, #Máximo de 5 tentativas
        'FEEDS': { #Cria parámetros para a criação do JSON
            'links_licitacoes.json': {
                'format': 'json', #Formato do arquivo
                'encoding': 'utf8', #Codificação do JSON (UTF-8)
                'overwrite': True, #Sobrescreve o JSON a cada execução
            },
        }
    }

    #Cria uma função que retorna as respostas baixadas do conteúdo do site
    def parse(self, response):
        #cria um loop que pega todos os 'href' dentro do elemento 'a', que está na classe 'title-list'
        #O 'getall()' retorna uma lista com os href
        for noticias in response.xpath('//h4[@class="title-list"]/a/@href').getall():
            #Retorna o que foi o que foi encontrado na solicitação feita para 'noticias'
            yield response.follow(noticias, callback=self.parse_conteudo)

    #Cria uma função que retorna as respostas baixadas dentro do conteúdo da notícia
    def parse_conteudo(self, response):
        #Retorna os elementos informados
        yield {
            'url': response.url, #Retorna a URL da página
            'titulo': response.xpath('//div[@class="col-lg-12"]/h4/text()').get(),
            'data': response.xpath('//div[@class="published"]/text()').get(),
            'dataAtualizacao': response.xpath('//*[@id="layout-content"]/div/div[2]/div/div/div/div/div/div/article/header/div[1]/div/div/div/text()[2]').get(),
            #Pega o conteúdo da div e concatena em uma única string. O join serve para não deixar em uma lista e facilitar o tratamento
            'texto': ' '.join(response.xpath('string(//div[@class="clearfix body-part"])').getall()),
            #Pega todas as imagens dentro de 'article'
            'imagens': response.xpath('//article[@class="col-lg-12 noticia content-item"]//img/@src').getall(),
            #Cria uma lista de dicionários
            'arquivos': [{
                'nome': (arquivo.xpath('string()').get()).replace(' ', ''), #Pega o texto do arquivo e transforma em uma string
                'arquivo': ((arquivo.xpath('./@href').get()) or []).replace('https://vilavalerio.es.gov.br', '') #Se encontrar, pega o arquivo, senão retorna []
            } for arquivo in response.xpath('//div[@class="clearfix body-part"]//a')] #Cria um loop que percorre cada arquivo dentro da div
        }
