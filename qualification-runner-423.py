import hashlib,json,pathlib,subprocess,time,sys
root=pathlib.Path('candidate'); out=pathlib.Path('proof'); out.mkdir(exist_ok=True)
expected='b057df18cea0da63994a3f6786ef411a5396a8e0'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==expected
commands=json.loads(pathlib.Path('harness/qualification-commands.json').read_text()); assert len(commands)==81
assert hashlib.sha256(pathlib.Path('harness/qualification-commands.json').read_bytes()).hexdigest() == '194a76f5a74de904108084c7ed7c02e93ac3f5f9f530545e8f34d2ef8d47f07f'
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=root,text=True).split('\0')
sources={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in tracked if p and (root/p).is_file()}
(out/'source-hashes.json').write_text(json.dumps(sources,sort_keys=True,indent=2)+'\n')
import platform,importlib.metadata as metadata
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(); chromium=browser.version; browser.close()
versions={"uname":subprocess.check_output(['uname','-a'],text=True).strip(),"python":sys.version,"node":subprocess.check_output(['node','--version'],text=True).strip(),"npm":subprocess.check_output(['npm','--version'],text=True).strip(),"playwright":metadata.version('playwright'),"chromium":chromium,"pillow":metadata.version('Pillow'),"claude":subprocess.check_output(['npx','--yes','@anthropic-ai/claude-code@2.1.229','--version'],text=True).strip()}
receipt={"status":"RUNNING","candidate":expected,"upstream_base":"0a8ea20ae69b33a5edce6018eedd3a9d26e90c1c","versions":versions}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert versions['playwright']=='1.62.0' and versions['pillow']=='12.1.1' and versions['claude'].startswith('2.1.229 ')
results=[]
for i,command in enumerate(commands,1):
 start=time.monotonic(); r=subprocess.run(command,shell=True,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (out/f'{i:02}.log').write_text(r.stdout)
 # Browser gates must actually execute, including the optional Excalidraw browser check.
 skipped=i in (18,19,27,78) and ('SKIP:' in r.stdout or 'browser check runs in lint-render' in r.stdout)
 mobile_browser_missing=i==27 and 'OK: worked example is contained and locally scrollable at 390px' not in r.stdout
 results.append(dict(index=i,command=command,returncode=r.returncode,seconds=time.monotonic()-start,browser_skipped=skipped,mobile_browser_missing=mobile_browser_missing))
 (out/'results.json').write_text(json.dumps(results,indent=2)+'\n'); print(i,r.returncode,command,flush=True)
subprocess.run(['git','diff','--exit-code'],cwd=root,check=True)
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==v for p,v in sources.items())
assert len(results)==81 and all(x['returncode']==0 and not x['browser_skipped'] and not x['mobile_browser_missing'] for x in results)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==expected
receipt.update(status='PASS',completed_gates=81,failed_gates=0,unchanged_sources=True)
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
