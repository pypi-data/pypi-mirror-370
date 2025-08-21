Automação Zendesk com Selenium e Zenpy
Este projeto contém um conjunto de classes Python para automatizar tarefas na plataforma Zendesk, combinando a automação de interface web com Selenium e a manipulação de dados via API com a biblioteca Zenpy.

A biblioteca é projetada para ser robusta, gerenciando sessões de navegador de longa duração (localmente ou via Selenoid) e interagindo com a API do Zendesk para buscar e atualizar tickets.

🚀 Funcionalidades Principais
Gerenciamento de Driver Selenium:

Criação de drivers do Chrome locais ou remotos (Selenoid).

Configuração de sessionTimeout para robôs de longa duração.

Verificação de saúde da sessão e recriação automática do driver em caso de falha.

Automação de UI do Zendesk (Selenium):

Login automático na plataforma.

Navegação para filas de tickets e início do modo "Play".

Extração de valores de campos de input e dropdown.

Preenchimento de campos e seleção de opções em dropdowns.

Envio de tickets e fechamento de abas.

Manipulação inteligente de esperas para elementos dinâmicos (como spinners de carregamento).

Interação com a API do Zendesk (Zenpy):

Autenticação segura via token.

Busca de tickets em filas (visualizações) específicas.

Extração de valores de campos personalizados (custom fields) de um ticket.

Criação de novos tickets com campos personalizados, tags e comentários.

📋 Pré-requisitos
Antes de começar, certifique-se de que você tem os seguintes pré-requisitos:

Python 3.8 ou superior.

As bibliotecas listadas no arquivo requirements.txt.

pip install selenium zenpy requests urllib3 python-dotenv pandas pandas-gbq
Acesso a uma instância do Selenoid (para execução remota) ou o chromedriver instalado localmente.

Um arquivo .env no diretório raiz para armazenar as credenciais de forma segura.

Variáveis de Ambiente (.env)
Crie um arquivo chamado .env e adicione as seguintes variáveis:

Snippet de código

# Credenciais para login via UI (Selenium)
ID_LOGIN="seu_email_login@exemplo.com"
ID_PASS="sua_senha"

# Credenciais para a API (Zenpy)
ZENPY_EMAIL="seu_email_api@exemplo.com/token"
ZENPY_TOKEN="seu_token_da_api"
🛠️ Como Usar
A biblioteca é dividida em três componentes principais: a classe de controle do Driver, a classe de automação do Selenium e a classe de interação com a API.

1. Classe Driver_Selenium
Esta classe é uma "fábrica" para criar e gerenciar a vida útil do driver do Selenium.

Uso:

Python

# Criar um driver remoto (padrão)
driver = Driver_Selenium.criar_driver(local=False, timeout='24h')

# Criar um driver local
# driver = Driver_Selenium.criar_driver(local=True)

# Verificar e recriar o driver se a sessão caiu
driver = Driver_Selenium.verificar_e_recriar_driver(driver)
2. Classe Zendesk_Selenium
Esta classe contém todos os métodos para interagir com a interface web do Zendesk. Ela recebe uma instância do driver para operar.

Uso:

Python

# Crie o driver primeiro
driver = Driver_Selenium.criar_driver()

# Crie a instância da classe, passando o driver
zendesk_ui = Zendesk_Selenium(driver, "usuario", "senha", "sua_instancia")

# Execute ações
zendesk_ui.login()
zendesk_ui.driver.get("https://sua_instancia.zendesk.com/agent/tickets/12345")
zendesk_ui.selecionar_dropdown(360011074672, 'CD300')
zendesk_ui.enviar_aberto() # Usa ActionChains para atalhos
zendesk_ui.fechar_ticket_atual()
3. Classe Zendesk_Zenpy
Esta classe lida com todas as comunicações com a API do Zendesk.

Uso:

Python

# Crie a instância com as credenciais da API
zenpy_api = Zendesk_Zenpy("email_api", "token_api", "sua_instancia")

# Buscar tickets de uma fila (view)
id_da_fila = 123456789
tickets_na_fila = zenpy_api.pegar_tickets(fila=id_da_fila)

# Extrair campos personalizados de um ticket específico
id_do_ticket = tickets_na_fila[0]
campos_desejados = {'CD_ENTREGA': 360011074672, 'PRAZO_FCR': 360013231212}
valores = zenpy_api.extrair_customfields(ticket_id=id_do_ticket, lista_campos=campos_desejados)

print(valores)
# Saída: {'CD_ENTREGA': 'cd_300', 'PRAZO_FCR': '3_dias'}
📜 Exemplo de Script Principal (Robô Contínuo)
O exemplo abaixo mostra como combinar as classes para criar um robô que monitora uma fila do Zendesk continuamente, se recuperando de falhas de sessão.

Python

# Importações e credenciais
from classes import Driver_Selenium, Zendesk_Selenium, Zendesk_Zenpy
# ...

# Inicialização
driver = None

try:
    while True:
        # Garante que o driver está ativo antes de cada ciclo
        driver = Driver_Selenium.verificar_e_recriar_driver(driver)
        
        # Cria as instâncias das classes com o driver ativo
        zendesk = Zendesk_Selenium(driver, usuario, senha, instancia)
        zenpy = Zendesk_Zenpy(zemail, zpass, instancia)

        # 1. Faz o login (se necessário)
        zendesk.login()

        # 2. Busca tickets na API
        lista_tickets = zenpy.pegar_tickets(fila=12345)

        if not lista_tickets:
            print("Fila vazia. Aguardando...")
            sleep(600)
            continue
        
        # 3. Processa cada ticket
        for ticket_id in lista_tickets:
            driver.get(f'https://sua_instancia.zendesk.com/agent/tickets/{ticket_id}')
            zendesk.esperar_carregamento()
            # ...lógica de automação...
            zendesk.fechar_ticket_atual()
        
        sleep(120)

except KeyboardInterrupt:
    print("Robô interrompido pelo usuário.")
finally:
    if driver:
        print("Encerrando a sessão do driver.")
        driver.quit()
