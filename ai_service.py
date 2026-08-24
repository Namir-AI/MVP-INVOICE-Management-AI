CATEGORIES=['Materials','Labour','Equipment','Transport','Subcontractor','Professional Services','Utilities','Other']

KEYWORDS={
 'Materials':['concrete','cement','steel','rebar','timber','brick','paint','material'],
 'Labour':['labour','labor','workers','manpower','wages'],
 'Equipment':['crane','excavator','equipment','rental','generator'],
 'Transport':['transport','delivery','freight','truck','logistics'],
 'Subcontractor':['subcontract','installation','civil works'],
 'Professional Services':['consulting','architect','engineering','survey'],
 'Utilities':['electricity','water','utility','internet'],
}

def classify(text):
 t=text.lower()
 scores={c:sum(k in t for k in ks) for c,ks in KEYWORDS.items()}
 best=max(scores,key=scores.get)
 return best if scores[best] else 'Other'

def match_project(text,projects):
 t=text.lower(); matches=[]
 for pid,name,desc in projects:
  score=0
  for token in name.lower().split()+desc.lower().replace(',','').split():
   if len(token)>4 and token in t: score+=1
  if name.lower() in t:score+=5
  matches.append((score,pid,name))
 matches.sort(reverse=True)
 if matches[0][0]>=5:return matches[0][1],matches[0][2],0.98,None
 if matches[0][0]>=2 and (len(matches)==1 or matches[0][0]>matches[1][0]):return matches[0][1],matches[0][2],0.78,None
 options=', '.join(m[2] for m in matches[:2])
 return None,None,0.45,f'Project assignment is uncertain. Please select the correct project ({options}).'

def answer_report_question(question, rows):
 q=question.lower()
 if 'p&l' in q or 'profit' in q or 'loss' in q:
  for r in rows:
   if r['name'].lower() in q:return f"{r['name']} — Income: {r['income']:,.2f}, Expenses: {r['expenses']:,.2f}, P&L: {r['pnl']:,.2f}"
  return '\n'.join(f"{r['name']}: P&L {r['pnl']:,.2f}" for r in rows)
 if 'expense' in q:
  for r in rows:
   if r['name'].lower() in q:return f"{r['name']} expenses: {r['expenses']:,.2f}"
  return '\n'.join(f"{r['name']}: {r['expenses']:,.2f}" for r in rows)
 return 'Try: “Show expenses for Project Alpha” or “Give me P&L for Project Beta”.'
