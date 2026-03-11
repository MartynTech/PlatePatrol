from detector import detect_plates


if __name__ == "__main__":
    detect_plates(
        video_path="C:/Users/21626/Videos/sample.mp4",
        vehicle_model_path="yolov8n.pt",
        plate_model_path="license_plate_detector.pt",
        output_csv_path="./test.csv",
    )
