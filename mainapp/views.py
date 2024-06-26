from django.http.response import HttpResponse
from django.shortcuts import render
import yahoo_fin.stock_info as si
import yfinance as yf
import time
import queue
from threading import Thread
from asgiref.sync import sync_to_async
# Create your views here.
def stockPicker(request):
    import nsepython as nse
    stock_picker = nse.nse_eq_symbols()
    for index, stock in enumerate(stock_picker):
        stock += '.NS'
        stock_picker[index] = stock

    print("ggn 16", stock_picker)
    #####
    # # Downloading the JSON of the datasource of this page - https://www.niftyindices.com/market-data/heat-map-detail?Indexname=NIFTY 50
    # import pandas as pd
    # df = pd.read_json('https://iislliveblob.niftyindices.com/jsonfiles/HeatmapDetail/FinalHeatmapNIFTY%2050.json')
    # d = df.head()
    # print("ggn 19", df)
    #####
    # stock_picker = si.tickers_nifty50()
    return render(request, 'mainapp/stockpicker.html', {'stockpicker':stock_picker})

def getData(stockpicker):
    data = {}
    # available_stocks = si.tickers_nifty50()
    # print("ggn 16", stockpicker)
    # print("ggn 17", available_stocks)
    # for i in stockpicker:
    #     if i in available_stocks:
    #         pass
    #     else:
    #         return {}
    #         # return HttpResponse("Error")

    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()
    start = time.time()
    for i in range(n_threads):
        thread = Thread(target=lambda q, arg1: q.put({stockpicker[i]: yf.Ticker(arg1).info}),
                        args=(que, stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)
    return data

async def stockTracker(request):

    stockpicker = request.GET.getlist('stockpicker')
    stockshare=str(stockpicker)[1:-1]
    
    ##
    data = getData(stockpicker)
    end = time.time()
    # time_taken =  end - start
    # print(time_taken)
    return render(request, 'mainapp/stocktracker.html', {'data': data, 'room_name': 'track','selectedstock':stockshare})
