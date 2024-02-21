import numpy as np
import pandas as pd
from scipy.integrate import quad
from Aging_Model import k_Cal, x_a, Ua_SOC, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC
import matplotlib.pyplot as plt

# 데이터 파일 경로
file_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\CRDR.csv"
data = pd.read_csv(file_path)

T_fixed = 298.15  # Fixed temperature in Kelvin


# Define the integration functions as before
def integrate_k_cal(t, T, SOC):
    return k_Cal(T, SOC) / (2 * np.sqrt(t))


def integrate_k_cycHighT(phi_tot, T):
    return k_Cyc_High_T(T) / (2 * np.sqrt(phi_tot))


def integrate_k_cycLowT(phi_ch, T, I_Ch):
    return k_Cyc_Low_T_Current(T, I_Ch) / (2 * np.sqrt(phi_ch))


def integrate_k_cycLowTHighSOC(T, I_Ch, SOC):
    return k_Cyc_Low_T_High_SOC(T, I_Ch, SOC)


# Updated calculation process
def calculate_loss(data):
    # Initialize lists to store the results
    calendar_losses = []
    cyc_high_T_losses = []
    cyc_low_T_losses = []
    cyc_low_T_high_SOC_losses = []
    total_losses = []

    # Initialize cumulative charge for calculations
    cumul_chg_current = 0  # Cumulative charge current for charging periods
    cumul_current = 0  # Cumulative absolute current for all periods

    for i in range(len(data)):
        time_i = data.loc[i, 'Time (seconds)']
        SOC_i = data.loc[i, 'SOC']
        current_i = data.loc[i, 'Current(mA)'] / 1000  # Convert mA to A

        # Update cumulative currents
        if current_i > 0:
            cumul_chg_current += current_i  # Update only for charging currents
        cumul_current += abs(current_i)  # Update for all currents

        # Calculate calendar aging loss
        calendar_loss, _ = quad(lambda t: integrate_k_cal(t, T_fixed, SOC_i), 1e-6, time_i)

        # High temperature cycling loss calculated with cumulative charging current
        cyc_high_T_loss, _ = quad(lambda phi_tot: integrate_k_cycHighT(phi_tot, T_fixed), 1e-6, cumul_current)

        # Low temperature cycling losses calculated with cumulative absolute current
        cyc_low_T_loss, _ = quad(lambda phi_ch: integrate_k_cycLowT(phi_ch, T_fixed, current_i), 1e-6, cumul_chg_current)
        cyc_low_T_high_SOC_loss, _ = quad(lambda phi_ch: integrate_k_cycLowTHighSOC(T_fixed, current_i, SOC_i), 0, cumul_chg_current)

        # Store the results
        calendar_losses.append(calendar_loss)
        cyc_high_T_losses.append(cyc_high_T_loss)
        cyc_low_T_losses.append(cyc_low_T_loss)
        cyc_low_T_high_SOC_losses.append(cyc_low_T_high_SOC_loss)
        total_losses.append(calendar_loss + cyc_high_T_loss + cyc_low_T_loss + cyc_low_T_high_SOC_loss)

    return calendar_losses, cyc_high_T_losses, cyc_low_T_losses, cyc_low_T_high_SOC_losses, total_losses


# Execute the calculation
results = calculate_loss(data)
calendar_losses, cyc_high_T_losses, cyc_low_T_losses, cyc_low_T_high_SOC_losses, total_losses = results

# Optionally, add the results back to the dataframe and inspect or save
data['Calendar_Loss'] = calendar_losses
data['Cyc_High_T_Loss'] = cyc_high_T_losses
data['Cyc_Low_T_Loss'] = cyc_low_T_losses
data['Cyc_Low_T_High_SOC_Loss'] = cyc_low_T_high_SOC_losses
data['Total_Loss'] = total_losses

# Plotting
plt.figure(figsize=(14, 10))

# 시간 데이터
time = data['Time (seconds)'] / 3600

# Calendar Loss 그래프
plt.plot(time, data['Calendar_Loss'], label='Calendar Loss', linewidth=2)

# Cyc High Temperature Loss 그래프
plt.plot(time, data['Cyc_High_T_Loss'], label='Cyc High Temperature Loss', linewidth=2)

# Cyc Low Temperature Loss 그래프
plt.plot(time, data['Cyc_Low_T_Loss'], label='Cyc Low Temperature Loss', linewidth=2)

# Cyc Low Temperature High SOC Loss 그래프
plt.plot(time, data['Cyc_Low_T_High_SOC_Loss'], label='Cyc Low Temperature High SOC Loss', linewidth=2)

# Total Loss 그래프
plt.plot(time, data['Total_Loss'], label='Total Loss', linewidth=2, linestyle='--')

plt.title('Battery Aging Losses Over Time')
plt.xlabel('Time (hours)')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.show()