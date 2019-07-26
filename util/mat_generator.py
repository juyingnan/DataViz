import os

import numpy as np
from scipy import io as sio
from skimage import io, transform, color
from skimage.util import img_as_ubyte
from pycocotools.coco import COCO


def get_png_compress_ratio(image_shape, image_size):
    (_h, _w) = image_shape[:2]
    channel = 1
    if len(image_shape) > 2:
        channel = image_shape[2]
    color_byte = 1
    uncompressed_size = _h * _w * channel * color_byte
    return 1.0 * image_size / uncompressed_size


def read_img(path, meta_info, as_gray=False, resize=None):
    imgs = list()
    dims = list()
    names = list()
    ids = list()
    ratios = list()
    count = 0
    print('reading the images:%s' % path)
    for info in meta_info:
        file_name = info['file_name']
        file_path = os.path.join(path, file_name)
        file_size = os.stat(file_path).st_size
        img = io.imread(file_path, as_gray=as_gray)
        # print(img.shape)
        if len(img.shape) == 2:
            img = color.gray2rgb(img)
        ratio = get_png_compress_ratio(img.shape, file_size)
        if resize is not None:
            img = img_as_ubyte(transform.resize(img, resize, anti_aliasing=False))
        imgs.append(img)
        dims.append((info['height'], info['width']))
        ids.append(info['id'])
        names.append(file_name)
        ratios.append(ratio)
        if count % 7 == 0:
            print("\rreading {0}/{1}".format(count, len(meta_info)), end='')
        count += 1
    print('\r', end='')

    return np.asarray(imgs, np.uint8), np.array(names), np.array(ids), np.array(dims), np.array(ratios)


if __name__ == '__main__':

    np.seterr(all='ignore')

    dataDir = '../COCO'
    dataType = 'val2017'
    annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
    coco = COCO(annFile)

    image_root_path = r'C:\Users\bunny\Desktop\val2017/'
    mat_output_dir = r'C:\Users\bunny\Desktop\val_output'

    cats = coco.loadCats(coco.getCatIds())
    nms = set([cat['supercategory'] for cat in cats])
    print('COCO supercategories: \n{}'.format(' '.join(nms)))

    nms = [cat['name'] for cat in cats]
    print('COCO categories: \n{}\n'.format(' '.join(nms)))

    for cat in cats:
        cat_id = cat['id']
        cat_name = cat['name']
        supercategory = cat['supercategory']
        imgIds = coco.getImgIds(catIds=cat_id)
        imgs_info = list(coco.loadImgs(imgIds))
        for edge in [10, 20, 50]:
            w = h = edge
            images, file_names, image_ids, dimensions, compress_ratios = read_img(image_root_path, imgs_info,
                                                                                  as_gray=False, resize=(h, w))
            print('mat size: ', images.shape)
            sio.savemat(os.path.join(mat_output_dir, '{:02d}_{}_{}.mat'.format(cat_id, cat_name, w)),
                        mdict={'images': images,
                               'file_names': file_names,
                               'ids': image_ids,
                               'dimensions': dimensions,
                               'ratios': compress_ratios})
