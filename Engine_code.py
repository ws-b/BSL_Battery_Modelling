import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import quad
from Aging_Model import k_Cal, x_a, Ua_SOC, k_Cyc_High_T, k_Cyc_Low_T_Current, k_Cyc_Low_T_High_SOC
from datetime import datetime, timedelta

# 데이터 파일 경로
chg_data_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\Scaled_CCCV_chg.csv"
dcg_data_path = r"C:\Users\WSONG\SynologyDrive\SamsungSTF\Data\Aging_Model\Scaled_CCCV_dcg.csv"
chg_data = pd.read_csv(chg_data_path)
dcg_data = pd.read_csv(dcg_data_path)

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
            # 충전 시 SOC가 99를 초과하면 100으로 조정
            new_SOC = min(100, new_SOC)
        else:  # direction == 'discharge'
            new_SOC = SOC[-1] - (delta_Q_As / C0_As) * 100
            # 방전 시 SOC가 1 미만이면 0으로 조정
            new_SOC = max(0, new_SOC)

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

# 'Time' 열을 다시 문자열로 변환하거나, 필요한 형식으로 유지합니다.
# 예: total_process['Time'] = total_process['Time'].dt.strftime('%Y-%m-%d %H:%M:%S')

# 결과 확인
print(total_process[['Time', 'Current(mA)', 'Scaled Voltage', 'SOC']].tail())


"""
# 적분을 위한 함수들
def integrate_k_cal(t, T, SOC):
    return k_Cal(T, SOC) / (2*np.sqrt(t)) * 100

def integrate_k_cycHighT(phi_tot, T):
    return k_Cyc_High_T(T) / (2*np.sqrt(phi_tot))

def integrate_k_cycLowT(phi_ch, T, I_Ch):
    return k_Cyc_Low_T_Current(T, I_Ch) / (2*np.sqrt(phi_ch))

def integrate_k_cycLowTHighSOC(T, I_Ch, SOC):
    return k_Cyc_Low_T_High_SOC(T, I_Ch, SOC)


# 사이클 반복 설정
N = 5  # 사이클 횟수
T = 298.15  # 온도 (K)
SOC = 80  # 상태 용량 (%)
I_Ch = 1.5  # 충전 전류 (A)
rest_time_hours = 1  # 휴식 시간 (시간 단위)

# 적분 범위 설정
phi_tot_start, phi_tot_end = 0, 1.5  # 총 충전량 (Ah), 예시 값
phi_ch_start, phi_ch_end = 0, 1.5  # 충전 중 충전량 (Ah), 예시 값

# 각 사이클마다의 총 손실 계산에 충전 및 방전 시간을 고려한 수정
Q_losses = []
total_hours = 0  # 초기 총 경과 시간

# 충전 및 방전 데이터의 첫 번째와 마지막 'Relative Time'을 datetime 객체로 변환
chg_start_relative = datetime.strptime(chg_data['Relative Time(h:min:s.ms)'].iloc[0], '%H:%M:%S.%f')
chg_end_relative = datetime.strptime(chg_data['Relative Time(h:min:s.ms)'].iloc[-1], '%H:%M:%S.%f')
dcg_start_relative = datetime.strptime(dcg_data['Relative Time(h:min:s.ms)'].iloc[0], '%H:%M:%S.%f')
dcg_end_relative = datetime.strptime(dcg_data['Relative Time(h:min:s.ms)'].iloc[-1], '%H:%M:%S.%f')

# timedelta 객체로 충전 및 방전 과정의 총 시간 계산
chg_duration_timedelta = chg_end_relative - chg_start_relative
dcg_duration_timedelta = dcg_end_relative - dcg_start_relative

# 총 시간을 시간 단위로 변환
chg_total_hours = chg_duration_timedelta.total_seconds() / 3600
dcg_total_hours = dcg_duration_timedelta.total_seconds() / 3600


for cycle in range(N):
    # Charge phase
    charge_start = total_hours
    total_hours += chg_total_hours  # Actual charge time from data
    charge_end = total_hours

    # First rest phase after charging
    rest_start = total_hours
    total_hours += rest_time_hours
    rest_end = total_hours

    # Calendar aging loss during rest phases
    Q_loss_cal_rest1, _ = quad(integrate_k_cal, rest_start, rest_end, args=(T, SOC))

    # Discharge phase
    discharge_start = total_hours
    total_hours += dcg_total_hours  # Actual discharge time from data
    discharge_end = total_hours

    # Second rest phase after discharging
    rest_start = total_hours
    total_hours += rest_time_hours
    rest_end = total_hours

    # Calendar aging loss during rest phases
    Q_loss_cal_rest2, _ = quad(integrate_k_cal, rest_start, rest_end, args=(T, SOC))

    # Cycle aging loss during charging
    Q_loss_cyc_chg, _ = quad(integrate_k_cycHighT, phi_tot_start, phi_tot_end, args=(T,))

    # Additional cycle aging loss during charging at low temperature and high SOC
    # Note: This assumes you want to evaluate it over the same phi_tot range as Q_loss_cyc_chg
    Q_loss_cycLowTHighSOC, _ = quad(integrate_k_cycLowTHighSOC, phi_tot_start, phi_tot_end, args=(T, I_Ch, SOC))

    # Cycle aging loss during discharging
    Q_loss_cyc_dcg, _ = quad(integrate_k_cycLowT, phi_ch_start, phi_ch_end, args=(T, I_Ch))

    # Total cycle loss including the additional cycle aging loss during charging
    Q_loss_cyc = Q_loss_cyc_chg + Q_loss_cycLowTHighSOC + Q_loss_cyc_dcg
    Q_loss_total = Q_loss_cal_rest1 + Q_loss_cal_rest2 + Q_loss_cyc
    Q_losses.append(Q_loss_total)

# 시간 경과에 따른 Q_loss 그래프 생성
hours = np.linspace(0, total_hours, N)
plt.figure(figsize=(10, 6))
plt.plot(hours, Q_losses, '-o', label='Total Q_loss')
plt.xlabel('Time (Hours)')
plt.ylabel('Total Q_loss')
plt.title('Total Q_loss Over Time')
plt.legend()
plt.grid(True)
plt.show()
"""