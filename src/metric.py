import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import io

def get_soup(start_season, end_season, startdate, enddate, league, qual, ind):
    """
    fangraph web crawler 
    fangraph_pitching_leader.py
    modified from https://github.com/jldbc/pybaseball/blob/master/pybaseball/pitching_leaders.py
    you can change the table by modifying url format 
    """
    url = "http://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg={}&qual={}&type=c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,-1&season={}&month=1000&season1={}&startdate={}&enddate={}&ind={}&team=&rost=&age=&filter=&players=&page=1_100000"
    #url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg={}&qual={}&type=c,3,4,5,6,7,9,10,11,12,13,14,15&season={}&month=0&season1={}&ind={}'
    url = url.format(league, qual, end_season, start_season, startdate, enddate, ind)
    s=requests.get(url).content
    #print(s)
    return BeautifulSoup(s, "lxml")

def get_table(soup, ind):
    """
    modified from https://github.com/jldbc/pybaseball/blob/master/pybaseball/pitching_leaders.py
    """
    table = soup.find('table', {'class': 'rgMasterTable'})

    data = []
    # pulls headings from the fangraphs table
    headings = []
    headingrows = table.find_all('th')
    
    for row in headingrows[1:]:
        headings.append(row.text.strip())
    
    data.append(headings)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    dict = {}
    dict['299'] = ['fangraph_playerid']

    for row in rows:
        cols = row.find_all('td')
        
        for link in row.find_all('a'):
          id = link.get('href').split('=')[1].split('&')[0]
          if id != 'all':
            dict['299'].append(id)
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols[1:]])

    data = pd.DataFrame(data)
    dp=pd.DataFrame(dict)
    data= data.join(dp)

    data = data.rename(columns=data.iloc[0])

    data = data.reindex(data.index.drop(0))

    # replace emptry strings with NaN
    data.replace(r'^\s*$', np.nan, regex=True, inplace = True)

    # convert all percent strings to proper percetages
    percentages = ['Contact% (pi)', 'Zone% (pi)','Z-Contact% (pi)','O-Contact% (pi)','Swing% (pi)','Z-Swing% (pi)','O-Swing% (pi)','SL% (pi)','SI% (pi)','SB% (pi)','KN% (pi)','FS% (pi)','FC% (pi)','FA% (pi)','CU% (pi)','CS% (pi)','CH% (pi)','TTO%','Hard%','Med%','Soft%','Oppo%','Cent%','Pull%','K-BB%','Zone% (pfx)','Contact% (pfx)','Z-Contact% (pfx)','O-Contact% (pfx)','Swing% (pfx)','Z-Swing% (pfx)','O-Swing% (pfx)','UN% (pfx)','KN% (pfx)','SC% (pfx)','CH% (pfx)','EP% (pfx)','KC% (pfx)','CU% (pfx)','SL% (pfx)','SI% (pfx)','FO% (pfx)','FS% (pfx)','FC% (pfx)','FT% (pfx)','FA% (pfx)','BB%','K%','SwStr%','F-Strike%','Zone%','Contact%','Z-Contact%','O-Contact%','Swing%','Z-Swing%','O-Swing%','XX%','KN%','SF%','CH%','CB%','CT%','SL%','FB%','BUH%','IFH%','HR/FB','IFFB%','GB%','LD%','LOB%', 'XX% (pi)', 'PO%']
    #percentages = ['LOB%', 'GB%', 'HR/FB']
    for col in percentages:
        # skip if column is all NA (happens for some of the more obscure stats + in older seasons)
        if not data[col].empty:
            if pd.api.types.is_string_dtype(data[col]):
                data[col] = data[col].astype(str).str.strip(' %')
                data[col] = data[col].astype(str).str.strip('%')
                data[col] = data[col].astype(float)/100.
        else:
            pass

    #convert everything except name and team to numeric
    cols_to_numeric = [col for col in data.columns if col not in ['Name', 'Team', 'Age Rng', 'Dollars']]
    data[cols_to_numeric] = data[cols_to_numeric].astype(float)

    #sort by WAR and wins so best players float to the top
    data = data.sort_values(['WAR', 'W'], ascending=False)
    #put WAR at the end because it looks better
    cols = data.columns.tolist()
    cols.insert(7, cols.pop(cols.index('WAR')))
    data = data.reindex(columns= cols)
    #print(len(dict['playerid']))
    
    #dp.set_index('fg_id', inplace=True)
    
    return data

def fangraphs_stats(start_season, end_season, start_date, end_date, league='all', qual=1, ind=1):
    """
    Get season-level pitching data from FanGraphs. 
    ARGUMENTS:
    start_season : int : first season you want data for (or the only season if you do not specify an end_season)
    end_season : int : final season you want data for 
    league : "all", "nl", or "al"
    qual: minimum number of pitches thrown to be included in the data (integer). Use the string 'y' for fangraphs default.
    ind : int : =1 if you want individual season-level data, =0 if you want a player's aggreagate data over all seasons in the query
    
    copied from https://github.com/jldbc/pybaseball/blob/master/pybaseball/pitching_leaders.py

    """
    soup = get_soup(start_season,  end_season, start_date, end_date, league=league, qual=qual, ind=ind)
    table = get_table(soup, ind)
    return table
    
# brl, con tables from statcast

def statcast_stats(start_year, end_year, start_date, end_date):
  seasons = ""
  for year in range(start_year, end_year+1):
    seasons += str(year) + "%7C"
  url_con ="https://baseballsavant.mlb.com/statcast_search/csv?hfPT=&hfAB=&hfBBT=fly%5C.%5C.ball%7Cpopup%7Cline%5C.%5C.drive%7Cground%5C.%5C.ball%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7C&hfC=&{}&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&game_date_lt={}&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfPull=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=xwoba&player_event_sort=h_launch_speed&sort_order=asc&min_pas=0#results"
  url_brl = "https://baseballsavant.mlb.com/statcast_search/csv?hfPT=&hfAB=&hfBBT=fly%5C.%5C.ball%7Cpopup%7Cline%5C.%5C.drive%7Cground%5C.%5C.ball%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7C&hfC=&{}&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=6%7C&game_date_gt={}&game_date_lt={}&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfPull=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=xwoba&player_event_sort=h_launch_speed&sort_order=asc&min_pas=0#results"
  url_con_wo_hr = "https://baseballsavant.mlb.com/statcast_search/csv?hfPT=&hfAB=single%7Cdouble%7Ctriple%7Cfield%5C.%5C.out%7Cdouble%5C.%5C.play%7Cgrounded%5C.%5C.into%5C.%5C.double%5C.%5C.play%7Cfielders%5C.%5C.choice%7Cfielders%5C.%5C.choice%5C.%5C.out%7Cforce%5C.%5C.out%7Csac%5C.%5C.bunt%7Csac%5C.%5C.bunt%5C.%5C.double%5C.%5C.play%7Csac%5C.%5C.fly%7Csac%5C.%5C.fly%5C.%5C.double%5C.%5C.play%7Ctriple%5C.%5C.play%7C&hfBBT=fly%5C.%5C.ball%7Cpopup%7Cline%5C.%5C.drive%7Cground%5C.%5C.ball%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7C&hfC=&{}&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&game_date_lt={}&hfInfield=&team=&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfPull=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=xwoba&player_event_sort=h_launch_speed&sort_order=asc&min_pas=0#results"
  
  s_con=requests.get(url_con.format(seasons, start_date, end_date))
  s_brl=requests.get(url_brl.format(seasons, start_date, end_date))
  s_con_wo_hr = requests.get(url_con_wo_hr.format(year, start_date, end_date))
  con= pd.read_csv(io.StringIO(s_con.text))
  brl = pd.read_csv(io.StringIO(s_brl.text))
  con_wohr = pd.read_csv(io.StringIO(s_con_wo_hr.text)) 
  print("size of con, brl, con_wohr:", len(con), len(brl), len(con_wohr))
  return con, brl, con_wohr


def new_metric(start_year, end_year, start_date, end_date):
  
  idmap = pd.read_csv("../assets/master.csv", encoding="ISO-8859-1") 
  
  con, brl, con_wohr= statcast_stats(start_year, end_year, start_date, end_date)
  fg  = fangraphs_stats(start_year, end_year, start_date, end_date)
  con.set_index('player_id', inplace=True)
  con_wohr.set_index('player_id', inplace=True)
  brl.set_index('player_id', inplace=True)
  idmap.set_index('fg_id', inplace=True)
  fg.set_index('fangraph_playerid', inplace=True)
  
  dict = {'fangraph_playerid':[], 'mlb_id':[]}
  for id in fg.index:

    try:
      dict['mlb_id'].append(idmap.loc[str(int(id))].mlb_id)
      dict['fangraph_playerid'].append(id)

    except:
      import numpy as np
      #dict['mlb_id'].append(np.nan)
      print("fagraphs id and name removed:", id, fg.loc[id].Name, "with innings", fg.loc[id].IP)

  idp=pd.DataFrame(dict)
  idp.set_index('fangraph_playerid', inplace=True)
  fg=fg.loc[idp.index]
  fg= fg.join(idp, on='fangraph_playerid')
  fg.set_index('mlb_id', inplace=True)
  
  
  
  fg.IP=fg.IP.astype(int)+(fg.IP-fg.IP.astype(int))*10*1/3
  
  fg.ERA = fg.ER/fg.IP*9
  ra = fg.R/fg.IP*9
  ra.name ='RA'
  fg = fg.join(ra, on='mlb_id')
    
  vfip = (13*fg.HR+ 3*(fg.BB+fg.HBP)-2*fg.SO)/fg.IP
  cfip = (-sum(vfip*fg.IP) + sum(fg.ERA*fg.IP))/sum(fg.IP)
  rcfip = (-sum(vfip*fg.IP) + sum(fg.RA*fg.IP))/sum(fg.IP)
  
  fg.FIP = vfip+cfip
  rfip = vfip + rcfip
  rfip.name = "rFIP"
  fg = fg.join(rfip, on='mlb_id')
  
  
  
  fg=fg[fg.IP>0]
  
  
  
  # brls
  dict = {'player_id':[], 'brls':[]}
  for id in con.index:
    dict['player_id'].append(id)
    try:
      dict['brls'].append(brl.loc[id].pitches)
    except:
      dict['brls'].append(0)
    
  brls=pd.DataFrame(dict)
  brls.set_index('player_id', inplace=True)
  con=con.join(brls, on='player_id')

  temp=con_wohr.loc[fg.index]
  temp=temp.dropna()
  con = con.loc[temp.index]
  b = fg.loc[temp.index] 
  b = b.join(brls, on='mlb_id')
  


  lgc = sum(con.loc[b.index].xwoba)/len(con.loc[b.index].xwoba) * sum(con.loc[b.index].pitches)*9/(sum(b.IP)-sum(b.SO)/3)
  lgc_wohr = sum(con_wohr.loc[b.index].xwoba)/len(con_wohr.loc[b.index].xwoba) * sum(con_wohr.loc[b.index].pitches)*9/(sum(b.IP)-sum(b.SO)/3)
  c = con.loc[b.index].xwoba * con.loc[b.index].pitches*9/(b.IP-b.SO/3)*cfip/lgc
  cr = con.loc[b.index].xwoba * con.loc[b.index].pitches*9/(b.IP-b.SO/3)*rcfip/lgc
  c_wohr = con_wohr.loc[b.index].xwoba * con_wohr.loc[b.index].pitches*9/(b.IP-b.SO/3)*cfip/lgc_wohr
  cr_wohr = con_wohr.loc[b.index].xwoba * con_wohr.loc[b.index].pitches*9/(b.IP-b.SO/3)*rcfip/lgc_wohr

  
  ratio = sum(b.HR)/sum(con.loc[b.index].brls)
  bhr = ratio*con.loc[b.index].brls
  xnfip = (13*ratio*con.loc[b.index].brls+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + c
  xnfip_wohr = (13*ratio*con.loc[b.index].brls+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + c_wohr  
  nfip = (13*b.HR+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + c
  nfip_wohr = (13*b.HR+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + c_wohr

  rxnfip = (13*ratio*con.loc[b.index].brls+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + cr
  rxnfip_wohr = (13*ratio*con.loc[b.index].brls+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + cr_wohr  
  rnfip = (13*b.HR+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + cr
  rnfip_wohr = (13*b.HR+ 3*(b.BB+b.HBP)-2*b.SO)/b.IP + cr_wohr
  
  nfip.name = 'nFIP'
  xnfip.name  ='xnFIP'
  nfip_wohr.name = 'nFIPwo'
  xnfip_wohr.name = 'xnFIPwo'
  rnfip.name = 'rnFIP'
  rnfip_wohr.name ='rnFIPwo'
  rxnfip.name  ='rxnFIP'
  rxnfip_wohr.name ='rxnFIPwo'
  c.name='cnfip'
  cr.name='crnfip'
  c_wohr.name='cnfipwo'
  cr_wohr.name='crnfipwo'
  
  b=b.join(nfip, on='mlb_id').sort_values(by='WAR', ascending = False)
  b=b.join(xnfip, on='mlb_id')
  b=b.join(xnfip_wohr, on='mlb_id')
  b=b.join(nfip_wohr, on='mlb_id')
  b=b.join(rnfip, on='mlb_id')
  b=b.join(rnfip_wohr, on='mlb_id')
  b=b.join(rxnfip, on='mlb_id')
  b=b.join(rxnfip_wohr, on='mlb_id') 
  b= b.join(c, on='mlb_id')
  b= b.join(c_wohr, on='mlb_id')
  b= b.join(cr, on='mlb_id')
  b= b.join(cr_wohr, on='mlb_id')

  return b

