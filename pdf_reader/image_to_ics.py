from image_processor import *
from text_processor import *
from random import random
import os

def handle_error(file_path, error):
    fh = open("errors.txt", "a")
    fh.write("FILE: " + file_path + "\n\n" + str(error) + "\n\n------------------------------------------\n\n")
    fh.close()

def generate_ics_list(file_paths):

    returned_files = []

    for f in file_paths:
        try:
            text, link = retreive_text(f)
            response = text_to_json(text)
            returned_files.append(create_ics(response, int(10000 * random()), link))
        except Exception as error:
            handle_error(f, error)

    return returned_files

file_paths = ["/Users/sam/Desktop/IMG_0680.jpg"]
for f in file_paths:
    if not os.path.exists(f):
        print("File not found: ", f)
    else:
        print("File found: ", f)
returned_files = generate_ics_list(file_paths)
print("Generated ICS files: ", returned_files)  

# names = ["IMG_0680.jpg", "IMG_0681.jpg", "IMG_0708.jpg", "IMG_0733.jpg", "IMG_0742.jpg", "IMG_0989.jpeg", "IMG_0990.jpeg", "IMG_0991.jpeg", "IMG_0992.jpeg", "IMG_0995.jpg"]
# generate_ics_list(names)