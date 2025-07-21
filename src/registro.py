# r0b3rT - SOAR Lite
# 13/07/2025
import sqlite3 # Módulo padrão do Python para interagir com bancos de dados SQLite
import os      # Módulo para interagir com o sistema operacional (caminhos de arquivos, criar pastas)
from dotenv import load_dotenv # Biblioteca para carregar variáveis de ambiente do arquivo .env

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Define o nome da pasta onde o banco de dados será armazenado
DB_FOLDER = "data"
# Pega o nome do banco de dados do .env (se não encontrar, usa 'incidents.db' como padrão)
DB_NAME = os.getenv("DATABASE_NAME", "incidents.db")
# Constrói o caminho completo para o arquivo do banco de dados
# os.getcwd() pega o diretório de trabalho atual (a raiz do seu projeto 'soar-lite/')
# os.path.join() junta os pedaços do caminho de forma correta para o sistema operacional (Windows, Linux, etc.)
DB_PATH = os.path.join(os.getcwd(), DB_FOLDER, DB_NAME)
# E o caminho final vai ser tipo: 'C:\usuário\seuprojeto\data\incidents.db
# SQL para criar a tabela de incidentes
CREATE_INCIDENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_origem TEXT NOT NULL,
    geolocalizacao TEXT,
    abuse_score INTEGER,
    acao_recomendada TEXT,
    justificativa_acao TEXT,
    data_registro TEXT NOT NULL,
    status TEXT DEFAULT 'Pendente'
);
"""
def get_db_connection():
    """
    Cria a pasta 'data' se não existir e retorna uma conexão com o banco de dados SQLite.
    """
    os.makedirs(DB_FOLDER, exist_ok=True) # Garante que a pasta 'data' existe
    conn = None # Inicializa a variável de conexão como None
    try:
        conn = sqlite3.connect(DB_PATH) # Tenta conectar ao banco de dados no caminho especificado
        conn.row_factory = sqlite3.Row # Configura para que os resultados das consultas possam ser acessados por nome da coluna (como dicionário)
        print(f"Conectado ao banco de dados: {DB_PATH}") # Mensagem de sucesso
        return conn # Retorna o objeto de conexão
    except sqlite3.Error as e: # Captura qualquer erro específico do SQLite
        print(f"Erro ao conectar ao banco de dados: {e}") # Imprime o erro
        return None # Retorna None em caso de falha na conexão
def initialize_db():
    """
    Inicializa o banco de dados, criando a tabela 'incidents' se ela não existir.
    """
    conn = get_db_connection() # Obtém uma conexão com o banco de dados
    if conn: # Verifica se a conexão foi bem-sucedida
        try:
            cursor = conn.cursor() # Cria um objeto cursor para executar comandos SQL
            cursor.execute(CREATE_INCIDENTS_TABLE_SQL) # Executa o SQL de criação da tabela
            conn.commit() # Confirma as alterações no banco de dados (salva)
            print("Tabela 'incidents' verificada/criada com sucesso.") # Mensagem de sucesso
        except sqlite3.Error as e: # Captura erros durante a execução do SQL
            print(f"Erro ao criar a tabela: {e}")
        finally:
            conn.close() # Fecha a conexão, liberando os recursos do banco de dados
    # Bloco para testar a inicialização ao rodar o arquivo diretamente
if __name__ == "__main__":
    print("Iniciando teste de inicialização do banco de dados...")
    initialize_db() # Chama a função para inicializar o DB
