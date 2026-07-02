import torch
from networks.helpers import get_model
from utils.YParams import YParams
import numpy as np
from torchinfo import summary

params = YParams('./config/swin.yaml', 'swin_71var')
params['in_channels'] = np.array(params['in_channels'])
params['out_channels'] = np.array(params['out_channels'])
params['n_in_channels'] = len(params['in_channels'])
params['n_out_channels'] = len(params['out_channels'])
device = torch.device("cuda:7")
model = get_model(params).to(device)
summary(model, input_size=(1, 71, 720, 1440))


