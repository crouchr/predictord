# Predictord needs to locate the forecaster-service microservice

# Option 1 - when using IDE
#endpoint_base = 'http://172.27.0.2:9501'

# Option2 - when using container
#endpoint_base = 'http://forecaster-service:9501'

# Option2 - when using xw6600
endpoint_base = 'http://localhost:9501'

# for accessing sunrise/sunset external API
metminimisc_service_listen_port = 9505
#metminimisc_service_endpoint_base = 'http://127.0.0.1:' + listen_port.__str__()
metminimisc_service_endpoint_base = 'http://192.168.1.180:' + metminimisc_service_listen_port.__str__()

light_service_listen_port = 9503
light_service_endpoint_base = 'http://192.168.1.180:' + light_service_listen_port.__str__()