import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect import identify, validate_event, safe_url
class ExtractionTests(unittest.TestCase):
 def test_extradition_request_not_actual(self):
  result,_=identify('3 capturados con fines de extradición')
  self.assertEqual(result,[{'metric':'capturas','quantity':3}])
 def test_neutralized_is_not_killed(self):self.assertEqual(identify('4 integrantes neutralizados')[0],[])
 def test_aggregate_excluded(self):self.assertEqual(identify('Balance: 350 capturados este mes')[0],[])
 def test_unambiguous_title(self):self.assertEqual(identify('5 presuntos capturados en Medellín')[0],[{'metric':'capturas','quantity':5}])
 def test_unsafe_sources(self):self.assertFalse(safe_url('http://localhost/'));self.assertFalse(safe_url('https://fake.gov.co.evil.com'))
 def test_official_international_and_military_sources(self):
  self.assertTrue(safe_url('https://www.ejercito.mil.co/noticia'))
  self.assertTrue(safe_url('https://www.justice.gov/es/noticia'))
  self.assertFalse(safe_url('https://www.justice.gov.evil.com/noticia'))
  self.assertFalse(safe_url('https://fake.mil.co.evil.com/noticia'))
 def test_review_and_date_required(self):
  with self.assertRaises(ValueError):validate_event({'event_date':'2026-01-01'},'2026-08-07')
class ReviewedDataTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((Path(__file__).resolve().parents[1]/'reviewed-events.json').read_text())
 def test_unique_operations_across_date_types(self):
  rows=self.data['events']+self.data['operation_reports'];ids=[x['operation_id'] for x in rows]
  self.assertEqual(len(ids),len(set(ids)))
  self.assertTrue(all('event_date' not in x for x in self.data['operation_reports']))
 def test_revised_azarias_replaces_preliminary_counts(self):
  rows=[x for x in self.data['events'] if x['operation_id'].startswith('azarias-')]
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['metrics']['bajas'],24)
 def test_orders_do_not_become_completed_extraditions(self):
  self.assertEqual(sum(x['metrics'].get('extradiciones',0) for x in self.data['events']+self.data['operation_reports']),9)
  self.assertTrue(any(b['metric']=='extradiciones' and b['value']==46 for b in self.data['national_balances']))
  self.assertTrue(any(b['metric']=='extradiciones_activas' and b['value']==4 for b in self.data['national_balances']))
  self.assertTrue(any(b['metric']=='ordenes_extradicion' and b['value']==119 for b in self.data['national_balances']))
if __name__=='__main__':unittest.main()
