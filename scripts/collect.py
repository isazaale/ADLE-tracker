"""Daily public-source discovery. Ambiguous news never become official totals."""
import argparse, hashlib, json, re, sys, time, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
 return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
def safe_url(url):
 p=urlparse(url); return p.scheme=='https' and p.hostname and (p.hostname.endswith('.gov.co') or p.hostname.endswith('.mil.co') or p.hostname in {'news.google.com','justice.gov','www.justice.gov'})
def identify(title):
 t=norm(title)
 if re.search(r'balance|en lo que va|durante el|este ano|este mes|acumulad|%|por ciento',t):return [],'Balance acumulado o porcentaje'
 metrics=[]
 patterns={'capturas':r'\b(\d+)\s+(?:presuntos?\s+)?(?:personas?\s+)?(?:capturad[oa]s?|capturas)\b','bajas':r'\b(\d+)\s+(?:presuntos?\s+)?(?:integrantes?\s+)?(?:abatid[oa]s?|muertos? en combate)\b','extradiciones':r'\b(\d+)\s+(?:personas?\s+)?extraditad[oa]s?\b','rescatados':r'\b(\d+)\s+(?:personas?\s+)?(?:secuestrad[oa]s?\s+)?rescatad[oa]s?\b','armas':r'\b(\d+)\s+armas\b'}
 if re.search(r'para (?:su )?extradicion|con fines de extradicion|solicitud de extradicion',t):patterns.pop('extradiciones')
 for key,p in patterns.items():
  vals=re.findall(p,t)
  if len(vals)==1:metrics.append({'metric':key,'quantity':int(vals[0])})
 return metrics,'Requiere fecha del hecho, alcance y revisión de duplicados'
def get_feed(source):
 result={'name':source['name'],'url':source['url'],'status':'error','articles':0}
 found=[]
 try:
  request=urllib.request.Request(source['url'],headers={'User-Agent':'ADLETracker/1.0 public-news-monitor (+https://github.com/isazaale/ADLE-tracker)'})
  with urllib.request.urlopen(request,timeout=20) as response: tree=ET.fromstring(response.read(4_000_000))
  items=tree.findall('.//item')
  for item in items[:60]:
   title=item.findtext('title','').strip(); url=item.findtext('link','').strip()
   if not safe_url(url):continue
   metrics,reason=identify(title)
   if not metrics and not re.search(r'captur|extrad|abatid|rescat|incaut|secuestro|homicid|extors',norm(title)):continue
   found.append({'id':hashlib.sha256(url.encode()).hexdigest()[:20],'title':title,'url':url,'source':source['name'],'published_raw':item.findtext('pubDate',''),'detected_at':datetime.now(timezone.utc).isoformat(),'suggested_metrics':metrics,'review_reason':reason,'status':'pending'})
  result.update(status='ok',articles=len(items))
 except Exception as e:result['error']=str(e)[:240]
 return result,found
def validate_event(e,start):
 date=datetime.strptime(e['event_date'],'%Y-%m-%d').date()
 if date<datetime.strptime(start,'%Y-%m-%d').date():raise ValueError('Evento anterior al periodo')
 if date>datetime.now(timezone.utc).date():raise ValueError('Fecha futura')
 if not e.get('operation_id') or not e.get('reviewed_at') or not e.get('reviewed_by'):raise ValueError('Falta revisión o identificador de operativo')
 if not e.get('sources') or not all(safe_url(s['url']) and urlparse(s['url']).hostname!='news.google.com' for s in e['sources']):raise ValueError('Falta fuente directa HTTPS')
 for k,v in e['metrics'].items():
  if k not in {'capturas','bajas','extradiciones','rescatados','armas'} or type(v)!=int or v<0:raise ValueError('Métrica o cantidad inválida')
 return e

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
 config=json.loads((ROOT/'sources.json').read_text());out=ROOT/'docs/data'
 prior=json.loads((out/'dashboard.json').read_text()) if (out/'dashboard.json').exists() else {}
 candidates={c['id']:c for c in prior.get('candidates',[])}
 statuses=[]
 if not args.offline:
  with ThreadPoolExecutor(max_workers=4) as pool:
   for status,items in pool.map(get_feed,config['feeds']):
    statuses.append(status)
    for c in items:
     if c['id'] not in candidates:candidates[c['id']]=c
 decisions=json.loads((ROOT/'reviewed-events.json').read_text())
 events=[];seen=set();reviewed_ids=set()
 for e in decisions['events']:
  validate_event(e,config['period_start'])
  if e['operation_id'] in seen:raise ValueError('Operativo duplicado: '+e['operation_id'])
  seen.add(e['operation_id']);events.append(e);reviewed_ids.update(e.get('candidate_ids',[]))
 rejected=set(decisions.get('rejected_candidate_ids',[]))
 output={'period_start':config['period_start'],'last_attempt':datetime.now(timezone.utc).isoformat(),'last_success':datetime.now(timezone.utc).isoformat() if any(s['status']=='ok' for s in statuses) else prior.get('last_success'),'collection_status':'offline' if args.offline else ('ok' if statuses and all(s['status']=='ok' for s in statuses) else 'partial' if any(s['status']=='ok' for s in statuses) else 'error'),'sources':statuses or prior.get('sources',[]),'events':events,'candidates':list(c for c in candidates.values() if c['id'] not in reviewed_ids|rejected),'official_series':decisions.get('official_series',[])}
 out.mkdir(parents=True,exist_ok=True);(out/'dashboard.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'events':len(events),'pending':len(output['candidates']),'collection_status':output['collection_status']}))
 if not args.offline and output['collection_status']=='error':sys.exit(2)
if __name__=='__main__':main()
