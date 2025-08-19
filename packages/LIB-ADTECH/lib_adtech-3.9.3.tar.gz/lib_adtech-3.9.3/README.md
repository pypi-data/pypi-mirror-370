# 📚 Biblioteca de Automação — LIB-ADTECH

A **LIB-ADTECH** é uma biblioteca Python desenvolvida para facilitar a automação de tarefas com **Selenium**, otimizando processos internos da **AD Promotora**. Ela oferece funções práticas para interação com elementos web, automação de ações recorrentes e integração com serviços como **Telegram**, **e-mail** e **sistemas bancários**.

---

## 📦 Instalação

Você pode instalar a biblioteca de duas formas:

### Via GitHub (recomendado):

```bash
pip install git+https://github.com/DesenvolvimentoAD/Adlib.git@main
```

### Via PyPI (versão desatualizada):

```bash
pip install LIB-ADTECH
```

🔗 Página oficial no PyPI:
[https://pypi.org/project/LIB-ADTECH/](https://pypi.org/project/LIB-ADTECH/)

---

## 🚀 Como usar

Exemplo básico de uso:

```python
from Adlib.funcoes import esperarElemento
```

---

## 🧩 Módulos Disponíveis

### `funcoes.py`

Módulo principal da biblioteca. Contém funções utilitárias para automação web, interações com Telegram, manipulação de arquivos, controle de fluxo e monitoramento de processos.

### `api.py`

Gerencia a comunicação com a API local, incluindo envio de requisições e mapeamento de objetos do banco de dados.

### `enums.py`

Define os enumeradores das entidades e status do sistema, utilizados para padronização e clareza no código.

### `utils.py`

Agrupa funções e variáveis auxiliares que não pertencem a um processo específico, mas são úteis em diversos contextos.

### `blip.py`

Organiza os fluxos de ações para integração com a plataforma **Take Blip**.

### `logins.py`

Inclui funções para login em sistemas bancários integrados, com suporte a captcha, múltiplas sessões e validações.

---

## 🏦 Módulos Específicos de Processos

### `virtaus.py`

Automatiza processos operacionais executados no sistema **Virtaus**.

### `criacao.py`

Módulo dedicado à criação automatizada de usuários nos sistemas internos.

### `reset.py`

Automatiza o processo de reset de usuários.

### `confirmacao.py`

Executa a rotina de **confirmação de crédito** no Virtaus.

### `importacao.py`

Responsável pela **importação automatizada de propostas** no sistema.

### `integracao.py`

Executa o fluxo de **integração de propostas** no Virtaus e registro nas pastas de rede.
