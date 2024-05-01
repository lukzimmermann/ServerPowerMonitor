import os
import time
import threading
from enum import Enum
from dotenv import load_dotenv
from src.shelly import Data, Shelly

load_dotenv()

class Source(Enum):
    ROUTER = "ROUTER"
    SERVER = "SERVER"
    K3S = "K3S"
    SWITCH = "SWITCH"

class DataCollector():
    def __init__(self, interval: int, max_length: int) -> None:
        self.interval = interval
        self.max_length = max_length
        self.router_history = []
        self.server_history = []
        self.k3s_history = []
        self.switch_history = []
        self.thread = None
        self.stop_event = threading.Event()
        self.shelly1 = Shelly(os.getenv("SHELLY1_IP"), '2PM')
        self.shelly2 = Shelly(os.getenv("SHELLY1_IP"), '2PM')

        self.start_data_collecting()

    def start_data_collecting(self):
        self.thread = threading.Thread(target=self.__collect_data)
        self.thread.start()

    def stop_data_collecting(self):
        self.stop_event.set()

    def get_last_dataset(self, type: Source) -> Data:
        if type == Source.ROUTER:
            if len(self.router_history) > 1:
                return self.router_history[-1]
            else:
                return Data()
        elif type == Source.SERVER:
            if len(self.server_history) > 1:
                return self.server_history[-1]
            else:
                return Data()
        elif type == Source.K3S:
            if len(self.k3s_history) > 1:
                return self.k3s_history[-1]
            else:
                return Data()
        elif type == Source.SWITCH:
            if len(self.switch_history) > 1:
                return self.switch_history[-1]
            else:
                return Data()
    
    def get_dataset(self, type: Source) -> list[Data]:
        if type == Source.ROUTER:
            return self.router_history
        elif type == Source.SERVER:
            return self.server_history
        elif type == Source.K3S:
            return self.k3s_history
        elif type == Source.SWITCH:
            return self.switch_history

    def __collect_data(self):
        while not self.stop_event.is_set():
            data = self.shelly1.get_data()
            self.router_history.append(data[0])
            self.server_history.append(data[1])

            data = self.shelly2.get_data()
            self.k3s_history.append(data[0])
            self.switch_history.append(data[1])

            if len(self.router_history) > self.max_length:
                self.router_history = self.router_history[1:]
                self.server_history = self.server_history[1:]
                self.k3s_history = self.k3s_history[1:]
                self.switch_history = self.switch_history[1:]

            time.sleep(self.interval)