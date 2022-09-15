from AlgorithmImports import *

class PowerEarningsGap(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 7, 20)
        self.SetEndDate(2022, 9, 15)
        self.SetCash(10000)

        # add SPY so that we can use it in the schedule rule below
        self.SPY = self.AddEquity('SPY', Resolution.Minute).Symbol

        # build a universe using the CoarseFilter and FineFilter functions defined below
        self.AddUniverse(self.CoarseFilter, self.FineFilter)

        self.SPY = self.AddEquity("SPY").Symbol
        self.Schedule.On(self.DateRules.EveryDay("SPY"), self.TimeRules.AfterMarketOpen("SPY", 1), self.AfterMarketOpen)


    def CoarseFilter(self, universe):
        # filter universe, ensure DollarVolume is above a certain threshold
        # also filter by assets that have fundamental data
        universe = [asset for asset in universe if asset.DollarVolume > 1000000 and asset.Price > 10 and asset.HasFundamentalData]
        
        # sort universe by highest dollar volume
        sortedByDollarVolume = sorted(universe, key=lambda asset: asset.DollarVolume, reverse=True)
        
        # only select the first 500
        topSortedByDollarVolume = sortedByDollarVolume[:500]

        # we must return a list of the symbol objects only
        symbolObjects = [asset.Symbol for asset in topSortedByDollarVolume]

        # this line is not necessary, but we will use it for debugging to see a list of ticker symbols
        tickerSymbolValuesOnly = [symbol.Value for symbol in symbolObjects]

        return symbolObjects

    def FineFilter(self, coarseUniverse):
        yesterday = self.Time - timedelta(days=1)
        fineUniverse = [asset.Symbol for asset in coarseUniverse if asset.EarningReports.FileDate == yesterday and asset.MarketCap > 1e9]

        tickerSymbolValuesOnly = [symbol.Value for symbol in fineUniverse]

        return fineUniverse


    def AfterMarketOpen(self):
        for security in self.ActiveSecurities.Values:
            symbol = security.Symbol

            if symbol == self.SPY:
                continue

            historyData = self.History(symbol, 2, Resolution.Daily)

            try:
                openDayAfterEarnings = historyData['open'][-1]
                closeDayAfterEarnings = historyData['close'][-1]
                highDayAfterEarnings = historyData['high'][-1]
                closeDayBeforeEarnings = historyData['close'][-2]

            except:
                self.Debug(f"History data unavailable for {symbol.Value}")
                continue
