from finflux.base_var import Config

import yfinance as yf # type: ignore
import numpy as np # type: ignore
import requests # type: ignore
import pandas as pd # type: ignore
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BDay
from matplotlib.ticker import FuncFormatter

#------------------------------------------------------------------------------------------
class InvalidParameterError(Exception):
    def __init__(self, msg):
        self.msg = msg

class InvalidSecurityError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class MissingConfigObject(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class ChartReadabilityError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

#------------------------------------------------------------------------------------------
class equity:
    security_type = 'EQUITY'

    def __init__(self,ticker):
        self.ticker = ticker
        self.mticker = ticker.split('.')[0]

        instrumentType = yf.Ticker(self.ticker).get_history_metadata()['instrumentType']
        if instrumentType != equity.security_type:
            raise InvalidSecurityError(f"Invalid security type. "
                                    f"Please select a valid '{equity.security_type}' symbol")
#------------------------------------------------------------------------------------------
    def timeseries(self, display: str = 'table', period: str = '5y', start: str = None, end: str = None, interval: str = '1d', data: str = 'all', calculation: str = 'price', round: bool = True):
        valid_params = {'valid_display' : ['table', 'json'],
                        'valid_period' : ['1mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
                        'valid_interval' : ['1d', '1wk', '1mo', '3mo'],
                        'valid_data' : ['open', 'high', 'low', 'close', 'volume', 'all'],
                        'valid_calculation' : ['price', 'simple return', 'log return'],
                        'valid_round' : [True, False]}
        
        params = {'display': display,
                  'period': period,
                  'interval': interval,
                  'data': data,
                  'calculation': calculation,
                  'round': round}
        
        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        #Note: start and end parameters will override any period parameter presence
        if start == None and end == None:
            yf_download = yf.download(self.ticker, period=period, interval=interval, ignore_tz=True, rounding=round, group_by='column', progress=False, auto_adjust=True)
        elif start != None and end != None:
            yf_download = yf.download(self.ticker, start=start, end=end, interval=interval, ignore_tz=True, rounding=round, group_by='column', progress=False, auto_adjust=True)
        #----------------------------------------------------------------------------------

        #STANDARDIZING TABLE---------------------------------------------------------------
        yf_download.columns = yf_download.columns.droplevel([1])
        yf_download.columns.name = None
        yf_download.columns = [f'{self.ticker} Close', f'{self.ticker} High', f'{self.ticker} Low', f'{self.ticker} Open', f'{self.ticker} Volume']

        #PARAMETER - DATA =================================================================
        if data == 'all':
            yf_download = yf_download
        else:
            yf_download = yf_download[f'{self.ticker} {data.capitalize()}']

        #PARAMETER - CALCULATION ==========================================================
        if calculation == 'price':
            yf_download = yf_download
        elif calculation == 'simple return':
            yf_download = (yf_download / yf_download.shift(1))-1
            yf_download = yf_download.drop(yf_download.index[0])
            if round == True:
                yf_download = yf_download.round(2)
        elif calculation == 'log return':
            yf_download = np.log(yf_download / yf_download.shift(1))
            yf_download = yf_download.drop(yf_download.index[0])
            if round == True:
                yf_download = yf_download.round(2)

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = yf_download
        elif display == 'json':
            yf_download.index = yf_download.index.strftime('%Y-%m-%d')
            
            yf_download_list = []
            if data == 'all':
                for index, row in yf_download.iterrows():
                    a = {
                        'Date': index,
                        f'{self.ticker} Open': float(row[f'{self.ticker} Open']),
                        f'{self.ticker} High': float(row[f'{self.ticker} Open']),
                        f'{self.ticker} Low': float(row[f'{self.ticker} Open']),
                        f'{self.ticker} Close': float(row[f'{self.ticker} Open']),
                        f'{self.ticker} Volume': float(row[f'{self.ticker} Open'])
                    }
                    yf_download_list.append(a)
            elif data != 'all':
                for index, row in yf_download.iterrows():
                    a = {
                        'Date': index,
                        f'{self.ticker} {data.title()}': row[f'{self.ticker} {data.title()}']
                    }
                    yf_download_list.append(a)
            
            output = yf_download_list

        return output
#------------------------------------------------------------------------------------------
    def candle_chart(self, period: str = '6mo', start: str = None, end: str = None, interval: str = '1d', sma: list = None, volume: bool = True, bollinger: list = None, o_label: bool = True, h_label: bool = True, l_label: bool = True, c_label: bool = True, legend: bool = False, title: bool = True, show: str = True, save: str = False):
        valid_params = {'valid_period' : ['1mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
                        'valid_interval' : ['1d', '1wk', '1mo'],
                        'valid_volume' : [True, False],
                        'valid_o_label' : [True, False],
                        'valid_h_label' : [True, False],
                        'valid_l_label' : [True, False],
                        'valid_c_label' : [True, False],
                        'valid_legend': [True, False],
                        'valid_title': [True, False],
                        'valid_show' : [True, False],
                        'valid_save' : [True, False]}
        
        params = {'period': period,
                  'interval': interval,
                  'volume': volume,
                  'o_label': o_label,
                  'h_label': h_label,
                  'l_label': l_label,
                  'c_label': c_label,
                  'legend': legend,
                  'title': title,
                  'show': show,
                  'save': save}
        
        #SMA will be int or list from 10-300 inclusive
        #bollinger will be 0.1-3.0 SDs floats inclusive with 0.05 increments; only works when sma is an int
        
        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        data = self.timeseries(period=period, data='all', calculation='price', round=True, interval=interval, start=start, end=end)
        data['DateNum'] = [x for x in range(0,len(data))]
        #----------------------------------------------------------------------------------

        #SETTING LIMITS ON NUMBER OF DATA DF ROWS POSSIBLE---------------------------------(this is to prevent overly cramped candlestick formatting)
        if len(data) > 265:
            raise ChartReadabilityError(f"Number of OHLC candles are capped at 265 to ensure plot readability. The current selection contains {len(data)} data points. Please reduce the time period or choose a larger interval.")
            #1d interval and 1y period is ~262 datapoints
            #1wk interval and 5y period is ~250 datapoints
            #1mo interval and 10y period is well below the cap

        #SETTING LIMITS ON SMA AND BOLLINGER BAND SD---------------------------------------
        #SMA 10-300 inclusive ints
        if isinstance(sma, list):
            if len(sma) > 5:
                raise ChartReadabilityError(f"Number of SMA lines are capped at 5 to ensure plot readability. The current selection contains {len(sma)} SMA lines. Please reduce the number of SMA lines.")
            for sma_i in sma:
                if sma_i > 300 or sma_i < 10:
                    raise InvalidParameterError(f"Invalid sma parameter '{sma_i}'. "
                                            f"Please choose an integer between 10 and 300 (inclusive)")

        #BB 0.1-3.0 inclusive floats
        if isinstance(bollinger, list):
            if len(sma) != len(bollinger):
                raise InvalidParameterError(f"Number of bollinger band standard deviation does not match the number of SMA lines. The current selection contains {len(sma)} SMA lines. Please match the number of bollinger band standard deviations to {len(sma)}.")
            for bollinger_i in bollinger:
                if bollinger_i != None:
                    if bollinger_i > 3 or bollinger_i < 0.1:
                        raise InvalidParameterError(f"Invalid bollinger parameter '{bollinger_i}'. "
                                                    f"Please choose an integer or float between 0.1 and 3 (inclusive)")

        #SETTING UP DATA DATAFRAME WITH OPTIONAL SMA AND BOLLINGER BAND COLUMN(S)----------
        if sma is not None:
            max_c_data = self.timeseries(period='max', data='all', calculation='price', round=True, interval=interval)
            #creating sma columns in data dataframe based on bollinger condition
            if bollinger == None:
                for i in sma:
                    max_c_data[f'SMA {i}'] = max_c_data[f'{self.ticker} Close'].rolling(window=i).mean()
                    data[f'SMA {i}'] = max_c_data[f'SMA {i}'].tail(len(data))
            elif isinstance(bollinger, list):
                for i, b in zip(sma, bollinger):
                    if b != None:
                        max_c_data[f'SMA {i}'] = max_c_data[f'{self.ticker} Close'].rolling(window=i).mean()
                        data[f'SMA {i}'] = max_c_data[f'SMA {i}'].tail(len(data))
                        max_c_data[f'SD {i}'] = max_c_data[f'{self.ticker} Close'].rolling(window=i).std()
                        data[f'bollinger_upper {i}'] = data[f'SMA {i}'] + (b * max_c_data[f'SD {i}'].tail(len(data)))
                        data[f'bollinger_lower {i}'] = data[f'SMA {i}'] - (b * max_c_data[f'SD {i}'].tail(len(data)))
                    elif b == None:
                        max_c_data[f'SMA {i}'] = max_c_data[f'{self.ticker} Close'].rolling(window=i).mean()
                        data[f'SMA {i}'] = max_c_data[f'SMA {i}'].tail(len(data))

        #CREATING THE MAIN FIG AX PAIR WITH AN OPTIONAL VOLUME AX--------------------------
        if volume == True:
            fig, (ax_p, ax_v) = plt.subplots(nrows=2, ncols=1, gridspec_kw={'height_ratios': [3,1]}, figsize=(10, 6), dpi=300)
            plt.subplots_adjust(hspace=0)
        elif volume == False:
            fig, ax_p = plt.subplots(figsize=(10, 4.5), dpi=300)

        #PLOTTING THE MAIN OHLC CANDLESTICKS-----------------------------------------------
        if len(data) > 200:
            candle_width = 0.3
        elif len(data) > 150:
            candle_width = 0.4
        elif len(data) > 100:
            candle_width = 0.5
        elif len(data) > 50:
            candle_width = 0.6
        else:
            candle_width = 0.7
        
        for index, row in data.iterrows():
            color = 'green' if row[f'{self.ticker} Close'] >= row[f'{self.ticker} Open'] else 'red'
            #wick
            ax_p.vlines(row['DateNum'], row[f'{self.ticker} Low'], row[f'{self.ticker} High'], color=color, linewidth=0.25)
            #box
            ax_p.add_patch(plt.Rectangle(
                (row['DateNum'] - (candle_width/2), min(row[f'{self.ticker} Open'], row[f'{self.ticker} Close'])), # bottom left corner of the rectangle
                candle_width, # horizontal width of the rectangle
                abs(row[f'{self.ticker} Close'] - row[f'{self.ticker} Open']), #vertical height of the rectangle
                color=color #fill color of the rectangle
            ))
        
        #PLOTTING THE OPTIONAL VOLUME BARS IN SEPERATE AXES BELOW THE OHLC CHART-----------
        if volume == True:
            for index, row in data.iterrows():
                color = 'green' if row[f'{self.ticker} Close'] >= row[f'{self.ticker} Open'] else 'red'
                ax_v.bar(row['DateNum'],
                        row[f'{self.ticker} Volume'],
                        color = 'green' if row[f'{self.ticker} Close'] >= row[f'{self.ticker} Open'] else 'red',
                        width = 0.8,
                        alpha = 0.3)
                
        #REPLACING VOLUME CHART YAXIS LABELS WITH USER FRIENDLY OPTIONS--------------------
        if volume == True:
            def human_format(x, pos):
                if x >= 1_000_000_000:
                    return f'{int(x*1e-9)}B'
                elif x >= 1_000_000:
                    return f'{int(x*1e-6)}M'
                elif x >= 1_000:
                    return f'{int(x*1e-3)}K'
                else:
                    return f'{x:.0f}'

            # Apply to volume axis
            ax_v.yaxis.set_major_formatter(FuncFormatter(human_format))

        #PLOTTING OPTIONAL SMA AND BOLLINGER BAND LINES------------------------------------
        if isinstance(sma, list):
            sma_colors = ["#1f77b4", "#ff7f0e", "#9467bd", "#8c564b", "#17becf"]
            if bollinger == None:
                for sma_number, sma_color in zip(sma, sma_colors):
                    ax_p.plot(data['DateNum'], data[f'SMA {sma_number}'], color = sma_color, linewidth = 0.6, label = f'SMA {sma_number}')
            elif isinstance(bollinger, list):
                for sma_number, sma_color, bollinger_number in zip(sma, sma_colors, bollinger):
                    if bollinger_number != None:
                        ax_p.plot(data['DateNum'], data[f'SMA {sma_number}'], color = sma_color, linewidth = 0.6, linestyle = '--', label = f'SMA {sma_number}')
                        ax_p.plot(data['DateNum'], data[f'bollinger_upper {sma_number}'], color = sma_color, linewidth = 0.4, linestyle = '-', label = f'BB ({sma_number}, {bollinger_number})')
                        ax_p.plot(data['DateNum'], data[f'bollinger_lower {sma_number}'], color = sma_color, linewidth = 0.4, linestyle = '-')
                        ax_p.fill_between(data['DateNum'], data[f'bollinger_lower {sma_number}'], data[f'bollinger_upper {sma_number}'], color = sma_color, alpha = 0.1)
                    elif bollinger_number == None:
                        ax_p.plot(data['DateNum'], data[f'SMA {sma_number}'], color = sma_color, linewidth = 0.6, label = f'SMA {sma_number}')

        #PLOTTING OPTIONAL OHLC LABELS-----------------------------------------------------
        label_bools = [o_label, h_label, l_label, c_label]

        ax_p_length = ax_p.get_xlim()[1] - ax_p.get_xlim()[0]

        label_vd_list = []

        if o_label:
            o_value, o_datenum = float(data[f'{self.ticker} Open'].iloc[0]), (0-ax_p.get_xlim()[0])/ax_p_length
        else:
            o_value, o_datenum = None, None

        if h_label:
            h_value, h_datenum = data[f'{self.ticker} High'].max(), (int(data.loc[data[f'{self.ticker} High'].idxmax(), "DateNum"])-ax_p.get_xlim()[0])/ax_p_length
        else:
            h_value, h_datenum = None, None

        if l_label:
            l_value, l_datenum = data[f'{self.ticker} Low'].min(), (int(data.loc[data[f'{self.ticker} Low'].idxmin(), "DateNum"])-ax_p.get_xlim()[0])/ax_p_length
        else:
            l_value, l_datenum = None, None

        if c_label:
            c_value, c_datenum = float(data[f'{self.ticker} Close'].iloc[-1]), (len(data)-1-ax_p.get_xlim()[0])/ax_p_length
        else:
            c_value, c_datenum = None, None

        label_vd_list.append([o_value, o_datenum, 'O'])
        label_vd_list.append([h_value, h_datenum, 'H'])
        label_vd_list.append([l_value, l_datenum, 'L'])
        label_vd_list.append([c_value, c_datenum, 'C'])

        for label_bool, label_vd in zip(label_bools, label_vd_list):
            if label_bool:
                ax_p.axhline(label_vd[0], xmin=label_vd[1], color="orange", ls="--", lw=0.6, alpha=0.6)  # guide line
                ax_p.text(
                    x=1, y=label_vd[0], 
                    s=f"{label_vd[2]}: {label_vd[0]}", 
                    va="center", ha="left",
                    backgroundcolor="white", 
                    bbox=dict(facecolor="lightblue", edgecolor="none", boxstyle="round,pad=0.2"),
                    fontsize=5.5,
                    transform=ax_p.get_yaxis_transform()  #this make the x parameter a value between 0 and 1, 0 meaning very left side of the plot and 1 being the right
                )

        #REPLACING XLABEL INTEGERS WITH DATESTRINGS----------------------------------------
        f_list = list(ax_p.get_xticks()[1:len(ax_p.get_xticks())-1])
        int_list = [int(x) for x in f_list]
        int_list

        date_label_list = []
        for i in int_list:
            diff = i - data['DateNum'].iloc[-1]

            interval_dict = { 
            '1d': BDay(diff),
            '1wk': pd.DateOffset(weeks=diff),
            '1mo': pd.DateOffset(months=diff)
        }
            if diff <= 0:
                date_label_list.append(data.index[i].strftime('%Y-%b-%d'))
            elif diff > 0:
                diff = i - data['DateNum'].iloc[-1]
                date = data.index[-1] + interval_dict[interval]
                
                date_label_list.append(date.strftime('%Y-%b-%d'))

        def date_tick_labels(ax):
            ax.set_xticks(int_list)
            ax.set_xticklabels(date_label_list)

        if volume == True: 
            date_tick_labels(ax_v)
        elif volume == False:
            date_tick_labels(ax_p)

        #MAKING THE PLOT AESTHETIC---------------------------------------------------------
        def style_ax(ax):
            ax.set_facecolor('#fafafa') #BACKGROUND COLOR

            for spine in ax.spines.values(): # SPINES AKA EDGES
                spine.set_visible(True)            # ensure visibility
                spine.set_edgecolor('#7A7A7A')    # gray color
                spine.set_linewidth(0.5)          # adjust thickness

            ax.minorticks_on()
            ax.tick_params(which="minor", axis='both', direction='out', color='white') #minor ticks invisible

            ax.grid(which='major', color='#bfbfbf', linestyle='-', linewidth=0.35) #major grid lines
            ax.grid(which='minor', color='#bfbfbf', linestyle='--', linewidth=0.15) #minor grid lines

            ax.yaxis.tick_right()            # ticks appear on the right
            ax.yaxis.set_label_position("right")  # y-axis label moves to the right

            for label in ax.get_xticklabels() + ax.get_yticklabels(): #sets all label fonts to 7 and Arial
                label.set_fontsize(7)
                label.set_fontname('Arial')

            ax.set_axisbelow(True) #making the grid and everything below the actual data line

        if volume == False:
            style_ax(ax_p)
            ax_p.tick_params(which="major", axis='both', direction='in', width=0.7) #major ohlc chart ticks
        elif volume == True:
            style_ax(ax_p)
            ax_p.tick_params(bottom=False, labelbottom=False) # deleting the ohlc chart xticks and xlabels
            style_ax(ax_v)
            ax_v.tick_params(which="major", axis='both', direction='in', width=0.7) #major volume chart ticks

        #OPTIONAL LEGEND-------------------------------------------------------------------
        if legend: ax_p.legend(fontsize=6, frameon=False, facecolor=None, borderaxespad=1.2)

        #OPTIONAL TITLE--------------------------------------------------------------------
        if title:
            interval_map = {
                '1d': 'Daily',
                '1wk': 'Weekly',
                '1mo': 'Monthly',
                '3mo': 'Quarterly'
            }
            first_date = data.index[0].strftime('%b %Y')
            last_date = data.index[-1].strftime('%b %Y')
            ax_p.set_title(f'{self.ticker} Stock Price — {interval_map[interval]} OHLC{' and Volume' if volume else ''} ({first_date} - {last_date})', fontsize=6.5, loc='left', pad=4, fontname='Arial', weight='bold')

        #SAVE------------------------------------------------------------------------------
        if save:
            plt.savefig(f'{self.ticker}_CandleChart.png', dpi=300, bbox_inches='tight')

        #SHOW------------------------------------------------------------------------------
        if show:
            plt.show()
        elif show == False:
            plt.close(fig)
#------------------------------------------------------------------------------------------
    def realtime(self, display: str = 'json'): 
        valid_params = {'display': ['json', 'pretty']}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        if Config.td_apikey is None:
            raise MissingConfigObject('Missing td_apikey. Please set your Twelve Data api key using the set_config() function.')

        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        url_1 = Config.td_baseurl + f'price?apikey={Config.td_apikey}&symbol={self.mticker}'
        td_realtime = requests.get(url_1).json()

        url_2 = Config.td_baseurl + f'quote?apikey={Config.td_apikey}&symbol={self.mticker}'
        td_quote = requests.get(url_2).json()
        #----------------------------------------------------------------------------------
        
        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            output = {'symbol': self.ticker,
                      'price': float(td_realtime['price']),
                      'currency': td_quote['currency']}
            return output
        
        elif display == 'pretty':
            output = f'''  Symbol: {self.ticker}
   Price: {round(float(td_realtime['price']),2)}
Currency: {td_quote['currency']}'''
            print(output)
#------------------------------------------------------------------------------------------
    def statement(self, display: str = 'json', statement: str = 'all', currency: str = None, unit: str = 'raw', decimal: bool = False, interval: str = 'annual'): 
        valid_params = {'valid_statement' : ['income', 'balance', 'cash', 'all'],
                        'valid_unit' : ['thousand', 'million', 'raw'],
                        'valid_display' : ['json', 'table'],
                        'valid_decimal' : [True, False],
                        'valid_interval' : ['annual', 'quarter']}
        
        params = {'statement': statement,
                  'units': unit,
                  'display': display,
                  'decimal': decimal,
                  'interval': interval}
        
        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        
        #RAW DATA/OBSERVATIONS--------------------------------------------------------------
        firm = yf.Ticker(self.ticker)

        #STATEMENT ITEMS
        statement_items = {
            'income': ['Total Revenue',
                       'Cost Of Revenue',
                       'Gross Profit',
                       'Research And Development',
                       'Other Operating Expenses',
                       'EBITDA',
                       'Reconciled Depreciation',
                       'EBIT',
                       'Interest Expense',
                       'Interest Income',
                       'Pretax Income',
                       'Tax Provision',
                       'Net Income'],
            'balance': ['Total Assets',
                        'Current Assets',
                        'Cash And Cash Equivalents',
                        'Accounts Receivable',
                        'Inventory',
                        'Other Current Assets',
                        'Total Non Current Assets',
                        'Net PPE',
                        'Goodwill And Other Intangible Assets',
                        'Other Non Current Assets',
                        'Total Liabilities Net Minority Interest',
                        'Current Liabilities',
                        'Accounts Payable',
                        'Current Debt And Capital Lease Obligation',
                        'Other Current Liabilities',
                        'Total Non Current Liabilities Net Minority Interest',
                        'Long Term Debt And Capital Lease Obligation',
                        'Other Non Current Liabilities',
                        'Total Equity Gross Minority Interest',
                        'Retained Earnings',
                        'Other Equity'],
            'cash': ['Operating Cash Flow',
                     'Net Income From Continuing Operations',
                     'Depreciation Amortization Depletion',
                     'Change In Working Capital',
                     'Other Operating Cash Flow',
                     'Investing Cash Flow',
                     'Capital Expenditure',
                     'Other Investing Cash Flow',
                     'Financing Cash Flow',
                     'Net Issuance Payments Of Debt',
                     'Net Common Stock Issuance',
                     'Cash Dividends Paid',
                     'Other Financing Cash Flow',
                     'Beginning Cash Position',
                     'Changes In Cash',
                     'Other Changes',
                     'End Cash Position']
        }

        renamed_items = {
            'income': ['Total Revenue',
                       'Cost Of Revenue',
                       'Gross Profit',
                       'Research And Development',
                       'Other Operating Expenses',
                       'EBITDA',
                       'Depreciation and Amortization',
                       'EBIT',
                       'Interest Expense',
                       'Interest Income',
                       'Pretax Income',
                       'Tax Provision',
                       'Net Income'],
            'balance': ['Total Assets',
                        'Total Current Assets',
                        'Cash And Cash Equivalents',
                        'Accounts Receivable',
                        'Inventory',
                        'Other Current Assets',
                        'Total Non Current Assets',
                        'Net PPE',
                        'Goodwill And Other Intangible Assets',
                        'Other Non Current Assets',
                        'Total Liabilities',
                        'Total Current Liabilities',
                        'Accounts Payable',
                        'Short Term Debt And Capital Lease Obligation',
                        'Other Current Liabilities',
                        'Total Non Current Liabilities',
                        'Long Term Debt And Capital Lease Obligation',
                        'Other Non Current Liabiltiies',
                        'Total Equity',
                        'Retained Earnings',
                        'Other Equity'],
            'cash': ['Operating Cash Flow',
                     'Net Income',
                     'Depreciation And Amortization',
                     'Change In Working Capital',
                     'Other Operating Cash Flow',
                     'Investing Cash Flow',
                     'Capital Expenditure',
                     'Other Investing Cash Flow',
                     'Financing Cash Flow',
                     'Net Issuance/Payments Of Debt',
                     'Net Common Stock Issuance',
                     'Cash Dividends Paid',
                     'Other Financing Cash Flow',
                     'Beginning Cash Position',
                     'Net Change in Cash',
                     'Other Changes',
                     'End Cash Position']
        }
        
        #PARAMETER - INTERVAL ==============================================================
        def Income():
            if interval == 'annual':
                IS = firm.income_stmt.iloc[:, 0:4]
            elif interval == 'quarter':
                IS = firm.quarterly_income_stmt.iloc[:, 0:5]

                    #creating new IS line item
            IS.loc['Other Operating Expenses'] = (
                (IS.loc['Gross Profit'] if 'Gross Profit' in IS.index else np.nan)
                - (IS.loc['Research And Development'] if 'Research And Development' in IS.index else 0)
                - (IS.loc['EBITDA'] if 'EBITDA' in IS.index else 0)
            )

                    #filtering which line items to output
            IS = IS.reindex(statement_items['income'], fill_value=np.nan)

                    #renaming line item titles to better syntax
            IS.index = renamed_items['income']

            return IS
        
        def Balance():
            if interval == 'annual':
                BS = firm.balance_sheet.iloc[:, 0:4]
            elif interval == 'quarter':
                BS = firm.quarterly_balance_sheet.iloc[:, 0:5]

            BS.loc['Other Current Assets'] = (
                (BS.loc['Current Assets'] if 'Current Assets' in BS.index else np.nan)
                - (BS.loc['Cash And Cash Equivalents'] if 'Cash And Cash Equivalents' in BS.index else 0) 
                - (BS.loc['Accounts Receivable'] if 'Accounts Receivable' in BS.index else 0) 
                - (BS.loc['Inventory'] if 'Inventory' in BS.index else 0)
            )
            BS.loc['Other Non Current Assets'] = (
                (BS.loc['Total Non Current Assets'] if 'Total Non Current Assets' in BS.index else np.nan)
                - (BS.loc['Net PPE'] if 'Net PPE' in BS.index else 0)
                - (BS.loc['Goodwill And Other Intangible Assets'] if 'Goodwill And Other Intangible Assets' in BS.index else 0)
            )
            BS.loc['Other Current Liabilities'] = (
                (BS.loc['Current Liabilities'] if 'Current Liabilities' in BS.index else np.nan)
                - (BS.loc['Accounts Payable'] if 'Accounts Payable' in BS.index else 0)
                - (BS.loc['Current Debt And Capital Lease Obligation'] if 'Current Debt And Capital Lease Obligation' in BS.index else 0)
            )
            BS.loc['Other Non Current Liabilities'] = (
                (BS.loc['Total Non Current Liabilities Net Minority Interest'] if 'Total Non Current Liabilities Net Minority Interest' in BS.index else np.nan)
                - (BS.loc['Long Term Debt And Capital Lease Obligation'] if 'Long Term Debt And Capital Lease Obligation' in BS.index else 0)
            )
            BS.loc['Other Equity'] = (
                (BS.loc['Total Equity Gross Minority Interest'] if 'Total Equity Gross Minority Interest' in BS.index else np.nan)
                - (BS.loc['Retained Earnings'] if 'Retained Earnings' in BS.index else 0)
            )

            BS = BS.reindex(statement_items['balance'], fill_value=np.nan)

            BS.index = renamed_items['balance']

            return BS

        def Cash():
            if interval == 'annual':
                CF = firm.cash_flow.iloc[:, 0:4]
            elif interval == 'quarter':
                CF = firm.quarterly_cash_flow.iloc[:, 0:5]

            CF.loc['Other Operating Cash Flow'] = (
                (CF.loc['Operating Cash Flow'] if 'Operating Cash Flow' in CF.index else np.nan)
                - (CF.loc['Net Income From Continuing Operations'] if 'Net Income From Continuing Operations' in CF.index else 0)
                - (CF.loc['Depreciation Amortization Depletion'] if 'Depreciation Amortization Depletion' in CF.index else 0)
                - (CF.loc['Change In Working Capital'] if 'Change In Working Capital' in CF.index else 0)
            )
            CF.loc['Other Investing Cash Flow'] = (
                (CF.loc['Investing Cash Flow'] if 'Investing Cash Flow' in CF.index else np.nan)
                - (CF.loc['Capital Expenditure'] if 'Capital Expenditure' in CF.index else 0)
            )
            CF.loc['Other Financing Cash Flow'] = (
                (CF.loc['Financing Cash Flow'] if 'Financing Cash Flow' in CF.index else np.nan)
                - (CF.loc['Net Issuance Payments Of Debt'] if 'Net Issuance Payments Of Debt' in CF.index else 0)
                - (CF.loc['Net Common Stock Issuance'] if 'Net Common Stock Issuance' in CF.index else 0)
                - (CF.loc['Cash Dividends Paid'] if 'Cash Dividends Paid' in CF.index else 0)
            )
            CF.loc['Other Changes'] = (
                (CF.loc['End Cash Position'] if 'End Cash Position' in CF.index else np.nan)
                - (CF.loc['Beginning Cash Position'] if 'Beginning Cash Position' in CF.index else 0)
                - (CF.loc['Changes In Cash'] if 'Changes In Cash' in CF.index else 0)
            )

            CF = CF.reindex(statement_items['cash'], fill_value=np.nan)

            CF.index = renamed_items['cash']

            return CF
        #-----------------------------------------------------------------------------------
        
        #PARAMETER - STATEMENT =============================================================
        if statement == 'all':
            data = pd.concat([Income(), 
                              Balance(), 
                              Cash().loc[['Operating Cash Flow',
                                          'Change In Working Capital',
                                          'Other Operating Cash Flow',
                                          'Investing Cash Flow',
                                          'Capital Expenditure',
                                          'Other Investing Cash Flow',
                                          'Financing Cash Flow',
                                          'Net Issuance/Payments Of Debt',
                                          'Net Common Stock Issuance',
                                          'Cash Dividends Paid',
                                          'Other Financing Cash Flow',
                                          'Beginning Cash Position',
                                          'Net Change in Cash',
                                          'Other Changes',
                                          'End Cash Position']]])
        elif statement == 'income':
            data = Income()
        elif statement == 'balance':
            data = Balance()
        elif statement == 'cash':
            data = Cash()

        #PARAMETER - UNIT ==================================================================
        if unit == 'thousand':
            data /= 1000
        elif unit == 'million':
            data /= 1000000

        #PARAMETER - CURRENCY ==============================================================
        current_currency = firm.get_info()['financialCurrency'] if 'financialCurrency' in firm.get_info().keys() else '---'
        
        if currency == current_currency or currency == '---':
            None
        elif currency != None:
            if Config.td_apikey is None:
                raise MissingConfigObject('Missing td_apikey. Please set you Twelve Data api key using the set_config() function.')
            
            forex_pair = f'{current_currency}/{currency}'
            url = Config.td_baseurl + f'price?apikey={Config.td_apikey}&symbol={forex_pair}'
            exchange_rate = requests.get(url).json()['price']
            
            data *= float(exchange_rate)
            
        #PARAMETER - DECIMAL ===============================================================
        if decimal == False:
            data = data.map(lambda x: str(x) if pd.isna(x) else x)
            data = data.map(lambda x: int('{:.0f}'.format(x)) if isinstance(x, float) else x)

        #COLUMN RENAMING
        if interval == 'annual':
            data.columns = [f'FY {str(col)[:4]}' for col in data.columns]
            data = data.iloc[:, :4]
        elif interval == 'quarter':
            data.columns = [f'{str(col)[:7]}' for col in data.columns]

        #PARAMETER - DISPLAY ===============================================================
        if display == 'json':
            output = data.to_dict()
            return output
        elif display == 'table':
            output = data.map(lambda x: f'{x:,}' if isinstance(x, (int, float)) and pd.notna(x) else x)
            return output
#------------------------------------------------------------------------------------------
    def quote(self, display: str = 'json'):
        valid_params = {'valid_display': ['json', 'pretty'],}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        #RAW DATA/OBSERVATIONS--------------------------------------------------------------
        today = date.today().strftime("%Y-%m-%d")
        six_y_ago = str(int(today[0:4])-6) + today[4:]
        
        yf_download = yf.download(self.ticker, progress=False, auto_adjust=True, start=six_y_ago, end=today)
        
        yf_quote = yf.Ticker(self.ticker).get_fast_info()

        yf_history_metadata = yf.Ticker(self.ticker).get_history_metadata()

        yf_eod = yf.download(self.ticker, progress=False, auto_adjust=True)['Close'].iloc[-1].iloc[0]

        current_year = pd.Timestamp.now().year
        #-----------------------------------------------------------------------------------
        
        #DATES
        initial_dates = [
                    date.today() - relativedelta(years=5),
                    date.today() - relativedelta(years=1),
                    date.today() - relativedelta(months=6),
                    date.today() - relativedelta(months=1)
                    #we do not need a date for 5 days because the # days is fixed
                ]

        initial_dates = [pd.Timestamp(d) for d in initial_dates]

        final_dates = []

        for d in initial_dates:
            while d not in yf_download.index.tolist():
                d = d + relativedelta(days=1)
            final_dates.append(d)
        
        #JSON FORMAT DATA
        quote_data = {
            'symbol': yf_history_metadata.get('symbol', '-'),
            'name': yf_history_metadata.get('longName', '-'),
            'exchange': yf_history_metadata.get('fullExchangeName', '-'),
            'currency': yf_history_metadata.get('currency', '-'),
            'timezone': yf_history_metadata.get('timezone','-'),
            'last trading day': {
                'date': str(yf_download.index[-1].date()),
                'open': float((yf_download['Open'].iloc[-1]).iloc[0]),
                'high': float((yf_download['High'].iloc[-1]).iloc[0]),
                'low': float((yf_download['Low'].iloc[-1]).iloc[0]),
                'close': float((yf_download['Close'].iloc[-1]).iloc[0]),
                'volume': int((yf_download['Volume'].iloc[-1]).iloc[0])
            },
            'ttm': {
                'high': round(float((yf_download['High'].loc[final_dates[1]:].max()).iloc[0]),2),
                'low': round(float((yf_download['Low'].loc[final_dates[1]:].min()).iloc[0]),2)
            },
            'percent change': {
                '5y': float(((yf_eod/yf_download['Close'].loc[final_dates[0]]) - 1).iloc[0]) if yf_download.shape[0]>1265 else np.nan,
                '1y': float(((yf_eod/yf_download['Close'].loc[final_dates[1]]) - 1).iloc[0]) if yf_download.shape[0]>260 else np.nan,
                'ytd': float(((yf_eod/yf_download['Close'][yf_download.index.year == current_year].iloc[0]) - 1).iloc[0]),
                '6m': float(((yf_eod/yf_download['Close'].loc[final_dates[2]]) - 1).iloc[0]) if yf_download.shape[0]>130 else np.nan,
                '1m': float(((yf_eod/yf_download['Close'].loc[final_dates[3]]) - 1).iloc[0]) if yf_download.shape[0]>25 else np.nan,
                '5d': float(((yf_eod/yf_download['Close'].iloc[-5]) - 1).iloc[0]) if yf_download.shape[0]>6 else np.nan
            },
            '50d average price': float((yf_download['Close'].iloc[-50:].mean()).iloc[0]),
            '200d average price': float((yf_download['Close'].iloc[-200:].mean()).iloc[0]),
            '10d average volume': int((yf_download['Volume'].iloc[-10:].mean()).iloc[0]),
            '90d average volume': int((yf_download['Volume'].iloc[-90:].mean()).iloc[0]),
            'shares outstanding': int(yf_quote['shares']),
            'market cap': int(yf_quote.get('shares', np.nan) * yf_eod)
        }

        #PARAMETER - DISPLAY ===============================================================
        if display == 'json':
            output = quote_data
            return output
        elif display == 'pretty':
            output = f'''
        Identifier: {quote_data['symbol']} - {quote_data['name']}
 Exchange/Timezone: {quote_data['exchange']} - {quote_data['timezone']}
          Currency: {quote_data['currency']}
Shares Outstanding: {'{:,}'.format(quote_data['shares outstanding'])}
        Market Cap: {'{:,}'.format(quote_data['market cap'])}

{quote_data['last trading day']['date']} OHLCV------------------------
           OPEN --  {round(quote_data['last trading day']['open'],2):,}
           HIGH --  {round(quote_data['last trading day']['high'],2):,}
            LOW --  {round(quote_data['last trading day']['low'],2):,}
          CLOSE --  {round(quote_data['last trading day']['close'],2):,}
         VOLUME --  {'{:,}'.format(round(quote_data['last trading day']['volume'],2))}
TTM HIGH/LOW----------------------------
           HIGH --  {round(quote_data['ttm']['high'],2):,}{'*' if yf_download.shape[0]<252 else ''}
            LOW --  {round(quote_data['ttm']['low'],2):,}{'*' if yf_download.shape[0]<252 else ''}
PERCENT CHANGE--------------------------
         5 YEAR -- {' ' if pd.isna(quote_data['percent change']['5y']) or quote_data['percent change']['5y']>0 else ''}{round(quote_data['percent change']['5y'] * 100,2)}%
         1 YEAR -- {' ' if pd.isna(quote_data['percent change']['1y']) or quote_data['percent change']['1y']>0 else ''}{round(quote_data['percent change']['1y'] * 100,2)}%
            YTD -- {' ' if pd.isna(quote_data['percent change']['ytd']) or quote_data['percent change']['ytd']>0 else ''}{round(quote_data['percent change']['ytd'] * 100,2)}%
        6 MONTH -- {' ' if pd.isna(quote_data['percent change']['6m']) or quote_data['percent change']['6m']>0 else ''}{round(quote_data['percent change']['6m'] * 100,2)}%
        1 MONTH -- {' ' if pd.isna(quote_data['percent change']['1m']) or quote_data['percent change']['1m']>0 else ''}{round(quote_data['percent change']['1m'] * 100,2)}%
          5 DAY -- {' ' if pd.isna(quote_data['percent change']['5d']) or quote_data['percent change']['5d']>0 else ''}{round(quote_data['percent change']['5d'] * 100,2)}%
MOVING AVERAGES-------------------------
   50 DAY PRICE --  {round(quote_data['50d average price'],2)}
  200 DAY PRICE --  {round(quote_data['200d average price'],2)}
  10 DAY VOLUME --  {'{:,}'.format(quote_data['10d average volume'])}
  90 DAY VOLUME --  {'{:,}'.format(quote_data['90d average volume'])}
'''
            print(output)
#------------------------------------------------------------------------------------------
    def info(self, display: str = 'json'): 
        valid_params = {'valid_display': ['json', 'pretty'],}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        #RAW DATA/OBSERVATIONS--------------------------------------------------------------
        yf_history_metadata = yf.Ticker(self.ticker).get_history_metadata()

        yf_info = yf.Ticker(self.ticker).get_info()

        yf_calendar = yf.Ticker(self.ticker).get_calendar()

        #cik id
        if Config.email_address is None:
                raise MissingConfigObject('Missing email_address. Please set your email address using the set_config() function.')

        sec_header = {'User-Agent': f"{Config.email_address}"}
        sec_list = requests.get(f'{Config.sec_baseurl}files/company_tickers.json', headers=sec_header).json()

        companyData = pd.DataFrame.from_dict(sec_list, orient='index')

        companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)

        try:
            index_of_ticker = int(companyData[companyData['ticker'] == self.ticker].index[0])

            sec_cik = companyData.iloc[index_of_ticker,0]
        except IndexError:
            sec_cik = '-'
        #-----------------------------------------------------------------------------------

        #COMPANY OFFICERS
        company_officers = {}
        if 'companyOfficers' in yf_info.keys():
            for officer in yf_info['companyOfficers']:
                company_officers[officer['name']] = officer['title']
            
            longest_name_length = max([len(name) for name in company_officers.keys()])

        #JSON FORMAT DATA
        info_data = {
            'symbol': yf_history_metadata.get('symbol', '-'),
            'name': yf_history_metadata.get('longName', '-'),
            'exchange': yf_history_metadata.get('fullExchangeName', '-'),
            'stock currency': yf_history_metadata.get('currency', '-'),
            'financial currency': yf_info.get('financialCurrency', '-'),
            'timezone': yf_history_metadata.get('timezone', '-'),
            'country': yf_info.get('country', '-'),
            'industry': yf_info.get('industry', '-'),
            'sector': yf_info.get('sector','-'),
            'cik': sec_cik,
            'dividend date': yf_calendar.get('Dividend Date', '-'),
            'ex-dividend date': yf_calendar.get('Ex-Dividend Date', '-'),
            'earnings date': yf_calendar.get('Earnings Date', '-'),
            'website': yf_info.get('website', '-'),
            'description': yf_info.get('longBusinessSummary', '-'),
            'company officers': company_officers
        }

        #COMPANY OFFICERS
        def companyOfficers():
            b = ''
            for k,v in company_officers.items():
                a = f'{k.rjust(longest_name_length)} -- {v}\n'
                b += a
            return b

        #PARAMETER - DISPLAY ===============================================================
        if display == 'json':
            output = info_data
            return output
        elif display == 'pretty':
            output = f'''
        Identifier: {info_data['symbol']} - {info_data['name']}
 Exchange/Timezone: {info_data['exchange']} - {info_data['timezone']}
    Stock Currency: {info_data['stock currency']}
Financial Currency: {info_data['financial currency']}
           Country: {info_data['country']}
               CIK: {info_data['cik']}
   Sector/Industry: {info_data['sector']} - {info_data['industry']}
           Website: {info_data['website']}
     Earnings Date: {info_data['earnings date'][0].strftime('%B %d, %Y') if info_data['earnings date'] != '-' else '-'}
     Dividend Date: {info_data['dividend date'].strftime('%B %d, %Y') if info_data['dividend date'] != '-' else '-'}
  Ex-Dividend Date: {info_data['ex-dividend date'].strftime('%B %d, %Y') if info_data['ex-dividend date'] != '-' else '-'}

DESCRIPTION-------------------------------------------------------
{info_data['description']}

COMPANY OFFICERS--------------------------------------------------
{companyOfficers()}'''
            
            print(output)
#------------------------------------------------------------------------------------------
    def filings(self, form: str = None): 
        
        if Config.email_address is None:
                raise MissingConfigObject('Missing email_address. Please set your email address using the set_config() function.')

        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        headers = {'User-Agent': f"{Config.email_address}"}
        companyTickers = requests.get(f'{Config.sec_baseurl}files/company_tickers.json', headers=headers) #ticker-cik json data request
        
        companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
        companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10) # adding leading zeros to cik

        index_of_ticker = int(companyData[companyData['ticker'] == self.ticker].index[0]) #finding the row with the desired ticker

        sec_cik = companyData.iloc[index_of_ticker,0] #retriving the cik id of the ticker

        filingMetadata = requests.get(f'https://data.sec.gov/submissions/CIK{sec_cik}.json', headers=headers) #requesting raw json filing data
        #----------------------------------------------------------------------------------

        #DATAFRAME ORGANIZATION
        allForms = pd.DataFrame.from_dict(filingMetadata.json()['filings']['recent'])

        allForms = allForms[['accessionNumber','filingDate','form']]

        allForms = allForms.set_index('accessionNumber')

        #PARAMETER - FORM =================================================================
        if form != None:
            allForms = allForms[allForms['form'] == form]

        return allForms
#------------------------------------------------------------------------------------------
    def analyst_estimates(self, display: str = 'json'): 
        valid_params = {'valid_display': ['json', 'pretty'],}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        firm = yf.Ticker(self.ticker)

        yf_calendar = firm.get_calendar()
        yf_earnings_estimate = firm.get_earnings_estimate()
        yf_revenue_estimate = firm.get_revenue_estimate()
        yf_growth_estimate = firm.get_growth_estimates()
        yf_price_estimate = firm.get_analyst_price_targets()

        yf_history_metadata = firm.get_history_metadata()

        yf_info = yf.Ticker(self.ticker).get_info()
        #----------------------------------------------------------------------------------

        #renaming a json format EARNINGS estimate data
        earnings_dict = yf_earnings_estimate.T.to_dict()
        earnings_dict['current quarter'] = earnings_dict.pop('0q')
        earnings_dict['next quarter'] = earnings_dict.pop('+1q')
        earnings_dict['current year'] = earnings_dict.pop('0y')
        earnings_dict['next year'] = earnings_dict.pop('+1y')
        

        #renaming a json format REVENUE estimate data
        revenue_dict = yf_revenue_estimate.T.to_dict()
        revenue_dict['current quarter'] = revenue_dict.pop('0q')
        revenue_dict['next quarter'] = revenue_dict.pop('+1q')
        revenue_dict['current year'] = revenue_dict.pop('0y')
        revenue_dict['next year'] = revenue_dict.pop('+1y')

        #renaming a json format GROWTH estimate data
        growth_dict = yf_growth_estimate.T.to_dict()
        growth_dict['current quarter'] = growth_dict.pop('0q')
        growth_dict['next quarter'] = growth_dict.pop('+1q')
        growth_dict['current year'] = growth_dict.pop('0y')
        growth_dict['next year'] = growth_dict.pop('+1y')

        #PRICE
        price_dict = yf_price_estimate

        #JSON FORMAT DATA
        estimate_data = {
            'symbol': yf_history_metadata.get('symbol','-'),
            'name': yf_history_metadata.get('longName','-'),
            'exchange': yf_history_metadata.get('fullExchangeName','-'),
            'stock currency': yf_history_metadata.get('currency','-'),
            'financial currency': yf_info.get('financialCurrency','-'),
            'timezone': yf_history_metadata.get('timezone','-'),
            'earnings date': yf_calendar.get('Earnings Date','-'),
            'dividend date': yf_calendar.get('Dividend Date','-'),
            'ex-dividend date': yf_calendar.get('Ex-Dividend Date','-'),
            'earnings_estimate': earnings_dict,
            'revenue_estimate': revenue_dict,
            'growth_estimate': growth_dict,
            'price_estimate': price_dict,
        }

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            output = estimate_data
            return output
        elif display == 'pretty':
            def two(num):
                return '{:.2f}'.format(num)
            
            def com(num):
                return '{:,}'.format(num)

            e = estimate_data['earnings_estimate']
            r = estimate_data['revenue_estimate']
            g = estimate_data['growth_estimate']

            output = f'''
        Identifier: {estimate_data['symbol']} - {estimate_data['name']}
 Exchange/Timezone: {estimate_data['exchange']} - {estimate_data['timezone']}
    Stock Currency: {estimate_data['stock currency']}
Financial Currency: {estimate_data['financial currency']}
     Earnings Date: {estimate_data['earnings date'][0].strftime('%B %d, %Y')}
     Dividend Date: {estimate_data['dividend date'].strftime('%B %d, %Y') if estimate_data['dividend date'] != '-' else '-'}
  Ex-Dividend Date: {estimate_data['ex-dividend date'].strftime('%B %d, %Y') if estimate_data['ex-dividend date'] != '-' else '-'}

EARNINGS ESTIMATE-------------------------------------------------------
                 Current |    Next | Current |    Next |
                 Quarter | Quarter |    Year |    Year |
          HIGH  {str(two(e['current quarter']['high'])).rjust(8)} |{str(two(e['next quarter']['high'])).rjust(8)} |{str(two(e['current year']['high'])).rjust(8)} |{str(two(e['next year']['high'])).rjust(8)} |
       AVERAGE  {str(two(e['current quarter']['avg'])).rjust(8)} |{str(two(e['next quarter']['avg'])).rjust(8)} |{str(two(e['current year']['avg'])).rjust(8)} |{str(two(e['next year']['avg'])).rjust(8)} |
           LOW  {str(two(e['current quarter']['low'])).rjust(8)} |{str(two(e['next quarter']['low'])).rjust(8)} |{str(two(e['current year']['low'])).rjust(8)} |{str(two(e['next year']['low'])).rjust(8)} |
       -1Y EPS  {str(two(e['current quarter']['yearAgoEps'])).rjust(8)} |{str(two(e['next quarter']['yearAgoEps'])).rjust(8)} |{str(two(e['current year']['yearAgoEps'])).rjust(8)} |{str(two(e['next year']['yearAgoEps'])).rjust(8)} |
      % CHANGE  {str(two(e['current quarter']['growth']*100)).rjust(8)}%|{str(two(e['next quarter']['growth']*100)).rjust(8)}%|{str(two(e['current year']['growth']*100)).rjust(8)}%|{str(two(e['next year']['growth']*100)).rjust(8)}%|
 # OF ANALYSTS  {str(int(e['current quarter']['numberOfAnalysts'])).rjust(8)} |{str(int(e['next quarter']['numberOfAnalysts'])).rjust(8)} |{str(int(e['current year']['numberOfAnalysts'])).rjust(8)} |{str(int(e['next year']['numberOfAnalysts'])).rjust(8)} |

REVENUE ESTIMATE-----------------------------------------in {yf_info['financialCurrency'].rjust(3)} millions
                 Current |    Next | Current |    Next |
                 Quarter | Quarter |    Year |    Year |
          HIGH  {com(int(r['current quarter']['high']/1000000)).rjust(8)} |{com(int(r['next quarter']['high']/1000000)).rjust(8)} |{com(int(r['current year']['high']/1000000)).rjust(8)} |{com(int(r['next year']['high']/1000000)).rjust(8)} |
       AVERAGE  {com(int(r['current quarter']['avg']/1000000)).rjust(8)} |{com(int(r['next quarter']['avg']/1000000)).rjust(8)} |{com(int(r['current year']['avg']/1000000)).rjust(8)} |{com(int(r['next year']['avg']/1000000)).rjust(8)} |
           LOW  {com(int(r['current quarter']['low']/1000000)).rjust(8)} |{com(int(r['next quarter']['low']/1000000)).rjust(8)} |{com(int(r['current year']['low']/1000000)).rjust(8)} |{com(int(r['next year']['low']/1000000)).rjust(8)} |
       -1Y REV  {com(int(r['current quarter']['yearAgoRevenue']/1000000)).rjust(8)} |{com(int(r['next quarter']['yearAgoRevenue']/1000000)).rjust(8)} |{com(int(r['current year']['yearAgoRevenue']/1000000)).rjust(8)} |{com(int(r['next year']['yearAgoRevenue']/1000000)).rjust(8)} |
      % CHANGE  {str(two(r['current quarter']['growth']*100)).rjust(8)}%|{str(two(r['next quarter']['growth']*100)).rjust(8)}%|{str(two(r['current year']['growth']*100)).rjust(8)}%|{str(two(r['next year']['growth']*100)).rjust(8)}%|
 # OF ANALYSTS  {str(int(r['current quarter']['numberOfAnalysts'])).rjust(8)} |{str(int(r['next quarter']['numberOfAnalysts'])).rjust(8)} |{str(int(r['current year']['numberOfAnalysts'])).rjust(8)} |{str(int(r['next year']['numberOfAnalysts'])).rjust(8)} |

GROWTH ESTIMATE---------------------------------------------------------
                 Current |    Next | Current |    Next |
                 Quarter | Quarter |    Year |    Year |
% STOCK CHANGE  {str(two(g['current quarter']['stockTrend']*100)).rjust(7)}% |{str(two(g['next quarter']['stockTrend']*100)).rjust(7)}% |{str(two(g['current year']['stockTrend']*100)).rjust(7)}% |{str(two(g['next year']['stockTrend']*100)).rjust(7)}% |
% INDEX CHANGE  {str(two(g['current quarter']['indexTrend']*100)).rjust(7)}% |{str(two(g['next quarter']['indexTrend']*100)).rjust(7)}% |{str(two(g['current year']['indexTrend']*100)).rjust(7)}% |{str(two(g['next year']['indexTrend']*100)).rjust(7)}% |

PRICE ESTIMATE----------------------------------------------------------
       CURRENT -- {two(estimate_data['price_estimate']['current'])}
        MEDIAN -- {two(estimate_data['price_estimate']['median'])}
          HIGH -- {two(estimate_data['price_estimate']['high'])}
          MEAN -- {two(estimate_data['price_estimate']['mean'])}
           LOW -- {two(estimate_data['price_estimate']['low'])}'''
            
            print(output)
#------------------------------------------------------------------------------------------
    def dividend(self, display: str = 'json'): 
        valid_params = {'valid_display': ['json', 'table'],}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
    
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        yf_dividends = yf.Ticker(self.ticker).get_dividends()
        #----------------------------------------------------------------------------------

        renamed_dates = {}
        for i in yf_dividends.keys():
            renamed_dates[i] = str(i)[0:10]

        #renaming the datetime indexes to date strings
        yf_dividends = yf_dividends.rename(renamed_dates)

        #converting series to dict to dataframe
        dividends_dict = yf_dividends.to_dict()
        dividends_df = pd.DataFrame.from_dict(dividends_dict, orient='index', columns=[f'{self.ticker} Dividends'])

        #making all values two decimal points
        dividends_df = dividends_df.map(lambda x: f'{x:.2f}' if isinstance(x, (int, float)) else x)
        dividends_df = dividends_df.astype(np.float64)
        dividends_df.index = pd.to_datetime(dividends_df.index)
        dividends_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            dividends_df.index = dividends_df.index.strftime('%Y-%m-%d')

            dividends_json_list = []
            for index, row in dividends_df.iterrows():
                a = {
                    'Date': index,
                    f'{self.ticker} Dividends': float(row[f'{self.ticker} Dividends'])
                }
                dividends_json_list.append(a)
            return dividends_json_list
        elif display == 'table':
            output = dividends_df
            return output
#------------------------------------------------------------------------------------------
    def split(self, display: str = 'json'): 
        valid_params = {'valid_display': ['json', 'table'],}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        yf_splits = yf.Ticker(self.ticker).get_splits()
        #----------------------------------------------------------------------------------

        renamed_dates = {}
        for i in yf_splits.keys():
            renamed_dates[i] = str(i)[0:10]

        #renaming the datetime indexes to date strings
        yf_splits = yf_splits.rename(renamed_dates)

        #converting series to dict to dataframe
        splits_dict = yf_splits.to_dict()
        splits_df = pd.DataFrame.from_dict(splits_dict, orient='index', columns=[f'{self.ticker} Splits'])
        splits_df.index = pd.to_datetime(splits_df.index)
        splits_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            splits_df.index = splits_df.index.strftime('%Y-%m-%d')

            splits_json_list = []
            for index, row in splits_df.iterrows():
                a = {
                    'Date': index,
                    f'{self.ticker} Splits': float(row[f'{self.ticker} Splits'])
                }
                splits_json_list.append(a)
            return splits_json_list
        elif display == 'table':
            output = splits_df
            return output
#------------------------------------------------------------------------------------------
    def stats(self, display: str = 'json'): 
        valid_params = {'valid_display': ['json', 'pretty'],}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        #ANNUAL DATA
        stmt_df = self.statement(display='table', unit='million') #gathering all statement item data
        stmt_df = stmt_df.map(lambda x: pd.to_numeric(x.replace(',', ''), errors='coerce') if isinstance(x, str) else x) #returning all df element datatypes to numerics
        stmt_loc = stmt_df.loc

        yf_raw_IS = yf.Ticker(self.ticker).income_stmt

        #QUARTERLY DATA
        q_stmt_df = self.statement(display='table', unit='million', interval='quarter')
        q_stmt_df = q_stmt_df.map(lambda x: pd.to_numeric(x.replace(',', ''), errors='coerce') if isinstance(x, str) else x)

        yf_raw_qIS = yf.Ticker(self.ticker).quarterly_income_stmt

        #OTHER
        yf_eod = yf.download(self.ticker, progress=False, auto_adjust=True)['Close'].iloc[-1].iloc[0]

        yf_quote = yf.Ticker(self.ticker).get_fast_info()

        yf_history_metadata = yf.Ticker(self.ticker).get_history_metadata()
        #-----------------------------------------------------------------------------------

        #CALCULATING ANNUAL FIGURES---------------------------------------------------------

        #ANNUAL FIGURES - PROFITABILITY
        stmt_loc['gross margin'] = stmt_loc['Gross Profit']/stmt_loc['Total Revenue']
        stmt_loc['ebit margin'] = stmt_loc['EBIT']/stmt_loc['Total Revenue']
        stmt_loc['net margin'] = stmt_loc['Net Income']/stmt_loc['Total Revenue']
        stmt_loc['roa'] = stmt_loc['Net Income']/stmt_loc['Total Assets']
        stmt_loc['roe'] = stmt_loc['Net Income']/stmt_loc['Total Equity']

        #ANNUAL FIGURES - LIQUIDITY
        stmt_loc['current ratio'] = stmt_loc['Total Current Assets']/stmt_loc['Total Current Liabilities']
        stmt_loc['quick ratio'] = (stmt_loc['Total Current Assets'] - stmt_loc['Inventory'])/stmt_loc['Total Current Liabilities']
        stmt_loc['cash ratio'] = stmt_loc['Cash And Cash Equivalents']/stmt_loc['Total Current Liabilities']

        #ANNUAL FIGURES - LEVERAGE
        stmt_loc['debt to equity'] = stmt_loc['Total Liabilities']/stmt_loc['Total Equity']
        stmt_loc['debt to assets'] = stmt_loc['Total Liabilities']/stmt_loc['Total Assets']
        stmt_loc['interest coverage ratio'] = stmt_loc['EBIT']/stmt_loc['Interest Expense']

        #ANNUAL FIGURES - EFFICIENCY
        stmt_loc['inventory turnover'] = stmt_loc['Cost Of Revenue'] / ((stmt_loc['Inventory'] + stmt_df.shift(-1, axis=1).loc['Inventory'])/2)
        stmt_loc['receivables turnover'] = stmt_loc['Total Revenue'] / ((stmt_loc['Accounts Receivable'] + stmt_df.shift(-1, axis=1).loc['Accounts Receivable'])/2)
        stmt_loc['payables turnover'] = stmt_loc['Cost Of Revenue'] / ((stmt_loc['Accounts Payable'] + stmt_df.shift(-1, axis=1).loc['Accounts Payable'])/2)
        stmt_loc['dio'] = 365 / stmt_loc['inventory turnover']
        stmt_loc['dso'] = 365 / stmt_loc['receivables turnover']
        stmt_loc['dpo'] = 365 / stmt_loc['payables turnover']
        stmt_loc['cash conversion cycle'] = stmt_loc['dso'] + stmt_loc['dio'] - stmt_loc['dpo']

        #ANNUAL FIGURES - CASH FLOW
        stmt_loc['fcff_DA.WC'] = stmt_loc['EBIT'] * (1 - (stmt_loc['Tax Provision']/stmt_loc['Pretax Income'])) + stmt_loc['Depreciation and Amortization'] + stmt_loc['Change In Working Capital'] + stmt_loc['Capital Expenditure']
        stmt_loc['fcff_DA.WC.otherNonCash'] = stmt_loc['fcff_DA.WC'] + stmt_loc['Other Operating Cash Flow']
        stmt_loc['fcfe_DA.WC'] = stmt_loc['Net Income'] + stmt_loc['Depreciation and Amortization'] + stmt_loc['Change In Working Capital'] + stmt_loc['Capital Expenditure'] + stmt_loc['Net Issuance/Payments Of Debt']
        stmt_loc['fcfe_DA.WC.otherNonCash'] = stmt_loc['Operating Cash Flow'] + stmt_loc['Capital Expenditure'] + stmt_loc['Net Issuance/Payments Of Debt']

        #ANNUAL FIGURES - GROWTH
        stmt_loc['revenue growth rate'] = (stmt_loc['Total Revenue'] / stmt_df.shift(-1, axis=1).loc['Total Revenue']) - 1
        stmt_loc['EBIT growth rate'] = (stmt_loc['EBIT'] / stmt_df.shift(-1, axis=1).loc['EBIT']) - 1

        #ANNUAL FIGURES - VALUATION
        #fy end date stock prices
        date_lists = []
        for i in yf_raw_IS.columns[0:4]:
            a = []
            a.append(str(i.date()))
            a.append(str(i.date() + timedelta(days=-1)))
            a.append(str(i.date() + timedelta(days=-2)))
            a.append(str(i.date() + timedelta(days=-3)))
            a.append(str(i.date() + timedelta(days=-4)))
            a.append(str(i.date() + timedelta(days=-5)))
            date_lists.append(a)

        FY_prices = []
        for date_list in date_lists:
            for date in date_list:
                try:
                    a = yf.download(self.ticker, progress=False, ignore_tz=True, auto_adjust=True, period='5y').loc[date]
                    FY_prices.append(float(a.iloc[0]))
                    break
                except KeyError:
                    None

        if len(FY_prices) == len(yf_raw_IS.columns[0:4]):
            for i in range(len(yf_raw_IS.columns[0:4]) - len(FY_prices)):
                FY_prices.append(np.nan)

        #valuation ratio calculations
        stmt_loc['stock price'] = FY_prices
        stmt_loc['shares outstanding'] = yf_raw_IS.loc['Basic Average Shares'].tolist()[0:4]
        stmt_loc['market cap'] = (stmt_loc['stock price'] * stmt_loc['shares outstanding'])/1000000

        stmt_loc['pe'] = stmt_loc['market cap'] / stmt_loc['Net Income']
        stmt_loc['ps'] = stmt_loc['market cap'] / stmt_loc['Total Revenue']
        stmt_loc['pb'] = stmt_loc['market cap'] / stmt_loc['Total Equity']
        stmt_loc['eps'] = yf_raw_IS.loc['Basic EPS'].tolist()[0:4]
        stmt_loc['dividend yield'] = -stmt_loc['Cash Dividends Paid'] / stmt_loc['market cap']
        stmt_loc['dividend payout ratio'] = -stmt_loc['Cash Dividends Paid'] / stmt_loc['Net Income']
        stmt_loc['enterprise value'] = stmt_loc['market cap'] + stmt_loc['Total Liabilities'] - stmt_loc['Cash And Cash Equivalents']
        stmt_loc['ev/ebitda'] = stmt_loc['enterprise value'] / stmt_loc['EBITDA']
        stmt_loc['ev/ebit'] = stmt_loc['enterprise value'] / stmt_loc['EBIT']
        #-----------------------------------------------------------------------------------

        #CALCULATING RECENT FIGURES---------------------------------------------------------

        #RECENT FIGURES - VALUTION
        market_cap = int(yf_quote['shares'] * yf_eod)/1000000
        
        try:
            ttm_pe = market_cap / sum(q_stmt_df.loc['Net Income'].tolist()[0:4])
        except ZeroDivisionError:
            ttm_pe = float('inf')

        try:
            ttm_ps = market_cap / sum(q_stmt_df.loc['Total Revenue'].tolist()[0:4])
        except ZeroDivisionError:
            ttm_ps = float('inf')

        
        mrq_pb = market_cap / q_stmt_df.iloc[:,0].loc['Total Equity']
        mrq_eps = yf_raw_qIS.iloc[:,0].loc['Basic EPS']
        ttm_eps = sum(yf_raw_qIS.loc['Basic EPS'].tolist()[0:4])
        ttm_dividend_yield = -sum(q_stmt_df.loc['Cash Dividends Paid'].tolist()[0:4]) / market_cap

        try:
            mrq_dividend_payout_ratio = -q_stmt_df.iloc[:,0].loc['Cash Dividends Paid'] / q_stmt_df.iloc[:,0].loc['Net Income']
        except ZeroDivisionError:
            mrq_dividend_payout_ratio = np.nan
        
        try:
            ttm_dividend_payout_ratio = -sum(q_stmt_df.loc['Cash Dividends Paid'].tolist()[0:4]) / sum(q_stmt_df.loc['Net Income'].tolist()[0:4])
        except ZeroDivisionError:
            ttm_dividend_payout_ratio = np.nan
        
        mrq_enterprise_value = market_cap + q_stmt_df.iloc[:,0].loc['Total Liabilities'] - q_stmt_df.iloc[:,0].loc['Cash And Cash Equivalents']
        
        try:
            ttm_ev_ebitda = mrq_enterprise_value / sum(q_stmt_df.loc['EBITDA'].tolist()[0:4])
        except ZeroDivisionError:
            ttm_ev_ebitda = np.nan
        
        try:
            ttm_ev_ebit = mrq_enterprise_value / sum(q_stmt_df.loc['EBIT'].tolist()[0:4])
        except ZeroDivisionError:
            ttm_ev_ebit = np.nan

        #RECENT FIGURES - PROFITABILITY
        try:
            mrq_gross_margin = q_stmt_df.iloc[:,0].loc['Gross Profit'] / q_stmt_df.iloc[:,0].loc['Total Revenue']
        except ZeroDivisionError:
            mrq_gross_margin = np.nan

        try:
            mrq_ebit_margin = q_stmt_df.iloc[:,0].loc['EBIT'] / q_stmt_df.iloc[:,0].loc['Total Revenue']
        except ZeroDivisionError:
            mrq_ebit_margin 

        try:
            mrq_net_margin = q_stmt_df.iloc[:,0].loc['Net Income'] / q_stmt_df.iloc[:,0].loc['Total Revenue']
        except ZeroDivisionError:
            mrq_net_margin = np.nan
        
        ttm_roa = sum(q_stmt_df.loc['Net Income'].tolist()[0:4]) / q_stmt_df.iloc[:,0].loc['Total Assets']
        ttm_roe = sum(q_stmt_df.loc['Net Income'].tolist()[0:4]) / q_stmt_df.iloc[:,0].loc['Total Equity']

        #RECENT FIGURES - GROWTH
        try:
            mrq_revenue_growth = (q_stmt_df.loc['Total Revenue'].tolist()[0]/q_stmt_df.loc['Total Revenue'].tolist()[1]) - 1
        except ZeroDivisionError:
            mrq_revenue_growth = np.nan

        try:
            mrq_ebit_growth = (q_stmt_df.loc['EBIT'].tolist()[0]/q_stmt_df.loc['EBIT'].tolist()[1]) - 1
        except ZeroDivisionError:
            mrq_ebit_growth = np.nan

        #RECENT FIGURES - LIQUIDITY
        try:
            mrq_current_ratio = q_stmt_df.iloc[:,0].loc['Total Current Assets'] / q_stmt_df.iloc[:,0].loc['Total Current Liabilities']
        except ZeroDivisionError:
            mrq_current_ratio = np.nan

        try:
            mrq_quick_ratio = (q_stmt_df.iloc[:,0].loc['Total Current Assets'] - q_stmt_df.iloc[:,0].loc['Inventory']) / q_stmt_df.iloc[:,0].loc['Total Current Liabilities']
        except ZeroDivisionError:
            mrq_quick_ratio = np.nan

        try:
            mrq_cash_ratio = q_stmt_df.iloc[:,0].loc['Cash And Cash Equivalents'] / q_stmt_df.iloc[:,0].loc['Total Current Liabilities']
        except ZeroDivisionError:
            mrq_cash_ratio = np.nan


        #RECENT FIGURES - LEVERAGE
        mrq_debt_to_equity = q_stmt_df.iloc[:,0].loc['Total Liabilities'] / q_stmt_df.iloc[:,0].loc['Total Equity']
        mrq_debt_to_assets = q_stmt_df.iloc[:,0].loc['Total Liabilities'] / q_stmt_df.iloc[:,0].loc['Total Assets']
        mrq_interst_coverage_ratio = q_stmt_df.iloc[:,0].loc['EBIT'] / q_stmt_df.iloc[:,0].loc['Interest Expense']

        #RECENT FIGURES - EFFICIENCY
        try:
            ttm_inventory_turnover = sum(q_stmt_df.loc['Cost Of Revenue'].tolist()[0:4]) / ((q_stmt_df.loc['Inventory'].tolist()[0] + q_stmt_df.loc['Inventory'].tolist()[3])/2)
        except ZeroDivisionError:
            ttm_inventory_turnover = np.nan
        
        try:
            ttm_receivables_turnover = sum(q_stmt_df.loc['Total Revenue'].tolist()[0:4]) / ((q_stmt_df.loc['Accounts Receivable'].tolist()[0]+q_stmt_df.loc['Accounts Receivable'].tolist()[3])/2)
        except ZeroDivisionError:
            ttm_receivables_turnover = np.nan
            
        try:
            ttm_payables_turnover = sum(q_stmt_df.loc['Cost Of Revenue'].tolist()[0:4]) / ((q_stmt_df.loc['Accounts Payable'].tolist()[0]+q_stmt_df.loc['Accounts Payable'].tolist()[3])/2)
        except ZeroDivisionError:
            ttm_payables_turnover = np.nan
        ttm_dio = 365 / ttm_inventory_turnover
        ttm_dso = 365 / ttm_receivables_turnover
        ttm_dpo = 365 / ttm_payables_turnover
        ttm_cash_conversion_cycle = ttm_dso + ttm_dio - ttm_dpo

        #RECENT FIGURES - CASHFLOW
        ttm_fcff_DA_WC = sum(q_stmt_df.loc['EBIT'].tolist()[0:4]) * (1 - sum(q_stmt_df.loc['Tax Provision'].tolist()[0:4])/sum(q_stmt_df.loc['Pretax Income'].tolist()[0:4])) + sum(q_stmt_df.loc['Depreciation and Amortization'].tolist()[0:4]) + sum(q_stmt_df.loc['Change In Working Capital'].tolist()[0:4]) + sum(q_stmt_df.loc['Capital Expenditure'].tolist()[0:4])
        ttm_fcff_DA_WC_nonCash = ttm_fcff_DA_WC + sum(q_stmt_df.loc['Other Operating Cash Flow'].tolist()[0:4])
        ttm_fcfe_DA_WC = sum(q_stmt_df.loc['Net Income'].tolist()[0:4]) + sum(q_stmt_df.loc['Depreciation and Amortization'].tolist()[0:4]) + sum(q_stmt_df.loc['Change In Working Capital'].tolist()[0:4]) + sum(q_stmt_df.loc['Capital Expenditure'].tolist()[0:4]) + sum(q_stmt_df.loc['Net Issuance/Payments Of Debt'].tolist()[0:4])
        ttm_fcfe_DA_WC_nonCash = sum(q_stmt_df.loc['Operating Cash Flow'].tolist()[0:4]) + sum(q_stmt_df.loc['Capital Expenditure'].tolist()[0:4]) + sum(q_stmt_df.loc['Net Issuance/Payments Of Debt'].tolist()[0:4])
        #-----------------------------------------------------------------------------------

        base_data = {
            'symbol': yf_history_metadata.get('symbol','-'),
            'name': yf_history_metadata.get('longName','-'),
            'exchange': yf_history_metadata.get('fullExchangeName','-'),
            'currency': yf_history_metadata.get('currency','-'),
            'timezone': yf_history_metadata.get('timezone','-'),
        }

        #JSON FORMATTING ANNUAL FIGURES-----------------------------------------------------
        stats_data = {
            'profitability': {
                'gross margin': stmt_loc['gross margin'].to_dict(),
                'ebit margin': stmt_loc['ebit margin'].to_dict(),
                'net margin': stmt_loc['net margin'].to_dict(),
                'roa': stmt_loc['roa'].to_dict(),
                'roe': stmt_loc['roe'].to_dict()
            },
            'liquidity': {
                'current ratio': stmt_loc['current ratio'].to_dict(),
                'quick ratio': stmt_loc['quick ratio'].to_dict(),
                'cash ratio': stmt_loc['cash ratio'].to_dict()
            },
            'leverage': {
                'debt to equity': stmt_loc['debt to equity'].to_dict(),
                'debt to assets': stmt_loc['debt to assets'].to_dict(),
                'interest coverage ratio': stmt_loc['interest coverage ratio'].to_dict()
            },
            'efficiency': {
                'inventory turnover': stmt_loc['inventory turnover'].to_dict(),
                'receivables turnover': stmt_loc['receivables turnover'].to_dict(),
                'payables turnover': stmt_loc['payables turnover'].to_dict(),
                'dio': stmt_loc['dio'].to_dict(),
                'dso': stmt_loc['dso'].to_dict(),
                'dpo': stmt_loc['dpo'].to_dict(),
                'cash conversion cycle': stmt_loc['cash conversion cycle'].to_dict()
            },
            'valuation': {
                'pe': stmt_loc['pe'].to_dict(),
                'ps': stmt_loc['ps'].to_dict(),
                'pb': stmt_loc['pb'].to_dict(),
                'eps': stmt_loc['eps'].to_dict(),
                'dividend yield': stmt_loc['dividend yield'].to_dict(),
                'dividend payout ratio': stmt_loc['dividend payout ratio'].to_dict(),
                'enterprise value': stmt_loc['enterprise value'].to_dict(),
                'market cap': stmt_loc['market cap'].to_dict(),
                'ev/ebitda': stmt_loc['ev/ebitda'].to_dict(),
                'ev/ebit': stmt_loc['ev/ebit'].to_dict()
            },
            'cash flow': {
                'fcff_DA.WC': stmt_loc['fcff_DA.WC'].to_dict(),
                'fcff_DA.WC.otherNonCash': stmt_loc['fcff_DA.WC.otherNonCash'].to_dict(),
                'fcfe_DA.WC': stmt_loc['fcfe_DA.WC'].to_dict(),
                'fcfe_DA.WC.otherNonCash': stmt_loc['fcfe_DA.WC.otherNonCash'].to_dict()
            },
            'growth': {
                'revenue growth rate': stmt_loc['revenue growth rate'].to_dict(),
                'ebit growth rate': stmt_loc['EBIT growth rate'].to_dict()
            }
        }
        #-----------------------------------------------------------------------------------

        #ADDING ALL RECENT FIGURES TO JSON DATA---------------------------------------------
        p_key = stats_data['profitability']
        li_key = stats_data['liquidity']
        le_key = stats_data['leverage']
        e_key = stats_data['efficiency']
        v_key = stats_data['valuation']
        cf_key = stats_data['cash flow']
        g_key = stats_data['growth']
        
        #Profitability
        p_key['gross margin']['mrq'] = mrq_gross_margin
        p_key['ebit margin']['mrq'] = mrq_ebit_margin
        p_key['net margin']['mrq'] = mrq_net_margin
        p_key['roa']['ttm'] = ttm_roa
        p_key['roe']['ttm'] = ttm_roe
        
        #Liquidity
        li_key['current ratio']['mrq'] = mrq_current_ratio
        li_key['quick ratio']['mrq'] = mrq_quick_ratio
        li_key['cash ratio']['mrq'] = mrq_cash_ratio

        #Leverage
        le_key['debt to equity']['mrq'] = mrq_debt_to_equity
        le_key['debt to assets']['mrq'] = mrq_debt_to_assets
        le_key['interest coverage ratio']['mrq'] = mrq_interst_coverage_ratio

        #Efficiency
        e_key['inventory turnover']['ttm'] = ttm_inventory_turnover
        e_key['receivables turnover']['ttm'] = ttm_receivables_turnover
        e_key['payables turnover']['ttm'] = ttm_payables_turnover
        e_key['dio']['ttm'] = ttm_dio
        e_key['dso']['ttm'] = ttm_dso
        e_key['dpo']['ttm'] = ttm_dpo
        e_key['cash conversion cycle']['ttm'] = ttm_cash_conversion_cycle

        #Valuation
        v_key['pe']['ttm'] = ttm_pe
        v_key['ps']['ttm'] = ttm_ps
        v_key['pb']['mrq'] = mrq_pb
        v_key['eps']['mrq'] = mrq_eps
        v_key['eps']['ttm'] = ttm_eps
        v_key['dividend yield']['ttm'] = ttm_dividend_yield
        v_key['dividend payout ratio']['mrq'] = mrq_dividend_payout_ratio
        v_key['dividend payout ratio']['ttm'] = ttm_dividend_payout_ratio
        v_key['enterprise value']['mrq'] = mrq_enterprise_value
        v_key['market cap']['now'] = market_cap
        v_key['ev/ebitda']['ttm'] = ttm_ev_ebitda
        v_key['ev/ebit']['ttm'] = ttm_ev_ebit

        #Cash Flow
        cf_key['fcff_DA.WC']['ttm'] = ttm_fcff_DA_WC
        cf_key['fcff_DA.WC.otherNonCash']['ttm'] = ttm_fcff_DA_WC_nonCash
        cf_key['fcfe_DA.WC']['ttm'] = ttm_fcfe_DA_WC
        cf_key['fcfe_DA.WC.otherNonCash']['ttm'] = ttm_fcfe_DA_WC_nonCash

        #Growth
        g_key['revenue growth rate']['mrq'] = mrq_revenue_growth
        g_key['ebit growth rate']['mrq'] = mrq_ebit_growth
        #-----------------------------------------------------------------------------------

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            output = stats_data
            return output
        if display == 'pretty':
            def trj(num):
                return '{:.2f}'.format(num).rjust(14)
           
            def icrj(num):
                if pd.isna(num) == True:
                    return '           nan'
                else:
                    return '{:,}'.format(int(num)).rjust(14)
            
            p = stats_data['profitability']
            g = stats_data['growth']
            li = stats_data['liquidity']
            le = stats_data['leverage']
            e = stats_data['efficiency']
            cf = stats_data['cash flow']
            v = stats_data['valuation']

            fy = stmt_df.columns.to_list()

            output = f'''
       Identifier: {base_data['symbol']} - {base_data['name']}
Exchange/Timezone: {base_data['exchange']} - {base_data['timezone']}
         Currency: {base_data['currency']}

                                     LATEST |       {stmt_df.columns[0]} |       {stmt_df.columns[1]} |       {stmt_df.columns[2]} |       {stmt_df.columns[3]} |
VALUATION----------------------------------------------------------------------------------------------------
                   P/E  ttm  {trj(v['pe']['ttm'])} |{trj(v['pe'][fy[0]])} |{trj(v['pe'][fy[1]])} |{trj(v['pe'][fy[2]])} |{trj(v['pe'][fy[3]])} |
                   P/S  ttm  {trj(v['ps']['ttm'])} |{trj(v['ps'][fy[0]])} |{trj(v['ps'][fy[1]])} |{trj(v['ps'][fy[2]])} |{trj(v['ps'][fy[3]])} |
                   P/B  mrq  {trj(v['pb']['mrq'])} |{trj(v['pb'][fy[0]])} |{trj(v['pb'][fy[1]])} |{trj(v['pb'][fy[2]])} |{trj(v['pb'][fy[3]])} |
                   EPS  ttm  {trj(v['eps']['ttm'])} |{trj(v['eps'][fy[0]])} |{trj(v['eps'][fy[1]])} |{trj(v['eps'][fy[2]])} |{trj(v['eps'][fy[3]])} |
        DIVIDEND YIELD  ttm  {trj(v['dividend yield']['ttm']*100)}%|{trj(v['dividend yield'][fy[0]]*100)}%|{trj(v['dividend yield'][fy[1]]*100)}%|{trj(v['dividend yield'][fy[2]]*100)}%|{trj(v['dividend yield'][fy[3]]*100)}%|
 DIVIDEND PAYOUT RATIO  ttm  {trj(v['dividend payout ratio']['ttm']*100)}%|{trj(v['dividend payout ratio'][fy[0]]*100)}%|{trj(v['dividend payout ratio'][fy[1]]*100)}%|{trj(v['dividend payout ratio'][fy[2]]*100)}%|{trj(v['dividend payout ratio'][fy[3]]*100)}%|
      ENTERPRISE VALUE  mrq  {icrj(v['enterprise value']['mrq'])} |{icrj(v['enterprise value'][fy[0]])} |{icrj(v['enterprise value'][fy[1]])} |{icrj(v['enterprise value'][fy[2]])} |{icrj(v['enterprise value'][fy[3]])} |
            MARKET CAP  now  {icrj(v['market cap']['now'])} |{icrj(v['market cap'][fy[0]])} |{icrj(v['market cap'][fy[1]])} |{icrj(v['market cap'][fy[2]])} |{icrj(v['market cap'][fy[3]])} |
             EV/EBITDA  ttm  {trj(v['ev/ebitda']['ttm'])} |{trj(v['ev/ebitda'][fy[0]])} |{trj(v['ev/ebitda'][fy[1]])} |{trj(v['ev/ebitda'][fy[2]])} |{trj(v['ev/ebitda'][fy[3]])} |
               EV/EBIT  ttm  {trj(v['ev/ebit']['ttm'])} |{trj(v['ev/ebit'][fy[0]])} |{trj(v['ev/ebit'][fy[1]])} |{trj(v['ev/ebit'][fy[2]])} |{trj(v['ev/ebit'][fy[3]])} |
                            
PROFITABILITY------------------------------------------------------------------------------------------------
          GROSS MARGIN  mrq  {trj(p['gross margin']['mrq']*100)}%|{trj(p['gross margin'][fy[0]]*100)}%|{trj(p['gross margin'][fy[1]]*100)}%|{trj(p['gross margin'][fy[2]]*100)}%|{trj(p['gross margin'][fy[3]]*100)}%|
           EBIT MARGIN  mrq  {trj(p['ebit margin']['mrq']*100)}%|{trj(p['ebit margin'][fy[0]]*100)}%|{trj(p['ebit margin'][fy[1]]*100)}%|{trj(p['ebit margin'][fy[2]]*100)}%|{trj(p['ebit margin'][fy[3]]*100)}%|
            NET MARGIN  mrq  {trj(p['net margin']['mrq']*100)}%|{trj(p['net margin'][fy[0]]*100)}%|{trj(p['net margin'][fy[1]]*100)}%|{trj(p['net margin'][fy[2]]*100)}%|{trj(p['net margin'][fy[3]]*100)}%|
                   ROA  ttm  {trj(p['roa']['ttm']*100)}%|{trj(p['roa'][fy[0]]*100)}%|{trj(p['roa'][fy[1]]*100)}%|{trj(p['roa'][fy[2]]*100)} |{trj(p['roa'][fy[3]]*100)}%|
                   ROE  ttm  {trj(p['roe']['ttm']*100)}%|{trj(p['roe'][fy[0]]*100)}%|{trj(p['roe'][fy[1]]*100)}%|{trj(p['roe'][fy[2]]*100)} |{trj(p['roe'][fy[3]]*100)}%|

GROWTH-------------------------------------------------------------------------------------------------------
   REVENUE GROWTH RATE  mrq  {trj(g['revenue growth rate']['mrq']*100)}%|{trj(g['revenue growth rate'][fy[0]]*100)}%|{trj(g['revenue growth rate'][fy[1]]*100)}%|{trj(g['revenue growth rate'][fy[2]]*100)}%|{'-'.rjust(14)} |
      EBIT GROWTH RATE  mrq  {trj(g['ebit growth rate']['mrq']*100)}%|{trj(g['ebit growth rate'][fy[0]]*100)}%|{trj(g['ebit growth rate'][fy[1]]*100)}%|{trj(g['ebit growth rate'][fy[2]]*100)}%|{'-'.rjust(14)} |

LIQUIDITY----------------------------------------------------------------------------------------------------
         CURRENT RATIO  mrq  {trj(li['current ratio']['mrq'])} |{trj(li['current ratio'][fy[0]])} |{trj(li['current ratio'][fy[1]])} |{trj(li['current ratio'][fy[2]])} |{trj(li['current ratio'][fy[3]])} |
           QUICK RATIO  mrq  {trj(li['quick ratio']['mrq'])} |{trj(li['quick ratio'][fy[0]])} |{trj(li['quick ratio'][fy[1]])} |{trj(li['quick ratio'][fy[2]])} |{trj(li['quick ratio'][fy[3]])} |
            CASH RATIO  mrq  {trj(li['cash ratio']['mrq'])} |{trj(li['cash ratio'][fy[0]])} |{trj(li['cash ratio'][fy[1]])} |{trj(li['cash ratio'][fy[2]])} |{trj(li['cash ratio'][fy[3]])} |

LEVERAGE-----------------------------------------------------------------------------------------------------
        DEBT TO EQUITY  mrq  {trj(le['debt to equity']['mrq'])} |{trj(le['debt to equity'][fy[0]])} |{trj(le['debt to equity'][fy[1]])} |{trj(le['debt to equity'][fy[2]])} |{trj(le['debt to equity'][fy[3]])} |
        DEBT TO ASSETS  mrq  {trj(le['debt to assets']['mrq'])} |{trj(le['debt to assets'][fy[0]])} |{trj(le['debt to assets'][fy[1]])} |{trj(le['debt to assets'][fy[2]])} |{trj(le['debt to assets'][fy[3]])} |
INTERST COVERAGE RATIO  mrq  {trj(le['interest coverage ratio']['mrq'])} |{trj(le['interest coverage ratio'][fy[0]])} |{trj(le['interest coverage ratio'][fy[1]])} |{trj(le['interest coverage ratio'][fy[2]])} |{trj(le['interest coverage ratio'][fy[3]])} |

EFFICIENCY---------------------------------------------------------------------------------------------------
    INVENTORY TURNOVER  ttm  {trj(e['inventory turnover']['ttm'])} |{trj(e['inventory turnover'][fy[0]])} |{trj(e['inventory turnover'][fy[1]])} |{trj(e['inventory turnover'][fy[2]])} |{'-'.rjust(14)} |
  RECEIVABLES TURNOVER  ttm  {trj(e['receivables turnover']['ttm'])} |{trj(e['receivables turnover'][fy[0]])} |{trj(e['receivables turnover'][fy[1]])} |{trj(e['receivables turnover'][fy[2]])} |{'-'.rjust(14)} |
     PAYABLES TURNOVER  ttm  {trj(e['payables turnover']['ttm'])} |{trj(e['payables turnover'][fy[0]])} |{trj(e['payables turnover'][fy[1]])} |{trj(e['payables turnover'][fy[2]])} |{'-'.rjust(14)} |
                   DIO  ttm  {trj(e['dio']['ttm'])} |{trj(e['dio'][fy[0]])} |{trj(e['dio'][fy[1]])} |{trj(e['dio'][fy[2]])} |{'-'.rjust(14)} |
                   DSO  ttm  {trj(e['dso']['ttm'])} |{trj(e['dso'][fy[0]])} |{trj(e['dso'][fy[1]])} |{trj(e['dso'][fy[2]])} |{'-'.rjust(14)} |
                   DPO  ttm  {trj(e['dpo']['ttm'])} |{trj(e['dpo'][fy[0]])} |{trj(e['dpo'][fy[1]])} |{trj(e['dpo'][fy[2]])} |{'-'.rjust(14)} |
 CASH CONVERSION CYCLE  ttm  {trj(e['cash conversion cycle']['ttm'])} |{trj(e['cash conversion cycle'][fy[0]])} |{trj(e['cash conversion cycle'][fy[1]])} |{trj(e['cash conversion cycle'][fy[2]])} |{'-'.rjust(14)} |

CASH FLOW----------------------------------------------------------------------------------------------------
            FCFF.DA.WC  ttm  {icrj(cf['fcff_DA.WC']['ttm'])} |{icrj(cf['fcff_DA.WC'][fy[0]])} |{icrj(cf['fcff_DA.WC'][fy[1]])} |{icrj(cf['fcff_DA.WC'][fy[2]])} |{icrj(cf['fcff_DA.WC'][fy[3]])} |
    FCFF.DA.WC.NonCash  ttm  {icrj(cf['fcff_DA.WC.otherNonCash']['ttm'])} |{icrj(cf['fcff_DA.WC.otherNonCash'][fy[0]])} |{icrj(cf['fcff_DA.WC.otherNonCash'][fy[1]])} |{icrj(cf['fcff_DA.WC.otherNonCash'][fy[2]])} |{icrj(cf['fcff_DA.WC.otherNonCash'][fy[3]])} |
            FCFE.DA.WC  ttm  {icrj(cf['fcfe_DA.WC']['ttm'])} |{icrj(cf['fcfe_DA.WC'][fy[0]])} |{icrj(cf['fcfe_DA.WC'][fy[1]])} |{icrj(cf['fcfe_DA.WC'][fy[2]])} |{icrj(cf['fcfe_DA.WC'][fy[3]])} |
    FCFE.DA.WC.NonCash  ttm  {icrj(cf['fcfe_DA.WC.otherNonCash']['ttm'])} |{icrj(cf['fcfe_DA.WC.otherNonCash'][fy[0]])} |{icrj(cf['fcfe_DA.WC.otherNonCash'][fy[1]])} |{icrj(cf['fcfe_DA.WC.otherNonCash'][fy[2]])} |{icrj(cf['fcfe_DA.WC.otherNonCash'][fy[3]])} |
'''
        
            print(output)
#------------------------------------------------------------------------------------------
    def eps(self, display: str = 'json'): 
        valid_params = {'valid_display': ['json', 'table'],}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
    
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        yf_eps_df = yf.Ticker(self.ticker).get_earnings_dates()
        #----------------------------------------------------------------------------------

        yf_eps_df.index = yf_eps_df.index.normalize().tz_localize(None)
        del yf_eps_df['Event Type']
        del yf_eps_df['Surprise(%)']
        yf_eps_df = yf_eps_df.rename(columns = {
            'EPS Estimate': f'{self.ticker} EPS Estimate',
            'Reported EPS': f'{self.ticker} EPS Actual'
        })
        yf_eps_df[f'{self.ticker} EPS Surprise(%)'] = round(((yf_eps_df[f'{self.ticker} EPS Actual']/yf_eps_df[f'{self.ticker} EPS Estimate']) - 1) * 100, 2)
        yf_eps_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            yf_eps_df.index = yf_eps_df.index.strftime('%Y-%m-%d')

            yf_eps_dictlist = []
            for index, row in yf_eps_df.iterrows():
                a = {'Date': index,
                    f'{self.ticker} EPS Estimate': float(row[f'{self.ticker} EPS Estimate']) if isinstance(row[f'{self.ticker} EPS Estimate'], np.float64) else row[f'{self.ticker} EPS Estimate'],
                    f'{self.ticker} EPS Actual': float(row[f'{self.ticker} EPS Actual']) if isinstance(row[f'{self.ticker} EPS Actual'], np.float64) else row[f'{self.ticker} EPS Estimate'],
                    f'{self.ticker} EPS Surprise(%)': float(row[f'{self.ticker} EPS Surprise(%)']) if isinstance(row[f'{self.ticker} EPS Surprise(%)'], np.float64) else row[f'{self.ticker} EPS Estimate']}
                yf_eps_dictlist.append(a)
            output = yf_eps_dictlist
            return output
        elif display == 'table':
            output = yf_eps_df
            return output
#------------------------------------------------------------------------------------------