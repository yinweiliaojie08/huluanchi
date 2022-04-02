// python SDK管理ECS安全组  
// pip install aliyun-python-sdk-ecs   
// 一个云账号、Access Key ID、Access Key Secret、安全组ID、Region ID(如cn-hangzhou，https://www.alibabacloud.com/help/zh/doc-detail/140601.htm这里查)  
// 修改脚本里的对应的四个参数  
// 使用参数说明：  
// python后面第一个参数是脚本名称；  
// 第二个参数是端口范围，一定要以"source-port/end-port"这种形式来写，这里以9100/9100为例；  
// 第三个参数是源ip 这里以115.197.107.141为例；  
// python secret_add.py 9100/9100 115.197.107.141  
// python secret_del.py 9100/9100 115.197.107.141
