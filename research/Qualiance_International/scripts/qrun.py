import openpyxl,subprocess,json,sys
F=sys.argv[1]; R='/root/.claude/skills/synced/593953b5-e569-4bc3-b4b6-3872b98e3292_8cf91ca0-2d35-4644-8101-30affa8a602c/xlsx/scripts/recalc.py'
out={}
for s in (1,2,3):
    wb=openpyxl.load_workbook(F); wb['Drivers']['C3']=s; wb.save(F)
    o=subprocess.run(['python3',R,F,'60'],capture_output=True,text=True).stdout
    j=json.loads(o[o.index('{'):])
    wb=openpyxl.load_workbook(F,data_only=True); p=wb['P&L']; d=wb['Drivers']; v=wb['Valuations']; sg=wb['Segments']
    chk=max([abs(p[f'{c}30'].value or 0) for c in 'FGHI']+[abs(p[f'{c}73'].value or 0) for c in 'BCDEFGHI']+[abs(p[f'{c}98'].value or 0) for c in 'BCDEFGHI']+[abs(sg[f'{c}10'].value or 0) for c in 'EFGH']+[abs(sg[f'{c}18'].value or 0) for c in 'EFGH'])
    r={'err':j['total_errors'],'errs':j.get('error_summary'),'chk':chk,'rev':[p[f'{c}3'].value for c in 'FGHI'],'ebitda':[p[f'{c}15'].value for c in 'FGHI'],'ebm':[p[f'{c}17'].value for c in 'FGHI'],'pat':[p[f'{c}27'].value for c in 'FGHI'],'eps':[p[f'{c}33'].value for c in 'FGHI'],
       'newrev':[d[f'{c}174'].value for c in 'CDEF'],'exrev':[d[f'{c}178'].value for c in 'CDEF'],'tp':v['C26'].value,'up':v['C27'].value,'ev_tp':v['C36'].value,'cfo':[p[f'{c}83'].value for c in 'FGHI'],'netdebt_fy27':v['C34'].value}
    out[s]=r
    print(s,{k:([round(x,2) if isinstance(x,(int,float)) else x for x in vv] if isinstance(vv,list) else (round(vv,3) if isinstance(vv,float) else vv)) for k,vv in r.items()})
json.dump(out,open(sys.argv[2],'w'),indent=1,default=str)
wb=openpyxl.load_workbook(F); wb['Drivers']['C3']=2; wb.save(F); subprocess.run(['python3',R,F,'60'],capture_output=True)
