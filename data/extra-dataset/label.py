from PIL import Image
from shutil import copyfile
import os

# Config
DATA_PATH = "./images"
FORMATTED_IMAGE_DIR = "./csgo-images-large"
SKIP_NO_BOXES_IMAGE = True
SKIP_SQUARE_IMAGES = False
ANNOTATION_IMAGE_PATH_PREFIX = "/csgo-images-large"
ANNOTATION_FILENAME = "csgo-large.txt"
SWAP_CT_AND_T_LABELS = True
# (w, h) and value must be between 0-1 (1 for 100%). None means no minmum requirement
MIN_BOX_PERCENTAGE = (0.010, None)


# NOTE: there're only 2 lables
#         - 0 : Terrorist (T)
#         - 1 : Counter Terrorist (CT)
#       for annotation, it is between 0 and 1 (basically percentage)
#       - first value indicate the category
#       - the remaining 4 values is center_x, center_y, width, height


class Format:
    def __init__(self, DATA_PATH, IMAGE_EXT = ".jpg", LABEL_EXT = ".txt"):
        self.files = os.listdir(DATA_PATH)
        self.data_path = DATA_PATH
        self.image_ext = IMAGE_EXT
        self.label_ext = LABEL_EXT

        self.images = []
        self.labels = []
        self.images_in_annotation = [] # name of images path used in annotation
        self.annotations = [] # store annotation string

        # load raw data
        self.read_raw_data()

    def read_raw_data(self):
        images, labels, unknowns = [], [], []

        # list file into images and label
        for file in self.files:
            if file.endswith(self.image_ext):
                images.append(file)
            elif file.endswith(self.label_ext):
                labels.append(file)
            else:
                unknowns.append(file)

        # make sure there's no unknown file
        assert len(unknowns) == 0

        # make sure num of images is same as num of labels
        assert len(images) == len(labels)

        self.images = images
        self.labels = labels

    def read_annotation(self, skip_empty = False, skip_320x320 = False, image_path_prefix = None, swap_labels = False, min_box_percentage = (None, None)):
        for image_name in self.images:

            image_path = f"{self.data_path}/{image_name}"
            annot_path = image_path[:-3] + "txt"

            # sometimes i will also skip if the bounding box is too small
            found_valid_annotation = False
            annotation_str = image_name if image_path_prefix is None else f"{image_path_prefix}/{image_name}"

            # read image for dimension
            image = Image.open(image_path)
            w, h = image.size
            min_box_width = None # minimum width each bounding box must have
            min_box_height = None # minimum height each bounding box must have 
            if min_box_percentage[0] is not None:
                min_box_width = w * min_box_percentage[0]
            if min_box_percentage[1] is not None:
                min_box_height = h * min_box_percentage[1]

            if skip_320x320 and (w <= 320 or h <= 320):
                continue

            with open(annot_path, 'r') as annot:
                annotation_data = [each for each in annot.read().split("\n") if each != ""]

                # skip image with no object inside
                if len(annotation_data) == 0 and skip_empty:
                    continue

                # store image path used for annotation
                self.images_in_annotation.append(image_name)
                for each in annotation_data:
                    each = each.split(' ')
                    label = each[0]

                    # swap labels or not
                    if swap_labels:
                        if label == '1':
                            label = '0'
                        elif label == '0':
                            label = '1'

                    # convert positions and dimenstion to float
                    each[1] = float(each[1])
                    each[2] = float(each[2])
                    each[3] = float(each[3])
                    each[4] = float(each[4])

                    center_x = each[1]
                    center_y = each[2]
                    width = each[3]
                    height = each[4]

                    # calculate top-left and bottom-right
                    top_left_x = center_x - width / 2
                    top_left_y = center_y - height / 2
                    bottom_right_x = center_x + width / 2
                    bottom_right_y = center_y + height / 2

                    # convert 0-1 scale to image w-h scale
                    top_left_x = int(top_left_x * w)
                    top_left_y = int(top_left_y * h)
                    bottom_right_x = int(bottom_right_x * w)
                    bottom_right_y = int(bottom_right_y * h)

                    # if width or height of the bounding box is very small; skip
                    # the bounding box
                    # /csgo-images-large/csgo000358.jpg 884,483,936,616,0 1131,463,1149,497,0 1296,495,1306,507,0 1254,495,1264,504,0
                    if min_box_width is not None and (bottom_right_x - top_left_x) < min_box_width:
                        continue
                    if min_box_height is not None and (bottom_right_y - top_left_y) < min_box_height:
                        continue

                    annotation_str += f' {top_left_x},{top_left_y},{bottom_right_x},{bottom_right_y},{label}'
                    found_valid_annotation = True

            if found_valid_annotation is False:
                continue

            self.annotations.append(annotation_str)

    def write_annotations(self, filename):
        with open(filename, 'w') as f:
            for each in self.annotations:
                f.write(f"{each}\n")

    def copy_images_for_annotation(self, directory_path):
        """ Copy images used in annotation into new directory """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        for image_name in self.images_in_annotation:
            copyfile(f"{self.data_path}/{image_name}", f"{directory_path}/{image_name}")


if __name__ == '__main__':
    # Create Annotations
    formatData = Format(DATA_PATH)
    formatData.read_annotation(
        skip_empty         = SKIP_NO_BOXES_IMAGE,
        skip_320x320       = SKIP_SQUARE_IMAGES,
        image_path_prefix  = ANNOTATION_IMAGE_PATH_PREFIX,
        swap_labels        = SWAP_CT_AND_T_LABELS,
        min_box_percentage = MIN_BOX_PERCENTAGE,
    )
    formatData.write_annotations(ANNOTATION_FILENAME)

    # Copy images used in annotation into new directory
    formatData.copy_images_for_annotation(FORMATTED_IMAGE_DIR)

    print(f"Total {len(formatData.images_in_annotation)} images in dataset.")
    print(f"Created new dataset with images in {FORMATTED_IMAGE_DIR} directory.")
