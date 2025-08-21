from finflux.base_var import Config

import yfinance as yf # type: ignore
import numpy as np # type: ignore
import requests # type: ignore
import pandas as pd # type: ignore
from datetime import timedelta
from datetime import date
from yfinance import EquityQuery

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

#------------------------------------------------------------------------------------------
class top:
#------------------------------------------------------------------------------------------
    def gainer(self, display: str = 'json', sector: str = 'all'): 
        valid_params = {'valid_display': ['json', 'table'],
                        'valid_sector': ['all', 'basic materials', 'communication services', 'consumer cyclical', ' consumer defensive', 'energy', 'financial services', 'healthcare', 'industrials', 'real estate', 'technology', 'utilities']}
        
        params = {'display': display,
                  'sector': sector}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        if sector == 'all':
            q = EquityQuery('and', [
                    EquityQuery('gt', ['percentchange', 0.1]),
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gte', ['intradaymarketcap', 300000000]),
                    EquityQuery('gte', ['intradayprice', 5]),
                    EquityQuery('gte', ['dayvolume', 500000])
                ])
        elif sector != 'all':
            q = EquityQuery('and', [
                    EquityQuery('eq', ['sector', sector.title()]),
                    EquityQuery('gt', ['percentchange', 0.1]),
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gte', ['intradaymarketcap', 300000000]),
                    EquityQuery('gte', ['intradayprice', 5]),
                    EquityQuery('gte', ['dayvolume', 500000])
                ])
        quotes = yf.screen(q, sortField = 'percentchange', sortAsc = False, size=10)['quotes']
        #----------------------------------------------------------------------------------

        #JSON FORMAT DATA
        quote_data = {}
        for quote in quotes:
            quote_info = yf.Ticker(quote['symbol']).get_info()

            quote_data[quote['symbol']] = {
                'name': quote['longName'] if 'longName' in quote.keys() else '-',
                'price change': quote['regularMarketChange'],
                'percent change': quote['regularMarketChangePercent'],
                'volume': quote['regularMarketVolume'],
                'sector': quote_info.get('sector', '-'),
                'industry': quote_info.get('industry', '-')
            }

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            output = quote_data
        if display == 'table':
            df = pd.DataFrame.from_dict(quote_data, orient='index')
            df['price change'] = df['price change'].round(2)
            df['percent change'] = df['percent change'].round(2)
            df['volume'] = (df['volume']//1000).apply(lambda x: f"{x:,}")
            df.columns = ['Name', 'Price Change', 'Percent Change', 'Volume (in Thousands)', 'Sector', 'Industry']

            output = df
            
        return output
#------------------------------------------------------------------------------------------
    def loser(self, display: str = 'json', sector: str = 'all'): 
        valid_params = {'valid_display': ['json', 'table'],
                        'valid_sector': ['all', 'basic materials', 'communication services', 'consumer cyclical', ' consumer defensive', 'energy', 'financial services', 'healthcare', 'industrials', 'real estate', 'technology', 'utilities']}
        
        params = {'display': display,
                  'sector': sector}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        if sector == 'all':
            q = EquityQuery('and', [
                    EquityQuery('lt', ['percentchange', -0.1]),
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gte', ['intradaymarketcap', 300000000]),
                    EquityQuery('gte', ['intradayprice', 5]),
                    EquityQuery('gte', ['dayvolume', 500000])
                ])
        elif sector != 'all':
            q = EquityQuery('and', [
                    EquityQuery('eq', ['sector', sector.title()]),
                    EquityQuery('lt', ['percentchange', -0.1]),
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gte', ['intradaymarketcap', 300000000]),
                    EquityQuery('gte', ['intradayprice', 5]),
                    EquityQuery('gte', ['dayvolume', 500000])
                ])
        quotes = yf.screen(q, sortField = 'percentchange', sortAsc = True, size=10)['quotes']
        #----------------------------------------------------------------------------------

        #JSON FORMAT DATA
        quote_data = {}
        for quote in quotes:
            quote_info = yf.Ticker(quote['symbol']).get_info()

            quote_data[quote['symbol']] = {
                'name': quote['longName'] if 'longName' in quote.keys() else '-',
                'price change': quote['regularMarketChange'],
                'percent change': quote['regularMarketChangePercent'],
                'volume': quote['regularMarketVolume'],
                'sector': quote_info.get('sector', '-'),
                'industry': quote_info.get('industry', '-')
            }

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            output = quote_data
        if display == 'table':
            df = pd.DataFrame.from_dict(quote_data, orient='index')
            df['price change'] = df['price change'].round(2)
            df['percent change'] = df['percent change'].round(2)
            df['volume'] = (df['volume']//1000).apply(lambda x: f"{x:,}")
            df.columns = ['Name', 'Price Change', 'Percent Change', 'Volume (in Thousands)', 'Sector', 'Industry']

            output = df
            
        return output
#------------------------------------------------------------------------------------------
    def active(self, display: str = 'json', sector: str = 'all'): 
        valid_params = {'valid_display': ['json', 'table'],
                        'valid_sector': ['all', 'basic materials', 'communication services', 'consumer cyclical', ' consumer defensive', 'energy', 'financial services', 'healthcare', 'industrials', 'real estate', 'technology', 'utilities']}
        
        params = {'display': display,
                  'sector': sector}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        if sector == 'all':
            q = EquityQuery('and', [
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gte', ['intradaymarketcap', 300000000]),
                    EquityQuery('gte', ['dayvolume', 500000])
                ])
        elif sector != 'all':
            q = EquityQuery('and', [
                    EquityQuery('eq', ['sector', sector.title()]),
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gte', ['intradaymarketcap', 300000000]),
                    EquityQuery('gte', ['dayvolume', 500000])
                ])
        quotes = yf.screen(q, sortField = 'dayvolume', sortAsc = False, size=10)['quotes']
        #----------------------------------------------------------------------------------

        #JSON FORMAT DATA
        quote_data = {}
        for quote in quotes:
            quote_info = yf.Ticker(quote['symbol']).get_info()

            quote_data[quote['symbol']] = {
                'name': quote['longName'] if 'longName' in quote.keys() else '-',
                'price change': quote['regularMarketChange'],
                'percent change': quote['regularMarketChangePercent'],
                'volume': quote['regularMarketVolume'],
                'sector': quote_info.get('sector', '-'),
                'industry': quote_info.get('industry', '-')
            }

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            output = quote_data
        if display == 'table':
            df = pd.DataFrame.from_dict(quote_data, orient='index')
            df['price change'] = df['price change'].round(2)
            df['percent change'] = df['percent change'].round(2)
            df['volume'] = (df['volume']//1000).apply(lambda x: f"{x:,}")
            df.columns = ['Name', 'Price Change', 'Percent Change', 'Volume (in Thousands)', 'Sector', 'Industry']

            output = df
            
        return output
#------------------------------------------------------------------------------------------
    def cap(self, display: str = 'json', sector: str = 'all'): 
        valid_params = {'valid_display': ['json', 'table'],
                        'valid_sector': ['all', 'basic materials', 'communication services', 'consumer cyclical', ' consumer defensive', 'energy', 'financial services', 'healthcare', 'industrials', 'real estate', 'technology', 'utilities']}
        
        params = {'display': display,
                  'sector': sector}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        if sector == 'all':
            q = EquityQuery('and', [
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gt', ['intradaymarketcap', 1000000000])
                ])
        elif sector != 'all':
            q = EquityQuery('and', [
                    EquityQuery('eq', ['sector', sector.title()]),
                    EquityQuery('is-in', ['exchange', 'NMS', 'NYQ', 'NGM', 'NCM']),
                    EquityQuery('gte', ['intradaymarketcap', 1000000000])
                ])
        quotes = yf.screen(q, sortField = 'intradaymarketcap', sortAsc = False, size=10)['quotes']
        #----------------------------------------------------------------------------------

        #JSON FORMAT DATA
        quote_data = {}
        for quote in quotes:
            quote_info = yf.Ticker(quote['symbol']).get_info()

            quote_data[quote['symbol']] = {
                'name': quote['longName'] if 'longName' in quote.keys() else '-',
                'price change': quote['regularMarketChange'],
                'percent change': quote['regularMarketChangePercent'],
                'volume': quote['regularMarketVolume'],
                'market cap': quote['marketCap'],
                'sector': quote_info.get('sector', '-'),
                'industry': quote_info.get('industry', '-')
            }

        #PARAMETER - DISPLAY ==============================================================
        if display == 'json':
            output = quote_data
        if display == 'table':
            df = pd.DataFrame.from_dict(quote_data, orient='index')
            df['price change'] = df['price change'].round(2)
            df['percent change'] = df['percent change'].round(2)
            df['volume'] = (df['volume']//1000).apply(lambda x: f"{x:,}")
            df['market cap'] = (df['market cap']//1000000).apply(lambda x: f"{x:,}")
            df.columns = ['Name', 'Price Change', 'Percent Change', 'Volume (in Thousands)', 'Market Cap (in Millions)', 'Sector', 'Industry']

            output = df
            
        return output
#------------------------------------------------------------------------------------------