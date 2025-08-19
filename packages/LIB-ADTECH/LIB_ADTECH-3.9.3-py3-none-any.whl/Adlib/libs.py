# Time & System
import os
import time
import shutil
import zipfile
import datetime
import requests
from bs4 import BeautifulSoup
 
# Selenium
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
 
 
# Adlib
from .api import EnumBanco, EnumProcesso, EnumStatus, putStatusRobo
from .utils import meses, chatIdMapping
from .logins import loginBMG, loginC6, loginDaycoval, loginFacta, loginVirtaus, loginOle, loginBanrisul
from .virtaus import finalizarSolicitacao, assumirSolicitacao, FiltrosSolicitacao, resetarTempoSessaoBMG, resetarTempoSessaoC6, resetarTempoSessaoFacta
from .funcoes import esperarElemento, esperarElementos, selectOption, aguardarDownload, \
                          clickElement,getCredenciais, setupDriver, clickCoordenada, \
                          getNumeroSolicitacao, mensagemTelegram

from .apiValid import verificarFraude, obterToken
from .integracao import integracaoVirtaus
from .apiConferirRg import enviarDocumentos
 
# Telegram Tokens
tokenImportarDoc = '7333756979:AAFDUBW0KKaub1ciwKrCb3Q7ncVRhfZHfEM'
tokenBotLogin = '7505814396:AAFEm1jwG3xwd8N41j_viCCxgZUBT-XhbbY'

 
__all__ = [
    "os", "shutil", "time", "datetime", "requests",
    "webdriver", "Chrome", "Service", "Keys", "ChromeDriverManager", "ActionChains", "WebDriverWait",
    "setupDriver", "esperarElemento", "esperarElementos", "clickCoordenada", "aguardarDownload", "selectOption",
    "loginBMG", "loginVirtaus", "assumirSolicitacao", "FiltrosSolicitacao", "getNumeroSolicitacao",
    "putStatusRobo", "EnumStatus", "EnumProcesso", "EnumBanco", "chatIdMapping", "resetarTempoSessaoBMG", "resetarTempoSessaoC6", "resetarTempoSessaoFacta",
    "integracaoVirtaus", "getCredenciais", "mensagemTelegram", "tokenImportarDoc", "meses",
    'loginFacta','loginC6', 'loginDaycoval', 'loginBanrisul', 'loginOle', 'obterToken', 'verificarFraude',
    'enviarDocumentos', 'finalizarSolicitacao', 'clickElement','zipfile','BeautifulSoup', 'NoSuchElementException',
]