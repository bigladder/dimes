# pylint:disable=C0114

from pathlib import Path
from dimes import GridAxis, GridPointData, RegularGridData


def test_2d_data():
    temperature = GridAxis([40, 50, 65, 70, 80, 90], name="Temperature", native_units="degF")
    humidity = GridAxis([0, 33, 67, 100], name="Relative Humidity", native_units="%")

    capacity_data = []
    power_data = []
    for t_value in temperature.data_values:
        for h_value in humidity.data_values:
            capacity_data.append(t_value + h_value)
            power_data.append((t_value + h_value) * 3.5)

    capacity = GridPointData(capacity_data, name="Capacity")
    power = GridPointData(power_data, name="Power")

    gridded_data = RegularGridData([temperature, humidity], [capacity, power])
    gridded_data.plot(capacity.name, temperature.name, {humidity.name: 33}, "capacity.html")
