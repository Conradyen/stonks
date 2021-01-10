import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime

ALPACA_API_KEY = "PKIL2PW9CADBJ8NB4M6O"
ALPACA_SECRET_KEY = "O2iwwMKrpYwnaYPlEgtZ6Ia6rgoFU21nACmqBlT7"
ALPACA_PAPER = True


class SmaCross(bt.Strategy):
    def __init__(self):

        self.currentDate = None
        self.openPrice = -1
        self.afternoorPrice = -1
        self.buyAtOpen = False
        self.isOrder = False

    def next(self):
        # trading hour 13:30 to 19:30
        # print(self.datetime.time(ago=0).hour)
        # print(self.datetime.date(ago=0),self.datetime.time(ago=0).hour , self.datetime.time(ago=0).minute)
        # self.isOrder = False
        # print("cash available : ",self.broker.get_cash() )
        # print(f"position {self.position}")
        if self.buyAtOpen == True and self.broker.get_cash() >= 2000:
            size = int(2000 / self.data)
            self.buy(size = size)
            self.isOrder = True

        if self.currentDate != self.datetime.date(ago=0):
            self.currentDate = self.datetime.date(ago=0)
            self.openPrice = self.data.open.get(ago=0)[0]
            self.buyAtOpen = False
            self.isOrder = False

        if self.datetime.time(ago=0).hour == 18 and self.datetime.time(ago=0).minute == 30:
            self.afternoorPrice = self.data.open.get(ago=0)[0]

        if self.datetime.time(ago=0).hour >= 14 and self.datetime.time(ago=0).hour < 17 and self.isOrder != True:
            # print("morning")
            self._is_morning_up()
            self._is_morning_down()

        if self.isOrder != True and (self.datetime.time(ago=0).hour == 18 and self.datetime.time(ago=0).minute > 30) or self.datetime.time(ago=0).hour == 19:
            # print("afternoon")
            self._is_afternoon_up()
            self._is_afternoon_down()

    def log(self, txt):
        ''' Logging function for this strategy'''
        print(f"{self.datetime.date(ago=0)}-{self.datetime.time(ago=0).hour}:{self.datetime.time(ago=0).minute}")
        print(txt)
        print(f"price : {self.data.open.get(ago=0)[0]}")
        print(f"position {self.position.size}")

    def _is_morning_up(self):
        move = (self.data - self.openPrice) / self.openPrice
        if move > 0.02 and self.isOrder != True:
            self.isOrder = True
            size = int(2000 / self.data)
            self.log(f"morning move up : {move}, sell ")
            if self.position.size - size > 0:
                self.sell(size = size)

    def _is_morning_down(self):
        move = (self.data - self.openPrice) / self.openPrice
        if move < -0.015:
            if self.isOrder != True and self.broker.get_cash() >= 2000:
                self.isOrder = True
                size = int(2000 / self.data)
                self.log(f"morning move dowm : {move}, buy ")
                self.buy(size = size)


    def _is_afternoon_up(self):
        move = (self.data - self.afternoorPrice) / self.afternoorPrice

        if move > 0.02 and self.isOrder != True:
            self.isOrder = True
            size = int(2000 / self.data)
            self.log(f"afternoon move up : {move}, sell ")
            if self.position.size - size > 0:
                self.sell(size = size)

    def _is_afternoon_down(self):
        move = (self.data - self.afternoorPrice) / self.afternoorPrice
        if move < -0.015 and self.isOrder != True:
            self.log(f"afternoon move down : {move}, buy ")
            self.buyAtOpen = True


cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

store = alpaca_backtrader_api.AlpacaStore(
    key_id=ALPACA_API_KEY,
    secret_key=ALPACA_SECRET_KEY,
    paper=ALPACA_PAPER
)

if not ALPACA_PAPER:
  broker = store.getbroker()  # or just alpaca_backtrader_api.AlpacaBroker()
  cerebro.setbroker(broker)

DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
data0 = DataFactory(dataname='ARKK', historical=True, fromdate=datetime(
    2019, 1, 1), timeframe=bt.TimeFrame.TFrame("Minutes"))
cerebro.resampledata(data0,timeframe=bt.TimeFrame.Minutes,compression=15)
cerebro.broker.setcash(10000.0)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
print(f'Total gain : {cerebro.broker.getvalue()-10000.0} , {(cerebro.broker.getvalue()-10000.0)*100/10000}%')
