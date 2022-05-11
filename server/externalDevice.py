#外接设备驱动  
import time
import requests

url = 'http://127.0.0.1:8899'

def deal(msg):
    print(msg)

if __name__ == '__main__':
    while True:
        params = {'id':'1'}
        data = requests.get(url+'/message', params).json()
        if(data['success']):
            deal(data['msg'])
        else:
            time.sleep(3)

