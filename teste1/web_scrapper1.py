import os
import pkg_resources

required = {'numpy', 'selenium', 'pandas', 'requests', 'fake_useragent'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
for pkg in missing:
    os.system(f'pip install {pkg}')


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import pandas as pd
import time

class WebScrapper():
    def __init__(self) -> None:
        self.list_inscricao = []
        self.list_identificacao = []
        self.list_tipo_pessoa = []
        self.list_situacao = []
        self.list_certidao_regularidade = []
        self.list_contato = []
        self.driver = None
        self.continua = True
        
        self.chrome_options = Options()
        self.chrome_options.add_argument("window-size=1920,1080")

    def iniciar(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get("https://www.crecisc.conselho.net.br/form_pesquisa_cadastro_geral_site.php")

        ''' Inserir Florianopolis no formulario '''
        input_cidade = self.driver.find_element(By.ID, "input-24")
        input_cidade.send_keys("Florianópolis")

        time.sleep(2)
        ''' Aperta o botão "Pesquisar" '''
        button_pesquisar = self.driver.find_element(By.XPATH, value="//div[3]/button")
        button_pesquisar.click()

        time.sleep(5)
        ''' Pegar conteudo da página '''
        self.content = self.driver.page_source

        self.monta_dados()
        self.monta_csv()

    def get_linha_tabela(self, tabela): 
       for row in tabela.find_elements(By.XPATH, value=".//tr"):
            yield [item for item in row.find_elements(By.XPATH, value=".//td")]

    def passa_pagina(self):
        button_passa_pagina = self.driver.find_element(By.XPATH, value=".//div[4]/button")
        if button_passa_pagina.get_attribute('disabled'):
            self.continua = False
        else:
            button_passa_pagina.click()

    def monta_dados(self):   
        ''' Iterar sobre a tabela'''
        while self.continua == True:
            for tabela in self.driver.find_elements(By.XPATH, value="//table/tbody"): #Percorrer as linhas e atribuir valores as listas
                for data in self.get_linha_tabela(tabela):
                    if data != []:
                        inscricao = data[0].text
                        identificacao = data[1].find_element(By.XPATH, value="//td[2]/div/div[2]/div[1]").text
                        tipo_pessoa = data[1].find_element(By.XPATH, value="//td[2]/div/div[2]/div[2]").text
                        situacao = data[2].text
                        certidao = data[3].text
                        contato = data[4].text
                        
                        self.list_inscricao.append(inscricao)
                        self.list_identificacao.append(identificacao)
                        self.list_tipo_pessoa.append(tipo_pessoa)
                        self.list_situacao.append(situacao)
                        self.list_certidao_regularidade.append(certidao)
                        self.list_contato.append(contato)
                    else:
                        break
                break
            self.passa_pagina()

        self.driver.close()
        self.driver.quit()

    def monta_csv(self):
        df = pd.DataFrame({'Inscrições':self.list_inscricao,'Identificação':self.list_identificacao,'Tipo Pessoa':self.list_tipo_pessoa,'Situação':self.list_situacao,'Certidão':self.list_certidao_regularidade,'Contato':self.list_contato}) 
        df.to_csv('cadastros.csv', index=False, encoding='utf-8')

if __name__ == '__main__':
    scrapper = WebScrapper()
    scrapper.iniciar()