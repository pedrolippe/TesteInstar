'''
PARSE: metodo responsável por processar a resposta e retornar os dados coletados
// - Acessa todos os nós
./ - Acessa um nó específico
.// - Acessa um nó específico dentro do caminho informado
'''

import scrapy

class VilavalerioSpider(scrapy.Spider):
    name = "vilaValerio"
    allowed_domains = ["vilavalerio.es.gov.br"] #Domínios permitidos
    #Cria uma 'lista' de links e acessa as urls com o valor de 1 a 22.
    start_urls = [f"https://vilavalerio.es.gov.br/Noticias?page={i}" for i in range(1, 23)]

    custom_settings = {
        'USER_AGENTS_LIST': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 Chrome/110.0.5481.65 Mobile Safari/537.36',
        ],
        'DEFAULT_REQUEST_HEADERS': {
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'FEEDS': {
            'links_licitacoes.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            },
        }
    }

    #Função que analisa o conteúdo do site
    def parse(self, response):
        #cria um loop que pega todos os 'href' dentro do elemento 'a', que está na classe 'title-list'
        #O 'getall()' retorna uma lista com os href
        for noticias in response.xpath('//h4[@class="title-list"]/a/@href').getall():
            #Cria uma requisição para o link em 'noticias' e roda o parse para coletar os dados
            yield response.follow(noticias, callback=self.parse_conteudo)

    def parse_conteudo(self, response):
        yield {
            'url': response.url, #Uma condição que retorna a URL da página
            'titulo': response.xpath('//div[@class="col-lg-12"]/h4/text()').get(),
            'data': response.xpath('//div[@class="published"]/text()').get(),
            'dataAtualizacao': response.xpath('//*[@id="layout-content"]/div/div[2]/div/div/div/div/div/div/article/header/div[1]/div/div/div/text()[2]').get(),
            #Pega o conteúdo da div e transforma em uma lista de strings. O join serve para juntar os elementos da lista, separando-os por ' '
            'texto': ' '.join(response.xpath('string(//div[@class="clearfix body-part"])').getall()),
            #Pega todas as imagens dentro de 'article'
            'imagens': response.xpath('//article[@class="col-lg-12 noticia content-item"]//img/@src').getall(),
            #Cria uma lista de dicionários
            'arquivos': [{
                'nome': (arquivo.xpath('string()').get()).replace(' ', ''), #Pega o texto do arquivo e transforma em uma string
                'arquivo': ((arquivo.xpath('./@href').get()) or []).replace('https://vilavalerio.es.gov.br', '') #Se encontrar, pega o arquivo, senão retorna []
            } for arquivo in response.xpath('//div[@class="clearfix body-part"]//a')] #Cria um loop que percorre cada arquivo dentro da div
        }
