# region imports
from AlgorithmImports import *
# endregion

class CryptoBot(QCAlgorithm):

    def Initialize(self):
        
        self.SetStartDate(2018, 12, 12)  # Aqui selecciona la fecha de inicio del backtest
        self.SetEndDate(2022,10,17)      # Aqui selecciona la fecha de finalizacion del backtest
        
        self.SetCash(100000)  # Set Strategy Cash
        
        #self.SetBrokerageModel(BrokerageName.Binance, AccountType.Margin)
        #self.DefaultOrderProperties = BinanceOrderProperties()
        #self.DefaultOrderProperties.TimeInForce = TimeInForce.GoodTilCanceled
        #self.DefaultOrderProperties.PostOnly = False

        self.btc = self.AddCrypto("BTCUSD",Resolution.Daily).Symbol
        self.eth = self.AddCrypto("ETHUSD",Resolution.Daily).Symbol


        self.btcBB = self.BB(self.btc, 20, 2)
        self.btcSMA13 = self.SMA(self.btc,13)
        self.btcSMA48 = self.SMA(self.btc,48)

        self.ethBB = self.BB(self.eth, 20, 2)
        self.ethSMA13 = self.SMA(self.eth,13)
        self.ethSMA48 = self.SMA(self.eth,48)

        self.btcPosition = "None"
        self.ethPosition = "None"

        self.btcStopOrder = None
        self.ethStopOrder = None

    def OnData(self, data: Slice):
        #Para BTC
        if not self.Portfolio[self.btc].Invested:
            #Si las bandas de bollinguer estan separadas
            if not self.btcBB.LowerBand.Current.Value * 0.25 > self.btcBB.UpperBand.Current.Value:
                if self.btcSMA13.Current.Value > self.btcSMA48.Current.Value:
                    self.btcPosition = "Long"
                    self.SetHoldings(self.btc,0.7)              
                if self.btcSMA13.Current.Value < self.btcSMA48.Current.Value:
                    self.btcPosition = "Short"
                    self.SetHoldings(self.btc,-0.7)
        else:
            if self.btcPosition == "Long" and self.btcSMA13.Current.Value < self.btcSMA48.Current.Value:
                self.Liquidate()
                self.btcStopOrder.Cancel()
            
            if self.btcPosition == "Short" and self.btcSMA13.Current.Value > self.btcSMA48.Current.Value:
                self.Liquidate()
                self.btcStopOrder.Cancel()
        
        #Para ETH
        if not self.Portfolio[self.eth].Invested:
            #Si las bandas de bollinguer estan separadas
            if not self.ethBB.LowerBand.Current.Value * 0.25 > self.ethBB.UpperBand.Current.Value:
                if self.ethSMA13.Current.Value > self.ethSMA48.Current.Value:
                    self.ethPosition = "Long"
                    self.SetHoldings(self.eth,0.3)
                if self.ethSMA13.Current.Value < self.ethSMA48.Current.Value:
                    self.ethPosition = "Short"
                    self.SetHoldings(self.eth,-0.3)       
        else:
            if self.ethPosition == "Long" and self.ethSMA13.Current.Value < self.ethSMA48.Current.Value:
                self.Liquidate()
                self.ethStopOrder.Cancel()

            if self.ethPosition == "Short" and self.ethSMA13.Current.Value > self.ethSMA48.Current.Value:
                self.Liquidate()
                self.ethStopOrder.Cancel()
    

    def OnOrderEvent(self, orderEvent: OrderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        if orderEvent.Status != OrderStatus.Filled:
            return
        
        symbol = orderEvent.Symbol
        quantity = orderEvent.Quantity
        fillprice = orderEvent.FillPrice

        if orderEvent.Symbol == self.btc:
            if self.btcPosition == "Long" and quantity < 0:
                return

            if self.btcPosition == "Short" and quantity > 0:
                return
            
            if quantity > 0:
                self.btcStopOrder = self.StopMarketOrder(self.btc, -quantity, fillprice*0.92)
            else:
                self.btcStopOrder = self.LimitOrder(self.btc, quantity, fillprice*0.108)
        
        if orderEvent.Symbol == self.eth:
            if self.ethPosition == "Long" and quantity < 0:
                return

            if self.ethPosition == "Short" and quantity > 0:
                return
            
            if quantity > 0:
                self.ethStopOrder = self.StopMarketOrder(self.eth, -quantity, fillprice*0.92)
            else:
                self.ethStopOrder = self.LimitOrder(self.eth, quantity, fillprice*0.108)
                