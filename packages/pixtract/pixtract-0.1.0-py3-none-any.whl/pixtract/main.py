"""Main entry point for the video processing application."""

import os
import sys
import logging
from tqdm import tqdm
from colorama import Fore, Style, init
from typing import List, Any, Optional, Dict
import argparse

from .cli import parse_args
from .processing import process_video_frames

init(autoreset=True)

def main() -> None:
    """Main function to process all specified videos."""
    try:
        args, parser = parse_args()

        # If no arguments were provided, print help and exit
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(0)

        # Configure logging
        log_level: int = logging.DEBUG if args.verbose else logging.INFO
        log_format: str = '%(asctime)s - %(levelname)s - %(message)s' if args.verbose else '%(message)s'
        logging.basicConfig(level=log_level, format=log_format)

        # Verbose header
        logging.debug(f"{Fore.CYAN}--- Verbose Mode Enabled ---")

        input_path: str = args.input_path
        output_directory: Optional[str] = args.output
        sharpness_threshold: int = args.sharpness
        duplicate_threshold: float = args.duplicate_threshold
        rotation_angle: int = args.rotate
        dry_run: bool = args.dry_run
        limit: Optional[int] = args.limit
        frame_interval: int = args.interval

        # --- CLI Argument Validation ---
        if not os.path.exists(input_path):
            logging.error(f"Error: Input path '{input_path}' does not exist.")
            sys.exit(1)
        
        if not os.path.isfile(input_path) and not os.path.isdir(input_path):
            logging.error(f"Error: Input path '{input_path}' is neither a file nor a directory.")
            sys.exit(1)

        # --- Determine Output Directory ---
        if output_directory is None:
            if os.path.isfile(input_path):
                output_directory_base = os.path.dirname(input_path)
                video_filename_no_ext = os.path.splitext(os.path.basename(input_path))[0]
                output_directory = os.path.join(output_directory_base, f"{video_filename_no_ext}_frames")
            else: # is a directory
                output_directory = os.path.join(input_path, "Processed_Frames")
        
        if os.path.isfile(input_path):
            video_files: List[str] = [input_path]
        else: # is a directory
            video_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]

        if not dry_run:
            # Check if output directory is writable
            if os.path.exists(output_directory) and not os.access(output_directory, os.W_OK):
                logging.error(f"Error: Output directory '{output_directory}' is not writable.")
                sys.exit(1)
            elif not os.path.exists(output_directory):
                try:
                    os.makedirs(output_directory)
                    logging.debug(f"Created output directory: {output_directory}")
                except OSError as e:
                    logging.error(f"Error creating output directory '{output_directory}': {e}", exc_info=True)
                    sys.exit(1)
        # --- End CLI Argument Validation ---

        if limit:
            video_files = video_files[:limit]

        processing_summaries: List[Dict[str, Any]] = []
        with tqdm(total=len(video_files), desc="Processing Videos", unit="video", bar_format="{l_bar}{bar:20}{r_bar}") as pbar:
            for video_file in video_files:
                # If input was a directory, each video gets its own subfolder in the output dir.
                # If input was a single file, frames are saved directly in the output dir.
                if os.path.isdir(input_path):
                    video_specific_output_folder = os.path.join(output_directory, os.path.splitext(os.path.basename(video_file))[0])
                else:
                    video_specific_output_folder = output_directory

                summary = process_video_frames(
                    video_file,
                    video_specific_output_folder,
                    sharpness_threshold=sharpness_threshold,
                    duplicate_threshold=duplicate_threshold,
                    rotation_angle=rotation_angle,
                    dry_run=dry_run,
                    frame_interval=frame_interval
                )
                processing_summaries.append(summary)
                pbar.update(1)

        logging.info(f"\n{Fore.GREEN}--- Video Processing Complete ---")
        total_frames_extracted: int = 0
        total_blurry_frames_removed: int = 0
        total_duplicate_frames_removed: int = 0
        total_final_frames_count: int = 0

        for summary in processing_summaries:
            total_frames_extracted += summary["extracted_frames"]
            total_blurry_frames_removed += summary["blurry_frames_removed"]
            total_duplicate_frames_removed += summary["duplicate_frames_removed"]
            total_final_frames_count += summary["final_frames_count"]

            logging.debug(f"\n{Fore.CYAN}Video: {summary['video']}")
            logging.debug(f"  {Fore.YELLOW}Output Folder: {summary['output_folder']}")
            logging.debug(f"  {Fore.BLUE}Extracted Frames: {summary['extracted_frames']}")
            logging.debug(f"  {Fore.RED}Blurry Frames Removed: {summary['blurry_frames_removed']}")
            logging.debug(f"  {Fore.MAGENTA}Duplicate Frames Removed: {summary['duplicate_frames_removed']}")
            logging.debug(f"  {Fore.GREEN}Final Frames Count: {summary['final_frames_count']}")

        logging.info(f"\n{Fore.GREEN}--- Overall Summary ---")
        logging.info(f"{Fore.BLUE}Total Extracted Frames: {total_frames_extracted}")
        logging.info(f"{Fore.RED}Total Blurry Frames Removed: {total_blurry_frames_removed}")
        logging.info(f"{Fore.MAGENTA}Total Duplicate Frames Removed: {total_duplicate_frames_removed}")
        logging.info(f"{Fore.GREEN}Total Final Frames Count: {total_final_frames_count}")

    except KeyboardInterrupt:
        logging.info("\n\nProcessing interrupted by user. Exiting gracefully.")
        sys.exit(0)
    except SystemExit as e:
        if e.code != 0:
            # Error is already printed by argparse custom error handler
            pass
        sys.exit(e.code)
    except Exception as e:
        logging.error(f"An unhandled error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()