from finflux.base_var import Config

import yfinance as yf # type: ignore
import numpy as np # type: ignore
import requests # type: ignore
import pandas as pd # type: ignore
from datetime import timedelta, datetime, date
import json
from dateutil.relativedelta import relativedelta

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
class indicator:
#------------------------------------------------------------------------------------------
    def gdp(self, display: str = 'table', type: str = 'n', period: str = '5y', figure: str = 'yoy'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_type': ['n', 'r', 'n_pc', 'r_pc', 'd'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'max', 'ytd'],
                        'valid_figure': ['raw', 'yoy', 'pop']}
        
        params = {'display': display,
                  'type': type,
                  'period': period,
                  'figure': figure}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        
        identifiers = {
            'n' : ['T10105', 'A191RC', 'Nominal GDP (in USD millions)'],
            'r' : ['T10106', 'A191RX', 'Real GDP (in USD millions)'],
            'n_pc' : ['T70100', 'A939RC', 'Nominal GDP per Capita (in USD)'],
            'r_pc' : ['T70100', 'A939RX', 'Real GDP per Capita (in USD)'],
            'd' : ['T10109', 'A191RD', 'GDP Deflator (index)'],
        }

        if Config.bea_apikey is None:
            raise MissingConfigObject('Missing bea_apikey. Please set your BEA api key using the set_config() function.')

        #RAW DATA/OBSERVATION-----------------------------------------------------------BEA
        url = f'{Config.bea_baseurl}/?&UserID={Config.bea_apikey}' + '&method=GetData' + '&datasetname=NIPA' + f'&TableName={identifiers[type][0]}' + '&Frequency=Q' + '&Year=X'
        response = requests.get(url).json()
        #----------------------------------------------------------------------------------

        data_list = response['BEAAPI']['Results']['Data']

        quarter_to_month = {
                    'Q1': '-03-01',
                    'Q2': '-06-01',
                    'Q3': '-09-01',
                    'Q4': '-12-01',
                }

        data_dict = {}
        for i in data_list:
            if i['SeriesCode'] == identifiers[type][1]:
                data_value = i['DataValue']
                data_value = data_value.replace(',','')
                date = i['TimePeriod'][0:4] + quarter_to_month[i['TimePeriod'][4:6]]
                data_dict[date] = int(data_value) if type!='d' else float(data_value)

        data_df = pd.DataFrame.from_dict(data_dict, orient='index', columns=[f'{identifiers[type][2]}'])

        #PARAMETER - PERIOD ================================================================
        if figure == 'raw':
            pass
        elif figure == 'yoy':
            data_df[f'{identifiers[type][2].split(" (")[0]} YoY % Change'] = (((data_df[f'{identifiers[type][2]}']/data_df[f'{identifiers[type][2]}'].shift(4)) - 1) * 100).round(2)
            del data_df[f'{identifiers[type][2]}']
            data_df = data_df.drop(data_df.index[0:4])
        elif figure == 'pop':
            data_df[f'{identifiers[type][2].split(" (")[0]} QoQ % Change'] = (((data_df[f'{identifiers[type][2]}']/data_df[f'{identifiers[type][2]}'].shift(1)) - 1) * 100).round(2)
            del data_df[f'{identifiers[type][2]}']
            data_df = data_df.drop(data_df.index[0:1])

        #PARAMETER - PERIOD ===============================================================
        period_to_df = {
            '1y': -5,
            '2y': -9,
            '5y': -21,
            '10y': -41,
        }    

        if period == 'max':
            data_df = data_df
        elif period == 'ytd':
            current_year = str(datetime.now().year)
            data_df = data_df[data_df.index.str[0:4] == current_year]
        elif period != 'max' or period != 'ytd':
            data_df = data_df.iloc[period_to_df[period]:]
        
        data_df.index = pd.to_datetime(data_df.index) # converting all row indices to datetime objects
        data_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')
            
            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def price_index(self, display: str = 'table', type: str = 'c', period: str = '5y', figure: str = 'yoy'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_type': ['c', 'p', 'cc', 'cp'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'max', 'ytd'],
                        'valid_figure': ['raw', 'yoy', 'pop']}
        
        params = {'display': display,
                  'type': type,
                  'period': period,
                  'figure': figure}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        identifiers = {
            'c': ['CUUR0000SA0', 'CPI (Index)'], #1913
            'p': ['WPUFD4', 'PPI (Index)'], #2009
            'cc': ['CUUR0000SA0L1E', 'Core CPI (Index)'], #1957
            'cp': ['WPUFD49104', 'Core PPI (Index)'] #2010
        }

        if Config.bls_apikey is None:
            raise MissingConfigObject('Missing bls_apikey. Please set your BLS api key using the set_config() function.')

        #RAW DATA/OBSERVATION-----------------------------------------------------------BLS
        if period != 'max':
            end_year = str(datetime.now().year)
            start_year = str(datetime.now().year - 11)
            
            headers = {'Content-type': 'application/json'}
            data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":start_year, "endyear":end_year, 'registrationkey':Config.bls_apikey})
            response = requests.post(Config.bls_baseurl, data=data, headers=headers).json()

            data_list = response['Results']['series'][0]['data'][::-1]

        elif period == 'max':
            end_year = str(datetime.now().year)
            headers = {'Content-type': 'application/json'}

            def dlist(response):
                return response['Results']['series'][0]['data']

            data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'2011', "endyear":end_year, 'registrationkey':Config.bls_apikey})
            response_1 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
            data_list = dlist(response_1)

            data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1991', "endyear":'2010', 'registrationkey':Config.bls_apikey})
            response_2 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
            data_list.extend(dlist(response_2))

            if type not in ('p', 'cp'):
                data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1971', "endyear":'1990', 'registrationkey':Config.bls_apikey})
                response_3 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                data_list.extend(dlist(response_3))

                data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1951', "endyear":'1970', 'registrationkey':Config.bls_apikey})
                response_4 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                data_list.extend(dlist(response_4))

                if type not in ('cc'):
                    data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1931', "endyear":'1950', 'registrationkey':Config.bls_apikey})
                    response_5 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                    data_list.extend(dlist(response_5))

                    data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1911', "endyear":'1930', 'registrationkey':Config.bls_apikey})
                    response_6 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                    data_list.extend(dlist(response_6))
            
            data_list = data_list[::-1]

        #----------------------------------------------------------------------------------

        month_to_month = {
                    'M01': '-01-01',
                    'M02': '-02-01',
                    'M03': '-03-01',
                    'M04': '-04-01',
                    'M05': '-05-01',
                    'M06': '-06-01',
                    'M07': '-07-01',
                    'M08': '-08-01',
                    'M09': '-09-01',
                    'M10': '-10-01',
                    'M11': '-11-01',
                    'M12': '-12-01',
                }

        data_dict = {}
        for i in data_list:
            date = i['year'] + month_to_month[i['period']]
            data_dict[date] = float(i['value'])

        data_df = pd.DataFrame.from_dict(data_dict, orient='index', columns=[f'{identifiers[type][1]}'])

        #PARAMETER - FIGURE ================================================================
        if figure == 'raw':
            pass
        elif figure == 'yoy':
            data_df[f'{identifiers[type][1].split(' (')[0]} YoY % Change'] = (((data_df[f'{identifiers[type][1]}']/data_df[f'{identifiers[type][1]}'].shift(12)) - 1) * 100).round(2)
            del data_df[f'{identifiers[type][1]}']
            data_df = data_df.drop(data_df.index[0:12])
        elif figure == 'pop':
            data_df[f'{identifiers[type][1].split(' (')[0]} MoM % Change'] = (((data_df[f'{identifiers[type][1]}']/data_df[f'{identifiers[type][1]}'].shift(1)) - 1) * 100).round(2)
            del data_df[f'{identifiers[type][1]}']
            data_df = data_df.drop(data_df.index[0:1])

        #PARAMETER - PERIOD ================================================================
        period_to_df = {
            '1y': -13,
            '2y': -25,
            '5y': -61,
            '10y': -121
        }      

        if period == 'max':
            data_df = data_df
        elif period == 'ytd':
            current_year = str(datetime.now().year)
            data_df = data_df[data_df.index.str[0:4] == current_year]
        elif period != 'max' or period != 'ytd':
            data_df = data_df.iloc[period_to_df[period]:]
        
        data_df.index = pd.to_datetime(data_df.index) # converting all row indices to datetime objects
        data_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def pce(self, display: str = 'table', type: str = 'raw', period: str = '5y', figure: str = 'yoy'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_type': ['raw', 'core'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'max', 'ytd'],
                        'valid_figure': ['raw', 'yoy', 'pop']}
        
        params = {'display': display,
                  'type': type,
                  'period': period,
                  'figure': figure}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        identifiers = {
            'raw' : ['T20804', 'DPCERG', 'PCE (index)'],
            'core' : ['T20804', 'DPCCRG', 'Core PCE (index)']
        }

        if Config.bea_apikey is None:
            raise MissingConfigObject('Missing bea_apikey. Please set your BEA api key using the set_config() function.')

        #RAW DATA/OBSERVATION-----------------------------------------------------------BEA
        url = f'{Config.bea_baseurl}/?&UserID={Config.bea_apikey}' + '&method=GetData' + '&datasetname=NIPA' + f'&TableName={identifiers[type][0]}' + '&Frequency=M' + '&Year=X'
        response = requests.get(url).json()
        #----------------------------------------------------------------------------------

        data_list = response['BEAAPI']['Results']['Data']

        month_to_month = {
                    'M01': '-01-01',
                    'M02': '-02-01',
                    'M03': '-03-01',
                    'M04': '-04-01',
                    'M05': '-05-01',
                    'M06': '-06-01',
                    'M07': '-07-01',
                    'M08': '-08-01',
                    'M09': '-09-01',
                    'M10': '-10-01',
                    'M11': '-11-01',
                    'M12': '-12-01',
                }

        data_dict = {}
        for i in data_list:
            if i['SeriesCode'] == identifiers[type][1]:
                data_value = i['DataValue']
                data_value = data_value.replace(',','')
                date = i['TimePeriod'][0:4] + month_to_month[i['TimePeriod'][4:7]]
                data_dict[date] = float(data_value)

        data_df = pd.DataFrame.from_dict(data_dict, orient='index', columns=[f'{identifiers[type][2]}'])

        #PARAMETER - PERIOD ================================================================
        if figure == 'raw':
            pass
        elif figure == 'yoy':
            data_df[f'{identifiers[type][2].split(" (")[0]} YoY % Change'] = (((data_df[f'{identifiers[type][2]}']/data_df[f'{identifiers[type][2]}'].shift(12)) - 1) * 100).round(2)
            del data_df[f'{identifiers[type][2]}']
            data_df = data_df.drop(data_df.index[0:12])
        elif figure == 'pop':
            data_df[f'{identifiers[type][2].split(" (")[0]} MoM % Change'] = (((data_df[f'{identifiers[type][2]}']/data_df[f'{identifiers[type][2]}'].shift(1)) - 1) * 100).round(2)
            del data_df[f'{identifiers[type][2]}']
            data_df = data_df.drop(data_df.index[0:1])

        #PARAMETER - PERIOD ================================================================
        period_to_df = {
            '1y': -13,
            '2y': -25,
            '5y': -61,
            '10y': -121,
        }    

        if period == 'max':
            data_df = data_df
        elif period == 'ytd':
            current_year = str(datetime.now().year)
            data_df = data_df[data_df.index.str[0:4] == current_year]
        elif period != 'max' or period != 'ytd':
            data_df = data_df.iloc[period_to_df[period]:]

        data_df.index = pd.to_datetime(data_df.index) # converting all row indices to datetime objects
        data_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def unemployment(self, display: str = 'table', type: str = 'U-3', period: str = '5y'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_type': ['U-3', 'U-6', 'g=male', 'g=female', 'r=white', 'r=black', 'r=asian', 'r=hispanic', 'e<hs', 'e=hs', 'e<bach', 'e>=bach'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'ytd', 'max']}
        
        params = {'display': display,
                  'type': type,
                  'period': period}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        identifiers = {
            'U-3': ['LNS14000000', 'UNRATE [U-3]'], #1943
            'U-6': ['LNS13327709', 'UNRATE [U-6]'], #1994
            'g=male': ['LNS14000025', 'UNRATE [Male]'], #1948
            'g=female': ['LNS14000026', 'UNRATE [Female]'], #1948
            'r=white': ['LNS14000003', 'UNRATE [White]'], #1954
            'r=black': ['LNS14000006', 'UNRATE [Black]'], #1972
            'r=asian': ['LNS14032183', 'UNRATE [Asian]'], #2003
            'r=hispanic': ['LNS14000009', 'UNRATE [Hispanic]'], #1973
            'e<hs': ['LNS14027659', 'UNRATE [<High School]'], #1992
            'e=hs': ['LNS14027660', 'UNRATE [=High School]'], #1992
            'e<bach': ['LNS14027689', 'UNRATE [<Bachelor]'], #1992
            'e>=bach': ['LNS14027662', 'UNRATE [>=Bachelor]'], #1992
        }

        if Config.bls_apikey is None:
            raise MissingConfigObject('Missing bls_apikey. Please set your BLS api key using the set_config() function.')

        #RAW DATA/OBSERVATION-----------------------------------------------------------BLS
        if period != 'max':
            end_year = str(datetime.now().year)
            start_year = str(datetime.now().year - 11)
            
            headers = {'Content-type': 'application/json'}
            data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":start_year, "endyear":end_year, 'registrationkey':Config.bls_apikey})
            response = requests.post(Config.bls_baseurl, data=data, headers=headers).json()

            data_list = response['Results']['series'][0]['data'][::-1]

        elif period == 'max':
            end_year = str(datetime.now().year)
            headers = {'Content-type': 'application/json'}

            def dlist(response):
                return response['Results']['series'][0]['data']

            data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'2021', "endyear":end_year, 'registrationkey':Config.bls_apikey})
            response_1 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
            data_list = dlist(response_1)

            data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'2001', "endyear":'2020', 'registrationkey':Config.bls_apikey})
            response_2 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
            data_list.extend(dlist(response_2))

            if type not in ('r=asian'):
                data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1981', "endyear":'2000', 'registrationkey':Config.bls_apikey})
                response_3 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                data_list.extend(dlist(response_3))

                if type not in ('U-6', 'e<hs', 'e=hs', 'e<bach', 'e>=bach'):
                    data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1961', "endyear":'1980', 'registrationkey':Config.bls_apikey})
                    response_4 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                    data_list.extend(dlist(response_4))

                    if type not in ('r=black', 'r=hispanic'):
                        data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1941', "endyear":'1960', 'registrationkey':Config.bls_apikey})
                        response_5 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                        data_list.extend(dlist(response_5))
            
            data_list = data_list[::-1]
        #----------------------------------------------------------------------------------

        month_to_month = {
                    'M01': '-01-01',
                    'M02': '-02-01',
                    'M03': '-03-01',
                    'M04': '-04-01',
                    'M05': '-05-01',
                    'M06': '-06-01',
                    'M07': '-07-01',
                    'M08': '-08-01',
                    'M09': '-09-01',
                    'M10': '-10-01',
                    'M11': '-11-01',
                    'M12': '-12-01',
                }

        data_dict = {}
        for i in data_list:
            date = i['year'] + month_to_month[i['period']]
            data_dict[date] = float(i['value'])

        data_df = pd.DataFrame.from_dict(data_dict, orient='index', columns=[f'{identifiers[type][1]}'])

        #PARAMETER - PERIOD ================================================================
        period_to_df = {
            '1y': -13,
            '2y': -25,
            '5y': -61,
            '10y': -121
        }      

        if period == 'max':
            data_df = data_df
        elif period == 'ytd':
            current_year = str(datetime.now().year)
            data_df = data_df[data_df.index.str[0:4] == current_year]
        elif period != 'max' or period != 'ytd':
            data_df = data_df.iloc[period_to_df[period]:]
        
        data_df.index = pd.to_datetime(data_df.index) # converting all row indices to datetime objects
        data_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def labor(self, display: str = 'table', type: str = 'participation', period: str = '5y'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_type': ['participation', 'payroll', 'quits', 'openings', 'earnings', 'claims'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'max', 'ytd']}
        
        params = {'display': display,
                  'type': type,
                  'period': period}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        identifiers = {
            'participation': ['LNS11300000', 'Labor Force Participation Rate', 0], #1948 M
            'payroll': ['CES0000000001', 'Nonfarm Payrolls', 0], #1939 M (this provides different figures from the one provided in the Employment Situation Summary which is the more widely used source for payroll data)
            'quits': ['JTS000000000000000QUR', 'Quits Rate', 0], #2001 M
            'openings': ['JTS000000000000000JOR', 'Job Openings Rate', 0], #2001 M
            'earnings': ['CES0500000003', 'Average Hourly Earnings', 0], #2006 M
            'claims': ['ICSA', 'Initial Claims', 1], # FRED (not BLS) 1967 W
        }

        if type != 'claims':
            if Config.bls_apikey is None:
                raise MissingConfigObject('Missing bls_apikey. Please set your BLS api key using the set_config() function.')
        
        elif type == 'claims':
            if Config.fred_apikey is None:
                raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')

        #RAW DATA/OBSERVATION-----------------------------------------------------------BLS
        if type != 'claims':
            if period != 'max':
                end_year = str(datetime.now().year)
                start_year = str(datetime.now().year - 11)
                
                headers = {'Content-type': 'application/json'}
                data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":start_year, "endyear":end_year, 'registrationkey':Config.bls_apikey})
                response = requests.post(Config.bls_baseurl, data=data, headers=headers).json()

                data_list = response['Results']['series'][0]['data'][::-1]

            elif period == 'max':
                end_year = str(datetime.now().year)
                headers = {'Content-type': 'application/json'}

                def dlist(response):
                    return response['Results']['series'][0]['data']

                data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'2011', "endyear":end_year, 'registrationkey':Config.bls_apikey})
                response_1 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                data_list = dlist(response_1)

                data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1991', "endyear":'2010', 'registrationkey':Config.bls_apikey})
                response_2 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                data_list.extend(dlist(response_2))

                if type not in ('quits', 'openings', 'earnings'):
                    data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1971', "endyear":'1990', 'registrationkey':Config.bls_apikey})
                    response_3 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                    data_list.extend(dlist(response_3))

                    data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1951', "endyear":'1970', 'registrationkey':Config.bls_apikey})
                    response_4 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                    data_list.extend(dlist(response_4))

                    data = json.dumps({"seriesid": [identifiers[type][0]],"startyear":'1931', "endyear":'1950', 'registrationkey':Config.bls_apikey})
                    response_5 = requests.post(Config.bls_baseurl, data=data, headers=headers).json()
                    data_list.extend(dlist(response_5))
                
                data_list = data_list[::-1]

        if type == 'claims':
            FRED_url = f'https://api.stlouisfed.org/fred/series/observations?series_id={identifiers[type][0]}&api_key={Config.fred_apikey}&file_type=json'
            data_list = requests.get(FRED_url).json()['observations']
        #----------------------------------------------------------------------------------

        month_to_month = {
                    'M01': '-01-01',
                    'M02': '-02-01',
                    'M03': '-03-01',
                    'M04': '-04-01',
                    'M05': '-05-01',
                    'M06': '-06-01',
                    'M07': '-07-01',
                    'M08': '-08-01',
                    'M09': '-09-01',
                    'M10': '-10-01',
                    'M11': '-11-01',
                    'M12': '-12-01',
                }

        data_dict = {}
        if type != 'claims':
            for i in data_list:
                date = i['year'] + month_to_month[i['period']]
                data_dict[date] = float(i['value'])

        elif type == 'claims':
            for i in data_list:
                data_dict[i['date']] = int(i['value'])

        data_df = pd.DataFrame.from_dict(data_dict, orient='index', columns=[f'{identifiers[type][1]}'])

        #PARAMETER - PERIOD ================================================================
        period_to_df = {
            '1y': [-13,-53],
            '2y': [-25,-105],
            '5y': [-61,-261],
            '10y': [-121,-522]
        }      

        if period == 'max':
            data_df = data_df
        elif period == 'ytd':
            current_year = str(datetime.now().year)
            data_df = data_df[data_df.index.str[0:4] == current_year]
        elif period != 'max' or period != 'ytd':
            data_df = data_df.iloc[period_to_df[period][identifiers[type][2]]:]
        
        data_df.index = pd.to_datetime(data_df.index) # converting all row indices to datetime objects
        data_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def sentiment(self, display: str = 'table', type: str = 'c_mcsi', period: str = '5y'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_type': ['c_mcsi', 'c_mcie', 'c_oecd', 'b_oecd'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'max', 'ytd']}
        
        params = {'display': display,
                  'type': type,
                  'period': period}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        FRED_IDs = {
            'c_mcsi': ['UMCSENT', 'Michigan Consumer Sentiment Index'], #UMich consumer sentiment
            'c_mcie': ['MICH', 'Michigan Consumer Inflation Expectations'], #UMich consumer inflation expectations
            'c_oecd': ['USACSCICP02STSAM', 'Composite Consumer Confidence for US'], #OECD consumer confidence
            'b_oecd': ['BSCICP02USM460S', 'Business Tendency Surveys Indicator for US Manufacturing'] #OECD business confidence
        }    

        period_points = {
            '6mo': -7,
            '1y': -13,
            '2y': -25,
            '5y': -61,
            '10y': -121,
        }

        if Config.fred_apikey is None:
            raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')
        
        #RAW DATA/OBSERVATION--------------------------------------------------------------
        id = FRED_IDs[type][0]

        FRED_url = f'{Config.fred_baseurl}series/observations?series_id={id}&api_key={Config.fred_apikey}&file_type=json'
        FRED_yield = requests.get(FRED_url).json()

        current_year = pd.Timestamp.now().year
        #----------------------------------------------------------------------------------

        def is_numeric(str):
            try:
                float(str)
                return True
            except ValueError:
                return False
        
        #PARAMETER - PERIOD ================================================================  
        data = {}
        if period == 'max':
            for data_point in FRED_yield['observations']:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        elif period == 'ytd':
            for data_point in FRED_yield['observations'][-15:]:
                if data_point['date'][0:4] == str(current_year):
                    data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        else:
            for data_point in FRED_yield['observations'][period_points[period]:]:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        data_df = pd.DataFrame.from_dict(data, orient='index', columns=[f'{FRED_IDs[type][1]}'])
        data_df.index = pd.to_datetime(data_df.index)
        data_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def fed_rate(self, display: str = 'table', interval: str = '1d', period: str = '5y'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_interval': ['1d', '1wk', '2wk', '1mo'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'ytd', 'max']}
        
        params = {'display': display,
                  'interval': interval,
                  'period': period}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        FRED_IDs = {
            '1d': ['RIFSPFFNB', 'DAILY'], 
            '1wk': ['FF', 'WEEKLY'], 
            '2wk': ['RIFSPFFNBWAW', 'BIWEEKLY'], 
            '1mo': ['FEDFUNDS', 'MONTHLY']
        }

        period_points = {
            '1wk': {
                '1y': -53,
                '2y': -105,
                '5y': -261,
                '10y': -521,
            },
            '2wk': {
                '1y': -27,
                '2y': -53,
                '5y': -131,
                '10y': -261,
            },
            '1mo': {
                '1y': -13,
                '2y': -25,
                '5y': -61,
                '10y': -121,
            }
        }

        def is_numeric(str):
            try:
                float(str)
                return True
            except ValueError:
                return False

        #RAW DATA/OBSERVATION--------------------------------------------------------------
        id = FRED_IDs[interval][0]

        FRED_url = f'{Config.fred_baseurl}series/observations?series_id={id}&api_key={Config.fred_apikey}&file_type=json'
        FRED_rate = requests.get(FRED_url).json()
        
        data = {}
        for data_point in FRED_rate['observations']:
            data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)
        
        data_df = pd.DataFrame.from_dict(data, orient='index', columns=[f'Federal Funds Rate ({FRED_IDs[interval][1]})'])
        data_df.index = pd.to_datetime(data_df.index)
        data_df.index.name= 'Date'

        current_year = pd.Timestamp.now().year
        #----------------------------------------------------------------------------------

        #DATES
        initial_dates = [
                    date.today() - relativedelta(years=1),
                    date.today() - relativedelta(years=2),
                    date.today() - relativedelta(years=5),
                    date.today() - relativedelta(years=10)
                ]

        initial_dates = [pd.Timestamp(d) for d in initial_dates]

        final_dates_list = []

        for d in initial_dates:
            while d not in data_df.index.tolist():
                d = d + relativedelta(days=1)
            final_dates_list.append(d)

        final_dates = {
            '1y': final_dates_list[0],
            '2y': final_dates_list[1],
            '5y': final_dates_list[2],
            '10y': final_dates_list[3],
        }
    
        #PARAMETER - PERIOD ================================================================  
        if period == 'max':
            output = data_df

        elif period == 'ytd':
            output = data_df[data_df.index.year == current_year]

        else:
            if interval == '1d':
                output = data_df.loc[final_dates[period]:]
            elif interval != '1d':
                output = data_df.iloc[period_points[interval][period]:]

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def housing(self, display: str = 'table', type: str = 'starts', period: str = '5y', figure: str = 'raw'): 
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_type' : ['starts', 'nsales', 'esales', '30y_rate', '15y_rate'],
                        'valid_period' : ['1y', '2y', '5y', '10y', 'max', 'ytd'],
                        'valid_figure' : ['raw', 'yoy', 'pop']}
        
        params = {'display': display,
                  'type': type,
                  'period': period,
                  'figure': figure}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        identifiers = {
            'starts': ['HOUST', 'Housing Starts SAAR (Thousands)', 'MoM', 0, 12], #CENSUS M
            'nsales': ['HSN1F', 'New Housing Sales SAAR (Thousands)', 'MoM', 0, 12], #CENSUS M
            'esales': ['EXHOSLUSM495S', 'Existing Housing Sales SAAR (Thousands)', 'MoM', 0, 12], #NAR M (Only provides data from a year back)
            '30y_rate': ['MORTGAGE30US', '30 Year Mortgage Rate', 'WoW', 1, 52], #Freddie Mac W
            '15y_rate': ['MORTGAGE15US', '15 Year Mortgage Rate', 'Wow', 1, 52] #Freddie Mac W
        }
        
        #RAW DATA/OBSERVATION----------------------------------------------------------FRED
        FRED_url = f'{Config.fred_baseurl}series/observations?series_id={identifiers[type][0]}&api_key={Config.fred_apikey}&file_type=json'
        data_list = requests.get(FRED_url).json()['observations']
        #----------------------------------------------------------------------------------
        
        def is_numeric(str):
            try:
                float(str)
                return True
            except ValueError:
                return False
        
        data_dict = {}
        for i in data_list:
            if identifiers[type][3] == 0:
                data_dict[i['date']] = int(float(i['value'])) if is_numeric(i['value']) else np.nan
            if identifiers[type][3] == 1:
                data_dict[i['date']] = float(i['value']) if is_numeric(i['value']) else np.nan

        data_df = pd.DataFrame.from_dict(data_dict, orient='index', columns=[f'{identifiers[type][1]}'])

        if type == 'esales':
            data_df = data_df.drop(data_df.index[0])
            data_df[f'{identifiers[type][1]}'] = (data_df[f'{identifiers[type][1]}']/1000).astype(int)

        period_to_df = {
            '1y': [-13,-53],
            '2y': [-25,-105],
            '5y': [-61,-261],
            '10y': [-121,-521]
        }

        #PARAMETER - FIGURE ================================================================
        if figure == 'raw':
            pass
        elif figure == 'yoy':
            if type != 'esales':
                data_df[f'{identifiers[type][1].split(' (')[0]} YoY % Change'] = (
                    (
                        (
                            data_df[f'{identifiers[type][1]}'] / data_df[f'{identifiers[type][1]}'].shift(identifiers[type][4])
                        ) - 1
                    ) * 100
                ).round(2)
                del data_df[f'{identifiers[type][1]}']
                data_df = data_df.drop(data_df.index[0:12])
            elif type == 'esales':
                raise InvalidParameterError(f"Data avaliablity limited at 1y for esales. YoY figure calculation invalid. ")
        elif figure == 'pop':
            data_df[f'{identifiers[type][1].split(' (')[0]} {identifiers[type][2]} % Change'] = (
                (
                    (
                        data_df[f'{identifiers[type][1]}'] / data_df[f'{identifiers[type][1]}'].shift(1)
                    ) - 1
                ) * 100
            ).round(2)
            del data_df[f'{identifiers[type][1]}']
            data_df = data_df.drop(data_df.index[0:1])

        #PARAMETER - PERIOD ================================================================
        if period == 'max':
            data_df = data_df
        elif period == 'ytd':
            current_year = str(datetime.now().year)
            data_df = data_df[data_df.index.str[0:4] == current_year]
        elif period != 'max' or period != 'ytd':
            data_df = data_df[period_to_df[period][identifiers[type][3]]:]
        
        data_df.index = pd.to_datetime(data_df.index) # converting all row indices to datetime objects
        data_df.index.name = 'Date'

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = data_df
            return output
        elif display == 'json':
            data_df.index = data_df.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in data_df.iterrows():
                a = {
                    'Date': index,
                    f'{data_df.columns[0]}': float(row[f'{data_df.columns[0]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def vix(self, display: str = 'table', period: str = '5y', start: str = None, end: str = None, interval: str = '1d', data: str = 'all'):
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_period' : ['1mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
                        'valid_interval' : ['1d', '1wk', '1mo', '3mo'],
                        'valid_data' : ['open', 'high', 'low', 'close', 'all']}
        
        params = {'display': display,
                  'period': period,
                  'interval': interval,
                  'data': data}
        
        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        #Note: start and end parameters will override any period parameter presence
        if start == None and end == None:
            yf_download = yf.download('^VIX', period=period, interval=interval, ignore_tz=True, rounding=True, group_by='column', progress=False, auto_adjust=True)
        elif start != None and end != None:
            yf_download = yf.download('^VIX', start=start, end=end, interval=interval, ignore_tz=True, rounding=True, group_by='column', progress=False, auto_adjust=True)
        #----------------------------------------------------------------------------------

        #STANDARDIZING TABLE---------------------------------------------------------------
        yf_download = yf_download.drop(columns=['Volume'])
        yf_download.columns = yf_download.columns.droplevel([1])
        yf_download.columns.name = None
        yf_download.columns = ['VIX Close', 'VIX High', 'VIX Low', 'VIX Open']

        #PARAMETER - DATA =================================================================
        if data == 'all':
            yf_download = yf_download
        else:
            yf_download = yf_download[f'VIX {data.capitalize()}']

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = yf_download
            return output
        elif display == 'json':
            yf_download.index = yf_download.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in yf_download.iterrows():
                a = {
                    'Date': index,
                    f'{yf_download.columns[0]}': float(row[f'{yf_download.columns[0]}']),
                    f'{yf_download.columns[1]}': float(row[f'{yf_download.columns[1]}']),
                    f'{yf_download.columns[2]}': float(row[f'{yf_download.columns[2]}']),
                    f'{yf_download.columns[3]}': float(row[f'{yf_download.columns[3]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------
    def dollar_index(self, display: str = 'table', period: str = '5y', start: str = None, end: str = None, interval: str = '1d', data: str = 'all'):
        valid_params = {'valid_display': ['table', 'json'],
                        'valid_period' : ['1mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
                        'valid_interval' : ['1d', '1wk', '1mo', '3mo'],
                        'valid_data' : ['open', 'high', 'low', 'close', 'all']}
        
        params = {'display': display,
                  'period': period,
                  'interval': interval,
                  'data': data}
        
        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        #RAW DATA/OBSERVATIONS-------------------------------------------------------------
        #Note: start and end parameters will override any period parameter presence
        if start == None and end == None:
            yf_download = yf.download('DX-Y.NYB', period=period, interval=interval, ignore_tz=True, rounding=True, group_by='column', progress=False, auto_adjust=True)
        elif start != None and end != None:
            yf_download = yf.download('DX-Y.NYB', start=start, end=end, interval=interval, ignore_tz=True, rounding=True, group_by='column', progress=False, auto_adjust=True)
        #----------------------------------------------------------------------------------

        #STANDARDIZING TABLE---------------------------------------------------------------
        yf_download = yf_download.drop(columns=['Volume'])
        yf_download.columns = yf_download.columns.droplevel([1])
        yf_download.columns.name = None
        yf_download.columns = ['$_INDEX Close', '$_INDEX High', '$_INDEX Low', '$_INDEX Open']

        #PARAMETER - DATA =================================================================
        if data == 'all':
            yf_download = yf_download
        else:
            yf_download = yf_download[f'$_INDEX {data.capitalize()}']

        output = yf_download

        #PARAMETER - DISPLAY ==============================================================
        if display == 'table':
            output = yf_download
            return output
        elif display == 'json':
            yf_download.index = yf_download.index.strftime('%Y-%m-%d')

            data_json_list = []
            for index, row in yf_download.iterrows():
                a = {
                    'Date': index,
                    f'{yf_download.columns[0]}': float(row[f'{yf_download.columns[0]}']),
                    f'{yf_download.columns[1]}': float(row[f'{yf_download.columns[1]}']),
                    f'{yf_download.columns[2]}': float(row[f'{yf_download.columns[2]}']),
                    f'{yf_download.columns[3]}': float(row[f'{yf_download.columns[3]}'])
                }
                data_json_list.append(a)
            output = data_json_list
            return output
#------------------------------------------------------------------------------------------