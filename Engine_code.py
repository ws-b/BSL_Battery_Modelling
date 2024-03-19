import numpy as np
import pandas as pd
from scipy.integrate import quad
import matplotlib.pyplot as plt
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC

# Path to the data file
file_path = '/Users/wsong/Library/CloudStorage/SynologyDrive-wsong/SamsungSTF/Data/Aging_Model/CRDR.csv'
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

# Define the function to calculate the losses
def calculate_loss(data, initial_time=0, initial_chr_cap=0, initial_cap=0):
    calendar_losses = []
    cyc_high_T_losses = []
    cyc_low_T_losses = []
    cyc_low_T_high_SOC_losses = []
    total_losses = []

    chr_cap_list = []
    cap_list = []
    time_list = []

    chr_cap = initial_chr_cap
    cap = initial_cap
    prev_time = initial_time

    for i in range(len(data)):
        SOC = data.loc[i, 'SOC']
        current = data.loc[i, 'Current(mA)'] / 1000  # Convert mA to A
        time = data.loc[i, 'Time (seconds)'] / 3600  # Convert seconds to hours
        dt = time - prev_time

        if current > 0:
            chr_cap += current * dt
        cap += abs(current) * dt

        chr_cap_list.append(chr_cap)
        cap_list.append(cap)
        time_list.append(time)

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

    final_time = data['Time (seconds)'].iloc[-1] / 3600  # Update final_time to the last time value in hours
    return calendar_losses, cyc_high_T_losses, cyc_low_T_losses, cyc_low_T_high_SOC_losses, total_losses, chr_cap_list, cap_list, chr_cap, cap, final_time

# Call the function with the initial values
num_cycles = 3
cumulative_losses_over_cycles = []
initial_chr_cap = 0
initial_cap = 0
initial_time = 0

for cycle in range(num_cycles):
    results = calculate_loss(data, initial_chr_cap, initial_cap, initial_time)
    _, _, _, _, total_losses, _, _, final_chr_cap, final_cap, final_time = results
    cumulative_loss = total_losses[-1]
    cumulative_losses_over_cycles.append(cumulative_loss if cycle == 0 else cumulative_losses_over_cycles[-1] + cumulative_loss)
    # Prepare for the next cycle
    initial_chr_cap = final_chr_cap
    initial_cap = final_cap
    initial_time = final_time


# Variables to carry over the last values from one cycle to the next
last_time = 0
last_chr_cap = 0
last_cap = 0

for cycle in range(num_cycles):
    # Call calculate_loss with the last values from the previous cycle
    _, _, _, _, total_losses, time_list, chr_cap_list, cap_list = calculate_loss(data, last_time, last_chr_cap, last_cap)

    # Update for the next cycle
    last_time = time_list[-1]
    last_chr_cap = chr_cap_list[-1]
    last_cap = cap_list[-1]


"""
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
"""

# Plotting the cumulative losses over cycles
plt.figure(figsize=(10, 6))
plt.plot(range(1, num_cycles + 1), cumulative_losses_over_cycles, label='Cumulative Total Losses', marker='o')
plt.xlabel('Cycle Number')
plt.ylabel('Cumulative Loss')
plt.title('Cumulative Losses Over Cycles')
plt.legend()
plt.grid(True)
plt.show()