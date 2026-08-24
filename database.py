import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'data' / 'demo.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS projects(
 id INTEGER PRIMARY KEY, name TEXT UNIQUE, description TEXT, status TEXT DEFAULT 'Active');
CREATE TABLE IF NOT EXISTS invoices(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 supplier_name TEXT, invoice_number TEXT, invoice_date TEXT,
 subtotal REAL, vat REAL, total REAL, currency TEXT,
 description TEXT, category TEXT, project_id INTEGER,
 project_confidence REAL, status TEXT, original_filename TEXT,
 FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS income(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 project_id INTEGER, date TEXT, amount REAL, description TEXT,
 FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE IF NOT EXISTS clarifications(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 invoice_id INTEGER, question TEXT, answer TEXT, status TEXT,
 FOREIGN KEY(invoice_id) REFERENCES invoices(id));
'''

PROJECTS = [
 (1,'Project Alpha','Residential tower, Riverside site','Active'),
 (2,'Project Beta','Commercial fit-out, Central district','Active'),
 (3,'Project Gamma','Warehouse and logistics hub, North zone','Active'),
 (4,'Project Delta','Road and drainage package, East zone','Active'),
]
INCOME = [
 (1,'2026-07-01',180000,'Client progress payment'),
 (2,'2026-07-05',125000,'Client progress payment'),
 (3,'2026-07-10',210000,'Client progress payment'),
 (4,'2026-07-12',95000,'Client progress payment'),
]

def connect():
 DB_PATH.parent.mkdir(parents=True, exist_ok=True)
 return sqlite3.connect(DB_PATH)

def init_db():
 with connect() as con:
  con.executescript(SCHEMA)
  con.executemany('INSERT OR IGNORE INTO projects(id,name,description,status) VALUES (?,?,?,?)', PROJECTS)
  if con.execute('SELECT COUNT(*) FROM income').fetchone()[0] == 0:
   con.executemany('INSERT INTO income(project_id,date,amount,description) VALUES (?,?,?,?)', INCOME)

def list_projects():
 with connect() as con:
  return con.execute('SELECT id,name,description FROM projects ORDER BY id').fetchall()

def save_invoice(d):
 with connect() as con:
  cur=con.execute('''INSERT INTO invoices(supplier_name,invoice_number,invoice_date,subtotal,vat,total,currency,description,category,project_id,project_confidence,status,original_filename)
  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
   d['supplier_name'],d['invoice_number'],d['invoice_date'],d['subtotal'],d['vat'],d['total'],d['currency'],d['description'],d['category'],d.get('project_id'),d.get('project_confidence',0),d.get('status','Validated'),d.get('original_filename','')))
  return cur.lastrowid

def get_invoices():
 with connect() as con:
  con.row_factory=sqlite3.Row
  return [dict(r) for r in con.execute('''SELECT i.*, p.name project_name FROM invoices i LEFT JOIN projects p ON p.id=i.project_id ORDER BY i.id DESC''')]

def update_invoice(invoice_id, **fields):
 allowed={'supplier_name','invoice_number','invoice_date','subtotal','vat','total','currency','description','category','project_id','status'}
 pairs=[(k,v) for k,v in fields.items() if k in allowed]
 if not pairs:return
 with connect() as con:
  con.execute('UPDATE invoices SET '+', '.join(f'{k}=?' for k,_ in pairs)+' WHERE id=?',[v for _,v in pairs]+[invoice_id])

def project_report():
 with connect() as con:
  con.row_factory=sqlite3.Row
  q='''SELECT p.id,p.name,COALESCE((SELECT SUM(amount) FROM income x WHERE x.project_id=p.id),0) income,
  COALESCE((SELECT SUM(total) FROM invoices i WHERE i.project_id=p.id),0) expenses
  FROM projects p ORDER BY p.id'''
  rows=[]
  for r in con.execute(q):
   d=dict(r);d['pnl']=d['income']-d['expenses'];rows.append(d)
  return rows
