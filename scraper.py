import requests
from bs4 import BeautifulSoup
from datetime import datetime
# import json
import jsonpickle
# import pandas as pd

# Utils


def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))


# Objects
class MarketsCont:
    def __init__(self, markets):
        self.Markets = markets


class Market:
    def __init__(self, code, title, countryCode, logo, tz, session, holidays):
        self.Code = code
        self.Title = title
        self.CountryCode = countryCode
        self.Logo = logo
        self.TimeZone = tz
        self.Sessions = session
        self.Holidays = holidays


class Sessions:
    def __init__(self, name, days=None, style=0, start=None, end=None):
        self.Title = name
        self.Days = days
        self.Style = style
        self.StartTime = start
        self.EndTime = end


class Holiday:
    def __init__(self, name, date, session):
        self.Title = name
        self.Date = date
        self.Sessions = session

# Functions


def ParseExchange(exchange_code):
    # Code, title, coutry, logo
    URL = 'https://www.tradinghours.com/exchanges/' + exchange_code
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    heading_e = soup.find('h1', class_='heading')
    logo = 'https://www.tradinghours.com' + heading_e.find('img')['src']
    title = heading_e.find('b').text
    country_code = soup.find('h2', id="countdown").find(
        'div', class_='flag-small').attrs['class'][1].split('-')[1]

    # Days and sessions
    URL = 'https://www.tradinghours.com/exchanges/' + exchange_code + '/trading-hours'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    cards_e = soup.find_all('div', class_='card-body')
    for card_e in cards_e:
        tradingSchedule_e = card_e.find('h3', id='trading-schedule')

        if(tradingSchedule_e):
            main_e = tradingSchedule_e.find_parent('div')
            tz_e = main_e.find_all('p', class_='text-muted')[0].find('b')
            tz = tz_e.text

            sessions = []
            days_ps_e = main_e.find_all('p')
            for days_p_e in days_ps_e:
                if ((not days_p_e.get('class')) or 'text-muted' not in days_p_e.get('class')):
                    days_e = days_p_e.find('b')
                    day_title = days_e.text.replace(':', '').split('/')
                    clean_times = []
                    for hours in days_p_e.next_siblings:
                        if(hours.name == 'p'):
                            break
                        elif(hours.name == None and '—' in hours):
                            clean_times.append(cleanTime(hours, 1))
                        elif(hours.name == 'b'):
                            clean_times.append(
                                cleanTime(hours.get_text(), 2))
                    for clean_time in clean_times:
                        sessions.append(
                            Sessions(
                                clean_time[0],  # Title
                                cleanDays(day_title),  # Days list
                                clean_time[1],  # Style
                                clean_time[2],  # Start
                                clean_time[3]  # End
                            )
                        )

# Holidays
    URL = 'https://www.tradinghours.com/exchanges/' + \
        exchange_code + '/market-holidays/2020'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    holidays = []
    table = soup.find('tbody')
    rows = table.find_all('tr')
    for row in rows:
        name = row.find(attrs={'data-title': 'Name'})
        date = row.find(attrs={'data-title': 'Observed Date'})
        status = row.find(attrs={'data-title': 'Status'})

        holidays.append([name.text.strip(), date.text.replace(
            '†', '').strip(), status.text.replace('‡', '').strip()])

    return [exchange_code,
            title,
            country_code,
            logo,
            tz,
            sessions,
            cleanHolidays(holidays)]


def cleanDays(days):
    clean_days = []
    for day in days:
        if day == 'Mo':
            clean_days.append('Monday')
        elif day == 'Tu':
            clean_days.append('Tuesday')
        elif day == 'We':
            clean_days.append('Wednesday')
        elif day == 'Th':
            clean_days.append('Thursday')
        elif day == 'Fr':
            clean_days.append('Friday')
        elif day == 'Sa':
            clean_days.append('Saturday')
        elif day == 'Su':
            clean_days.append('Sunday')
        else:
            raise ValueError('Day not recognized.')
    return clean_days


def cleanTime(time, style):
    time_c = time.strip()
    start_time = time_c.split(' — ')[0].split(
        ' - ')[0].replace(' ', '').strip()
    end_time = time_c.split(' — ')[0].split(
        ' - ')[1].replace(' ', '').strip()
    if len(start_time) < 7:
        start_time = '0' + start_time
    if len(end_time) < 7:
        end_time = '0' + end_time
    return [cleanSessionTitle(time_c.split(' — ')[1]),
            style,
            parseTime(start_time),
            parseTime(end_time)
            ]


def cleanHolidays(holidays):
    clean_holidays = []
    for holiday in holidays:
        holiday_session = holiday[2].replace(
            '(passed)', '').replace('(today)', '')
        if('Closed' in holiday_session):
            session = Sessions(
                holiday_session.strip()  # Title
            )
        else:
            start_time = holiday_session.split(',')[1].split(
                '-')[0].replace(' ', '').strip()
            end_time = holiday_session.split(',')[1].split(
                '-')[1].replace(' ', '').strip()
            if len(start_time) < 7:
                start_time = '0' + start_time
            if len(end_time) < 7:
                end_time = '0' + end_time
            session = Sessions(
                holiday_session.split(',')[0].strip(),  # Title
                None,  # Days list
                2,  # Style
                parseTime(start_time),  # Start
                parseTime(end_time)  # End
            )
        clean_holidays.append(
            Holiday(
                holiday[0],
                cleanDate(holiday[1]),
                session
            )
        )
    return clean_holidays


def cleanDate(date):
    return datetime.strptime(date, '%B %d, %Y').strftime('%d/%m/%y')


def parseTime(time_string):
    return datetime.strptime(time_string, '%I:%M%p').strftime('%H:%M')


def cleanSessionTitle(title):
    if('Pre-Opening Session' == title or
        'Pre Opening Session' == title or
        'Pre-Opening' == title or
        'Pre Opening' == title or
        'Pre-opening session' == title or
        'Pre-opening' == title or
        'Pre-opening I' == title or
        'Pre-opening II' == title or
        'Pre-opening Phase' == title or
        'Afternoon Pre Opening Session' == title or

        'Pre Trading' == title or
        'Pre Trading Phase' == title or
        'Pre Open Session' == title or
        'Pre-open' == title or
        'Pre-Open' == title or
        'Pre Auction' == title or
        False
       ):
        return 'Pre Open'

    if('Opening Session' == title or
        'Opening Auction' == title or
        'Opening Auction Call' == title or
        'Opening Auction Call' == title or
        'Opening Call Auction' == title or
        'Opening Imbalance Period' == title or
        'Opening Phase' == title or
        'Opening Routine' == title or
        'Early Trading Session' == title or
        False
       ):
        return 'Opening'

    if('Core Trading Session' == title or
        'Trading Session' == title or
        'Continuous Trading' == title or
        'Normal Trading' == title or
        'Trading' == title or
        'Regular Trading' == title or
        '1st Session' == title or
        '2nd Session' == title or
        'Day Session' == title or
        'Open Auction Session' == title or
        'Morning Trading Session' == title or
        False
       ):
        return 'Open'

    if('Lunch Break' == title or
        'Mid-Day Break' == title or
        'Intermission' == title or
        False
       ):
        return 'Lunch'

    if('Pre-CSPA' == title or
        'Pre-Closing' == title or
        'Pre-Closing Session' == title or
        'Pre-close' == title or
        'Pre-Close' == title or
        False
       ):
        return 'Pre Close'

    if('Closing Auction' == title or
        'Closing Auction & end of trade' == title or
        'Closing Auction Call' == title or
        'Closing Auction Freeze Period' == title or
        'Closing Call' == title or
        'Closing Call Auction' == title or
        'Closing Imbalance Period' == title or
        'Closing Price Cross' == title or
        'Closing Price Cross Session' == title or
        'Closing Price Publication' == title or
        'Closing Price Publication Session' == title or
        'Closing Routine' == title or
        'Closing Session' == title or
        'Closing Single Price Auction' == title or
        'Closing call auction' == title or
        'End of Trading' == title or
        'Trading at Last' == title or
        'Trade at Last' == title or
        'Trading at last' == title or
        'Pre-Close Auction Period' == title or
        'Negotiation at the last price' == title or
        False
       ):
        return 'Closing'

    if('Post Close' == title or
        'Post Close Session' == title or
        'Post Trade Session' == title or
        'Post-Close' == title or
        'Post-Close Session' == title or
        'Post-Closing' == title or
        'Post-Closing' == title or
        'Post-Trading Session' == title or
        'After-hour Fixed Price Trading' == title or
        'Off-Hour Trading' == title or
        'Late Trading Session' == title or
        'Overnight Trading' == title or
        False
       ):
        return 'After Hours'
    else:
        return title


# Main
exchanges = []
MarketCodes = ['nyse', 'nasdaq', 'lse', 'jpx', 'sse', 'hkex', 'euronext', 'szse', 'tsx', 'bse-bombay', 'nse-india', 'six', 'asx', 'krx', 'omx', 'jse', 'bme', 'twse', 'bovespa', 'fsx', 'myx', 'jse-jamaica', 'bvs', 'bvc', 'bvl', 'bmv', 'bcba', 'cse', 'cse-colombo', 'dse', 'hose', 'idx', 'nzx', 'pse', 'sgx', 'set', 'adx', 'ase-amman', 'ase-athens', 'bist', 'bc', 'bvb', 'bse-budapest', 'dfm', 'egx', 'ise', 'kase', 'luxse', 'moex', 'nse-nigeria', 'ose', 'pex', 'qe', 'tadawul', 'sem', 'tse', 'tase', 'ux', 'gpw', 'vse', 'zse', 'mse', 'bde-barbados', 'bsx', 'hnx', 'bhb', 'bse-beirut', 'eurex', 'psx', 'nse-nairobi', 'omxh-helsinki', 'omxr-riga',
               'euronext-paris', 'bx', 'mta', 'omxc-copenhagen', 'otc', 'amex', 'aim', 'tpex', 'belex', 'bse-bulgaria', 'cnsx', 'pfts', 'nilx', 'euronext-brussels', 'euronext-lisbon', 'cde', 'xsat', 'xkuw', 'cse-cyprus', 'xlju', 'bsse', 'msm', 'xetr', 'lme', 'bmex', 'xice', 'xtsx', 'xngo', 'xham', 'xfka', 'xmun', 'xber', 'xpra', 'rusx', 'xsap', 'lotc', 'xdus', 'xhan', 'xngm', 'xstu', 'gse', 'iex', 'xula', 'xzse', 'csx', 'blse', 'sase', 'xmae', 'tise', 'nsx', 'xcsx', 'bse-botswana', 'bvmt', 'rse', 'omxv-vilnius', 'mnse', 'nex', 'xdse', 'ndxb', 'nsxa', 'neo', 'bvpa', 'bvcc', 'omxt-tallinn', 'bvg', 'bnv', 'bbv', 'ssx', 'bcse', 'kosdaq', 'brvm', 'ifb']
# MarketCodes = ['tase']
for marketCode in MarketCodes:
    parsed_exchange = ParseExchange(marketCode)
    exchanges.append(
        Market(
            parsed_exchange[0],  # code
            parsed_exchange[1],  # title
            parsed_exchange[2],  # country
            parsed_exchange[3],  # logo
            parsed_exchange[4],  # tz
            parsed_exchange[5],  # session
            parsed_exchange[6]  # holidays
        )
    )

markets = MarketsCont(exchanges)
# dump(exchanges)
# for exchange in exchanges:
#     print(jsonpickle.encode(exchange))
f = open('Markets.json', 'w')
f.write(jsonpickle.encode(markets, unpicklable=False))
f.close()
