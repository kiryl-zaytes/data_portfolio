import matplotlib as mpl
mpl.use('TkAgg')
import os
import sys
import json
import numpy as np
from math import floor
from PIL import Image
from torchvision import datasets, transforms
from operator import itemgetter
import torch
import seaborn as sn
import matplotlib.pyplot as plt
from settings import DEFAULT_PATHS, IMAGE


def load_mapping(file_path):
    with open(file_path, 'r') as f:
        id_name = json.load(f)
    return id_name


def get_info(directory, mapping):
    data = {}
    with open(mapping, 'r') as f:
        id_name = json.load(f)

    for root, d, f in os.walk(directory):
        if len(f) != 0:
            dir_num = root.split('/')[2]
            data[id_name.get(dir_num)] = len(f)
    return zip(*sorted(data.items(), key=itemgetter(1)))


def prepare_data(data, batch_size):
    train = os.path.join('..', data, DEFAULT_PATHS['train'])
    valid = os.path.join('..', data, DEFAULT_PATHS['valid'])
    test = os.path.join('..', data, DEFAULT_PATHS['test'])

    train_batch, valid_batch, test_batch = batch_size

    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(IMAGE['crop'][0]),
        transforms.ToTensor(),
        transforms.Normalize(IMAGE['means'], IMAGE['std']),
    ])

    data_transforms = transforms.Compose([
        transforms.Resize(IMAGE['size']),
        transforms.CenterCrop(IMAGE['crop'][0]),
        transforms.ToTensor(),
        transforms.Normalize(IMAGE['means'], IMAGE['std']),
    ])

    # Load the datasets with ImageFolder
    training_datasets = datasets.ImageFolder(train, transform=train_transforms)
    validation_datasets = datasets.ImageFolder(valid, transform=data_transforms)
    testing_datasets = datasets.ImageFolder(test, transform=data_transforms)

    # Using the image datasets and the trainforms, define the dataloaders
    train_loader = torch.utils.data.DataLoader(training_datasets, batch_size=train_batch, shuffle=True)
    valid_loader = torch.utils.data.DataLoader(validation_datasets, batch_size=valid_batch, shuffle=True)
    testing_loader = torch.utils.data.DataLoader(testing_datasets, batch_size=test_batch)

    return train_loader, valid_loader, testing_loader


def index_prob(path, probs, labels, k=5):
    """
    Get top k probabilities and return real names of idx classes.
    """
    pid = torch.topk(probs, k)[1][0].cpu().numpy()
    ps = torch.topk(probs, k)[0][0].cpu().numpy()
    ids = [load_mapping(path).get(reverse_idx(labels, x)) for x in pid]
    return ps, ids


def output_result(self, image, topk):
    """
    Output sample + top k predictions.
    """
    for i in image:
        im = Image.open(i, 'r')
        ps = self.predict(i, topk=topk)
        data = index_prob(ps, topk)
        f, ax = plt.subplots(1, 2, figsize=(20, 5))
        ax[0].imshow(np.asarray(im))
        ax[1] = sn.barplot(x=data[0], y=data[1])


def output_cmd(path, model, image, topk):
    """
    Output sample + top k predictions.
    """
    for im in image:
        ps = model.predict(im, path, topk=topk)
        data = index_prob(path, ps, model.idx, k=topk)
        res = list(zip(data[0], data[1]))
        for i in res:
            print("Probability:{}%".format(round(i[0] * 100, 3)), "Flower:{}".format(i[1]) + "\n")


def process_image(image):
    ''' Scales, crops, and normalizes a PIL image for a PyTorch model,
        returns an Numpy array
    '''
    im = Image.open(image)
    width, height = im.size
    if width == height:
        im.thumbnail((IMAGE['size'], IMAGE['size']), Image.ANTIALIAS)
    if width > 256 or height > 256:
        if width > height:
            ratio = 256 / width
        else:
            ratio = 256 / height
    r_image= im.resize((floor(ratio * height), floor(ratio * width)))
    w, h = r_image.size
    l, t = ((w - IMAGE['crop'][0]) / 2, (h - IMAGE['crop'][1]) / 2)
    r, b = ((w + IMAGE['crop'][0]) / 2, (h + IMAGE['crop'][1]) / 2)
    r_image = r_image.crop((l, t, r, b))
    np_image = np.array(r_image)
    np_image = np_image / 255
    for i, value in enumerate(np_image, 0):
        for j, value2 in enumerate(np_image[i], 0):
            np_image[i, j] = (np_image[i][j] - np.array(IMAGE['means'])) / np.array(IMAGE['std'])
    return np_image.transpose((2, 1, 0))


def reverse_idx(labels, idx):
    """
    Match labels by idx class
    """
    for k, v in labels.items():
        if v == int(idx):
            return k


def get_device(is_gpu):
    set_to = None
    real_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if is_gpu:
        if str(real_device) == "cpu":
            print('gpu computations are not available on this machine')
        else:
            set_to = "cuda:0"
    else:
        set_to = "cpu"
    if set_to is None:
        sys.exit("GPU is not available")
    return set_to


def imshow(image, ax=None, title=None):
    """Imshow for Tensor."""
    if ax is None:
        fig, ax = plt.subplots()

    # PyTorch tensors assume the color channel is the first dimension
    # but matplotlib assumes is the third dimension
    image = image.transpose((1, 2, 0))

    # Undo preprocessing
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image = std * image + mean

    # Image needs to be clipped between 0 and 1 or it looks like noise when displayed
    image = np.clip(image, 0, 1)

    ax.imshow(image)

    return ax
