using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;
#if UNITY_2018_1_OR_NEWER
using UnityEditor.Build.Reporting;
#endif
public static class DokdoWebBuild
{
    private static readonly string[] Scenes = {
        "Assets/0.my/Scenes/load.unity", "Assets/0.my/Scenes/Intro.unity", "Assets/0.my/Scenes/Main.unity"
    };
    [MenuItem("Dokdo/Build Korean WebGL")]
    public static void Build()
    {
        foreach (string scene in Scenes) if (!File.Exists(scene)) throw new FileNotFoundException(scene);
        Font font = AssetDatabase.LoadAssetAtPath<Font>("Assets/Resources/WebPort/Korean.ttf");
        if (font == null) throw new InvalidOperationException("Korean.ttf did not import as a Unity Font.");
        TrueTypeFontImporter importer = AssetImporter.GetAtPath("Assets/Resources/WebPort/Korean.ttf") as TrueTypeFontImporter;
        if (importer != null) { importer.fontTextureCase = FontTextureCase.Dynamic; importer.includeFontData = true; importer.SaveAndReimport(); }
        foreach (string scene in Scenes)
        {
            var loaded = EditorSceneManager.OpenScene(scene, OpenSceneMode.Single);
            foreach (Text label in Resources.FindObjectsOfTypeAll<Text>())
                if (!EditorUtility.IsPersistent(label)) { label.font = font; EditorUtility.SetDirty(label); }
            EditorSceneManager.MarkSceneDirty(loaded);
            EditorSceneManager.SaveScene(loaded);
        }
        PlayerSettings.companyName = "Personal Web Reconstruction";
        PlayerSettings.productName = "독도까지 한국어 웹판";
        PlayerSettings.defaultWebScreenWidth = 540;
        PlayerSettings.defaultWebScreenHeight = 960;
        PlayerSettings.runInBackground = false;
        PlayerSettings.SetScriptingBackend(BuildTargetGroup.WebGL, ScriptingImplementation.IL2CPP);
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Disabled;
        PlayerSettings.WebGL.memorySize = 256;
        string output = Environment.GetEnvironmentVariable("DOKDO_WEB_OUTPUT");
        if (String.IsNullOrEmpty(output)) output = "Build/WebGL";
        Directory.CreateDirectory(output);
#if UNITY_2018_1_OR_NEWER
        BuildReport result = BuildPipeline.BuildPlayer(Scenes, output, BuildTarget.WebGL, BuildOptions.None);
        if (result.summary.result != BuildResult.Succeeded) throw new Exception("WebGL build failed: " + result.summary.result);
#else
        string error = BuildPipeline.BuildPlayer(Scenes, output, BuildTarget.WebGL, BuildOptions.None);
        if (!String.IsNullOrEmpty(error)) throw new Exception(error);
#endif
        File.WriteAllText(Path.Combine(output, ".nojekyll"), "");
        Debug.Log("DOKDO_WEB_BUILD_OK " + Path.GetFullPath(output));
    }
}
