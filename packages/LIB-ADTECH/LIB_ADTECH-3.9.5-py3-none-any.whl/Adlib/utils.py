import os
import sys
import time
import psutil
import shutil
import asyncio
import chardet
import datetime
import subprocess
import pandas as pd
from .enums import EnumProcesso, EnumBanco
from selenium.webdriver.remote.webelement import WebElement


meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}


tokenBotLogin = '7505814396:AAFEm1jwG3xwd8N41j_viCCxgZUBT-XhbbY'
tokenBotAnaliseDocs = "7333756979:AAFDUBW0KKaub1ciwKrCb3Q7ncVRhfZHfEM"
tokenBotImportacao = "8013361039:AAGBT5eMqYw3WdfxAdWsqgCySpuFPLHhl2Y"
tokenBotImportacaoItau = "7310212931:AAH-1HvkQZo03h1TTTfaKI7QIgsipA0XV2I"
tokenBotConfirmacao = "7519811574:AAGayFV_OReR-piS06_7APOgkWg9FZfwPSs"
tokenBotReset = "5795666778:AAG-_c6cniTaBOSOwvh9_FLyY01uVZ1uT04"
tokenBotCriacao = "5929694836:AAGNuG2-f8kJQMIJuVO_GkIeD8g-8Q3MZUo"
tokenBotIntegracao = "7506259919:AAEpbbkg5Xu7YXK0T8IVM76LM23pzIvt6wY"
tokenBotPagDev = "5636690814:AAG07yuDlO9CYNv5LUuwanoH4tK-2WJZ9do" 
tokenBotConsulta = "6025392431:AAGoTFLMDyIT1sBu3L_7q3bUjGYnlwfpkBQ"
tokenBotBlipLink = "6025392431:AAGoTFLMDyIT1sBu3L_7q3bUjGYnlwfpkBQ"
tokenBotAprovadorBMG = "8088224910:AAFx6D2EPNeF12D10TztfW28pm3qEUeV-AI"
tokenBotAprovadorBanrisul = "6442613707:AAEEKfLHxUFTzG6_l6xmH3A3yxmt5Wxgep8"
tokenBotAprovadorC6 = "5902150437:AAFw4pFqcVp8XCYBTJeYvuM3vkLRWwZuDI0"
tokenBotAprovadorCrefisa = "6586328186:AAE74rFDPa6JK8Hlbtf5oBqA9MT6p_XwzDQ"
tokenBotAprovadorDaycoval = "6450552160:AAE6tJ-b_adK3wJ9V9zip2G9hd1cOpEZRgQ"
tokenBotAprovadorDigio = "7502689321:AAHrPDp9Y-MsVhcTzh_OImoRZXJsOPNoNKk"
tokenBotAprovadorFacta = "6514704466:AAEDHQo7nmkszonbuoiiNc9p7Zlj9qpzGx4"
tokenBotAprovadorItau = "7310212931:AAH-1HvkQZo03h1TTTfaKI7QIgsipA0XV2I"
tokenBotAprovadorOle = "5849027495:AAG9i1hdGV_Aj3nvLzAfzuOYO1p9nK5vAhg"
tokenBotAprovadorPan = "6956643976:AAGHCcaelAZzEaQNmJ_n3pD14LV-vsFDnYo"
tokenBotColetor = "6525330287:AAEDmosxFqWL1xgem-B3cYx-Y6fI0n4gaao"
tokenBotAprovadorAmigoz = "8058216345:AAEuEhCDaJZVseUMJslYU0f4ypMdlMe4LbY"


chatIdEsteiraLogin = "-1002257326271"
chatIdIntegracaoLogin = "-1002556560733"
chatIdUsuariosLogin = "-4095757991"
chatIdConfirmacaoLogin = "-4643090903"
chatIdBlipConsulta = "-910947972"
chatIdConfirmacao = "-1002420514126"
chatIdCriacao = "-1001716522279"
chatIdReset = "-1002798198497"
chatIdColetor = "-1001975297001"
chatIdImportacao = "-794597825"
chatIdAutenticacaoPan = "-4511821162"
chatIdPagDev = "-848622864"
chatIdIntegracao = "-4579971115"
chatIdAprovadores = "-820496030"
chatIdErroImportacao = "-768254624"
chatIdAnalise = "-4264004977"

loginChatIdMapping = {
    EnumProcesso.CRIACAO: chatIdUsuariosLogin,
    EnumProcesso.RESET: chatIdUsuariosLogin,
    EnumProcesso.BLIP_CONSULTA: chatIdUsuariosLogin,
    EnumProcesso.BLIP_LINK: chatIdUsuariosLogin,
    EnumProcesso.CONFIRMACAO_CREDITO: chatIdConfirmacaoLogin,
    EnumProcesso.ANALISE_DOCUMENTOS: chatIdEsteiraLogin,
    EnumProcesso.IMPORTACAO: chatIdEsteiraLogin,
    EnumProcesso.APROVADORES: chatIdEsteiraLogin,
    EnumProcesso.INTEGRACAO: chatIdIntegracaoLogin,
}

chatIdMapping = {
    EnumProcesso.CRIACAO: chatIdCriacao,
    EnumProcesso.RESET: chatIdReset,
    EnumProcesso.CONFIRMACAO_CREDITO: chatIdConfirmacao,
    EnumProcesso.ANALISE_DOCUMENTOS: chatIdAnalise,
    EnumProcesso.INTEGRACAO: chatIdIntegracao,
    EnumProcesso.BLIP_LINK: chatIdBlipConsulta,
    EnumProcesso.BLIP_CONSULTA: chatIdBlipConsulta,
    EnumProcesso.PAG_DEV: chatIdPagDev,
    EnumProcesso.IMPORTACAO: chatIdImportacao,
    (EnumProcesso.IMPORTACAO, EnumBanco.PAN): chatIdAutenticacaoPan,
    EnumProcesso.APROVADORES: chatIdAprovadores,
    (EnumProcesso.APROVADORES, EnumBanco.VIRTAUS): chatIdColetor,
}

botTokenMapping = {
    EnumProcesso.ANALISE_DOCUMENTOS: tokenBotAnaliseDocs,
    EnumProcesso.IMPORTACAO: tokenBotImportacao,
    (EnumProcesso.IMPORTACAO, EnumBanco.ITAU): tokenBotImportacaoItau,
    EnumProcesso.CONFIRMACAO_CREDITO: tokenBotConfirmacao,
    EnumProcesso.RESET: tokenBotReset,
    EnumProcesso.CRIACAO: tokenBotCriacao,
    EnumProcesso.INTEGRACAO: tokenBotIntegracao,
    EnumProcesso.PAG_DEV: tokenBotPagDev,
    EnumProcesso.BLIP_CONSULTA: tokenBotConsulta,
    EnumProcesso.BLIP_LINK: tokenBotBlipLink,
    (EnumProcesso.APROVADORES, EnumBanco.BMG): tokenBotAprovadorBMG,
    (EnumProcesso.APROVADORES, EnumBanco.BANRISUL): tokenBotAprovadorBanrisul,
    (EnumProcesso.APROVADORES, EnumBanco.C6): tokenBotAprovadorC6,
    (EnumProcesso.APROVADORES, EnumBanco.CREFISA): tokenBotAprovadorCrefisa,
    (EnumProcesso.APROVADORES, EnumBanco.DAYCOVAL): tokenBotAprovadorDaycoval,
    (EnumProcesso.APROVADORES, EnumBanco.DIGIO): tokenBotAprovadorDigio,
    (EnumProcesso.APROVADORES, EnumBanco.FACTA): tokenBotAprovadorFacta,
    (EnumProcesso.APROVADORES, EnumBanco.ITAU): tokenBotAprovadorItau,
    (EnumProcesso.APROVADORES, EnumBanco.OLE): tokenBotAprovadorOle,
    (EnumProcesso.APROVADORES, EnumBanco.PAN): tokenBotAprovadorPan,
    (EnumProcesso.APROVADORES, EnumBanco.VIRTAUS): tokenBotColetor,
    (EnumProcesso.APROVADORES, EnumBanco.AMIGOZ): tokenBotAprovadorAmigoz
}


baseFolderMapping = {
    (EnumBanco.VAZIO, EnumProcesso.INTEGRACAO):  0,
    (EnumBanco.PAN, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\02 - Pan",
    (EnumBanco.OLE, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\05 - Bonsucesso",
    (EnumBanco.MEU_CASH_CARD, EnumProcesso.INTEGRACAO): "Meu CashCard",
    (EnumBanco.BMG, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\04 - BMG",
    (EnumBanco.DIGIO, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\29 - Digio",
    (EnumBanco.BANRISUL, EnumProcesso.INTEGRACAO): "Banrisul",
    (EnumBanco.BANCO_DO_BRASIL, EnumProcesso.INTEGRACAO): "Banco do Brasil",
    (EnumBanco.C6, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\08 - C6 Bank",
    (EnumBanco.ITAU, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\03 - Itau",
    (EnumBanco.MASTER, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\21 - Master_Consig_e_FGTS",
    (EnumBanco.PAULISTA, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\23 - Paulista",
    (EnumBanco.CREFAZ, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\15 - Crefaz",
    (EnumBanco.CCB, EnumProcesso.INTEGRACAO): 13,
    (EnumBanco.DAYCOVAL, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\07 - Daycoval",
    (EnumBanco.DAYCOVAL_CARTAO, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\07 - Daycoval",
    (EnumBanco.ICRED, EnumProcesso.INTEGRACAO): 15,
    (EnumBanco.AMIGOZ, EnumProcesso.INTEGRACAO): 16,
    (EnumBanco.SAFRA, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\18 - Safra",
    (EnumBanco.SANTANDER, EnumProcesso.INTEGRACAO): 18,
    (EnumBanco.CREFISA, EnumProcesso.INTEGRACAO): 20,
    (EnumBanco.FACTA, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\12 - Facta",
    (EnumBanco.SABEMI, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\13 - Sabemi",
    (EnumBanco.FUTURO_PREVIDENCIA, EnumProcesso.INTEGRACAO): 23,
    (EnumBanco.CREFISA_CP, EnumProcesso.INTEGRACAO): 24,
    (EnumBanco.PAN_CARTAO, EnumProcesso.INTEGRACAO): 25,
    (EnumBanco.PAN_PORT, EnumProcesso.INTEGRACAO): 26,
    (EnumBanco.HAPPY_PORT, EnumProcesso.INTEGRACAO): 27,
    (EnumBanco.NUVIDEO, EnumProcesso.INTEGRACAO): 28,
    (EnumBanco.PROMOBANK, EnumProcesso.INTEGRACAO): 29,
    (EnumBanco.GETDOC, EnumProcesso.INTEGRACAO): 31,
    (EnumBanco.PRESENCA_BANK, EnumProcesso.INTEGRACAO): r"Z:\Arquivos de Integração\33 - Presença Bank",
    (EnumBanco.VAZIO, EnumProcesso.CONFIRMACAO_CREDITO):  0,
    (EnumBanco.PAN, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\24 - Pan",
    (EnumBanco.OLE, EnumProcesso.CONFIRMACAO_CREDITO): 2,
    (EnumBanco.MEU_CASH_CARD, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\23 - MeuCashCard",
    (EnumBanco.BMG, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\5.1 - Bmg (Rôbo)",
    (EnumBanco.DIGIO, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\15 - Digio",
    (EnumBanco.BANRISUL, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\04 - Banrisul",
    (EnumBanco.BANCO_DO_BRASIL, EnumProcesso.CONFIRMACAO_CREDITO): "Banco do Brasil",
    (EnumBanco.C6, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\08 - C6",
    (EnumBanco.ITAU, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\20 - Itau",
    (EnumBanco.MASTER, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\22 - Master",
    (EnumBanco.PAULISTA, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\25 - Paulista",
    (EnumBanco.CREFAZ, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\12 - Crefaz",
    (EnumBanco.CCB, EnumProcesso.CONFIRMACAO_CREDITO): 13,
    (EnumBanco.DAYCOVAL, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\14 - Daycoval",
    (EnumBanco.ICRED, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\19 - Icred",
    (EnumBanco.HAPPY_AMIGOZ, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\02 - AmigoZ",
    (EnumBanco.SAFRA, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\27 - Safra",
    (EnumBanco.SANTANDER, EnumProcesso.CONFIRMACAO_CREDITO): 18,
    (EnumBanco.CREFISA, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\13 - Crefisa",
    (EnumBanco.FACTA, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\17 - Facta",
    (EnumBanco.SABEMI, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\26 - Sabemi",
    (EnumBanco.FUTURO_PREVIDENCIA, EnumProcesso.CONFIRMACAO_CREDITO): r"Z:\Arquivos de Confirmação de Crédito\16 - Futuro Previdência",
    (EnumBanco.CREFISA_CP, EnumProcesso.CONFIRMACAO_CREDITO): 24,
    (EnumBanco.PAN_CARTAO, EnumProcesso.CONFIRMACAO_CREDITO): 25,
    (EnumBanco.PAN_PORT, EnumProcesso.CONFIRMACAO_CREDITO): 26,
    (EnumBanco.HAPPY_PORT, EnumProcesso.CONFIRMACAO_CREDITO): 27,
    (EnumBanco.NUVIDEO, EnumProcesso.CONFIRMACAO_CREDITO): 28,
    (EnumBanco.PROMOBANK, EnumProcesso.CONFIRMACAO_CREDITO): 29,
    (EnumBanco.GETDOC, EnumProcesso.CONFIRMACAO_CREDITO): 31,
}


def importarPastaMonitoramento(filepathList: list[str], enumBanco: EnumBanco, enumProcesso: EnumProcesso, subPasta: str = '',  data: datetime.datetime = None):
    """
    Copia um arquivo para uma pasta organizada por ano, mês e dia, conforme o banco especificado,
    criando as pastas necessárias caso não existam.

    Args:
        filePath (str): Caminho completo do arquivo a ser copiado.
        enumBanco (EnumBanco): Enum que identifica o banco, usado para determinar o diretório base.
        data (datetime.datetime, opcional): Data para organizar a pasta de destino. 
            Se não fornecida, usa a data atual.

    Returns:
        str: Caminho completo do arquivo copiado no diretório de monitoramento.
    """
    diretorioBase = baseFolderMapping[(enumBanco, enumProcesso)]
    hoje = datetime.datetime.now()
    
    if data:
        hoje = data
    
    pastaAno = str(hoje.year)
    pastaMes = f"{hoje.month:02d} - {meses[hoje.month]}" # 01 - Janeiro
    pastaDia = f"{hoje.day:02d}"

    caminho = os.path.join(diretorioBase, subPasta, pastaAno, pastaMes, pastaDia)

    os.makedirs(caminho, exist_ok=True)

    for filepath in filepathList:
        nomeArquivo = os.path.basename(filepath)
        destino = os.path.join(caminho, nomeArquivo)
        shutil.copy(filepath, destino)
        os.remove(filepath)

    return caminho


def renomearArquivo(filepath, newFilename) -> str:
    """
    Renames a file to a new filename in the same directory.

    If a file with the new name already exists, it will be removed before renaming.

    Args:
        filepath (str): The full path to the original file.
        newFilename (str): The new name for the file (without the directory path).

    Returns:
        str: The full path to the renamed file.

    Raises:
        FileNotFoundError: If the original file does not exist.
        PermissionError: If there are permission issues during rename or delete operations.
        OSError: For other OS-related errors.
    """
    newFilepath = os.path.join(os.path.dirname(filepath), newFilename)

    if os.path.exists(newFilepath):
        os.remove(newFilepath)

    os.rename(filepath, newFilepath)

    return newFilepath


def detectEncoding(filepath, sample_size=10000):
    with open(filepath, 'rb') as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    return result['encoding']


async def aguardarTempo(intervalo: int = 900):

    async def countdown(intervalo: int):
        """
        Contagem assíncrona que mostra os minutos e segundos restantes
        
        Args:
            intervalo (int): A duração da contagem (em segundos).
        """
        tempo = 0
        while tempo < intervalo:
            for suffix in ["   ", ".  ", ".. ", "..."]:
                remaining = intervalo - tempo
                minutos, segundos = divmod(remaining, 60)
                print(f"Próxima checagem em {minutos:02}:{segundos:02} - Aguardando{suffix}", end="\r")
                await asyncio.sleep(1)
                tempo += 1
        print(f" "*75, end="\r")

    await countdown(intervalo)


def convertHTMLTable2Dataframe(tableElement: WebElement) -> pd.DataFrame:
    """
    Converte um elemento <table> (Selenium WebElement) em um DataFrame

    Args:
        tableElemento (WebElement): O elemento do Selenium que representa a tabela em HTML <table>

    Returns:
        pd.DataFrame: A DataFrame containing the table data.
    """
    headers = [header.text for header in tableElement.find_elements("xpath", './/th')]
    
    rows = []
    for row in tableElement.find_elements("xpath", './/tr'):
        cells = row.find_elements("xpath", './/td')
        rows.append([cell.text for cell in cells])
    
    rows = [row for row in rows if row]
    
    if headers:
        return pd.DataFrame(rows, columns=headers)
    else:
        return pd.DataFrame(rows)


def executarPythonScripts(workingDirs: list[str], scripts: list[str], tabNames: list[str], delay: int = 10):
    def getTerminalsCount():
        return sum(1 for p in psutil.process_iter(attrs=['name']) if p.info['name'] == "powershell.exe")


    python = sys.executable
        
    subprocess.run(["wt"])
    time.sleep(1)  # Small delay to ensure the new window is created before opening tabs

    numWindows = getTerminalsCount()
    base_command = ["wt", "--window", f"{numWindows + 2}", "new-tab", "--title"]

    for workingDir, script, tabName in zip(workingDirs, scripts, tabNames):
        subprocess.run(base_command + [tabName] + ["cmd", "/k"] + ["cd", "/d", workingDir, "&&", python, script])
        time.sleep(delay)


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
    if coluna not in df:
        return pd.DataFrame()

    mask = df[coluna].str.contains(matchingString, na=False)
    return df[~mask] if inverter else df[mask]


def df2csv(df: pd.DataFrame, filename: str, encoding: str = "utf-8", quotechar = '"', sep: chr = ';') -> str:
    try:
        path = os.getcwd()
        filepath = os.path.join(path, filename+".csv")
        df.to_csv(filepath, index=False, sep=sep, encoding=encoding, quotechar=quotechar, errors='replace')
        
        return filepath
    except Exception as e:
        print(e)


def removerArquivos(DOWNLOAD_FOLDER, substring: str):
    for file in os.listdir(DOWNLOAD_FOLDER):
        filepath = os.path.join(DOWNLOAD_FOLDER, file)
        if substring in file:
            os.remove(filepath)


if __name__=="__main__":

    from Adlib.funcoes import mensagemTelegram

    mensagemTelegram(tokenBotReset, chatIdReset, "teste")

    # scripts = ["teste2.py", "teste3.py"]

    # workingDirs = [r"C:\Users\dannilo.costa\Desktop\Repos AD\Adlib", r"C:\Users\dannilo.costa\Desktop\Repos AD\Adlib"]

    # executarPythonScripts(workingDirs, scripts, ["teste2", "teste3"])