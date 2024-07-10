from datetime import datetime

filename = "vso_health_check_20230911_1948.csv"
date_str = filename.split('_')[3][:8]
check_date = datetime.strptime(date_str, '%Y%m%d').date()
print(check_date)
