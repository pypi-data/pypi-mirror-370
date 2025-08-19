import os
import time
import logging
import threading
from .robos import importacaoCashCard
from .funcoes import setupDriver
from selenium import webdriver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BotManager:


    def __init__(self, botTask, shutdownCallback=None, countdown=600):
        """
        Initialize the BotManager.

        :param botTask: Função principal que executa o robô.
        :param countdown: Tempo de esperar para reiniciar o robô até a última tarefa concluída com sucesso
        """
        self.botTask = botTask
        self.shutdownCallback = shutdownCallback
        self.countdown = countdown
        self._botThread = None
        self._managerThread = None
        self._stopEvent = threading.Event()
        self._resetEvent = threading.Event()
        self._lock = threading.RLock()
        self.driver: webdriver.Chrome = None


    def _mainTaskWrapper(self):
        """Wrap the main task to handle its lifecycle."""
        try:
            logging.info("Iniciando robô")

            original_chrome = webdriver.Chrome

            def driver_wrapper(*args, **kwargs):
                driver = original_chrome(*args, **kwargs)
                self.driver = driver
                return driver

            webdriver.Chrome = driver_wrapper

            if not self._stopEvent.is_set():
                self.botTask(self._resetEvent)

            logging.info("Finalizando robô")
        except Exception as e:
            logging.error(f"Erro no robô: {e}")
        finally:
            webdriver.Chrome = original_chrome

            if self.driver:
                try:
                    self.driver.quit()
                    logging.info("Driver encerrado com sucesso.")
                except Exception as e:
                    logging.warning(f"Erro ao encerrar o driver: {e}")
                self.driver = None


    def _managerTask(self):
        """Manage the bot execution flow and handle restarts if necessary."""
        last_reset_time = float()  # Tracks the last reset time to prevent immediate restarts
        time.sleep(20)
        print()
        while not self._stopEvent.is_set():

            reset_triggered = self._resetEvent.wait(self.countdown)

            with self._lock:
                current_time = time.time()

                if reset_triggered:
                    logging.info("Reset event triggered, resetting countdown.")
                    time.sleep(30)
                    self._resetEvent.clear()
                    last_reset_time = current_time
                elif current_time - last_reset_time >= self.countdown:
                    logging.warning("Countdown expired, restarting the bot.")
                    self.restartBot()
                    last_reset_time = current_time
                else:
                    logging.info("Skipping restart to avoid immediate restart after reset.")


    def startBot(self):
        """Start the bot's main task in a separate thread."""
        with self._lock:
            self._resetEvent.set()
            if self._botThread is None or not self._botThread.is_alive():
                self._botThread = threading.Thread(target=self._mainTaskWrapper, daemon=True, name="BotThread")
                self._botThread.start()
                logging.info("Bot thread started.")


    def restartBot(self):
        """Restart the bot by stopping the current task and starting a new one."""
        with self._lock:
            if self._botThread and self._botThread.is_alive():
                logging.info("Stopping the current bot thread.")
                self._stopEvent.set()
                self.driver.quit()
                self._botThread.join(timeout=60)  # Aumentar o timeout, se necessário
                self._stopEvent.clear()
                
            logging.info("Starting a new bot thread.")

        self.startBot()


    def startManager(self):
        """Start the manager task in a separate thread."""
        if self._managerThread is None or not self._managerThread.is_alive():
            self._managerThread = threading.Thread(target=self._managerTask, daemon=True, name="ManagerThread")
            self._managerThread.start()
            logging.info("Manager thread started.")

    def stop(self):
        """Stop both the manager and the bot."""
        logging.info("Stopping manager and bot.")
        self._stopEvent.set()
        if self._botThread:
            self._botThread.join(timeout=2.5)
        if self._managerThread:
            self._managerThread.join(timeout=2.5)
        logging.info("All threads stopped.")
        if self.shutdownCallback:
            self.shutdownCallback()
        os._exit(0)


if __name__ == "__main__":

    tempo = 10 # Tempo

    def teste(restevent):
        while True:
            driver = setupDriver()
            driver.get("https://www.google.com")

            for i in range(100):
                print(i)
                time.sleep(1)

    manager1= BotManager(importacaoCashCard, countdown=60*tempo)
    # manager1 = BotManager(teste, countdown=60*tempo)
    manager1.startBot()
    manager1.startManager()

    # manager2 = BotManager(importacaoDaycovalCartao, countdown=60*tempo)
    # manager2.startBot()
    # manager2.startManager()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrupt received, shutting down.")
        manager1.stop()
        manager1.driver.quit()
        # manager2.stop()