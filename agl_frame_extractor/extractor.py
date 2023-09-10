import cv2
import os
import json
from tqdm import tqdm
import logging
from concurrent.futures import ThreadPoolExecutor

class VideoFrameExtractor:
    def __init__(self, input_folder, output_folder, use_multithreading=False, image_format='jpg'):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.use_multithreading = use_multithreading
        self.image_format = image_format
        logging.basicConfig(filename='video_frame_extraction.log', level=logging.INFO)

    def process_video(self, mov_file):
        video_path = os.path.join(self.input_folder, mov_file)
        cap = cv2.VideoCapture(video_path)

        frames_folder = os.path.join(self.output_folder, f"{mov_file}_frames")
        if not os.path.exists(frames_folder):
            os.makedirs(frames_folder)

        metadata = {
            'video_file': mov_file,
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': int(cap.get(cv2.CAP_PROP_FPS)),
            'duration': int(cap.get(cv2.CAP_PROP_POS_MSEC))
        }

        frame_number = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_file = os.path.join(frames_folder, f"frame_{frame_number}.{self.image_format}")
            cv2.imwrite(frame_file, frame)
            frame_number += 1

        metadata_file = os.path.join(self.output_folder, f"{mov_file}_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)

        cap.release()
        logging.info(f"Extracted frames and metadata from {mov_file}")

    def extract_frames_and_metadata(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            logging.info(f"Created output folder {self.output_folder}")

        mov_files = [f for f in os.listdir(self.input_folder) if f.endswith('.MOV')]
        logging.info(f"Found {len(mov_files)} .MOV files.")

        if self.use_multithreading:
            with ThreadPoolExecutor() as executor:
                list(tqdm(executor.map(self.process_video, mov_files), total=len(mov_files)))
        else:
            for mov_file in tqdm(mov_files, desc="Processing .MOV files"):
                self.process_video(mov_file)
