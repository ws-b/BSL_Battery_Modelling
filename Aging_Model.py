import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

# Equation 9 : Temperature and SOC dependence for Calendar Aging
def k_Cal(T_kelvin, SOC):
    term1 = np.exp(-Ea_Cal * (1/T_kelvin - 1/T_Ref) / Rg)
    term2 = np.exp(alpha * F * (Ua_Ref - Ua_SOC(x_a(SOC))) / (Rg * T_Ref))
    return k_Cal_Ref * term1 * (term2 + k0)

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

# Equation 15: Temperature dependence for high temperature cycle aging
def k_Cyc_High_T(T):
    return k_Cyc_High_T_Ref * np.exp(-Ea_Cyc_High_T / Rg * (1 / T - 1 / T_Ref))


# Equation 18: Temperature and current rate dependence for low temperature cycle aging
def k_Cyc_Low_T_Current(T, I_Ch):
    temp_term = np.exp(Ea_Cyc_Low_T / Rg * (1 / T - 1 / T_Ref))

    current_term = np.exp(beta_Low_T * (I_Ch - I_Ch_Ref) / C0)
    return k_Cyc_Low_T_Ref * temp_term * current_term


# Equation 21 : Temperature and SOC dependence for low temperature and high SOC cycling Aging
def k_Cyc_Low_T_High_SOC(T, I_Ch, SOC):
    temp_term = np.exp(Ea_Cyc_Low_T_High_SOC / Rg * (1 / T - 1 / T_Ref))

    current_term = np.exp(beta_Low_T_High_SOC * (I_Ch - I_Ch_Ref) / C0)

    # SOC가 SOC_Ref 이상인 경우에만 계산 적용
    sgn_SOC = np.where(SOC - SOC_Ref >= 0, 1, 0)

    return k_Cyc_Low_T_High_SOC_Ref * temp_term * current_term * 0.5 * (sgn_SOC + 1)


# Creating the mesh for Temperature and SOC
temperature_celsius = np.linspace(0, 60, 101)  # Temperature range (°C)
soc_range = np.linspace(0, 100, 101)           # SOC range
T_mesh_celsius, SOC_mesh = np.meshgrid(temperature_celsius, soc_range)

# Creating the mesh for Temperature and Current
current_range = np.linspace(0, 3, 101)  # Current range (0C to 1C(3A))
T_mesh_celsius, Current_mesh = np.meshgrid(temperature_celsius, current_range)

# Calculate k_Cal values for the mesh
k_Cal_mesh_celsius = np.array([[k_Cal(T+273.15, SOC) for T, SOC in zip(t_row, SOC_mesh_row)]
                               for t_row, SOC_mesh_row in zip(T_mesh_celsius, SOC_mesh)])

# Calculate k_Cyc_High_T values for the mesh
k_Cyc_High_T_mesh = np.array([[k_Cyc_High_T(T+273.15) for T in t_row] for t_row in T_mesh_celsius])

# Calculate k_Cyc_Low_T_Current for the mesh
k_Cyc_Low_T_mesh = np.array([[k_Cyc_Low_T_Current(T+273.15, Current) for T, Current in zip(t_row, Current_mesh_row)]
                             for t_row, Current_mesh_row in zip(T_mesh_celsius, Current_mesh)])
# Calculate k_Cyc_Low_T_High_SOC for the mesh
# k_Cyc_Low_T_High_SOC_mesh = np.array([[k_Cyc_Low_T_High_SOC(T+273.15, Current, SOC) for T, Current, SOC in zip(t_row, Current_mesh_row, SOC_mesh_row)]
#                              for t_row, Current_mesh_row, SOC_mesh_row in zip(T_mesh_celsius, Current_mesh, SOC_mesh)])
# Calculate k_Cyc_Low_T_High_SOC for the mesh
k_Cyc_Low_T_High_SOC_mesh = np.array([[k_Cyc_Low_T_High_SOC(T+273.15, Current, 90) for T, Current in zip(t_row, Current_mesh_row)]
                             for t_row, Current_mesh_row in zip(T_mesh_celsius, Current_mesh)])


# # Plotting the 3D surface plot
# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection='3d')
#
# # Plotting the surface
# surf = ax.plot_surface(SOC_mesh, T_mesh_celsius, k_Cal_mesh_celsius, cmap='viridis')
#
# # Adding labels and title
# ax.set_xlabel('State of Charge (SOC) [%]')
# ax.set_ylabel('Temperature (°C)')
# ax.set_zlabel('k_Cal(T, SOC)')
# ax.set_title('3D Surface Plot of k_Cal(T, SOC)')



# # Plotting the 3D surface plot
# fig2 = plt.figure(figsize=(10, 7))
# ax2 = fig2.add_subplot(111, projection='3d')
#
# # Plotting the surface
# surf2 = ax2.plot_surface(T_mesh_celsius,Current_mesh, k_Cyc_High_T_mesh, cmap='inferno')
#
# # Adding labels and title
# ax2.set_xlabel('Temperature (°C)')
# ax2.set_ylabel('Current (A)')
# ax2.set_zlabel('k_Cyc_High_T(T)')
# ax2.set_title('3D Surface Plot of k_Cyc_High_T(T)')
#
# Plotting the 3D surface plot for k_Cyc_Low_T_Current
# fig3 = plt.figure(figsize=(10, 7))
# ax3 = fig3.add_subplot(111, projection='3d')
#
# # Plotting the surface
# surf3 = ax3.plot_surface(T_mesh_celsius, Current_mesh, k_Cyc_Low_T_mesh, cmap='viridis')
#
# # Adding labels and title
# ax3.set_xlabel('Temperature (°C)')
# ax3.set_ylabel('Current (A)')
# ax3.set_zlabel('k_Cyc_Low_T(T, I)')
# ax3.set_title('3D Surface Plot of k_Cyc_Low_T_Current(T, I)')
# ax3.set_xlim(60, 0)  # Set the x-axis limits from 60 to 0


# # # Plotting the 3D surface plot for k_Cyc_Low_T_Current
# fig4 = plt.figure(figsize=(10, 7))
# ax4 = fig4.add_subplot(111, projection='3d')
#
# # Plotting the surface
# surf4 = ax4.plot_surface(T_mesh_celsius, Current_mesh, k_Cyc_Low_T_High_SOC_mesh, cmap='viridis')
#
# # Adding labels and title
# ax4.set_xlabel('Temperature (°C)')
# ax4.set_ylabel('Current (A)')
# ax4.set_zlabel('k_Cyc_Low_T_High_SOC(T, I)')
# ax4.set_title('3D Surface Plot of k_Cyc_Low_T_High_SOC (T, I, SOC=100)')
# ax4.set_xlim(60, 0)  # Set the x-axis limits from 60 to 0

# Show the plot
plt.show()

