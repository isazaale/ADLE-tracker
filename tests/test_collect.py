import sys,unittest
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
 def test_review_and_date_required(self):
  with self.assertRaises(ValueError):validate_event({'event_date':'2026-01-01'},'2026-08-07')
if __name__=='__main__':unittest.main()
