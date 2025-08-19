import os
import time
import datetime
import threading
from typing import Callable
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
from urllib.parse import parse_qs, urlparse
from .logins import loginVirtaus
from .api import EnumBanco, EnumStatus, EnumProcesso, putStatusRobo
from .utils import chatIdMapping, botTokenMapping, importarPastaMonitoramento
from .funcoes import setupDriver, esperarElemento, esperarElementos, clickarElemento, selectOption, getCredenciais, aguardarElemento, mensagemTelegram



class FormularioSolicitacao:
    """
        Classe que representa o formulário de solicitação no sistema Virtaus.
        Contém mapeamentos dos campos do formulário para facilitar a automação.
    """
    def __init__(self, virtaus: Chrome):
        self.solicitacao = getNumeroSolicitacao(virtaus)
        
        menuFrame = esperarElemento(virtaus, '//*[@id="workflowView-cardViewer"]')
        virtaus.switch_to.frame(menuFrame)

        self.login = aguardarElemento(virtaus, '//*[@id="nomeLogin"]').get_attribute('value')
        self.ferramenta = aguardarElemento(virtaus, '//*[@id="ferramenta"]').get_attribute('value')
        self.senha = aguardarElemento(virtaus, '//*[@id="senhaLogin"]').get_attribute('value')
        self.nome = aguardarElemento(virtaus, '//*[@id="contaPessoaNome"]').get_attribute('value')
        self.email = aguardarElemento(virtaus, '//*[@id="contaEmail"]').get_attribute('value')
        self.telefone = aguardarElemento(virtaus, '//*[@id="contaTelefone"]').get_attribute('value')
        self.rg = aguardarElemento(virtaus, '//*[@id="contaRg"]').get_attribute('value')
        self.cpf = aguardarElemento(virtaus, '//*[@id="contaCpf"]').get_attribute('value')
        self.uf = aguardarElemento(virtaus, '//*[@id="contaUF"]').get_attribute('value')
        self.nomeMae = aguardarElemento(virtaus, '//*[@id="contaNomeMae"]').get_attribute('value')
        self.idConta = aguardarElemento(virtaus, '//*[@id="contaIdCode"]').get_attribute('value')
        self.nomeConta = aguardarElemento(virtaus, '//*[@id="contaNome"]').get_attribute('value')
        self.dataNascimento = aguardarElemento(virtaus, '//*[@id="contaDataNascimento"]').get_attribute('value')
        self.relacionamentoConta = aguardarElemento(virtaus, '//*[@id="relacionamentoConta"]').get_attribute('value')

        virtaus.switch_to.default_content()


class FiltrosSolicitacao:

    AGUARDANDO_AVERBACAO = "Aguardando Averbação | AnaliseAverbacao"
    AGUARDANDO_SENHA_BANCO = "Aguardando Senha do Banco | EmissaoDeNovaSenhaLoginExterno"
    AGUARDANDO_TERCEIROS = "Aguardando Terceiros | Notificacao Pagamento Devolvido"
    ANALISA_RECLAMACAO = "Analisa Reclamacao | Criacao de Eventos Reclamacao"
    ANALISAR_CONTRATO_NO_BANCO = "AnalisarContratoNoBanco | AnaliseDaMonitoria"
    ANALISE = "Analise | AnaliseAverbacao"
    ATENDE_AGUARDANDO_TERCEIROS = "Atende Aguardando Terceiros | Criacao de Eventos Reclamacao"
    ATENDIMENTO_ALTERACAO_STATUS_LOGIN = "Atendimento | AlteracaoDoStatusDeLogin"
    CRIACAO = "Atendimento | CriacaoDeLoginExternoParaParceiro"
    RESET = "Atendimento | EmissaoDeNovaSenhaLoginExterno"
    ATENDIMENTO_EMISSAO_NOVA_SENHA_FUNCIONARIO = "Atendimento | EmissaoDeNovaSenhaLoginExternoFuncionario"
    LIBERAR_PROPOSTA = "Liberar Proposta"
    AGUARDANDO_VIDEOCHAMADA = "Aguardando Videochamada | AnaliseDeEsteira"
    COLETAR_DOCUMENTOS = "Analisar Documentos"


mapping = {
    FiltrosSolicitacao.CRIACAO : EnumProcesso.CRIACAO,
    FiltrosSolicitacao.RESET : EnumProcesso.RESET,
    FiltrosSolicitacao.COLETAR_DOCUMENTOS : EnumProcesso.ANALISE_DOCUMENTOS,
    FiltrosSolicitacao.AGUARDANDO_SENHA_BANCO : EnumProcesso.RESET
}



def getNumeroSolicitacao(virtaus: Chrome):
    """
    Extrai o número da solicitação (processInstanceId) da URL atual do navegador no Virtaus.

    Args:
        virtaus (Chrome): Instância do navegador Chrome controlada pelo Selenium, já na página do Virtaus.

    Returns:
        str: O número da solicitação que se encontrado na URL; caso contrário, retorna None.
    """
    time.sleep(5)

    urlAtual = virtaus.current_url
 
    parsed_url = urlparse(urlAtual)
    query_params = parse_qs(parsed_url.query)
 
    if 'app_ecm_workflowview_processInstanceId' in query_params:
        return query_params['app_ecm_workflowview_processInstanceId'][0]
    return None


def assumirSolicitacao(virtaus: Chrome,
                       nomeFerramenta: str,
                       enumBanco: EnumBanco,
                       tipoFiltro: FiltrosSolicitacao,
                       localizacao: str = None, 
                       HORA_FINALIZACAO: int = 19,
                       loopInfinito: bool = True,
                       resetSessao: Callable[[Chrome], None] = None,
                       driverReset: Chrome = None,
                       resetEvent: threading.Event = None) -> FormularioSolicitacao:
    """
        Função para assumir uma solicitação no sistema Virtaus com base em filtros específicos e nome da ferramenta.

        Esta função realiza o seguinte fluxo:
        - Navega para a página de tarefas centralizadas no sistema Virtaus.
        - Seleciona um filtro específico fornecido no parâmetro `tipoFiltro`.
        - Busca pelo nome da ferramenta no campo de pesquisa.
        - Seleciona o primeiro item correspondente à ferramenta.
        - Clica no botão "Assumir Tarefa" para iniciar o processamento.

        Parâmetros:
        - virtaus (Chrome): Instância do navegador Chrome controlada pelo Selenium.
        - nomeFerramenta (str): Nome da ferramenta para buscar nas solicitações.
        - enumBanco (EnumBanco): Enumeração que identifica o banco associado à solicitação.
        - tipoFiltro (FiltrosSolicitacao): Filtro a ser utilizado para categorizar as solicitações.
        - HORA_FINALIZACAO (int): Horário limite para finalizar a execução da função (padrão: "19:00").

        Exceções:
        - A função trata exceções durante a execução, exibindo mensagens informativas e aguardando para novas tentativas.
    """

    enumProcesso = mapping[tipoFiltro]
    
    putStatusRobo(EnumStatus.LIGADO, enumProcesso, enumBanco)

    while True:
        virtaus.get("https://adpromotora.virtaus.com.br/portal/p/ad/pagecentraltask")

        try:
            qntBotoes = len(esperarElementos(virtaus, '//*[@id="centralTaskMenu"]/li'))
            idxBtn = qntBotoes - 1
            
            tarefasEmPool = clickarElemento(virtaus, f'//*[@id="centralTaskMenu"]/li[{idxBtn}]/a', debug=False)

            if tarefasEmPool:
                tarefasEmPool.click()

                # Seleciona o filtro de "Emissão De Nova Senha Login Externo"
                filtroProcesso = clickarElemento(virtaus, f'//*[@id="centralTaskMenu"]/li[{idxBtn}]/ul//a[contains(text(), "{tipoFiltro}")]', debug=False)

                if filtroProcesso:
                    filtroProcesso.click()
                    time.sleep(5)

                    # Busca pelo nome da ferramenta
                    clickarElemento(virtaus, '//*[@id="inputSearchFilter"]', debug=False).send_keys(nomeFerramenta)
                    time.sleep(5)

                    if not localizacao:
                        localizacao = nomeFerramenta

                    # Clica no primeira item da lista de solicitações
                    solicitacao = clickarElemento(virtaus, f'//td[@title="{localizacao}"]', debug=False)
                    if solicitacao:
                        solicitacao.click()
                        break
            
            if not loopInfinito:
                break

            hora = datetime.datetime.now()
            print(f"Não há solicitações do banco {enumBanco.name.title()} no momento {hora.strftime('%H:%M')}")

            if HORA_FINALIZACAO < hora.hour:
                virtaus.quit()
                
                if driverReset:
                    driverReset.quit()

                putStatusRobo(EnumStatus.DESLIGADO, enumProcesso, enumBanco)

            time.sleep(20)
                
            if resetSessao and driverReset:
                resetSessao(driverReset)

        except KeyboardInterrupt:
            putStatusRobo(EnumStatus.DESLIGADO, enumProcesso, enumBanco)
            break
        except Exception as e:
            print(e)
        finally:
            if resetEvent:
                resetEvent.set()      # Reseta countdown de restart do bot
    try:
        print("Assumindo Tarefa")
        # Clica em Assumir Tarefa e vai para o menu de Cadastro de usuário
        clickarElemento(virtaus, '//*[@id="workflowActions"]/button[1]').click()
        
        return FormularioSolicitacao(virtaus)
    
    except Exception as e:
        print(e)
        print("Erro ao assumir tarefa")


def finalizarSolicitacao(virtaus: Chrome,
                         senha: str | None = None,
                         usuario: str | None = None,
                         codigoLoja: int | None = None,
                         motivo: str | None = None,
                         status: str = 'Finalizado com Sucesso'):

    try:
        virtaus.switch_to.default_content()

        menuFrame = esperarElemento(virtaus, '//*[@id="workflowView-cardViewer"]')
        virtaus.switch_to.frame(menuFrame)
 
        if usuario:
            elementoUsuario = esperarElemento(virtaus, '//*[@id="nomeLogin"]')
            if elementoUsuario:
                elementoUsuario.send_keys(usuario)
 
        if senha:
            elementoSenha = esperarElemento(virtaus, '//*[@id="senhaLogin"]')
            if elementoSenha:
                elementoSenha.clear()
                elementoSenha.send_keys(senha)
 
        if codigoLoja:
            elementoCodigoLoja = esperarElemento(virtaus, '//*[@id="groupCodigoDeLoja"]/span/span[1]/span/ul/li/input')
            if elementoCodigoLoja:
                elementoCodigoLoja.send_keys(codigoLoja)
                esperarElemento(virtaus, '//*[@id="select2-codigoDeLojaId-results"]/li[2]').click()
        
        if motivo:
            elementoMotivo = esperarElemento(virtaus, '//*[@id="motivoLogin"]')
            if elementoMotivo:
                selectOption(virtaus, '//*[@id="motivoLogin"]', motivo)
        
        try:
            esperarElemento(virtaus, '//*[@id="abaDadosGerais"]/div[4]/div[2]/div/div/div[3]/span/div/button', tempoEspera=3, debug=False).click()
            esperarElemento(virtaus, '//*[@id="abaDadosGerais"]/div[4]/div[2]/div/div/div[3]/span/div/ul/li[2]/a/label/input', tempoEspera=3, debug=False).click()
        except Exception as erro:
            pass
            #print('Não precisou escolher Tipo de Analise', erro)

        time.sleep(5)

        virtaus.switch_to.default_content()
        esperarElemento(virtaus, '//*[@id="send-process-button"]').click()

        selectOption(virtaus, '//*[@id="nextActivity"]', status)

        esperarElemento(virtaus, '//*[@id="moviment-button"]').click()
        time.sleep(5)

    except TimeoutException as e:
        print(f"Erro ao localizar elemento: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def importarArquivos(virtaus: Chrome, enumBanco: EnumBanco, enumProcesso: EnumProcesso, codigoPasta: int, nomeBanco: str, filepathList: list, subPastaRede: str = ''):
    """
        Filtra arquivos na pasta de downloads do usuário e os envia para o sistema Virtaus.

        Parâmetros:
        - virtaus: Chrome - WebDriver do Selenium.
        - enumBanco: EnumBanco
        - codigoPasta: int - Código da pasta do banco no Virtaus (disponível na URL)
        - nomeBanco: str - Nome descritivo do banco (usado para gerar mensagens de feedback).
        - filepathList: list[str] - Lista dos caminhos dos arquivos.

        Fluxo:
        1. Acessa a URL específica do banco no sistema Virtaus.
        3. Faz o upload de cada arquivo para o sistema Virtaus.
        4. Remove o arquivo após o upload bem-sucedido.
        5. Exibe uma mensagem de sucesso ou erro no console.
    """
    chatId = chatIdMapping[enumProcesso]
    token = botTokenMapping[enumProcesso]

    try:
        putStatusRobo(EnumStatus.IMPORTANDO, enumProcesso, enumBanco)

        virtaus.get(f'https://adpromotora.virtaus.com.br/portal/p/ad/ecmnavigation?app_ecm_navigation_doc={codigoPasta}')
        time.sleep(10)

        temArquivos = any(filepathList)

        if not temArquivos:
            putStatusRobo(EnumStatus.SEM_ARQUIVOS, enumProcesso, enumBanco)
            mensagem = f"Não haviam documentos para importar! ⚠️ <b>{nomeBanco}</b>"
            mensagemTelegram(token, chatId, mensagem)

        else:
            for i, caminho in enumerate(filepathList, start=1):

                # Simula o envio do arquivo
                importarArquivo = aguardarElemento(virtaus, '//*[@id="ecm-navigation-inputFile-clone"]')
                importarArquivo.send_keys(caminho)

                print(f'Arquivo {caminho} enviado com sucesso')
            
                # Aguarda o upload finalizar
                time.sleep(10)

                # Mensagem de sucesso
                mensagem = f"Arquivo importado: {i}/{len(filepathList)}"
                mensagemTelegram(token, chatId, mensagem)

                importarPastaMonitoramento([caminho], enumBanco, enumProcesso, subPastaRede)

            else:
                mensagem = f"Todos os documentos foram integrados com sucesso!\n<b>{nomeBanco}</b> ✅"
                mensagemTelegram(token, chatId, mensagem)
                putStatusRobo(EnumStatus.LIGADO, enumProcesso, enumBanco)
                print(mensagem)
    
    except Exception as erro:
        print(erro)
        print('Não deu certo')
        putStatusRobo(EnumStatus.ERRO, enumProcesso, enumBanco)


if __name__=="__main__":
    
    userVirtaus, senhaVirtaus = getCredenciais(154)#"dannilo.costa@adpromotora.com.br", "Costa@36"
    
    driver = setupDriver(r"C:\Users\dannilo.costa\AppData\Roaming\Python\Python312\site-packages\Adlib\webdriver\chromedriver.exe")
    
    loginVirtaus(driver, userVirtaus, senhaVirtaus)

    solicitacao: FormularioSolicitacao = assumirSolicitacao(driver, "BMG CONSIG", EnumBanco.BMG, FiltrosSolicitacao.RESET)

    print(solicitacao.solicitacao)
    print(solicitacao.nome)
    print(solicitacao.cpf)
    print(solicitacao.uf)
    print(solicitacao.rg)
    print(solicitacao.email)