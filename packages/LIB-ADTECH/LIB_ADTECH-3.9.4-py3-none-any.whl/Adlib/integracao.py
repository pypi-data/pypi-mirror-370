from .api import EnumBanco
from .enums import EnumProcesso
from .logins import loginVirtaus
from .funcoes import setupDriver
from .virtaus import importarArquivos


def integracaoVirtaus(driver, usuario: str, senha: str, enumBanco: EnumBanco, codigoBanco: int, nomeBanco: str, filepaths: list, subPastaRede: str = ''):
    """
        Função principal que coordena a automação de login e importação de arquivos para o Virtaus.

        Parâmetros:
        - driver: webdriver.Chrome - WebDriver do Selenium
        - usuario: str - Nome de usuário para o login no Virtaus.
        - senha: str - Senha para o login no Virtaus.
        - codigoBanco: int - Código do banco no Virtaus (disponível na URL de integração do banco)
        - nomeBanco: str - Nome do banco para gerar mensagens de log e feedback.
        - substring: str - Substring usada para filtrar os arquivos na pasta de downloads.
        - formatoArquivo: str - Extensão dos arquivos a serem filtrados (por exemplo, 'xlsx', 'csv').
        - usuarioWindows: str - Nome de usuário no Windows para acessar a pasta de downloads (por exemplo, 'yan.fontes').

        Fluxo:
        1. Realiza o login no sistema Virtaus usando a função loginVirtaus.
        2. Filtra e envia arquivos da pasta de downloads para o sistema Virtaus utilizando a função importarArquivos.
    """

    loginVirtaus(driver, usuario, senha)
    importarArquivos(driver, enumBanco, EnumProcesso.INTEGRACAO, codigoBanco, nomeBanco, filepaths, subPastaRede)


if __name__=="__main__":

    driver = setupDriver()

    nomeBanco = "Paulista"
    codigoBanco = 2865957
    userVirtaus = "dannilo.costa@adpromotora.com.br"
    senhaVirtaus = "Costa@36"
    substringNomeArquivo = "FE361338-299B-429B-8F57-79B0AA2D872A"
    formatoArquivo = "xlsx"
    usuarioWindows = "dannilo.costa"

    integracaoVirtaus(driver, userVirtaus, senhaVirtaus, EnumBanco.PAULISTA, codigoBanco, nomeBanco, [])