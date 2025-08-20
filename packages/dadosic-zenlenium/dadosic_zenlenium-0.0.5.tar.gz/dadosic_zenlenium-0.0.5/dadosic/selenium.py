from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from zenpy import Zenpy
from zenpy.lib.api_objects import CustomField, Ticket, Comment, User
from zenpy.lib.exception import RecordNotFoundException, APIException
from dataclasses import dataclass
from typing import Optional, Dict, Any, Iterable, List
import traceback

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = True

#Timeout padrão selenium
TIMEOUT = 300

#Status do heartbeat
execucao = 'EM EXECUÇÃO'
aguardando = 'AGUARDANDO CASOS'
erro = 'ERRO'
manutencao = 'EM MANUTENÇÃO'
desligado = 'DESLIGADO'

class Heartbeat():
    """Destinada a enviar atualizações via API para o painel de bots."""
    def __init__(self, bot_id, endpoint, token):
        self.bot_id = bot_id
        self.endpoint = endpoint
        self.token = token
    

    def alertas(self, alertas=None, status=None, warning=None, ticket_id=None):
        """Envia alertas via gchat, status para o painel e registro de casos realizados.

        Args:
            alertas: Envia notificação do status do RPA via GCHAT.
            status: Envia o status atual do bot para o painel de acompanhamento.
            warning: Envia uma notificação do erro do RPA via GCHAT.
            ticket_id: Envia o ticket para registro no banco e contagem de casos.
        """
        url_todos_status = self.endpoint
        headers = {
            'Token': self.token, 
            "Content-Type": "application/json"
        }
        payload = {
            "bot_id": self.bot_id,
        }
        campos_opcionais = [
            ("alertas", alertas),
            ("status", status),
            ("warning", warning),
            ("ticket_id", ticket_id),
        ]

        for campo, valor in campos_opcionais:
            if valor:
                payload[campo] = valor

        try:
            alert = requests.put(url_todos_status, json=payload, headers=headers, timeout=10, verify=False)
            print(f"--- Resposta da API Alerta ---\nCódigo de Status: {alert.status_code}")

        except Exception as e:
            print(f"Um erro geral e inesperado ocorreu: {e}")


class Driver_Selenium():
    """Destinada a criação e gerenciamento de drivers do selenium."""

    def criar_driver(local=False, timeout='5m', headless=True):
        """Cria um driver local ou virtual no selenoid, também é configuravel seu timeout.

        Args:
            local: False (padrão) para executar via selenoid, True para executar localmente.
            timeout: Configura o tempo de inatividade máximo do driver (Limite: 24h).

        Returns:
            driver aberto em selenium.
        """
        if local:
            options = ChromeOptions()
            driver = webdriver.Chrome(options=options)
        else:
            options = ChromeOptions()
            options.browser_version = "latest"
            options.set_capability("browserName", "chrome")
            options.set_capability(
                "selenoid:options", {
                    "enableVNC": True,
                    "sessionTimeout": timeout
                }
            )
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--blink-settings=imagesEnabled=false")

            driver = webdriver.Remote(
                command_executor="http://201.23.65.205:4444/wd/hub",
                options=options
            )
        driver.maximize_window()
        return driver

    def validar_driver(driver):
        """Verifica se o driver está ativo. Se não, cria um novo e o retorna."""
        if driver:
            try:
                _ = driver.title
                print("Sessão do driver está ativa.")
                return driver 
            except Exception:
                print("Sessão do driver inativa. Recriando...")
                try:
                    driver.quit()
                except Exception:
                    pass

        novo_driver = Driver_Selenium.criar_driver()
        return novo_driver


class Zendesk_Selenium:
    """Destinada à facilitar a automação UI da zendesk junto ao selenium."""
    def __init__(self, driver, usuario, senha, instancia):
        """Chamada inicial para configurar o ambiente.

        Args:
            driver: Driver criado na classe Driver Selenium.
            usuario: Usuario para realizar o login na zendesk.
            senha: Senha para realizar o login na zendesk.
            instancia: Instancia da zendesk para que o login possa ser efetuado corretamente.
        """
        self.driver = driver
        self.usuario = usuario
        self.senha = senha
        self.instancia = instancia


    def login(self):
        """Realiza o login na plataforma zendesk."""
        link = self.instancia
        link = f'https://{link}.zendesk.com/access/normal'
        self.driver.get(link)
        try:
            login_zendesk = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, 'user_email'))
            )
            login_zendesk.send_keys(self.usuario)

            pass_zendesk = self.driver.find_element(By.ID, 'user_password')
            pass_zendesk.send_keys(self.senha)

            entrar_zendesk = self.driver.find_element(By.ID, 'sign-in-submit-button')
            entrar_zendesk.click()
        except:
            pass

        WebDriverWait(self.driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="home_icon"]'))
        )


    def play(self, fila:int):
        """Inicia o play automatico de uma visualização da zendesk.

        Args:
            fila (int): Número da visualização da zendesk.
        """
        self.driver.get(self.fila)
        play = WebDriverWait(self.driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="views_views-header-play-button"]'))
                )
        play.click()
        sleep(5)

    def fechar_dois_pacotes(self):
        """Procura e fecha o MODAL de 2 pacotes dentro do ticket na zendesk.
        
        Returns:
            True quando modal foi encontrado e fechado, False quando o modal não foi encontrado no ticket.
        """
        try:
            dois_pacotes = WebDriverWait(self.driver, 30).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'header.modal-header a.close'))
                        )
            dois_pacotes.click()
            return True
        except:
            return False
        
    def selecionar_dropdown(self, id: int, valor_campo: str):
        """ Seleciona a opção desejada dentro de um campo dropdown na zendesk.

        Args:
            id (int): Identificador único do custom field na zendesk.
            valor_campo (str): Exato valor a ser preenchido nas opções do dropdown.
        """
        seletor = f'[data-test-id="ticket-form-field-dropdown-field-{id}"] [data-garden-id="typography.ellipsis"]'
        campo = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, seletor))
        )
        campo.click()

        menu = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id="ticket-form-field-dropdown-menu"]'))
        )

        opcao = WebDriverWait(menu, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'.//li[.//span[normalize-space()="{valor_campo}"]]'))
        )
        opcao.click()
    
    def obter_valores_input(self, ids:dict):
        """Verifica e retorna os valores preenchidos dentro campos input.

        Args:
            ids (dict): Dicionario com Nome do campo e ID unico do campo input.

        Returns:
            Dicionario com Nome dos campos e valor dentro dele.
        """
        valores_campos = {}
        for nome_campo, id_campo in ids.items():
            try:
                seletor = f'.custom_field_{id_campo} input[data-test-id="ticket-fields-text-field"]'
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                valor_elemento = elemento.get_attribute("value")
                valores_campos[nome_campo] = valor_elemento

            except NoSuchElementException:
                print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
                valores_campos[nome_campo] = None
            
        return valores_campos
        
    def obter_valores_dropdown(self, ids:dict):
        """Realiza a captura de todos os valores dentro de campos dropdown na zendesk.

        Args:
            ids (dict): Dicionario contendo o nome do campo e ID unico do campo dropdown.

        Returns:
            dict: Dicionario contendo o nome do campo e o valor dentro do dropdown que está selecionado.
        """
        valores_campos = {}
        for nome_campo, id_campo in ids.items():
            try:
                seletor = f'[data-test-id="ticket-form-field-dropdown-field-{id_campo}"] [data-garden-id="typography.ellipsis"]'
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                valor_elemento = elemento.text
                valores_campos[nome_campo] = valor_elemento

            except NoSuchElementException:
                print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
                valores_campos[nome_campo] = None
        return valores_campos
        
    def preencher_input(self, id:int, valor:str):
        """Preenche com um valor o campo input pre-determinado.

        Args:
            id (int): ID unico do custom field da zendesk.
            valor (str): Valor a ser preenchido no campo.

        Returns:
            None em caso de falha ao não conseguir localizar o elemento.
        """
        seletor = f'.custom_field_{id} input[data-test-id="ticket-fields-text-field"]'
        try:
            campo = self.driver.find_element(By.CSS_SELECTOR, seletor)
            campo.send_keys(valor)

        except NoSuchElementException:
            print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
            return None
        
    def enviar_ticket(self, status:str):
        """Encerra o ticket enviando ele como resolvido, aberto, pendente ou em espera.

        Args:
            status (str): Nome do status que o ticket precisa ser enviado.
        """
        actions = ActionChains(self.driver)
        status_ajustado = status.lower()
        if status_ajustado == 'aberto':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('o').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        elif status_ajustado == 'resolvido':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('s').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        elif status_ajustado == 'espera' or status_ajustado == 'em espera':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('d').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        elif status_ajustado == 'pendente':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('p').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()

    def fechar_ticket_atual(self):
        """Fecha o ticket atual para evitar cacheamento no driver durante as iterações em cada ticket."""
        for i in range(3):
            try:
                fechar_ticket = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="close-button"]'))
                )
                fechar_ticket.click()
                # fechar_aba = WebDriverWait(self.driver,10).until(
                #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="ticket-close-confirm-modal-confirm-btn"]'))
                # )
                # fechar_aba.click()
                print('Ticket fechado.')
                break
            except (StaleElementReferenceException, TimeoutException):
                print(f"Tentando fechar ticket.. Elemento obsoleto... (tentativa {i+1})")
                sleep(2)
    
    def esperar_carregamento(self):
        """Ao enviar o ticket como aberto ou outro status, é necessario aguardar o carregamento do ticket para fecha-lo."""
        try:
            seletor_de_carregamento = (By.CSS_SELECTOR, "section.main_panes.ticket.working")
            
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(seletor_de_carregamento)
            )
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.invisibility_of_element_located(seletor_de_carregamento)
            )
            sleep(2)

        except TimeoutException:
            print("Nenhum círculo de carregamento detectado, continuando...")
            pass
    
    def enviar_mensagem(self, mensagem: str, publica=False):
        """Envia mensagem dentro do ticket como obs. interna ou pública.

        Args:
            mensagem (str): Mensagem a ser enviada no ticket.
            publica (bool, optional): True para enviar mensagem ao cliente, False para adicionar observação interna, o padrão é False.
        """
        try:
            actions = ActionChains(self.driver)
            if publica:
                actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('c').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
            else:
                actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('x').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
                
            caixa_texto = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="omnicomposer-rich-text-ckeditor"]'))
            )
            caixa_texto.send_keys(mensagem)

        except Exception as e:
            print(e)

    def aplicar_macro(self, macro:str):
        """Aplica uma macro no ticket.

        Args:
            macro (str): Nome da macro que consta no zendesk (ATENÇÃO: Necessario ser exatamente o nome da macro e NÃO o caminho dela com ::)
        """
        try:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('m').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()

            input_macro = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='ticket-footer-macro-menu-autocomplete-input'] input"))
            )
            input_macro.send_keys(macro)
            sleep(2)
            clickmacro = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'[aria-label="{macro}"]'))
            )
            clickmacro.click()
        except Exception as e:
            print(e)



class Zendesk_Zenpy:
    """Destinada a facilitar as automações via zenpy na zendesk."""
    def __init__(self, zlogin, zpass, instancia):
        self.zlogin = zlogin
        self.zpass = zpass
        self.instancia = instancia
        self.zenpy_client = None
        self.auth_zenpy()


    def auth_zenpy(self):
        """Realiza a autenticação na API."""
        creds = {
            'email': self.zlogin,
            'token': self.zpass,
            'subdomain': self.instancia
        }
        try:
            print("Autenticando cliente Zenpy...")
            self.zenpy_client = Zenpy(session=session, **creds)
            print("Cliente Zenpy autenticado com sucesso.")
        except Exception as e:
            print(f"Erro na autenticação do Zenpy: {e}")

    def _zenpy_client(self):
        return self.zenpy_client
            
    def pegar_tickets(self, fila:int, minimo=1, invertido=False):
        """Captura todos os tickets dentro de uma visualização na zendesk.

        Args:
            fila (int): ID da visualização.
            minimo (int, optional): Minimo de casos que a visualização precisa para retornar. Padrão setado em 1.
            invertido (bool, optional): False para retornar os pedidos em ordem crescente, True para retornar os pedidos em ordem decrescente. Padrão setado em False.

        Returns:
            None em casos de erros ou quantidade minima não atingida. Lista com todos os tickets para caso de sucesso.
        """
        print('Verificando tickets na fila...')
        
        if not self.zenpy_client:
            print("Erro: Cliente Zenpy não foi autenticado. Verifique as credenciais.")
            return None
        
        todos_os_tickets = []
        try:
            for ticket in self.zenpy_client.views.tickets(view=fila):
                todos_os_tickets.append(ticket.id)
            if len(todos_os_tickets) >= minimo:
                print(f'A visualização conta com {len(todos_os_tickets)} tickets.')
                todos_os_tickets = sorted(todos_os_tickets, reverse=invertido)
                return todos_os_tickets
            else:
                print(f'A visualização não tem o minimo de tickets para inicializar. (Minimo: {minimo} Fila: {len(todos_os_tickets)})')
                return None
        except Exception as e:
            print(f"Erro ao buscar tickets: {str(e)}")
            return None
        
    def _valores_customfield(self, ticket: Any) -> Dict[int, Any]:
        
        if not hasattr(ticket, 'custom_fields') or not ticket.custom_fields:
            return {}

        field_objects: Iterable[Any]
        if hasattr(ticket.custom_fields, 'values'):
            field_objects = ticket.custom_fields.values()
        else:
            field_objects = ticket.custom_fields

        parsed_fields = {}
        for field in field_objects:
            field_id = None
            field_value = None

            if isinstance(field, dict):
                field_id = field.get('id')
                field_value = field.get('value')
            elif hasattr(field, 'id') and hasattr(field, 'value'):
                field_id = field.id
                field_value = field.value
            
            if field_id is not None:
                parsed_fields[field_id] = field_value
        
        return parsed_fields
    
    def extrair_customfields(self, ticket_id:int, lista_campos: Dict[str, int]) -> Optional[Dict[str, Any]]:
        try:
            ticket = self.zenpy_client.tickets(id=ticket_id)

            todos_os_valores = self._valores_customfield(ticket)

            resultado = {}
            for nome, id_campo in lista_campos.items():
                valor = todos_os_valores.get(id_campo)
                resultado[nome] = valor

            return resultado
        except RecordNotFoundException:
            print(f"Ticket {ticket_id} não encontrado no Zendesk.")
            return None
        except APIException as e:
            print(f"Erro de API ao buscar ticket {ticket_id}: {e}")
            return None
        except Exception:
            print(f"Erro inesperado ao processar ticket {ticket_id}:")
            traceback.print_exc()
            return None

#=============================================================================

