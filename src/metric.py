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
    #https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=y&type=8&season=2017&month=1000&season1=2019&ind=0&team=&rost=&age=&filter=&players=&startdate=2017-10-03&enddate=2019-10-03
    
    url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg={}&qual={}&type=c%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%2C33%2C34%2C35%2C36%2C37%2C38%2C39%2C40%2C41%2C42%2C43%2C44%2C45%2C46%2C47%2C48%2C50%2C51%2C52%2C53%2C54%2C55%2C56%2C57%2C58%2C59%2C60%2C61%2C62%2C63%2C64%2C65%2C66%2C67%2C68%2C69%2C70%2C71%2C72%2C73%2C74%2C75%2C76%2C77%2C78%2C79%2C80%2C81%2C82%2C83%2C84%2C85%2C86%2C87%2C88%2C89%2C90%2C91%2C92%2C93%2C94%2C95%2C96%2C97%2C98%2C99%2C100%2C101%2C102%2C103%2C104%2C105%2C106%2C107%2C108%2C109%2C110%2C111%2C112%2C113%2C114%2C115%2C116%2C117%2C118%2C119%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C145%2C146%2C147%2C148%2C149%2C150%2C151%2C152%2C153%2C154%2C155%2C156%2C157%2C158%2C159%2C160%2C161%2C162%2C163%2C164%2C165%2C166%2C167%2C168%2C169%2C170%2C171%2C172%2C173%2C174%2C175%2C176%2C177%2C178%2C179%2C180%2C181%2C182%2C183%2C184%2C185%2C186%2C187%2C188%2C189%2C190%2C191%2C192%2C193%2C194%2C195%2C196%2C197%2C198%2C199%2C200%2C201%2C202%2C203%2C204%2C205%2C206%2C207%2C208%2C209%2C210%2C211%2C212%2C213%2C214%2C215%2C216%2C217%2C218%2C219%2C220%2C221%2C222%2C223%2C224%2C225%2C226%2C227%2C228%2C229%2C230%2C231%2C232%2C233%2C234%2C235%2C236%2C237%2C238%2C239%2C240%2C241%2C242%2C243%2C244%2C245%2C246%2C247%2C248%2C249%2C250%2C251%2C252%2C253%2C254%2C255%2C256%2C257%2C258%2C259%2C260%2C261%2C262%2C263%2C264%2C265%2C266%2C267%2C268%2C269%2C270%2C271%2C272%2C273%2C274%2C275%2C276%2C277%2C278%2C279%2C280%2C281%2C282%2C283%2C284%2C285%2C286%2C287%2C288%2C289%2C290%2C291%2C292%2C293%2C294%2C295%2C296%2C297%2C298%2C299%2C-1&season={}&month=1000&season1={}&ind={}&team=0&rost=0&age=0&filter=&players=0&startdate={}&enddate={}&page=1_100000"
    url = url.format(league, qual, start_season, end_season, ind, startdate, enddate)

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

