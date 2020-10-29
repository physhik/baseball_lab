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
      for type in ['batting', 'pitching']:
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
      runmap[(year, 'W', han)] = dp.W.values
      
  dp2 = pd.DataFrame(runmap)

  dp2.index = dp.index.values
  return dp2

def initial_factors(start, end):
  IF = {}
  n = 4*2
  dp = runs(start, end)
  for team in dp.index:
    for year in range(start,end+1):
      i = year - start
      try:
        IF[str(year)].append(((int(dp.loc[team][n*i])+int(dp.loc[team][n*i+1]))/int(dp.loc[team][n*i+2]))/((int(dp.loc[team][n*i+4])+int(dp.loc[team][n*i+5]))/int(dp.loc[team][n*i+6])))
      except:
        IF[str(year)]=[((int(dp.loc[team][n*i])+int(dp.loc[team][n*i+1]))/int(dp.loc[team][n*i+2]))/((int(dp.loc[team][n*i+4])+int(dp.loc[team][n*i+5]))/int(dp.loc[team][n*i+6]))]
        
      hwp = int(dp.loc[team][n*i+3])/int(dp.loc[team][n*i+2])
      awp = int(dp.loc[team][n*i+7])/int(dp.loc[team][n*i+6])
      ipc = (18.5 - hwp)/(18.5- awp)
      
      try:
        IF[str(year)+'IPC'].append(ipc)
      except:
        IF[str(year)+'IPC'] = [ipc]
        
      
  dpif = pd.DataFrame(IF)
  dpif.index = dp.index.values
  return dpif


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
  
  poltr = [[0 for x in range(60)] for y in range(60)]

  for i in range(30):
    s=0
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
  
  
  #for i in range(30):
   # for j in range(30):
    #  poltr[i][j]=IF.loc[tmap[teaml[i]]]['SF']*
  
  
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

  SF = x/30 / IF[year+'IPC']


  print("Ideally sum of the factors is 30, and here is ",sum(SF))
  d = {'mOPCxRUN/IPC':[]}
  for i in range(30):
    d['mOPCxRUN/IPC'].append(SF[i])  
  dp = pd.DataFrame(d)
  dp.index = IF.index
  
  return IF.join(dp)



def oldBP(year, teamd, new = False):
      
  rdp = runs(year,year)
  factor = oldOPCxRUN(year) 
  IF = solver(year, factor, teamd)
  
  if new:
    SF = IF['mOPCxRUN/IPC']
    SF1 = 1- (IF['mOPCxRUN/IPC']-1)/29
  else:
    SF = IF['OPCxRUN/IPC']
    SF1 = 1- (IF['OPCxRUN/IPC']-1)/29
  year = str(year)
  RAL = (sum([int(x) for x in rdp[(year,'batting','home')]])+sum([int(x) for x in rdp[(year,'pitching','home')]])) / sum([int(x) for x in rdp[year,'GP','home']])
  TPR = 1
  TBR = ([int(x) for x in rdp[(year,'batting','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'batting','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TPR-1)/29) / RAL
  TPR = ([int(x) for x in rdp[(year,'pitching','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'pitching','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TBR-1)/29) / RAL
  TBR = ([int(x) for x in rdp[(year,'batting','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'batting','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TPR-1)/29) / RAL
  TPR = ([int(x) for x in rdp[(year,'pitching','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'pitching','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TBR-1)/29) / RAL
  TBR = ([int(x) for x in rdp[(year,'batting','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'batting','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TPR-1)/29) / RAL
  TPR = ([int(x) for x in rdp[(year,'pitching','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'pitching','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TBR-1)/29) / RAL
  TBR = ([int(x) for x in rdp[(year,'batting','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'batting','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TPR-1)/29) / RAL
  TPR = ([int(x) for x in rdp[(year,'pitching','away')]]/SF1/[int(x) for x in rdp[(year,'GP','away')]] + [int(x) for x in rdp[(year,'pitching','home')]]/SF/[int(x) for x in rdp[(year,'GP','home')]])  * (1+(TBR-1)/29) / RAL
   
  
  BPF = (SF+SF1)/(2*(1+(TPR-1)/29)) 
  PPF = (SF+SF1)/(2*(1+(TBR-1)/29)) 
  
  TBR.name = 'TBR'
  TPR.name = 'TPR'
  BPF.name = 'BPF'
  PPF.name = 'PPF'
  for factor in [TBR, TPR, BPF, PPF]:
    IF=pd.concat([IF, factor], axis=1)
  return IF


  
def main(year):
  teamd = {}
  teaml = ['lad','col','sf','ari','sd','stl','pit','cin','chc','mil','phi','nym','wsh','mia','atl','hou','tex','oak','sea','laa','min','kc','cle','chw','det','nyy', 'tor','bos','tb','bal'] 

  for t in teaml:
    teamd[t] = {'Home' :{}, 'Away':{}}

  teamd = gamestadium(year, teaml, teamd)
  factor = oldOPCxRUN(year)
  return solver(year, factor, teamd)