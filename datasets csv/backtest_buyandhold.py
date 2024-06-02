from pyalgotrade import strategy
from pyalgotrade.barfeed import csvfeed

class BuyAndHoldStrategy(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument):
        super(BuyAndHoldStrategy, self).__init__(feed)
        self.instrument = instrument
        self.setUseAdjustedValues(False)
        self.position = None

    def onEnterOk(self, position):
        self.info(f"{position.getEntryOrder().getExecutionInfo()}")

    def onBars(self, bars):
        bar = bars[self.instrument]

        if self.position is None:
            close = bar.getClose()
            broker = self.getBroker()
            cash = broker.getCash()
            quantity = cash / close

            self.position = self.enterLong(self.instrument, quantity)

feed = csvfeed.GenericBarFeed(86400)
feed.setDateTimeFormat('%d/%m/%Y')
feed.addBarsFromCSV("servicom", "servicom.csv")

strategy = BuyAndHoldStrategy(feed, "servicom")
print(strategy.getBroker().getCash())
strategy.run()
print(strategy.getBroker().getCash())
portfolio_value = strategy.getBroker().getEquity() + strategy.getBroker().getCash()
print(portfolio_value)