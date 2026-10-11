"""Review a discovered item using verified direct sources; no credentials required."""
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from collect import validate_event
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='Publicar un operativo revisado o rechazar una noticia')
p.add_argument('candidate_id');p.add_argument('--reject',action='store_true');p.add_argument('--operation-id');p.add_argument('--date');p.add_argument('--department');p.add_argument('--location',default='');p.add_argument('--reviewer');p.add_argument('--metric',action='append',default=[],help='capturas=3; puede repetirse');args=p.parse_args()
d=json.loads((ROOT/'docs/data/dashboard.json').read_text());decision=json.loads((ROOT/'reviewed-events.json').read_text());c=next((c for c in d['candidates'] if c['id']==args.candidate_id),None)
if not c:p.error('La noticia no existe o ya fue revisada')
if args.reject:
 if args.candidate_id not in decision['rejected_candidate_ids']:decision['rejected_candidate_ids'].append(args.candidate_id)
else:
 if not all([args.operation_id,args.date,args.department,args.reviewer,args.metric]):p.error('Indica operativo, fecha del hecho, departamento, revisor y métricas verificadas')
 metrics={}
 for m in args.metric:
  k,v=m.split('=',1)
  if k in metrics:p.error('Métrica repetida')
  metrics[k]=int(v)
 e={'operation_id':args.operation_id,'event_date':args.date,'department':args.department,'location':args.location,'title':c['title'],'metrics':metrics,'sources':[{'name':c['source'],'url':c['url']}],'reviewed_at':datetime.now(timezone.utc).isoformat(),'reviewed_by':args.reviewer,'candidate_ids':[c['id']]}
 config=json.loads((ROOT/'sources.json').read_text());validate_event(e,config['period_start'])
 if any(x['operation_id']==e['operation_id'] for x in decision['events']):p.error('Operativo ya registrado: agrega esta fuente al registro existente, no una copia')
 decision['events'].append(e)
(ROOT/'reviewed-events.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n');print('Revisión guardada. Ejecuta collect.py --offline para regenerar el dashboard.')
