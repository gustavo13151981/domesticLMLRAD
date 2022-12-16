# Hugging face dataset image downloader for Edge Impulse
# Domestic ML LRAD project
# Roni Bandini, Dec 2022

# Requisites
# pip install datasets
# pip install datasets[vision]

from datasets import load_dataset, Image

# you can also download test split by changing split="test"
dataset = load_dataset("Bingsu/Human_Action_Recognition", split="train")

# edit label id here
myLabel=11

for x in range(12000):
  print("Browsing image: "+str(x) )

  if dataset[x]["labels"]==myLabel:
    print("Downloading...")
    im1=dataset[x]["image"]
    im1.save(str(x)+".jpg")
