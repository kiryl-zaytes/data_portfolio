In this project, I'll train an image classifier to recognize different species of flowers. 
Lets imagine using something like this in a phone app that tells you the name of the flower your camera is looking at.
App is organized as console program and could be run using several predifined commands with their keys as below. 

Folders structure:
- **checkpoints** - folder to store checkpoints
- **flowers** - data folder could be downloaded from http://www.robots.ox.ac.uk/~vgg/data/bicos/data/oxfordflower102.tar, should be
added before trainig.
- **cat_to_name.json** - mapping file
- **flowers_network** - main class to build nn with required methods
- **predict** - entry point to start prediction
- **train** - entry point to start training
- **utils** - supporting code

**Example** how to use cmd commands to train and predict. I changed a bit keys to be more usable.

- python network_setup/train.py flowers --save_dir ../checkpoints --arch vgg11 --learning_rate 0.001 --input_layer 12800 --output_layer 2500 --input_layer 2500 --output_layer 250 --output_layer  102 --epochs 7 --gpu

- python FlowersClassifier/network_setup/train.py flowers --save_dir ../checkpoints --arch densenet121 --learning_rate 0.001 --input_layer 200  --output_layer 102 --epochs 7 --gpu

- python FlowersClassifier/network_setup/predict.py FlowersClassifier/flowers/rose.jpeg FlowersClassifier/checkpoints/densenet121_7_0.001_0.93_0.3148.pth --top_k 5 --arch densenet121 --category_names FlowersClassifier/cat_to_name.json
