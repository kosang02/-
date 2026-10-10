#!/usr/bin/env python3
"""Bundle local ESM modules and Korean font into an offline HTML, no dependencies."""
from pathlib import Path
import re,base64,zipfile,argparse
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'artifacts');args=parser.parse_args();OUT=args.output.resolve()
OUT.mkdir(exist_ok=True,parents=True)
def read(name): return (DIST/name).read_text()
def declarations(src): return re.findall(r'export\s+(?:const|function|class)\s+(\w+)',src)
def strip(src):
    src=re.sub(r'^import\s+[\s\S]*?from\s+[\"\'][^\"\']+[\"\'];?\s*','',src,flags=re.M)
    src=re.sub(r'export\s*\{[^}]*\};','',src)
    return re.sub(r'\bexport\s+(?=const|function|class)','',src)
def wrap(name,src,pre,names):return f'const {name}=(()=>{{\n{pre}\n{strip(src)}\nreturn{{{names}}};\n}})();\n'
three=read('three.module.js')
exports=re.search(r'export\s*\{(.*?)\};?\s*$',three,re.S).group(1)
fields=[]
for entry in exports.split(','):
    parts=entry.strip().split(' as ')
    fields.append(parts[1]+':'+parts[0] if len(parts)>1 else parts[0])
js=wrap('THREE',three,'',','.join(fields))
rules=read('rules.js');js+=wrap('RULES',rules,'',','.join(declarations(rules)))
js+=wrap('DATA',read('world.js'),'','WORLD')
js+=wrap('ENGINE',read('engine.js'),'const R=RULES;const{WORLD}=DATA;','R,WORLD,TAU,clamp,distance,landRadius,angleDiff,KO,initialState,validateState,Game')
js+=wrap('RENDER',read('render.js'),'const T=THREE;const{WORLD,clamp,distance,landRadius}=ENGINE;','View')
js+='(()=>{const{Game,R,WORLD,KO,clamp,distance}=ENGINE;const{View}=RENDER;\n'+strip(read('main.js'))+'\n})();'
font=base64.b64encode((DIST/'fonts/korean.woff2').read_bytes()).decode()
css=re.sub(r"url\([\"']?\./fonts/korean\.woff2[\"']?\)", 'url("data:font/woff2;base64,'+font+'")', read('style.css'))
html=re.sub(r'<link[^>]*href="style.css"[^>]*>',lambda m:'<style>'+css+'</style>',read('index.html'))
html=re.sub(r'<link rel="preload"[^>]*>','',html)
html=re.sub(r'<script[^>]*src="main.js"[^>]*>\s*</script>',lambda m:'<script>'+js.replace('</script','<\\/script')+'</script>',html)
html+='\n<!-- Third-party licenses\n'+(ROOT/'THREE-LICENSE.txt').read_text()+'\n'+(DIST/'fonts/OFL.txt').read_text()+'\n-->\n'
(OUT/'dokdo-korean.html').write_text(html)
with zipfile.ZipFile(OUT/'dokdo-korean-source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for path in ROOT.rglob('*'):
        if path.is_file() and not (path.suffix=='.png' and path.parent==ROOT) and not any(p in path.parts for p in ['node_modules','.git','.openai','artifacts','__pycache__','downloads']):
            z.write(path,Path('dokdo-korean')/path.relative_to(ROOT))
print('HTML:',(OUT/'dokdo-korean.html').stat().st_size,'bytes; ZIP:',(OUT/'dokdo-korean-source.zip').stat().st_size,'bytes')
