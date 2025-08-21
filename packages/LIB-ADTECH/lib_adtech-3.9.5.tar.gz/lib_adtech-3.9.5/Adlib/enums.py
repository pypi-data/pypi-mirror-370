from enum import Enum


class EnumStatusAcompanhamento(Enum):
    VAZIO = 0
    ERRO = 1
    LIGADO = 2
    DESLIGADO = 3
    IMPORTANDO = 4
    APROVADO = 5
    CANCELADA = 6
    SEM_ARQUIVOS = 8

class EnumStatus(Enum):
    VAZIO = 0
    ERRO = 1
    LIGADO = 2
    DESLIGADO = 3
    IMPORTANDO = 4
    APROVADO = 5
    CANCELADA = 6
    SEM_PROPOSTA = 7
    SEM_ARQUIVOS = 8

class EnumProcesso(Enum):
    INTEGRACAO = 0
    IMPORTACAO = 1
    APROVADORES = 2
    BLIP_CONSULTA = 3
    BLIP_LINK = 4
    PAG_DEV = 5
    JURIDICO = 6
    RESET = 7
    ANALISE_DOCUMENTOS = 8
    CRIACAO = 9
    CONFIRMACAO_CREDITO = 10


class EnumBanco(Enum):
    VAZIO = 0
    PAN = 1
    OLE = 2
    MEU_CASH_CARD = 3
    BMG = 4
    BRADESCO = 5
    BANRISUL = 6
    PRESENCA_BANK = 7 # Pedir pra atualizar
    BANCO_DO_BRASIL = None
    C6 = 8
    ITAU = 9
    MASTER = 10
    PAULISTA = 11
    CREFAZ = 12
    CCB = 13
    DAYCOVAL = 14
    ICRED = 15
    AMIGOZ = 16
    HAPPY_AMIGOZ = None
    SAFRA = 17
    SANTANDER = 18
    SABEMI = 19
    CREFISA = 20
    FACTA = 21
    VIRTAUS = 22
    FUTURO_PREVIDENCIA = 23
    CREFISA_CP = 24
    PAN_CARTAO = 25
    PAN_PORT = 26
    HAPPY_PORT = 27
    NUVIDEO = 28
    PROMOBANK = 29
    BLIP = 30
    GETDOC = 31
    ITAU_DIGITAL = 32
    DIGIO = 33
    ITAU_360 = 34
    DAYCOVAL_CARTAO = 35
    HAPPY = 36
    CAIXA = 37
    QUALIBANK = 38
    BRB = 39
    BTW = 40
    NEON = 41
    PROMOBANK_2 = 42
    PROMOBANK_3 = 43

class EnumStatusSolicitacao(Enum):
    EM_ATENDIMENTO = 0
    CONCLUIDO = 1
    ERRO = 2
    TRANSFERIDO = 3


class EnumTipoContrato(Enum):
    JUDICIAL = "judicial"
    EXTRAJUDICIAL = "extra_judicial"
