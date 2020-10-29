from opc import *

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
