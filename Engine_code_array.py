import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC

# 데이터 로드
file_path = "/Users/wsong/Library/CloudStorage/SynologyDrive-wsong/SamsungSTF/Data/Aging_Model/CRDR.csv"  # 실제 파일 경로로 변경 필요
data = pd.read_csv(file_path)

# Extract necessary columns and convert units
base_time = data['Time (seconds)'].values / 3600  # 초를 시간으로 변환
SOC = data['SOC'].values
current = data['Current(mA)'].values / 1000  # Convert mA to A
T_fixed = 298.15  # Fixed temperature in Kelvin
T_array = np.full_like(SOC, T_fixed)

# Corrected function to calculate losses
def calculate_loss(time, current, Temperature, initial_phi_ch, initial_phi_total):
    # k_cal, k_cyc 값 미리 계산
    k_cal_values = np.array([k_Cal(t, soc) for t, soc in zip(Temperature, SOC)])
    k_cyc_high_T_values = np.array([k_Cyc_High_T(t) for t in Temperature])
    k_cyc_low_T_values = np.array([k_Cyc_Low_T_Current(t, cur) for t, cur in zip(Temperature, current)])
    k_cyc_low_T_high_SOC_values = np.array([k_Cyc_Low_T_High_SOC(t, cur, soc) for t, cur, soc in zip(Temperature, current, SOC)])

    n = len(time)
    total_losses = np.zeros(n)

    phi_ch_values = np.zeros(n)
    phi_total_values = np.zeros(n)

    # 손실 계산
    for i in range(1, n):
        dt = time[i] - time[i - 1]
        dQ = current[i] * dt
        if current[i] > 0:  # 충전 시
            initial_phi_ch += abs(dQ)
        initial_phi_total += abs(dQ)

        phi_ch_values[i] = initial_phi_ch
        phi_total_values[i] = initial_phi_total

        # 0으로 나누는 것을 방지하기 위해 안전한 분모를 계산
        safe_denominator_cal = np.where(time[:i] > 0, 2 * np.sqrt(time[:i]), 1)
        safe_denominator_cyc_high_T = np.where(phi_total_values[:i] > 0, 2 * np.sqrt(phi_total_values[:i]), 1)
        safe_denominator_cyc_low_T = np.where(phi_ch_values[:i] > 0, 2 * np.sqrt(phi_ch_values[:i]), 1)

        # 손실 계산
        #calendar_loss = np.trapz(k_cal_values[:i] / safe_denominator_cal, x=time[:i])
        cyc_high_T_loss = np.trapz(k_cyc_high_T_values[:i] / safe_denominator_cyc_high_T, x=phi_total_values[:i])
        cyc_low_T_loss = np.trapz(k_cyc_low_T_values[:i] / safe_denominator_cyc_low_T, x=phi_total_values[:i])
        cyc_low_T_high_SOC_loss = np.trapz(k_cyc_low_T_high_SOC_values[:i], x=phi_ch_values[:i])

        # total_losses[i] = calendar_loss + cyc_high_T_loss + cyc_low_T_loss + cyc_low_T_high_SOC_loss
        total_losses[i] = cyc_high_T_loss + cyc_low_T_loss + cyc_low_T_high_SOC_loss
    return total_losses, time[-1], phi_ch_values[-1], phi_total_values[-1]

# Temperature settings in Kelvin for the simulation
temperature_settings = [273.15, 288.15, 298.15, 308.15, 318.15] # 0, 15, 25, 35, 45°C
cumulative_losses_by_temp = {}

# Simulation over multiple cycles
num_cycles = 500

# Running simulation for each temperature setting
for T_fixed in temperature_settings:
    T_array = np.full_like(SOC, T_fixed)
    initial_phi_ch = 0
    initial_phi_total = 0
    cumulative_losses = []
    cycle_reached_80 = None

    for cycle in range(num_cycles):
        time = base_time + cycle * base_time[-1]
        results = calculate_loss(time, current, T_array, initial_phi_ch, initial_phi_total)
        total_losses, final_time, final_phi_ch, final_phi_total = results

        cumulative_loss = total_losses[-1]
        cumulative_losses.append(cumulative_loss)

        if cumulative_loss >= 0.2 and cycle_reached_80 is None:
            cycle_reached_80 = cycle + 1  # 첫 번째로 80%에 도달한 사이클 저장
            break

        initial_phi_ch = final_phi_ch
        initial_phi_total = final_phi_total

    cumulative_losses_percent = [loss * 100 for loss in cumulative_losses]
    cumulative_losses_by_temp[T_fixed] = cumulative_losses_percent

    if cycle_reached_80:
        print(f"At {T_fixed}°C, capacity retention reached 80% at cycle {cycle_reached_80}.")
    else:
        print(f"At {T_fixed}°C, capacity retention did not reach 80% within {num_cycles} cycles.")

plt.figure(figsize=(12, 8))

# 각 온도별로 사이클에 따른 capacity retention 그리기
for T_fixed, losses in cumulative_losses_by_temp.items():
    # 각 온도 설정에 대한 사이클 수는 losses 리스트의 길이에 따라 달라짐
    cycles = range(1, len(losses) + 1)
    plt.plot(cycles, losses, marker='', linestyle='-', linewidth=2, label=f'Temperature = {int(T_fixed - 273.15)}°C')
plt.xlabel('Cycle Number')
plt.ylabel('Pure Cycling Capacity Retention (%)')
plt.title('Capacity Retention over cycles for different temperatures')
plt.legend()
plt.grid(True)
plt.show()