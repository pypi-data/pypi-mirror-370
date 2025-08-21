import os

import numpy as np
import torch
from PIL import Image
from torch.nn.functional import softmax

from root_painter_trainer.unet import UNetGNRes


def test_unet_gn_res_smoke(tmp_path):
    """
    A smoke test for UNetGNRes.
    It creates a black image, runs inference, and checks output shape.
    This is based on the original __main__ block in unet.py
    """
    unet = UNetGNRes()
    unet.eval()

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    unet.to(device)

    test_input = np.zeros((1, 3, 572, 572))
    test_input = torch.from_numpy(test_input).float().to(device)

    with torch.no_grad():
        output = unet(test_input)

    assert output.shape == (1, 2, 500, 500)

    softmaxed = softmax(output, 1)[:, 1, :, :]  # just fg probability
    softmaxed = softmaxed[0, :, :]  # single image

    assert softmaxed.shape == (500, 500)

    # test saving image
    im_arr = softmaxed.cpu().numpy() * 255
    im = Image.fromarray(im_arr.astype(np.uint8))

    out_fpath = os.path.join(tmp_path, 'out.png')
    im.save(out_fpath)
    assert os.path.exists(out_fpath)
