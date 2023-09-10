# agl-frame-extractor
## Description

`agl_frame_extractor` is a Python package designed to extract individual frames and metadata from .MOV video files. This package is highly useful for researchers and clinicians who require frame-by-frame analysis of video data. With applications ranging from medical research to training simulations, the package aims to improve standards and classifications in gastrointestinal endoscopy by enhancing objectivity and reproducibility.

## Features

- Extracts individual frames from .MOV files and saves them as PNG images.
- Gathers video metadata including total number of frames, frames per second, and video duration.
- Offers optional multithreading support for faster frame extraction.
- Generates a log file to record the extraction process.

## Installation

To install this package, clone the repository and run the following command in the repository root:

```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from video_frame_extractor.extractor import VideoFrameExtractor

input_folder = "input_videos"
output_folder = "output_frames_metadata"

extractor = VideoFrameExtractor(input_folder, output_folder)
extractor.extract_frames_and_metadata()

# If you want to extract png files instead of jpgs:
input_folder = "input_videos"
output_folder = "output_frames_metadata"

extractor = VideoFrameExtractor(input_folder, output_folder, image_format='png')
extractor.extract_frames_and_metadata()
```

### Multithreaded Usage

To enable multithreading for faster frame extraction:

```python
from video_frame_extractor.extractor import VideoFrameExtractor

input_folder = "input_videos"
output_folder = "output_frames_metadata"

extractor = VideoFrameExtractor(input_folder, output_folder, use_multithreading=True)
extractor.extract_frames_and_metadata()
```

## Dependencies

- OpenCV
- tqdm

## Logging

The package generates a log file `video_frame_extraction.log` in the directory where it is executed. This log file contains detailed information about the extraction process.

## Contributing

We welcome contributions to improve this package. Please follow the standard GitHub pull request process. Make sure to document your code thoroughly, keeping in mind that the package targets an academic audience focused on research.

