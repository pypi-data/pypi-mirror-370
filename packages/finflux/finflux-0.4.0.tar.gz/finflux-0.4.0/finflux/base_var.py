class Config:
    td_apikey     = None
    fred_apikey   = None
    bea_apikey    = None
    bls_apikey    = None
    email_address = None
    td_baseurl    = 'https://api.twelvedata.com/'
    fred_baseurl  = 'https://api.stlouisfed.org/fred/'
    sec_baseurl   = 'https://www.sec.gov/'
    bea_baseurl   = 'https://apps.bea.gov/api/data'
    bls_baseurl   = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'

def set_config(td=None, fred=None, email=None, bea=None, bls=None):
    Config.td_apikey     = td
    Config.fred_apikey   = fred
    Config.email_address = email
    Config.bea_apikey    = bea
    Config.bls_apikey    = bls

