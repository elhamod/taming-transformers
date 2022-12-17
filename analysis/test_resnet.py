# License: BSD
# Author: Sasank Chilamkurthy


import os
from taming.analysis_utils import get_phylomapper_from_config
from taming.data.phylogeny import Phylogeny
from taming.plotting_utils import dump_to_json, plot_confusionmatrix
import torch
import torch.nn as nn
from torchvision import datasets
import numpy
import albumentations

import argparse
from omegaconf import OmegaConf
from tqdm import tqdm

from torchmetrics import F1Score


def get_input(x):
    if len(x.shape) == 3:
        x = x[..., None]
    x = x.permute(0, 3, 1, 2).to(memory_format=torch.contiguous_format)
    return x.float()

class Processor:
    def __init__(self, size):
        self.size = size
        
    def get_preprocess_image(self):
        def preprocess_image(image):
            if not image.mode == "RGB":
                image = image.convert("RGB")
            image = numpy.array(image).astype(numpy.uint8)
            
            rescaler = albumentations.SmallestMaxSize(max_size = self.size)
            cropper = albumentations.CenterCrop(height=self.size,width=self.size)
            preprocessor = albumentations.Compose([rescaler, cropper])

            image = preprocessor(image=image)["image"]
            image = (image/127.5 - 1.0).astype(numpy.float32)
            return image
        
        return preprocess_image
        
@torch.no_grad()
def main(configs_yaml):
    DEVICE= configs_yaml.DEVICE
    size= configs_yaml.size
    bb_model_path = configs_yaml.bb_model_path
    dataset_path = configs_yaml.dataset_path
    batch_size= configs_yaml.batch_size
    num_workers= configs_yaml.num_workers
    phylogeny_path = configs_yaml.phylogeny_path
    
    level = 3
    if phylogeny_path is not None:
        level = configs_yaml.level
        phyloDistances_string = configs_yaml.phyloDistances_string
    
    
    dataset_test = datasets.ImageFolder(dataset_path, transform= Processor(size).get_preprocess_image())
    dataloader = torch.utils.data.DataLoader(dataset_test, batch_size=batch_size,
                                             shuffle=False, num_workers=num_workers)
    
    indx_to_class = {v: k for k, v in dataset_test.class_to_idx.items()}
    
    if phylogeny_path is not None:
        phylomapper = get_phylomapper_from_config(Phylogeny(phylogeny_path), phyloDistances_string, level)
        num_classes = phylomapper.get_len()
    else:
        num_classes = len(indx_to_class.keys())
        
    model_ft = torch.load(bb_model_path)
    model_ft.eval()
    

    F1 = F1Score(num_classes=num_classes, multiclass=True).to(DEVICE)
    
    preds = []
    classes = []
    for img, target in tqdm(dataloader):
        if phylogeny_path is not None:
            target = phylomapper.get_mapped_truth(target)

        classes.append(target)
        preds.append(model_ft(get_input(img).to(DEVICE)))
    classes = torch.cat(classes, dim=0).to(DEVICE)
    
    preds = torch.cat(preds, dim=0)
    
    a = sorted(set([i.item() for i in classes]))
    class_names = [indx_to_class[i] for i in a]
    print("calculate F1 and Confusion matrix")
    plot_confusionmatrix(preds, classes, class_names, os.path.join(dataset_path, 'fake'), title="Confusion Matrix according to BB model - level {}".format(level))            
    
    test_measures = {}
    test_measures['class_f1'] = F1(preds, classes).item()
    dump_to_json(test_measures, os.path.join(dataset_path, 'fake'), name='f1_BB- level {}'.format(level))
    





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--config",
        type=str,
        nargs="?",
        const=True,
        default="analysis/configs/test_resnet.yaml",
    )
    
    cfg, _ = parser.parse_known_args()
    configs = OmegaConf.load(cfg.config)
    cli = OmegaConf.from_cli()
    config = OmegaConf.merge(configs, cli)
    print(config)
    
    main(config)