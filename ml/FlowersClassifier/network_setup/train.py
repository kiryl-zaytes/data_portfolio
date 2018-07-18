import argparse

import torch
from torch import nn

from network_setup.flowers_network import Network
from utils import get_device

parser = argparse.ArgumentParser(description="Flowers classifier")

parser.add_argument('dir_name', action='store')
parser.add_argument('--save_dir', action='store', default='./', dest="dir", help='Set directory directory name to'
                                                                                 'take data from')
parser.add_argument('--arch', action='store', dest="architecture", help='Pre-trained network architecture')
parser.add_argument('--learning_rate', action='store', dest="alpha", type=float, help='gradient step')
parser.add_argument('--input_layer', action='append', dest="input_features", type=int, help='layers input sizes')
parser.add_argument('--output_layer', action='append', dest="output_features", type=int, help='layers output sizes')
parser.add_argument('--epochs', action='store', default=3, dest="epochs", type=int, help='epochs to train model')
parser.add_argument('--gpu', action='store_true', default=False, dest="gpu", help='turn gpu on')
cmd_dict = parser.parse_args()

n = Network(cmd_dict.dir_name, cmd_dict.architecture, device=get_device(cmd_dict.gpu))

try:
    connector = n.model.classifier[0].in_features
except TypeError:
    connector = n.model.classifier.in_features
except AttributeError:
    connector = n.model.fc.in_features

cmd_dict.output_features.insert(0, cmd_dict.input_features[0])
cmd_dict.input_features.insert(0, connector)

n.model.classifier = Network.build_classifier(cmd_dict.input_features,
                                              cmd_dict.output_features,
                                              nn.ReLU,
                                              nn.LogSoftmax)

n.optimizer = torch.optim.Adam(n.model.classifier.parameters(), lr=cmd_dict.alpha)
n.criterion = nn.NLLLoss()
n.train_model(n_epoch=cmd_dict.epochs)
n.test()
n.save_model(filename=cmd_dict.dir + '/' +
                      str(cmd_dict.architecture)+'_' +
                      str(cmd_dict.epochs) + '_' +
                      str(cmd_dict.alpha) + '_' +
                      str(n.testing_acc) + '_' +
                      str(n.testing_loss) + '.pth', arch=cmd_dict.architecture)
