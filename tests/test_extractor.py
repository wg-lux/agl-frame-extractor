import unittest
from ..agl_frame_extractor.extractor import VideoFrameExtractor

class TestVideoFrameExtractor(unittest.TestCase):
    
    def test_initialization(self):
        extractor = VideoFrameExtractor("input", "output")
        self.assertEqual(extractor.input_folder, "input")
        self.assertEqual(extractor.output_folder, "output")

    # Add more tests here

if __name__ == '__main__':
    unittest.main()
