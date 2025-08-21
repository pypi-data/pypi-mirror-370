from typing import Optional
import torch
from torchvision import transforms
from PIL import Image

to_pil = transforms.ToPILImage()
transform = transforms.ToTensor()

def load_image_as_tensor(filepath:str) -> torch.Tensor:
    image = Image.open(filepath).convert('RGB')
    return transform(image) # 0~255 -> 0~1

def save_tensor_as_image(tensor, save_path):
    image = to_pil(tensor)
    image.save(save_path)


def generate_equi_facetype(h: int, w: int, device: torch.device) -> torch.Tensor:
    """
        등장방형 마스크 생성
        :return: torch.Tensor([h,w]) -> 012345(FRBLUD)
    """
    int_dtype = torch.int64

    # 기본 face 타입 생성
    tensor_facetype = torch.arange(4, dtype=int_dtype, device=device).repeat_interleave(w // 4).unsqueeze(0)
    tensor_facetype = tensor_facetype.repeat(h, 1)
    tensor_facetype = torch.roll(tensor_facetype, shifts=3 * w // 8, dims=1)

    # ceil mask 준비
    w_ratio = (w - 1) / w
    h_ratio = (h - 1) / h

    theta = torch.linspace(-torch.pi * w_ratio, torch.pi * w_ratio, w // 4)
    idx = h // 2 - torch.round(torch.atan(torch.cos(theta / 4)) * h / (torch.pi * h_ratio)).to(int_dtype)

    mask = torch.zeros((h, w // 4), dtype=torch.bool, device=device)
    for i, j in enumerate(idx):
        mask[:j, i] = 1

    mask = torch.cat([mask] * 4, dim=1)
    mask = torch.roll(mask, 3 * w // 8, dims=1)

    tensor_facetype[mask] = 4
    tensor_facetype[torch.flip(mask, dims=(0,))] = 5

    return tensor_facetype.to(int_dtype)


def generate_c2e_grid(h_out: int, w_out: int, face_size: int, tensor_facetype:torch.Tensor, device: torch.device) -> torch.Tensor:
    """
        등장방형 -> 큐브맵 매핑 그리드 생성

        :return c2e_grid: torch.Tensor([3,h,w])
            [h][w][0] = face type; 0F 1R 2B 3L 4U 5D
            [h][w][1] = h
            [h][w][2] = w
    """
    dtype = torch.float32

    w_ratio = (w_out - 1) / w_out
    h_ratio = (h_out - 1) / h_out
    theta = torch.linspace(-(torch.pi * w_ratio), torch.pi * w_ratio, steps=w_out, dtype=dtype, device=device)
    phi = torch.linspace((torch.pi * h_ratio) / 2, -(torch.pi * h_ratio) / 2, steps=h_out, dtype=dtype, device=device)
    phi, theta = torch.meshgrid([phi, theta], indexing="ij")


    # Initialize coordinate maps
    coor_x = torch.zeros((h_out, w_out), dtype=dtype, device=device)
    coor_y = torch.zeros((h_out, w_out), dtype=dtype, device=device)

    for i in range(6):
        mask = tensor_facetype == i
        theta_masked = theta[mask]
        phi_masked = phi[mask]
        
        if i < 4:
            coor_x[mask] = 0.5 * torch.tan(theta_masked - torch.pi * i / 2)
            coor_y[mask] = -0.5 * torch.tan(phi_masked) / torch.cos(theta_masked - torch.pi * i / 2)
        else:
            c = 0.5 * torch.tan(torch.pi / 2 - torch.abs(phi_masked)) # 문제 시 torch.abs 부분 확인
            coor_x[mask] = c * torch.sin(theta_masked)
            coor_y[mask] = c * (1 if i == 4 else -1) * torch.cos(theta_masked)

    # Final renormalize and adjust coordinates
    coor_x = torch.clamp((coor_x + 0.5) * face_size, 0, face_size - 1).int()
    coor_y = torch.clamp((coor_y + 0.5) * face_size, 0, face_size - 1).int()

    c2e_grid = torch.stack((coor_y, coor_x, tensor_facetype)).to(device)
    return c2e_grid

    
def map_c2e(tensor_cubemap: torch.Tensor, tensor_c2e_grid: torch.Tensor) -> torch.Tensor:
    """
        :param tensor_cubemap: cubemap image. torch.Tensor([6,h,w,3])

        :param tensor_c2e_grid: cubemap grid. torch.Tensor([h,w,3])
        [h][w][0] = y
        [h][w][1] = x
        [h][w][2] = face type
    """
    y, x, facetype = tensor_c2e_grid
    tensor_img_new = tensor_cubemap[facetype, y, x]
    return tensor_img_new

def get_image_width(image_path: str) -> int:
    image = Image.open(image_path)
    return image.width

def cubemap2pano(width:int, height:int, cubemap_paths: list[tuple[list[str], str]], device: Optional[torch.device]=None):
    """
        :param width: output image width
        :param height: output image height
        :param cubemap_paths: list of tuple
            - cubemap_paths: list of cubemap image paths. [F, R, B, L, U, D]
            - save_path: output image path
            [
                (["F.jpg", "R.jpg", "B.jpg", "L.jpg", "U.jpg", "D.jpg"], "result.jpg"),
                ...
            ]

    """
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if len(cubemap_paths) == 0:
        raise ValueError("cubemap_paths is empty")

    # face_width = tensor_cubemap_list[0][0].shape[1]
    face_width = get_image_width(cubemap_paths[0][0][0])

    print("등장방형 마스크 생성")
    tensor_facetype = generate_equi_facetype(height, width, device)

    print("매핑 그리드 생성")
    c2e_grid = generate_c2e_grid(height, width, face_width, tensor_facetype, device)
    for cube_paths, save_path in cubemap_paths:
        tensor_cubemap = torch.stack([load_image_as_tensor(cube_path).to(device) for cube_path in cube_paths]).permute(0, 2, 3, 1)

        print(f"processing {save_path}")
        # 큐브맵->등장방형 매핑
        tensor_result = map_c2e(tensor_cubemap, c2e_grid)
        # 이미지 저장
        save_tensor_as_image(tensor_result.permute(2, 0, 1), save_path)
