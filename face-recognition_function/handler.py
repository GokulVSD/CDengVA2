#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"
import os
import boto3
from PIL import Image
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

s3 = boto3.client('s3')

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion

def face_recognition_function(key_path, weights_path):
    # Face extraction
    img = cv2.imread(key_path, cv2.IMREAD_COLOR)
    boxes, _ = mtcnn.detect(img)

    # Face recognition
    key = os.path.splitext(os.path.basename(key_path))[0].split(".")[0]
    output_filename = key + ".txt"
    output_filepath = os.path.join("/tmp", output_filename)
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    face, prob = mtcnn(img, return_prob=True, save_path=None)
    saved_data = torch.load(weights_path)  # loading data.pt file
    if face != None:
        emb = resnet(face.unsqueeze(0)).detach()  # detech is to make required gradient false
        embedding_list = saved_data[0]  # getting embedding data
        name_list = saved_data[1]  # getting list of names
        dist_list = []  # list of matched distances, minimum distance is used to identify the person
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
        idx_min = dist_list.index(min(dist_list))

        # Save the result name in a file
        with open(output_filepath, 'w+') as f:
            f.write(name_list[idx_min])
    else:
        print(f"No face is detected")
        with open(output_filepath, 'w+') as f:
            f.write("Unknown")
    return output_filepath, output_filename


def handler(event, context):
    bucket = event["responsePayload"]["body"]["bucket_name"]
    input_filename = event["responsePayload"]["body"]["image_file_name"]

    downloaded_weights_file = os.path.join("/tmp", "data.pt")
    if not os.path.isfile(downloaded_weights_file):
        s3.download_file(
            Filename=downloaded_weights_file,
            Bucket="1229503862-lambda-utils",
            Key="data.pt"
        )

    downloaded_file = os.path.join("/tmp", input_filename)
    s3.download_file(
        Filename=downloaded_file,
        Bucket=bucket,
        Key=input_filename
    )

    output_path, filename = face_recognition_function(downloaded_file, downloaded_weights_file)
    s3.upload_file(output_path, '1229503862-output', filename)