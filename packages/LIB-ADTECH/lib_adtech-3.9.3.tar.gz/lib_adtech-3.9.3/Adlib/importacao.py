import os
import time
import inspect
import logging
import functools
import threading
import traceback
from time import sleep
from pathlib import Path
from functools import wraps
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from .utils import tokenBotImportacao, chatIdImportacao
from .api import EnumBanco, EnumStatus, EnumProcesso, putStatusRobo, putTicket
from .funcoes import aguardarElemento, esperarElemento, clickarElemento, selectOption, aguardarAlert, mensagemTelegram, setupDriver

class ImportacaoOptions:
    def __init__(self, portabilidade: bool = False, crefisa_cp: bool = False, layout: str = "", empty: bool = False):
        self.PORTABILIDADE = portabilidade
        self.CREFISA_CP = crefisa_cp
        self.LAYOUT = layout
        self.VAZIO = empty


def checkEvent():
    """
    Decorator to check if an event is set before executing the decorated function.
    The event is dynamically retrieved from the function's arguments.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the function's signature and parameter names
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            resetManager = bound_args.arguments.get("resetManager")
            
            if isinstance(resetManager, threading.Event):
                resetManager.set()

            return func(*args, **kwargs)
        return wrapper
    return decorator


@checkEvent()
def importacaoVirtaus(virtaus: Chrome, filepath: Path, nomeBanco: str, enumBanco: EnumBanco, options: ImportacaoOptions = ImportacaoOptions(), resetManager: threading.Event = None) -> int:
    """
    Realiza a rotina de importação de propostas no sistema Virtaus.

    Args:
        virtaus (Chrome): Instância do driver Selenium.
        filepath (Path): Caminho do arquivo a ser importado.
        nomeBanco (str): Nome do banco a ser selecionado.
        enumBanco (EnumBanco): Enum do banco.
        options (ImportacaoOptions): Opções específicas para a importação.
        resetManager (threading.Event, optional): Evento para controle de reinício/encerramento do bot.

    Returns:
        int: Código de status da operação (0 = sucesso, 1 = encerramento via resetManager).
    """
    putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, enumBanco)
    
    portabilidade = "SIM" if options.PORTABILIDADE else "NÃO"
    crefisa_cp = "crefisa_cp" if options.CREFISA_CP else None
    layout = options.LAYOUT
    empty = options.VAZIO

    if empty:
        putStatusRobo(EnumStatus.SEM_PROPOSTA, EnumProcesso.IMPORTACAO, enumBanco)

    else:
        maxTry = 5
        tryCount = 0
        
        while tryCount <= maxTry:
            putStatusRobo(EnumStatus.IMPORTANDO, EnumProcesso.IMPORTACAO, enumBanco)
            tryCount += 1
            try:
                if resetManager:
                    if not resetManager.is_set():   # Finaliza o bot
                        virtaus.quit()
                        return 1
                time.sleep(5)
                virtaus.get('https://adpromotora.virtaus.com.br/portal/p/ad/pageworkflowview?processID=ImportacaoArquivoEsteira')
                aguardarAlert(virtaus)
                
                sleep(10)
                iframe = virtaus.find_elements('tag name','iframe')[0]
                virtaus.switch_to.frame(iframe)

                # Banco
                clickarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').click()
                esperarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').send_keys(nomeBanco)
                sleep(5)
                esperarElemento(virtaus, '/html/body/div/form/div/div[1]/div[2]/div/div[1]/span/span[1]/span/ul/li/input').send_keys(Keys.ENTER)

                # Layout
                if layout:
                    try:
                        selectOption(virtaus, '//*[@id="selectLayout"]', layout)
                    except Exception as e:
                        print(f"Error selecting option: {e}")

                # Portabilidade
                if portabilidade:
                    try:
                        selectOption(virtaus, '//*[@id="selectPortabilidade"]', portabilidade)
                    except Exception as e:
                        print(f"Error selecting option: {e}")
                        
                # Crefisa CP
                if crefisa_cp:
                    try:
                        selectOption(virtaus, '//*[@id="selectCrefisa"]', crefisa_cp)
                    except Exception as e:
                        print(f"Error selecting option: {e}")

                virtaus.switch_to.default_content()          

                clickarElemento(virtaus, '//*[@id="tab-attachments"]/a/span').click()
                sleep(5)
                esperarElemento(virtaus, '//*[@id="lb-input-upload"]')
                
                importarArquivo = aguardarElemento(virtaus, '//*[@id="ecm-navigation-inputFile-clone"]')
                importarArquivo.send_keys(str(filepath))
                sleep(5)
                
                # Upload arquivo
                clickarElemento(virtaus, '//*[@id="workflowActions"]/button[1]').click()
                sleep(5)

                elemento = esperarElemento(virtaus, '/html/body/div[1]/div[3]/div/div/div[2]/div/div/div/div[3]/div[1]/div/div[1]/span/a')
                numeroSolicitacao = elemento.text
                os.remove(str(filepath)) ## Só remover após ter certeza de que foi concluído
                putTicket(numeroSolicitacao, EnumProcesso.IMPORTACAO, enumBanco)
                mensagem = f"Importação Efetuada: <b> {enumBanco.name.replace('_', ' ')} - {numeroSolicitacao}</b> ✅"
                
                if resetManager:
                    resetManager.set()              # Reseta countdown de restart do bot

                mensagemTelegram(tokenBotImportacao, chatIdImportacao, mensagem)
                putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, enumBanco)
                
                os.remove(str(filepath))
                
                return 0

            except Exception as e:
                print(e)
                print('Erro ao tentar importar no Virtaus')
                putStatusRobo(EnumStatus.ERRO, EnumProcesso.IMPORTACAO, enumBanco)


def loopImportacao(enumBanco: EnumBanco, tempoLimite=25, prefs=dict()):
    def tempoDecorrido(t: float):
        return (time.time() - t) / 60
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    virtaus, bank = setupDriver(numTabs=2, experimentalOptions=prefs, autoSwitch=True)
                    logging.info(f"Driver inicializado!")
                    ultimaExecucaoBemSucedida = time.time()

                    while tempoDecorrido(ultimaExecucaoBemSucedida) <= tempoLimite:
                        func(virtaus, bank, *args, **kwargs)
                        ultimaExecucaoBemSucedida = time.time()
                        logging.info(f"Importação bem sucedida!")
                    
                    logging.info(f"Tarefa será reiniciada")
                    virtaus.quit()
                    logging.info(f"Driver finalizado")
                except KeyboardInterrupt:
                    logging.info("Execução interrompida pelo usuário.")
                    putStatusRobo(EnumStatus.DESLIGADO, EnumProcesso.IMPORTACAO, enumBanco)
                except Exception as e:
                    logging.error(f"Erro inesperado: {e}")
                    print(traceback.print_exc())
        return wrapper
    return decorator
