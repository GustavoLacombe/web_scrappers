import os
import pkg_resources
import subprocess
import json
import platform

required = {'numpy', 'selenium', 'pandas', 'requests', 'fake_useragent'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
for pkg in missing:
    os.system(f'pip install {pkg}')


import requests
import numpy as np
from io import BytesIO
from scipy.io import wavfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import time
import csv


class WebScrapper():
    def __init__(self) -> None:
        self.list_cpf = []        
        self.list_data_nascimento = []
        self.list_situacao_cadastral = []
        self.list_data_inscricao = []
        self.list_digito_verificador = []
        self.list_ano_obito = []
        self.list_data_hora_consulta = []
        self.filename = 'cpfs_consulta.csv'
        
        self.URLwave = 'https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/captcha/gerarSom.asp'
        self.URLmain = 'https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublicaSonoro.asp'
        self.INPUTCaptcha = 'txtTexto_captcha_serpro_gov_br'
        self.DIVContent = 'mainComp'
        self.BTSearch = 'id_submit'
        self.header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}

        self.driver = None
        self.continua = True
        
        self.chrome_options = Options()
        self.chrome_options.add_argument("window-size=1920,1080")

        with open('data/digits.json') as f:
            self.digitsData = json.load(f)

        if platform.system() == 'Darwin':
            self.copy_keyword = 'pbcopy'
        elif platform.system() == 'Windows':
            self.copy_keyword = 'clip'

    def iniciar(self):
        first_time = True
        while self.continua == True:
            with open(self.filename, 'r') as csvfile:
                datareader = csv.reader(csvfile)
                for row in datareader:
                    if first_time:
                        first_time = False
                    else:
                        cpf = row[0]
                        data = row[1]
                        self.get(cpf, data)
                        self.monta_dados(row)
            break
        self.driver.close()    
        self.driver.quit()
        
    def monta_dados(self, row):   
        cpf = row[0]
        data_nascimento = row[1]
        self.list_cpf.append(cpf)
        self.list_data_nascimento.append(data_nascimento)
            
    def _download_wave(self, first_try = True):
        if first_try:
            time.sleep(2)

        cookie_dict = {}
        for cookie in self.driver.get_cookies():
            cookie_dict[cookie['name']] = cookie['value']

        header = self.header

        r = requests.get(self.URLwave, cookies= cookie_dict, headers = header)
        
        if r.content == b'':
            if not first_try:
                print('Error: Failed to download wave file, please reload the page!')
                self.driver.refresh()
                time.sleep(1)
                self._download_wave(first_try=True)
            else:
                time.sleep(1)
                r = requests.get(self.URLwave, cookies= cookie_dict, headers = header)
                if r.content == b'':
                    self._download_wave(first_try=False)

        else:
            self.wave_rate, self.wave_data = wavfile.read(BytesIO(r.content))
            return True

    def _remove_noise(self, data, acc = .4, steps = 500):
        x = data.copy()
        last = 0
        for idx in range(steps, len(x), steps):
            dist = len(set(x[last:idx])) / len(x[last:idx])
            if dist > acc and dist < .91:
                x[last:idx] = self._remove_noise(x[last:idx], steps = int(steps/2))
            if dist < acc:
                x[last:idx] = 0
            last = idx
        return x

    def _find_letters(self, x, limit = 100):
        letters = []
        letter = False
        zeros = 0
        for idx, value in enumerate(x):
            if value != 0 and letter == False:
                start = idx
                letter = True
                zeros = 0
            elif value == 0 and letter:
                zeros += 1

            if (zeros > limit and letter) or (idx == len(x)-1):
                if (idx-limit) - start >= 2000:
                    letters.append(x[start:idx-limit])
                letter = False

        return letters

    def _solve_captcha(self):
        new_data = self._remove_noise(self.wave_data)
        limit = 100
        ar_letters = 'letters'
        while len(ar_letters) > 6:
            limit += 50
            ar_letters = self._find_letters(new_data, limit = limit)

        r = ''
        for letter in ar_letters:
            maxs = sorted(letter, reverse=True)[:100]
            mins = sorted(letter)[:100]

            for key, values in self.digitsData.items():
                if (np.std(np.array(values['maxs']) - np.array(maxs)) < 10) or (np.std(np.array(values['mins']) - np.array(mins)) < 10):
                    r += key
                    break
        return r

    def _start_chrome(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        self.driver = driver


    def get(self, cpf, data_nascimento):
        if self.driver is None:
            self._start_chrome()

        self.driver.get(self.URLmain)

        time.sleep(2)
        input_cpf = self.driver.find_element(By.ID, "txtCPF")
        input_cpf.send_keys(cpf)

        time.sleep(2)
        input_data_nascimento = self.driver.find_element(By.ID, "txtDataNascimento")
        input_data_nascimento.send_keys(data_nascimento)

        if self._download_wave():
            captcha = self.driver.find_element(By.ID, self.INPUTCaptcha)
            captcha.click()
            time.sleep(2)

            self._paste_text(self._solve_captcha())

            time.sleep(2)
            self.driver.find_element(By.ID, self.BTSearch).click()

            teste = self.driver.find_element(By.ID, self.DIVContent)
            print(teste.text)
            self.salva(cpf, 'teste')
        else:
            return False

    def _paste_text(self, value):
        subprocess.run(self.copy_keyword, universal_newlines=True, input=value)
        ActionChains(self.driver).key_down(Keys.CONTROL).key_down('v').key_up('v').key_up(Keys.CONTROL).perform()

    def salva(self, cpf, teste):
        df = pd.read_csv ('cpfs_consulta.csv')
        update = df['cpf'] = cpf
        df.loc[update, 'situacao_cadastral'] = teste

if __name__ == '__main__':
    scrapper = WebScrapper()
    scrapper.iniciar()