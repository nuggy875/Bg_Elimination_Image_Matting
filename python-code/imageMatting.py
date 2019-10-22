import math
import os
import random
import argparse

import cv2 as cv
import numpy as np
import torch
from torchvision import transforms

from config import device, fg_path_test, a_path_test, bg_path_test
from data_gen import data_transforms, gen_trimap
from utils import compute_mse, compute_sad, ensure_folder, draw_str


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default="imageF")
    parser.add_argument('--bg', type=str, default="trans2000")
    return parser.parse_args()


def composite4(fg, bg, a, w, h):
    print(fg.shape, bg.shape, a.shape, w, h)
    fg = np.array(fg, np.float32)
    bg_h, bg_w = bg.shape[:2]
    x = 0
    if bg_w > w:
        x = np.random.randint(0, bg_w - w)
    y = 0
    if bg_h > h:
        y = np.random.randint(0, bg_h - h)
    bg = np.array(bg[y:y + h, x:x + w], np.float32)
    alpha = np.zeros((h, w, 1), np.float32)
    alpha[:, :, 0] = a
    im = alpha * fg + (1 - alpha) * bg
    im = im.astype(np.uint8)
    return im, bg


def composite4_test(fg, bg, a, w, h):
    print(':: Image w, h :: ', w, h)

    fg = np.array(fg, np.float32)
    bg_h, bg_w = bg.shape[:2]
    print(':: Background w, h ::', bg_w, bg_h)
    x = max(0, int((bg_w - w) / 2))
    y = max(0, int((bg_h - h) / 2))

    crop = np.array(bg[y:y + h, x:x + w], np.float32)
    alpha = np.zeros((h, w, 1), np.float32)
    alpha[:, :, 0] = a / 255.
    im = alpha * fg + (1 - alpha) * crop
    im = im.astype(np.uint8)

    new_a = np.zeros((h, w), np.uint8)
    new_a[0:h, 0:w] = a
    return im, new_a, fg, bg


def image_process(im_path, a_path, bg_path):
    im = cv.imread(os.path.join('input', im_path))
    a = cv.imread(os.path.join('input', a_path), 0)
    h, w = im.shape[:2]
    bg = cv.imread(os.path.join('input', bg_path))
    bh, bw = bg.shape[:2]
    wratio = w / bw
    hratio = h / bh
    ratio = wratio if wratio > hratio else hratio
    if ratio > 1:
        bg = cv.resize(src=bg, dsize=(math.ceil(bw * ratio), math.ceil(bh * ratio)), interpolation=cv.INTER_CUBIC)

    return composite4_test(im, bg, a, w, h)


if __name__ == '__main__':
    opts = parser()
    im_name = opts.input + '.png'
    a_name = opts.input + '_a.png'
    bg_name = opts.bg + '.png'
    img_original = cv.imread(os.path.join('input', im_name))

    checkpoint = 'checkpoint.tar'
    checkpoint = torch.load(checkpoint)
    model = checkpoint['model'].module
    model = model.to(device)
    model.eval()

    # transformer = data_transforms['valid']
    transformer = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    ensure_folder('images')

    # bg_test = 'data/bg_test/'
    # new_bgs = [f for f in os.listdir(bg_test) if os.path.isfile(os.path.join(bg_test, f)) and f.endswith('.jpg')]
    # new_bgs = random.sample(new_bgs, 10)

    # fcount = int(name.split('.')[0].split('_')[0])
    # bcount = int(name.split('.')[0].split('_')[1])
    # im_name = fg_test_files[fcount]
    # bg_name = bg_test_files[bcount]
    print('==> ', im_name, bg_name)
    im, alpha, fg, bg = image_process(im_name, a_name, bg_name)

    cv.imwrite('results/{}_0_img_original.png'.format(opts.input), img_original)
    cv.imwrite('results/{}_1_img_crop.png'.format(opts.input), im)
    # 알파 이미지
    cv.imwrite('results/{}_3_alpha.png'.format(opts.input), alpha)

    print('\nStart processing image: {}'.format(opts.input))
    print('\nBackground: {}'.format(opts.bg))

    h, w = im.shape[:2]

    trimap = gen_trimap(alpha)
    cv.imwrite('results/{}_4_trimap.png'.format(opts.input), trimap)

    x = torch.zeros((1, 4, h, w), dtype=torch.float)
    image = im[..., ::-1]  # RGB
    image = transforms.ToPILImage()(image)
    image = transformer(image)
    x[0:, 0:3, :, :] = image
    x[0:, 3, :, :] = torch.from_numpy(trimap.copy() / 255.)

    # Move to GPU, if available
    x = x.type(torch.FloatTensor).to(device)
    alpha = alpha / 255.

    with torch.no_grad():
        pred = model(x)

    pred = pred.cpu().numpy()
    pred = pred.reshape((h, w))

    pred[trimap == 0] = 0.0
    pred[trimap == 255] = 1.0

    # Calculate loss
    # loss = criterion(alpha_out, alpha_label)
    mse_loss = compute_mse(pred, alpha, trimap)
    sad_loss = compute_sad(pred, alpha)
    str_msg = 'sad: %.4f, mse: %.4f' % (sad_loss, mse_loss)
    print(str_msg)

    out = (pred.copy() * 255).astype(np.uint8)
    draw_str(out, (10, 20), str_msg)
    cv.imwrite('results/{}_5_out.png'.format(opts.input), out)

    # new_bg = new_bgs[i]
    # new_bg = cv.imread(os.path.join(bg_test, new_bg))
    new_bg = cv.imread(os.path.join('input', bg_name))
    bh, bw = new_bg.shape[:2]
    wratio = w / bw
    hratio = h / bh
    ratio = wratio if wratio > hratio else hratio
    print('ratio: ' + str(ratio))
    if ratio > 1:
        new_bg = cv.resize(src=new_bg, dsize=(math.ceil(bw * ratio), math.ceil(bh * ratio)),
                           interpolation=cv.INTER_CUBIC)

    im, bg = composite4(im, new_bg, pred, w, h)
    cv.imwrite('results/{}_7_compose.png'.format(opts.input), im)


