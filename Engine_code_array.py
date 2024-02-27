import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC

# 데이터 로드
file_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\CRDR.csv"  # 실제 파일 경로로 변경 필요
data = pd.read_csv(file_path)

# Extract necessary columns and convert units
base_time = data['Time (seconds)'].values / 3600  # 초를 시간으로 변환
SOC = data['SOC'].values
current = data['Current(mA)'].values / 1000  # Convert mA to A
T_fixed = 298.15  # Fixed temperature in Kelvin

# k_cal, k_cyc 값 미리 계산
k_cal_values = np.array([k_Cal(T_fixed, soc) for soc in SOC])
k_cyc_high_T_values = np.array([k_Cyc_High_T(T_fixed) for _ in SOC])
k_cyc_low_T_values = np.array([k_Cyc_Low_T_Current(T_fixed, cur) for cur in current])
k_cyc_low_T_high_SOC_values = np.array([k_Cyc_Low_T_High_SOC(T_fixed, cur, soc) for cur, soc in zip(current, SOC)])

# Corrected function to calculate losses
def calculate_loss(time, current, initial_phi_ch, initial_phi_total):
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


# Simulation over multiple cycles
num_cycles = 500
initial_phi_ch = 0
initial_phi_total = 0
final_time = 0
cumulative_losses = []

for cycle in range(num_cycles):
    time = base_time + cycle * base_time[-1]
    results = calculate_loss(time, current, initial_phi_ch, initial_phi_total)
    total_losses, final_time, final_phi_ch, final_phi_total = results

    cumulative_loss = total_losses[-1]
    cumulative_losses.append(cumulative_loss)

    initial_phi_ch = final_phi_ch
    initial_phi_total = final_phi_total

cumulative_losses_percent = [loss * 100 for loss in cumulative_losses]
"""
# 누적 손실 시각화
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_cycles+1), cumulative_losses_percent, marker='', linestyle='-', linewidth=2)
plt.xlabel('Cycle Number')
plt.ylabel('Capacity Retention (%)')
plt.title('Capacity Retention over cycles')
plt.grid(False)
plt.show()
"""
# 누적 손실 시각화
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_cycles+1), cumulative_losses_percent, marker='', linestyle='-', linewidth=2)
plt.xlabel('Cycle Number')
plt.ylabel('Pure Cycling Capacity Retention (%)')
plt.title('Capacity Retention over cycles')
plt.grid(False)
plt.show()

# plt.figure(figsize=(10, 6))
# plt.plot(time_hours, calendar_losses, label='Calendar Loss')
# plt.plot(time_hours, cyc_high_T_losses, label='Cyc High T Loss')
# plt.plot(time_hours, cyc_low_T_losses, label='Cyc Low T Loss')
# plt.plot(time_hours, cyc_low_T_high_SOC_losses, label='Cyc Low T High SOC Loss')
# plt.plot(time_hours, total_losses, label='Total Loss', linewidth=2, color='black')
# plt.xlabel('Time (hours)')
# plt.ylabel('Loss')
# plt.title('Battery Aging Losses Over Time')
# plt.legend()
# plt.grid(True)
# plt.show()