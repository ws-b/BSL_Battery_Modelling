import numpy as np
import pandas as pd
from scipy.integrate import quad
import matplotlib.pyplot as plt
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC

# Path to the data file
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

    # Initialize lists to store cumulative charge capacities
    chr_cap_list = []
    cap_list = []
    chr_cap = 0
    cap = 0

    # Calculate time intervals (assuming the first time interval is 0)
    delta_t = np.diff(data['Time (seconds)'], prepend=0) / 3600  # Convert time to hours

    for i in range(len(data)):
        time = data['Time (seconds)'] / 3600
        SOC = data['SOC']
        current = data['Current(mA)'] / 1000  # Convert mA to A
        dt = delta_t[i]  # Current time interval

        # Update cumulative currents for charging
        if current[i] > 0:
            chr_cap += current[i] * dt
        # Update cumulative current for all currents
        cap += abs(current[i]) * dt

        # Append the current cumulative capacities to their respective lists
        chr_cap_list.append(chr_cap)
        cap_list.append(cap)

        # Calculate calendar aging loss
        calendar_loss, _ = quad(lambda t: integrate_k_cal(t, T_fixed, SOC[i]), 1e-6, time[i])

        # Calculate high temperature cycling loss with cumulative charging current
        cyc_high_T_loss, _ = quad(lambda phi_tot: integrate_k_cycHighT(phi_tot, T_fixed), 1e-6, cap_list[i])

        # Calculate low temperature cycling losses with cumulative absolute current
        cyc_low_T_loss, _ = quad(lambda phi_ch: integrate_k_cycLowT(phi_ch, T_fixed, current[i]), 1e-6, chr_cap_list[i])
        cyc_low_T_high_SOC_loss, _ = quad(lambda phi_ch: integrate_k_cycLowTHighSOC(T_fixed, current[i], SOC[i]), 0, chr_cap_list[i])

        # Store the results
        calendar_losses.append(calendar_loss)
        cyc_high_T_losses.append(cyc_high_T_loss)
        cyc_low_T_losses.append(cyc_low_T_loss)
        cyc_low_T_high_SOC_losses.append(cyc_low_T_high_SOC_loss)
        total_losses.append(calendar_loss + cyc_high_T_loss + cyc_low_T_loss + cyc_low_T_high_SOC_loss)

    return calendar_losses, cyc_high_T_losses, cyc_low_T_losses, cyc_low_T_high_SOC_losses, total_losses, chr_cap_list, cap_list

# Execute the calculation
results = calculate_loss(data)
calendar_losses, cyc_high_T_losses, cyc_low_T_losses, cyc_low_T_high_SOC_losses, total_losses,chr_cap_list, cap_list = results

# Optionally, add the results back to the dataframe and inspect or save
data['Cumulative_Charging_Capacity'] = chr_cap_list
data['Cumulative_Capacity'] = cap_list
data['Calendar_Loss'] = calendar_losses
data['Cyc_High_T_Loss'] = cyc_high_T_losses
data['Cyc_Low_T_Loss'] = cyc_low_T_losses
data['Cyc_Low_T_High_SOC_Loss'] = cyc_low_T_high_SOC_losses
data['Total_Loss'] = total_losses

# Plotting
plt.figure(figsize=(14, 10))

# Time data
time = data['Time (seconds)'] / 3600

# Plot Calendar Loss
plt.plot(time, data['Calendar_Loss'], label='Calendar Loss', linewidth=2, linestyle='dotted')

# Plot Cyc High Temperature Loss
plt.plot(time, data['Cyc_High_T_Loss'], label='Cyc High Temperature Loss', linewidth=2, linestyle='--')

# Plot Cyc Low Temperature Loss
plt.plot(time, data['Cyc_Low_T_Loss'], label='Cyc Low Temperature Loss', linewidth=2, linestyle='--')

# Plot Cyc Low Temperature High SOC Loss
plt.plot(time, data['Cyc_Low_T_High_SOC_Loss'], label='Cyc Low Temperature High SOC Loss', linewidth=2, linestyle='--')

# Plot Total Loss
plt.plot(time, data['Total_Loss'], label='Total Loss', linewidth=2)

plt.title('Battery Aging Losses Over Time')
plt.xlabel('Time (hours)')
plt.ylabel('Loss $Q_{Loss}$%')
plt.legend()
plt.grid(True)

plt.show()
