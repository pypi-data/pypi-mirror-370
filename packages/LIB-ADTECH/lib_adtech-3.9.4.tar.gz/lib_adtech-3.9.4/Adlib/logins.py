import os
import time
import inspect
import asyncio
from enum import Enum
from typing import Callable
from functools import wraps
from .api import storeCaptcha, solveCaptcha
from .enums import EnumBanco, EnumProcesso
from .utils import loginChatIdMapping, aguardarTempo, tokenBotLogin, chatIdUsuariosLogin
from .funcoes import setupDriver, esperarElemento, mensagemTelegram, aguardarAlert, clickarElemento, \
                          enviarCaptcha, saveCaptchaImage, solveReCaptcha, coletarPinBanrisul, getCredenciais
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys


formatEnumName = lambda x: x.name.replace('_', ' ') if x is not None else ''

class LoginReturn(Enum):
    ACESSO_SIMULTANEO = "Acesso simultâneo"
    CAPTCHA_INCORRETO = "Captcha incorreto"
    LOGIN_COM_SUCESSO = "Login com sucesso"
    CREDENCIAIS_INVALIDAS = "Credenciais inválidas"
    USUARIO_INATIVO = "Usuário inativo"
    ERRO_AO_LOGAR = "Erro ao logar"
    RESETAR_SENHA = "Resetar senha"
    ATUALIZAR_DADOS = "Atualizar Dados Cadastrais"


def login_decorator(func):

    @wraps(func)
    def wrapper(driver: Chrome, usuario: str, senha: str, *args):
        try:
            returns = func(driver, usuario, senha, *args)

            if isinstance(returns, tuple) and len(returns) == 3:
                loginReturn, enumBanco, enumProcesso = returns
            elif isinstance(returns, tuple) and len(returns) == 2:
                loginReturn, enumBanco = returns
            else:
                loginReturn = returns
                enumBanco = enumProcesso = None

            match loginReturn:
                case LoginReturn.LOGIN_COM_SUCESSO:
                    pass
                    # mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Login com sucesso! {formatEnumName(enumBanco)} {formatEnumName(enumProcesso)} ✅")
                case LoginReturn.RESETAR_SENHA:
                    mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Resetar a senha! {formatEnumName(enumBanco)} {formatEnumName(enumProcesso)} ⚠️")
                case LoginReturn.CREDENCIAIS_INVALIDAS:
                    mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Credenciais inválidas! {formatEnumName(enumBanco)} {formatEnumName(enumProcesso)} ❌")
                case LoginReturn.USUARIO_INATIVO:
                    mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Usuário inativo! {formatEnumName(enumBanco)} {formatEnumName(enumProcesso)} ❌")
                case LoginReturn.ATUALIZAR_DADOS:
                    mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Atualizar dados cadastrais! {formatEnumName(enumBanco)} {formatEnumName(enumProcesso)} ❌")
                case LoginReturn.ERRO_AO_LOGAR:
                    mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Erro ao fazer login! {formatEnumName(enumBanco)} {formatEnumName(enumProcesso)} ❌")
                
                # if loginReturn not in [LoginReturn.LOGIN_COM_SUCESSO, LoginReturn.ERRO_AO_LOGAR]:
                # input("Não foi possível logar, verifique o robô.")
                
            time.sleep(10)
            return loginReturn

        except Exception as e:
            print(f"Erro ao realizar login: {func.__name__}")
            print(e)
    return wrapper


def captcha_decorator(loginFunc: Callable[[Chrome, str, str, EnumProcesso], tuple[LoginReturn, EnumBanco]]) -> LoginReturn:
    @wraps(loginFunc)
    def wrapper(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso) -> tuple[LoginReturn, str, str]:
        while True:
            loginReturn, enumBanco, enumProcesso = loginFunc(driver, usuario, senha, enumProcesso)
            loginReturn, enumBanco, enumProcesso = loginFunc(driver, usuario, senha, enumProcesso)
            
            if enumProcesso:
                global chatId    
                chatId = loginChatIdMapping[enumProcesso]

            if loginReturn == LoginReturn.ACESSO_SIMULTANEO:
                mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Acesso simultâneo! {formatEnumName(enumBanco)} {formatEnumName(enumProcesso)} ⚠️")
                mensagemTelegram(tokenBotLogin, chatIdUsuariosLogin, f"Aguarde 30 minutos...")
                asyncio.run(aguardarTempo(60*30))

            elif loginReturn != LoginReturn.CAPTCHA_INCORRETO:
                return loginReturn, enumBanco, enumProcesso


            aguardarAlert(driver)
            driver.refresh()
            aguardarAlert(driver)

    return wrapper


@login_decorator
def loginItau(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    
    def checkLogin() -> LoginReturn:
        if driver.current_url == "https://portal.icconsig.com.br/proposal":
            return LoginReturn.LOGIN_COM_SUCESSO

    driver.get('https://portal.icconsig.com.br/')
    time.sleep(10)

    iframe = esperarElemento(driver, '/html/body/cc-lib-dialog/div/div[1]/div[2]/div/app-auth-dialog/div/iframe', tempoEspera=20)
    driver.switch_to.frame(iframe)

    esperarElemento(driver, '//*[@id="username"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="password"]').send_keys(senha + Keys.ENTER)
    
    return checkLogin(), EnumBanco.ITAU, enumProcesso


@login_decorator
def loginAmigoz(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    
    def checkLogin():
        if "https://amigozconsig.com.br/contratos" in driver.current_url:
            return LoginReturn.LOGIN_COM_SUCESSO
        return LoginReturn.ERRO_AO_LOGAR
    
    driver.get("https://amigozconsig.com.br/login")

    esperarElemento(driver, '//*[@id="identifier"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="password"]').send_keys(senha)
    clickarElemento(driver, '//button[.//span[text()="Continuar"]]').click()
    return checkLogin(), EnumBanco.AMIGOZ, enumProcesso


@login_decorator
def loginHappy(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    
    def checkLogin():
        if "https://portal.happyconsig.com.br/contratos" in driver.current_url:
            return LoginReturn.LOGIN_COM_SUCESSO
        return LoginReturn.ERRO_AO_LOGAR
    
    driver.get("https://portal.happyconsig.com.br/login")

    esperarElemento(driver, '//*[@id="identifier"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="password"]').send_keys(senha)
    clickarElemento(driver, '//button[.//span[text()="Continuar"]]').click()
    #return checkLogin(), EnumBanco.AMIGOZ, enumProcesso


@login_decorator
def loginCrefisaCP(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:

    driver.get("https://app1.gerencialcredito.com.br/CREFISA/default.asp")

    esperarElemento(driver, '//*[@id="txtUsuario"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="txtSenha"]').send_keys(senha)

    solveReCaptcha(driver)
    esperarElemento(driver, '//*[@id="btnLogin"]').click()
    
    return LoginReturn.LOGIN_COM_SUCESSO, EnumBanco.CREFISA_CP, enumProcesso


@login_decorator
def loginC6(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:

    def checkLogin() -> LoginReturn:
        text = aguardarAlert(driver)

        if "Usuário ou senha inválido" in text:
            return LoginReturn.CREDENCIAIS_INVALIDAS
        if "Usuário inativo ou afastado" in text:
            return LoginReturn.USUARIO_INATIVO
        if "Usuário já autenticado" in text:
            return LoginReturn.LOGIN_COM_SUCESSO
        if esperarElemento(driver, '//span[contains(text(), "Atualizar meus Dados Cadastrais")]', tempoEspera=3, debug=False):
            return LoginReturn.ATUALIZAR_DADOS
        LoginReturn.ERRO_AO_LOGAR

    driver.get("https://c6.c6consig.com.br/WebAutorizador/Login/AC.UI.LOGIN.aspx")

    esperarElemento(driver, "//*[@id='EUsuario_CAMPO']").send_keys(usuario)
    esperarElemento(driver, "//*[@id='ESenha_CAMPO']").send_keys(senha)
    clickarElemento(driver, '//*[@id="lnkEntrar"]').click()

    return checkLogin(), EnumBanco.C6, enumProcesso
    

@login_decorator
def loginDigio(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:

    def checkLogin() -> LoginReturn:
        text = aguardarAlert(driver)
        
        if "Usuário ou senha inválido" in text:
            return LoginReturn.CREDENCIAIS_INVALIDAS
        if "Usuário inativo ou afastado" in text:
            return LoginReturn.USUARIO_INATIVO
        if "Usuário já autenticado" in text:
            return LoginReturn.LOGIN_COM_SUCESSO
        if esperarElemento(driver, '//span[contains(text(), "Alteração de Senha")]', tempoEspera=3, debug=False):
            return LoginReturn.RESETAR_SENHA
        if esperarElemento(driver, '//span[contains(text(), "Atualizar meus Dados Cadastrais")]', tempoEspera=3, debug=False):
            return LoginReturn.ATUALIZAR_DADOS
            
        LoginReturn.ERRO_AO_LOGAR

    driver.get("https://funcaoconsig.digio.com.br/FIMENU/Login/AC.UI.LOGIN.aspx")

    esperarElemento(driver, "//*[@id='EUsuario_CAMPO']").send_keys(usuario)
    esperarElemento(driver, "//*[@id='ESenha_CAMPO']").send_keys(senha)
    clickarElemento(driver, '//*[@id="lnkEntrar"]').click()
    
    return checkLogin(), EnumBanco.DIGIO, enumProcesso


@login_decorator
def loginBlip(driver: Chrome, usuario: str, senha: str) -> LoginReturn:

    driver.get('https://takegarage-7ah6a.desk.blip.ai/')
    time.sleep(5)
    shadowPrincipal = driver.find_element('css selector', 'body > bds-theme-provider > bds-grid > bds-grid.form_space.host.direction--undefined.justify_content--center.flex_wrap--undefined.align_items--center.xxs--12.xs--undefined.sm--undefined.md--6.lg--undefined.xg--undefined.gap--undefined.xxsoffset--undefined.xsoffset--undefined.smoffset--undefined.mdoffset--undefined.lgoffset--undefined.xgoffset--undefined.padding--undefined.margin--undefined.hydrated > bds-grid.login-content.host.direction--column.justify_content--undefined.flex_wrap--undefined.align_items--undefined.xxs--10.xs--6.sm--undefined.md--6.lg--undefined.xg--undefined.gap--2.xxsoffset--undefined.xsoffset--undefined.smoffset--undefined.mdoffset--1.lgoffset--undefined.xgoffset--undefined.padding--undefined.margin--undefined.hydrated > bds-grid.host.direction--column.justify_content--undefined.flex_wrap--undefined.align_items--undefined.xxs--undefined.xs--undefined.sm--undefined.md--undefined.lg--undefined.xg--undefined.gap--2.xxsoffset--undefined.xsoffset--undefined.smoffset--undefined.mdoffset--undefined.lgoffset--undefined.xgoffset--undefined.padding--undefined.margin--undefined.hydrated')
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadowPrincipal)

    shadow_host = driver.find_element('css selector', '#email-input')
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
    shadow_root.find_element('class name', 'input__container__text').send_keys(usuario)

    # Shadow host Senha
    shadow_host = driver.find_element('css selector', '#password-input')
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
    shadow_root.find_element('css selector', 'div > div.input__container > div > input').send_keys(senha + Keys.ENTER + Keys.ENTER)
    time.sleep(5)


@login_decorator
def loginFacta(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:

    def checkLogin() -> LoginReturn:
        if esperarElemento(driver, '//*[@id="divAlertaMsg"][contains(text(), "SUA SENHA PRECISA SER ALTERADA!")]', tempoEspera=3, debug=False):
            return LoginReturn.RESETAR_SENHA
        
        if esperarElemento(driver, '//*[@id="divAlertaMsg"][contains(text(), "Usuário/senha incorretos!")]', tempoEspera=3, debug=False):
            return LoginReturn.CREDENCIAIS_INVALIDAS

        if driver.current_url == "https://desenv.facta.com.br/sistemaNovo/dashboard.php":
            return LoginReturn.LOGIN_COM_SUCESSO
        
        return LoginReturn.ERRO_AO_LOGAR
    
    driver.get('https://desenv.facta.com.br/sistemaNovo/login.php')
    
    esperarElemento(driver, '//*[@id="login"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="senha"]').send_keys(senha)

    esperarElemento(driver,'//*[@id="btnLogin"]').click()

    return checkLogin(), EnumBanco.FACTA, enumProcesso


@login_decorator
def loginMargem(driver: Chrome, usuario: str, senha: str) -> LoginReturn:
    driver.get('https://adpromotora.promobank.com.br/') 

    esperarElemento(driver, '//*[@id="inputUsuario"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="passField"]').send_keys(senha + Keys.ENTER)

    return LoginReturn.LOGIN_COM_SUCESSO, EnumBanco.PROMOBANK


def loginBanrisul(driver: Chrome, usuario: str, senha: str, email: str = None, pasta: str = ''):
    driver.get('https://bemweb.bempromotora.com.br/autenticacao/login')

    esperarElemento(driver, '//*[@id="user"]').send_keys(usuario)
    esperarElemento(driver, '//button[text()="Avançar"]').click()
    time.sleep(5)

    esperarElemento(driver, '//*[@id="password"]').send_keys(senha)
    esperarElemento(driver, '//button[text()="Entrar"]').click()
    
    inputPIN = esperarElemento(driver, '//*[@id="pin"]', debug=False)

    if inputPIN:
        while True:
            if email:            
                time.sleep(10) # Aguarda o email chegar
                pin = coletarPinBanrisul(email, pasta)
                try:
                    inputPIN.clear()
                    inputPIN.send_keys(pin)
                    time.sleep(5)
                    esperarElemento(driver, '//button[text()="Entrar"]').click()
                    time.sleep(5)
                    break
                except:
                    print('Tente logar novamente')
                    input("Digite o PIN...")
            else:
                input("Digite o PIN...")
                break

    return LoginReturn.LOGIN_COM_SUCESSO, EnumBanco.BANRISUL



@login_decorator
def loginCashCard(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    
    driver.get(f"https://front.meucashcard.com.br/WebAppBPOCartao/Login/ICLogin?ReturnUrl=%2FWebAppBPOCartao%2FPages%2FProposta%2FICPropostaCartao")
     
    esperarElemento(driver, '//*[@id="txtUsuario_CAMPO"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="txtSenha_CAMPO"]').send_keys(senha)

    esperarElemento(driver, '//*[@id="bbConfirmar"]').click()

    return LoginReturn.LOGIN_COM_SUCESSO, EnumBanco.MEU_CASH_CARD, enumProcesso


@login_decorator
def loginVirtaus(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    
    def checkLogin() -> LoginReturn:
        if "https://adpromotora.fluigidentity.com" in driver.current_url:
            return LoginReturn.LOGIN_COM_SUCESSO
    
    
    driver.get("https://app.fluigidentity.com/ui/login")
    time.sleep(5)

    loginReturn = checkLogin()
    if loginReturn == LoginReturn.LOGIN_COM_SUCESSO:
        return loginReturn
    
    esperarElemento(driver, '//*[@id="username"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="password"]').send_keys(senha + Keys.ENTER)
    
    loginReturn = checkLogin()

    return loginReturn, EnumBanco.VIRTAUS, enumProcesso


@login_decorator
def loginPaulista(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    driver.get("https://creditmanager.bancopaulista.com.br/Login.aspx?ReturnUrl=%2fConcessao%2fMonitor.aspx")
    
    esperarElemento(driver, '//*[@id="MainContent_txtUsuario"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="MainContent_txtSenha"]').send_keys(senha)
    
    esperarElemento(driver, '//*[@id="MainContent_Button1"]').click()
    
    return LoginReturn.LOGIN_COM_SUCESSO, EnumBanco.ITAU, enumProcesso


@login_decorator
def loginSafra(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    
    def checkLogin() -> LoginReturn:
        if esperarElemento(driver, '//*[@id="toast-container"]', tempoEspera=3, debug=False):
            return LoginReturn.USUARIO_INATIVO
        if esperarElemento(driver, '//*[@id="lblMensagemErro"]', tempoEspera=3, debug=False):
            return LoginReturn.CREDENCIAIS_INVALIDAS
        if driver.current_url == "https://epfweb.safra.com.br/":
            return LoginReturn.LOGIN_COM_SUCESSO
        
        return LoginReturn.ERRO_AO_LOGAR
    
    driver.get("https://epfweb.safra.com.br/")
    
    esperarElemento(driver, '//*[@id="txtUsuario"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="txtSenha"]').send_keys(senha)

    buttonLogin = esperarElemento(driver, '//*[@id="btnEntrar"]').click()

    carregando = esperarElemento(driver, '//*[@id="sec-overlay" and @style="display: block;"]', debug=False)

    while carregando:
        carregando = esperarElemento(driver, '//*[@id="sec-overlay" and @style="display: block;"]', tempoEspera=1, debug=False)
        time.sleep(3)
    
    buttonLogin = esperarElemento(driver, '//*[@id="btnEntrar"]').click()

    return checkLogin(), EnumBanco.SAFRA, enumProcesso
    
@login_decorator
def loginMaster(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    
    driver.get('https://autenticacao.bancomaster.com.br/login')

    esperarElemento(driver, '//*[@id="mat-input-0"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="mat-input-1"]').send_keys(senha)
    clickarElemento(driver, '/html/body/app-root/app-login/div/div[2]/mat-card/mat-card-content/form/div[3]/button[2]').click()
    
    if acessoSimultaneo := clickarElemento(driver, '//*[@id="#sim_button_id"]', tempoEspera=5, debug=False):
        acessoSimultaneo.click()
    

    return LoginReturn.LOGIN_COM_SUCESSO, EnumBanco.MASTER, enumProcesso



@login_decorator
@captcha_decorator
def loginIBConsig(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso) -> tuple[LoginReturn, EnumBanco]:
    
    enumBanco = EnumBanco.ITAU

    def checkLogin() -> LoginReturn:
        if esperarElemento(driver, '//*[@id="Table_01"]/tbody/tr[3]/td/table[2]/tbody/tr[1]/td/font[contains(text(), "A palavra de verificação está inválida")]', tempoEspera=5, debug=False):
            return LoginReturn.CAPTCHA_INCORRETO
        if esperarElemento(driver, '//*[@id="Table_01"]/tbody/tr[3]/td/table[2]/tbody/tr[1]/td/font[contains(text(), "acesso simultâneo")]', tempoEspera=5, debug=False):
            return LoginReturn.ACESSO_SIMULTANEO
        if esperarElemento(driver, '//*[@id="Table_01"]//font[contains(normalize-space(text()), "Usuário e/ou senha inválido")]', tempoEspera=3, debug=False):
            return LoginReturn.CREDENCIAIS_INVALIDAS
        if driver.current_url == "https://www.ibconsigweb.com.br/principal/fsconsignataria.jsp":
            return LoginReturn.LOGIN_COM_SUCESSO
        return LoginReturn.ERRO_AO_LOGAR
    
    driver.get("https://www.ibconsigweb.com.br/")

    esperarElemento(driver, '/html/body/table/tbody/tr[2]/td[3]/table/tbody/tr/td/form/table/tbody/tr[1]/td[3]/input').send_keys(usuario)
    esperarElemento(driver, '/html/body/table/tbody/tr[2]/td[3]/table/tbody/tr/td/form/table/tbody/tr[2]/td[2]/font/strong/input').send_keys(senha)
                                     
    captchaElement = esperarElemento(driver, '/html/body/table/tbody/tr[2]/td[3]/table/tbody/tr/td/form/table/tbody/tr[4]/td/table/tbody/tr[2]/td/iframe')

    imgPath = saveCaptchaImage(captchaElement, enumBanco, enumProcesso)

    captcha = solveCaptcha(imgPath) # enviarCaptcha(imgPath, enumBanco, enumProcesso)

    try:
        esperarElemento(driver, '/html/body/table/tbody/tr[2]/td[3]/table/tbody/tr/td/form/table/tbody/tr[4]/td/table/tbody/tr[1]/td[2]/input').send_keys(captcha)

        esperarElemento(driver, '/html/body/table/tbody/tr[2]/td[3]/table/tbody/tr/td/form/table/tbody/tr[4]/td/table/tbody/tr[1]/td[3]/a').click()
        time.sleep(10)
    except Exception as e:
        print(e)
        
    loginReturn = checkLogin()

    return loginReturn, enumBanco, enumProcesso


@login_decorator
@captcha_decorator
def loginBMG(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso) -> tuple[LoginReturn, EnumBanco]:
    
    def fecharAbasPopUp():
        substring = "bmgconsig"
        originalTab = driver.current_window_handle

        popups = [handle for handle in driver.window_handles if handle != originalTab]

        for handle in popups:
            driver.switch_to.window(handle)
            if substring in driver.current_url:
                driver.close()

        driver.switch_to.window(originalTab)

    def checkLoginBMG() -> LoginReturn:

        if esperarElemento(driver, '//*[@id="div-error"]/span[contains(text(), "A palavra de verificação está inválida.")]', tempoEspera=3, debug=False):
            return LoginReturn.CAPTCHA_INCORRETO
        
        if esperarElemento(driver, '//*[@id="div-error"]/span[contains(text(), "Usuário/Senha inválidos")]', tempoEspera=3, debug=False):
            return LoginReturn.CREDENCIAIS_INVALIDAS
        
        if esperarElemento(driver, '//*[@id="div-error"]/span[contains(text(), "Usuário se encontra bloqueado")]', tempoEspera=3, debug=False):
            return LoginReturn.USUARIO_INATIVO

        if esperarElemento(driver, '//*[@id="div-error"]/span[contains(text(), "tentativa de acesso simultâneo")]', tempoEspera=3, debug=False):
            return LoginReturn.ACESSO_SIMULTANEO
        
        driver.switch_to.frame(esperarElemento(driver, '//*[@id="rightFrame"]'))

        if esperarElemento(driver, '//font[contains(text(), "A sua senha expirou")]', tempoEspera=3, debug=False):
            return LoginReturn.RESETAR_SENHA
        
        driver.switch_to.default_content()
        
        if driver.current_url == "https://www.bmgconsig.com.br/principal/fsconsignataria.jsp":
            return LoginReturn.LOGIN_COM_SUCESSO
        
        return LoginReturn.ERRO_AO_LOGAR
    
    enumBanco = EnumBanco.BMG
    
    driver.get("https://www.bmgconsig.com.br/Index.do?method=prepare")

    esperarElemento(driver,'//*[@id="usuario"]').send_keys(usuario + Keys.ENTER)
    esperarElemento(driver, '//*[@id="j_password"]').send_keys(senha + Keys.ENTER)

    captchaElement = esperarElemento(driver, '/html/body/section[1]/div/div[1]/div/div/form/div[3]/iframe')

    imgPath = saveCaptchaImage(captchaElement, enumBanco, enumProcesso)

    captcha = solveCaptcha(imgPath) # enviarCaptcha(imgPath, enumBanco, enumProcesso)
    try:
        esperarElemento(driver, '//*[@id="captcha"]').send_keys(captcha)
        esperarElemento(driver, '//*[@id="bt-login"]').click()
        time.sleep(5)
    except Exception as e:
        print(e)

    loginReturn = checkLoginBMG()

    # if loginReturn == LoginReturn.LOGIN_COM_SUCESSO:
    #     fecharAbasPopUp()

    return loginReturn, enumBanco, enumProcesso


@login_decorator
@captcha_decorator
def loginDaycoval(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso) -> tuple[LoginReturn, EnumBanco]:

    enumBanco = EnumBanco.DAYCOVAL

    def checkLogin():
        text = aguardarAlert(driver)

        if "Código da Imagem Inválido" in text:
            return LoginReturn.CAPTCHA_INCORRETO
        
        if "Usuário ou senha inválido" in text:
            return LoginReturn.CREDENCIAIS_INVALIDAS
        
        if "expirar" in text:
            return LoginReturn.RESETAR_SENHA
        
        if driver.current_url == "https://consignado.daycoval.com.br/Autorizador/": # URL após login bem sucedido
            return LoginReturn.LOGIN_COM_SUCESSO
        
        return LoginReturn.ERRO_AO_LOGAR
    
    aguardarAlert(driver)

    driver.get('https://consignado.daycoval.com.br/Autorizador/Login/AC.UI.LOGIN.aspx')
    time.sleep(5)
    
    esperarElemento(driver, '//*[@id="Captcha_lkReGera"]').click()
    time.sleep(1)
    esperarElemento(driver, '//*[@id="EUsuario_CAMPO"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="ESenha_CAMPO"]').send_keys(senha)
    
    captchaElement = driver.find_element('xpath', '//*[@id="form1"]/img')#captchaElement = esperarElemento(driver, '//*[@id="form1"]/img')

    imgPath = saveCaptchaImage(captchaElement, enumBanco, enumProcesso)

    captcha = solveCaptcha(imgPath) # enviarCaptcha(imgPath, enumBanco, enumProcesso)
    
    esperarElemento(driver, '//*[@id="Captcha_txtCaptcha_CAMPO"]').send_keys(captcha)

    esperarElemento(driver, '//*[@id="lnkEntrar"]').click()
    time.sleep(5)
    
    loginReturn = checkLogin()

    return loginReturn, enumBanco, enumProcesso


def logoutBMG(bmg: Chrome):
    
    bmg.get("https://www.bmgconsig.com.br/login/logout.jsp")
    try:
        esperarElemento(bmg, '//*[@id="buttonLink"]').click()
        time.sleep(3)
        aguardarAlert(bmg)
    except:
        pass
    time.sleep(5)


@login_decorator
def loginOle(driver: Chrome, usuario: str, senha: str, enumProcesso: EnumProcesso = None) -> LoginReturn:
    driver.get('https://ola.oleconsignado.com.br/')
    esperarElemento(driver, '//*[@id="Login"]').send_keys(usuario)
    esperarElemento(driver, '//*[@id="Senha"]').send_keys(senha + Keys.ENTER)
    
    esperarElemento(driver, '//*[@id="botaoAcessar"]').click()

    return LoginReturn.LOGIN_COM_SUCESSO, EnumBanco.OLE, enumProcesso


if __name__=="__main__":
    # prefs = {
    #     "useAutomationExtension": False,
    #     "excludeSwitches": ['enable-automation']
    # }

    driver = setupDriver()

    user, senha = getCredenciais(357)#"SE07547063543A", "G@O1987Ts"#getCredenciais(409)
    
    loginBanrisul(driver, user, senha, "dannilo.costa@adpromotora.com.br", "PIN Banrisul")

    # loginSafra(driver, user, senha)

    # loginOle(driver, user, senha)

    # user, senha = getCredenciais(356)
    # loginSafra(driver, user, senha)

    input("FECHAR????")
    input("FECHAR????")
    input("FECHAR????")
    input("FECHAR????")
    input("FECHAR????")