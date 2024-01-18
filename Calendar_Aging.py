import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Ua(SOC) function definition
def x_a(SOC):
    return 8.5e-3 + 0.01 * SOC * (7.8e-1 - 8.5e-3)

def Ua_SOC(x_a_value):
    result = (0.6379 + 0.5416 * np.exp(-305.5309 * x_a_value)
              + 0.044 * np.tanh(-(x_a_value - 0.1958) / 0.1088)
              - 0.1978 * np.tanh((x_a_value - 1.0571) / 0.0854)
              - 0.6875 * np.tanh((x_a_value + 0.0117) / 0.0529)
              - 0.0175 * np.tanh((x_a_value - 0.5692) / 0.0875))
    return result

# Constants and parameters for k_Cal calculation
k_Cal_Ref = 3.69e-4  # h^-0.5
Ea_Cal = 2.06e4      # J/mol
T_Ref = 298.15       # K (25°C)
Rg = 8.314           # J/(mol*K)
alpha = 0.384        # Dimensionless
F = 96485            # C/mol (Faraday constant)
Ua_Ref = 0.123       # V (Reference potential)
k0 = 0.142           # Dimensionless offset

def kCal(T_kelvin, SOC):
    term1 = np.exp(-Ea_Cal * (1/T_kelvin - 1/T_Ref) / Rg)
    term2 = np.exp(alpha * F * (Ua_Ref - Ua_SOC(x_a(SOC))) / (Rg * T_Ref))
    return k_Cal_Ref * term1 * (term2 + k0)

# Creating the mesh for Temperature and SOC
temperature_celsius = np.linspace(0, 60, 101)  # Temperature range (°C)
soc_range = np.linspace(0, 100, 101)           # SOC range
T_mesh_celsius, SOC_mesh = np.meshgrid(temperature_celsius, soc_range)

# Calculate k_Cal values for the mesh
k_Cal_mesh_celsius = np.array([[kCal(T+273.15, SOC) for T, SOC in zip(t_row, SOC_mesh_row)]
                               for t_row, SOC_mesh_row in zip(T_mesh_celsius, SOC_mesh)])

# Plotting the 3D surface plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Plotting the surface
surf = ax.plot_surface(SOC_mesh, T_mesh_celsius, k_Cal_mesh_celsius, cmap='viridis')

# Adding labels and title
ax.set_xlabel('Temperature (°C)')
ax.set_ylabel('State of Charge (SOC) [%]')
ax.set_zlabel('k_Cal(T, SOC)')
ax.set_title('3D Surface Plot of k_Cal(T, SOC)')

# Show the plot
plt.show()
