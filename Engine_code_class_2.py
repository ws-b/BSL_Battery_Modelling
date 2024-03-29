import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time as tm
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC
class CycleData:
    def __init__(self, cycle_number, initial_time=0, initial_phi_ch=0, initial_phi_total=0):
        self.cycle_number = cycle_number
        self.cycle_losses = 0
        self.initial_time = initial_time
        self.initial_phi_ch = initial_phi_ch
        self.initial_phi_total = initial_phi_total
        self.integrand_cyc1_losses = []
        self.integrand_cyc2_losses = []
        self.integrand_cyc3_losses = []
        self.final_time = None
        self.final_phi_ch = None
        self.final_phi_total = None

    def calculate_loss(self, base_time, current, Temperature, SOC):
        # Adjust time by adding the initial time of this cycle
        time = base_time + self.initial_time

        # Calculate k_cal, k_cyc values
        k_cal_values = np.array([k_Cal(t, soc) for t, soc in zip(Temperature, SOC)])
        k_cyc_high_T_values = np.array([k_Cyc_High_T(t) for t in Temperature])
        k_cyc_low_T_values = np.array([k_Cyc_Low_T_Current(t, cur) for t, cur in zip(Temperature, current)])
        k_cyc_low_T_high_SOC_values = np.array([k_Cyc_Low_T_High_SOC(t, cur, soc) for t, cur, soc in zip(Temperature, current, SOC)])

        # Calculate time intervals
        time_intervals = np.diff(time, prepend=0)

        # Adjust phi_ch and phi_total by adding initial values
        phi_ch = np.cumsum(np.where(current > 0, current * time_intervals, 0)) + self.initial_phi_ch
        phi_total = np.cumsum(np.abs(current * time_intervals)) + self.initial_phi_total

        # Calculate integrands
        integrand_cal = k_cal_values / np.where(time > 0, 2 * np.sqrt(time), 1e-6)
        integrand_cyc1 = k_cyc_high_T_values / np.where(phi_total > 0, 2 * np.sqrt(phi_total), 1e-6)
        integrand_cyc2 = k_cyc_low_T_values / np.where(phi_ch > 0, 2 * np.sqrt(phi_ch), 1e-6)
        integrand_cyc3 = k_cyc_low_T_high_SOC_values

        # Calculate losses
        self.integrand_cyc1_losses = np.trapz(integrand_cyc1, x=phi_total)
        self.integrand_cyc2_losses = np.trapz(integrand_cyc2, x=phi_ch)
        self.integrand_cyc3_losses = np.trapz(integrand_cyc3, x=phi_ch)

        # Update final values for this cycle
        self.final_time = time[-1]
        self.final_phi_ch = phi_ch[-1]
        self.final_phi_total = phi_total[-1]

# Load data
file_path = "/Users/wsong/Library/CloudStorage/SynologyDrive-wsong/SamsungSTF/Data/Aging_Model/CRDR.csv"
data = pd.read_csv(file_path)

# Extract necessary columns and convert units
time = data['Time (seconds)'].values / 3600  # Convert seconds to hours
SOC = data['SOC'].values
current = data['Current(mA)'].values / 1000  # Convert mA to A

# Simulation settings
num_cycles = 300
temperature_settings = [273.15, 298.15] # Temperatures: 0, 15, 25, 35, 45°C

# Simulation loop
cycles_data = []
initial_time = 0
initial_phi_ch = 0
initial_phi_total = 0

# making dictionary to store temperature losses
integrand_losses = {temp: {'cyc1': [], 'cyc2': [], 'cyc3': []} for temp in temperature_settings}
cycle_numbers = np.arange(1, num_cycles + 1)
temperature_calculation_times = {}

# calculate losses for each temperature
for temp in temperature_settings:
    # start time
    start_time = tm.time()
    # initial values
    initial_time = 0
    initial_phi_ch = 0
    initial_phi_total = 0
    cumulative_losses = []

    for cycle in range(num_cycles):
        cycle_data = CycleData(cycle, initial_time, initial_phi_ch, initial_phi_total)
        Temperature = np.full(len(time), temp)
        cycle_data.calculate_loss(time, current, Temperature, SOC)

        integrand_losses[temp]['cyc1'].append(cycle_data.integrand_cyc1_losses)
        integrand_losses[temp]['cyc2'].append(cycle_data.integrand_cyc2_losses)
        integrand_losses[temp]['cyc3'].append(cycle_data.integrand_cyc3_losses)

        # 초기값을 업데이트합니다.
        initial_time = cycle_data.final_time
        initial_phi_ch = cycle_data.final_phi_ch
        initial_phi_total = cycle_data.final_phi_total

    # 끝나는 시간 기록
    end_time = tm.time()  # 현재 시간(계산 완료 시간)을 기록합니다.
    calculation_time = end_time - start_time  # 계산에 걸린 시간을 계산합니다.
    temperature_calculation_times[temp] = calculation_time  # 계산 시간을 저장합니다.

# 온도별 계산 시간을 출력합니다.
for temp, calc_time in temperature_calculation_times.items():
    print(f"Temperature {int(temp - 273.15)}°C: Calculation took {calc_time:.2f} seconds")

# 결과 시각화
plt.figure(figsize=(12, 8))
cycle_numbers = np.arange(1, num_cycles + 1)

colors = ['blue', 'orange', 'green']
line_styles = ['-', '--']  # 0°C는 실선, 25°C는 점선

for i, (temp, losses) in enumerate(integrand_losses.items()):
    temp_label = f"{int(temp - 273.15)}°C"
    for j, (integrand_key, loss_values) in enumerate(losses.items()):
        plt.plot(cycle_numbers, np.cumsum(loss_values), line_styles[i], color=colors[j],
                 label=f'{integrand_key} at {temp_label}')

plt.xlabel('Cycle Number')
plt.ylabel('Cumulative Loss')
plt.title('Cumulative Losses over Cycles by Temperature and Integrand')
plt.legend()
plt.grid(True)
plt.show()