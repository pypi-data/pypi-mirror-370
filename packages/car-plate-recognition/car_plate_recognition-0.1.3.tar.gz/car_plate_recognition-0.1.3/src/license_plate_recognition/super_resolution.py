import os
import platform
import torch
import requests
import cv2
import numpy as np

from .network_swinir import SwinIR as net
from . import util_calculate_psnr_ssim as util

class SuperResolution:

    def __init__(self, model_path: str, download_model:bool = False):
        scale:int = 4
        self.__model_path = model_path
        
        if not os.path.exists(model_path) and not download_model:
            raise ValueError(f"The model path {model_path} does not exist.")
        
        if not os.path.isfile(model_path) and download_model:
            self.__download_model()

        if 'pth' not in model_path:
            raise ValueError("The model path must point to a .pth file.")
        
        
        self.__param_key_g = 'params_ema'
        self.__scale = scale
        self.__window_size = 8

        os_name = platform.system().lower()

        self.__device = 'cpu'

        if os_name == 'windows':
            self.__device = 'cuda' if torch.cuda.is_available() else 'cpu'
        elif os_name == 'linux':
            self.__device = 'cuda' if torch.cuda.is_available() else 'cpu'
        elif os_name == 'darwin':
            self.__device = 'mps' if torch.backends.mps.is_available() else 'cpu'

        self.__load_model()
        
    def __load_model(self):
        self.__model = net( upscale=self.__scale, in_chans=3, img_size=64, window_size=8,
                            img_range=1., depths=[6, 6, 6, 6, 6, 6, 6, 6, 6], embed_dim=240,
                            num_heads=[8, 8, 8, 8, 8, 8, 8, 8, 8],
                            mlp_ratio=2, upsampler='nearest+conv', resi_connection='3conv')
        pretrained_model = torch.load(self.__model_path)
        self.__model.load_state_dict(pretrained_model[self.__param_key_g] if self.__param_key_g in pretrained_model.keys() else pretrained_model, strict=True)
        self.__model.eval().to(self.__device)


    def __download_model(self):
        os.makedirs(os.path.dirname(self.__model_path), exist_ok=True)
        url = f'https://github.com/JingyunLiang/SwinIR/releases/download/v0.0/003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth'
        r = requests.get(url, allow_redirects=True)
        open(self.__model_path, 'wb').write(r.content)

    def __get_image_pair(self, image_path:str):
        (imgname, imgext) = os.path.splitext(os.path.basename(image_path))
        img_gt = None
        img_lq = cv2.imread(image_path, cv2.IMREAD_COLOR).astype(np.float32) / 255.
        return imgname, img_lq, img_gt

    def run_super_resolution(self, image_path:str, out_path:str) -> str:
        imgname, img_lq, img_gt = self.__get_image_pair(image_path)
        img_lq = np.transpose(img_lq if img_lq.shape[2] == 1 else img_lq[:, :, [2, 1, 0]], (2, 0, 1))  
        img_lq = torch.from_numpy(img_lq).float().unsqueeze(0).to(self.__device) 
        with torch.no_grad():
            _, _, h_old, w_old = img_lq.size()
            h_pad = (h_old // self.__window_size + 1) * self.__window_size - h_old
            w_pad = (w_old // self.__window_size + 1) * self.__window_size - w_old
            img_lq = torch.cat([img_lq, torch.flip(img_lq, [2])], 2)[:, :, :h_old + h_pad, :]
            img_lq = torch.cat([img_lq, torch.flip(img_lq, [3])], 3)[:, :, :, :w_old + w_pad]
            output = self.__model(img_lq)
            output = output[..., :h_old * self.__scale, :w_old * self.__scale]

            output = output.data.squeeze().float().cpu().clamp_(0, 1).numpy()
            if output.ndim == 3:
                output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))  # CHW-RGB to HCW-BGR
            output = (output * 255.0).round().astype(np.uint8)  # float32 to uint8
            cv2.imwrite(out_path, output)


    

