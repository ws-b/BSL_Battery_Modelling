import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
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

# 적분을 위한 더미 함수들
def integrate_k_cal(t, T, SOC):
    return k_Cal(T, SOC) / (2*np.sqrt(t)) * 100

def integrate_k_cycHighT(phi_tot, T):
    return k_Cyc_High_T(T) / (2*np.sqrt(phi_tot))

def integrate_k_cycLowT(phi_ch, T, I_Ch):
    return k_Cyc_Low_T_Current(T, I_Ch) / (2*np.sqrt(phi_ch))

def integrate_k_cycLowTHighSOC(T, I_Ch, SOC):
    return k_Cyc_Low_T_High_SOC(T, I_Ch, SOC)


phi_tot_start = 0
phi_tot_end = 500  # 총 충전량
phi_ch_start = 0
phi_ch_end = 500  # 충전 충전량

# Calculate Q_Loss_cal for different SOCs over time
T_celsius = 45
T = T_celsius + 273.15  # Temperature in Kelvin
soc_range = np.linspace(0, 100, 9)  # SOC values from 0 to 100 in 8 intervals

# Days and corresponding hours for integration
days = np.linspace(0, 250, 250)
hours = days * 24
t_start = 1e-6

# Q_Loss_cal, _ = quad(integrate_k_cal, t_start, t_end, args=(T, SOC))
# Q_Loss_cycHighT, _ = quad(integrate_k_cycHighT, phi_tot_start, phi_tot_end, args=(T,))
# Q_Loss_cycLowT, _ = quad(integrate_k_cycLowT, phi_ch_start, phi_ch_end, args=(T, I_Ch))
# Q_Loss_cycLowTHighSOC, _ = quad(integrate_k_cycLowTHighSOC, phi_ch_start, phi_ch_end, args=(T, I_Ch, SOC))

# # 총 용량 손실 계산
# Q_Loss_total = Q_Loss_cal + Q_Loss_cycHighT + Q_Loss_cycLowT + Q_Loss_cycLowTHighSOC

# Plotting
plt.figure(figsize=(10, 6))

for SOC in soc_range:
    Q_Loss_cal = [quad(integrate_k_cal, t_start, h, args=(T, SOC))[0] for h in hours]
    plt.plot(days, Q_Loss_cal, label=f'SOC = {SOC}%')


plt.xlabel('Days')
plt.ylabel('Calendar Aging Loss $Q_{Loss_{cal}}$%')
plt.title("Calendar Aging Loss at "f"{T_celsius}""'C over Time for Different SOCs")
plt.legend()
plt.grid(False)
plt.show()