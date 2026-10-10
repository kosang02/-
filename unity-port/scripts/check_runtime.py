#!/usr/bin/env python3
"""C# source check against extracted Unity 5.6 reference DLLs; not a Unity/WebGL build."""
import argparse,json,subprocess
from pathlib import Path

def check(project,references,dotnet,compiler,output):
    output.mkdir(parents=True,exist_ok=True)
    refs=[p for p in references.glob('*.dll') if not p.name.startswith('Assembly-')]
    if not (references/'UnityEngine.dll').exists():raise ValueError('UnityEngine.dll reference is missing')
    allfiles=[p for p in (project/'Assets').rglob('*.cs') if 'Editor' not in p.relative_to(project/'Assets').parts]
    plugin=[p for p in allfiles if 'Plugins' in p.relative_to(project/'Assets').parts]
    main=[p for p in allfiles if p not in plugin]
    results=[]
    for name,files,extra in [('Assembly-CSharp-firstpass',plugin,[]),('Assembly-CSharp',main,[output/'Assembly-CSharp-firstpass.dll'])]:
        args=['/target:library','/noconfig','/nostdlib+','/langversion:7.3','/unsafe+','/define:UNITY_WEBGL,UNITY_5_6_OR_NEWER','/out:'+str(output/(name+'.dll'))]
        args+=['/r:'+str(p) for p in refs+extra]+[str(p) for p in files]
        rsp=output/(name+'.rsp');rsp.write_text('\n'.join('"'+arg+'"' for arg in args))
        run=subprocess.run([str(dotnet),str(compiler),'@'+str(rsp)],capture_output=True,text=True)
        log=run.stdout+run.stderr;(output/(name+'.log')).write_text(log)
        errors=[line for line in log.splitlines() if 'error ' in line]
        warnings=[line for line in log.splitlines() if 'warning ' in line]
        results.append({'assembly':name,'sourceCount':len(files),'exitCode':run.returncode,'errorCount':len(errors),'warningCount':len(warnings)})
        print(name+':',len(files),'files;',len(errors),'errors;',len(warnings),'warnings')
        if errors:print('\n'.join(errors[:35]));break
    report={'check':'Roslyn C# 7.3 against extracted Unity 5.6 API references','unityEditorRun':False,'webglBuild':False,'assemblies':results,'passed':len(results)==2 and all(r['exitCode']==0 for r in results)}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['project','references','dotnet','compiler','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();r=check(a.project.resolve(),a.references.resolve(),a.dotnet.resolve(),a.compiler.resolve(),a.output.resolve());raise SystemExit(0 if r['passed'] else 1)
