# Pixtract

Pixtract is a powerful and efficient command-line tool designed to extract high-quality frames from videos. It streamlines the process of obtaining sharp, non-duplicate images from your video files, making it ideal for computer vision datasets, video analysis, or simply capturing the best moments from your recordings.

## Features

- **High-Quality Frame Extraction:** Extracts frames from a variety of video formats (MP4, MOV, AVI, MKV).
- **Blur Detection:** Automatically analyzes and discards blurry frames, ensuring you only get sharp, clear images.
- **Duplicate Frame Removal:** Efficiently identifies and removes duplicate or near-duplicate frames based on a configurable threshold, saving you time and disk space.
- **Image Rotation:** Corrects the orientation of frames with adjustable rotation.
- **Batch Processing:** Process multiple videos in a single run, from a given directory.
- **Dry Run Mode:** Simulate the process without creating or deleting any files.
- **Verbose Output:** Get detailed logging information for debugging or deeper insights.

## Installation

You can install Pixtract directly from GitHub using `Git`:
```bash
pip install git+https://github.com/rahaaatul/Pixtract.git
```
or from PyPI using `pip`:

```bash
pip install pixtract
```
Or with `pipx` for isolated installation:

```bash
pipx install pixtract
```

## Usage

To use Pixtract, simply run the `pixtract` command with the path to your video file or a directory containing videos.

### Basic Usage

Process a single video and save frames to a default output folder:

```bash
pixtract "path/to/your/video.mp4"
```

Process all videos in a directory and save frames to a specified output folder:

```bash
pixtract "path/to/your/videos_directory" -o "path/to/your/output_folder"
```

### Examples

Extract frames from `my_movie.mp4`, remove blurry frames (sharpness threshold 50), and remove duplicates (threshold 0.98):

```bash
pixtract my_movie.mp4 -s 50 -d 0.98
```

Process videos in `my_videos/`, rotate frames by 90 degrees, and enable verbose output:

```bash
pixtract my_videos/ -r 90 -v
```

Simulate processing `holiday_clip.mp4` without actually saving or deleting files:

```bash
pixtract holiday_clip.mp4 --dry-run
```

## Command-Line Options

| Option              | Short | Type    | Default        | Description                                                              |
| :------------------ | :---- | :------ | :------------- | :----------------------------------------------------------------------- |
| `--input-path`      |       | `str`   | Current Dir    | Path to a video file or a directory containing videos.                   |
| `--output`          | `-o`  | `str`   | `Processed_Frames` | Path to the output directory.                                            |
| `--sharpness`       | `-s`  | `int`   | `100`          | Set the sharpness threshold for blur detection. Lower values are more permissive. |
| `--duplicate`       | `-d`  | `float` | `1`         | Set the threshold for duplicate detection. Higher values are more strict. |
| `--rotate`          | `-r`  | `int`   | `0`            | Rotate frames by 0, 90, 180, or 270 degrees.                             |
| `--dry-run`         |       | `flag`  | `False`        | Simulate the process without creating or deleting files.                 |
| `--limit`           | `-l`  | `int`   | `None`         | Limit the number of videos to process.                                   |
| `--verbose`         | `-v`  | `flag`  | `False`        | Enable verbose (debug) output.                                           |

## Development

To set up the project for development, clone the repository and install the development dependencies:

```bash
git clone https://github.com/rahaaatul/pixtract.git
cd pixtract
pip install -e .[dev]
```

### Running Tests

To run the test suite, ensure you have installed the development dependencies and then execute `pytest`:

```bash
pip install -e .[dev]
pytest
```

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request. For bug reports, please use the [Bug Report template](https://github.com/rahaaatul/pixtract/issues/new?assignees=&labels=bug&projects=&template=bug_report.md&title=). For new features, use the [Feature Request template](https://github.com/rahaaatul/pixtract/issues/new?assignees=&labels=enhancement&projects=&template=feature_request.md&title=).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.