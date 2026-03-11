import argparse
import ast

import cv2
import numpy as np
import pandas as pd


def draw_border(img, top_left, bottom_right, color=(0, 255, 0), thickness=10, line_length_x=200, line_length_y=200):
    x1, y1 = top_left
    x2, y2 = bottom_right

    cv2.line(img, (x1, y1), (x1, y1 + line_length_y), color, thickness)
    cv2.line(img, (x1, y1), (x1 + line_length_x, y1), color, thickness)

    cv2.line(img, (x1, y2), (x1, y2 - line_length_y), color, thickness)
    cv2.line(img, (x1, y2), (x1 + line_length_x, y2), color, thickness)

    cv2.line(img, (x2, y1), (x2 - line_length_x, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + line_length_y), color, thickness)

    cv2.line(img, (x2, y2), (x2, y2 - line_length_y), color, thickness)
    cv2.line(img, (x2, y2), (x2 - line_length_x, y2), color, thickness)

    return img


def _parse_bbox(text):
    return ast.literal_eval(text.replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))


def create_visualization(results_csv='test_interpolated.csv', video_path='sample.mp4', output_video='./out.mp4'):
    results = pd.read_csv(results_csv)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f'Unable to open video: {video_path}')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    license_plate = {}
    for car_id in np.unique(results['car_id']):
        max_ = np.amax(results[results['car_id'] == car_id]['license_number_score'])
        plate_number = results[(results['car_id'] == car_id) & (results['license_number_score'] == max_)]['license_number'].iloc[0]
        license_plate[car_id] = {'license_crop': None, 'license_plate_number': plate_number}

        target_frame = results[(results['car_id'] == car_id) & (results['license_number_score'] == max_)]['frame_nmr'].iloc[0]
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        if not ret:
            continue

        x1, y1, x2, y2 = _parse_bbox(
            results[(results['car_id'] == car_id) & (results['license_number_score'] == max_)]['license_plate_bbox'].iloc[0]
        )

        license_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
        if license_crop.size == 0:
            continue

        license_crop = cv2.resize(license_crop, (int((x2 - x1) * 400 / (y2 - y1)), 400))
        license_plate[car_id]['license_crop'] = license_crop

    frame_nmr = -1
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    ret = True
    while ret:
        ret, frame = cap.read()
        frame_nmr += 1
        if not ret:
            break

        df_ = results[results['frame_nmr'] == frame_nmr]
        for row_indx in range(len(df_)):
            car_x1, car_y1, car_x2, car_y2 = _parse_bbox(df_.iloc[row_indx]['car_bbox'])
            draw_border(
                frame,
                (int(car_x1), int(car_y1)),
                (int(car_x2), int(car_y2)),
                (0, 255, 0),
                25,
                line_length_x=200,
                line_length_y=200,
            )

            x1, y1, x2, y2 = _parse_bbox(df_.iloc[row_indx]['license_plate_bbox'])
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 12)

            car_id = df_.iloc[row_indx]['car_id']
            license_crop = license_plate.get(car_id, {}).get('license_crop')
            if license_crop is None:
                continue

            H, W, _ = license_crop.shape
            try:
                frame[int(car_y1) - H - 100:int(car_y1) - 100, int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = license_crop
                frame[int(car_y1) - H - 400:int(car_y1) - H - 100, int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = (255, 255, 255)

                plate_number = license_plate[car_id]['license_plate_number']
                (text_width, text_height), _ = cv2.getTextSize(plate_number, cv2.FONT_HERSHEY_SIMPLEX, 4.3, 17)
                cv2.putText(
                    frame,
                    plate_number,
                    (int((car_x2 + car_x1 - text_width) / 2), int(car_y1 - H - 250 + (text_height / 2))),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    4.3,
                    (0, 0, 0),
                    17,
                )
            except Exception:
                continue

        out.write(frame)

    out.release()
    cap.release()


def main():
    parser = argparse.ArgumentParser(description='Create annotated output video from interpolated CSV.')
    parser.add_argument('--csv', default='test_interpolated.csv', help='Interpolated CSV path.')
    parser.add_argument('--video', required=True, help='Source video path.')
    parser.add_argument('--output', default='out.mp4', help='Output video path.')
    args = parser.parse_args()
    create_visualization(args.csv, args.video, args.output)


if __name__ == '__main__':
    main()
