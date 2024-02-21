import pandas as pd

# 파일 경로
file_path = '/Users/wsong/Downloads/CCCV_dcg.csv'

# 데이터 불러오기
df = pd.read_csv(file_path)

# 전압(Voltage)의 최소값과 최대값 확인
min_voltage = df['Voltage(V)'].min()
max_voltage = df['Voltage(V)'].max()

# 스케일링할 새로운 최소값과 최대값 설정
new_min = 2.7
new_max = 3.4

# 선형 변환 적용하여 새로운 범위로 스케일링
df['Scaled Voltage(V)'] = ((df['Voltage(V)'] - min_voltage) / (max_voltage - min_voltage)) * (new_max - new_min) + new_min

# 결과를 새 파일로 저장
output_file_path = '/Users/wsong/Downloads/Scaled_CCCV_dcg.csv'
df.to_csv(output_file_path, index=False)
