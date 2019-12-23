# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import argparse
import glob
import multiprocessing as mp
import os
import time
import cv2
import tqdm
import numpy as np
import torch

from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger

from predictor import VisualizationDemo

# constants
WINDOW_NAME = "COCO detections"


def setup_cfg(args):
    # load config from file and command-line arguments
    cfg = get_cfg()
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    # Set score_threshold for builtin models
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = args.confidence_threshold
    cfg.freeze()
    return cfg

def get_parser():
    parser = argparse.ArgumentParser(description="Detectron2 demo for builtin models")
    parser.add_argument(
        "--config-file",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")),
        metavar="FILE",
        help="path to config file",
    )
    parser.add_argument("--input", 
        nargs="+", 
        help="A list of space separated input images",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../public/input/input.jpg")),
    )
    parser.add_argument(
        "--output",
        help="A file or directory to save output visualizations. "
        "If not given, will show output in an OpenCV window.",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../public/result")),
    )

    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.5,
        help="Minimum score for instance predictions to be shown",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=["MODEL.WEIGHTS",
        "detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl"],
        nargs=argparse.REMAINDER,
    )

    parser.add_argument(
        "--val",
        type=int,
        default=3
    )
    return parser

def get_trimap(instances, val):
    mask = instances.pred_masks
    height, width = instances.image_size
    img_tri = np.zeros((height, width, 3), np.uint8)
    for i in range(0, height):
        for j in range(0, width):
            if mask[0][i][j]:
                img_tri = cv2.line(img_tri, (j ,i), (j, i), (255, 255, 255), 1)
    
    for i in range(0, height):
        for j in range(0, width):
            if mask[0][i][j]:
                count = 0
                if mask[0][i-1][j-1] and mask[0][i-1][j] and mask[0][i-1][j+1] and mask[0][i][j-1] and mask[0][i][j+1] and mask[0][i+1][j-1] and mask[0][i+1][j] and mask[0][i+1][j+1]:
                    pass
                else:
                    img_tri = cv2.rectangle(img_tri, (j-val ,i-val), (j+val, i+val), (128, 128, 128), -1)

    cv2.imwrite(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../public/input/input_a.jpg")), img_tri)
    print('Segmentation Complete')
    


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    args = get_parser().parse_args()
    logger = setup_logger()
    logger.info("Arguments: " + str(args))

    cfg = setup_cfg(args)

    demo = VisualizationDemo(cfg)
    if args.input:
        if len(args.input) == 1:
            args.input = glob.glob(os.path.expanduser(args.input[0]))
            assert args.input, "The input path(s) was not found"
        
        # use PIL, to be consistent with evaluation
        img = read_image(args.input, format="BGR")
        start_time = time.time()
        predictions, visualized_output = demo.run_on_image(img)
        logger.info(
            "{}: detected {} instances in {:.2f}s".format(
                args.input, len(predictions["instances"]), time.time() - start_time
            )
        )
        if args.output:
            if os.path.isdir(args.output):
                assert os.path.isdir(args.output), args.output
                out_filename = os.path.join(args.output, os.path.basename(args.input))
            else:
                assert len(args.input) == 1, "Please specify a directory with args.output"
                out_filename = args.output
            visualized_output.save(out_filename)

        # // get trimap from result
        get_trimap(predictions["instances"].to(torch.device("cpu")), args.val)
        # masks = np.asarray(predictions["instances"].pred_masks)
