import pandas as pd
import matplotlib.pyplot as plt

file_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\CRDR.csv"
df = pd.read_csv(file_path)

# 그래프 설정
fig, ax1 = plt.subplots()

# 첫 번째 y축 설정 (Current)
color = 'tab:red'
ax1.set_xlabel('Time (seconds)')
ax1.set_ylabel('Current(mA)', color=color)
ax1.plot(df['Time (seconds)'], df['Current(mA)'], color=color)
ax1.tick_params(axis='y', labelcolor=color)

# x축 공유하면서 두 번째 y축 생성 (Scaled Voltage)
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Scaled Voltage(V)', color=color)
ax2.plot(df['Time (seconds)'], df['Scaled Voltage(V)'], color=color)
ax2.set_ylim(2, 4)
ax2.tick_params(axis='y', labelcolor=color)

# 두 번째 y축 공유하면서 세 번째 y축 생성 (SOC)
ax3 = ax1.twinx()
color = 'tab:green'
# 오른쪽에 두 번째 y축 위치 조정
ax3.spines['right'].set_position(('outward', 60))
ax3.set_ylabel('SOC', color=color)
ax3.plot(df['Time (seconds)'], df['SOC'], color=color)
ax3.tick_params(axis='y', labelcolor=color)

# 그래프 제목 및 레이아웃 조정
plt.title('Time Series Plot of Current, Scaled Voltage, and SOC')
fig.tight_layout()

plt.show()
