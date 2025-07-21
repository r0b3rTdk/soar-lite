# r0b3rT - SOAR Lite
# 14/07/2025

# esse script sera o Guarda de Entrada do SOAR Lite -> verificar quem está chegando (o IP)

import ipaddress

def processar_alerta_ip(ip: str) -> dict:
    """
    Valida um endereço IP e retorna um dicionario com o status da validacao.
    """
    try:
        ip_obj = ipaddress.ip_address(ip)  # tenta criar um objeto IP
        # se a linha acima não gerar ValueError, o IP é válido
        if isinstance(ip_obj, ipaddress.IPv4Address):
            # retornamos um dicionário com status, ip_tipo e a mensagem
            return {"status" : "valido", "ip_tipo": "IPv4", "mensagem": f"IP {ip} é um endereço IPv4 válido."} 
        elif isinstance(ip_obj, ipaddress.IPv6Address):
            return {"status" : "valido", "ip_tipo": "IPv6", "mensagem": f"IP {ip} é um endereço IPv6 válido."} 
    except ValueError as e:
        # se ValueError for gerado, o IP é inválido
        # retornamos um dicionário com status de erro e a mensagem do erro.
        return {"status" : "invalido", "mensagem": f"IP inválido: {e}"}