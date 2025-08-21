import requests
 
# URL base da API
#tirar o -hml
BASE_URL = "https://services-hml.flexdoc-apis.com.br/services/api/v1"
 
 
def obterToken(username: str, password: str) -> str:
    """
    Obtém o token de autenticação usando as credenciais fornecidas.
 
    :param username: Nome de usuário
    :param password: Senha
    :return: Token de acesso ou None em caso de erro
    """
    auth_url = f"{BASE_URL}/authentication"
    auth_payload = {"username": username, "password": password}
    auth_headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
 
    response = requests.post(auth_url, json=auth_payload, headers=auth_headers)
 
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Erro ao obter token: {response.status_code} - {response.text}")
        return None
 
 
def verificarFraude(token: str, cpf: str, documentos: list[str]):
    """
    Realiza a análise de fraude e retorna True se o score for > 80, senão retorna False.
 
    :param token: Token de autenticação
    :param cpf: CPF do usuário
    :param documentos: Lista contendo exatamente dois caminhos de imagens (frente e verso do documento)
    :return: True se score > 80, senão False
    """
    if len(documentos) < 1 :  # Só passa se tiver exatamente 2 documentos
        print("Erro: A lista de documentos deve conter exatamente 2 arquivos (frente e verso).")
        return False
 
    imagem_frente, imagem_verso = documentos  # Pegando os dois arquivos da lista
    
    ## https://flex-hml.flexdoc-apis.com.br/services/api/v1/fraud/analysis
    fraud_url = f"{BASE_URL}/fraud/analysis"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
 
    try:
        with open(imagem_frente, "rb") as frente, open(imagem_verso, "rb") as verso:
            files = {
                "cpf": (None, cpf),
                "imageFront": (imagem_frente, frente, "image/jpeg"),
                "imageBack": (imagem_verso, verso, "image/jpeg"),
            }
 
            response = requests.post(fraud_url, headers=headers, files=files)
 
        if response.status_code == 200:
            resultado = response.json()
            score = resultado.get("scoreResult", {}).get("score", 0)
            return score > 80
        else:
            print(f"Erro na análise de fraude: {response.status_code} - {response.text}")
            return False
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
        return False
 
 
def main():
    username = "adpromo.api"
    password = "a3d5p-r5o0m0"
 
    token = obterToken(username, password)
 
    if token:
        cpf = "01360504257"
        imagem_frente = "rg representante1.jpg"
        imagem_verso = "rg representante (1).jpg"
 
        status = verificarFraude(token, cpf, imagem_frente, imagem_verso)
        print(f"Resultado da análise: {status}")
    else:
        print("Não foi possível autenticar o usuário.")
 
 
if __name__ == "__main__":
    main()
 