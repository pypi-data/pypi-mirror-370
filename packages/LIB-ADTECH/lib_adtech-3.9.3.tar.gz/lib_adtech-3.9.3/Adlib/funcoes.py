import os
import re
import sys
import time
import msal
import base64
import shutil
import smtplib
import requests
import datetime
import platform
import mimetypes
import subprocess
from pathlib import Path
from pprint import pprint
from bs4 import BeautifulSoup
from email.message import EmailMessage
from Adlib.enums import EnumStatus
from Adlib.api import EnumBanco, EnumProcesso, putStatusRobo
from Adlib.utils import loginChatIdMapping
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from webdriver_manager.chrome import ChromeDriverManager


TOKEN_CAPTCHA = "7505814396:AAFEm1jwG3xwd8N41j_viCCxgZUBT-XhbbY"
CHAT_ID_CAPTCHA = "-4095757991"

# EXCLUDED_METHODS = ["close"]
EXCLUDED_ATTRIBUTES = []
from functools import wraps

class TabDriver:
    """
    A proxy class representing a single tab in a multi-tab Chrome instance.
    Ensures the correct tab is always active before any attribute or method is accessed.
    """
    def __init__(self, driver: Chrome, index: int):
        self.driver = driver
        self.index = index
        self.handle = driver.window_handles[index]
        
        self.autoSwitch()

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if callable(attr) and not name.startswith("__"):
            @wraps(attr)
            def wrapped(*args, **kwargs):
                self.driver.switch_to.window(self.handle)
                return attr(*args, **kwargs)
            return wrapped
        return attr

    def __getattr__(self, name):
        
        self.autoSwitch()

        attr = getattr(self.driver, name)

        if callable(attr):
            @wraps(attr)
            def wrapped(*args, **kwargs):
                self.autoSwitch()
                return attr(*args, **kwargs)
            return wrapped
        
        return attr

    def autoSwitch(self):
        if self.driver.current_window_handle != self.handle:
            self.driver.switch_to.window(self.handle)


def setupDriver(
    webdriverPath: str = os.path.join(os.path.dirname(__file__), r"webdriver\chromedriver.exe"), 
    numTabs: int = 1,
    options: list[str] = [],
    experimentalOptions: dict[str, any] = dict(),
    autoSwitch: bool = False,
    headless: bool = False

) -> list[TabDriver] | Chrome:
    """
    Initializes a single Chrome instance with multiple tabs, then returns a list
    of TabDriver instances—one for each tab.
    """
    if platform.system() == "Linux":
        webdriverPath = os.path.join(os.path.dirname(__file__), r"webdriver\chromedriver")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("log-level=3")
    chrome_options.add_argument("--silent")


    # driver = Chrome(ChromeDriverManager().install())
    if headless:
        headlessOptions = [
            'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36',
            '--no-sandbox',
            '--window-size=1920,1080',
            '--headless',
            '--disable-gpu',
            '--allow-running-insecure-content'
        ]
        for option in headlessOptions:
            chrome_options.add_argument(option)
                     
    for option in options:
        chrome_options.add_argument(option)

    experimentalOptions["profile.default_content_setting_values.notifications"] = 2

    chrome_options.add_experimental_option("prefs", experimentalOptions)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    creation_flags = 0
    if hasattr(subprocess, 'CREATE_NO_WINDOW'):
        creation_flags = subprocess.CREATE_NO_WINDOW

    service = Service(
        executable_path=ChromeDriverManager().install(),
        service_args=['--silent'],
    )
    service.creationflags = creation_flags
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
   
    for _ in range(numTabs - 1):
        driver.execute_script("window.open('');")

    # Return one TabDriver per tab.
    if autoSwitch:
        return TabDriver(driver, 0) if (numTabs == 1) else (TabDriver(driver, i) for i in range(numTabs))
    
    return driver


def setupDriverLinux(numTabs: int = 1, options: list[str] = [], experimentalOptions: dict[str, any] = {}):
    """
    Inicializa o Chrome no Linux, baixando automaticamente o WebDriver correto.
    """
    chrome_service = webdriver.ChromeService(ChromeDriverManager().install())

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("log-level=3")

    for option in options:
        chrome_options.add_argument(option)

    chrome_options.add_experimental_option("prefs", experimentalOptions)

    driver = Chrome(service=chrome_service, options=chrome_options)
    driver.maximize_window()

    # Abrir abas adicionais
    for _ in range(numTabs - 1):
        driver.execute_script("window.open('');")

    return [TabDriver(driver, i) for i in range(numTabs)]


def getCredenciais(id: int) -> tuple[str, str] | tuple[None, None]:
    """
    Recupera as credenciais (login e senha) de uma API com base no ID fornecido.

    Esta função faz uma requisição `GET` para uma API REST usando o ID fornecido e tenta recuperar as credenciais de login e senha. Se a requisição for bem-sucedida (status code 200) e os dados estiverem presentes, ela retorna uma tupla contendo o login e a senha. Caso contrário, retorna uma tupla com `None` nos dois valores.

    Args:
        id (int): O ID utilizado para buscar as credenciais na API.

    Returns:
        tuple[str, str] | tuple[None, None]: 
            - Uma tupla contendo `login` e `senha` se a requisição for bem-sucedida e os dados estiverem presentes.
            - Uma tupla `(None, None)` se a requisição falhar ou os dados não estiverem disponíveis.
    """
    url = f"http://172.16.10.6:8080/credenciais/{id}"
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            login = dados.get('login')
            senha = dados.get('senha')
            return login, senha
        return None, None
    except Exception as e:
        print(e)
        print("Não foi possível acessar a API")


def instalarPacote(pacote: str):
    """
    Instala uma biblioteca do python
    Arguments:
        pacote: nome do pacote disponível no PyPI
    """
    subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
  

def enviarEmailOutlook(
    destinatarios: list[str],
    assunto: str,
    corpo: str,
    remetente: str,
    senha: str,
    cc: list[str] = [],
    anexos: list[str] = []
):
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    msg["Cc"] = ", ".join(cc)
    msg.set_content(corpo)

    for caminho in anexos:
        caminho_arquivo = Path(caminho)
        tipo, codificacao = mimetypes.guess_type(caminho_arquivo)
        tipo = tipo or "application/octet-stream"
        maintype, subtype = tipo.split("/", 1)

        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()
            msg.add_attachment(
                conteudo,
                maintype=maintype,
                subtype=subtype,
                filename=caminho_arquivo.name
            )

    with smtplib.SMTP("smtp.office365.com", 587) as smtp:
        smtp.starttls()
        smtp.login(remetente, senha)
        smtp.send_message(msg, to_addrs=destinatarios + cc)
      

def aguardarAlert(driver: Chrome | TabDriver) -> str:
    """
    Aguarda por um alerta JavaScript no navegador e retorna seu texto.

    Se um alerta for encontrado em até 10 segundos, ele será aceito (ou descartado caso o `accept()` falhe).
    Caso nenhum alerta apareça no tempo limite, retorna uma string vazia.

    Args:
        driver (Chrome | TabDriver): Instância do driver do Selenium, podendo ser `Chrome` direto ou um `TabDriver`.

    Returns:
        str: Texto do alerta, ou "" se nenhum alerta for detectado.
    """
    if isinstance(driver, TabDriver):
        driver = driver.driver
    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert_text = alert.text
        try:
            alert.accept()
        except:
            alert.dismiss()
        return alert_text
    except:
        return ""


def selectOption(driver: Chrome, selectXpath: str, visibleText: str):
    """
    Seleciona uma opção em um elemento <select> com base no texto visível.

    Args:
        driver (Chrome): Instância do WebDriver.
        selectXpath (str): XPath do elemento <select>.
        visibleText (str): Texto visível da opção a ser selecionada.

    Returns:
        None
    """

    select = Select(esperarElemento(driver, selectXpath))
    select.select_by_visible_text(visibleText)


def esperarElemento(driver: Chrome | TabDriver, xpath: str, tempoEspera=10, debug=True) -> WebElement | None:
    """
    Aguarda o elemento estar visível na tela
    Arguments:
        driver: driver do site
        xpath: XPath do elemento
        tempoEspera: Tempo máximo de espera, em segundos
    Returns:
        Elemento
    """
    if isinstance(driver, TabDriver):
        driver = driver.driver
    try:
        return WebDriverWait(driver, tempoEspera).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    except:
        if debug:
            print(f"Elemento não encontrado: {xpath}")
 

def aguardarElemento(driver: Chrome | TabDriver, xpath: str, tempoEspera=10, debug=True) -> WebElement | None:
    """
    Aguarda o elemento ser renderizado no DOM da página
    Arguments:
        driver: driver do site
        xpath: XPath do elemento
        tempoEspera: Tempo máximo de espera, em segundos
    Returns:
        Elemento
    """
    if isinstance(driver, TabDriver):
        driver = driver.driver
    try:
        return WebDriverWait(driver, tempoEspera).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        if debug:
            print(f"Elemento não encontrado: {xpath}")


def esperarElementos(driver: Chrome, xpath: str, tempoEspera=10) -> list[WebElement]:
    """
    Retorna todos os elementos visíveis na tela.
    Arguments:
        driver: driver do site
        xpath: XPath dos elementos
        tempoEspera: Tempo máximo de espera, em segundos
    Returns:
        Lista de elementos
    """
    if isinstance(driver, TabDriver):
        driver = driver.driver
    try:
        return WebDriverWait(driver, tempoEspera).until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))
    except:
        return []


def aguardarElementos(driver: Chrome, xpath: str, tempoEspera=10) -> list[WebElement]:
    """
    Aguarda todos os elementos serem renderizados.
    Arguments:
        driver: driver do site
        xpath: XPath dos elementos
        tempoEspera: Tempo máximo de espera, em segundos
    Returns:
        Lista de elementos
    """
    if isinstance(driver, TabDriver):
        driver = driver.driver
    try:
        return WebDriverWait(driver, tempoEspera).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    except:
        return []


def clickarElemento(driver: Chrome | TabDriver, xpath: str, tempoEspera=10, debug=True) -> WebElement | None:
    """
    Aguarda o elemento do Xpath de entrada eser clicável e retorna o elemento.
    Args:
        driver: driver do site
        xpath: XPath do elemento
    Returns:
        Elemento
    """
    if isinstance(driver, TabDriver):
        driver = driver.driver
    try:
        return WebDriverWait(driver, tempoEspera).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except:
        if debug:
            print(f"Elemento não encontrado: {xpath}")


def clickElementJS(driver: Chrome, xpath: str, tempoEspera: int = 20):
    """
        Aguarda o elemento entrar em estado clicável e executa um clique usando Javascript
    """
    if isinstance(driver, TabDriver):
        driver = driver.driver
    driver.execute_script("arguments[0].click();", WebDriverWait(driver, tempoEspera).until(EC.element_to_be_clickable((By.XPATH, xpath))))


def mensagemTelegram(token: str, chat_id: int, mensagem: str):
    """
    Envia uma mensagem pela API do Telegram
    Arguments:
        token: token do bot do Telegram
        chat_id: id do chat
        mensagem: mensagem a ser enviada
    Returns:
        JSON com a resposta da requisição
    """
    mensagem_formatada = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=HTML&text={mensagem}'
    resposta = requests.get(mensagem_formatada)
    return resposta.json()
 

def aguardarDownload(downloadsFolder: str, substringNomeArquivo: str, checkpoint: float = None, maxWaitTime: int = 60) -> str:
    """
    Aguarda o download de arquivos contendo uma substring específica no nome após um determinado ponto de verificação, se fornecido.

    Args:
        downloadsFolder (str): Caminho do diretório de download.
        substringNomeArquivo (str): Substring que o arquivo baixado deve conter no nome.
        checkpoint (float, optional): Marca de tempo (timestamp) para verificar os arquivos baixados após esse momento. Se não fornecido,
        modificados após a chamada da função serão verificados.
        maxWaitTime (int, optional): Tempo máximo de espera em segundos. O padrão é 60 segundos.
    Returns:
        str: Caminho completo do arquivo baixado, se encontrado.
    """
    if checkpoint is None:
        checkpoint = datetime.datetime.now().timestamp()

    if not os.path.exists(downloadsFolder):
        raise FileNotFoundError(f"A pasta de downloads não foi encontrada: {downloadsFolder}")

    t = 0
    
    while t <= maxWaitTime:
        matchingArquivos = [arquivo for arquivo in os.listdir(downloadsFolder) if substringNomeArquivo in arquivo]
        
        for arquivo in matchingArquivos:
            caminhoArquivo = os.path.join(downloadsFolder, arquivo)
            data_modificacao = os.path.getmtime(caminhoArquivo)
            if (data_modificacao > checkpoint) and not arquivo.endswith(".crdownload") and not arquivo.endswith(".tmp"):
                return caminhoArquivo

        time.sleep(1)
        t += 1


def solveReCaptcha(driver):
    """
    Resolve um reCAPTCHA v2 em uma página web usando o selenium_recaptcha_solver.

    Configura o caminho do executável ffmpeg necessário para o solver,
    localiza o iframe do reCAPTCHA e executa o clique para resolver o desafio.

    Args:
        driver: Instância do Selenium WebDriver em que o reCAPTCHA está presente.

    Returns:
        None
    """
    from selenium_recaptcha_solver import RecaptchaSolver
    
    ffmpeg_dir = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")

    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
    
    if isinstance(driver, TabDriver):
        driver = driver.driver
        
    solver = RecaptchaSolver(driver=driver)
    recaptchaFrame = esperarElemento(driver, '//iframe[@title="reCAPTCHA"]')
    solver.click_recaptcha_v2(iframe=recaptchaFrame)



def enviarCaptcha(imagePath: str | Path, enumBanco: EnumBanco, enumProcesso: EnumProcesso, token: str = TOKEN_CAPTCHA, chatId: str = CHAT_ID_CAPTCHA, tempoEspera: int = 60) -> str:
    """
    Envia uma imagem do captcha para um chat do Telegram e retorna uma resposta no intervalo de tempo.

    Args:
        chat_id (int): ID do chat do Telegram.
        imagePath (str | Path): Caminho da imagem do captcha.
    """

    baseUrl = f'https://api.telegram.org/bot{token}'
    
    chatId = loginChatIdMapping[enumProcesso]

    formatName = lambda x: (" ".join(c for c in x.split('_'))).upper()

    with open(imagePath, 'rb') as imageFile:
        parametros = {
            "chat_id": chatId,
            "caption": f"Realizar Captcha\n{formatName(enumBanco.name)} {formatName(enumProcesso.name)}"
        }

        files = {
            "photo": imageFile
        }

        resp = requests.post(f"{baseUrl}/sendPhoto", data=parametros, files=files).json()
        messageId = resp["result"]["message_id"]
        messageTimestamp = resp["result"].get("date", 0) - 5
    
    baseUrl = f"https://api.telegram.org/bot{token}"
    offset = 0
    tempoInicial = time.time()

    while (time.time() - tempoInicial) < tempoEspera:
        response = requests.get(
            f"{baseUrl}/getUpdates",
            params={"timeout": 20, "offset": offset},
            timeout=25
        )
        
        updates = response.json().get("result", [])
        
        for update in updates:
            offset = update["update_id"] + 1
            msg = update.get("message")
            
            if msg and msg.get("reply_to_message", {}).get("message_id") == messageId:
                if msg.get("date", 0) > messageTimestamp:
                    return msg["text"]

    return "123456"


def saveCaptchaImage(imgElement: WebElement, enumBanco: EnumBanco, enumProcesso: EnumProcesso) -> str:
    """
    Salva a imagem do captcha capturada a partir de um elemento WebElement em disco.

    O arquivo é salvo no diretório atual com nome no formato:
    "Token_<{enumBanco}>_<{enumProcesso}>.png".

    Args:
        imgElement (WebElement): Elemento da imagem do captcha na página.
        enumBanco (EnumBanco): Enumeração representando o banco.
    """
    imgFolderPath = os.getcwd()
    imgName = f"Token_{enumBanco.name}_{enumProcesso.name}.png"
    
    imgPath = os.path.join(imgFolderPath, imgName)

    imgElement.screenshot(imgName)

    return imgPath


def clickCoordenada(driver: Chrome, x: int, y: int) -> None:
    """
    Clica em uma coordenada específica na tela.
    Args:
        driver: driver do site
        x: coordenada x
        y: coordenada y
    """

    action = ActionBuilder(driver)
    action.pointer_action.move_to_location(x, y)
    action.pointer_action.click()
    action.perform()


def rightClick(driver: Chrome, xpath: str):
    """
    Realiza um clique com o botão direito do mouse em um elemento identificado pelo XPath.

    Args:
        driver (Chrome): Instância do Selenium WebDriver.
        xpath (str): XPath do elemento que receberá o clique com o botão direito.

    Returns:
        None
    """
    element = esperarElemento(driver, xpath)
    actions = ActionChains(driver)
    actions.context_click(element).perform()
    

def moveToElement(driver: Chrome, xpath: str, click: bool = False):
    """
    Moves the mouse to the position where the element is located.

    Args:
        driver: The Chrome WebDriver instance.
        xpath: The XPath of the element to move to.
    """
    element = esperarElemento(driver, xpath)
    actions = ActionChains(driver)
    if click:
        actions.move_to_element(element).click().perform()
    else:
        actions.move_to_element(element).perform()


def coletarPinBanrisul(email: str, pasta: str):

    codigos = coletarDadosEmail(
        userEmail=email,
        filtroAssunto="BemWeb - Pin Autenticação",
        regexConteudo=r"seguida: (\d+)",
        filtroEmail="naoresponder@bempromotora.com.br",
        pasta=pasta
    )
    
    if codigos:
        return codigos[0][0]


def dataEscolha(days: int, formato: str = '%d/%m/%Y') -> str:
    return (datetime.datetime.today() - datetime.timedelta(days=days)).strftime(formato)


def horaFinalizacao(driver, enumProcesso, enumBanco, hora=18, minuto=0):
    agora = datetime.datetime.now()
    horario_limite = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)

    if agora >= horario_limite:
        putStatusRobo(EnumStatus.DESLIGADO, enumProcesso, enumBanco)
        driver.quit()
        return True  # sinaliza que deve parar

    return False  # ainda não é hora


def coletarDadosEmail(
    userEmail: str,
    filtroAssunto: str = '',
    regexConteudo: str = r".*",
    n_emails: int = 5000,
    filtroEmail: str = None,
    recebidoApos: datetime.datetime = datetime.datetime.combine(datetime.date.today(), datetime.time.min),
    pasta: str = '',
    separador: str = ' ',
    show: bool = False
) -> list:
    """
    Coleta informações de e-mails específicos de uma caixa de entrada do Outlook

    Args:
        userEmail (str): O endereço de e-mail do usuário cuja caixa de entrada será acessada.
        filtroAssunto (str, optional): String para filtrar o assunto do e-mail (case-sensitive).
                                        Se None, não filtra por assunto.
        regexConteudo (str, optional): Expressão regular para extrair valores do corpo do e-mail.
                                       Se None, não tenta extrair e returns None.
        n_emails (int, optional): O número máximo de e-mails recentes a serem buscados. Padrão para 20.
        filtroEmail (str, optional): Filtra e-mails de um remetente específico. Se None, não filtra por remetente.
        recebidoApos (datetime.datetime, optional): Filtra e-mails recebidos após esta data/hora.
                                                    Opcional. Deve ser um objeto datetime.datetime (UTC).

    Returns:
        list: A list of tuples.
    """

    def getFolderId(user_id: str, token: str, folderName: str = '') -> str | None:
        
        def getChildFolderId(folderList):
            for folder in folderList:

                if folder['displayName'].lower() in matchingFolders:
                    return folder['id']

                if 'childFolderCount' in folder and folder['childFolderCount'] > 0:
                    child_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders/{folder['id']}/childFolders"
                    child_resp = requests.get(child_url, headers=headers)
                    if child_resp.status_code == 200:
                        child_folders = child_resp.json().get('value', [])
                        foundId = getChildFolderId(child_folders)
                        if foundId:
                            return foundId
            return None

        matchingFolders = [folderName.lower()]
        
        if not folderName:
            matchingFolders = ["inbox", "caixa de entrada"]

        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders?$top=100"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            folders = resp.json().get("value", [])
            return getChildFolderId(folders)
        else:
            print(f"Erro ao listar pastas: {resp.status_code} - {resp.text}")
            return None


    CLIENT_ID = "d45fc956-3ea0-4c51-93be-c1ac46502c0d"
    CLIENT_SECRET = getCredenciais(572)[1]
    TENANT_ID = "adaa0a29-8e4a-4216-8ac8-187b1608c2e1"
    USER_ID = userEmail 
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPES = ["https://graph.microsoft.com/.default"]

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

    result = app.acquire_token_for_client(scopes=SCOPES)

    if "access_token" in result:
        tokenAcesso = result["access_token"]
        headers = {"Authorization": f"Bearer {tokenAcesso}"}
        
        datetimeFormatado = recebidoApos.isoformat(timespec='seconds') + 'Z'
        
        folderId = getFolderId(USER_ID, tokenAcesso, pasta)

        messages_url = (
            f"https://graph.microsoft.com/v1.0/users/{USER_ID}/mailFolders/{folderId}/messages?"
            f"$top={n_emails}&"
            f"$filter=receivedDateTime ge {datetimeFormatado}"
        )
        
        try:
            response = requests.get(messages_url, headers=headers)
            response.raise_for_status()
            results = response.json()
            messages = results.get("value", [])

            emailsFiltrados = []

            for msg in messages:
                if filtroAssunto and filtroAssunto.lower() not in msg.get('subject', '').lower():
                    continue

                emailRemetente = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                if filtroEmail and filtroEmail.lower() != emailRemetente.lower():
                    continue

                emailsFiltrados.append(msg)
            
            emailsOrdenados = sorted(emailsFiltrados, key=lambda x: x.get('receivedDateTime', ''), reverse=True)
    
            dadosExtraidos = []
            
            if emailsOrdenados and regexConteudo:
                for msg in emailsOrdenados:
                    body = msg.get('body', {}).get('content', '')

                    soup = BeautifulSoup(body, 'html.parser')
                    emailContent = soup.get_text(separator=separador)
                    if show:
                        print(emailContent)
                    matches = re.finditer(regexConteudo, emailContent)

                    for match in matches:
                        dadosExtraidos.append(match.groups())
                else:
                    return dadosExtraidos        
            else:
                return []
            
        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP ao acessar as mensagens: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erro de requisição ao acessar as mensagens: {e}")
            return None
    else:
        print(f"Erro ao obter o token: {result.get('error_description', result.get('error'))}")
        return None
    

def coletarAnexosEmail(
    userEmail: str,
    filtroAssunto: str = None,
    n_emails: int = 500,
    filtroEmail: str = None,
    recebidoApos: datetime.datetime = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
) -> list:
    """
    Coleta anexos de e-mails da caixa de entrada do Outlook.

    Args:
        userEmail (str): O endereço de e-mail do usuário.
        filtroAssunto (str, optional): Filtra o assunto do e-mail (case-sensitive).
        n_emails (int, optional): Número máximo de e-mails a serem buscados.
        filtroEmail (str, optional): Filtra e-mails de um remetente específico.
        recebidoApos (datetime.datetime, optional): Filtra e-mails recebidos após esta data.

    Returns:
        list: Lista de dicionários com os anexos encontrados.
    """
    CLIENT_ID = "d45fc956-3ea0-4c51-93be-c1ac46502c0d"
    CLIENT_SECRET = getCredenciais(572)[1]
    TENANT_ID = "adaa0a29-8e4a-4216-8ac8-187b1608c2e1"
    USER_ID = userEmail
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPES = ["https://graph.microsoft.com/.default"]

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

    result = app.acquire_token_for_client(scopes=SCOPES)
    
    if "access_token" in result:
        tokenAcesso = result["access_token"]
        headers = {"Authorization": f"Bearer {tokenAcesso}"}
        from urllib.parse import quote

        base_url = f"https://graph.microsoft.com/v1.0/users/{USER_ID}/messages"
        filtros = []

        if recebidoApos:
            data_formatada = recebidoApos.isoformat(timespec='seconds') + 'Z'
            filtros.append(f"receivedDateTime ge {data_formatada}")

        if filtroAssunto:
            filtros.append(f"contains(subject,'{filtroAssunto}')")

        if filtroEmail:
            filtros.append(f"from/emailAddress/address eq '{filtroEmail}'")

        filtro_query = ""
        if filtros:
            filtro_query = f"&$filter=" + quote(" and ".join(filtros))

        messagesURL = f"{base_url}?$top={min(n_emails, 1000)}{filtro_query}"

        try:
            response = requests.get(messagesURL, headers=headers)
            response.raise_for_status()
            messages = response.json().get("value", [])

            anexosColetados = []

            for msg in messages:
                assunto = msg.get("subject", "")
                remetente = msg.get("from", {}).get("emailAddress", {}).get("address", "")

                if filtroAssunto and filtroAssunto not in assunto:
                    continue

                if filtroEmail and filtroEmail.lower() != remetente.lower():
                    continue

                # Buscar anexos do e-mail
                idMsg = msg["id"]
                anexosURL = f"https://graph.microsoft.com/v1.0/users/{USER_ID}/messages/{idMsg}/attachments"

                anexosResponse = requests.get(anexosURL, headers=headers)
                anexosResponse.raise_for_status()

                anexos = anexosResponse.json().get("value", [])

                for anexo in anexos:
                    if anexo["@odata.type"] == "#microsoft.graph.fileAttachment":
                        conteudoBytes = base64.b64decode(anexo["contentBytes"])
                        anexosColetados.append({
                            "nome_arquivo": anexo["name"],
                            "conteudo": conteudoBytes,
                            "assunto_email": assunto,
                            "remetente": remetente,
                            "data_recebimento": msg.get("receivedDateTime")
                        })

            return anexosColetados

        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erro de requisição: {e}")
            return None
    else:
        print(f"Erro ao obter o token: {result.get('error_description', result.get('error'))}")
        return None


def resetarTempoSessaoBMG(bmg: Chrome):
        bmg.switch_to.default_content()
        bmg.switch_to.frame("leftFrame")
        bmg.execute_script("document.getElementById('leftFrame').contentWindow.location.reload();")
        print('Refresh BMG com sucesso')
        time.sleep(10)


def resetarTempoSessaoC6(c6: Chrome):
    primeiroLinkToken = c6.current_url
    tokenc6 = primeiroLinkToken.split('=')[-1]
    print(tokenc6)
    time.sleep(5)
    linkGetEtapa = f'https://c6.c6consig.com.br/WebAutorizador/MenuWeb/Consulta/GeDoc/UI.CnAnexarDocumentacao.aspx?FISession={tokenc6}'
    time.sleep(5)


def resetarTempoSessaoFacta(facta: Chrome):
    facta.get('https://desenv.facta.com.br/sistemaNovo/andamentoPropostas.php')



if __name__=="__main__":
    
    email = "dannilo.costa@adpromotora.com.br"
    coletarAnexosEmail(email)
