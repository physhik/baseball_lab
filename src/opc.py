import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json 
from initial_factors import *

def oldOPCxRUN(year):
  """
  Initial factors are given with more significant figures than ESPN park factor
  """
  
  tmap = {'ari': 'Arizona',
 'atl': 'Atlanta',
 'bal': 'Baltimore',
 'bos': 'Boston',
 'chc': 'Chicago Cubs',
 'chw': 'Chicago White Sox',
 'cin': 'Cincinnati',
 'cle': 'Cleveland',
 'col': 'Colorado',
 'det': 'Detroit',
 'hou': 'Houston',
 'kc': 'Kansas City',
 'laa': 'Los Angeles Angels',
 'lad': 'Los Angeles Dodgers',
 'mia': 'Miami',
 'mil': 'Milwaukee',
 'min': 'Minnesota',
 'nym': 'New York Mets',
 'nyy': 'New York Yankees',
 'oak': 'Oakland',
 'phi': 'Philadelphia',
 'pit': 'Pittsburgh',
 'sd': 'San Diego',
 'sea': 'Seattle',
 'sf': 'San Francisco',
 'stl': 'St. Louis',
 'tb': 'Tampa Bay',
 'tex': 'Texas',
 'tor': 'Toronto',
 'wsh': 'Washington'}
  
  IF=initial_factors(year, year)
  OPCxRUN=30/(29+IF[str(year)])*IF[str(year)]/IF[str(year)+'IPC']
  OPCxRUN.name = 'OPCxRUN/IPC'
  IF=IF.join(OPCxRUN)
  id = list(tmap.values())
  id.sort()
  IF.index = id
  return IF

def gamestadium(year, teaml, teamd):
  """
  Make a dictionary data structure has team names keys and game numbers played at each parks as home/away.
  """
  url = "https://www.espn.com/mlb/team/schedule/_/name/{}/season/{}/seasontype/2/half/{}"
    
  for t in teaml: 

      for i in [2,1]:
        url_half = url.format(t,year, i)
        s=requests.get(url_half)
        soup=BeautifulSoup(s.content,'lxml')
        table = soup.find_all('tr')
        data = []
        for ta in table[1:]:
          cols = ta.find_all('td')

          cols = [ele.text.strip() for ele in cols]
          try:
            teamname = ta.find('a').get('href')
            full = {('mets',' Mets'),( 'yankees', ' Yankees'), ('white', ' White Sox'),('cubs', ' Cubs'), ('angels', ' Angels'), ('dodgers', ' Dodgers')}
            for i, j in full:
              if i in teamname:
                cols[1] += j
          except:
            pass
          
          data.append([ele for ele in cols[1:]])
    
        if data !=[] :
          dp = pd.DataFrame(data[2:])
          dp.columns =  data[1]
          
        
          
          # remove postpone date using None
          dp= dp.iloc[:,0:5]
          dp = dp.dropna()
  
          for i in range(len(dp)):
            team  = dp.Opponent.values[i]
            result = dp.Result.values[i]
            result = result.split(' ')[0]
            WL = result[0]
            #print(WL)
            scores = result[1:].split('-')
            
            def addscore(ha, b):
              
              try:
                teamd[t][ha][team+' SR'] += int(scores[b])
                teamd[t][ha][team+' AR'] += int(scores[(b+1)%2])
              except:
                teamd[t][ha][team+' SR'] = int(scores[b])
                teamd[t][ha][team+' AR'] = int(scores[(b+1)%2])
                       
            if team[0] == 'v' and (WL in 'WL'):
              team = team[3:]        
              try:
                teamd[t]['Home'][team+' GP'] +=1
              except:            
                teamd[t]['Home'][team+' GP'] =1

               
              if WL == 'W':
                addscore('Home', 0)
              else:
                addscore('Home',1)
                  
            elif team[0] =='@' and (WL in 'WL'):
              team = team[2:]
              try:
                teamd[t]['Away'][team+' GP'] +=1
              except:            
                teamd[t]['Away'][team+' GP'] =1
              if WL == 'W':  
                addscore('Away', 0)
              else:
                addscore('Away',1)         

  
  teaml=[]
  for t in teamd.keys():
    if teamd[t] == {'Away': {}, 'Home': {}}:
      teaml.append(t) 
  
  if teaml == []:
    return teamd
  print(len(teaml), " teams are on processing...")
  
  gamestadium(year,teaml, teamd)      

  return teamd

def solver(year, IF, teamd):
  "Find opc x runs by solving linear equations, and return the joined dataframe."
  
  year = str(year)  
  tmap = {'ari': 'Arizona',
 'atl': 'Atlanta',
 'bal': 'Baltimore',
 'bos': 'Boston',
 'chc': 'Chicago Cubs',
 'chw': 'Chicago White Sox',
 'cin': 'Cincinnati',
 'cle': 'Cleveland',
 'col': 'Colorado',
 'det': 'Detroit',
 'hou': 'Houston',
 'kc': 'Kansas City',
 'laa': 'Los Angeles Angels',
 'lad': 'Los Angeles Dodgers',
 'mia': 'Miami',
 'mil': 'Milwaukee',
 'min': 'Minnesota',
 'nym': 'New York Mets',
 'nyy': 'New York Yankees',
 'oak': 'Oakland',
 'phi': 'Philadelphia',
 'pit': 'Pittsburgh',
 'sd': 'San Diego',
 'sea': 'Seattle',
 'sf': 'San Francisco',
 'stl': 'St. Louis',
 'tb': 'Tampa Bay',
 'tex': 'Texas',
 'tor': 'Toronto',
 'wsh': 'Washington'}
  
  teaml = list(tmap.keys())
  
  pol = [[0 for x in range(30)] for y in range(30)]

  for i in range(30):
    h = teamd[teaml[i]]['Home']
    a = teamd[teaml[i]]['Away']
  
    for j in range(30):
      if tmap[teaml[j]]+' GP' in h.keys():
        s += h[tmap[teaml[j]]+ ' GP']    

      if tmap[teaml[j]]+' GP' in a.keys():
        pol[i][j] = a[tmap[teaml[j]] + ' GP']
    pol[i][i] =s    

  for i in range(30):
    for j in range(30):
      if i!=j:
        pol[i][j] *= -float(IF.loc[tmap[teaml[i]]][year])
        
  print("The determinant of 30x30 matrice must be near zero, ", np.linalg.det(pol)/(80**30))
  
  x= [0]*30
  xl = []
  for i in range(30):
    pol2=pol[:][:]


    pol2[29-i] = [1]*30
    A= np.array(pol2)
    b= [0]*30
    b[29-i] = 30
    b = np.array(b)
    x += np.linalg.solve(A,b)
    xl.append(np.linalg.solve(A,b))

  SF = x/30/IF[year+'IPC']
  print("Ideally sum of the factors is 30, and here is ",sum(SF))
  d = {'mOPCxRUN/IPC':[]}
  for i in range(30):
    d['mOPCxRUN/IPC'].append(SF[i]) 
  dp = pd.DataFrame(d)
  dp.index = IF.index
  
  return IF.join(dp)
      
def main(year):
  teamd = {}
  teaml = ['lad','col','sf','ari','sd','stl','pit','cin','chc','mil','phi','nym','wsh','mia','atl','hou','tex','oak','sea','laa','min','kc','cle','chw','det','nyy', 'tor','bos','tb','bal'] 

  for t in teaml:
    teamd[t] = {'Home' :{}, 'Away':{}}

  teamd = gamestadium(year, teaml, teamd)
  factor = oldOPCxRUN(year)
  return solver(year, factor, teamd)
