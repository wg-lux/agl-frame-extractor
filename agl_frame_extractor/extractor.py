"""Model for extracting frames from video files and saving them as images."""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import cv2
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_FPS, CAP_PROP_POS_MSEC  # pylint: disable=no-name-in-module
from tqdm import tqdm
import subprocess  # new import for transcoding
from icecream import ic
from pathlib import Path


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

        video_files = [
            f
            for f in os.listdir(self.input_folder)
            if f.lower().endswith((".mov", ".mp4"))
        ]
        logging.info("Found %d video files.", len(video_files))

        futures = []
        for video_file in tqdm(video_files):
            input_path = os.path.join(self.input_folder, video_file)
            transcoded = self.transcode_video(input_path)
            futures.append(transcoded)

        with tqdm(total=len(futures)) as pbar:
            for future in futures:
                self.process_video(future)
                pbar.update(1)

    def transcode_video(self, mov_file):
        """
        Transcodes a video to a compatible MP4 format using ffmpeg.
        If the transcoded file exists, it is returned.

        Parameters
        ----------
        mov_file : str
            The full path to the video file.

        Returns
        -------
        transcoded_path : str
            The full path to the transcoded video file.
        """
        ic("Transcoding video")
        ic(f"Input path: {mov_file}")
        # Determine transcoded output filepath (appending '_transcoded.mp4')
        base = os.path.splitext(os.path.basename(mov_file))[0]
        transcoded_path = os.path.join(self.output_folder, f"{base}_transcoded.mp4")

        ic(f"Transcoded path: {transcoded_path}")
        if os.path.exists(transcoded_path):
            return transcoded_path

        # Run ffmpeg to transcode the video using H264 and AAC
        # TODO Document settings, check if we need to change them
        command = [
            "ffmpeg",
            "-i",
            mov_file,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "aac",
            transcoded_path,
        ]
        subprocess.run(command, check=True)
        logging.info("Transcoded video saved to %s", transcoded_path)
        return transcoded_path

    def frames_already_extracted(self, video_path: str) -> bool:
        """Check if frames have already been extracted for this video."""
        video_name = Path(video_path).name
        frames_dir = Path(self.output_folder) / f"{video_name}_frames"
        metadata_file = Path(self.output_folder) / f"{video_name}_metadata.json"

        # Quick check if either doesn't exist
        if not frames_dir.is_dir() or not metadata_file.is_file():
            return False

        try:
            # Read metadata
            with metadata_file.open("r") as f:
                metadata = json.load(f)
            expected_frames = metadata.get("total_frames", 0)

            # Count actual frames
            actual_frames = len(list(frames_dir.glob(f"*.{self.image_format}")))

            return actual_frames == expected_frames
        except (json.JSONDecodeError, KeyError, OSError):
            return False

    def process_video(self, mov_file):
        """
        Extracts frames from a single video file and saves them as images.

        Parameters
        ----------
        mov_file : str
            The video file path (absolute or file name) to extract frames from.
        """
        # Use absolute path if provided; otherwise, join with input_folder.

        ic(mov_file)
        video_path = (
            mov_file
            if os.path.isabs(mov_file)
            else os.path.join(self.input_folder, mov_file)
        )

        if self.frames_already_extracted(video_path):
            logging.info(f"Frames already extracted for {mov_file}, skipping...")
            return

        # Use explicit ffmpeg backend to help address HEVC decoding issues.
        cap = VideoCapture(video_path)  # pylint: disable=no-member
        mov_file_name = os.path.basename(mov_file)
        frames_folder = os.path.join(self.output_folder, f"{mov_file_name}_frames")
        if not os.path.exists(frames_folder):
            os.makedirs(frames_folder)

        metadata = {
            "total_frames": int(cap.get(CAP_PROP_FRAME_COUNT)),
            "fps": int(cap.get(CAP_PROP_FPS)),
            "duration": int(cap.get(CAP_PROP_POS_MSEC)),
        }

        frame_number = 0
        metadata_file = os.path.join(
            self.output_folder, f"{mov_file_name}_metadata.json"
        )
        with open(metadata_file, "w", encoding="utf-8") as f:
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

        logging.info("Extracted frames and metadata from %s", mov_file)
