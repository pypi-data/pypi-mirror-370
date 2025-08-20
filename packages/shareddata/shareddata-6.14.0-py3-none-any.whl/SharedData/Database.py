DATABASE_PKEYS = {
    'Symbols':          ['symbol'],
        
    'TimeSeries':       ['date'],
    'MarketData':       ['date', 'symbol'],
    'Relationships':    ['date', 'symbol', 'symbol1'],
    'Options':          ['date', 'symbol', 'expiry', 'strike', 'callput'],
    
    'Tags':             ['date', 'tag', 'symbol'],
    'Text':             ['date', 'hash'],
    
    'Accounts':         ['portfolio'],
    'Portfolios':       ['date', 'portfolio'],
    'Signals':          ['date', 'portfolio', 'symbol'],
    'Risk':             ['date', 'portfolio', 'symbol'],
    'Positions':        ['date', 'portfolio', 'symbol'],
    'Requests':         ['date', 'portfolio', 'requestid'],
    'Orders':           ['date', 'portfolio', 'clordid'],
    'Trades':           ['date', 'portfolio', 'symbol', 'tradeid']
}

STRING_FIELDS = ['symbol','tag','portfolio','requestid','clordid','tradeid']

PERIODS = ['D1','M15','M1','RT']