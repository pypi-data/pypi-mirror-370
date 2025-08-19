import pytest
import cv2
import numpy as np
import os
from pixtract.processing import process_video_frames

@pytest.fixture
def robust_dummy_video(tmp_path):
    """Create a dummy video with more realistic, non-solid frames."""
    video_path = tmp_path / "test_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, 1, (20, 20))

    # Frame A: White background with a black square
    frame_a = np.ones((20, 20, 3), dtype=np.uint8) * 255
    cv2.rectangle(frame_a, (5, 5), (15, 15), (0, 0, 0), -1)

    # Frame B: Black background with a white circle
    frame_b = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.circle(frame_b, (10, 10), 5, (255, 255, 255), -1)

    # Write a sequence that will have duplicates when sampled
    # Sequence: [A, B, B, B, B, A, B, B, B, B, A, B]
    # Sampled at interval 5: Frame 0 (A), Frame 5 (A), Frame 10 (A)
    for i in range(12):
        if i == 0 or i == 5 or i == 10:
            out.write(frame_a)
        else:
            out.write(frame_b)
    
    out.release()
    return str(video_path)

def test_process_video_frames_with_robust_video(robust_dummy_video, tmp_path):
    """A more robust integration test for the main video processing function."""
    output_dir = tmp_path / "output"
    video_name = os.path.splitext(os.path.basename(robust_dummy_video))[0]
    video_output_dir = output_dir / video_name

    # Run the processing with a high duplicate threshold and a specific interval
    summary = process_video_frames(
        robust_dummy_video,
        str(video_output_dir),
        sharpness_threshold=10, # Lower threshold for simple frames
        duplicate_threshold=0.99, # Use a high threshold for near-identical frames
        frame_interval=5
    )

    # 1. Check the summary report
    assert summary is not None
    # With frame_interval=5, 12 frames should result in 3 extracted frames (0, 5, 10)
    assert summary["extracted_frames"] == 3
    # All three extracted frames are identical (Frame A), so 2 should be removed.
    assert summary["duplicate_frames_removed"] == 2
    assert summary["blurry_frames_removed"] == 0
    assert summary["final_frames_count"] == 1

    # 2. Check the actual file output
    assert os.path.isdir(video_output_dir)
    final_files = os.listdir(video_output_dir)
    assert len(final_files) == 1
    assert len([f for f in final_files if f.endswith(".jpg")]) == 1
