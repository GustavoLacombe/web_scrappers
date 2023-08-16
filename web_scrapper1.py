from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

list_inscricao = []
list_identificacao = []
list_tipo_pessoa = []
list_situacao = []
list_certidao_regularidade = []
list_contato = []

continua = True

driver = webdriver.Chrome()
driver.get("https://www.crecisc.conselho.net.br/form_pesquisa_cadastro_geral_site.php")


''' Inserir Florianopolis no formulario '''
input_cidade = driver.find_element(By.ID, "input-24")
input_cidade.send_keys("Florianópolis")

time.sleep(2)
''' Aperta o botão "Pesquisar" '''
button_pesquisar = driver.find_element(By.XPATH, value="//div[3]/button")
button_pesquisar.click()

time.sleep(5)

''' Pegar conteudo da página '''
content = driver.page_source
soup = BeautifulSoup(content, features="html5lib")


''' Iterar sobre a tabela'''

def get_row_data(tabela): #Pegar linhas da tabela
   for row in tabela.find_elements_by_xpath(".//tr"):
        return [item.text for item in row.find_elements(By.XPATH, value=".//td")]

#while continua == True:
for tabela in driver.find_elements(By.XPATH, value="//table"): #Percorrer as linhas e atribuir valores as listas
    for data in get_row_data(tabela):
        inscricao = data[0]
        list_inscricao.append(inscricao)

#    button_passa_pagina = driver.find_element(By.XPATH, value="//div[4]/button")
#    button_passa_pagina.click()

        
print(list_inscricao)
driver.quit()
'''
for a in soup.findAll('a',href=True, attrs={'class':'_31qSD5'}):
    inscricao=a.find('div', attrs={'class':'primary--text'})
    identificacao=a.find('div', attrs={'class':'v-list-item-title'}) 
    tipo_pessoa=a.find('div', attrs={'class':'v-chup__content'})
    situacao=a.find('div', attrs={'class':'_3wU53n'})
    certidao_regularidade=a.find('div', attrs={'class':'_1vC4OE _2rQ-NK'})
    contato=a.find('div', attrs={'class':'hGSR34 _2beYZw'})

    inscricao.append(inscricao.text)
    identificacao.append(identificacao.text)
    tipo_pessoa.append(tipo_pessoa.text) 
    situacao.append(situacao.text)
    certidao_regularidade.append(certidao_regularidade.text)
    contato.append(contato.text) 

df = pd.DataFrame({'Inscrições':inscricao,'Identificação':identificacao,'Tipo Pessoa':tipo_pessoa,'Situação':situacao,'Certidão':certidao_regularidade,'Contato':contato}) 
df.to_csv('cadastros_crecisc.csv', index=False, encoding='utf-8')'''