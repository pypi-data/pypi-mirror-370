from typing import Optional
import torch
from torchvision import transforms
from PIL import Image
import math

# ----- I/O helpers (원본 스타일 유지) -----
to_pil = transforms.ToPILImage()
transform = transforms.ToTensor()

def load_image_as_tensor(filepath: str) -> torch.Tensor:
    image = Image.open(filepath).convert('RGB')
    return transform(image)  # [C,H,W], float32, 0~1

def save_tensor_as_image(tensor: torch.Tensor, save_path: str):
    # tensor: [C,H,W], float32, 0~1
    image = to_pil(tensor)
    image.save(save_path)

# ----- 유틸 -----
def _make_linspace_face(face_size: int, device: torch.device):
    """
    얼굴(face) 로컬 좌표계를 위한 정규화 그리드 생성
    a: [-1, 1] 좌→우 (x축), b: [-1, 1] 상→하 (y축)
    """
    a = torch.linspace(-1.0, 1.0, face_size, device=device)  # x
    b = torch.linspace(-1.0, 1.0, face_size, device=device)  # y (이미지 기준: 위=-1, 아래=1)
    b, a = torch.meshgrid(b, a, indexing="ij")               # [F,F]
    return a, b

def _dir_from_face_uv(face_idx: int, a: torch.Tensor, b: torch.Tensor):
    """
    각 face의 로컬 좌표 (a,b) ∈ [-1,1]^2 를
    월드 방향 벡터 (x,y,z)로 매핑 (정규화 전).
    face 인덱스: 0:F +X, 1:R +Z, 2:B -X, 3:L -Z, 4:U +Y, 5:D -Y
    이미지 y는 아래로 증가하므로, 3D Y에는 음수 부호를 반영해야 함에 주의.
    관례적으로 다음 매핑을 사용합니다.
    """
    if face_idx == 0:   # Front  (+X)
        x, y, z = torch.ones_like(a), -b,  a
    elif face_idx == 1: # Right  (+Z)
        x, y, z = -a,    -b,  torch.ones_like(a)
    elif face_idx == 2: # Back   (-X)
        x, y, z = -torch.ones_like(a), -b, -a
    elif face_idx == 3: # Left   (-Z)
        x, y, z =  a,    -b, -torch.ones_like(a)
    elif face_idx == 4: # Up     (+Y)
        x, y, z =  a,     torch.ones_like(a), -b
    elif face_idx == 5: # Down   (-Y)
        x, y, z =  a,    -torch.ones_like(a),  b
    else:
        raise ValueError("face_idx must be in [0..5]")
    return x, y, z

def _spherical_from_dir(x: torch.Tensor, y: torch.Tensor, z: torch.Tensor):
    """
    방향 벡터를 구면좌표로 변환.
    theta ∈ [-pi, pi] (경도, +x→+z 시계방향 증가),
    phi   ∈ [-pi/2, pi/2] (위도, +y 위쪽 양수).
    """
    # 정규화
    inv_norm = torch.rsqrt(x*x + y*y + z*z)
    x = x * inv_norm
    y = y * inv_norm
    z = z * inv_norm

    theta = torch.atan2(z, x)   # [-pi, pi]
    phi   = torch.asin(y)       # [-pi/2, pi/2]
    return theta, phi

def _equirect_xy_from_spherical(theta: torch.Tensor, phi: torch.Tensor, w_in: int, h_in: int):
    """
    구면 좌표 → equirect 픽셀 좌표 (정수 인덱스; 수평 래핑).
    - theta: [-pi, pi] → x ∈ [0, w_in)
    - phi  : [-pi/2, pi/2] → y ∈ [0, h_in)
    """
    two_pi = 2.0 * math.pi
    # 연속 좌표 (float)
    x = (theta + math.pi) / two_pi * w_in
    y = ( (math.pi/2 - phi) / math.pi ) * h_in

    # 최근접 샘플링(원 코드 스타일에 맞춤) + 수평 래핑(mod)
    x_idx = torch.remainder(torch.round(x).to(torch.int64), w_in)
    y_idx = torch.clamp(torch.round(y).to(torch.int64), 0, h_in - 1)
    return x_idx, y_idx

def generate_e2c_grid(face_size: int, h_in: int, w_in: int, device: torch.device) -> torch.Tensor:
    """
    Equirect → Cubemap 매핑 그리드 생성
    반환: torch.Tensor([6, face, face, 2])  마지막 2는 (y, x) = 파노라마 인덱스
    """
    a, b = _make_linspace_face(face_size, device)  # [F,F]

    grids = []
    for i in range(6):
        x, y, z = _dir_from_face_uv(i, a, b)
        theta, phi = _spherical_from_dir(x, y, z)
        x_idx, y_idx = _equirect_xy_from_spherical(theta, phi, w_in, h_in)  # [F,F]
        grid = torch.stack([y_idx, x_idx], dim=-1)  # [F,F,2] -> (y,x)
        grids.append(grid)

    return torch.stack(grids, dim=0)  # [6,F,F,2]

def map_e2c(tensor_pano: torch.Tensor, tensor_e2c_grid: torch.Tensor) -> torch.Tensor:
    """
    :param tensor_pano: equirect 이미지 [H,W,3]
    :param tensor_e2c_grid: [6, F, F, 2]  (y,x) 인덱스
    :return: cubemap 텐서 [6, F, F, 3]
    """
    H, W, _ = tensor_pano.shape
    faces, F, _, _ = tensor_e2c_grid.shape

    # grid에서 인덱스 분리
    y = tensor_e2c_grid[..., 0]  # [6,F,F]
    x = tensor_e2c_grid[..., 1]  # [6,F,F]

    # 브로드캐스팅 인덱싱을 위해 batch 차원 추가
    y = y.view(faces, F, F, 1).expand(-1, -1, -1, 3)  # [6,F,F,3]
    x = x.view(faces, F, F, 1).expand(-1, -1, -1, 3)  # [6,F,F,3]

    pano_expanded = tensor_pano.view(1, H, W, 3)  # [1,H,W,3]
    # 고급 인덱싱: gather 비슷하게 사용
    # 인덱싱은 마지막 두 차원 (H,W)을 목표로 하므로, 아래처럼 한 번에 접근
    cubemap = pano_expanded[0, y, x, torch.tensor([0,1,2], device=tensor_pano.device)]
    return cubemap  # [6,F,F,3]

def pano2cubemap(
    face_size: int,
    pano_paths: list[tuple[str, list[str]]],
    device: Optional[torch.device] = None
):
    """
    :param face_size: 각 큐브면 해상도 (정사각형)
    :param pano_paths: [(pano_path, [F, R, B, L, U, D] 저장경로 리스트), ...]
    :param device: torch.device (미지정 시 자동 선택)
    """
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if len(pano_paths) == 0:
        raise ValueError("pano_paths is empty")

    for pano_path, save_paths in pano_paths:
        if not isinstance(save_paths, (list, tuple)) or len(save_paths) != 6:
            raise ValueError("save_paths must be a list of 6 paths: [F,R,B,L,U,D]")

        print(f"loading {pano_path}")
        # [C,H,W] -> [H,W,3]
        tensor_pano = load_image_as_tensor(pano_path).to(device).permute(1, 2, 0)
        H, W, _ = tensor_pano.shape

        print("Equirect -> Cubemap 매핑 그리드 생성")
        e2c_grid = generate_e2c_grid(face_size, H, W, device)  # [6,F,F,2]

        print("샘플링")
        tensor_cubemap = map_e2c(tensor_pano, e2c_grid)  # [6,F,F,3]

        # 저장
        labels = ["F","R","B","L","U","D"]
        for i, save_path in enumerate(save_paths):
            print(f"saving {labels[i]} -> {save_path}")
            save_tensor_as_image(tensor_cubemap[i].permute(2, 0, 1).cpu(), save_path)

# -------------------------
# 사용 예시
# -------------------------
# pano2cubemap(
#     face_size=1024,
#     pano_paths=[
#         (
#             "panorama.jpg",
#             ["F.jpg","R.jpg","B.jpg","L.jpg","U.jpg","D.jpg"]
#         )
#     ]
# )
