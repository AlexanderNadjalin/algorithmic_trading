# About
algorithmic_trading is meant to be an event-driven backtester for different trading strategies. It is currently designed for equity style transactions (equities, funds, ETF:s, certificates etc.) in the same currency.

The main use cases is to design, test and evaluate trading strategies in an even-driven environment. The strategies can be simple and based metrics, ranging to more complex strategies based on Machine Learning approaches for example. The strategies are evaluated using standard metrics for performance and risk, as well as plotted outputs.

It is Python-based and designed as a project for me to dive deper into progamming, quantitative finance topics and data wrangling. This project is not complete.

"Past performance is no guarantee of future results". Do no, under any circumstances, try to use this software for real world trading activities.

# Usage and examples
Here is a simple example to show how the module can be used. More details on the specific sub-modules are provided in the Structure section.

### Market data
First we need market data. This is expected to be a .csv file containing all the en-of-day date for the identifiers in our investment universe, including any benchmarks. Market data details are specified in the market_config.ini file.

```
market = Market(market_file_name=market_file_name,
                fill_missing_method='forward')
```

### Portfolio

Next we create the portfolio which will hold all trade details and history. The portfolio object reads the portofolio_config.ini file containing static information about it:

```
[commission]
commission_scheme = ''

[init_cash]
init_cash = 100000.0

[benchmark]
benchmark_name = .OMXS30

[portfolio_information]
currency = SEK
pf_id = pf01
```

Commission schemes are supported for the avaza.se broker but can be expanded to include any others.

Creating the portfolio object:

```
pf = Portfolio(inception_date='2017-07-27')
```

### Strategy

We need to define a strategy containing rules for buying and selling. In this case, we'll use a monthly re-balancing scheme at the start of the month. At each first busines day of the month, the strategy will re-balance its holdings to contain the following securities with the respective weights:

* XACTOMXS30.ST at 89%
* SXRT.TG       at 10%
* cash          at 1%

This weighting scheme is just an example.

```
s = PeriodicRebalancing(period='som',
                        id_weight={'XACTOMXS30.ST': 0.89,
                        'SXRT.TG': 0.1})
```

### The backtest

Next we set up the backtest, add our strategy and run the whole thing.

```
bt = Backtest(market=market,
              pf=pf,
              start_date=pf.inception_date,
              end_date='2021-07-02')

# Add strategy to backtest and run.
bt.add_strategy(strategy=s)
bt.run()
```

### Calculated metrics

In the metric_config.ini file, we define the parameters used for all our calculations regarding risk and performace:

```
[rolling_beta]
period = 252

[rolling_sharpe_ratio]
period = 252

[sharpe_ratio]
period = 252

[sortino_ratio]
period = 252
```

The last command, `bt.run()`, runs the backtest between the desired dates, excuting the strategy as per its definition. The core of the function is a Python queque which handles events of different types such as "MARKET", "TRANSACTION" etc. Each day counts as a new event where the strategy evaluates market data and positions. If the strategy decides that a transaction should be made, it adds a "TRANSACTION" event to the queue.

The function lastly calculates all performance and risk measurements.

### Results

We can now see the reults in the form of a few plots and some metrics.

First we se the strategy's cummulative performance and its drawdown statistics.

<img width="700" src="/output_files/pf01_drawdowns.png" />

***

Return heatmaps for different periods:

<img width="700" src="/output_files/pf01_return_heatmaps.png" />

***

Rolling Sharpe ratio and beta:

<img width="700" src="/output_files/pf01_rolling_sharpe_beta.png" />

***

A simple tear sheet with various metrics added in one place:

<img width="700" src="/output_files/pf01_tear_sheet.png" />

***
The code for producing these four plots are straight forward:

```
p = Plot(bt=bt)
p.drawdowns_plot(save=True)
p.periodic_returns(save=True)
p.rolling_sharpe_beta_plot(save=True)
p.plot_text(save=True)
```

# Further improvements
Several areas of improvement exists, some of which are listed below.

* Add functionality for more data sources such as Yahoo Finance etc.
* Add more standard type strategies.
* Support for multi-currency portfolios.
* Support for intraday markets data and transactions.
* Added risk metrics such as Value-at-Risk (VaR), Expected Shortfall (ES) etc.

Other itmes:

* Complete documentation and examples.


# License
Copyright (c) 2021, Nadjalin Enterprises AB

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
