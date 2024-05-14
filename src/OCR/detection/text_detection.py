import os
import sys
import time
import argparse
import numpy as np

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

from src.OCR.ppocr.utils.logging import get_logger
from src.OCR.ppocr.data import create_operators, transform
from src.OCR.ppocr.postprocess import build_post_process
from src.OCR.tools.infer.utility import create_predictor, get_infer_gpuid

logger = get_logger()

class TextDetection(object):

    def str2bool(self, v):
        """
        Convert string to bool
        Input: v (string)
        Output: re (bool)
        """
        re = v.lower() in ("true", "t", "1")
        return re
    
    def init_args(self):
        """
        Init the arguments
        Input: None
        Output: parser (argparse.ArgumentParser)
        """
        parser = argparse.ArgumentParser()
        # params for prediction engine
        parser.add_argument("--use_gpu", type=self.str2bool, default=False)
        parser.add_argument("--use_xpu", type=self.str2bool, default=False)
        parser.add_argument("--use_npu", type=self.str2bool, default=False)
        parser.add_argument("--ir_optim", type=self.str2bool, default=True) #The prediction process can be accelerated
        parser.add_argument("--use_tensorrt", type=self.str2bool, default=False) #TensorRT can significantly improve the inference performance of deep learning models on NVIDIA GPUs,
        parser.add_argument("--min_subgraph_size", type=int, default=15)
        parser.add_argument("--precision", type=str, default="fp32")
        parser.add_argument("--gpu_mem", type=int, default=500)
        parser.add_argument("--gpu_id", type=int, default=0)

        # params for text detector
        parser.add_argument("--image_dir", type=str)
        parser.add_argument("--det_algorithm", type=str, default='DB')
        parser.add_argument("--det_model_dir", type=str, default='model/PaddleModel/text_detection')
        parser.add_argument("--det_limit_side_len", type=float, default=960)
        parser.add_argument("--det_limit_type", type=str, default='max')
        parser.add_argument("--det_box_type", type=str, default='quad')

        # DB parmas
        parser.add_argument("--det_db_thresh", type=float, default=0.4)
        parser.add_argument("--det_db_box_thresh", type=float, default=0.5) #confidence threshold
        parser.add_argument("--det_db_unclip_ratio", type=float, default=1.5)
        parser.add_argument("--max_batch_size", type=int, default=10)
        parser.add_argument("--use_dilation", type=self.str2bool, default=False)
        parser.add_argument("--det_db_score_mode", type=str, default="fast")

        parser.add_argument("--enable_mkldnn", type=self.str2bool, default=True)
        parser.add_argument("--cpu_threads", type=int, default=10)
        parser.add_argument("--use_pdserving", type=self.str2bool, default=True)
        parser.add_argument("--warmup", type=self.str2bool, default=False)


        # EAST parmas
        parser.add_argument("--det_east_score_thresh", type=float, default=0.8)
        parser.add_argument("--det_east_cover_thresh", type=float, default=0.1)
        parser.add_argument("--det_east_nms_thresh", type=float, default=0.2)

        # SAST parmas
        parser.add_argument("--det_sast_score_thresh", type=float, default=0.5)
        parser.add_argument("--det_sast_nms_thresh", type=float, default=0.2)

        # PSE parmas
        parser.add_argument("--det_pse_thresh", type=float, default=0)
        parser.add_argument("--det_pse_box_thresh", type=float, default=0.85)
        parser.add_argument("--det_pse_min_area", type=float, default=16)
        parser.add_argument("--det_pse_scale", type=int, default=1)

        # FCE parmas
        parser.add_argument("--scales", type=list, default=[8, 16, 32])
        parser.add_argument("--alpha", type=float, default=1.0)
        parser.add_argument("--beta", type=float, default=1.0)
        parser.add_argument("--fourier_degree", type=int, default=5)

        
        parser.add_argument(
            "--draw_img_save_dir", type=str, default="./inference_results")
    
        # multi-process
        parser.add_argument("--use_mp", type=self.str2bool, default=False)
        parser.add_argument("--total_process_num", type=int, default=1)
        parser.add_argument("--process_id", type=int, default=0)


        parser.add_argument("--save_log_path", type=str, default="./log_output/")
        parser.add_argument("--use_onnx", type=self.str2bool, default=False)
        parser.add_argument("--benchmark", type=self.str2bool, default=True)

        parser.add_argument("--show_log", type=self.str2bool, default=True)
        return parser

    def parse_args(self):
        """
        Parse the arguments
        Input: None
        Output: parser.parse_args() (argparse.Namespace) 
        """
        parser = self.init_args()
        return parser.parse_args(args=[])
    

    def __init__(self, args):
        """
        This method initializes the class.
        Input:
            args: the arguments
        Output: None
        """
        init_args = vars(args)
        self.args = self.parse_args()
        for key in init_args:
            setattr(self.args, key, init_args[key])
        args = self.args
        self.det_algorithm = args.det_algorithm
        self.use_onnx = args.use_onnx
        pre_process_list = [{
            'DetResizeForTest': {
                'limit_side_len': args.det_limit_side_len,
                'limit_type': args.det_limit_type,
            }
        }, {
            'NormalizeImage': {
                'std': [0.229, 0.224, 0.225],
                'mean': [0.485, 0.456, 0.406],
                'scale': '1./255.',
                'order': 'hwc'
            }
        }, {
            'ToCHWImage': None #Chanel-Height-Width
        }, {
            'KeepKeys': {
                'keep_keys': ['image', 'shape']
            }
        }]

        postprocess_params = {}
        if self.det_algorithm == "DB":
            postprocess_params['name'] = 'DBPostProcess'
            postprocess_params["thresh"] = args.det_db_thresh 
            postprocess_params["box_thresh"] = args.det_db_box_thresh #confidence
            postprocess_params["max_candidates"] = 1000
            postprocess_params["unclip_ratio"] = args.det_db_unclip_ratio
            postprocess_params["use_dilation"] = args.use_dilation
            postprocess_params["score_mode"] = args.det_db_score_mode
            postprocess_params["box_type"] = args.det_box_type
        elif self.det_algorithm == "DB++":
            postprocess_params['name'] = 'DBPostProcess'
            postprocess_params["thresh"] = args.det_db_thresh
            postprocess_params["box_thresh"] = args.det_db_box_thresh
            postprocess_params["max_candidates"] = 1000
            postprocess_params["unclip_ratio"] = args.det_db_unclip_ratio
            postprocess_params["use_dilation"] = args.use_dilation
            postprocess_params["score_mode"] = args.det_db_score_mode
            postprocess_params["box_type"] = args.det_box_type
            pre_process_list[1] = {
                'NormalizeImage': {
                    'std': [1.0, 1.0, 1.0],
                    'mean':
                    [0.48109378172549, 0.45752457890196, 0.40787054090196],
                    'scale': '1./255.',
                    'order': 'hwc'
                }
            }
        elif self.det_algorithm == "EAST":
            postprocess_params['name'] = 'EASTPostProcess'
            postprocess_params["score_thresh"] = args.det_east_score_thresh
            postprocess_params["cover_thresh"] = args.det_east_cover_thresh
            postprocess_params["nms_thresh"] = args.det_east_nms_thresh
        elif self.det_algorithm == "SAST":
            pre_process_list[0] = {
                'DetResizeForTest': {
                    'resize_long': args.det_limit_side_len
                }
            }
            postprocess_params['name'] = 'SASTPostProcess'
            postprocess_params["score_thresh"] = args.det_sast_score_thresh
            postprocess_params["nms_thresh"] = args.det_sast_nms_thresh

            if args.det_box_type == 'poly':
                postprocess_params["sample_pts_num"] = 6
                postprocess_params["expand_scale"] = 1.2
                postprocess_params["shrink_ratio_of_width"] = 0.2
            else:
                postprocess_params["sample_pts_num"] = 2
                postprocess_params["expand_scale"] = 1.0
                postprocess_params["shrink_ratio_of_width"] = 0.3

        elif self.det_algorithm == "PSE":
            postprocess_params['name'] = 'PSEPostProcess'
            postprocess_params["thresh"] = args.det_pse_thresh
            postprocess_params["box_thresh"] = args.det_pse_box_thresh
            postprocess_params["min_area"] = args.det_pse_min_area
            postprocess_params["box_type"] = args.det_box_type
            postprocess_params["scale"] = args.det_pse_scale
        elif self.det_algorithm == "FCE":
            pre_process_list[0] = {
                'DetResizeForTest': {
                    'rescale_img': [1080, 736]
                }
            }
            postprocess_params['name'] = 'FCEPostProcess'
            postprocess_params["scales"] = args.scales
            postprocess_params["alpha"] = args.alpha
            postprocess_params["beta"] = args.beta
            postprocess_params["fourier_degree"] = args.fourier_degree
            postprocess_params["box_type"] = args.det_box_type
        elif self.det_algorithm == "CT":
            pre_process_list[0] = {'ScaleAlignedShort': {'short_size': 640}}
            postprocess_params['name'] = 'CTPostProcess'
        else:
            logger.info("unknown det_algorithm:{}".format(self.det_algorithm))
            sys.exit(0)

        self.preprocess_op = create_operators(pre_process_list)
        self.postprocess_op = build_post_process(postprocess_params)
        self.predictor, self.input_tensor, self.output_tensors, self.config = create_predictor(args, 'det',logger)
    
        if self.use_onnx:
            img_h, img_w = self.input_tensor.shape[2:]
            if img_h is not None and img_w is not None and img_h > 0 and img_w > 0:
                pre_process_list[0] = {
                    'DetResizeForTest': {
                        'image_shape': [img_h, img_w]
                    }
                }

        self.preprocess_op = create_operators(pre_process_list)
        

        if args.benchmark:
            import auto_log
            pid = os.getpid()
            gpu_id = get_infer_gpuid()
            self.autolog = auto_log.AutoLogger(
                model_name="det",
                model_precision=args.precision,
                batch_size=1,
                data_shape="dynamic",
                save_path=None,
                inference_config=self.config,
                pids=pid,
                process_name=None,
                gpu_ids=gpu_id if args.use_gpu else None,
                time_keys=[
                    'preprocess_time', 'inference_time', 'postprocess_time'
                ],
                warmup=2,
                logger=logger)
    

    def order_points_clockwise(self, pts):
        """Order points in clockwise order.
        Input: an array of shape [4, 2]
        Output: an array of shape [4, 2] where the points are ordered"""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        tmp = np.delete(pts, (np.argmin(s), np.argmax(s)), axis=0)
        diff = np.diff(np.array(tmp), axis=1)
        rect[1] = tmp[np.argmin(diff)]
        rect[3] = tmp[np.argmax(diff)]
        return rect

    def clip_det_res(self, points, img_height, img_width):
        """
        Clip the coordinates of a set of point within the image size
        Input: points: an array of shape [4, 2],
                img_height: the height of the image
                img_width: the width of the image
        Output: an array of shape [4, 2] where the points are clipped
        """
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def filter_tag_det_res(self, dt_boxes, image_shape):
        """
        Filter a set of detected boxes based on their size and position within the input image.
        Order points in clockwise order and clip the coordinates of a set of point within the image size
        Input: dt_boxes: an array of shape [N, 4, 2]
                image_shape: the shape of the input image [height, width, channel]
        Output: an array of shape [M, 4, 2] where M <= N 
                
        """
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            if type(box) is list:
                box = np.array(box)
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)
            rect_width = int(np.linalg.norm(box[0] - box[1]))
            rect_height = int(np.linalg.norm(box[0] - box[3]))
            if rect_width <= 3 or rect_height <= 3:
                continue
            dt_boxes_new.append(box)
        dt_boxes = np.array(dt_boxes_new)
        return dt_boxes

    def filter_tag_det_res_only_clip(self, dt_boxes, image_shape):
        """
        Filter a set of detected boxes based on their size and position within the input image.
        Clip the coordinates of a set of point within the image size
        Input: dt_boxes: an array of shape [N, 4, 2]
                image_shape: the shape of the input image [height, width, channel]
        Output: an array of shape [N, 4, 2] 
        """
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            if type(box) is list:
                box = np.array(box)
            box = self.clip_det_res(box, img_height, img_width)
            dt_boxes_new.append(box)
        dt_boxes = np.array(dt_boxes_new)
        return dt_boxes

    def __call__(self, img):
        """
        Get the text detection result of an image
        Input: 
            img: the input image 
        Output:
            dt_boxes: the detection result of text boxes
        """
        ori_im = img.copy()
        data = {'image': img}

        start_time = time.time()
        data = transform(data, self.preprocess_op)
        img, shape_list = data
        if img is None:
            return None, 0
        img = np.expand_dims(img, axis=0)
        shape_list = np.expand_dims(shape_list, axis=0)
        img = img.copy()

        self.input_tensor.copy_from_cpu(img)
        self.predictor.run()
        outputs = []
        for output_tensor in self.output_tensors:
            output = output_tensor.copy_to_cpu()
            outputs.append(output)

        preds = {}
        if self.det_algorithm == "EAST":
            preds['f_geo'] = outputs[0]
            preds['f_score'] = outputs[1]
        elif self.det_algorithm == 'SAST':
            preds['f_border'] = outputs[0]
            preds['f_score'] = outputs[1]
            preds['f_tco'] = outputs[2]
            preds['f_tvo'] = outputs[3]
        elif self.det_algorithm in ['DB', 'PSE', 'DB++']:
            preds['maps'] = outputs[0]
        elif self.det_algorithm == 'FCE':
            for i, output in enumerate(outputs):
                preds['level_{}'.format(i)] = output
        elif self.det_algorithm == "CT":
            preds['maps'] = outputs[0]
            preds['score'] = outputs[1]
        else:
            raise NotImplementedError

        post_result = self.postprocess_op(preds, shape_list)
        dt_boxes = post_result[0]['points']

        if self.args.det_box_type == 'poly':
            dt_boxes = self.filter_tag_det_res_only_clip(dt_boxes, ori_im.shape)
        else:
            dt_boxes = self.filter_tag_det_res(dt_boxes, ori_im.shape)
        end_time = time.time()
        run_time = end_time - start_time
        return dt_boxes, run_time
    