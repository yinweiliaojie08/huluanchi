#!/bin/bash
host=$1
port=$2
#end_date=`openssl s_client -host $host -port $port -showcerts </dev/null 2>/dev/null | sed -n '/BEGIN CERTIFICATE/,/END CERT/p'| openssl x509 -text 2>/dev/null | sed -n 's/ *Not After : *//p'`

end_date=`timeout 2 openssl s_client -servername ${host}  -connect ${host}:${port} 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | awk -F '=' '{print $2}'`

if [ -n "$end_date" ]
then
    end_date_seconds=`date '+%s' --date "$end_date"`
    now_seconds=`date '+%s'`
    echo "($end_date_seconds-$now_seconds)/24/3600" | bc 
fi
