import pandas as pd
import matplotlib.pyplot as plt

# 데이터 불러오기 및 처리
file_path = '/Users/wsong/Downloads/OCV25-20120905/LFP_OCV_with_SOC.csv'  # 파일 경로를 실제 경로로 변경
data = pd.read_csv(file_path)
voltage = data.iloc[:, 2]  # 3열: 전압
soc = data.iloc[:, 3] # 4열 : SOC

# 그래프 그리기
plt.figure(figsize=(10, 6))
plt.scatter(soc, voltage, alpha=0.5)
plt.title("OCV-SOC Graph")
plt.xlabel("State of Charge (%)")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.show()
