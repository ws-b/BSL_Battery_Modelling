import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time as tm
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC
class CycleData:
    def __init__(self, cycle_number, initial_time = 0, initial_phi_ch = 0, initial_phi_total = 0):
        self.cycle_number = cycle_number
        self.cycle_losses = None
        self.initial_time = initial_time
        self.initial_phi_ch = initial_phi_ch
        self.initial_phi_total = initial_phi_total
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
        time_intervals = np.diff(time, prepend = time[0])

        phi_ch = np.cumsum(np.where(current > 0, current * time_intervals, 0)) + self.initial_phi_ch
        phi_total = np.cumsum(np.abs(current * time_intervals)) + self.initial_phi_total

        # Calculate integrands
        integrand_cal = k_cal_values / np.where(time > 0, 2 * np.sqrt(time), 1e-1)
        integrand_cyc1 = k_cyc_high_T_values / np.where(phi_total > 0, 2 * np.sqrt(phi_total), 1e-1)
        integrand_cyc2 = k_cyc_low_T_values / np.where(phi_ch > 0, 2 * np.sqrt(phi_ch), 1e-1)
        integrand_cyc3 = k_cyc_low_T_high_SOC_values

        # Calculate losses
        # self.cycle_losses = np.trapz(integrand_cal, x=time) + np.trapz(integrand_cyc1, x=phi_total) + np.trapz(integrand_cyc2, x=phi_ch) + np.trapz(integrand_cyc3, x=phi_ch)
        self.cal_losses = np.trapz(integrand_cal, x=time)
        self.cycle1_losses = np.trapz(integrand_cyc1, x=phi_total)
        self.cycle2_losses = np.trapz(integrand_cyc2, x=phi_ch)
        self.cycle3_losses = np.trapz(integrand_cyc3, x=phi_ch)
        self.cycle_losses = self.cycle1_losses + self.cycle2_losses + self.cycle3_losses
        self.total_losses = self.cal_losses + self.cycle_losses

        # Update final values for this cycle
        self.final_time = time
        self.final_phi_ch = phi_ch
        self.final_phi_total = phi_total

        return
# Load data
file_path = "/Users/wsong/Library/CloudStorage/SynologyDrive-SamsungSTF/Data/Aging_Model/CRDR.csv"
data = pd.read_csv(file_path)

# Extract necessary columns and convert units
time = data['Time (seconds)'].values / 3600  # Convert seconds to hours
SOC = data['SOC'].values
current = data['Current(mA)'].values / 1000  # Convert mA to A

# Simulation settings
num_cycles = 3000
temperature_settings = [273.15, 298.15] # Temperatures: 0, 15, 25, 35, 45°C

# making dictionary to store temperature losses
temperature_losses = {temp: [] for temp in temperature_settings}
cycle_1_losses = {temp: [] for temp in temperature_settings}
cycle_2_losses = {temp: [] for temp in temperature_settings}
cycle_3_losses = {temp: [] for temp in temperature_settings}

cycle_numbers = np.arange(1, num_cycles + 1)
temperature_calculation_times = {}

data_by_temp = {
    temp: {cycle: {'time': [], 'Q_cal' : [], 'Q_cycle1' : [], 'Q_cycle2' : [], 'Q_cycle3' : [], 'Q_total' : []} for cycle in range(1, num_cycles + 1)}
    for temp in temperature_settings
}

# calculate losses for each temperature
for temp in temperature_settings:
    # start time
    start_time = tm.time()
    initial_time = 0
    initial_phi_ch = 0
    initial_phi_total = 0
    cumulative_losses = []
    cycle1_losses = []
    cycle2_losses = []
    cycle3_losses = []

    for cycle in range(num_cycles):
        cycle_data = CycleData(cycle, initial_time, initial_phi_ch, initial_phi_total)
        Temperature = np.full(len(time), temp)
        cycle_data.calculate_loss(time, current, Temperature, SOC)

        # 온도별 손실을 저장합니다.
        cumulative_losses.append(cycle_data.cycle_losses)
        cycle1_losses.append(cycle_data.cycle1_losses)
        cycle2_losses.append(cycle_data.cycle2_losses)
        cycle3_losses.append(cycle_data.cycle3_losses)

        print(f"Cycle {cycle}: Q_loss : {cycle_data.cycle_losses}")

        # 온도별 사전에 각 사이클의 결과 추가
        data_by_temp[temp][cycle + 1]['time'].append(cycle_data.final_time)

        # 초기값을 업데이트합니다.
        initial_time = cycle_data.final_time[-1]
        initial_phi_ch = cycle_data.final_phi_ch[-1]
        initial_phi_total = cycle_data.final_phi_total[-1]

    # 누적 손실을 계산합니다.
    temperature_losses[temp] = np.cumsum(cumulative_losses)
    cycle_1_losses[temp] = np.cumsum(cycle1_losses)
    cycle_2_losses[temp] = np.cumsum(cycle2_losses)
    cycle_3_losses[temp] = np.cumsum(cycle3_losses)

    # 끝나는 시간 기록
    end_time = tm.time()  # 현재 시간(계산 완료 시간)을 기록합니다.
    calculation_time = end_time - start_time  # 계산에 걸린 시간을 계산합니다.
    temperature_calculation_times[temp] = calculation_time  # 계산 시간을 저장합니다.

# 온도별 계산 시간을 출력합니다.
for temp, calc_time in temperature_calculation_times.items():
    print(f"Temperature {int(temp - 273.15)}°C: Calculation took {calc_time:.2f} seconds")

plt.figure(figsize=(12, 12))

# 각 온도별로 사이클 손실 그래프를 그립니다.
for temp in temperature_settings:
    cycle_nums = np.arange(1, num_cycles + 1)

    # 각 사이클별 누적 손실값
    Q_cycle1_cumulative_losses = cycle_1_losses[temp]
    Q_cycle2_cumulative_losses = cycle_2_losses[temp]
    Q_cycle3_cumulative_losses = cycle_3_losses[temp]
    Q_cycle_cumulative_losses = temperature_losses[temp]

    # Q_cycle1 손실 그래프
    plt.subplot(2, 2, 1)
    plt.plot(cycle_nums, Q_cycle1_cumulative_losses, label=f'Temp = {int(temp - 273.15)}°C')
    plt.title('Q_cycle1 Cumulative Losses by Cycle')
    plt.xlabel('Cycle Number')
    plt.ylabel('Capacity Retention')
    plt.legend()
    plt.grid(True)

    # Q_cycle2 손실 그래프
    plt.subplot(2, 2, 2)
    plt.plot(cycle_nums, Q_cycle2_cumulative_losses, label=f'Temp = {int(temp - 273.15)}°C')
    plt.title('Q_cycle2 Cumulative Losses by Cycle')
    plt.xlabel('Cycle Number')
    plt.ylabel('Capacity Retention')
    plt.legend()
    plt.grid(True)

    # Q_cycle3 손실 그래프
    plt.subplot(2, 2, 3)
    plt.plot(cycle_nums, Q_cycle3_cumulative_losses, label=f'Temp = {int(temp - 273.15)}°C')
    plt.title('Q_cycle3 Cumulative Losses by Cycle')
    plt.xlabel('Cycle Number')
    plt.ylabel('Capacity Retention')
    plt.legend()
    plt.grid(True)

    # Q_cycle3 손실 그래프
    plt.subplot(2, 2, 4)
    plt.plot(cycle_nums, Q_cycle3_cumulative_losses, label=f'Temp = {int(temp - 273.15)}°C')
    plt.title('Pure Cycling Losses')
    plt.xlabel('Cycle Number')
    plt.ylabel('Capacity Retention')
    plt.legend()
    plt.grid(True)

plt.tight_layout()
plt.show()

# 각 온도에 대한 그래프 그리기
for temp in temperature_settings:
    # k 값 계산
    k_cal_values = np.array([k_Cal(t, soc) for t, soc in zip(np.full(len(time), temp), SOC)])
    k_cyc_high_T_values = np.array([k_Cyc_High_T(temp) for _ in time])
    k_cyc_low_T_current_values = np.array([k_Cyc_Low_T_Current(temp, cur) for cur in current])
    k_cyc_low_T_high_SOC_values = np.array([k_Cyc_Low_T_High_SOC(temp, cur, soc) for cur, soc in zip(current, SOC)])

    # 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(time, k_cal_values, label='k_Cal')
    plt.plot(time, k_cyc_high_T_values, label='k_Cyc_High_T')
    plt.plot(time, k_cyc_low_T_current_values, label='k_Cyc_Low_T_Current')
    plt.plot(time, k_cyc_low_T_high_SOC_values, label='k_Cyc_Low_T_High_SOC')

    plt.title(f'k Values Over Time at {temp - 273.15}°C')
    plt.xlabel('Time (hours)')
    plt.ylabel('k Values')
    plt.legend()
    plt.grid(True)
    plt.show()