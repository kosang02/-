#!/usr/bin/env python3
"""Run a prepared project in an installed, activated Unity Editor. Never handles credentials."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--editor',type=Path);a=p.parse_args()
editor=a.editor or (Path(os.environ['UNITY_EDITOR_PATH']) if os.environ.get('UNITY_EDITOR_PATH') else None)
if editor is None:
    found=shutil.which('Unity') or shutil.which('unity-editor')
    if found:editor=Path(found)
if editor is None or not editor.is_file():
    print(json.dumps({'status':'blocked','reason':'Unity Editor is not installed or --editor was not supplied. Install Editor plus WebGL Build Support using Unity Hub and activate a license on the build machine.','webglBuilt':False},ensure_ascii=False))
    raise SystemExit(2)
project=a.project.resolve();output=a.output.resolve()
if not (project/'WEB_PORT_PREPARATION.json').exists():raise SystemExit('Prepare the exported project first.')
output.mkdir(parents=True,exist_ok=True);log=output.parent/'unity-web-build.log'
log.unlink(missing_ok=True)  # A previous successful log must not satisfy this build.
env=os.environ.copy();env['DOKDO_WEB_OUTPUT']=str(output)
command=[str(editor.resolve()),'-batchmode','-nographics','-quit','-projectPath',str(project),'-buildTarget','WebGL','-executeMethod','DokdoWebBuild.Build','-logFile',str(log)]
print('Starting Unity; log:',log,flush=True)
result=subprocess.run(command,env=env)
text=log.read_text(errors='replace') if log.exists() else ''
passed=result.returncode==0 and 'DOKDO_WEB_BUILD_OK' in text and (output/'index.html').exists()
print(json.dumps({'status':'built' if passed else 'failed','exitCode':result.returncode,'log':str(log),'webglBuilt':passed},ensure_ascii=False))
raise SystemExit(0 if passed else 1)
