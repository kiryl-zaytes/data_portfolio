import os
from collections import OrderedDict
import torch
from torch import nn
from utils import process_image, prepare_data, load_mapping, reverse_idx, index_prob, get_device
from settings import ARCHITECTURES, BATCH_SIZES


class Network:
    def __init__(self, data=None, arch=None, filename='checkpoint.pth', device='cpu'):
        """
          Get pre-trained network and switch off gradient calculation. Swap classifier with provided and put Tensors to
          actual type of device (cuda or cpu).
        """
        self.train_loader, self.valid_loader, self.testing_loader = None, None, None
        self.epoch_storage = []
        self._optimizer = None
        self._criterion = None
        self._classifier = None
        self.testing_acc = None
        self.testing_loss = None
        self.device = device

        if arch is not None:
            self.model = ARCHITECTURES[arch](pretrained=True)
            for p in self.model.parameters():
                p.requires_grad = False
            self.model.to(self.device)

        if data is not None:
            self.get_data(data, BATCH_SIZES)

    @property
    def optimizer(self):
        return self._optimizer

    @optimizer.setter
    def optimizer(self, opt):
        if opt is not None:
            self._optimizer = opt

    @property
    def criterion(self):
        return self._criterion

    @criterion.setter
    def criterion(self, crit):
        if crit is not None:
            self._criterion = crit

    @property
    def classifier(self):
        return self._classifier

    @classifier.setter
    def classifier(self, classifier):
        if classifier is not None:
            self._classifier = classifier
            self.model.classifier = self._classifier
            self.model.to(self.device)

    @staticmethod
    def build_classifier(in_features, out_features, act, out):
        """
        Creates network with given sizes and activation functions.
        :param in_features: Array of input sizes for each layer
        :param out_features: Array of output sizes for each layer
        :param act: Activation function
        :param out: Out function
        :return: model
        """
        network = []
        c = list(zip(in_features, out_features))
        for j, i in enumerate(c):
            network.append(('L' + str(j), nn.Linear(*i)))
            if len(c) != j + 1:
                network.append(('A' + str(j), act()))
        network.append(('out', out(dim=1)))
        return nn.Sequential(OrderedDict(network))

    def predict(self, image_path, mapping_path, topk=3):
        """
        Predict the class (or classes) of an image using a trained deep learning model.
        :param image_path: path to image
        :mapping_path: path mapping json file
        :return: probabilities
        """
        img = process_image(image_path)
        self.model.eval()
        img = torch.from_numpy(img).to(self.device)
        img.unsqueeze_(0)
        model = self.model.double()
        with torch.no_grad():
            o = model.forward(img)
            ps = torch.exp(o)

        data = index_prob(mapping_path, ps, self.idx, k=topk)
        res = list(zip(data[0], data[1]))
        for i in res:
            print("Probability:{}%".format(round(i[0] * 100, 3)), "Flower:{}".format(i[1]) + "\n")

    def save_model(self, filename, arch=None, check=None):
        if check is None:
            check = {
                'architecture': arch,
                'classifier': self.classifier,
                'state_dict': self.model.state_dict(),
                'optimizer': self.optimizer,
                'criterion': self.criterion,
                'epoch_res': self.epoch_storage,
                'classes': self.train_loader.dataset.class_to_idx
            }
        torch.save(check, filename)

    def get_data(self, path, batch):
        self.train_loader, self.valid_loader, self.testing_loader = prepare_data(path, batch)

    @staticmethod
    def load_model(arch='vgg11', filename='checkpoint_new.pth', device='cpu'):
        model_file = torch.load(filename, map_location=lambda storage, loc: storage)
        n = Network(arch=arch, device=device)
        n.classifier = model_file['classifier']
        n.idx = model_file['classes']
        n.epoch_storage = model_file['epoch_res']
        n.model.load_state_dict(model_file['state_dict'])
        n.model.to(device)
        return n

    def train_model(self, n_epoch=5, steps_to_interm_res=40):
        """
        Train feed forward network number of epochs and print result after steps_to_interm_res. Store result after each
        epoch to dictionary.
        """
        steps = 0
        epoch_results = {}

        for i in range(n_epoch):
            r_loss = 0
            test_loss = 0
            acc = 0
            for ii, (inp, lbl) in enumerate(self.train_loader):
                steps += 1
                inp, lbl = inp.to(self.device), lbl.to(self.device)
                self.optimizer.zero_grad()
                output = self.model.forward(inp)
                loss = self.criterion(output, lbl)
                loss.backward()
                self.optimizer.step()
                r_loss += loss.item()

                if steps % steps_to_interm_res == 0:
                    acc, test_loss = self.validate(self.valid_loader)
                    print("Epoch {} out of {}".format(i + 1, n_epoch))
                    print("Running training loss {:.4f}".format(r_loss / ((i + 1) * steps_to_interm_res)))
                    print("Running validation loss {:.4f}".format(test_loss))
                    print("Accuracy {}%".format(100 * acc))
                    #                 r_loss=0

            epoch_results['training_loss'] = r_loss / len(self.train_loader)
            epoch_results['validation_loss'] = test_loss
            epoch_results['acc'] = acc
            print(epoch_results['training_loss'], epoch_results['validation_loss'], epoch_results['acc'])
            self.epoch_storage.append(epoch_results.copy())

    def validate(self, test_loader):
        """
        Put model in evaluation state and alculate losses on validation set.
        Return: mean accuracy and mean validation loss.
        """
        test_loss = 0
        acc = 0
        total = 0
        self.model.eval()
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                output = self.model.forward(images)
                test_loss += self.criterion(output, labels).item()
                _, pred = torch.max(output.data, 1)
                total += labels.size(0)
                acc += (pred == labels).sum().item()
        self.model.train()
        return round(acc / total, 2), round(test_loss / len(test_loader), 4)

    def test(self):
        self.testing_acc, self.testing_loss = self.validate(self.testing_loader)
        print("Accuracy on testing set is {} %".format(100 * self.testing_acc))
        print("Loss on testing set is {} ".format(self.testing_loss))

    def index_prob(self, data_dir, probs, k=5):
        """
        Get top k probabilities and return real names of idx classes.
        """
        pid = torch.topk(probs, k)[1][0].cpu().numpy()
        ps = torch.topk(probs, k)[0][0].cpu().numpy()
        labels = self.train_loader.dataset.class_to_idx
        mapping = load_mapping(os.path.join(data_dir, 'cat_to_name.json'))
        ids = [mapping.get(reverse_idx(labels, x)) for x in pid]
        return ps, ids
