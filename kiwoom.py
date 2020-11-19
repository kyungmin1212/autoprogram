import sys
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
from pandas import DataFrame


class Kiwoom():
    def __init__(self):
        self.ocx=QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        ##### 이벤트 받으면 연결되는 메서드 #####
        self.ocx.OnEventConnect.connect(self._handler_login)
        self.ocx.OnReceiveTrData.connect(self._handler_tr)
        self.ocx.OnReceiveChejanData.connect(self._handler_chejan)
        self.ocx.OnReceiveMsg.connect(self._handler_msg)
        self.ocx.OnReceiveConditionVer.connect(self._handler_condition_load)
        self.ocx.OnReceiveTrCondition.connect(self._handler_tr_condition)
        self.ocx.OnReceiveRealData.connect(self._handler_real_data)
        ####################################

    ##### 실시간 타입을 위한 메소드 #####
    def SetRealReg(self,screen_no,code_list,fid_list,real_type):
        self.ocx.dynamicCall("SetRealReg(QString,QString,QString,QString)",screen_no,code_list,fid_list,real_type)

    def GetCommRealData(self,code,fid):
        data=self.ocx.dynamicCall("GetCommRealData(QString,int)",code,fid)
        return data

    def DisConnectRealData(self,screen_no):
        self.ocx.dynamicCall("DisConnectRealData(QString)",screen_no)

    ##### 로그인 정보 #####
    def GetLoginInfo(self,tag):
        data=self.ocx.dynamicCall("GetLoginInfo(QString)",tag)
        return data
    # ACCOUNT_CNT:계좌개수 , ACCNO:계좌번호 , USER_ID:사용자 ID , USER_NAME:사용자 이름

    ##### 로그인 함수 #####
    def CommConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        self.login_loop=QEventLoop()
        self.login_loop.exec()

    ##### 종목 코드 #####
    def GetCodeListByMarket(self,market):
        data =self.ocx.dynamicCall("GetCodeListByMarket(QString)",market)
        codes=data.split(";")
        return codes[:-1]
    # 0:장내(코스피) , 3:ELW , 4:뮤추얼펀드 , 5:신주인수권 , 6:리츠 , 8:ETF , 9:하이일드펀드 , 10:코스닥 , 30:K-OTC , 50:코넥스

    ##### 종목명 #####
    def GetMasterCodeName(self,code):
        data=self.ocx.dynamicCall("GetMasterCodeName(QString)",code)
        return data
    # 종목코드 입력하면 종목명 반환

    ##### 상장 주식수 #####
    def GetMasterListedStockCnt(self,code):
        data=self.ocx.dynamicCall("GetMasterListedStockCnt(QString)",code)
        return data
    # 종목코드 입력하면 그 종목의 상장 주식수 반환

    ##### 상장일 #####
    def GetMasterListedStockDate(self,code):
        data =self.ocx.dynamicCall("GetMasterListedStockDate(QString)",code)
        return data
    # 종목코드 입력하면 그 종목의 상장일 반환

    ##### 전일가 #####
    def GetMasterLastPrice(self,code):
        data=self.ocx.dynamicCall("GetMasterLastPrice(QString)",code)
        return int(data)
    # 종목코드 입력하면 그 종목의 전일가 반환

    ##### 감리구분 #####
    def GetMasterConstruction(self,code):
        data=self.ocx.dynamicCall("GetMasterConstruction(QString)",code)
        return data
    # 감리구분 - 정상, 투자주의 , 투자경고 , 투자위험, 투자주의환기종목 (종목코드를 입력하면 감리구분 반환)

    ##### 종목상태 #####
    def GetMasterStockState(self,code):
        data =self.ocx.dynamicCall("GetMasterStockState(QString)",code)
        return data
    # 종목상태 - 정상,증거금100%,거래정지,관리종목,감리종목,투자유의종목,담보대출,액면분할,신용가능(종목코드 입력하면 종목상태 반환)

    ##### 테마코드와 테마명 #####
    def GetThemeGroupList(self,type):
        data=self.ocx.dynamicCall("GetThemeGroupList(int)",type)
        tokens=data.split(';')

        data_dic={}
        for theme in tokens:
            code,name=theme.split('|')
            if type==0:
                data_dic[code]=name
            else:
                data_dic[name]=code
        return data_dic
    # type 에 0을 입력하면 테마코드 테마명 순으로 출력되고 1을 입력하면 테마명 테마코드 순으로 출력된다.

    ##### 테마코드에 소속된 종목코드 #####
    def GetThemeGroupCode(self,theme_code):
        data=self.ocx.dynamicCall("GetThemeGroupCode(QString)",theme_code)
        tokens=data.split(';')

        result=[]
        for code in tokens:
            result.append(code[1:])

        return result
    # 테마코드를 입력하면 그안에 속해있는 종목코드를 리스트 형태로 반환한다.

    ##### 멀티 데이터의 행의 개수 파악 #####
    def GetRepeatCnt(self,trcode,rqname):
        ret=self.ocx.dynamicCall("GetRepeatCnt(QString,QString)",trcode,rqname)
        return ret

    ##### TR 데이터 셋팅 #####
    def SetInputValue(self,id,value):
        self.ocx.dynamicCall("SetInputValue(QString,QString)",id,value)
    # ex) id 에 종목코드 value에 003490 입력하면 그값이 세팅된다. id에 계좌번호 value에 83590020 이런식으로 입력하면 계좌번호가 세팅된다.

    ##### 데이터 넘겨주기 #####
    def CommRqData(self,rqname,trcode,next,screen):
        self.ocx.dynamicCall("CommRqData(QString,QString,int,QString)",rqname,trcode,next,screen)
        self.tr_loop=QEventLoop()
        self.tr_loop.exec()
    # rqname 요청이름(내맘대로 설정) , trcode:"opt10001" 이런식으로 tr코드 문자열로 작성 , next:처음 600개 조회할땐 0 그다음데이터부턴 2 입력, screen:"0000"을 제외한 아무값을 적으면 된다.

    ##### 데이터 가져오기 #####
    def GetCommData(self,trcode,rqname,index,item):
        data=self.ocx.dynamicCall("GetCommData(QString,QString,int,QString)",trcode,rqname,index,item)
        return data.split()
    # index 은 열을 의미한다. 싱글 데이터면 무조건 0 이다. 멀티데이터면 원하는 row 의 값을 입력한다. item 자리에는 TR데이터의 OUTPUT 중에 원하는 데이터 값을 문자열로 입력한다.
    # CommRqData 를 통해 데이터를 넘겨주고 기다리면 이벤트가 발생하는데 그때 _handler_tr 함수로 넘어가게 되고 거기서 이 데이터 가져오는 함수가 사용된다.

    ##### 주문하기 #####
    def SendOrder(self,rqname,screen,accno,order_type,code,quantity,price,hoga,order_no):
        self.ocx.dynamicCall("SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",[rqname,screen,accno,order_type,code,quantity,price,hoga,order_no])

    ##### 조건식 저장 메서드 #####
    def GetConditionLoad(self):
        self.ocx.dynamicCall("GetConditionLoad()")
        # 사용자 조건식 저장 이벤트까지 대기
        self.condition_load_loop=QEventLoop()
        self.condition_load_loop.exec()

    ##### 조건명 리스트 불러오기 #####
    def GetConditionNameList(self):
        data=self.ocx.dynamicCall("GetConditionNameList()")
        conditions=data.split(";")[:-1]

        ret=[]
        for condition in conditions:
            index,name=condition.split('^')
            ret.append((index,name))
        return ret

    ##### 조건검색 종목조회 #####
    def SendCondition(self,screen,cond_name,cond_index,search):
        ret=self.ocx.dynamicCall("SendCondition(QString,QString,int,int)",screen,cond_name,cond_index,search)

        # event loop
        self.condition_tr_loop=QEventLoop()
        self.condition_tr_loop.exec()

###########################이벤트 받으면 연결되는 함수 ##############################

    # 실시간 데이터 구독 신청
    ##### 로그인 이벤트 루프 종료 #####
    def _handler_login(self,err):
        self.login_loop.exit()
        if err==0:
            print("로그인완료")
        self.subscribe_market_time()

    def subscribe_market_time(self):
        self.SetRealReg("1000","","215",0)
        # 1000은 아무 스크린 번호 두번째 자리는 종목코드 자리인데 상관없으므로 비워두고 세번째 자리는 FID 숫자 자리인데 받아오는것중에 하나만 입력해줘도 된다. 네번째는 최초등록이면 0
        print("장시작시간 구독완료")

    def subscribe_stock_conclusion(self,screen_no,code):
        self.SetRealReg(screen_no,code,"20",0)
        print("주식체결 구독신청")
        #code 를 쓸땐 "005930;035420" 처럼 ; 로 구분해주기.

    ##### 실시간 데이터 받아오는 함수 #####
    def _handler_real_data(self,code,real_type,real_data):
        if real_type=="장시작시간":
            market_op_type=self.GetCommRealData(code,215)
            sign_time=self.GetCommRealData(code,20)
            remained_time=self.GetCommRealData(code,214)
            print(market_op_type,sign_time,remained_time)
            if market_op_type=="3":
                if self.previous_day_hold:
                    self.previous_day_hold=False
                    self.SendOrder("매도","8001",self.account,2,"229200",self.previous_day_hold_quantity,0,"03","")
        elif real_type == "주식체결":
            체결시간=self.GetCommRealData(code,20)
            현재가=self.GetCommRealData(code,10)
            현재가=abs(int(현재가))
            시가=self.GetCommRealData(code,16)
            시가=abs(int(시가))
            self.target=int(시가+(self.range)*0.5)

            if self.hold is None and 현재가>self.target:
                self.hold=True
                self.SendOrder("매수","8000",self.account,1,"229200",10,0,"03","")

            print(code,체결시간,현재가)


    def _handler_chejan(self,gubun,item_cnt,fid_list):
        print("OnReceiveChejanData",gubun,item_cnt,fid_list)

    def _handler_msg(self,screen,rqname,trcode,msg):
        print("OnReceiveMsg:",screen,rqname,trcode,msg)

    def _handler_condition_load(self,ret,msg):
        print("OnReceiveConditionVer: ",ret,msg)
        self.condition_load_loop.exit()

    def _handler_tr_condition(self,screen,codelist,cond_name,cond_index,next):
        codes=codelist.split(';')
        self.condition_codes=codes[:-1]

        self.condition_tr_loop.exit()



    ##### TR 데이터 가져오고 이벤트루프 종료 #####
    def _handler_tr(self,screen,rqname,trcode,record,next):
        #OnReceiveTrData가 데이터를 보내줄때 데이터가 600개보내고 더 남아있으면 next를 2로 보내준다. 보내다가 데이터가 더이상없는경우 next를 0으로 보내준다.
        if next=='2':
            self.remained=True
        else:
            self.remained=False

        if rqname=="opt10081":
            self._opt10081(rqname,trcode)
        elif rqname=="opt10001":
            self._opt10001(rqname,trcode)
        elif rqname=="opw00001":
            self._opw00001(rqname,trcode)


        try:
            self.tr_loop.exit()
        except:
            pass



########################################################################

##################### TR요청 관련 데이터 ##################################
    ##### _handler_tr 안에 들어갈 trcode 에 따라 얻어오는 데이터 함수 #####
    # 일봉데이터 요청(opt10081)
    def _opt10081(self,rqname,trcode):
        data=[]
        columns=["일자","시가","고가","저가","현재가","거래량"]

        rows=self.GetRepeatCnt(trcode,rqname)
        for i in range(rows):
            date = self.GetCommData(trcode,rqname,i,"일자")
            open = self.GetCommData(trcode, rqname, i, "시가")
            high = self.GetCommData(trcode, rqname, i, "고가")
            low = self.GetCommData(trcode, rqname, i, "저가")
            close = self.GetCommData(trcode, rqname, i, "현재가")
            volume = self.GetCommData(trcode, rqname, i, "거래량")

            dt=datetime.datetime.strptime(date[0],"%Y%m%d")


            data.append([dt,open[0],high[0],low[0],close[0],volume[0]])
            self.tr_data=DataFrame(data=data,columns=columns)
            return self.tr_data
    # opt10081 처럼 멀티데이터로 반환되는경우는 GetRepeatCnt 함수를 사용하여 for문으로 데이터를 출력한다.




    # 주식 기본정보 요청 (opt10001)
    def _opt10001(self, rqname, trcode):
        self.tr_data = {}
        per = self.GetCommData(trcode, rqname, 0, "PER")
        pbr = self.GetCommData(trcode, rqname, 0, "PBR")
        eps = self.GetCommData(trcode, rqname, 0, "EPS")
        roe = self.GetCommData(trcode, rqname, 0, "ROE")
        ev = self.GetCommData(trcode, rqname, 0, "EV")
        bps = self.GetCommData(trcode, rqname, 0, "BPS")
        try:
            per = float(per[0])
        except:
            per = 0
        try:
            pbr = float(pbr[0])
        except:
            pbr = 0
        try:
            eps = float(eps[0])
        except:
            eps = 0
        try:
            roe = float(roe[0])
        except:
            roe = 0
        try:
            ev = float(ev[0])
        except:
            ev = 0
        try:
            bps = float(bps[0])
        except:
            bps = 0
        self.tr_data['PER'] = per
        self.tr_data['PBR'] = pbr
        self.tr_data['EPS'] = eps
        self.tr_data['ROE'] = roe
        self.tr_data['EV'] = ev
        self.tr_data['BPS'] = bps
        return self.tr_data

    # 예수금 상세 현황 요청 (opw00001)
    def _opw00001(self, rqname, trcode):
        ysg = self.GetCommData(trcode, rqname, 0, "예수금")
        self.예수금=int(ysg[0])

#######################################################################

app=QApplication(sys.argv)