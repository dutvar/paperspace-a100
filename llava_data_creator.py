
from PIL import Image
from io import BytesIO
import requests
import os
import json
import uuid
import argparse


parser = argparse.ArgumentParser(description='Data processing')
parser.add_argument('--input_path', type=str)
parser.add_argument('--output_path', type=str)
parser.add_argument('--val_samples', type=int, default=100)

args = parser.parse_args()

input_path = args.input_path
if not input_path.endswith("/"):
    input_path = input_path + "/"

output_path = args.output_path
if not output_path.endswith("/"):
    output_path = output_path + "/"

val_samples = args.val_samples

def process_and_save(image_root, label_keys, labels, output_folder, subset_name, question):
    # Define image subfolder within output folder
    subset_folder = os.path.join(output_folder, subset_name)
    image_subfolder = os.path.join(output_folder, 'images')


    if not os.path.exists(image_subfolder):
        os.makedirs(image_subfolder)


    if not os.path.exists(subset_folder):
        os.makedirs(subset_folder)


    # Initialize list to hold all JSON data
    json_data_list = []


    # Process and save images and labels
    for id in label_keys:

        image = Image.open(image_root+f'/{id}.jpg')


        # Create a unique ID for each image
        unique_id = str(uuid.uuid4())


        # Define image path
        image_path = os.path.join(image_subfolder, f"{unique_id}.jpg")


        # Save image
        image.save(image_path)


        # Remove duplicates and format answers
        answers = json.dumps(labels[id])
        unique_answers = list(set(answers))
        formatted_answers = ", ".join(unique_answers)


        # Structure for LLaVA JSON
        json_data = {
            "id": unique_id,
            "image": f"{unique_id}.jpg",
            "conversations": [
                {
                    "from": "human",
                    "value": question
                },
                {
                    "from": "gpt",
                    "value": formatted_answers
                }
            ]
        }


        # Append to list
        json_data_list.append(json_data)


    # Save the JSON data list to a file
    json_output_path = os.path.join(output_folder, subset_name, 'dataset.json')
    with open(json_output_path, 'w') as json_file:
        json.dump(json_data_list, json_file, indent=4)

def main():
    
    labels=json.load(open(input_path+'labels.json'))
    image_root=input_path+'data_img'
    ids=list(labels.keys())
    question='A chat between a curious human and artificial intelligence agent about a digital ad post on social media. Look at the ad and return the text of following components in a json format: brand, caption, main text, legal disclaimer, footer, call to action button.'
    process_and_save(image_root, ids[val_samples:], labels, output_path, 'train', question)
    process_and_save(image_root, ids[:val_samples], labels, output_path, 'val', question)


if __name__ == '__main__':
    main()