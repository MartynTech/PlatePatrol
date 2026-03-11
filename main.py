import argparse
from detector import detect_plates

from detector import detect_plates


def main():
    parser = argparse.ArgumentParser(description='Run PlatePatrol detection and write CSV output.')
    parser.add_argument('--video', required=True, help='Input video path.')
    parser.add_argument('--vehicle-model', default='yolov8n.pt', help='YOLO model path for vehicles.')
    parser.add_argument('--plate-model', default='license_plate_detector.pt', help='YOLO model path for plates.')
    parser.add_argument('--output-csv', default='test.csv', help='Output CSV path.')
    args = parser.parse_args()

    detect_plates(
        video_path=args.video,
        vehicle_model_path=args.vehicle_model,
        plate_model_path=args.plate_model,
        output_csv_path=args.output_csv,
    )


if __name__ == '__main__':
    main()
if __name__ == "__main__":
    detect_plates(
        video_path="C:/Users/21626/Videos/sample.mp4",
        vehicle_model_path="yolov8n.pt",
        plate_model_path="license_plate_detector.pt",
        output_csv_path="./test.csv",
    )
