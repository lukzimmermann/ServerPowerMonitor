import time
import streamlit as st
import numpy as np
from src.data_collector import DataCollector, Source
from src.shelly import Data


INTERVAL = 1

def main():
    st.title("Server Power Monitor")

    data = DataCollector(INTERVAL, 10000)

    def get_metric_data(dataset: list[Data]) -> tuple[float, float]:
        value = -1.0
        delta = -1.0
        length = len(dataset)
        if length > 1:
            value = dataset[-1].power
        if length > 2:
            delta = dataset[-1].power - dataset[-2].power

        return value, delta

    def get_plot_data(dataset: list[Data], max_length) -> list[float]:
        data_list = []
        if len(dataset) > max_length:
            length = max_length
        else:
            length = len(dataset)
        
        for i, item in enumerate(reversed(dataset)):
            if i > length: break

            data_list.insert(0, item.power)
        
        return data_list

    def update_metric():

        col1, col2, col3, col4 = st.columns(4)
        with col1: router = st.empty()
        with col2: server = st.empty()
        with col3: k3s = st.empty()
        with col4: switch = st.empty()

        with st.container(height=30, border=False): pass
        
        graph = st.empty()

        while True:
            value, delta = get_metric_data(data.get_dataset(Source.ROUTER))
            router.metric(label="Router", value=f"{value:.1f} W", delta=f"{delta:.1f} W", delta_color="inverse")

            value, delta = get_metric_data(data.get_dataset(Source.SERVER))
            server.metric(label="Server", value=f"{value:.1f} W", delta=f"{delta:.1f} W", delta_color="inverse")

            value, delta = get_metric_data(data.get_dataset(Source.K3S))
            k3s.metric(label="k3s", value=f"{value:.1f} W", delta=f"{delta:.1f} W", delta_color="inverse")

            value, delta = get_metric_data(data.get_dataset(Source.SWITCH))
            switch.metric(label="Switch and AP", value=f"{value:.1f} W", delta=f"{delta:.1f} W", delta_color="inverse")


            MAX_LENGTH = 50
            data_set = {
                "Router": get_plot_data(data.get_dataset(Source.ROUTER), MAX_LENGTH),
                "Server": get_plot_data(data.get_dataset(Source.ROUTER), MAX_LENGTH),
                "k3s": get_plot_data(data.get_dataset(Source.K3S), MAX_LENGTH),
                "Switch and AP": get_plot_data(data.get_dataset(Source.SWITCH), MAX_LENGTH)
            }
            graph.line_chart(data_set)

            time.sleep(INTERVAL)

    update_metric()

if __name__ == "__main__":
    main()