import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from Aging_Model import k_Cal, x_a, Ua_SOC, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC

# Constants and Parameters from Table IV
k_Cal_Ref = 3.69e-4  # h^-0.5
k_Cyc_High_T_Ref = 1.46e-4  # Ah^-0.5
k_Cyc_Low_T_Ref = 4.01e-4  # Ah^-0.5
k_Cyc_Low_T_High_SOC_Ref = 2.03e-6  # Ah^-1
Ea_Cal = 2.06e4  # J/mol
Ea_Cyc_High_T = 3.27e4  # J/mol
Ea_Cyc_Low_T = 5.55e4  # J/mol
Ea_Cyc_Low_T_High_SOC = 2.33e5  # J/mol
alpha = 0.384  # dimensionless
beta_Low_T = 2.64  # h
beta_Low_T_High_SOC = 7.84  # h
SOC_Ref = 82  # 82%
T_Ref = 298.15  # K (25°C)
I_Ch_Ref = 3  # A
Ua_Ref = 0.123  # V (Reference potential)
k0 = 0.142  # dimensionless
Rg = 8.314  # J/(mol*K)
F = 96485  # C/mol (Faraday constant)
C0 = 3  # Ah, nominal cell capacity

# Q_L_cal = k_cal(T+273.15, SOC) * sqrt(Time)
# Q_L_cyc_high_T = k_Cyc_High_T(T) * sqrt(Q_total)
# Q_L_cyc_low_T = k_Cyc_Low_T_Current(T,I_ch) * sqrt(Q_total)
# Q_L_cyc_high_T_SOC = k_Cyc_Low_T_High_SOC(T,I_ch, SOC) * Q_ch

# Q_Loss = Q_L_cal + Q_L_cyc_high_T + Q_L_cyc_low_T + Q_L_cyc_high_T_SOC

# 시간 범위 설정
time_range_days = np.linspace(0, 200, 200)  # 0일부터 200일
time_range_hours = time_range_days * 24  # 시간 단위로 변환

# SOC 값 범위 설정
soc_values = np.linspace(0, 100, 9)

# 고정된 값 설정
Temp = 15
T_fixed = Temp + 273.15
Current_fixed = 0  # Current fixed at 0
Q_total = 0  # Total charge fixed at 0
Q_ch = 0  # Charge fixed at 0

# Calculate the integrands
tau = 2*np.sqrt(time_range_hours)
phi_total = 2*np.sqrt(Q_total)
phi_ch = 2*np.sqrt(Q_ch)

# Calculate Q_L_cal for each SOC and time step
Q_L_cal_mesh = {soc: k_Cal(T_fixed, soc) * tau for soc in soc_values}

# Q_L_cyc_high_T_mesh = k_Cyc_High_T(T_fixed) * np.sqrt(Q_total)
# Q_L_cyc_low_T_mesh = k_Cyc_Low_T_Current(T_fixed, Current_mesh) * np.sqrt(Q_total)
# Q_L_cyc_high_T_SOC_mesh = k_Cyc_Low_T_High_SOC(T_fixed, Current_mesh, SOC_mesh) * Q_total

# Q_loss_percent_soc = {soc: [(k_Cal(T_fixed, soc) * np.sqrt(t) +
#                              k_Cyc_High_T(T_fixed) * np.sqrt(Q_total) +
#                              k_Cyc_Low_T_Current(T_fixed, Current_fixed) * np.sqrt(Q_total) +
#                              k_Cyc_Low_T_High_SOC(T_fixed, Current_fixed, soc) * Q_ch) / C0 * 100
#                              for t in time_range_hours] for soc in soc_values}

# Plotting
plt.figure(figsize=(12, 8))
for soc, q_l_cal in Q_L_cal_mesh.items():
    plt.plot(time_range_days, q_l_cal, label=f'SOC = {soc}%')

plt.xlabel('Time (days)')
plt.ylabel('Capacity Loss (%)')
plt.title('Calendar Aging Capacirty loss at 'f"{Temp}"'°C for Different SOC Values')
plt.legend()
plt.show()