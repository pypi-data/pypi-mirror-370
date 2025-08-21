import argparse
import sys
import time

import torch
import torch.nn as nn
from pathlib import Path
# 添加yolov5目录到Python路径
yolov5_dir = Path(__file__).parent
sys.path.insert(0, str(yolov5_dir))

from models.experimental import attempt_load
from utils.general import set_logging, check_img_size
from utils.torch_utils import select_device



def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='./yolov5s.pt', help='weights path')
    parser.add_argument('--img-size', nargs='+', type=int, default=[640, 640], help='image size')  # height, width
    parser.add_argument('--batch-size', type=int, default=1, help='batch size')
    parser.add_argument('--max-obj', type=int, default=100, help='topk')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='nms iou threshold')
    parser.add_argument('--score-thres', type=float, default=0.25, help='nms score threshold')
    parser.add_argument('--dynamic', action='store_true', help='dynamic ONNX axes')
    parser.add_argument('--device', default='cpu', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    opt = parser.parse_args()

    return opt


def run(weights="yolov5s.pt", imgsz=(640, 640), device="cpu", hisi3559=False, opset=11):
    """运行ONNX转换"""

    import global_config
    global_config.HISI3559 = hisi3559
    
    set_logging()
    t = time.time()

    # Load PyTorch model
    device = select_device(device)
    model = attempt_load(weights, device=device) # load FP32 model

    # Checks
    gs = int(max(model.stride))  # grid size (max stride)
    img_size = [check_img_size(x, gs) for x in imgsz]  # verify img_size are gs-multiples
    
    # Input
    batch_size = 1
    img = torch.zeros(batch_size, 3, *img_size).to(device)  # image size(1,3,320,192) iDetection
    model.eval()

    y = model(img)  # dry run

    model.model[-1].export = True

    # ONNX export
    try:
        import onnx
        print('\nStarting ONNX export with onnx %s, opset=%d 🚀' % (onnx.__version__, opset))
        f = weights.replace('.pt', '.onnx')  # filename
        torch.onnx.export(model,
                            img, 
                            f, 
                            opset_version=opset, 
                            input_names=['images'],
                            dynamic_axes= None,
                            )

        # Checks
        onnx_model = onnx.load(f)  # load onnx model

        
        print("Simplifying ONNX model...")
        from onnxsim import simplify
        model_simp, check = simplify(onnx_model)
        if check:
            onnx.save(model_simp, str(f))
            print("ONNX model simplified successfully.")
        else:
            print("ONNX simplify check failed, using original model.")


        print('ONNX export success, saved as %s' % f)
    except Exception as e:
        print('ONNX export failure: %s' % e)

if __name__ == "__main__":
    opt = parse_opt()
    run(opt.weights, opt.img_size, opt.device)
