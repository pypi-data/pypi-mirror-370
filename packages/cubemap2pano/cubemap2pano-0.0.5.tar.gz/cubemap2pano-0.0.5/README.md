# cubemap2pano

`cubemap2pano`는 큐브맵 이미지를 등각 원통형 파노라마 이미지로 변환하는 Python 패키지입니다.

## 설치

```bash
pip install cubemap2pano
```

## 사용법

다음은 `cubemap2pano` 패키지를 사용하는 예제입니다:

```python

from cubemap2pano import cubemap2pano

if __name__ == "__main__":
    HEIGHT = 1024
    WIDTH = HEIGHT * 2

    cubemap_paths = [
        ([ "./F.jpg", "./R.jpg", "./B.jpg", "./L.jpg", "./U.jpg", "./D.jpg"], "./result/pano.jpg")
    ]
    cubemap2pano(WIDTH, HEIGHT, cubemap_paths)
```
