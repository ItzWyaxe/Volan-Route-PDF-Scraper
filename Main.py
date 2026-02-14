import requests
from bs4 import BeautifulSoup
import re
import time
import os
from urllib.parse import urljoin

TargetUrl = 'https://www.mavcsoport.hu/mav-szemelyszallitas/belfoldi-utazas/vonali-menetrendek'
SavePath = './PDFs'
LogPath = './ErrorLog.log'
Headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

if not os.path.exists(SavePath):
    os.makedirs(SavePath)

def LogError(Message):
    with open(LogPath, 'a', encoding='UTF-8') as LogFile:
        LogFile.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {Message}\n')

def DownloadPdf(Url, Filename):
    try:
        Response = requests.get(Url, headers=Headers, stream=True, timeout=15)
        Response.raise_for_status()
        
        FilePath = os.path.join(SavePath, f'{Filename}.pdf')
        with open(FilePath, 'wb') as Pdf:
            for Chunk in Response.iter_content(chunk_size=8192):
                Pdf.write(Chunk)
        print(f'Success: {Filename}.pdf downloaded.')
    except Exception as E:
        Msg = f'Error during download ({Filename}): {E}'
        print(Msg)
        LogError(Msg)

def GetPdfLinks(Url):
    UniqueLinks = set()
    try:
        Response = requests.get(Url, headers=Headers, timeout=10)
        Response.raise_for_status()
        Soup = BeautifulSoup(Response.content, 'html.parser')

        for AnchorTag in Soup.find_all('a', href=True):
            Href = AnchorTag['href']
            AbsoluteUrl = urljoin(Url, Href)
            
            if '/letoltes/' in AbsoluteUrl:
                UniqueLinks.add(AbsoluteUrl)
    except Exception as E:
        Msg = f'Error fetching page ({Url}): {E}'
        print(Msg)
        LogError(Msg)
    
    return sorted(list(UniqueLinks))

try:
    MainResponse = requests.get(TargetUrl, headers=Headers, timeout=15)
    MainResponse.raise_for_status()
    MainSoup = BeautifulSoup(MainResponse.text, 'html.parser')
    
    Table = MainSoup.find(id='route-list')
    Rows = Table.find('tbody').find_all('tr', class_=re.compile(r'route\s(.+)'))
    
    for Row in Rows:
        ClassAttr = ' '.join(Row.get('class', []))
        Match = re.search(r'route\s+(\d+[a-z]?)', ClassAttr)
        if not Match: continue
        
        RouteNum = Match.group(1)
        LinkTag = Row.find('a', href=True)
        
        if LinkTag:
            FullRouteUrl = urljoin('https://www.mavcsoport.hu', LinkTag['href'])
            PdfLinks = GetPdfLinks(FullRouteUrl)
            
            if PdfLinks:
                DownloadPdf(PdfLinks[-1], RouteNum)
                time.sleep(0.5)
            else:
                Msg = f'No Pdf found for route {RouteNum}.'
                print(f'Info: {Msg}')
                LogError(Msg)

except Exception as E:
    LogError(f'Critical error: {E}')
    print(f'Critical error: {E}')