import websocket
import json
import pyupbit
try:
    import thread
except ImportError:
    import _thread as thread
import time
f=open("upbit.txt")
lines=f.readlines()
access=lines[0].strip()
secret=lines[1].strip()
f.close()
upbit=pyupbit.Upbit(access,secret)


dataFromServer = [ ]
tic60=[]
linelist60=[]
linelist120=[]
gradient120=[]
hold= False
def on_message(ws, message):
    get_message = json.loads(message.decode('utf-8'))
    dataFromServer.append(get_message['trade_price'])
    if len(dataFromServer) >= 60:  # 데이터 개수가 60개 넘어가면은 그값을 평균내서 60틱봉 data60으로 저장한다.
        data60 = sum(dataFromServer[-60:]) / 60
        if len(dataFromServer)%60==0:
            tic60.append(data60)  # tic60 은 60틱봉 한개데이터
        if len(tic60) >= 120:  # 60틱봉 개수가 120개가 넘어가면 120선과 60선 데이터를 만들어준다.
            line60 = sum(tic60[-60:]) / 60
            line120 = sum(tic60[-120:]) / 120
            linelist60.append(line60)
            linelist120.append(line120)
            if len(linelist120) >= 2:
                ave = (linelist120[-1] - linelist120[-2]) / 2
                gradient120.append(ave)
            else:
                gradient120.append(0)
            if len(gradient120) > 20:
                gradient120_ave20 = (sum(gradient120[-20:])) / 20
            else:
                gradient120_ave20 = 0

            krw_balance=upbit.get_balance("KRW")
            if (linelist60[-1] > linelist120[-1]) and (gradient120_ave20 > 0) and (data60 > line60) and (krw_balance>10):
                krw_balance=upbit.get_balance("KRW")
                print(krw_balance)
                upbit.buy_market_order("KRW-HIVE",krw_balance*0.999) #바꿔야할 부분 1군데
                print("매수되었습니다.")

            coin_balance=upbit.get_balance("KRW-HIVE") #바꿔야할 부분 1군데
            if coin_balance is None:
                coin_balance=0

            if (data60 < line60) and (coin_balance>0.1): # coin balance 도 가격대에 맞춰서 변경해주기

                coin_balance = upbit.get_balance("KRW-HIVE")    #바꿔야할 부분 1군데
                upbit.sell_market_order("KRW-HIVE",coin_balance*0.999)   #바꿔야할부분 1군데
                print("매도되었습니다.")

    print(get_message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("close")

def on_open(ws):
    def run(*args):
        ws.send('[{"ticket":"test"},{"type":"trade","codes":["KRW-HIVE"]}]') #바꿔야할부분 1군데
        time.sleep(1)
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
