from torchvision import models

# To extend if needed
ARCHITECTURES = {'vgg11': models.vgg11,
                 'densenet121': models.densenet121,
                 'resnet-34': models.resnet34
                 }
# Data paths
DEFAULT_PATHS = {'train': 'train',
                 'valid': 'valid',
                 'test': 'test'}

# bags for each loader : training, validation, testing
BATCH_SIZES = (64, 64, 32)


# Images section

IMAGE = {'size': 256,
         'crop': (224, 224),
         'means': [0.485, 0.456, 0.406],
         'std': [0.229, 0.224, 0.225]}
