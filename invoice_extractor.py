import re
import fitz

MONEY=r'([0-9][0-9,]*(?:\.[0-9]{1,2})?)'

def pdf_text(data:bytes)->str:
 doc=fitz.open(stream=data,filetype='pdf')
 return '\n'.join(page.get_text() for page in doc)

def image_text(data:bytes)->str:
 try:
  import pytesseract
  from PIL import Image
  import io
  return pytesseract.image_to_string(Image.open(io.BytesIO(data)))
 except Exception:
  return ''

def _first(pattern,text,default=''):
 m=re.search(pattern,text,re.I|re.M)
 return m.group(1).strip() if m else default

def parse_invoice(text:str)->dict:
 supplier=_first(r'(?:Supplier|Vendor|From)\s*[:\-]\s*(.+)',text)
 inv=_first(r'(?:Invoice\s*(?:No\.?|Number)|Inv\.?\s*No\.?)\s*[:#\-]?\s*([A-Z0-9\-/]+)',text)
 date=_first(r'(?:Invoice\s*Date|Date)\s*[:\-]\s*([0-9]{1,4}[\-/][0-9]{1,2}[\-/][0-9]{1,4})',text)
 currency_token=r'(?:[$€£₹]|(?:EUR|USD|INR|GBP))?'
 subtotal=_first(r'(?:Subtotal|Net)\s*[:\-]?\s*'+currency_token+r'\s*'+MONEY,text,'0')
 vat=_first(r'(?:VAT|Tax|GST)\s*[:\-]?\s*'+currency_token+r'\s*'+MONEY,text,'0')
 total=_first(r'^(?:Grand\s*Total|Total)\s*[:\-]?\s*'+currency_token+r'\s*'+MONEY,text,'0')
 desc=_first(r'(?:Description|For)\s*[:\-]\s*(.+)',text)
 currency='EUR' if '€' in text or re.search(r'\bEUR\b',text,re.I) else 'USD' if '$' in text or re.search(r'\bUSD\b',text,re.I) else 'INR' if '₹' in text or re.search(r'\bINR\b',text,re.I) else 'GBP' if '£' in text or re.search(r'\bGBP\b',text,re.I) else 'USD'
 num=lambda s: float(str(s).replace(',','') or 0)
 return {'supplier_name':supplier,'invoice_number':inv,'invoice_date':date,'subtotal':num(subtotal),'vat':num(vat),'total':num(total),'currency':currency,'description':desc,'raw_text':text}

def validate(d):
 issues=[]
 for f in ['supplier_name','invoice_number','invoice_date','total']:
  if not d.get(f):issues.append(f'Missing {f.replace("_"," ")}')
 if d.get('subtotal') and d.get('total'):
  expected=d['subtotal']+d.get('vat',0)
  if abs(expected-d['total'])>max(1,0.01*d['total']):issues.append('Subtotal + VAT does not match total')
 return issues
