"""Core functions for video frame extraction, sharpness analysis, and duplicate detection."""
import os
import cv2
import logging
from typing import Dict, Any, Optional
from tqdm import tqdm
from .utils import calculate_sharpness, are_images_duplicates

def extract_frames(video_path: str, output_folder: str, frame_interval: int = 1, rotation_angle: int = 0, dry_run: bool = False) -> int:
    """
    Extracts frames from a video file and saves them as images.

    Args:
        video_path (str): The path to the video file.
        output_folder (str): The path to the output directory.
        frame_interval (int, optional): The interval at which to extract frames. Defaults to 1 (every frame).
        rotation_angle (int, optional): The angle to rotate the frames. Defaults to 0.
        dry_run (bool, optional): If True, simulates the process without saving files. Defaults to False.

    Returns:
        int: The number of frames that were actually saved.
    """
    if not dry_run:
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as e:
            logging.error(f"Error creating output directory {output_folder}: {e}", exc_info=True)
            return 0

    try:
        cap = cv2.VideoCapture(video_path)
    except cv2.error as e:
        logging.error(f"OpenCV error opening video file {video_path}: {e}", exc_info=True)
        return 0
    except Exception as e:
        logging.error(f"Unexpected error opening video file {video_path}: {e}", exc_info=True)
        return 0

    if not cap.isOpened():
        logging.error(f"Could not open video file: {video_path}")
        return 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    saved_frame_count = 0
    
    with tqdm(total=total_frames, desc=f"Extracting {os.path.basename(video_path)}", unit="frame", leave=False) as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                if rotation_angle != 0:
                    if rotation_angle == 90:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif rotation_angle == 180:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif rotation_angle == 270:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
                if not dry_run:
                    try:
                        if cv2.imwrite(frame_filename, frame):
                            saved_frame_count += 1
                        else:
                            logging.warning(f"cv2.imwrite reported failure for frame: {frame_filename}")
                    except Exception as e:
                        logging.error(f"Exception while writing frame {frame_filename}: {e}", exc_info=True)
                else:
                    saved_frame_count += 1 # Assume success in dry run

            frame_count += 1
            pbar.update(1)

    cap.release()
    logging.debug(f"Extracted {saved_frame_count} frames from {video_path}")
    return saved_frame_count

def process_video_frames(video_path: str, output_folder: str, sharpness_threshold: int = 100, duplicate_threshold: float = 1.0, rotation_angle: int = 0, dry_run: bool = False, frame_interval: int = 1) -> Dict[str, Any]:
    """
    Extracts, cleans, and processes frames from a single video.

    Args:
        video_path (str): The path to the video file.
        output_folder (str): The directory for the output frames.
        sharpness_threshold (int, optional): The sharpness threshold for blur detection. Defaults to 100.
        duplicate_threshold (float, optional): The threshold for duplicate detection. Higher values (closer to 1.0) are more strict, meaning frames must be nearly identical to be considered duplicates. Defaults to 1.0.
        rotation_angle (int, optional): The angle to rotate the frames. Defaults to 0.
        dry_run (bool, optional): If True, simulates the process without saving files. Defaults to False.
        frame_interval (int, optional): The interval at which to extract frames. Defaults to 1 (every frame).

    Returns:
        dict: A summary of the processing results.
    """
    initial_frame_count = extract_frames(video_path, output_folder, rotation_angle=rotation_angle, dry_run=dry_run, frame_interval=frame_interval)

    if initial_frame_count == 0:
        return {
            "video": os.path.basename(video_path),
            "extracted_frames": 0,
            "blurry_frames_removed": 0,
            "duplicate_frames_removed": 0,
            "final_frames_count": 0,
            "output_folder": output_folder
        }

    # Process blurriness
    frame_files = []
    try:
        if not dry_run:
            frame_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".jpg")]
    except OSError as e:
        logging.error(f"Error listing files in {output_folder} for blurriness check: {e}", exc_info=True)
        return {
            "video": os.path.basename(video_path),
            "extracted_frames": initial_frame_count,
            "blurry_frames_removed": 0,
            "duplicate_frames_removed": 0,
            "final_frames_count": initial_frame_count,
            "output_folder": output_folder,
            "error": "Failed to list files for blurriness check"
        }

    blurry_frames_removed = 0
    if not dry_run:
        for frame_file in frame_files:
            sharpness = calculate_sharpness(frame_file)
            if sharpness < sharpness_threshold:
                try:
                    os.remove(frame_file)
                    blurry_frames_removed += 1
                    logging.debug(f"Removed blurry frame: {frame_file}")
                except OSError as e:
                    logging.error(f"Error removing blurry frame {frame_file}: {e}", exc_info=True)

    # Process duplicates
    remaining_frames = []
    try:
        if not dry_run:
            remaining_frames = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".jpg")]
            remaining_frames.sort()
    except OSError as e:
        logging.error(f"Error listing files in {output_folder} for duplicate check: {e}", exc_info=True)
        return {
            "video": os.path.basename(video_path),
            "extracted_frames": initial_frame_count,
            "blurry_frames_removed": blurry_frames_removed,
            "duplicate_frames_removed": 0,
            "final_frames_count": initial_frame_count - blurry_frames_removed,
            "output_folder": output_folder,
            "error": "Failed to list files for duplicate check"
        }
    
    duplicates_removed = 0
    if not dry_run and len(remaining_frames) > 1:
        to_remove = set()
        for i in range(len(remaining_frames)):
            for j in range(i + 1, len(remaining_frames)):
                if remaining_frames[j] in to_remove:
                    continue
                if are_images_duplicates(remaining_frames[i], remaining_frames[j], duplicate_threshold=duplicate_threshold):
                    to_remove.add(remaining_frames[j])

        for frame_to_remove in to_remove:
            try:
                os.remove(frame_to_remove)
                logging.debug(f"Removed duplicate frame: {frame_to_remove}")
            except OSError as e:
                logging.error(f"Error removing duplicate frame {frame_to_remove}: {e}", exc_info=True)
        duplicates_removed = len(to_remove)

    final_frames_count = 0
    if not dry_run:
        try:
            final_frames_count = len([f for f in os.listdir(output_folder) if f.endswith(".jpg")])
        except OSError as e:
            logging.error(f"Could not count final frames in {output_folder}: {e}", exc_info=True)
    else:
        final_frames_count = initial_frame_count - blurry_frames_removed - duplicates_removed


    return {
        "video": os.path.basename(video_path),
        "extracted_frames": initial_frame_count,
        "blurry_frames_removed": blurry_frames_removed,
        "duplicate_frames_removed": duplicates_removed,
        "final_frames_count": final_frames_count,
        "output_folder": output_folder
    }
