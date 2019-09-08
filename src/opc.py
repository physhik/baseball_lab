import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json 

def init_factor(year):
  """
  web crawling ESPN park factor. 
  
  The factors have 3 below decimal points, so the precision is rather limited. I would soon upgrade it by scraping official sites and calculating runs at home/away.
  """
  url = 'http://www.espn.com/mlb/stats/parkfactor/_/year/{}'
  url = url.format(year)
  s=requests.get(url).content
  soup=BeautifulSoup(s,'lxml')
  table = soup.find_all('tr')
  data = []
  for t in table[1:]:
    cols = t.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols[1:]])
  
  IF = pd.DataFrame(data[1:])
  IF.columns =  data[0]
  
  opcxrun = []
  for i in range(30):
    opc=30/(29+float(IF.RUNS[i]))
    opcxrun.append(opc*float(IF.RUNS[i]))
  OPCxRUN ={}
  OPCxRUN['RUNS x OPC'] = opcxrun

  dpx=pd.DataFrame(OPCxRUN)
  IF=IF.join(dpx)
  
  parkmap = {'Angel Stadium of Anaheim (Anaheim, California)': 'laa',
 'Busch Stadium (St. Louis, Missouri)': 'stl',
 'Chase Field (Phoenix, Arizona)': 'ari',
 'Citi Field (New York, New York)': 'nym',
 'Citizens Bank Park (Philadelphia, Pennsylvania)': 'phi',
 'Comerica Park (Detroit, Michigan)': 'det',
 'Coors Field (Denver, Colorado)': 'col',
 'Dodger Stadium (Los Angeles, California)': 'lad',
 'Fenway Park (Boston, Massachusetts)': 'bos',
 'Globe Life Park in Arlington (Arlington, Texas)': 'tex',
 'Great American Ball Park (Cincinnati, Ohio)': 'cin',
 'Guaranteed Rate Field (Chicago, Illinois)': 'chw',
 'Kauffman Stadium (Kansas City, Missouri)': 'kc',
 'Marlins Park (Miami, Florida)': 'mia',
 'Miller Park (Milwaukee, Wisconsin)': 'mil',
 'Minute Maid Park (Houston, Texas)': 'hou',
 'Nationals Park (Washington, D.C.)': 'wsh',
 'Oakland Coliseum (Oakland, California)': 'oak',
 'Oracle Park (San Francisco, California)': 'sf',
 'Oriole Park at Camden Yards (Baltimore, Maryland)': 'bal',
 'PNC Park (Pittsburgh, Pennsylvania)': 'pit',
 'Petco Park (San Diego, California)': 'sd',
 'Progressive Field (Cleveland, Ohio)': 'cle',
 'Rogers Centre (Toronto, Ontario)': 'tor',
 'SunTrust Park (Cumberland, GA)': 'atl',
 'T-Mobile Park (Seattle, Washington)': 'sea',
 'Target Field (Minneapolis, Minnesota)': 'min',
 'Tropicana Field (St. Petersburg, Florida)': 'tb',
 'Wrigley Field (Chicago, Illinois)': 'chc',
 'Yankee Stadium (New York, New York)': 'nyy'}
  
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

  l = list(parkmap.values())

  for i in range(30):
    try:
      p = IF['PARK NAME'].values[i] 
      IF['PARK NAME'].values[i] = parkmap[p]
      l.remove(parkmap[p])
    except:
      print("Park name is changed for ", IF['PARK NAME'].values[i])

  for i in range(30):
    p = IF['PARK NAME'].values[i]
    if IF['PARK NAME'].values[i] in parkmap.values():
      continue
    else:
      IF['PARK NAME'].values[i] = l[0]
      
  l = []
  for i in IF['PARK NAME'].values:
    l.append(tmap[i])
  
  IF['PARK NAME'] = l
  IF.columns = ['TEAMS(PARK)', 'RUNS', 'HR', 'H', '2B', '3B', 'BB', 'RUNS x OPC']
  IF.index = l

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
  
          for team in dp.Opponent:
            if 'vs' in team:
              team = team[3:]
              try:
                teamd[t]['Home'][team] +=1
              except:            
                teamd[t]['Home'][team] =1
            else:
              team = team[2:]
              try:
                teamd[t]['Away'][team] +=1
              except:            
                teamd[t]['Away'][team] =1
   

  
  teaml=[]
  for t in teamd.keys():
    if teamd[t] == {'Away': {}, 'Home': {}}:
      teaml.append(t) 
  
  if teaml == []:
    return teamd
  print(len(teaml), " teams are on processing...")
  
  gamestadium(year,teaml, teamd)      

  return teamd

def solver(IF, teamd):
  "Find opc x runs by solving linear equations, and return the joined dataframe."
  
    
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
  
    pol[i][i] = sum(h.values())
    for j in range(30):
      if tmap[teaml[j]] in a.keys():
        pol[i][j] = a[tmap[teaml[j]]]
    

  for i in range(30):
    for j in range(30):
      if i!=j:
        pol[i][j] *= -float(IF.loc[tmap[teaml[i]]].RUNS)
        
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

  P = x/30
  print("Ideally sum of the factors is 30, and here is ",sum(P))
  d = {'RUNS x mOPC':[]}
  for i in range(30):
    d['RUNS x mOPC'].append(P[i])
  dp = pd.DataFrame(d)
  IF = IF.sort_values(by='TEAMS(PARK)')
  IF.set_index('TEAMS(PARK)', inplace=True)
  
  dp.index = IF.index
  
  return IF.join(dp)
      
def main(year):
  teamd = {}
  teaml = ['lad','col','sf','ari','sd','stl','pit','cin','chc','mil','phi','nym','wsh','mia','atl','hou','tex','oak','sea','laa','min','kc','cle','chw','det','nyy', 'tor','bos','tb','bal'] 

  for t in teaml:
    teamd[t] = {'Home' :{}, 'Away':{}}

  teamd = gamestadium(year, teaml, teamd)
  factor = init_factor(year)
  return solver( factor , teamd)
