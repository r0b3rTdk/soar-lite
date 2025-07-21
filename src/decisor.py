# r0b3rT - SOAR Lite
# 21/07/2025

# esse script sera o Juiz -> toma a decisão com base nos dados do Detetive

# Definindo Paises de origem de risco
PAISES_RISCO = ["CN", "RU", "IR"] 

def tomar_decisao(dados_alerta_enriquecidos):
    """
    Toma uma decisão com base nos dados enriquecidos do alerta.
    Retorna uma ação recomendada e justificativa.
    """
    
    ip = dados_alerta_enriquecidos.get("ip")
    pais_origem = dados_alerta_enriquecidos.get("geolocalizacao")
    # se o pontuacao_delitos for None, consideramos como 0 (IP sem delitos)
    pontuacao_delitos = dados_alerta_enriquecidos.get("abuse_score")
    if pontuacao_delitos is None:
        pontuacao_delitos = 0
    
    # --- REGRAS DE DECISAO ---
    
    # REGRA 1: se o OP e de risco AND o Score for alto -> BLOQUEAR
    if pais_origem in PAISES_RISCO and pontuacao_delitos >= 50:
        acao_final = "BLOQUEAR"
        justificativa_final = f"IP ({ip}) de origem em país de risco ({pais_origem}) e com alta pontuação de abuso ({pontuacao_delitos})."
    # REGRA 2.1: se for IPs Internos/Locais (RFC1918) -> IGNORAR
    elif ip.startswith(("10.", "172.", "192.")):
        acao_final = "IGNORAR"
        justificativa_final = f"IP ({ip}) é um endereço interno ou local, considerado seguro."
    # REGRA 2.2: se o score baixo -> IGNORAR
    elif pontuacao_delitos == 0:
        acao_final = "IGNORAR"
        justificativa_final = f"IP ({ip}) com pontuação de abuso zero, considerado seguro."
    
    # REGRA 3: se o IP e desconhecido OU score medio -> ALERTAR
    elif pais_origem is None or (pontuacao_delitos >= 1 and pontuacao_delitos <= 50):
        acao_final = "INVESTIGAR"
        justificativa_final = f"IP ({ip}) com status incerto (geolocalização: {pais_origem}, score: {pontuacao_delitos}), requer análise manual."
    # se nenhuma regra se aplicar, requer investigação manual
    else:
        acao_final = "INVESTIGAR"
        justificativa_final = f"IP ({ip}) não se encaixou nas regras definidas, requer investigação manual."

    # Retornar a ação recomendada e a justificativa
    return {
        "acao_recomendada": acao_final,
        "justificativa_acao": justificativa_final
    }