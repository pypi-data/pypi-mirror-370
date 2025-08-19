import os
import base64
import requests
from Adlib.enums import EnumBanco, EnumStatus, EnumProcesso, EnumStatusSolicitacao, Enum, EnumTipoContrato
from requests.exceptions import RequestException, Timeout, ConnectionError


class IdSolicitacaoCriacaoBanco(Enum):
    BMG = 41
    C6 = 42
    DIGIO = 47
    BRADESCO = 47
    ITAU = 44
    VIRTAUS = 46
    AMIGOZ = 89

    @classmethod
    def getEnum(cls, key):
        try:
            return cls[key].value
        except KeyError:
            raise ValueError(f"Chave {key} não encontrada em {cls.__name__}.")


class IdSolicitacaoResetBanco(Enum):
    BMG = 48
    MASTER = 49
    CREDCESTA = 49
    ITAU = 50
    BANRISUL = 51
    FACTA = 52
    CREFISA = 53
    DIGIO = 54
    BRADESCO = 54
    AMIGOZ = 87
    C6 = 90
    DAYCOVAL = 91
    ICRED = 92

    @classmethod
    def getEnum(cls, key):
        try:
            return cls[key].value
        except KeyError:
            raise ValueError(f"Chave {key} não encontrada em {cls.__name__}.")


def putStatusRobo(status: EnumStatus, enumProcesso: EnumProcesso, enumBanco: EnumBanco):
    """
    Envia duas requisições HTTP PUT para atualizar o status de um processo e registrar o horário da atualização.

    Parâmetros:
    ----------
    status : IntegracaoStatus
        Um valor da enumeração `IntegracaoStatus` que representa o status do processo a ser atualizado.
    enumProcesso : int
        Um número inteiro que representa o ID do processo a ser atualizado.
    enumBanco : int
        Um número inteiro que representa o ID do banco a ser atualizado.
    """
    PORTA = 7118
    
    if enumProcesso in [EnumProcesso.INTEGRACAO, EnumProcesso.IMPORTACAO, EnumProcesso.APROVADORES]:
        PORTA = 8443

    horaFeita = f'http://172.16.10.6:{PORTA}/acompanhamentoTotal/horaFeita/{enumProcesso.value}/{enumBanco.value}'
    URLnovaApi = f'http://172.16.10.6:{PORTA}/acompanhamentoTotal/processoAndBancoStatus/{enumProcesso.value}/{enumBanco.value}'

    data = { "status": status.value }
    headers = { "Content-Type": "application/json" }
    try:
        response = requests.put(URLnovaApi, headers=headers, json=data)

    except requests.Timeout:
        print("A requisição expirou. Verifique sua conexão ou o servidor.")
    except ConnectionError:
        print("Erro de conexão. Verifique sua rede ou o servidor.")
    except requests.RequestException as e:
        print(f"Ocorreu um erro ao realizar a requisição: {e}")

    if status == EnumStatus.LIGADO:
        requests.put(horaFeita)

    if response.status_code == 200: 
        pass
        # print("Requisição PUT bem-sucedida!")
        # print("Resposta:", response.json())
    else:
        print(f"Falha na requisição PUT. Código de status: {response.status_code}")
        # print("Resposta:", response.text)


def putStatusSolicitacao(idSolicitacao: int, enumStatus: EnumStatusSolicitacao, observacao: str = ""):
    """
    Atualiza o status de uma solicitação via requisição PUT e registra a hora de finalização.

    Args:
        idSolicitacao (int): ID da solicitação a ser atualizada.
        enumStatus (EnumStatusSolicitacao): Novo status da solicitação.
        observacao (str, opcional): Texto adicional com observações. Padrão: "".

    Returns:
        None
    """
    data = {
        "enumDetalheSolicitacoesStatus": enumStatus.value,
        "observação": observacao
    }
    headers = {
        "Content-Type": "application/json"
    }

    URLChangeStatus = f'http://172.16.10.6:7118/detalhesSolicitacao/{idSolicitacao}'

    try:
        response = requests.put(URLChangeStatus, headers=headers, json=data)

        if response.status_code == 200:
            # print("Requisição PUT bem-sucedida!")
            requests.put(f'http://172.16.10.6:7118/detalhesSolicitacao/horaFim/{idSolicitacao}', headers=headers, json=data)
        else:
            print(f"Falha na requisição PUT. Código de status: {response.status_code}")
            print("Resposta:", response.text)
    except Timeout:
        print("A requisição expirou. Verifique sua conexão ou o servidor.")
    except ConnectionError:
        print("Erro de conexão. Verifique sua rede ou o servidor.")
    except RequestException as e:
        print(f"Ocorreu um erro ao realizar a requisição: {e}")


def postSolicitacao(enumStatusSolicitacao: EnumStatusSolicitacao, enumProcesso: EnumProcesso, solicitacao: int, enumBanco: EnumBanco) -> int:
    """
    Envia uma solicitação HTTP POST para solicitação.

    Essa função constrói e envia uma requisição POST para a API de detalhes de solicitação,
    baseada nos enums fornecidos e no número da solicitação. O identificador da solicitação
    é derivado de um mapeamento baseado no tipo de processo e banco.

    Args:
        enumStatusSolicitacao (EnumStatusSolicitacao): Status atual da solicitação (ex: EM ATENDIMENTO, APROVADO).
        enumProcesso (EnumProcesso): Tipo do processo (ex: CRIACAO, RESET).
        solicitacao (int): Número da solicitação.
        enumBanco (EnumBanco): Banco associado à solicitação.

    Returns:
        int: O ID retornado pela API após a criação do detalhe da solicitação.

    Raises:
        KeyError: Se o enumProcesso não existir no mapeamento.
        requests.exceptions.RequestException: Para erros de rede ou problemas com a requisição.
        ValueError: Se a resposta da API não contiver o campo esperado `detalhesSolicitacaoId`.
    """
    mapping =   {
                    EnumProcesso.CRIACAO : IdSolicitacaoCriacaoBanco,
                    EnumProcesso.RESET: IdSolicitacaoResetBanco
                }
    
    idBanco = mapping[enumProcesso].getEnum(enumBanco.name)
    
    data = {
        "enumDetalheSolicitacoesStatus": enumStatusSolicitacao.value,
        "numeroSolicitacao": solicitacao,
        "acompanhamentoDomain": {
            "acompanhamentoId": idBanco
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post("http://172.16.10.6:7118/detalhesSolicitacao/", headers=headers, json=data)

    if response.status_code == 200:
        pass
        # print("Requisição POST bem-sucedida!")
        # print("Resposta:", response.json()) 
    
    else:
        print(f"Falha na requisição POST. Código de status: {response.status_code}")
        # print("Resposta:", response.text)

    dataApi = response.json()
    detalhesSolicitacaoId = dataApi['detalhesSolicitacaoId']

    return detalhesSolicitacaoId


def storeCaptcha(imagePath: str, enumBanco: EnumBanco = EnumBanco.VAZIO, enumProcesso: EnumProcesso = EnumProcesso.IMPORTACAO):
    """
    Envia uma imagem de captcha para a API e remove o arquivo local.

    Args:
        imagePath (str): Caminho da imagem no disco (formato esperado: nome_CAPTCHA.png).
        enumBanco (EnumBanco): Banco relacionado. Padrão: EnumBanco.VAZIO.
        enumProcesso (EnumProcesso): Processo relacionado. Padrão: EnumProcesso.IMPORTACAO.

    Returns:
        None
    """
    url = "http://172.16.10.12:5000/storeCaptcha"

    name = os.path.basename(imagePath)
    captcha = name.split("_")[1].split(".")[0]
    processo = enumBanco.name
    banco = enumProcesso.name

    with open(imagePath, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        document = {
            "nomeArquivo": name,
            "textoCaptcha": captcha,
            "processo": processo,
            "banco": banco,
            "imagem": f"data:image/png;base64,{base64_image}"
        }
    requests.post(url, json=document)
    os.remove(imagePath)


def putTicket(solicitacao: str, enumProcesso: EnumProcesso, enumBanco: EnumBanco):
    
    data = {
        "solicitacao": solicitacao
    }
    headers = {
        "Content-Type": "application/json"
    }

    URLChangeStatus = f'http://172.16.10.6:8443/acompanhamentoTotal/processoAndBancoSolicitacao/{enumProcesso.value}/{enumBanco.value}'

    try:
        response = requests.put(URLChangeStatus, headers=headers, json=data)

        if response.status_code == 200:
            # print("Requisição PUT bem-sucedida!")
            pass
        else:
            print(f"Falha na requisição PUT. Código de status: {response.status_code}")
            print("Resposta:", response.text)
    except Timeout:
        print("A requisição expirou. Verifique sua conexão ou o servidor.")
    except ConnectionError:
        print("Erro de conexão. Verifique sua rede ou o servidor.")
    except RequestException as e:
        print(f"Ocorreu um erro ao realizar a requisição: {e}")


dynamicFunctions = dict()

def createShutdownBotFunctions():
    from itertools import product

    for processo, banco in product(EnumProcesso, EnumBanco):
        func_name = f"desligar{processo.name.title()}{banco.name.title()}"
        
        def func(p=processo, b=banco):
            putStatusRobo(EnumStatus.DESLIGADO, p, b)

        dynamicFunctions[func_name] = func


def postReclamacao(contrato: int, enumBanco: EnumBanco, enumTipoContrato: EnumTipoContrato, observacao: str, prazo: int):
    """
    Envia uma nova reclamação de contrato para o serviço de contratos.

    Esta função realiza uma requisição HTTP POST para registrar uma nova reclamação
    associada a um contrato específico. Os dados da reclamação incluem o número do contrato,
    o banco, o tipo de contrato e uma observação. A reclamação é inicialmente marcada
    como 'não notificada'.

    Args:
        contrato (int): O número identificador do contrato.
        enumBanco (EnumBanco): O enum que representa o banco associado ao contrato.
        enumTipoContrato (EnumTipoContrato): O enum que representa o tipo de contrato.
        observacao (str): Uma string contendo observações adicionais sobre a reclamação.

    Returns:
        None: Esta função não retorna nenhum valor. Ela apenas envia a requisição HTTP.

    Raises:
        requests.exceptions.RequestException: Se ocorrer um erro durante a requisição HTTP.
    """
    url = "http://172.16.10.6:1928/contratos"

    data = {
        "contrato": contrato,
        "banco": enumBanco.name,
        "tipoContratoEnum": enumTipoContrato.value,
        "observacao": observacao,
        "notificado": False,
        "prazo": prazo
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("notificado", False)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar reclamação para o contrato {contrato}: {e}")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao enviar a reclamação para o contrato {contrato}: {e}")
        return False


def putReclamacao(contrato: int):
    """
    Atualiza o status de notificação de uma reclamação de contrato.

    Esta função realiza uma requisição HTTP PUT para marcar uma reclamação específica
    como "notificada". A atualização é feita com base no número do contrato.

    Args:
        contrato (int): O número identificador do contrato cuja reclamação será atualizada.

    Returns:
        None: Esta função não retorna nenhum valor. Ela apenas envia a requisição HTTP.

    Raises:
        requests.exceptions.RequestException: Se ocorrer um erro durante a requisição HTTP.
    """ 
    url = f"http://172.16.10.6:1928/contratos/notificado/{contrato}"

    try:
        response = requests.put(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar o status de notificação para o contrato {contrato}: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao atualizar o status de notificação para o contrato {contrato}: {e}")


def solveCaptcha(filepath: str) -> str | None:
    """
    Envia uma imagem de captcha para API de OCR.

    Args:
        filepath (str): Caminho da imagem do captcha.

    Returns:
        str | None: Texto previsto se a requisição for bem-sucedida, ou um dicionário de erro em caso de falha.
    """

    url = "http://172.16.21.76:9856/predict"
    try:
        with open(filepath, "rb") as img_file:
            files = {"image": img_file}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            return response.json()["prediction"]
        else:
            return {"erro": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {'erro': str(e)}
    finally:
        os.remove(filepath)


def putTicketBlip(enumStatusSolicitacao:EnumStatusSolicitacao, observacaoValue,ticketId):
    urlApi = f'http://172.16.10.6:7118/ticket/{ticketId}'
    data = {
        'enumTicketsStatus': enumStatusSolicitacao.value,
        'observação': observacaoValue
    }
    headers = {
    "Content-Type": "application/json"
}
    response = requests.put(urlApi, headers=headers, json=data)

    if response.status_code != 200:
        print.error(f"Falha na requisição PUT. Código de status: {response}")


def putHoraFinalFunction(ticketId):
    urlApiHorafinal = f'http://172.16.10.6:7118/ticket/horaFim/{ticketId}'
    data = {
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.put(urlApiHorafinal, headers=headers, json=data)

    if response.status_code != 200:
        print.error(f"Falha na requisição PUT. Código de status: {response}")

if __name__=="__main__":
    
    # print(solveCaptcha(r"C:\Users\dannilo.costa\Pictures\Imagens\Captchas\1737471966_5ak3.png"))

    # dynamicFunctions["desligarImportacaoNuvideo"]()
    #putTicketBlip(EnumStatusSolicitacao.CONCLUIDO, "teste", 42246)
    #putStatusRobo(EnumStatus.LIGADO, EnumProcesso.INTEGRACAO, EnumBanco.PRESENCA_BANK)
    # putStatusRobo(EnumStatus.LIGADO, EnumProcesso.CRIACAO, EnumBanco.BMG)
    # putStatusRobo(EnumStatus.LIGADO, EnumProcesso.CRIACAO, EnumBanco.C6)
    # postSolicitacao(None, EnumProcesso.CRIACAO, 123345, EnumBanco.BANRISUL)
    # putStatusRobo(EnumStatus.LIGADO, EnumProcesso.IMPORTACAO, EnumBanco.MEU_CASH_CARD)
    # putStatusRobo(EnumStatus.LIGADO, EnumProcesso.RESET, EnumBanco.BANRISUL)
    #postSolicitacao(EnumStatusSolicitacao.EM_ATENDIMENTO, EnumProcesso.RESET, 123456, EnumBanco.DIGIO)
    pass