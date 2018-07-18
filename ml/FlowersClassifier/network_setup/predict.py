import argparse

from utils import output_cmd, get_device
from network_setup.flowers_network import Network

parser = argparse.ArgumentParser(description="Flowers predictor")
parser.add_argument('path_to_image', action='store')
parser.add_argument('path_to_checkpoint', action='store')
parser.add_argument('--top_k', action='store', dest="top_k", type=int, help='Predict k most probabilities')
parser.add_argument('--category_names', action='store', dest="cat_names", help='path to mapping file')
parser.add_argument('--gpu', action='store_true', default=False, dest="gpu",  help='turn gpu on')
parser.add_argument('--arch', action='store', dest="arch",  help='architecture')
cmd_dict = parser.parse_args()

nn = Network.load_model(arch=cmd_dict.arch, filename=cmd_dict.path_to_checkpoint, device=get_device(cmd_dict.gpu))
nn.predict(cmd_dict.path_to_image, cmd_dict.cat_names, topk=cmd_dict.top_k)