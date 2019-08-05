import os
from scipy import io as sio
import numpy as np
from bokeh.plotting import figure, show, output_file, reset_output
from bokeh.layouts import column

import math


def find_sqrt_root_roof(number):
    sqrt_root = math.floor(math.sqrt(number))
    while sqrt_root ** 2 < number:
        sqrt_root += 1
    return sqrt_root


def output_image_wall(imgs, output_path, title, ids, info, info_name):
    dim = find_sqrt_root_roof(len(imgs))
    img_dimension = imgs[0].shape[0]
    p = figure(title=title, width=dim * img_dimension, height=dim * img_dimension,
               tooltips=[('x,y', '@xs, @ys'), ('id', '@ids'), (info_name, '@info')])
    p.x_range.range_padding = p.y_range.range_padding = 0

    rgba_images = list()
    xs = list()
    ys = list()

    for i in range(len(imgs)):
        img = imgs[i]
        rgba = np.dstack((img, 255 - np.zeros(img.shape[:-1], dtype=np.uint8)))
        rgba_images.append(rgba)
        xs.append(i % dim)
        ys.append(i // dim)

    data = dict(
        images=rgba_images,
        xs=xs,
        ys=ys,
        ids=ids,
        info=info,
    )

    p.image_rgba('images', source=data, x='xs', y='ys', dw=1, dh=1)

    additional_p = figure(title="Corresponding jpeg compress ratio",
                          width=dim * img_dimension, height=dim * img_dimension,
                          tooltips=[('x,y', '@xs, @ys'), ('id', '@ids'), (info_name, '@info')])
    additional_p.x_range.range_padding = additional_p.y_range.range_padding = 0
    additional_p.rect(source=data, x='xs', y='ys', width=1, height=1, color='black', hover_line_color='black',
                      line_color=None, alpha='info')

    output_file(output_path, title=title)
    output_column = column([p,
                            additional_p])
    show(output_column)
    reset_output()


if __name__ == '__main__':
    root_path = r'C:\Users\bunny\Desktop\val_output'
    img_size = 20
    category = "01_person"
    file_name = '{}_{}.mat'.format(category, img_size)
    mat_path = os.path.join(root_path, file_name)
    digits = sio.loadmat(mat_path)
    images = digits.get('images')
    image_ids = digits.get('ids')[0]
    compress_ratios = digits.get('ratios')[0]
    n_samples, height, width, channel = images.shape
    print("{} samples, Height: {}, Width: {}, Channel: {}".format(n_samples, height, width, channel))

    id_sorted_images = [x for _, x in sorted(zip(image_ids, images))]
    output_image_wall(id_sorted_images,
                      output_path="output/thumbnail_{}_{}.html".format(category, img_size),
                      title="Thumbnail sorted by id",
                      ids=sorted(image_ids),
                      info=compress_ratios,
                      info_name='compress ratio')

    ratio_sorted_images = [x for _, x in sorted(zip(compress_ratios, images))]
    test = compress_ratios.tolist()
    output_image_wall(ratio_sorted_images,
                      output_path="output/thumbnail_{}_{}_jpeg_ratio.html".format(category, img_size),
                      ids=image_ids,
                      title="thumbnail sorted jpeg compress ratio",
                      info=sorted(compress_ratios),
                      info_name='compress ratio')
