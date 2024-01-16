import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def Ua(SOC):

    return  0.123

# Constants and parameters
k_Cal_Ref = 3.69e-4  # h^-0.5
Ea_Cal = 2.06e4      # J/mol
T_Ref = 298.15       # K (25°C)
Rg = 8.314           # J/(mol*K)
alpha = 0.384        # Dimensionless
F = 96485            # C/mol (Faraday constant)
UaRef = 0.123        # V (Reference potential)
k0 = 0.142           # Dimensionless offset

# Function for kCal(T, SOC)
def kCal(T_kelvin, SOC):
    term1 = np.exp(-Ea_Cal / Rg * (1/T_kelvin - 1/T_Ref))
    term2 = np.exp(alpha * F * (UaRef - Ua(SOC)) / (Rg * T_Ref))
    return k_Cal_Ref * term1 * term2 + k0

# Generating a meshgrid for temperature in Celsius and SOC
temperature_celsius = np.linspace(0, 70, 100)  # From 0°C to 70°C
temperature_kelvin = temperature_celsius + 273.15  # Converting to Kelvin
soc_range = np.linspace(0, 100, 100)  # From 0% to 100%
T_mesh_celsius, SOC_mesh = np.meshgrid(temperature_celsius, soc_range)

# Calculating k_Cal for each combination of temperature and SOC
k_Cal_mesh_celsius = np.array([[kCal(T, SOC) for SOC in soc_row] for T, soc_row in zip(temperature_kelvin, SOC_mesh)])

# Plotting the 3D graph with temperature in Celsius
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(T_mesh_celsius, SOC_mesh, k_Cal_mesh_celsius, cmap='viridis')

# Labels and title with temperature in Celsius
ax.set_xlabel('Temperature (°C)')
ax.set_ylabel('SOC (%)')
ax.set_zlabel('k_Cal(T, SOC)')
ax.set_title('3D Surface Plot of k_Cal(T, SOC)')

# # Adding a color bar
# fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

plt.show()
