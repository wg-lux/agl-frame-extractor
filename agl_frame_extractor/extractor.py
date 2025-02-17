"""Model for extracting frames from video files and saving them as images."""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import cv2
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_FPS, CAP_PROP_POS_MSEC  # pylint: disable=no-name-in-module
from tqdm import tqdm


# TODO Fix / Implement Multithreading; maybe use commandline opencv?
class VideoFrameExtractor:
    """
    A class used to extract frames from a video file and save them as images.

    Attributes
    ----------
    input_folder : str
        The path to the folder containing the input video files.
    output_folder : str
        The path to the folder where the extracted frames and metadata will be saved.
    use_multithreading : bool, optional
        Whether to use multithreading to extract frames from multiple videos simultaneously. Default is False.
    image_format : str, optional
        The format to use when saving the extracted frames as images. Default is 'jpg'.

    Methods
    -------
    process_video(mov_file)
        Extracts frames from a single video file and saves them as images.
    extract_frames_and_metadata()
        Extracts frames and metadata from all video files in the input folder.
    """

    def __init__(
        self, input_folder, output_folder, use_multithreading=False, image_format="jpg"
    ):
        """
        Parameters
        ----------
        input_folder : str
            The path to the folder containing the input video files.
        output_folder : str
            The path to the folder where the extracted frames and metadata will be saved.
        use_multithreading : bool, optional
            Whether to use multithreading to extract frames from multiple videos simultaneously. Default is False.
        image_format : str, optional
            The format to use when saving the extracted frames as images. Default is 'jpg'.
        """
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.use_multithreading = use_multithreading
        self.image_format = image_format
        logging.basicConfig(filename="video_frame_extraction.log", level=logging.INFO)

    def extract_frames_and_metadata(self):
        """
        Extracts frames and metadata from all video files in the input folder.
        """
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            logging.info("Created output folder %s", self.output_folder)

        mov_files = [f for f in os.listdir(self.input_folder) if f.endswith(".MOV")]
        logging.info("Found %d .MOV files.", len(mov_files))

        with ThreadPoolExecutor() as executor:
            futures = []
            for mov_file in mov_files:
                futures.append(executor.submit(self.process_video, mov_file))

            with tqdm(total=len(futures)) as pbar:
                for future in futures:
                    future.result()
                    pbar.update(1)

    def process_video(self, mov_file):
        """
        Extracts frames from a single video file and saves them as images.

        Parameters
        ----------
        mov_file : str
            The name of the video file to extract frames from.
        """
        video_path = os.path.join(self.input_folder, mov_file)
        cap = VideoCapture(video_path)

        frames_folder = os.path.join(self.output_folder, f"{mov_file}_frames")
        if not os.path.exists(frames_folder):
            os.makedirs(frames_folder)

        metadata = {
            "total_frames": int(cap.get(CAP_PROP_FRAME_COUNT)),
            "fps": int(cap.get(CAP_PROP_FPS)),
            "duration": int(cap.get(CAP_PROP_POS_MSEC)),
        }

        frame_number = 0
        metadata_file = os.path.join(self.output_folder, f"{mov_file}_metadata.json")
        with open(metadata_file, "w", encoding="") as f:
            json.dump(metadata, f, indent=4)

        with tqdm(total=metadata["total_frames"]) as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_file = os.path.join(
                    frames_folder, f"frame_{frame_number}.{self.image_format}"
                )
                cv2.imwrite(  # pylint: disable=no-member
                    frame_file, frame
                )
                frame_number += 1
                pbar.update(1)

        cap.release()

        metadata_file = os.path.join(self.output_folder, f"{mov_file}_metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        logging.info("Extracted frames and metadata from %s", mov_file)
