import streamlit as st
import pandas as pd
from database import init_db,list_projects,save_invoice,get_invoices,update_invoice,project_report
from invoice_extractor import pdf_text,image_text,parse_invoice,validate
from ai_service import classify,match_project,answer_report_question

st.set_page_config(page_title='AI Invoice Expense Agent',layout='wide')
init_db()
st.title('AI Invoice & Expense Agent — MVP')
st.caption('Portfolio prototype: invoice extraction → classification → project assignment → review → reporting')

tabs=st.tabs(['Dashboard','Upload Invoice','Invoices','Reports','Ask'])

with tabs[0]:
 rows=project_report(); df=pd.DataFrame(rows)
 c1,c2,c3=st.columns(3)
 c1.metric('Projects',len(rows)); c2.metric('Total income',f"{df['income'].sum():,.2f}"); c3.metric('Total expenses',f"{df['expenses'].sum():,.2f}")
 st.dataframe(df,use_container_width=True)

with tabs[1]:
 f=st.file_uploader('Upload invoice',type=['pdf','png','jpg','jpeg'])
 if f:
  data=f.read(); text=pdf_text(data) if f.type=='application/pdf' else image_text(data)
  if not text.strip():
   st.warning('No text was extracted. For this fast MVP, scanned-image OCR depends on local Tesseract; production would use a document-processing service.')
  d=parse_invoice(text)
  d['category']=classify(text+' '+d.get('description',''))
  projects=list_projects(); pid,pname,conf,question=match_project(text,projects)
  d['project_id']=pid; d['project_confidence']=conf; d['status']='Needs clarification' if question else 'Validated'; d['original_filename']=f.name
  issues=validate(d)
  st.subheader('Extracted fields')
  d['supplier_name']=st.text_input('Supplier',d['supplier_name'])
  d['invoice_number']=st.text_input('Invoice number',d['invoice_number'])
  d['invoice_date']=st.text_input('Invoice date',d['invoice_date'])
  col1,col2,col3=st.columns(3)
  d['subtotal']=col1.number_input('Subtotal',value=float(d['subtotal']))
  d['vat']=col2.number_input('VAT / Tax',value=float(d['vat']))
  d['total']=col3.number_input('Total',value=float(d['total']))
  d['description']=st.text_input('Description',d['description'])
  d['category']=st.selectbox('Category',['Materials','Labour','Equipment','Transport','Subcontractor','Professional Services','Utilities','Other'],index=['Materials','Labour','Equipment','Transport','Subcontractor','Professional Services','Utilities','Other'].index(d['category']))
  project_map={p[1]:p[0] for p in projects}; names=['— Select —']+list(project_map)
  default=names.index(pname) if pname in names else 0
  chosen=st.selectbox('Project',names,index=default)
  if chosen!='— Select —':d['project_id']=project_map[chosen]; d['status']='Validated'; d['project_confidence']=1.0
  if question:st.info(question)
  if issues:st.warning('Validation: '+'; '.join(issues))
  else:st.success('Basic validation passed')
  if st.button('Save invoice',type='primary'):
   iid=save_invoice(d);st.success(f'Invoice #{iid} saved')

with tabs[2]:
 inv=get_invoices()
 if not inv:st.info('No invoices saved yet.')
 else:
  st.dataframe(pd.DataFrame(inv),use_container_width=True)
  ids=[x['id'] for x in inv]; iid=st.selectbox('Edit invoice ID',ids)
  row=next(x for x in inv if x['id']==iid)
  supplier=st.text_input('Edit supplier',row['supplier_name'],key='e_supplier')
  category=st.selectbox('Edit category',['Materials','Labour','Equipment','Transport','Subcontractor','Professional Services','Utilities','Other'],index=max(0,['Materials','Labour','Equipment','Transport','Subcontractor','Professional Services','Utilities','Other'].index(row['category']) if row['category'] in ['Materials','Labour','Equipment','Transport','Subcontractor','Professional Services','Utilities','Other'] else 7),key='e_cat')
  pmap={p[1]:p[0] for p in list_projects()}; pnames=list(pmap); current=row.get('project_name'); psel=st.selectbox('Edit project',pnames,index=pnames.index(current) if current in pnames else 0,key='e_project')
  if st.button('Save edits'):
   update_invoice(iid,supplier_name=supplier,category=category,project_id=pmap[psel],status='Validated');st.success('Updated')

with tabs[3]:
 rows=project_report();st.subheader('Project P&L');st.dataframe(pd.DataFrame(rows),use_container_width=True)
 inv=get_invoices()
 if inv:
  df=pd.DataFrame(inv)
  st.subheader('Expenses by category');st.dataframe(df.groupby('category',dropna=False)['total'].sum().reset_index(),use_container_width=True)
  st.metric('VAT / Tax total',f"{df['vat'].fillna(0).sum():,.2f}")

with tabs[4]:
 q=st.text_input('Ask a reporting question',placeholder='Give me P&L for Project Beta')
 if q:st.write(answer_report_question(q,project_report()))
