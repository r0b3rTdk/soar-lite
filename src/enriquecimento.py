# r0b3rT - SOAR Lite
# 16/07/2025

# esse script sera o Detetive -> busca a origem e ficha de reputação do IP

import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()  # carrega as variaveis do .env

def descobrir_origem_ip(ip: str) -> dict:
    """
    Descobre a origem geográfica de um endereço IP usando uma API externa.
    Retorna um dicionário com informações de geolocalização.
    """
    url_api = f"http://ip-api.com/json/{ip}"
    
    try:
        resposta = requests.get(url_api, timeout=5)  # faz a requisicao e aguarda a resposta em 5 segundos
        
        # verifica se a ligacao foi um sucesso (codigo HTTP 200)
        if resposta.status_code == 200:
            dados = resposta.json()
            # verificar se a resposta tem os status de sucesso
            if dados.get('status') == 'success': # se o status for 'success'
                #extrair o pais (geolocalizacao)
                pais = dados.get('countryCode')
                # retornar o dicionario com os dados
                return {
                    "status": "sucesso",
                    "geolocalizacao": pais,
                    "mensagem": "Geolocalização obtida com sucesso."
                }
            else:
                # se o status não for 'success', significa que o IP e invalido ou não encontrado
                return {
                    "status": "erro",
                    "mensagem": dados.get('message', 'IP inválido ou não encontrado pela API de geolocalização.'),
                }
        else:
            # se a ligacao for feita mas resultar em um erro HTTP (400, 404, etc.)
            return {
                "status": "erro",
                "mensagem": f"Erro HTTP: {resposta.status_code}",
            }
    # se a requisicao falhar (problemas de rede, timeout, etc.)
    except requests.exceptions.RequestException as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao conectar com a API: {e}",
        }
    # se a resposta não for um JSON
    except json.JSONDecodeError as e:
        return {
            "status": "erro",
            "mensagem": f"Resposta inválida da API: {e}",
        }
    # qualquer outro erro inesperado
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro inesperado: {e}",
        } 

def consultar_reputacao_ip(ip: str) -> dict:
    """
    Consulta a reputação de um endereço IP usando uma API externa.
    Retorna um dicionário com informações de reputação.
    """
    url_reputacao = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}" # URL da API de reputação de IP
    # preparar a "credencial de acesso" (is cabecalhos HTTP)
    api_key = os.getenv("ABUSEIPDB_API_KEY")  # chave da API do AbuseIPDB do .env
    # verifica se a chave da API está configurada
    if not os.getenv("ABUSEIPDB_API_KEY"):
        return {
            "status": "erro",
            "mensagem": "Chave de API do AbuseIPDB não configurada no .env.",
        }
    headers = {
        'Key': os.getenv("ABUSEIPDB_API_KEY"),  
        'Accept': 'application/json' # afirma que aceitamos resposta em JSON
    }
    # preparar "parametros de pesquisa"
    params = {
        'ipAddress': ip,  
        'maxAgeInDays': 90  # dados dos ultimos 90 dias
    }
    try:
        # faz a requisicao GET com os parametros e cabecalhos
        resposta_reputacao = requests.get(url_reputacao, headers=headers, params=params, timeout=5)
        # verifica se a resposta foi código HTTP 200 = sucesso
        if resposta_reputacao.status_code == 200:
            #pega os dados em formato JSON
            data = resposta_reputacao.json()
            score = data.get('data', {}).get('abuseConfidenceScore')
            return {
                "status": "sucesso",
                "abuse_score": score,
                "mensagem": f"Reputação do IP {ip} consultada com sucesso."
            }
        elif resposta_reputacao.status_code in [401, 403]:
            return {
                "status": "erro",
                "mensagem": "Erro de autenticação na API AbuseIPDB: Verifique sua chave de API.",
            }
        elif resposta_reputacao.status_code == 429:
            return {
                "status": "erro",
                "mensagem": f"Limite de requisições excedido na API AbuseIPDB. Tente novamente mais tarde.",
            }
        else:
            return {
                "status": "erro",
                "mensagem": f"Erro HTTP: {resposta_reputacao.status_code} na API AbuseIPDB.",
            }
     # se a requisicao falhar (problemas de rede, timeout, etc.)
    except requests.exceptions.RequestException as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao conectar com a API: {e}",
        }
    # se a resposta não for um JSON
    except json.JSONDecodeError as e:
        return {
            "status": "erro",
            "mensagem": f"Resposta inválida da API: {e}",
        }
    # qualquer outro erro inesperado
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro inesperado: {e}",
        } 