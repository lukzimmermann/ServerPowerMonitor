import datetime
import requests
import threading
import time
import numpy as np
from enum import Enum

class ShellyType(Enum):
    VALUE1 = "1PM"
    VALUE2 = "2PM"

class Data():
    def __init__(self) -> None:
        self.time = datetime.datetime.now()
        self.channel: int = -1
        self.status: bool = False
        self.power: float = -1.0
        self.voltage: float = -1.0
        self.current: float = -1.0
        self.frequency: float = -1.0
        self.pf: float = -1.0
        self.temperature: float = -1.0

class Shelly:
    def __init__(self, ip, type:ShellyType) -> None:
        self.ip = ip
        self.type = type

        if self.type == '1PM': self.number_of_channels = 1
        if self.type == '2PM': self.number_of_channels = 2

        self.dataset = []
        self.average_dataset = []

        self.thread = None
        self.stop_event = threading.Event()

    def get_raw_data(self):
        url = f'http://{self.ip}/rpc'
        data = {"id":0, "method":"Shelly.GetStatus"}

        response = requests.post(url, json=data)

        return response.json()

    def update_data(self):
        data = self.get_raw_data()

        dataset = []
        for i in range(self.number_of_channels):
            channel_name = f'switch:{i}'
            channel = Data()
            channel.channel = i
            channel.status = data['result'][channel_name]['output']
            channel.power = data['result'][channel_name]['apower']
            channel.voltage = data['result'][channel_name]['voltage']
            channel.current = data['result'][channel_name]['current']
            channel.frequency = data['result'][channel_name]['freq']
            channel.pf = data['result'][channel_name]['pf']
            channel.temperature = data['result'][channel_name]['temperature']['tC']
            dataset.append(channel)
        
        self.dataset = dataset
    
    def get_data(self) -> list[Data]:
        self.update_data()
        return self.dataset
    
    def get_average_data(self) -> list[Data]:

        data = []
        
        for i in range(self.number_of_channels):
            channel = Data()
            channel.channel = i
            channel.status = -1
            channel.power = self.average_dataset[i].power
            channel.voltage = self.average_dataset[i].voltage
            channel.current = self.average_dataset[i].current
            channel.frequency = self.average_dataset[i].frequency
            channel.pf = self.average_dataset[i].pf
            channel.temperature = self.average_dataset[i].temperature

            data.append(channel)

        return data
    
    def recording(self, length, interval):
        while not self.stop_event.is_set():

            self.update_data()

            self.average_dataset = []
            
            for i, data in enumerate(self.dataset):

                self.average_power[i].append(data.power)
                self.average_voltage[i].append(data.power)
                self.average_current[i].append(data.power)
                self.average_frequency[i].append(data.power)
                self.average_pf[i].append(data.power)
                self.average_temperature[i].append(data.power)

                if len(self.average_power[i]) > length:
                    self.average_power[i] = self.average_power[i][1:]
                    self.average_voltage[i] = self.average_voltage[i][1:]
                    self.average_current[i] = self.average_current[i][1:]
                    self.average_frequency[i] = self.average_frequency[i][1:]
                    self.average_pf[i] = self.average_pf[i][1:]
                    self.average_temperature[i] = self.average_temperature[i][1:]

                channel = Data()
                channel.channel = i
                channel.status = self.dataset[i].status
                channel.power = np.mean(self.average_power[i])
                channel.voltage = np.mean(self.average_voltage[i])
                channel.current = np.mean(self.average_current[i])
                channel.frequency = np.mean(self.average_frequency[i])
                channel.pf = np.mean(self.average_pf[i])
                channel.temperature = np.mean(self.average_temperature[i])
                self.average_dataset.append(channel)

            time.sleep(interval)

    def start_recording(self, length: int, interval: int, log_to_db=False):
        self.average_power = [[] for _ in range(self.number_of_channels)]
        self.average_voltage = [[] for _ in range(self.number_of_channels)]
        self.average_current = [[] for _ in range(self.number_of_channels)]
        self.average_frequency = [[] for _ in range(self.number_of_channels)]
        self.average_pf = [[] for _ in range(self.number_of_channels)]
        self.average_temperature = [[] for _ in range(self.number_of_channels)]

        self.thread = threading.Thread(target=self.recording, args=(length, interval))
        self.thread.start()

    def stop_recording(self):
        if self.thread is not None and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join()
