# r0b3rT - SOAR Lite
# 15/07/2025
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src import ingestao 
from src import enriquecimento
from src import decisor

soar_API = FastAPI() # inicializa a aplicação FastAPI

class Alerta_API(BaseModel): # modelo de dados para o alerta de IP
    ip: str 

@soar_API.post("/alerta") # decorador do endpoint POST

# uso de async para funcoes de endpoint no FastAPI
async def receber_alerta(alerta: Alerta_API): # recebe o alerta
    ip_recebido = alerta.ip
    resultado_validacao = ingestao.processar_alerta_ip(ip_recebido)
    # 1. valida o IP recebido
    if resultado_validacao["status"] == "valido":
        print(f"IP valido recebido: {ip_recebido} ({resultado_validacao['ip_tipo']})")
        
        # inicializa as variaveis para os dados de enriquecimento
        geolocalizacao = None
        detalhes_geolocalizacao = 'Nao obtida.'
        abuse_score = None
        detalhes_reputacao = 'Nao obtida.'
        
        #  --- Parte da Geolocalização ---
        # 2. se o IP for valido, chama a função de enriquecimento para descobrir a origem do IP        
        resultado_geo = enriquecimento.descobrir_origem_ip(ip_recebido)
        if resultado_geo["status"] == "sucesso":
            print(f"Geolocalizacao para {ip_recebido}: {resultado_geo['geolocalizacao']}")
            geolocalizacao = resultado_geo["geolocalizacao"]
            detalhes_geolocalizacao = resultado_geo["mensagem"]
        else:
            print(f"Falha ao obter geolocalizacao para {ip_recebido}: Detalhe: {resultado_geo['mensagem']}")
            detalhes_geolocalizacao = resultado_geo["mensagem"]
            
            
        # --- Parte da Reputação ---
        # 3. Se o IP for valido, podemos prosseguir com o enriquecimento de reputação
        resultado_reputacao = enriquecimento.consultar_reputacao_ip(ip_recebido)
        if resultado_reputacao['status'] == 'sucesso':
            print(f"Reputacao para {ip_recebido}: {resultado_reputacao['abuse_score']}")
            abuse_score = resultado_reputacao['abuse_score']
            detalhes_reputacao = resultado_reputacao['mensagem']
        else:
            print(f"Aviso: Falha ao obter reputacao para {ip_recebido}: Detalhe: {resultado_reputacao['mensagem']}")
            detalhes_reputacao = resultado_reputacao['mensagem']
        
        # --- Parte da Decisão ---
        # 1. depois dos dados enriquecidos, enviamos eles ao decisor para tomar a decisão
        dados_para_decisao = {
            "ip": ip_recebido,
            "geolocalizacao": geolocalizacao,
            "abuse_score": abuse_score
        }
        # 2. chama a função decisor e recebe a ação recomendada e justificativa
        decisao = decisor.tomar_decisao(dados_para_decisao)
        # 3. Resposta final com os dados enriquecidos e a decisão tomada
        return {
            "mensagem": "Alerta processado com enriquecimento.",
            "ip": ip_recebido,
            "status_validacao": resultado_validacao["mensagem"],
            "geolocalizacao": geolocalizacao,
            "detalhes_geolocalizacao": detalhes_geolocalizacao,
            "abuse_score": abuse_score,
            "detalhes_reputacao": detalhes_reputacao,
            "acao_recomendada": decisao["acao_recomendada"],
            "justificativa_acao": decisao["justificativa_acao"]
        }
       
    else:
        # se o IP for invalido, levanta uma exceção HTTP com status de erro
        print(f"Erro: IP invalido recevido: {ip_recebido}. Detalhe: {resultado_validacao['mensagem']}")
        raise HTTPException(
            status_code=400, # codigo de status de HTTP para requisição inválida
            detail={
                "mensagem": "Erro: IP invalido recebido.",
                "detalhes": resultado_validacao["mensagem"]
            }
        )