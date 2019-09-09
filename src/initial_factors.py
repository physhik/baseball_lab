import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json 

pd.options.display.float_format = '{:.6f}'.format


def runs(start, end):
  runmap={}
  for year in range(start,end+1):
    year = str(year)
    for ha in ['33', '34']:
      if ha =='33':
        han = 'home'
      else:
        han = 'away'
      for type in ['pitching', 'batting']:
        url = "http://www.espn.com/mlb/stats/team/_/stat/{}/year/{}/split/{}"
        url = url.format(type, year, ha)
        s=requests.get(url).content
        soup=BeautifulSoup(s,'lxml')
        table = soup.find_all('tr')
        data = []
        for t in table[1:]:
          cols = t.find_all('td')
          cols = [ele.text.strip() for ele in cols]
          data.append([ele for ele in cols[1:]])
        
        dp = pd.DataFrame(data[1:31])
        dp.columns = data[0]
        dp.set_index('TEAM', inplace = True)  
        dp= dp.sort_values(by='TEAM')
        runmap[(year, type, han)] = dp.R.values
      runmap[(year, 'GP',han)] = dp.GP.values
      
  dp2 = pd.DataFrame(runmap)

  dp2.index = dp.index.values
  return dp2


def initial_factors(start, end):
  IF = {}
  dp2 = runs(start, end)
  for team in dp2.index:
    for year in range(start,end+1):
      i = year - start
      try:
        IF[str(year)].append(((int(dp2.loc[team][6*i])+int(dp2.loc[team][6*i+1]))/int(dp2.loc[team][6*i+2]))/((int(dp2.loc[team][6*i+3])+int(dp2.loc[team][6*i+4]))/int(dp2.loc[team][6*i+5])))
      except:
        IF[str(year)]=[((int(dp2.loc[team][6*i])+int(dp2.loc[team][6*i+1]))/int(dp2.loc[team][6*i+2]))/((int(dp2.loc[team][6*i+3])+int(dp2.loc[team][6*i+4]))/int(dp2.loc[team][6*i+5]))]

  dpif = pd.DataFrame(IF)
  dpif.index = dp2.index.values
  return dpif
