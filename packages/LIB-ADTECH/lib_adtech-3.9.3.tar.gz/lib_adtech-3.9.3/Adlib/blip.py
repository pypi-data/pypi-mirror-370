import time
from selenium.webdriver import Chrome
from Adlib.api import putStatusSolicitacao, EnumStatusSolicitacao, EnumStatus, putTicketBlip, putHoraFinalFunction

def ficarOnline(blip: Chrome):
    try:
        ficarOnline = blip.find_element('id' , 'set-online-btn')
        ficarOnline.click()
        time.sleep(5)
    except:
        print("ja esta online")
        time.sleep(5)

def transferiTicket(blip, tag, obsErro, ticket):
    try:
        print("Iniciando transferência 🔁")

        transferir = blip.find_elements('xpath', '//*[@id="transfer-ticket-button"]')[0]
        transferir.click()
        time.sleep(3)

        selecionarFila = blip.find_element('xpath', '//*[@id="transfer-attendance"]/div[1]/div/div[2]/div[1]/bds-autocomplete')
        selecionarFila.click()                    
        time.sleep(3)    
        selecionarFila.send_keys(tag)              
        time.sleep(3)

        shadow_host = blip.find_element('css selector', '#transfer-attendance > div.transfer-modal-content.w-100 > div > div.select-field > div:nth-child(1) > bds-autocomplete')
        time.sleep(3)

        shadow_root = blip.execute_script("return arguments[0].shadowRoot", shadow_host)
        time.sleep(3)

        elemento_desejado = shadow_root.find_element('css selector', 'div.select__options.select__options--position-bottom.select__options--open > bds-select-option:nth-child(12)')
        elemento_desejado.click()
        time.sleep(3)

        confirmarTransferencia = blip.find_element('xpath', '//*[@id="confirm-transfer-btn"]')
        confirmarTransferencia.click()

        putTicketBlip(EnumStatusSolicitacao.TRANSFERIDO, obsErro, ticket)
        putHoraFinalFunction(ticket)
        print("Ticket transferido 🔁")
    except Exception as e:
        print(f"❌ Erro na transferência: {e}")
