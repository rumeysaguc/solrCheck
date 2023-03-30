# -*- coding: utf-8 -*-

import urllib.request
import json
from datetime import datetime
import datetime
import sys
from json import JSONEncoder

import time

getData = sys.argv[1] + "url.txt"

scanDate = datetime.date.today() - datetime.timedelta(days=1)
print("İşlem yapılacak tarih: ", scanDate)
result = {}
resultList = []


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def lookupFunction(url, date, isKoseYazari, search_term):
    search_term = search_term.encode(encoding='UTF-8', errors='strict')
    type = 0
    if isKoseYazari == "SORUMLU YAZI İŞLERİ MÜDÜRÜ":
        queryUrl = solrUrl + 'select?indent=on&q=tag:columnist%20AND%20id:*' + url + '*%20AND%20datepublished:[%22' + str(
            date.year) + '-' + str(date.month) + '-' + str(date.day) + 'T00:00:00.000Z%22%20TO%20%22' + str(
            date.year) + '-' + str(date.month) + '-' + str(date.day) + 'T23:59:59.990Z%22]&rows=10000&wt=json'
        type = 1
    else:
        queryUrl = solrUrl + 'select?indent=on&q=tag:news%20AND%20id:*' + url + '*%20AND%20datepublished:[%22' + str(
            date.year) + '-' + str(date.month) + '-' + str(date.day) + 'T00:00:00.000Z%22%20TO%20%22' + str(
            date.year) + '-' + str(date.month) + '-' + str(date.day) + 'T23:59:59.990Z%22]&rows=10000&wt=json'
    print(queryUrl)

    with urllib.request.urlopen(queryUrl) as response:
        html = response.read()

    count = 0
    jsonVal = json.loads(html)
    print(jsonVal['response']['numFound'], 'Records found')

    for haber in jsonVal['response']['docs']:
        print(haber['content'])
        haberContent = haber['content']
        search_term_position = haberContent.find(str(search_term))
        if search_term_position != -1:
            print(haber['datepublished'], haber['content'][search_term_position - 20:search_term_position + 50])
            count = count + 1

    print(search_term, 'içeren', count, 'haber bulundu.')
    return count, type


if __name__ == '__main__':
    startTime = datetime.datetime.now()
    urlCount = 0
    message = ""
    search_term = ""
    intlcerikSayisiParm = 0
    intKoseYazisiSayisiParm = 0
    boolKayitBulunduParm = False
    with open(getData, encoding="utf8") as f:
        data = json.load(f)
        solrUrl = data['solrUrl']
        resultFolder = data['resultFolder']
    for item in data['fikirIscisiListesi']:
        urlCount += 1
        if item['boolKadroBilgisiBulunduParm'] == True:
            boolKayitBulunduParm = True
            message = "Successfully"
            if str(item['strKisiIkinciAdParm']) != "":
                search_term = str(item['strKisiAdParm']) + " " + str(item['strKisiIkinciAdParm']) + " " + str(
                    item['strKisiSoyadParm'])
            search_term = str(item['strKisiAdParm']) + " " + str(item['strKisiSoyadParm'])
            response, type = lookupFunction(item['strYayinAdi_InternetAdresiParm'], scanDate, item['strKisiUnvanParm'],
                                            search_term)
            if type == 1:
                intlcerikSayisiParm = response
            else:
                intKoseYazisiSayisiParm = response
        result = {
            "dateTarihParm": datetime.datetime.now(),
            "intKoseYazisiSayisiParm": intKoseYazisiSayisiParm,
            "intlcerikSayisiParm": intlcerikSayisiParm,
            "classDeclaration": "",  # gelen data da yok
            "strKisiUnvanParm": item['strKisiUnvanParm'],
            "strKisilkinciAdParm": item['strKisiIkinciAdParm'],
            "strKisiSoyadParm": item['strKisiSoyadParm'],
            "strKisiAdParm": item['strKisiAdParm'],
            "int64TCKimlikNoParm": item['int64TCKimlikNoParm'],
            "boolKayitBulunduParm": boolKayitBulunduParm,
            "boolKayitEklendiParm": "",
            "strServisMesajParm": message,
            "strYayinKoduParm": item['strYayinKoduParm'],
            "strYayinAdiInternetAdresiParm": item['strYayinAdi_InternetAdresiParm']
        }

        resultList.append(result)
    outfile = open(resultFolder + "returnData.json", "w")
    json.dump(resultList, outfile, cls=DateTimeEncoder)

    outfile2 = open(resultFolder + "logData.json", 'w')
    text = []

    endTime = datetime.datetime.now()
    timeDelta = endTime - startTime
    resultDict = {
        "urlCount": urlCount,
        "date": scanDate,
        "crawlTime": str(timeDelta.seconds) + " saniye sürdü",
        "results": result,
    }
    text.append(resultDict)
    json.dump(text, outfile2, cls=DateTimeEncoder)
    print("Tüm işlemler tamamlandı.")
