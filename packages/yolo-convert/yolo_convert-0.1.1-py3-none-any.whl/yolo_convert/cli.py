import argparse
from pathlib import Path
from .yolov5 import export_onnx as yolo_export

def main():
    parser = argparse.ArgumentParser(prog="yolo_convert", description="YOLOv5 model converter")
    parser.add_argument("-i", "--input", type=str, default='./yolov5s.pt', help='weights path')
    parser.add_argument("--hisi3559", action="store_true", help="Export to 3-heads ONNX outputs for HiSilicon 3559")
    parser.add_argument("--imgsz", "--img", "--img-size", nargs="+", type=int, default=[640, 640], help="image (h, w)")
    parser.add_argument("--opset", type=int, default=11, help="ONNX opset version")
    args = parser.parse_args()

    # weights_path = str(Path(args.input).resolve())

    # 调用 run() 时直接传 Python 参数
    yolo_export.run(weights=args.input,
                    imgsz=args.imgsz,
                    hisi3559=args.hisi3559,
                    opset=args.opset
                    )
