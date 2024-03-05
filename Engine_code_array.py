import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Aging_Model import k_Cal, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC

# Load data
file_path = "/Users/wsong/Library/CloudStorage/SynologyDrive-wsong/SamsungSTF/Data/Aging_Model/CRDR.csv"
data = pd.read_csv(file_path)

# Extract necessary columns and convert units
time = data['Time (seconds)'].values / 3600  # Convert seconds to hours
SOC = data['SOC'].values
current = data['Current(mA)'].values / 1000  # Convert mA to A

# Simulation settings
num_cycles = 500
temperature_settings = [273.15, 288.15, 298.15, 308.15, 318.15] # Temperatures: 0, 15, 25, 35, 45°C

# Function to calculate losses
def calculate_loss(time, current, Temperature, initial_phi_ch, initial_phi_total):
    # Pre-calculate k_cal, k_cyc values
    k_cal_values = np.array([k_Cal(t, soc) for t, soc in zip(Temperature, SOC)])
    k_cyc_high_T_values = np.array([k_Cyc_High_T(t) for t in Temperature])
    k_cyc_low_T_values = np.array([k_Cyc_Low_T_Current(t, cur) for t, cur in zip(Temperature, current)])
    k_cyc_low_T_high_SOC_values = np.array([k_Cyc_Low_T_High_SOC(t, cur, soc) for t, cur, soc in zip(Temperature, current, SOC)])

    # Calculate time intervals with correct handling for the first interval
    time_intervals = np.diff(time, prepend=0)

    # Calculate cumulative charge (Ah) for charging (phi_ch) and total charge/discharge (phi_total)
    phi_ch = np.cumsum(np.where(current > 0, current * time_intervals, 0) / 3600)
    phi_total = np.cumsum(np.abs(current * time_intervals) / 3600)

    integrand_cal = k_cal_values / np.where(time > 0, 2 * np.sqrt(time), 1)
    integrand_cyc1 = k_cyc_high_T_values / np.where(phi_total > 0, 2 * np.sqrt(phi_total), 1)
    integrand_cyc2 = k_cyc_low_T_values / np.where(phi_ch > 0, 2 * np.sqrt(phi_ch), 1)
    integrand_cyc3 = k_cyc_low_T_high_SOC_values

    # Calculate losses
    calendar_loss = np.trapz(integrand_cal, x=time)
    cyc_high_T_loss = np.trapz(integrand_cyc1, x=phi_total)
    cyc_low_T_loss = np.trapz(integrand_cyc2, x=phi_ch)
    cyc_low_T_high_SOC_loss = np.trapz(integrand_cyc3, x=phi_ch)

    total_losses = calendar_loss + cyc_high_T_loss + cyc_low_T_loss + cyc_low_T_high_SOC_loss
    return total_losses, integrand_cal, integrand_cyc1, integrand_cyc2, integrand_cyc3, time, phi_ch, phi_total

cumulative_losses_by_temp = {}

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

        # Stop the loop if capacity retention reaches 80%
        if cumulative_loss >= 0.2 and cycle_reached_80 is None:
            cycle_reached_80 = cycle + 1  # Store the cycle number when 80% capacity retention is first reached
            break

        initial_phi_ch = final_phi_ch
        initial_phi_total = final_phi_total

    cumulative_losses_percent = [loss * 100 for loss in cumulative_losses]
    cumulative_losses_by_temp[T_fixed] = cumulative_losses_percent

    if cycle_reached_80:
        print(f"At {int(T_fixed - 273.15)}°C, capacity reached 80% at cycle {cycle_reached_80}.")
    else:
        print(f"At {int(T_fixed - 273.15)}°C, capacity retention did not reach 80% within {num_cycles} cycles.")

plt.figure(figsize=(12, 8))

# Plot capacity retention over cycles for different temperatures
for T_fixed, losses in cumulative_losses_by_temp.items():
    cycles = range(1, len(losses) + 1)
    plt.plot(cycles, losses, marker='', linestyle='-', linewidth=2, label=f'Temperature = {int(T_fixed - 273.15)}°C')
plt.xlabel('Cycle Number')
plt.ylabel('Pure Cycling Capacity Retention (%)')
plt.title('Capacity Retention over cycles for different temperatures')
plt.legend()
plt.grid(True)
plt.show()
