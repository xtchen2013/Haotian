import os
import torch
from utils.data_loader_era5 import get_data_loader
from utils.YParams import YParams
from networks.helpers import get_model
import matplotlib.pyplot as plt
from torchinfo import summary

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
#os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

# load swin-T-v2 hyperparameters
# params = YParams('config/swin.yaml', 'swin_71var')
# params.batch_size = 1
# params.n_future = 3
# params.n_in_channels=75
params = YParams('config/swin.yaml', 'swin_71var_geo_dp2_chwt_invar_4step')
params.add_zenith = False
params.add_orography = False
params.add_landmask = False
dataloader, dataset, sampler = get_data_loader(params, params.train_data_path, distributed=False, train=True)
valid_dataloader, dataset_valid = get_data_loader(params, params.valid_data_path, distributed=False, train=False)
# load model
device = torch.device("cuda:0")
# device = torch.device("cpu")
model = get_model(params).to(device)
# summary(model, input_size=(1, 71, 720, 1440))
iters = 0

with torch.no_grad():
    for i, data in enumerate(valid_dataloader, 0):                       # 365(366) * 4 = 1460(1464)
        if i >= 2:
            break
        # add_zenith: False (inp, tar), add_zenith: True (inp, tar, zen_inp, zen_tar)
        # inp -> (1, 71, 720, 1440)
        # tar -> (1, 71, 720, 1440)
        # zen_inp -> (1, 1, 720, 1440)
        # zen_tar -> (1, 1, 720, 1440)
        print("data len is %s" % len(data))
        iters += 1
        inp, tar = map(lambda x: x.to(device, dtype=torch.float), data[:2])  #
        print(inp.shape)
        print(tar.shape)
        # plt.rcParams["figure.figsize"] = (16, 9)
        # plt.figure()
        # for ch in range(inp.shape[1]):
        #     plt.subplot(3, 2, ch + 1)  # 3 raws * 2 cols
        #     plt.imshow(inp[0, ch, :, :].cpu(), cmap='RdBu')
        #     plt.colorbar()
        # plt.savefig(r"C:\Users\76480\Desktop" + '\\' + str(i) + ".png")
        # plt.close()
        gen = model(inp)
        print(gen.shape)
