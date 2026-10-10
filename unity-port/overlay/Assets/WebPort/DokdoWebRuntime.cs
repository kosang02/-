using System;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

// Runs before the recovered scenes. No game geometry, economy or physics is replaced.
public sealed class DokdoWebRuntime : MonoBehaviour
{
    private static DokdoWebRuntime instance;
    private Font korean;
    private float refreshAt;
    private float saveAt;
    private string notice = "";
    private float noticeUntil;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    private static void Install()
    {
        if (instance != null) return;
        GameObject root = new GameObject("Dokdo Korean Web Runtime");
        DontDestroyOnLoad(root);
        instance = root.AddComponent<DokdoWebRuntime>();
    }
    private void Awake()
    {
        korean = Resources.Load<Font>("WebPort/Korean");
        if (korean == null) Debug.LogError("Embedded Korean font is missing.");
        SceneManager.sceneLoaded += SceneLoaded;
    }
    private void OnDestroy() { SceneManager.sceneLoaded -= SceneLoaded; }
    private void SceneLoaded(Scene scene, LoadSceneMode mode) { RefreshLabels(); }
    private void Update()
    {
        if (Time.realtimeSinceStartup > refreshAt)
        {
            refreshAt = Time.realtimeSinceStartup + 0.5f;
            RefreshLabels();
        }
        if (Time.realtimeSinceStartup > saveAt)
        {
            saveAt = Time.realtimeSinceStartup + 10f;
            Save();
        }
    }
    private void RefreshLabels()
    {
        if (korean == null) return;
        foreach (Text label in Resources.FindObjectsOfTypeAll<Text>())
            if (label.font != korean) label.font = korean;
        foreach (TextMesh label in Resources.FindObjectsOfTypeAll<TextMesh>())
        {
            if (label.font == korean) continue;
            label.font = korean;
            Renderer renderer = label.GetComponent<Renderer>();
            if (renderer != null) renderer.sharedMaterial = korean.material;
        }
    }
    private void Save()
    {
        if (GameManager.Instance != null) GameManager.Instance.Save();
        PlayerPrefs.Save();
    }
    private void OnApplicationPause(bool paused) { if (paused) Save(); }
    private void OnApplicationFocus(bool focused) { if (!focused) Save(); }
    private void OnApplicationQuit() { Save(); }
    public static void Notice(string text)
    {
        Debug.Log(text);
        if (instance == null) return;
        instance.notice = text;
        instance.noticeUntil = Time.realtimeSinceStartup + 4f;
    }
    private void OnGUI()
    {
        if (Time.realtimeSinceStartup >= noticeUntil) return;
        GUIStyle style = new GUIStyle(GUI.skin.box);
        style.font = korean;
        style.fontSize = Mathf.Max(14, Screen.height / 40);
        style.alignment = TextAnchor.MiddleCenter;
        style.wordWrap = true;
        GUI.Box(new Rect(Screen.width * .1f, Screen.height * .4f, Screen.width * .8f, Screen.height * .12f), notice, style);
    }
}
