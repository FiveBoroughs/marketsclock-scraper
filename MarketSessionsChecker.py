import json


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


with open('Markets.json') as json_data:
    d = json.load(json_data)

    for market in d['markets']:
        for session in market['Sessions']:
            title = session['Title']
            # if(session['Style'] == 2 and title != 'Open'):
            #     print(title)
            # if(session['Style'] == 1):
            #     print(market['Code'] + ',' + title)
            print(market['Code'] + ',' + cleanSessionTitle(title))
