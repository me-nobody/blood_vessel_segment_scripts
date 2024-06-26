# -*- coding: utf-8 -*-
"""blood_vessel_augmentations_may24.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1VgMeysm_hKRwyzC29XqTZnG7TH34RShq

This code is adapted from [kaggle notebook Semantic Segmentation is easy](https://https://www.kaggle.com/code/ligtfeather/semantic-segmentation-is-easy-with-pytorch)
"""

from google.colab import drive
drive.mount('/content/drive')

"""OK. I am putting 8955_2023_image1.png and its mask to the location for histosegnet data"""

!pip install segmentation-models-pytorch --quiet

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms as T
import albumentations as A
import torchvision
import torch.nn.functional as F
from torch.autograd import Variable
from torch.nn.functional import normalize
import torchvision.transforms as transforms

import tifffile
from PIL import Image
import cv2

from sklearn.model_selection import train_test_split

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import time
import os
from tqdm.notebook import tqdm

"""I am creating a folder for original images and their masks, after augmentation. This is made of slides from histosegnet data and few NVU slides which I annotated myself."""

rm *.png

!cp *.png /content/drive/MyDrive/histoSegNet_data/img/01_tuning_patch/all_images/

!cp *.png /content/drive/MyDrive/histoSegNet_data/gt/01_tuning_patch/morph/all_images/

"""I have transferred all the self annotated images to the common folder"""

# access google drive
IMAGE_PATH = '/content/drive/MyDrive/histoSegNet_data/img/01_tuning_patch/all_images/'
len(os.listdir(IMAGE_PATH))

MASK_PATH = '/content/drive/MyDrive/histoSegNet_data/gt/01_tuning_patch/morph/all_images/'
len(os.listdir(MASK_PATH))

!cp  /content/drive/MyDrive/histoSegNet_data/img/01_tuning_patch/all_images/*.png .

!cp  /content/drive/MyDrive/histoSegNet_data/gt/01_tuning_patch/morph/all_images/*.png .

!zip histosegnet_images.zip ./*.png

!zip histosegnet_masks.zip ./*.png

"""We have to now frame the dataset class for our images"""

n_classes = 20

def create_df():
    name = []
    for dirname, _, filenames in os.walk(IMAGE_PATH):
        for filename in filenames:
            name.append(filename[:-4])

    return pd.DataFrame({'id': name}, index = np.arange(0, len(name)))

df = create_df()
print('Total Images: ', len(df))

df.head()

#split data
X_train, X_test = train_test_split(df['id'].values, test_size=0.1, random_state=19)

print('Train Size   : ', len(X_train))
print('Test Size    : ', len(X_test))

df['id'][40]

img = Image.open(IMAGE_PATH + df['id'][40] + '.png')
mask = Image.open(MASK_PATH + df['id'][40] + '.png')
print('Image Size', np.asarray(img).shape)
print('Mask Size', np.asarray(mask).shape)

fig,ax = plt.subplots(1,2,figsize = (5,5))
ax = ax.ravel()
ax[0].imshow(img)
ax[0].set_title('tissue')
ax[1].imshow(mask)
ax[1].set_title('mask')
plt.show()

"""### DATASET

### we have to map all the classes in the mask and limit it to 20 classes
"""

class SlideAugmentDataset(Dataset):

  """we are returning integer dtype numpy arrays here to be used
    as input for Albumentations library. The input images are from
    HistoSegNet database and 5 images from my NVU dataset"""

  def __init__(self, img_path, mask_path, X):
      self.img_path = img_path
      self.mask_path = mask_path
      self.X = X

  def __len__(self):
      return len(self.X)

  def __getitem__(self, idx):
      img_x = 640 # divisible by 32 for the CNN to work
      img_y = 640 # divisible by 32 for hte CNN to work
      img = cv2.imread(self.img_path + self.X[idx] + '.png')
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      img = cv2.resize(img,(img_x,img_y),cv2.INTER_LINEAR)

      #img = Image.fromarray(img)
      mask = cv2.imread(self.mask_path + self.X[idx] + '.png')
      mask = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
      mask = cv2.resize(mask,(img_x,img_y),cv2.INTER_LINEAR)
      # we are re-mapping the mask
      x = mask.shape[0]
      y = mask.shape[1]
      for i in range(x):
        for j in range(y):
          if mask[i,j] <= 30:
            mask[i,j] = 0
          elif mask[i,j] > 30 and mask[i,j] <= 50:
            mask[i,j] = 1
          elif mask[i,j] > 50 and mask[i,j] <= 70:
            mask[i,j] = 2
          elif mask[i,j] > 70 and mask[i,j] <= 90:
            mask[i,j] = 3
          elif mask[i,j] > 90 and mask[i,j] <= 100:
            mask[i,j] = 4
          elif mask[i,j] > 100 and mask[i,j] <= 120:
            mask[i,j] = 5
          elif mask[i,j] > 120 and mask[i,j] <= 130:
            mask[i,j] = 6
          elif mask[i,j] > 130 and mask[i,j] <= 140:
            mask[i,j] = 7
          elif mask[i,j] > 140 and mask[i,j] <= 150:
            mask[i,j] = 8
          elif mask[i,j] > 150 and mask[i,j] <= 160:
            mask[i,j] = 9
          elif mask[i,j] > 160 and mask[i,j] <= 170:
            mask[i,j] = 10
          elif mask[i,j] > 170 and mask[i,j] <= 180:
            mask[i,j] = 11
          elif mask[i,j] > 180 and mask[i,j] <= 190:
            mask[i,j] = 12
          elif mask[i,j] > 190 and mask[i,j] <= 230:
            mask[i,j] = 13
          elif mask[i,j] > 230 and mask[i,j] <= 255:
            mask[i,j] = 14

      mask = np.tile(mask,(3,1,1)) # same size as input image
      mask = np.moveaxis(mask,0,2) # same shape as input image

      return img, mask

slide_dataset = SlideAugmentDataset(IMAGE_PATH,MASK_PATH,X_train)

!mkdir /content/drive/MyDrive/BBB/

!mkdir /content/drive/MyDrive/BBB/images
!mkdir /content/drive/MyDrive/BBB/masks

AUG_IMG_PATH = "/content/drive/MyDrive/BBB/images"
AUG_MSK_PATH = "/content/drive/MyDrive/BBB/masks"

pwd

!zip /content/aug_images.zip /content/drive/MyDrive/BBB/images/*.png

!zip /content/aug_masks.zip /content/drive/MyDrive/BBB/masks/*.png

slide_img,slide_mask = slide.__getitem__(10)

"""#### The mask has been re-mapped to less than the 20 classes in the model"""

np.unique(slide_mask)

slide_img.shape, slide_mask.shape



t_train = A.Compose([A.HorizontalFlip(p=0.6),
                     A.VerticalFlip(p=0.6),
                     A.GridDistortion(p=0.5),
                     A.OpticalDistortion(p=0.5),
                     A.Sharpen(p=0.4),
                     A.CLAHE(p=0.3),
                     A.Defocus(p=0.2),
                     A.RandomSnow(p=0.4)])

t_val = A.Compose([A.Resize(640, 640, interpolation=cv2.INTER_NEAREST), A.HorizontalFlip(),A.GridDistortion(p=0.2)])

fig,ax = plt.subplots(1,2,figsize = (5,5))
ax = ax.ravel()
ax[0].imshow(slide_img)
ax[0].set_title('slide_image')
ax[1].imshow(slide_mask[:,:,0])
ax[1].set_title('slide_mask')
plt.show()

def get_augmented_images(slide_dataset):
  len_dataset = len(slide_dataset)
  transformed_img_list =[]
  transformed_msk_list = []
  print(f"dataset has {len_dataset} images")
  for idx in range(len_dataset):
    slide_img,slide_mask = slide.__getitem__(idx)
    slide_mask = slide_mask[:,:,0]
    #print(f"image shape {slide_img.shape}")
    #print(f"mask shape {slide_mask.shape}")
    transformed_img_list.append(slide_img)
    transformed_msk_list.append(slide_mask)
    # add the augmentations
    for ndx in range(20):
      transformed = t_train(image = slide_img,mask = slide_mask)
      t_sl_img = transformed['image']
      t_sl_msk = transformed['mask']
      transformed_img_list.append(t_sl_img)
      transformed_msk_list.append(t_sl_msk)
    print(f"total images in library {len(transformed_img_list)}")
    print(f"total masks in library {len(transformed_msk_list)}")
    #break
  return transformed_img_list,transformed_msk_list

transformed_img_list,transformed_msk_list = get_augmented_images(slide_dataset)

for i,pair in enumerate(zip(transformed_img_list,transformed_msk_list)):
  image_name = "img_"+str(i+1)+".png"
  mask_name = "img_"+str(i+1)+".png"
  image_path = os.path.join(AUG_IMG_PATH,image_name)
  mask_path = os.path.join(AUG_MSK_PATH,image_name)
  cv2.imwrite(image_path,pair[0])
  cv2.imwrite(mask_path,pair[1])

!ls /content/drive/MyDrive/BBB/masks

fig,ax = plt.subplots(4,4,figsize = (8,8))
ax = ax.ravel()
for i in range(16):
  ax[i].imshow(transformed_img_list[i])
fig.tight_layout()
plt.show()

fig,ax = plt.subplots(4,4,figsize = (8,8))
ax = ax.ravel()
for i in range(16):
  ax[i].imshow(transformed_msk_list[i][:,:,2])
plt.show()

