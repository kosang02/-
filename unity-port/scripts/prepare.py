#!/usr/bin/env python3
"""Prepare an AssetRipper export for the offline Korean Unity WebGL port.
The input export is never modified. Proprietary input assets are not distributed by this kit.
"""
import argparse,json,re,shutil
from pathlib import Path
KIT=Path(__file__).resolve().parents[1]

def prepare(source,output):
    source=source.resolve();output=output.resolve()
    if source == output or source in output.parents:raise ValueError('Output must be outside the input export.')
    if not (source/'Assets/0.my/Scenes/Main.unity').is_file():raise ValueError('Expected DOKDO AssetRipper ExportedProject with Main.unity')
    if output.exists():raise ValueError('Output must not exist; choose a new folder to preserve the input and previous work.')
    shutil.copytree(source,output)
    changed=[];removed=[]
    def edit(relative,fn):
        p=output/relative;old=p.read_text();new=fn(old)
        if new!=old:p.write_text(new);changed.append(relative)
    scripts='Assets/Scripts/Assembly-CSharp/'
    # Unity re-groups recovered UnityScript/C# source; exported AssemblyInfo files conflict.
    for p in output.glob('Assets/**/AssemblyInfo.cs'):
        removed.append(str(p.relative_to(output)));p.unlink();p.with_suffix('.cs.meta').unlink(missing_ok=True)
    # Unreferenced SDK sample scenes are not part of DOKDO. Their calls target internal APIs.
    examples=output/(scripts+'Facebook/Unity/Example')
    scenes=''.join(p.read_text() for p in output.glob('Assets/0.my/Scenes/*.unity'))
    for p in examples.rglob('*.cs'):
        meta=p.with_suffix('.cs.meta')
        guid=re.search(r'guid: (\w+)',meta.read_text()) if meta.exists() else None
        if guid and guid[1] in scenes:raise ValueError('SDK example is referenced by a game scene: '+p.name)
    if examples.exists():removed.append(str(examples.relative_to(output)));shutil.rmtree(examples)
    edit(scripts+'LocalizeManager.cs',lambda s:s.replace('Language = ObscuredPrefs.GetString("lang", Application.systemLanguage.ToString());','#if UNITY_WEBGL || UNITY_EDITOR\n\t\tLanguage = "Korean";\n#else\n\t\tLanguage = ObscuredPrefs.GetString("lang", Application.systemLanguage.ToString());\n#endif'))
    edit(scripts+'PreciseLocale.cs',lambda s:s.replace('_platform = new PreciseLocaleAndroid();','#if UNITY_WEBGL || UNITY_EDITOR\n\t\t\t\t_platform = new EditorBridge();\n#else\n\t\t\t\t_platform = new PreciseLocaleAndroid();\n#endif').replace('return "US";','return "KR";').replace('return "en";','return "ko";').replace('return "en_US";','return "ko_KR";').replace('return "USD";','return "KRW";'))
    edit(scripts+'GameManager.cs',lambda s:s.replace('SpeedHackDetector.StartDetection(OnSpeedHackDetected);','#if !UNITY_WEBGL\n\t\tSpeedHackDetector.StartDetection(OnSpeedHackDetected);\n#endif'))
    # Replace only the integration facade; original movement, physics, economy and scenes remain.
    facade=output/(scripts+'ThirdPartyManager.cs')
    facade.write_text((KIT/'ThirdPartyManager.cs').read_text());changed.append(scripts+'ThirdPartyManager.cs')
    edit(scripts+'Localization.cs',lambda s:s.replace('LM.localized.TryGetValue(id, out str);','LM = LocalizeManager.Instance;\n\t\tif (LM == null) { Invoke("OnEnable", 0.05f); return; }\n\t\tif (label == null) label = GetComponent<Text>();\n\t\tLM.localized.TryGetValue(id, out str);'))
    # Central Google Analytics sender is a no-op in the offline WebGL build.
    manager='Assets/Plugins/Assembly-CSharp-firstpass/SA/Analytics/Google/Manager.cs'
    edit(manager,lambda s:s.replace('public static void Send(string request)\n\t\t{','public static void Send(string request)\n\t\t{\n#if UNITY_WEBGL\n\t\t\treturn;\n#endif'))
    # Guard native platform game-service calls at the game layer.
    for p in (output/scripts).rglob('*.cs'):
        s=p.read_text();out=[];n=0
        for line in s.splitlines(keepends=True):
            if re.search(r'Singleton<UM_GameServiceManager>\.Instance\.(?:Connect|UnlockAchievement|SubmitScore|ShowLeader|ShowAchiev)',line) and line.rstrip().endswith(';'):
                out.extend(['#if !UNITY_WEBGL\n',line,'#endif\n']);n+=1
            else:out.append(line)
        if n:p.write_text(''.join(out));changed.append(str(p.relative_to(output)))
    shutil.copytree(KIT/'overlay',output,dirs_exist_ok=True)
    # 2018.4 is an initial migration target, not a claim of completed Editor validation.
    (output/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 2018.4.36f1\n')
    # Preserve exported built-in module dependencies (UI, physics, audio, etc.).
    report={'status':'prepared-not-unity-built','inputVersion':'5.6.5p1','targetVersion':'2018.4.36f1','changed':changed,'removed':removed,'overlayFiles':[str(p.relative_to(KIT/'overlay')) for p in (KIT/'overlay').rglob('*') if p.is_file()]}
    (output/'WEB_PORT_PREPARATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    r=prepare(a.source,a.output);print(json.dumps({'status':r['status'],'changed':len(r['changed']),'removed':len(r['removed']),'output':str(a.output)},ensure_ascii=False))
