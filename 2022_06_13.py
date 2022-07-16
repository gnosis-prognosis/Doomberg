from prompt_toolkit.application import Application
from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style 
from prompt_toolkit.widgets import TextArea, SearchToolbar
from prompt_toolkit.layout import FormattedTextControl, WindowAlign, ScrollablePane, BufferControl
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.bindings.page_navigation import scroll_page_up, scroll_page_down

import urllib.request
import json
import threading
import pandas as pd
import time
import csv

##########################
# #                      #
# #      START         # #
# #                      #
##########################

terminal_title = "Doomberg"
print(f'\33]0;{terminal_title}\a', end='', flush=True)

bindings = KeyBindings()
bindings.add('s-tab')(focus_next)
@bindings.add('c-c')
def _(event):
    event.app.exit()

   
def do_every(delay, task):
    while True:
        task()
        time.sleep(delay)
        


def fnYFinJSON(stock):
    if stock == None:
        return {}
    else:
        urlData = "https://query2.finance.yahoo.com/v7/finance/quote?symbols="+stock
       # urlData = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{}".format(stock)
        user_agent = 'Mozilla/5.0'
        headers = {'User-Agent': user_agent}
        webUrl = urllib.request.urlopen(urlData)
        if (webUrl.getcode() == 200):
            data = webUrl.read()
            data = (data.decode('ascii'))
            yFinJSON = json.loads(json.loads(json.dumps(data)))
            return  yFinJSON["quoteResponse"]["result"][0]
        else:
            return None

# ------------------------------------



def test2(tickers): 
    fields = { 'regularMarketChangePercent': '%', 'regularMarketPrice':'Price', 'currency':'Curr',
               'shortName':'Company', 'priceToBook':'P/B',
               'trailingPE':'ltm P/E', 'forwardPE':'fwd P/E','marketState':'State'}
    results = {}
    for ticker in tickers:
        tickerData = fnYFinJSON(ticker)
        singleResult = {}
        if not tickerData.__contains__('"result":[]'):
            for key in fields.keys():
                if key in tickerData:
                    singleResult[fields[key]] = tickerData[key]
                else:
                    singleResult[fields[key]] = "N/A"
        else:
            pass
        results[ticker] = singleResult
    #default is keys are columns
    dfTransp = pd.DataFrame.from_dict(results)
    #unless you set orient as index
    df = pd.DataFrame.from_dict(results, orient='index')
    df_formated = df.applymap(lambda x: round(x, 1) if isinstance(x, (int, float)) else x)
   # df_formated['Price'] = pd.Series([round(val, 2) for val in df['Price']], index = df.index)
   # df_formated['%'] = pd.Series([round(val, 2) for val in df['%']], index = df.index)
    # df['Var3'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df['var3']], index = df.index)
    return str(df_formated) 
#------------------------------------------------------
    
watchlist_symbols = []
# with open('ticker_list.csv', newline='') as inputfile:
#     for row in csv.reader(inputfile):
#        watchlist_symbols.append(row[0])
def _get_symbols_from_csv(file_name):
    _symbols = []
    with open(file_name, newline='') as inputfile:
        for row in csv.reader(inputfile):
            _symbols.append(row[0])
    return _symbols

def _get_csv_path():
    _csv_file = ''
    _csv_file = BottomInputInstructionsView.get_input_instructions_view()
    return _csv_file

watchlist_symbols = _get_symbols_from_csv('default_ticker_list.csv')
#------------------------------------------------------
path_completer = PathCompleter(expanduser=True)

class BottomInputInstructionsView(object):
    def __init__(self):
         self.__completer = 'to_do'

    def get_input_instructions_view(self):
        return TextArea(height=1,
                        prompt='>',
                        style="class:input-field",
                        complete_while_typing=True,
                        multiline=False,
                        wrap_lines=False,
                        completer=path_completer,
                        )

       # return  prompt_result = prompt(">>> ", completer=completer, validator=completer.get_validator())

#--------------------------------------------------------


MAIN_BUFFER = Buffer()

class WatchListView(object):
    def __init__(self):
        self.__watchlist_title_view_text = 'Watchlist'

    def get_watchlist_stocks_view(self):
                return Window(BufferControl(
                        buffer=MAIN_BUFFER,focusable=True,focus_on_click=True),
                        )

            
class PyTickerLayout(object):
    def __init__(self):
        self.__watchlist = WatchListView()
        self.__bottom = BottomInputInstructionsView()

    def _get_main_content_layout(self):        
        output = self.__watchlist.get_watchlist_stocks_view()
        return output

    def get_layout(self) -> Layout:
        root_container = HSplit([
            self.__bottom.get_input_instructions_view(),
            self._get_main_content_layout(),
            ], padding_char='-', padding=1) #'#242525'
        return Layout(container=root_container)


class PyTicker(object):
    def __init__(self):
        self._application = None
        self._pyticker_layout = PyTickerLayout()

    def init_application(self):
        layout = self._pyticker_layout.get_layout()
        self._application = Application(layout=layout,
                                        full_screen=True,
                                        key_bindings=bindings, cursor=CursorShape.UNDERLINE)

    def _invalidate(self):
        # yahoo_client = YahooHttpClient(watchlist_symbols)
        # watchlist_text = yahoo_client.get_stock_quotes()
        watchlist_text = test2(watchlist_symbols)
        MAIN_BUFFER.text = (watchlist_text)
        self._application.invalidate()

    def run(self):
        # yahoo_client = YahooHttpClient(watchlist_symbols)
        # watchlist_text = yahoo_client.get_stock_quotes()        
        watchlist_text = test2(watchlist_symbols)
        MAIN_BUFFER.text = watchlist_text
        threading.Thread(target=lambda: do_every(3, self._invalidate), daemon=True).start()
        self._application.run()

def main():
    pyticker = PyTicker()
    pyticker.init_application()
    pyticker.run()
    
if __name__ == '__main__':
    main()
