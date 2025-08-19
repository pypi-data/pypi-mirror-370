import os
import requests

# URL fixa da API
URL_API = "http://172.16.20.50:9022/classificarDocumentos"

def enviarDocumentos(pastaDocumentos: str):
    """
    Envia todos os documentos de uma pasta para um endpoint fixo em uma única requisição.

    :param pastaDocumentos: Caminho da pasta contendo os documentos.
    :return: Código de status, resposta da API e lista de arquivos com resposta True.
    """
    # Lista todos os arquivos na pasta
    filepaths = [os.path.join(pastaDocumentos, f) for f in os.listdir(pastaDocumentos) if os.path.isfile(os.path.join(pastaDocumentos, f))]

    if not filepaths:
        return "Nenhum arquivo encontrado na pasta.", []

    # Criando o dicionário de arquivos
    files = [("files", (os.path.basename(path), open(path, "rb"))) for path in filepaths]

    try:
        # Enviando todos os arquivos de uma vez para a URL fixa
        response = requests.post(URL_API, files=files)
        responseJson = response.json()

        # Filtrando os documentos que tiveram resposta "true"
        documentosTrue = [nome for nome, resultado in responseJson.items() if resultado is True]

        return response.status_code, responseJson, documentosTrue
    except Exception as e:
        return f"Erro ao enviar documentos: {str(e)}", [], []
    finally:
        # Fechando os arquivos
        for _, file_obj in files:
            file_obj[1].close()


def main():
    # Caminho da pasta com os documentos
    pastaDocumentos = r"C:\Users\yan.fontes\Dropbox\PC\Downloads\ImportarDocumento-importar-documento-c6\ImportarDocumento-importar-documento-c6\C6 Importar Documneto\Documentos"

    # Chama o método para enviar os documentos
    status_code, resposta_api, documentosTrue = enviarDocumentos(pastaDocumentos)

    # Exibindo o resultado
    print(f"Código de status: {status_code}")
    print(f"Resposta da API: {resposta_api}")
    print(f"Documentos com resposta True: {documentosTrue}")

# Chamando a função main quando o script for executado
if __name__ == "__main__":
    main()