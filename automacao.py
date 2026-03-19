# Passo a passo
# Passo 1: Abrir o navegador
# Passo 2: Carregar a lista de produtos (livros)
# Passo 3: Para cada item da lista (para cada livro)
    # Passo 4: Pesquisar no gutenberg: https://www.gutenberg.org/
    # Passo 5: Se não encontrar:
        # Pesquisar no https://books.toscrape.com/
    # Passo 6: Registrar preço e link do livro na planilha

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

navegador = webdriver.Chrome()

import pandas as pd

df_produtos = pd.read_excel("Produtos.xlsx")
print(df_produtos)

def pesquisar_gutenberg(nome, autor, navegador):
    lista_palavras_autor = autor.split(" ")
    navegador.get("https://www.gutenberg.org/") 

    elemento = navegador.find_element("class name", "search-input")
    elemento.send_keys(nome)
    elemento.send_keys(Keys.ENTER)

    lista_resultados = navegador.find_elements("class name", "booklink")
    link = None
    for resultado in lista_resultados:
        texto = resultado.text
        if nome.lower() in texto.lower():
            if all(palavra in texto for palavra in lista_palavras_autor):  
                link = resultado.find_element("class name", "link").get_attribute("href")
                break
    if link:
        preco = 0
    else:
        preco = None
    return link, preco

def pesquisar_bookstocrape(nome, autor, navegador):
    navegador.get("https://books.toscrape.com/") 
    lista_categorias = navegador.find_element("class name", "nav-list")
    try:
        lista_categorias.find_element("link text", categoria).click()
    except:
        print("Nenhuma categoria selecionada")

    
    link = None
    preco = None
    encontrado = False
    while not encontrado: 
        lista_resultados = navegador.find_elements("class name", "product_pod")
        for resultado in lista_resultados:
            elemento_h3 = resultado.find_element("tag name", "h3")
            elemento_do_link = elemento_h3.find_element("tag name", "a")
            titulo = elemento_do_link.get_attribute("title")
            if nome.lower() in titulo.lower():
                encontrado = True
                link = elemento_do_link.get_attribute("href")
                preco = resultado.find_element("class name", "price_color").text
                break
        try:
            navegador.find_element("link text", "next").click()
        except:
            break
    return link, preco

for linha in df_produtos.index:
    nome = df_produtos.loc[linha, "nome"]
    autor = df_produtos.loc[linha, "autor"]
    categoria = df_produtos.loc[linha, "categoria"]

    link1, preco1 = pesquisar_gutenberg(nome, autor, navegador)
    print(nome, link1, preco1)
    if not link1:
        link2, preco2 = pesquisar_bookstocrape(nome, autor, navegador)
        print(nome, link2, preco2)
        df_produtos.loc[linha, "preco"] = preco2
        df_produtos.loc[linha, "link"] = link2
    else:
        df_produtos.loc[linha, "preco"] = preco1
        df_produtos.loc[linha, "link"] = link1

        nome_novo_arquivo = "Produtos_Atualizados.xlsx"

df_produtos.to_excel(nome_novo_arquivo, index=False)

print(f"Sucesso! Os dados foram salvos em: {nome_novo_arquivo}")

