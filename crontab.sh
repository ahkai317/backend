#!/bin/bash 
step=3 #間隔的秒數，不能大於60 
for (( i = 0; i < 60; i=i+(9) )); do 
/usr/local/bin/python /app/backend/manage.py get_stock_detail & 
/usr/local/bin/python /app/backend/manage.py get_stock_detail2
echo '=============== start sleeping... ==================='
sleep $step 
done 
exit 0 
