import pandas as pd
from datetime import datetime, timedelta

# 데이터 파일 경로
chg_data_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\Scaled_CCCV_chg.csv"
dcg_data_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\Scaled_CCCV_dcg.csv"
chg_data = pd.read_csv(chg_data_path)
dcg_data = pd.read_csv(dcg_data_path)

# 저장할 파일 경로
save_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\CRDR.csv"

# Coulomb counting을 위한 기본 설정
C0_Ah = 1.54  # 배터리의 총 용량 (Ah)
C0_As = C0_Ah * 3600  # 총 용량을 As (Ampere-second)로 변환

def calculate_SOC(data, initial_SOC, direction='charge'):
    SOC = [initial_SOC]
    for i in range(1, len(data)):
        time_diff = (pd.to_datetime(data.iloc[i]['Relative Time(h:min:s.ms)']) - pd.to_datetime(data.iloc[i-1]['Relative Time(h:min:s.ms)'])).total_seconds()
        current_A = data.iloc[i-1]['Current(mA)'] / 1000  # mA to A
        delta_Q_As = current_A * time_diff  # ΔQ = I * Δt

        if direction == 'charge':
            new_SOC = SOC[-1] + (delta_Q_As / C0_As) * 100
            if new_SOC > 99:
                new_SOC = 100
        else:  # direction == 'discharge'
            new_SOC = SOC[-1] + (delta_Q_As / C0_As) * 100
            if new_SOC < 1:
                new_SOC = 0

        SOC.append(new_SOC)
    data['SOC'] = SOC

# 충전 데이터에 대해 SOC 계산
calculate_SOC(chg_data, initial_SOC=0, direction='charge')

# 방전 데이터에 대해 SOC 계산
calculate_SOC(dcg_data, initial_SOC=100, direction='discharge')

# "Relative Time(h:min:s.ms)"를 datetime 객체로 변환
chg_data['Time'] = pd.to_datetime(chg_data['Relative Time(h:min:s.ms)'])
dcg_data['Time'] = pd.to_datetime(dcg_data['Relative Time(h:min:s.ms)'])

# 첫 번째 휴식 기간을 추가하기 위한 마지막 시간 계산
last_time_chg = chg_data['Time'].iloc[-1]
rest_time_1 = last_time_chg + timedelta(hours=1)

# 방전 데이터의 시작 시간을 첫 번째 휴식 기간 이후로 설정
start_time_dcg = rest_time_1
dcg_data['Time'] = start_time_dcg + (dcg_data['Time'] - dcg_data['Time'].iloc[0])

# 두 번째 휴식 기간을 추가하기 위한 마지막 시간 계산
last_time_dcg = dcg_data['Time'].iloc[-1]
rest_time_2 = last_time_dcg + timedelta(hours=1)

# 휴식 기간 데이터 생성
rest_period_1 = pd.DataFrame({'Time': [rest_time_1],
                              'Current(mA)': [0],
                              'Scaled Voltage(V)': [chg_data['Scaled Voltage(V)'].iloc[-1]],
                              'SOC': [chg_data['SOC'].iloc[-1]]})

rest_period_2 = pd.DataFrame({'Time': [rest_time_2],
                              'Current(mA)': [0],
                              'Scaled Voltage(V)': [dcg_data['Scaled Voltage(V)'].iloc[-1]],
                              'SOC': [dcg_data['SOC'].iloc[-1]]})

# 모든 데이터 결합
total_process = pd.concat([chg_data, rest_period_1, dcg_data, rest_period_2], ignore_index=True)

# 'Time' 열의 차이를 초 단위로 계산하여 새로운 열에 저장
total_process['Time (seconds)'] = (total_process['Time'] - total_process['Time'].iloc[0]).dt.total_seconds()

# "Time (seconds)", "Current(mA)", "Scaled Voltage(V)", "SOC" 열만 선택하여 CSV 파일로 저장
total_process.to_csv(save_path, columns=['Time (seconds)', 'Current(mA)', 'Scaled Voltage(V)', 'SOC'], index=False)

print("Data saved to:", save_path)