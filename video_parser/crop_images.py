import os
import math
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

img_path = "/home/ekmek/intership_project/video_parser/test/frame294.jpg"
save_crops_folder = "/home/ekmek/intership_project/video_parser/crops_test/"
if not os.path.exists(save_crops_folder):
    os.makedirs(save_crops_folder)

img = Image.open(img_path)
width, height = img.size

bool_generate_plot = True

if bool_generate_plot:
    fig, ax = plt.subplots()

    plt.imshow(img)
    plt.xlim(-1*(width/10.0), width+1*(width/10.0))
    plt.ylim(-1*(height/10.0), height+1*(height/10.0))
    plt.gca().invert_yaxis()

def get_crops_parameters(w, crop=288, over=0.5, scale=1.0):
    crop = scale * crop

    block = crop * (1.0 - over)
    pocet = (w - (crop - block)) / block
    nastejne = (w - (crop - block)) / int(pocet)

    offset = w - (int((int(pocet) - 1) * nastejne) + crop)
    balance = offset / 2.0

    params = []
    for i in range(0, int(pocet)):
        w_from = int(i * nastejne + balance)
        w_to = int(w_from + crop)
        params.append((w_from, w_to))

    #print w - w_to
    return params

# crop*scale is the size inside input image
# crop is the size of output image
crop = 544
over = 0.2
scale = 1.0
w_crops = get_crops_parameters(width, crop, over, scale)
h_crops = get_crops_parameters(height, crop, over, scale)

print "Number of crops:", len(w_crops) * len(h_crops)

i = 0
for w_crop in w_crops:
    for h_crop in h_crops:
        ax.add_patch(
            patches.Rectangle(
                (w_crop[0], h_crop[0]),
                scale*crop,
                scale*crop, fill=False
            )
        )

        area = (w_crop[0], h_crop[0], w_crop[0] + scale*crop, h_crop[0] + scale*crop)
        cropped_img = img.crop(box=area)
        cropped_img = cropped_img.resize((crop,crop),resample=Image.ANTIALIAS)
        cropped_img.load()
        cropped_img.save(save_crops_folder+'_'+str(i)+".jpg")
        i += 1


"""
width = 3840
height = 2160

crop_sizes_possible = [288,352,416,480,544]

"""

plt.show()