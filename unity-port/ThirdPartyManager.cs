// Offline integration facade. Keeps serialized script identity and public entry points.
using UnityEngine;
public class ThirdPartyManager : MonoBehaviour
{
    public static ThirdPartyManager instance;
    public string DevUrl = "";
    private void Awake() { if (instance == null) instance = this; }
    public void ShowInterstitialAds() { }
    public void ShowVideoAds(RewardType type)
    {
        Time.timeScale = 1f;
        Panel_AskAds panel = Object.FindObjectOfType<Panel_AskAds>();
        if (panel != null) panel.Close();
        DokdoWebRuntime.Notice("웹판에서는 광고 보상을 사용할 수 없습니다.");
    }
    public void Restore() { DokdoWebRuntime.Notice("웹판에서는 모바일 결제 복원을 지원하지 않습니다."); }
    public void BuyProduct(string product) { DokdoWebRuntime.Notice("웹판에서는 결제를 지원하지 않습니다."); }
}
