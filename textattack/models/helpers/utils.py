import os

import torch

from textattack.shared import utils


def load_cached_state_dict(model_folder_path):
    # model_folder_path = '/p/qdata/jm8wx/datasets/sst-models/wordCNN'
    model_folder_path = "/p/qdata/jm8wx/datasets/sst-models/wordLSTM/"
    print("model_folder_path /", model_folder_path)
    # model_folder_path = utils.download_if_needed(model_folder_path)
    model_path = os.path.join(model_folder_path, "model.bin")
    state_dict = torch.load(model_path, map_location=utils.device)
    return state_dict
