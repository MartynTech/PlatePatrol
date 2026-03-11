import argparse


def run_full_pipeline(video, vehicle_model, plate_model, raw_csv, interpolated_csv, output_video):
    from detector import detect_plates
    from add_missing_data import interpolate_csv
    from visualize import create_visualization

    detect_plates(
        video_path=video,
        vehicle_model_path=vehicle_model,
        plate_model_path=plate_model,
        output_csv_path=raw_csv,
    )
    interpolate_csv(raw_csv, interpolated_csv)
    create_visualization(interpolated_csv, video, output_video)


def main():
    parser = argparse.ArgumentParser(
        description='One-stop PlatePatrol runner for detection, interpolation, and visualization.'
    )
    parser.add_argument(
        '--mode',
        choices=['full', 'detect', 'interpolate', 'visualize'],
        default='full',
        help='What to run. full runs all stages in sequence.',
    )
    parser.add_argument('--video', help='Input video path (required for detect/full/visualize).')
    parser.add_argument('--vehicle-model', default='yolov8n.pt')
    parser.add_argument('--plate-model', default='license_plate_detector.pt')
    parser.add_argument('--raw-csv', default='test.csv')
    parser.add_argument('--interpolated-csv', default='test_interpolated.csv')
    parser.add_argument('--output-video', default='out.mp4')
    args = parser.parse_args()

    if args.mode in {'full', 'detect', 'visualize'} and not args.video:
        parser.error('--video is required for selected mode.')

    if args.mode == 'full':
        run_full_pipeline(
            video=args.video,
            vehicle_model=args.vehicle_model,
            plate_model=args.plate_model,
            raw_csv=args.raw_csv,
            interpolated_csv=args.interpolated_csv,
            output_video=args.output_video,
        )
    elif args.mode == 'detect':
        from detector import detect_plates

        detect_plates(
            video_path=args.video,
            vehicle_model_path=args.vehicle_model,
            plate_model_path=args.plate_model,
            output_csv_path=args.raw_csv,
        )
    elif args.mode == 'interpolate':
        from add_missing_data import interpolate_csv

        interpolate_csv(args.raw_csv, args.interpolated_csv)
    elif args.mode == 'visualize':
        from visualize import create_visualization

        create_visualization(args.interpolated_csv, args.video, args.output_video)


if __name__ == '__main__':
    main()
