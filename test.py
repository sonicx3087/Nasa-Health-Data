from datetime import datetime

filename = "vso_health_check_20220321_130704.csv"
date_str = filename.split('_')[3][:8]
check_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
print(check_date)
