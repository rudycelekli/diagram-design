import importlib.util,sys,io,json,subprocess,hashlib,importlib.metadata
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
repo=Path('candidate');out=Path('proof')
path=repo/'skills/diagram-design/scripts/export_svg.py';candidate=path.read_bytes();original=subprocess.check_output(['git','show','92fc7e4916638cd271effcdaa24e3e9afe44905b:skills/diagram-design/scripts/export_svg.py'],cwd=repo)
html=r'<style>.revenue\,net\31 foo {fill:blue}</style><svg viewBox="0 0 10 10"><g fill="rgba(255,0,0,0.5)"><rect class="revenue,net1foo" width="10" height="10"/></g></svg>'
results={}
with sync_playwright()as p:
 browser=p.chromium.launch(args=["--host-resolver-rules=MAP * ~NOTFOUND"]);page=browser.new_page(viewport={'width':40,'height':40},device_scale_factor=1);page.route('**/*',lambda route:route.abort())
 for name,source in [('before',original),('after',candidate)]:
  module=type(sys)('probe_'+name);module.__file__=str(path);sys.modules[module.__name__]=module;exec(compile(source,str(path),'exec'),module.__dict__)
  svg=module.export_svg_document(html,Path('escaped-paint.html'),system_fonts=True);page.set_content('<body style="margin:0;background:white">'+svg+'</body>');page.locator('svg').evaluate('(e)=>{e.style.width="40px";e.style.height="40px"}')
  png=page.screenshot();(out/('423-'+name+'.png')).write_bytes(png);pixel=Image.open(io.BytesIO(png)).convert('RGB').getpixel((20,20));results[name]={'center_pixel':pixel,'png_sha256':hashlib.sha256(png).hexdigest(),'computed_fill':page.locator('rect').evaluate('(e)=>getComputedStyle(e).fill'),'computed_fill_opacity':page.locator('rect').evaluate('(e)=>getComputedStyle(e).fillOpacity')}
 version=browser.version;browser.close()
assert results['before']['center_pixel'][0]>=120 and results['before']['center_pixel'][1]>=120 and results['before']['center_pixel'][2]==255,results
assert results['after']['center_pixel']==(0,0,255),results
(out/'423-browser-proof.json').write_text(json.dumps({'status':'PASS','actual_browser':version,'playwright':importlib.metadata.version('playwright'),'source_hashes':{'before':hashlib.sha256(original).hexdigest(),'after':hashlib.sha256(candidate).hexdigest()},'results':results},indent=2));print(results)
