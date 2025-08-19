import time
from pprint import pprint
from typing import Callable
from dataclasses import dataclass
from selenium.webdriver import ChromeOptions
from .logins import loginVirtaus
from .virtaus import assumirSolicitacao, FiltrosSolicitacao, finalizarSolicitacao
from .funcoes import setupDriver, mensagemTelegram
from .utils import chatIdCriacao, tokenBotCriacao
from .api import EnumBanco, EnumStatus, EnumProcesso, putStatusSolicitacao, putStatusRobo, postSolicitacao, EnumStatusSolicitacao


@dataclass
class CriacaoUsuarioOptions:
    email: bool = False
    customPassword: bool = False
    autoRefreshPage: bool = True
    loginBankPage: bool = False


def criacaoUsuario(nomeFerramenta: str, codigoLoja: str, userBanco: str, senhaBanco: str, enumBanco: EnumBanco, loginBanco: Callable[[ChromeOptions, str, str], None],
criarUsuario: Callable[[ChromeOptions,str,str], None], userVirtaus: str, senhaVirtaus: str, options: CriacaoUsuarioOptions = None):    

    """
    Executa rotina de criação de usuário para banco específico.
    Acessa o Virtaus, buscando por solicitações de criação de usuário do banco especificado
    e executa o fluxo de cadastro de usuário no banco a partir da função criarUsuario()

    Arguments:
        nomeFerramenta: nome da ferramenta do banco (case sensitive)
        userBanco: nome de usuário do banco
        senhaBanco: senha de usuário do banco
        loginBanco: função da rotina de login no banco.
        criarUsuario: função da rotina de cadastro de usuário no banco
        userVirtaus: nome de usuário do Virtaus
        senhaVirtaus: senha do Virtaus
    """
    
    virtaus, banco = setupDriver(numTabs=2)

    # Banco
    loginBanco(banco, userBanco, senhaBanco)
    
    while True:
        
        putStatusRobo(EnumStatus.LIGADO, EnumProcesso.CRIACAO, enumBanco)
        
        # Login Virtaus
        loginVirtaus(virtaus, userVirtaus, senhaVirtaus)
        
        while True:
            try:
                formularioSolicitacao = assumirSolicitacao(virtaus, nomeFerramenta, enumBanco, FiltrosSolicitacao.CRIACAO)

                solicitacaoVirtaus = formularioSolicitacao.solicitacao

                idSolicitacao = None
                idSolicitacao = postSolicitacao(EnumStatusSolicitacao.EM_ATENDIMENTO, EnumProcesso.CRIACAO, solicitacaoVirtaus, enumBanco)

                cpf = formularioSolicitacao.cpf
                nomeUsuario = formularioSolicitacao.nome
                
                if not nomeUsuario:
                    putStatusSolicitacao(idSolicitacao, EnumStatusSolicitacao.ERRO, "Nome de usuário não encontrado no Virtaus")
                    break

                if not cpf:
                    putStatusSolicitacao(idSolicitacao, EnumStatusSolicitacao.ERRO, "CPF do usuário não encontrado no Virtaus")
                    break

                # Chamar função para criação de usuário no banco
                try:
                    loginBanco(banco, userBanco, senhaBanco)
                    time.sleep(10)

                    print("Criando Usuario")
                    usuario, senha = criarUsuario(banco, formularioSolicitacao)

                    print(usuario, senha)
                except Exception as e: 
                    print(e)
                    print("Erro na criação de usuário no Banco")
                    msg = f"""Erro na criação usuário \nUsuário: {usuario} \nSolicitação {solicitacaoVirtaus} {nomeFerramenta}  ❌"""
                    mensagemTelegram(tokenBotCriacao, chatIdCriacao, msg)
                    break
                try:
                    if usuario and senha:
                        finalizarSolicitacao(virtaus, senha, usuario, codigoLoja)
                        putStatusSolicitacao(idSolicitacao, EnumStatusSolicitacao.CONCLUIDO, "Usuário criado com sucesso!")
                        msg = f"Criação de usuário efetuada com sucesso!\nUsuário: {usuario}\nSolicitação {solicitacaoVirtaus} {nomeFerramenta.title()}  ✅"    
                    else:
                        putStatusSolicitacao(idSolicitacao, EnumStatusSolicitacao.ERRO, "Erro ao criar usuário!")
                        msg = f"Erro na criação usuário \nUsuário: {usuario} \nSolicitação {solicitacaoVirtaus} {nomeFerramenta} ❌"
                    mensagemTelegram(tokenBotCriacao, chatIdCriacao, msg)

                except Exception as e:
                    print(e)
                    print("Erro ao enviar solicitação")
                    putStatusSolicitacao(idSolicitacao, EnumStatusSolicitacao.ERRO, "Erro ao criar usuário!")
                    msg = f"Erro na criação usuário \nUsuário: {usuario} \nSolicitação {solicitacaoVirtaus} {nomeFerramenta} ❌"
                    mensagemTelegram(tokenBotCriacao, chatIdCriacao, msg)
                
            except Exception as e:
                print(e)
                break


if __name__=="__main__":
    # Credenciais Virtaus
    userVirtaus = 'dannilo.costa@adpromotora.com.br'
    senhaVirtaus = 'Costa@36'

    # Credenciais Banco
    userDigio = "03478690501_204258"
    senhaDigio = "Adpromo10*"

    def loginBanco():
        pass

    def criarUsuario():
        pass

    criacaoUsuario("DIGIO", "4258", userDigio, senhaDigio, EnumBanco.DIGIO, loginBanco, criarUsuario, userVirtaus, senhaVirtaus)