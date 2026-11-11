import subprocess, sys, os, shutil
src = os.path.abspath(sys.argv[1]); outdir = os.path.abspath(sys.argv[2])
os.makedirs(outdir, exist_ok=True)
prof = '/tmp/claude-0/-home-user-Power/562dd684-59fa-5b19-94f2-822ecbb92d34/scratchpad/lo_profile'
r = subprocess.run(['soffice', f'-env:UserInstallation=file://{prof}', '--headless', '--calc', '--convert-to', 'xlsx:Calc MS Excel 2007 XML', '--outdir', outdir, src], capture_output=True, text=True, timeout=600)
print(r.stdout[-300:], r.stderr[-300:])
