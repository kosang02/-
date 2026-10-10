# 독도까지 Unity WebGL 포팅 준비본

**현재 상태: 준비 코드 작성 및 런타임 C# 검사 완료. Unity Editor 실행, WebGL 빌드, 브라우저 실행은 미완료입니다. 이 폴더는 플레이 가능한 게임 배포물이 아닙니다.**

APK를 웹페이지에 넣는 방식이 아니라, AssetRipper로 복원한 Unity 프로젝트를 수정하여 WebGL로 다시 빌드하는 방식입니다. 기존 JavaScript 재구성판은 저장소의 `main` 브랜치에 있습니다. 이 브랜치는 Unity 포팅 작업용입니다.

## 실제 확인 결과

| 검사 | 결과 |
| --- | --- |
| 복원본 Unity 버전 | 5.6.5p1 |
| 런타임 소스 1,130개, 2개 어셈블리 | C# 컴파일 오류 0개, 경고 119개 |
| 검사 도구와 참조 | Roslyn / C# 7.3, APK에서 추출한 Unity 5.6 API DLL |
| 수정 대상 외 입력 파일 | 3,570개 바이트 동일 |
| 제거한 스크립트를 참조하는 남은 직렬화 에셋 | 검사 범위에서 없음 |
| 임베드 폰트 | 정적 TTF, 한글 완성형 11,172자 포함 |
| Unity Editor / 셰이더 / IL2CPP 검사 | 실행하지 못함 |
| 실제 WebGL / 브라우저 검사 | 실행하지 못함 |

빌드 사전 검사에서 Unity Editor가 설치되어 있지 않아 중단되었습니다. 이 작업 환경에는 활성화된 Unity 라이선스도 없습니다. 실제 빌드에는 Editor, WebGL Build Support, 빌드 환경에서 활성화한 라이선스가 필요합니다. Unity 계정 비밀번호나 라이선스를 이 저장소에 넣지 마세요.

`verification/`의 JSON은 실행한 검사 결과입니다. C# 검사에는 원본 게임의 `Assembly-*.dll`을 참조하지 않고 복원한 소스로 두 어셈블리를 각각 생성했습니다. 다만 Editor 전용 코드는 제외했으며, Unity 2018 API와의 호환성을 입증하는 검사는 아닙니다.

## 준비 코드가 변경하는 것

- 원본 씬, 모델, 텍스처, 오디오, 게임 로직을 입력 프로젝트에서 유지합니다.
- 웹 실행 시 한국어를 선택하고 UI에 정적 Noto Sans KR 폰트를 적용합니다.
- Android 전용 언어 감지와 플랫폼 게임 서비스 호출을 웹에서 우회합니다.
- 광고·결제 연동 진입점을 비활성화하고 사용할 수 없다는 한국어 안내를 표시합니다. 광고 보상과 결제 기능은 지원하지 않습니다.
- Google Analytics 전송 진입점을 비활성화합니다. 모든 SDK의 런타임 동작 및 외부 요청은 아직 실행 검증하지 않았습니다.
- 브라우저 탭의 시간 제한 때문에 오작동할 수 있는 속도 감지를 웹에서 끄고 주기적 저장을 추가합니다. 브라우저 저장 복원은 아직 확인하지 않았습니다.
- 누락된 셰이더 4개를 새로 작성한 호환 셰이더로 교체합니다. 원본 셰이더의 복원이 아니며 원본과 같은 화면을 보장하지 않습니다.
- 중복 어셈블리 속성과 게임 씬에서 참조하지 않는 Facebook 예제 스크립트를 제거합니다.

입력 프로젝트를 덮어쓰지 않습니다. 새 출력 폴더에만 준비본을 생성하며, 원래 스크립트와 셰이더의 `.meta`를 유지합니다. 공개 저장소에는 준비 스크립트·새로 작성한 코드·OFL 폰트만 포함하고 APK, 원본 복원 프로젝트, 원본 DLL은 포함하지 않습니다.

## 프로젝트 준비

Python 3.9 이상과 별도로 준비한 AssetRipper `ExportedProject`가 필요합니다. 이 준비 코드는 아래 APK에서 복원한 구조를 기준으로 작성했습니다. 다른 버전의 입력에는 추가 수정이 필요할 수 있습니다.

입력 APK SHA-256: `e84b45c25bdefba2d743d3b314b6199e7b6ba1e7918ae6994cd1f2fee15e5aec`

저장소 루트에서 실행합니다. 경로는 실제 로컬 경로로 바꾸세요.

```sh
python unity-port/scripts/prepare.py --source /path/to/ExportedProject --output /path/to/DokdoWeb
python unity-port/scripts/verify_project.py --source /path/to/ExportedProject --prepared /path/to/DokdoWeb --report /path/to/preservation.json
```

입력과 출력은 서로 다른 폴더여야 하고 출력 폴더는 아직 없어야 합니다. `WEB_PORT_PREPARATION.json`에 수정 내역이 기록됩니다.

## Unity에서 이어서 빌드

1. Unity Hub에서 로그인하고 사용 가능한 라이선스를 활성화합니다. [공식 라이선스 안내](https://docs.unity.com/en-us/hub/manage-license).
2. Unity **2018.4.36f1 + WebGL Build Support**를 설치하고 준비한 출력 프로젝트를 엽니다. 이 버전은 최초 마이그레이션 대상으로 지정했으며, 실제 import/build 성공을 검증한 버전은 아닙니다.
3. 에셋 import, API 업그레이드, Editor 스크립트 컴파일 결과를 확인합니다. Console 오류, 누락 스크립트, 분홍색 머티리얼 등을 해결해야 할 수 있습니다.
4. Editor 메뉴 `Dokdo > Build Korean WebGL`을 실행하거나 아래 명령을 사용합니다.

```sh
python unity-port/scripts/build.py --project /path/to/DokdoWeb --output /path/to/WebGL --editor /path/to/Unity
```

Windows의 Editor 경로 예: `C:\Program Files\Unity\Hub\Editor\2018.4.36f1\Editor\Unity.exe`.
macOS의 Editor 경로 예: `/Applications/Unity/Hub/Editor/2018.4.36f1/Unity.app/Contents/MacOS/Unity`.

실행 파일 경로에 공백이 있으면 따옴표로 감싸세요. `UNITY_EDITOR_PATH` 환경 변수도 지원합니다. 성공 판정에는 Unity 종료 코드 0, 새 빌드 로그의 성공 표시, 출력 `index.html`이 모두 필요합니다. 출력 폴더의 상위에 `unity-web-build.log`가 저장됩니다.

압축을 끈 정적 호스팅용 출력을 만들도록 설정했습니다. 빌드 성공 후 HTTP 서버로 실행합니다.

```sh
python -m http.server 8080 --directory /path/to/WebGL
```

`http://localhost:8080`에서 로딩 → 시작 → 항해 → 정박/강화/전투 → 저장 후 새로고침, 한글 표시와 오디오를 확인해야 합니다. `file://`로 여는 방식은 사용하지 않습니다. 검증된 WebGL 출력이 생긴 다음 GitHub Pages에 게시할 수 있습니다.

## 런타임 소스 검사 재현

이 검사는 Unity Editor 없이 가능하지만 WebGL 빌드를 대체하지 않습니다. .NET SDK와 APK에서 추출한 Managed DLL 폴더가 필요합니다.

```sh
python unity-port/scripts/check_runtime.py --project /path/to/DokdoWeb --references /path/to/Managed --dotnet /path/to/dotnet --compiler /path/to/sdk/8.0.425/Roslyn/bincore/csc.dll --output /path/to/check
```

## 남아 있는 검증

Unity 2018 에셋 import 및 API 업그레이드, Editor 코드 컴파일, 셰이더 컴파일, IL2CPP/AOT 및 SDK 네이티브 의존성, 폰트 실제 렌더링, 입력/물리/저장/오디오, 모바일 브라우저 메모리 사용량을 검증해야 합니다. 실제 플레이 화면이나 완성된 Unity 웹판 링크는 아직 없습니다.

## 폰트 출처

Noto Sans KR, Google Fonts의 `ofl/notosanskr/NotoSansKR[wght].ttf`를 weight 450 정적 TTF로 변환하고 문자 범위를 추렸습니다. 한글 완성형 전체를 포함합니다. SIL Open Font License 1.1은 `overlay/Assets/Resources/WebPort/OFL.txt`에 있습니다.
