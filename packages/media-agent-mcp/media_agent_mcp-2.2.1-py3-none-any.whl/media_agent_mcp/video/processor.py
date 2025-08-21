"""Video processing module.

This module provides video processing functionality including concatenation and frame extraction.
Uses pure OpenCV for video processing without FFmpeg dependencies.
"""
import logging
import os
import tempfile
import time
import uuid
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse

import cv2
import numpy as np
import requests
import subprocess

from media_agent_mcp.storage.tos_client import upload_to_tos

logger = logging.getLogger(__name__)


def get_video_info(video_path: str) -> Tuple[int, int, float, int]:
    """Get video information using OpenCV.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Tuple of (width, height, fps, frame_count)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    cap.release()
    return width, height, fps, frame_count


def get_video_codec_and_format(video_path: str, high_quality: bool = True) -> Tuple[int, str]:
    """Get video codec information for output video with quality optimization.
    
    Args:
        video_path: Path to the video file
        high_quality: Whether to prioritize quality over compatibility
        
    Returns:
        Tuple of (fourcc_code, file_extension)
    """
    # Test codec availability by creating a temporary video writer
    def test_codec(fourcc_code, width=640, height=480, fps=30.0):
        """Test if a codec is available by trying to create a VideoWriter."""
        try:
            temp_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
            writer = cv2.VideoWriter(temp_path, fourcc_code, fps, (width, height))
            is_opened = writer.isOpened()
            writer.release()
            
            # Clean up test file
            try:
                os.unlink(temp_path)
            except:
                pass
                
            return is_opened
        except:
            return False
    
    if high_quality:
        # Prioritize quality codecs for high-quality concatenation
        codecs_to_try = [
            ('H264', cv2.VideoWriter_fourcc(*'H264')),  # H.264 - best quality and compatibility
            ('avc1', cv2.VideoWriter_fourcc(*'avc1')),  # H.264 alternative
            ('X264', cv2.VideoWriter_fourcc(*'X264')),  # H.264 alternative
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),  # XVID - good quality
            ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),  # MPEG-4 - decent quality
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),  # Motion JPEG - larger files but good quality
        ]
        logger.info("Testing available video codecs for high-quality output...")
    else:
        # Standard compatibility-focused codec selection
        codecs_to_try = [
            ('H264', cv2.VideoWriter_fourcc(*'H264')),  # H.264 - best browser compatibility
            ('avc1', cv2.VideoWriter_fourcc(*'avc1')),  # H.264 alternative
            ('X264', cv2.VideoWriter_fourcc(*'X264')),  # H.264 alternative
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),  # XVID - good compatibility
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),  # Motion JPEG - widely supported
            ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),  # MPEG-4 - last resort
        ]
        logger.info("Testing available video codecs for browser compatibility...")
    
    for codec_name, fourcc in codecs_to_try:
        if test_codec(fourcc):
            logger.info(f"Using codec: {codec_name} (high_quality={high_quality})")
            return fourcc, '.mp4'
        else:
            logger.debug(f"Codec {codec_name} not available")
    
    # If no codec works, fall back to mp4v without testing
    logger.warning("No tested codecs available, using mp4v as fallback")
    return cv2.VideoWriter_fourcc(*'mp4v'), '.mp4'


def download_video_from_url(url: str) -> Dict[str, Any]:
    """Download video from URL to a temporary file.
    
    Args:
        url: URL of the video to download
        
    Returns:
        JSON response with status, data (file path), and message
    """
    try:
        # Parse URL to get file extension
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.mp4'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_path = temp_file.name
        temp_file.close()
        
        # Download the video
        logger.info(f"Downloading video from {url}...")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Video downloaded to {temp_path}")
        return {
            "status": "success",
            "data": {"file_path": temp_path},
            "message": "Video downloaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error downloading video from {url}: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error downloading video from {url}: {e}"
        }


def concat_videos(video_urls: list, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Concatenate multiple videos into one using pure OpenCV.
    
    Args:
        video_urls: List of URLs or paths to video files to concatenate in order
        output_path: Optional output path for the concatenated video
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_files = []
    video_captures = []
    video_writer = None
    
    try:
        if not video_urls or len(video_urls) == 0:
            return {
                "status": "error",
                "data": None,
                "message": "No video URLs provided"
            }
            
        if not output_path:
            output_path = f"concatenated_{int(time.time())}.mp4"
        
        # Download videos if they are URLs and prepare local paths
        video_paths = []
        for video_input in video_urls:
            if video_input.startswith(('http://', 'https://')):
                download_result = download_video_from_url(video_input)
                if download_result["status"] == "error":
                    return download_result
                video_path = download_result["data"]["file_path"]
                temp_files.append(video_path)
                video_paths.append(video_path)
            elif os.path.exists(video_input):
                video_paths.append(video_input)
            else:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Video file {video_input} not found"
                }
        
        # Get video information from all videos to determine optimal output parameters
        logger.info("Analyzing video properties for high-quality concatenation...")
        video_infos = []
        
        for i, video_path in enumerate(video_paths):
            try:
                width, height, fps, frame_count = get_video_info(video_path)
                video_infos.append({
                    'path': video_path,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'frame_count': frame_count
                })
                logger.info(f"Video {i+1}: {width}x{height}, {fps} fps, {frame_count} frames")
            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error reading video {video_path}: {str(e)}"
                }
        
        # Use the maximum dimensions to preserve highest quality
        # This ensures no video is downscaled, maintaining original quality
        output_width = max(info['width'] for info in video_infos)
        output_height = max(info['height'] for info in video_infos)
        
        # Use the highest frame rate for smooth playback
        output_fps = max(info['fps'] for info in video_infos)
        
        logger.info(f"Output parameters for high quality: {output_width}x{output_height}, {output_fps} fps")
        logger.info("Note: Smaller videos will be upscaled to maintain consistent dimensions")
        
        # Concatenate videos using FFmpeg for higher efficiency and quality
        logger.info("Concatenating videos with FFmpeg...")
        
        try:
            # Build FFmpeg command dynamically for scaling and concatenation
            ffmpeg_cmd = ["ffmpeg", "-y"]
            for path in video_paths:
                ffmpeg_cmd.extend(["-i", path])
            
            filter_parts = []
            for idx in range(len(video_paths)):
                filter_parts.append(f"[{idx}:v]scale={output_width}:{output_height}:flags=lanczos,fps={output_fps}[v{idx}];")
            concat_inputs = "".join([f"[v{i}]" for i in range(len(video_paths))])
            filter_complex = "".join(filter_parts) + f"{concat_inputs}concat=n={len(video_paths)}:v=1:a=0[outv]"
            
            ffmpeg_cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                output_path
            ])
            
            logger.debug(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
            result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return {
                    "status": "error",
                    "data": None,
                    "message": "FFmpeg failed to concatenate videos"
                }
            
            logger.info(f"Videos concatenated successfully with FFmpeg: {output_path}")
        except Exception as e:
            logger.error(f"Error during FFmpeg concatenation: {e}")
            return {
                "status": "error",
                "data": None,
                "message": f"Error concatenating videos with FFmpeg: {str(e)}"
            }
        # Estimate total frames from metadata for logging purposes
        total_frames_written = sum(info['frame_count'] for info in video_infos)
        logger.info(f"Estimated total frames in concatenated video: {total_frames_written}")
        
        # Upload concatenated video to TOS
        try:
            tos_url = upload_to_tos(output_path)
            logger.info(f"Video uploaded to TOS: {tos_url}")
            
            # Clean up local concatenated file
            try:
                os.unlink(output_path)
                logger.info(f"Cleaned up local concatenated file: {output_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up local file {output_path}: {e}")
            
            return {
                "status": "success",
                "data": {"tos_url": tos_url},
                "message": f"Videos concatenated and uploaded successfully ({total_frames_written} frames)"
            }
        except Exception as e:
            logger.error(f"Error uploading to TOS: {e}")
            return {
                "status": "error",
                "data": None,
                "message": f"Error uploading to TOS: {str(e)}"
            }
        
    except Exception as e:
        logger.error(f"Error concatenating videos: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error concatenating videos: {str(e)}"
        }
    finally:
        # No video_writer to release when using FFmpeg
        
        # Release any remaining video captures
        for cap in video_captures:
            if cap.isOpened():
                cap.release()
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")


def extract_last_frame(video_input: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract the last frame from a video as an image and upload to TOS.
    
    Args:
        video_input: URL or path to the video file
        output_path: Optional output path for the extracted frame
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_video_file = None
    
    try:
        # Handle URL or local file path
        if video_input.startswith(('http://', 'https://')):
            # Download video from URL
            download_result = download_video_from_url(video_input)
            if download_result["status"] == "error":
                return download_result
            video_path = download_result["data"]["file_path"]
            temp_video_file = video_path
        elif os.path.exists(video_input):
            video_path = video_input
        else:
            return {
                "status": "error",
                "data": None,
                "message": f"Video file {video_input} not found"
            }
        
        if not output_path:
            output_path = f"last_frame_{uuid.uuid4().hex}.jpg"
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                "status": "error",
                "data": None,
                "message": f"Could not open video {video_path}"
            }
        
        # Get total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Video has no frames"
            }
        
        # Set position to last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        
        # Read the last frame
        ret, frame = cap.read()
        
        if ret:
            # Save the frame
            cv2.imwrite(output_path, frame)
            cap.release()
            logger.info(f"Last frame extracted: {output_path}")
            
            # Upload frame to TOS
            try:
                tos_url = upload_to_tos(output_path)
                logger.info(f"Frame uploaded to TOS: {tos_url}")
                
                # Clean up local frame file
                try:
                    os.unlink(output_path)
                    logger.info(f"Cleaned up local frame file: {output_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up local file {output_path}: {e}")
                
                return {
                    "status": "success",
                    "data": {"tos_url": tos_url},
                    "message": "Last frame extracted and uploaded successfully"
                }
            except Exception as e:
                logger.error(f"Error uploading frame to TOS: {e}")
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error uploading to TOS: {str(e)}"
                }
        else:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Could not read the last frame"
            }
            
    except Exception as e:
        logger.error(f"Error extracting last frame: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error extracting last frame: {str(e)}"
        }
    finally:
        # Clean up temporary video file if downloaded
        if temp_video_file and os.path.exists(temp_video_file):
            try:
                os.unlink(temp_video_file)
                logger.info(f"Cleaned up temporary video file: {temp_video_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary video file {temp_video_file}: {e}")


if __name__ == '__main__':
    # Example usage
    video_urls = [
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4",
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205817458400000000000000000000ffffc0a850948120ae.mp4"
    ]

    concatenated_video = concat_videos(video_urls)
    print(f"Concatenated video URL: {concatenated_video}")

    last_frame_url = extract_last_frame(video_urls[0])
    print(f"Last frame URL: {last_frame_url}")