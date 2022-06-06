#!/bin/bash 
step=3 #間隔的秒數，不能大於60 
for (( i = 0; i < 60; i=i+(12) )); do 
/usr/local/bin/python /app/backend/manage.py get_stock_detail
echo '=============== start sleeping... ==================='
sleep $step 
done 
exit 0 
