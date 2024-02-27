import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC

# 데이터 로드
file_path = '/Users/wsong/Library/CloudStorage/SynologyDrive-wsong/SamsungSTF/Data/Aging_Model/CRDR.csv'  # 실제 파일 경로로 변경 필요
data = pd.read_csv(file_path)

# Extract necessary columns and convert units
time_hours = data['Time (seconds)'].values / 3600  # 초를 시간으로 변환
SOC = data['SOC'].values
current_A = data['Current(mA)'].values / 1000  # Convert mA to A
T_fixed = 298.15  # Fixed temperature in Kelvin

# Corrected function to calculate losses
def calculate_loss(time, current, initial_phi_ch, initial_phi_total):
    # Precompute k_cal and k_cyc values
    k_cal_values = np.array([k_Cal(T_fixed, soc) for soc in SOC])
    k_cyc_high_T_values = np.array([k_Cyc_High_T(T_fixed))
    k_cyc_low_T_values = np.array([k_Cyc_Low_T_Current(T_fixed, current) for current in current_A])
    k_cyc_low_T_high_SOC_values = np.array([k_Cyc_Low_T_High_SOC(T_fixed, current, soc) for current, soc in zip(current_A, SOC)])

    n = len(time)
    calendar_losses = np.zeros(n)
    cyc_high_T_losses = np.zeros(n)
    cyc_low_T_losses = np.zeros(n)
    cyc_low_T_high_SOC_losses = np.zeros(n)
    total_losses = np.zeros(n)
    epsilon = 1e-10  # A small constant

    for i in range(1, n):
        dt = time[i] - time[i-1]
        dQ = current[i] * dt

        if current[i] > 0:  # 양의 전류는 충전을 의미
            initial_phi_ch += abs(dQ)
        initial_phi_total += abs(dQ)

        calendar_losses = np.trapz(k_cal_values / (2 * np.sqrt(time+epsilon)), x=time)
        cyc_high_T_losses = np.trapz(k_cyc_high_T_values / (2 * np.sqrt(phi_total + epsilon)), x=phi_total_array)
        cyc_low_T_losses= np.trapz(k_cyc_low_T_values / (2 * np.sqrt(phi_ch+epsilon)), x=phi_ch)
        cyc_low_T_high_SOC_losses = np.trapz(k_cyc_low_T_high_SOC_values), x=phi_ch

        total_losses[i] = calendar_losses[i] + cyc_high_T_losses[i] + cyc_low_T_losses[i] + cyc_low_T_high_SOC_losses[i]

    # 최종 충전량 및 전체 충전량 업데이트
    final_time = time[-1]
    final_phi_ch = initial_phi_ch
    final_phi_total = initial_phi_total

    return total_losses, final_time, final_phi_ch, final_phi_total

# Simulation over multiple cycles
num_cycles = 300
initial_phi_ch = 0
initial_phi_total = 0
final_phi_total = 0
final_phi_ch = 0

cumulative_losses_over_cycles = []

for cycle in range(num_cycles):
    if cycle > 0:
        # 사이클마다 시간 데이터 업데이트: 각 요소에 누적 시간 추가
        time_hours = time_hours + final_time

    # calculate_loss 함수 호출: 필요한 인자 전달 및 final_time 업데이트 로직 확인
    results = calculate_loss(time_hours, current_A, initial_phi_ch, initial_phi_total)
    total_losses, final_phi_ch, final_phi_total, final_time = results

    cumulative_loss
    cumulative_losses_over_cycles.append(cumulative_loss)


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

# 사이클 번호에 따른 누적 손실 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_cycles + 1), cumulative_losses_over_cycles, label='Cumulative Loss over Cycles', marker='o')
plt.xlabel('Cycle Number')
plt.ylabel('Cumulative Loss')
plt.title('Cumulative Battery Aging Losses Over Multiple Cycles')
plt.legend()
plt.grid(True)
plt.show()