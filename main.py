import json
from time import sleep


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def scrapping_mercado_livre_ofertas(paginas=None, producao=False):
    """

    :param paginas: N° de paginas consultadas. Se não informado, e
    producao =True, então paginas = 20
    :param producao: Se esta em producao
    :return:
    """
    # Configurações globais
    produtos = []
    options = Options()
    options.add_argument('window-size=400,800')
    options.add_argument('--headless')
    if producao:
        if paginas:
            n = paginas
        else:
            n = 20
    else:
        n = paginas

    # Inicializa o webdriver
    navegador = webdriver.Firefox(options=options)

    try:
        for pagina in range(1, n+1):
            print(f'[LOG]: Página de oferta sendo consultada: {pagina}')

            navegador.get(f'https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-1&page={pagina}')
            sleep(1)  # Espera a página carregar
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')

            ofertas_ol = site.find('ol', attrs={'class': 'items_container'})
            ofertas_li = ofertas_ol.findAll('li')

            for idx, item in enumerate(ofertas_li):
                link_prod = item.find('a', attrs={'class': 'promotion-item__link-container'})['href']
                nome_prod = item.find('p', attrs={'class': 'promotion-item__title'}).text

                vl_antigo_prod = item.find('s', attrs={'class': 'andes-money-amount andes-money-amount-combo__previous-value andes-money-amount--previous andes-money-amount--cents-comma'})
                vl_atual_prod_texto = item.find(
                    'span', attrs={'class': 'andes-money-amount__fraction'}).text
                vl_atual_prod_texto = vl_atual_prod_texto.replace('.', '')
                vl_atual_prod_centavos = item.find(
                    'span',
                    attrs={'class': 'andes-money-amount__cents andes-money-amount__cents--superscript-24'})
                if vl_atual_prod_centavos:
                    vl_atual_prod_centavos = vl_atual_prod_centavos.text
                    vl_atual_prod_real = vl_atual_prod_texto+'.'+ vl_atual_prod_centavos
                    vl_atual_prod_real = float(vl_atual_prod_real)
                else:
                    vl_atual_prod_real = float(vl_atual_prod_texto)



                if vl_antigo_prod:
                    vl_antigo_prod = vl_antigo_prod.text
                    vl_antigo_prod = int(vl_antigo_prod[7:vl_antigo_prod.find('reais')].replace('.', ''))
                    descont_prod = 1 - (vl_atual_prod_real / vl_antigo_prod)
                    descont_prod = round(descont_prod, 2)
                else:
                    descont_prod = None

                loja_prod = item.find('span', attrs={'class': 'promotion-item__seller'})
                if loja_prod:
                    loja_prod = loja_prod.text[4:]

                produto = {
                    'link_prod': link_prod,
                    'nome_prod': nome_prod,
                    'vl_antigo_prod': vl_antigo_prod,
                    'vl_atual_prod_real': vl_atual_prod_real,
                    'descont_prod': descont_prod,
                    'loja_prod': loja_prod,
                    'n_pagina_oferta': pagina,
                }
                produtos.append(produto)

        with open('output/ofertas.json', 'w') as json_file:
            json.dump(produtos, json_file)

    finally:
        navegador.quit()
        print(f'Total de produtos captados: {len(produtos)}')

if __name__ == '__main__':
    scrapping_mercado_livre_ofertas(producao=True)

