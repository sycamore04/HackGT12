from image_processor import *
from text_processor import *
from random import random

def handle_error(file_path, error):
    fh = open("errors.txt", "a")
    fh.write("FILE: " + file_path + "\n\n" + str(error) + "\n\n------------------------------------------\n\n")
    fh.close()
    print(str(error))

def generate_ics_list(file_paths):

    returned_files = []

    for f in file_paths:
        try:
            text, link = retrieve_text(f)
            response = text_to_json(text)
            returned_files.append(create_ics(response, int(10000 * random()), link))
        except Exception as error:
            handle_error(f, error)

    return returned_files

# names = ["IMG_0680.jpg", "IMG_0681.jpg", "IMG_0708.jpg", "IMG_0733.jpg", "IMG_0742.jpg", "IMG_0989.jpeg", "IMG_0990.jpeg", "IMG_0991.jpeg", "IMG_0992.jpeg", "IMG_0995.jpg", "IMG_special.png", "IMG_tried.png", "IMG_whatever.png", "IMG_zoomed.png"]
#generate_ics_list(names)
