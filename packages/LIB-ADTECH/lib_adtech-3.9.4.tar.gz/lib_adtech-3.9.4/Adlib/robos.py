import os
import asyncio
import datetime
import threading
import pandas as pd
from time import sleep
from io import StringIO
from bs4 import BeautifulSoup
from datetime import timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from .api import EnumBanco, EnumStatus, EnumProcesso, putStatusRobo
from .utils import aguardarTempo
from .importacao import importacaoVirtaus, ImportacaoOptions
from .logins import loginCashCard, loginDaycoval, loginVirtaus
from .funcoes import esperarElemento, getCredenciais, setupDriver, aguardarDownload


def importacaoDaycovalCartao(resetEvent: threading.Event):


    def getPropostasDaycoval(driver: Chrome) -> pd.DataFrame | None:

        driver.get('https://consignado.daycoval.com.br/Autorizador/MenuWeb/Consignado/UI.CN.CartaoConsignado.aspx')
        sleep(5)
        driver.get('https://cartaocredito.daycoval.com.br/Proposta/Aprovacao.aspx')

        # Data Atual
        dataAtual = datetime.datetime.now()

        dataInicial = dataAtual - timedelta(days=30)
        dataInicialFormatada = dataInicial.strftime("%d%m%Y")
        dataFinalFormatada = dataAtual.strftime("%d%m%Y")

        sleep(5)

        dataInputs = ['//*[@id="ctl00_ContentPlaceHolder1_txtPeriodoDeC_txtData"]',
                    '//*[@id="ctl00_ContentPlaceHolder1_txtPeriodoAteC_txtData"]']
        
        datas = [dataInicialFormatada, dataFinalFormatada]
        
        for xpath, data in zip(dataInputs, datas):
            dataInput = esperarElemento(driver, xpath)
            dataInput.send_keys(Keys.CONTROL + "A")
            dataInput.send_keys(Keys.DELETE)
            dataInput.send_keys(Keys.HOME)
            for char in data:
                dataInput.send_keys(char)
                sleep(0.5)

        sleep(5)
        esperarElemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_btnPesquisar"]').click()
        sleep(5)

        try:
            elementTabela = esperarElemento(driver, '//*[@id="ctl00_ContentPlaceHolder1_gvwPropostaC"]', tempo_espera=30)#'/html/body/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td/div/div/div/div/div/div/div/div/div/table/tbody/tr[1]/td/div/table')
            # df = convertHTMLTable2Dataframe(elementTabela)
            html_contenttabela = elementTabela.get_attribute('outerHTML')

            soup = BeautifulSoup(html_contenttabela, 'html.parser')
            table = soup.find(name='table')
            tableHtml = StringIO(str(table))  
            df = pd.read_html(tableHtml, encoding='ISO-8859-1', thousands='')[0]
            
            # print('Propostas coletadas e planilha criada.')
            # print(df.columns)
            tabelaVazia = 0 in df.columns

            if tabelaVazia:
                return pd.DataFrame()
            
            return df
            
        except Exception as e:
            return pd.DataFrame()


    def manipulacaoPlanilha(planilhaDaycovalCartao: pd.DataFrame) -> str:
        try:
            df = planilhaDaycovalCartao

            colunas_para_remover = ['Unnamed: 0', 'Unnamed: 14']
            df.drop(columns=colunas_para_remover, inplace=True, errors='ignore')
            
            # Salva a planilha manipulada
            path = os.getcwd()
            filepath = os.path.join(path, "daycovalCartao.csv")

            if df.empty:
                return ""

            df.to_csv(filepath, encoding='ISO-8859-1', sep=';', index=False)
            
            # print(f"Planilha manipulada e salva em: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"Erro durante a manipulação da planilha: {e}")


    loginBanco, senhaBanco = getCredenciais(227)
    userVirtaus, senhaVirtaus = getCredenciais(304)

    driver = setupDriver(r"C:\Users\dannilo.costa\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe", numTabs=2)
    intervalo = 6*60 # 6 minutos
     
    options = {
        "portabilidade": "NÃO",
        "layout": "Cartão",
        "empty": False
    }

    driver.switch_to.window(driver.window_handles[0])
    loginDaycoval(driver, loginBanco, senhaBanco, EnumBanco.DAYCOVAL_CARTAO, EnumProcesso.IMPORTACAO)

    driver.switch_to.window(driver.window_handles[1])
    loginVirtaus(driver, userVirtaus, senhaVirtaus)

    agora = datetime.datetime.now()    
    horaAtual = agora.hour + (agora.minute / 60)

    HORA_DESLIGAMENTO = 19.75 # 16:30
    try:
        while horaAtual < HORA_DESLIGAMENTO:
            
            driver.switch_to.window(driver.window_handles[0])
            df = getPropostasDaycoval(driver)
            filepathManipulado = manipulacaoPlanilha(df)
            
            options["empty"] = not filepathManipulado

            driver.switch_to.window(driver.window_handles[1])
            importouSemSucesso = importacaoVirtaus(driver, filepathManipulado, 'Daycoval', EnumBanco.DAYCOVAL_CARTAO, options, resetEvent)
            
            if importouSemSucesso:
                print("Daycoval Cartão vai parar")
                break
            
            asyncio.run(aguardarTempo(intervalo))
            
            agora = datetime.datetime.now()
            horaAtual = agora.hour + (agora.minute / 60)

    except KeyboardInterrupt:
        putStatusRobo(EnumStatus.DESLIGADO, EnumProcesso.IMPORTACAO, EnumBanco.DAYCOVAL_CARTAO)


def importacaoCashCard(resetEvent: threading.Event):


    def getPropostasMeuCashCard(cashcard: Chrome, userWindows: str) -> str:
        cashcard.get("https://front.meucashcard.com.br/WebAppBPOCartao/Pages/Relatorios/ICRLProducaoAnalitico")
        esperarElemento(cashcard, '//*[@id="ctl00_Cph_bbExportarCSV"]').click()
        
        filepath = aguardarDownload(downloadsFolder, "RelatorioProducaoAnalitico")
        
        return filepath


    def filtrarColunaString(df: pd.DataFrame, coluna: str, matchingString: str, inverter: bool = False) -> pd.DataFrame:
        """
        Filtra o DataFrame com base em uma string correspondente a uma coluna específica.

        Args:
            df (pd.DataFrame): DataFrame a ser filtrado.
            coluna (str): Nome da coluna a ser analisada.
            matching_string (str): String que será usada para encontrar correspondências.
            inverter (bool, opcional): Se True, inverte a lógica do filtro. Default é False.

        Returns:
            pd.DataFrame: DataFrame filtrado.
        """
        mask = df[coluna].str.contains(matchingString, na=False)
        return df[~mask] if inverter else df[mask]


    def df2csv(df: pd.DataFrame, filename: str) -> str:
        try:
            path = os.getcwd()
            filepath = os.path.join(path, filename+".csv")
            df.to_csv(filepath, index=False, encoding="ISO-8859-1", sep=';', errors="ignore")
            
            return filepath
        except Exception as e:
            print(e)


    def processarPropostas(filePath: str):
        try:
            df = pd.read_csv(filePath, sep=';')
            
            del df["Código Empregador"]
            del df["Última Observação"]

            df["CPF/CNPJ"] = df["CPF/CNPJ"].str.replace(r"[.,-]", "", regex=True)

            return filtrarColunaString(df, "Atividade", "CORBAN APROVAR")
        
        except Exception as e:
            print("Erro ao processar propostas")
            print(e)

    
    usuario, senha = getCredenciais(467)
    virtaus, mcc = setupDriver(numTabs=2, autoSwitch=True)

    intervalo = 6*60 # 10 minutos

    userWindows = "dannilo.costa"
    
    userVirtaus, senhaVirtaus = getCredenciais(302)
    downloadsFolder = os.path.join(r"C:/Users", userWindows, "Downloads")
    
    for file in os.listdir(downloadsFolder):
        filepath = os.path.join(downloadsFolder, file)
        if "RelatorioProducaoAnalitico" in file:
            os.remove(filepath)

    options = ImportacaoOptions()
    
    loginVirtaus(virtaus, userVirtaus, senhaVirtaus)

    agora = datetime.datetime.now()
    horaAtual = agora.hour + (agora.minute / 60)
    HORA_DESLIGAMENTO = 18  #  17.5 = 17:30

    try:
        while True:

            loginCashCard(mcc, usuario, senha)

            filePath = getPropostasMeuCashCard(mcc, userWindows)
            dfAprovado = processarPropostas(filePath)

            propostasPath = df2csv(dfAprovado, "MEUCASH CARD")
            
            # print(propostasPath)

            if filePath:
                importouSemSucesso = importacaoVirtaus(virtaus, propostasPath, 'MeuCashCard', EnumBanco.MEU_CASH_CARD, options, resetEvent)

                if importouSemSucesso:
                    break

            os.remove(filePath)
            
            asyncio.run(aguardarTempo(intervalo))

            agora = datetime.datetime.now()
            horaAtual = agora.hour + (agora.minute / 60)

            mcc.quit()

    except KeyboardInterrupt:
        putStatusRobo(EnumStatus.DESLIGADO, EnumProcesso.IMPORTACAO, EnumBanco.MEU_CASH_CARD)