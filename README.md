# Floka 원본 프런트엔드 복제 프로젝트

기준 사이트: https://floka.casethemes.net/

이 프로젝트는 새로 디자인한 Floka 스타일 홈페이지가 아닙니다. 실제 데모가 출력한 HTML과 CSS·JavaScript·이미지·폰트·영상을 보존하고, 파일 경로와 페이지 링크만 독립 실행용으로 변환합니다. 듀포드 문구, 새 이미지, 임의 서체, 새 레이아웃을 넣지 않았습니다. WordPress/PHP 설치 없이 정적 웹서버에서 실행합니다. 원본이 사용한 Elementor의 **브라우저용 실행 파일**은 효과 유지를 위해 포함했습니다.

## 포함 범위

- Home 1~9 및 각각의 Onepage 데모
- About Us, Our Team, Team Details
- Contact Us 1·2, FAQ, Career 및 채용 상세
- Services 1~4, 서비스 상세
- Portfolio Grid·Carousel·Masonry·Showcase·상세·분류
- Blog Grid·Standard·상세·사이드바 변형·분류·페이지 넘김
- Shop·상품 상세·Cart·Checkout의 공개 비로그인 화면
- Landing Page와 원본 404 화면
- 메인 `home-1-video.mp4`, Home 5 영상, 원본 이미지·폰트·아이콘, 스크롤·호버·슬라이드 효과 스크립트

`PAGE-INVENTORY.csv`에는 모든 캡처 URL, 로컬 파일, 원본 응답 상태를 기록했습니다. 원본의 잘못된 링크가 연결하는 404 화면도 그대로 포함했습니다. 페이지 수에는 분류·페이지 넘김·사이드바 변형과 404 응답이 포함되며, 서로 다른 디자인 254개라는 의미는 아닙니다.

## Windows에서 가장 쉽게 확인하기

1. ZIP을 완전히 압축 해제합니다.
2. Python 3가 설치된 PC에서 `START-WINDOWS.cmd`를 실행합니다.
3. 자동으로 열린 브라우저에서 확인합니다. 종료할 때 검은 창에서 `Ctrl+C`를 누릅니다.

`index.html`을 파일 탐색기에서 더블클릭하는 방식은 사용하지 마세요. WebGL 이미지 효과, 동영상, 동적 스크립트가 웹서버 주소를 기준으로 동작합니다.

터미널에서는 다음과 같이 실행합니다.

```sh
python3 scripts/build.py
python3 scripts/serve.py
```

Node가 있다면 `npm start`도 가능합니다. npm 패키지 설치는 필요하지 않습니다. 빌드에는 Python 표준 라이브러리만 사용합니다.

## GitHub에 올리기

공개 저장소: **https://github.com/skarjqn/duford-floka**

사용자 요청에 따라 저장소 이름은 `duford-floka`, 접근 범위는 **Public(공개)**입니다. GitHub Free 계정으로 공개 소스 저장소를 사용할 수 있습니다.

1. [GitHub 가입](https://github.com/signup)에서 이메일 또는 Google/Apple 계정으로 가입합니다. 사용자 이름을 정하고, 표시되는 이메일 인증을 완료합니다.
2. 기존 공개 저장소를 내려받으려면 `git clone https://github.com/skarjqn/duford-floka.git`을 실행합니다. GitHub Desktop에서는 `File → Clone repository → URL`에 같은 주소를 입력합니다.
3. 계정의 `duford-floka` 공개 저장소로 이 프로젝트의 `main` 브랜치를 업로드합니다. 저장소 루트에는 `capture/`, `scripts/`, `capture-manifest.json`, `.github/workflows/pages.yml`이 들어갑니다. ZIP 파일 자체를 올리는 방식이 아닙니다.
4. 소스 업로드와 웹사이트 공개는 별도 단계입니다. 기본 상태에서는 업로드만으로 GitHub Pages가 배포되지 않습니다.

공식 안내: [계정 만들기](https://docs.github.com/en/account-and-profile/how-tos/account-management/creating-an-account-on-github), [GitHub Free 안내](https://docs.github.com/en/get-started/learning-about-github/githubs-plans).

### GitHub Desktop으로 공개 업로드하기

이번 ZIP에는 `main` 브랜치와 첫 커밋을 포함한 로컬 Git 저장소가 들어 있습니다. 압축을 완전히 풀면 바로 GitHub Desktop에 추가할 수 있습니다.

1. [GitHub Desktop](https://desktop.github.com/download/)을 설치하고 자신의 GitHub 계정으로 로그인합니다.
2. ZIP을 완전히 압축 해제한 후, GitHub Desktop에서 `File → Add local repository → Choose...`를 선택합니다.
3. 압축에서 나온 `duford-floka` 폴더를 고르고 `Add repository`를 누릅니다.
4. 상단 `Publish repository`를 누르고 `Name`을 `duford-floka`로 정합니다.
5. **`Keep this code private` 체크를 해제**하고, 개인 계정으로 올릴 경우 `Organization`은 `None`으로 둡니다.
6. `Publish repository`를 누르고 업로드가 끝날 때까지 기다립니다. 이어 `Repository → View on GitHub`에서 파일 목록과 `Public` 표시를 확인합니다.

같은 이름의 저장소가 이미 있으면 새 이름을 선택하거나 기존 저장소의 용도를 먼저 확인합니다. 기존 저장소 내용을 강제로 덮어쓸 필요는 없습니다.

공식 안내: [로컬 저장소 추가](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop), [공개 저장소로 게시](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop).

### GitHub Pages를 별도로 사용할 때

GitHub Free의 Pages는 공개 저장소에서 사용할 수 있습니다. 공개 저장소 업로드를 완료한 다음 아래 단계로 웹사이트를 별도 배포할 수 있습니다. 기존 미리보기는 https://duford-kindergarten.namgb77.chatgpt.site 에서 확인할 수 있습니다.

1. 계정과 저장소가 Pages 사용 조건에 맞는지 확인합니다.
2. 저장소 `Settings → Pages → Build and deployment → Source`를 `GitHub Actions`로 설정합니다.
3. `Settings → Secrets and variables → Actions → Variables`에 `ENABLE_GITHUB_PAGES`를 만들고 값을 `true`로 설정합니다.
4. `Actions → Publish original Floka frontend → Run workflow`를 실행합니다. 이후 `main` 브랜치 변경 시에도 자동 배포됩니다.

워크플로는 GitHub가 제공하는 저장소 경로를 읽어 링크·CSS·영상 경로에 반영합니다. `사용자.github.io/저장소이름/` 형태에서도 서브페이지 링크가 연결됩니다. 사용자 지정 도메인을 쓰는 경우도 Pages의 base path를 따릅니다.

테마와 데모 원본 파일의 권리 및 출처는 `THIRD-PARTY-NOTICE.md`에 기록했습니다. GitHub Pages를 별도 배포한 뒤에는 실제 배포 주소를 추가하세요.

공식 안내: [GitHub Pages 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [GitHub 파일 크기 제한](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

## 원본 유지와 서버 기능의 경계

보존한 부분: 원본 문구, 이미지 위치, 타이포그래피 정의, 여백, 색상, 반응형 CSS, 원본 클라이언트 애니메이션 코드, 공개 페이지 구조입니다. `capture/`는 확보한 원본 파일이며, `site/`는 경로 변환 후 생성됩니다.

원본 운영 서버나 데이터베이스를 가져온 것은 아닙니다. 문의 이메일 전송, 댓글 저장, 검색 서버, 회원 로그인, 장바구니 저장·결제, 관리자 게시판, AJAX 추가 불러오기는 별도 백엔드 연결이 필요합니다. Google 지도와 YouTube 등 외부 임베드는 원본처럼 인터넷 연결이 필요합니다.

원본 데모 업체에 실수로 제출되지 않도록 폼 제출과 장바구니·위시리스트 요청은 차단합니다. 제출 시에만 정적 데모 안내가 나타나며, 성공한 것처럼 표시하거나 개인정보를 전송하지 않습니다. 초기 화면 디자인은 변경하지 않습니다.

## 검증 범위

`verification-report.json`은 원본 대비 본문 문구·DOM 구조·클래스·인라인 스타일, 로컬 파일 참조, JavaScript 구문 확인 결과입니다. `capture-manifest.json`에는 파일 출처와 SHA-256이 있습니다. 원본 사이트가 반환한 누락 파일도 기록했습니다. 없는 이미지를 새 이미지로 만들거나, 없는 폰트를 임의 폰트로 교체하지 않았습니다.

기존 비공개 미리보기에 배포했으며, 메인 HTML·About Us HTML·메인 MP4의 HTTP 200 응답을 확인했습니다. 원본 사이트의 메인 영상 재생과 Funnel Display 서체는 실제 브라우저에서 확인했습니다. **복제본의 모든 브라우저 애니메이션을 최종 육안 검증한 것은 아닙니다.** 모든 서버 기능까지 동일하게 완성된 서비스는 아닙니다.

## 파일 수정과 재빌드

원본 보존 파일은 `capture/`에 있습니다. 화면을 수정할 때 해당 HTML/CSS를 편집한 후 빌드합니다. 생성된 `site/`만 편집하면 다음 빌드에 덮어써집니다.

```sh
python3 scripts/build.py --base /저장소이름/
```

새로 자료를 가져오는 스크립트는 `scripts/mirror.py`, `capture_async.py`, `fetch_extras.py`이며, 일반 실행·배포에는 필요 없습니다. 자료 재수집과 검증 도구에만 `lxml`, `aiohttp`가 필요합니다. 구매 패키지는 재수집 전에 `licensed-package/Floka_FullPackage/`에 풀거나 `FLOKA_PACKAGE_ROOT` 환경변수에 경로를 지정합니다. 원본 운영 서버에 쓰기 요청을 보내는 기능은 포함하지 않았습니다.
