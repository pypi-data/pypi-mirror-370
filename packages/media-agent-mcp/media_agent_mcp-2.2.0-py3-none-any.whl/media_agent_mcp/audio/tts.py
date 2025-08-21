import requests
import json
import base64
import os
import tempfile
import subprocess
from loguru import logger
from typing import Dict, Any, List
from media_agent_mcp.storage.tos_client import upload_to_tos
from media_agent_mcp.video.processor import download_video_from_url, get_video_info
from media_agent_mcp.ai_models.seed16 import process_vlm_task
from media_agent_mcp.install_tools.installer import which_ffmpeg


FFMPEG_PATH = which_ffmpeg()
FFPROBE_PATH = ""
if FFMPEG_PATH:
    FFPROBE_PATH = os.path.join(os.path.dirname(FFMPEG_PATH), "ffprobe")


# Pre-defined voice mapping
VOICE_MAP = [
    {"scenario": "Dubbing", "language": ["English", "Chinese"], "voice": "Tina", "gender": "Female", "style": "Vivid", "speaker_id": "zh_female_shaoergushi_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["English", "Chinese"], "voice": "William", "gender": "Male", "style": "Deep", "speaker_id": "zh_male_silang_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["English", "Chinese"], "voice": "James", "gender": "Male", "style": "Clear", "speaker_id": "zh_male_jieshuonansheng_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["English", "Chinese"], "voice": "Grace", "gender": "Female", "style": "Softe", "speaker_id": "zh_female_jitangmeimei_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["English", "Chinese"], "voice": "Sophia", "gender": "Female", "style": "Warm", "speaker_id": "zh_female_tiexinnvsheng_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["English", "Chinese"], "voice": "Mia", "gender": "Female", "style": "Vivid", "speaker_id": "zh_female_qiaopinvsheng_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["English", "Chinese"], "voice": "Ava", "gender": "Female", "style": "Vivid", "speaker_id": "zh_female_mengyatou_mars_bigtts"},
    {"scenario": "General", "language": ["English", "Chinese"], "voice": "Luna", "gender": "Female", "style": "Clear", "speaker_id": "zh_female_cancan_mars_bigtts"},
    {"scenario": "General", "language": ["English", "Chinese"], "voice": "Olivia", "gender": "Female", "style": "Clear", "speaker_id": "zh_female_qingxinnvsheng_mars_bigtts"},
    {"scenario": "General", "language": ["English", "Chinese"], "voice": "Lily", "gender": "Female", "style": "Vivid", "speaker_id": "zh_female_linjia_mars_bigtts"},
    {"scenario": "General", "language": ["English", "Chinese"], "voice": "Mark", "gender": "Male", "style": "Warm", "speaker_id": "zh_male_wennuanahu_moon_bigtts"},
    {"scenario": "General", "language": ["English", "Chinese"], "voice": "Ethan", "gender": "Male", "style": "Clear", "speaker_id": "zh_male_shaonianzixin_moon_bigtts"},
    {"scenario": "General", "language": ["English", "Chinese"], "voice": "Aria", "gender": "Female", "style": "Vivid", "speaker_id": "zh_female_shuangkuaisisi_moon_bigtts"},
    {"scenario": "Fun", "language": ["English", "Chinese - Beijing Accent"], "voice": "Thomas", "gender": "Male", "style": "Fun", "speaker_id": "zh_male_jingqiangkanye_moon_bigtts"},
    {"scenario": "General", "language": ["English"], "voice": "Anna", "gender": "Female", "style": "Soft", "speaker_id": "en_female_anna_mars_bigtts"},
    {"scenario": "General", "language": ["American English"], "voice": "Adam", "gender": "Male", "style": "Clear", "speaker_id": "en_male_adam_mars_bigtts"},
    {"scenario": "General", "language": ["Australian English"], "voice": "Sarah", "gender": "Female", "style": "Soft", "speaker_id": "en_female_sarah_mars_bigtts"},
    {"scenario": "General", "language": ["Australian English"], "voice": "Dryw", "gender": "Male", "style": "Deep", "speaker_id": "en_male_dryw_mars_bigtts"},
    {"scenario": "General", "language": ["British English"], "voice": "Smith", "gender": "Male", "style": "Deep", "speaker_id": "en_male_smith_mars_bigtts"},
    {"scenario": "Audio Book", "language": ["Chinese"], "voice": "Edward", "gender": "Male", "style": "Deep", "speaker_id": "zh_male_baqiqingshu_mars_bigtts"},
    {"scenario": "Audio Book", "language": ["Chinese"], "voice": "Emma", "gender": "Female", "style": "Soft", "speaker_id": "zh_female_wenroushunv_mars_bigtts"},
    {"scenario": "Role", "language": ["Chinese"], "voice": "Charlotte", "gender": "Female", "style": "Clear", "speaker_id": "zh_female_gaolengyujie_moon_bigtts"},
    {"scenario": "General", "language": ["Chinese"], "voice": "Lila", "gender": "Female", "style": "Clear", "speaker_id": "zh_female_linjianvhai_moon_bigtts"},
    {"scenario": "General", "language": ["Chinese"], "voice": "Joseph", "gender": "Male", "style": "Deep", "speaker_id": "zh_male_yuanboxiaoshu_moon_bigtts"},
    {"scenario": "General", "language": ["Chinese"], "voice": "George", "gender": "Male", "style": "Clear", "speaker_id": "zh_male_yangguangqingnian_moon_bigtts"},
    {"scenario": "Fun", "language": ["Chinese - Cantonese Accent"], "voice": "Andrew", "gender": "Male", "style": "Clear", "speaker_id": "zh_male_guozhoudege_moon_bigtts"},
    {"scenario": "Fun", "language": ["Chinese - Cantonese Accent"], "voice": "Robert", "gender": "Male", "style": "Fun", "speaker_id": "zh_female_wanqudashu_moon_bigtts"},
    {"scenario": "Fun", "language": ["Chinese - Sichuan Accent"], "voice": "Elena", "gender": "Female", "style": "Cute", "speaker_id": "zh_female_daimengchuanmei_moon_bigtts"},
    {"scenario": "Fun", "language": ["Chinese - Taiwanese Accent"], "voice": "Isabella", "gender": "Female", "style": "Vivid", "speaker_id": "zh_female_wanwanxiaohe_moon_bigtts"},
    {"scenario": "General", "language": ["Japanese", "Spanish"], "voice": "かずね", "gender": "Male", "style": "Fun", "speaker_id": "multi_male_jingqiangkanye_moon_bigtts"},
    {"scenario": "General", "language": ["Japanese", "Spanish"], "voice": "はるこ", "gender": "Female", "style": "Vivid", "speaker_id": "multi_female_shuangkuaisisi_moon_bigtts"},
    {"scenario": "General", "language": ["Japanese", "Spanish"], "voice": "ひろし", "gender": "Male", "style": "Fun", "speaker_id": "multi_male_wanqudashu_moon_bigtts"},
    {"scenario": "General", "language": ["Japanese"], "voice": "あけみ", "gender": "Female", "style": "Clear", "speaker_id": "multi_female_gaolengyujie_moon_bigtts"}
]


def get_tts_resource_map():
    """
    Returns the pre-defined voice mapping.
    
    Returns:
        list: The complete VOICE_MAP list
    """
    return VOICE_MAP


def get_voice_speaker(language: str, gender: str) -> Dict[str, Any]:
    """
    Return available speakers that match the provided language and gender filters.
    
    Args:
        language: The language to filter by (enum): English | Chinese | American English | Australian English | British English | Japanese | Spanish
        gender: The gender to filter by (enum): Male | Female
    
    Returns:
        dict: JSON response with status, data (available_speakers list), and message
    """
    try:
        # Filter speakers based on language and gender
        available_speakers = []
        
        for speaker in VOICE_MAP:
            # Check if the requested language is in the speaker's language list
            if language in speaker["language"] and speaker["gender"] == gender:
                available_speakers.append({
                    "speaker_id": speaker["speaker_id"],
                    "voice": speaker["voice"],
                    "style": speaker["style"],
                    "scenario": speaker["scenario"]
                })
        
        return {
            "status": "success",
            "data": {"available_speakers": available_speakers},
            "message": f"Found {len(available_speakers)} speakers for {language} {gender}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error getting voice speakers: {str(e)}"
        }


def get_audio_duration(audio_path: str) -> float:
    """
    Get audio duration in seconds using ffprobe.
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        float: Duration in seconds
    """
    try:
        if not FFPROBE_PATH or not os.path.exists(FFPROBE_PATH):
            raise FileNotFoundError("ffprobe executable not found")
        cmd = [
            FFPROBE_PATH, '-v', 'quiet', '-print_format', 'json', 
            '-show_format', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0.0


def speed_up_audio(audio_path: str, speed_factor: float, output_path: str) -> bool:
    """
    Speed up audio while preserving pitch using ffmpeg with enhanced quality filters.
    
    Args:
        audio_path: Path to input audio file
        speed_factor: Speed multiplier (e.g., 1.2 for 20% faster)
        output_path: Path for output audio file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not FFMPEG_PATH or not os.path.exists(FFMPEG_PATH):
            raise FileNotFoundError("ffmpeg executable not found")
        # Enhanced audio processing with quality preservation filters
        cmd = [
            FFMPEG_PATH, '-i', audio_path, 
            '-filter:a', f'atempo={speed_factor},highpass=f=80,lowpass=f=8000,dynaudnorm=p=0.9:s=5',
            '-ar', '24000',  # Ensure consistent sample rate
            '-ac', '2',      # Ensure stereo output
            '-b:a', '128k',  # Set audio bitrate for quality
            '-y', output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except Exception as e:
        print(f"Error speeding up audio: {e}")
        return False


def combine_video_audio(video_path: str, audio_path: str, output_path: str, video_duration: float, audio_duration: float) -> Dict[str, Any]:
    """
    Combine video with audio using ffmpeg, replacing original audio with TTS audio.

    Args:
        video_path: Path to input video file
        audio_path: Path to input audio file
        output_path: Path for output video file
        video_duration: Duration of the video in seconds
        audio_duration: Duration of the audio in seconds

    Returns:
        dict: A dictionary containing the status and an error message if applicable.
    """
    try:
        if not FFMPEG_PATH or not os.path.exists(FFMPEG_PATH):
            raise FileNotFoundError("ffmpeg executable not found")

        # Calculate optimal audio start time to center audio in video
        if audio_duration >= video_duration:
            # If audio is longer than or equal to video, start from beginning
            audio_start_time = 0.0
        else:
            # Center the audio in the video
            audio_start_time = (video_duration - audio_duration) / 2

        # Create a temporary audio file with proper timing
        temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name

        # Add silence before and after the audio to center it and match video duration
        silence_before = audio_start_time
        silence_after = video_duration - audio_duration - silence_before

        if silence_after < 0:
            silence_after = 0

        # Create audio with proper timing using ffmpeg with consistent sample rate
        audio_cmd = [
            FFMPEG_PATH, '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=24000:duration={silence_before}',
            '-i', audio_path,
            '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=24000:duration={silence_after}',
            '-filter_complex', '[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]',
            '-map', '[out]', '-t', str(video_duration),
            '-ar', '24000',  # Ensure consistent sample rate
            '-y', temp_audio_path
        ]

        result = subprocess.run(audio_cmd, capture_output=True, text=True, check=True)

        # Combine video with the timed audio with enhanced audio quality
        cmd = [
            FFMPEG_PATH, '-i', video_path, '-i', temp_audio_path,
            '-c:v', 'copy', '-c:a', 'aac',
            '-b:a', '128k',  # Set audio bitrate for quality
            '-ar', '24000',  # Ensure consistent sample rate
            '-ac', '2',      # Ensure stereo output
            '-map', '0:v:0', '-map', '1:a:0',
            '-shortest',
            '-y', output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Clean up temporary audio file
        try:
            os.unlink(temp_audio_path)
        except:
            pass

        return {"status": "success"}

    except subprocess.CalledProcessError as e:
        error_message = f"Failed to combine video and audio. FFmpeg stderr: {e.stderr}"
        logger.error(f"Error combining video and audio: {e}")
        logger.error(f"FFmpeg stderr: {e.stderr}")
        return {"status": "error", "message": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred during video-audio combination: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "message": error_message}


def get_tts_video(video_url: str, speaker_id: str, text: str, can_summarize: bool = False) -> Dict[str, Any]:
    """
    Generate a TTS voiceover for the given video and return a video URL with the audio applied.
    Audio will be automatically centered in the video.
    
    Args:
        video_url: URL of the source video
        speaker_id: ID of the speaker to use for TTS
        text: Text to convert to speech
        can_summarize: Whether to summarize the text when audio is too long
    
    Returns:
        dict: JSON response with status, data (tts_video_url), and message
    """
    temp_files = []
    
    try:
        # Download the source video
        download_result = download_video_from_url(video_url)
        if download_result["status"] == "error":
            return download_result
        
        video_path = download_result["data"]["file_path"]
        temp_files.append(video_path)
        
        # Get video duration
        try:
            _, _, fps, frame_count = get_video_info(video_path)
            video_duration = frame_count / fps if fps > 0 else 0
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"Error getting video info: {str(e)}"
            }
        
        # Generate TTS audio
        audio_data = tts(text, speaker_id)
        if not audio_data:
            return {
                "status": "error",
                "data": None,
                "message": "Failed to generate TTS audio"
            }

        # Save audio to temporary file
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        temp_files.append(audio_path)

        with open(audio_path, 'wb') as f:
            f.write(audio_data)

        # Get audio duration
        audio_duration = get_audio_duration(audio_path)

        final_audio_path = audio_path
        current_text = text

        # Check if audio duration exceeds video duration
        if audio_duration > video_duration:
            # First, try speeding up audio (capped at 1.2x)
            logger.info(f'[Audio length: {audio_duration}]Audio duration exceeds video duration, attempting to speed up audio')
            speed_factor = 1.1

            # Apply speed-up if factor is greater than 1.0
            if speed_factor > 1.0:
                sped_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
                temp_files.append(sped_audio_path)

                if speed_up_audio(audio_path, speed_factor, sped_audio_path):
                    final_audio_path = sped_audio_path
                    audio_duration = get_audio_duration(sped_audio_path)
                    logger.info(f'Speeded up audio duration: {audio_duration:.3f}s with factor {speed_factor:.3f}')
            else:
                logger.info(f'Audio duration difference is minimal ({required_speed:.3f}), skipping speed-up')

            # If still exceeds video duration after speeding up
            if audio_duration > video_duration:
                if can_summarize:
                    # Use seed16 to summarize the text
                    messages = [{
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes text to make it shorter while keeping the main message.Please give the response directly don't add on other comments or explanations.Must be short than the original text. Could delete some content"
                    },{
                        "role": "user",
                        "content": f"Please summarize the following text to make it shorter while keeping the main message: {text}"
                    }]

                    summary_result = process_vlm_task(messages)
                    if summary_result["status"] == "success":
                        summarized_text = summary_result["data"]["response"]
                        logger.info(f'Summarized_text: {summarized_text}')

                        # Generate new TTS with summarized text
                        new_audio_data = tts(summarized_text, speaker_id)
                        if new_audio_data:
                            new_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
                            temp_files.append(new_audio_path)

                            with open(new_audio_path, 'wb') as f:
                                f.write(new_audio_data)

                            final_audio_path = new_audio_path
                            current_text = summarized_text
                            audio_duration = get_audio_duration(new_audio_path)

                            # Check if summarized audio still exceeds video duration
                            if audio_duration > video_duration:
                                return {
                                    "status": "error",
                                    "data": None,
                                    "message": f"Audio duration ({audio_duration:.2f}s) still exceeds video duration ({video_duration:.2f}s) even after summarization"
                                }
                else:
                    return {
                        "status": "error",
                        "data": None,
                        "message": f"Audio duration ({audio_duration:.2f}s) exceeds video duration ({video_duration:.2f}s) and summarization is not enabled"
                    }

        # Combine video and audio
        output_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        temp_files.append(output_video_path)

        combine_result = combine_video_audio(video_path, final_audio_path, output_video_path, video_duration, get_audio_duration(final_audio_path))
        if combine_result["status"] == "error":
            return {
                "status": "error",
                "data": None,
                "message": combine_result.get("message", "Failed to combine video with audio")
            }

        # Upload result to TOS
        upload_result = upload_to_tos(output_video_path)
        if upload_result["status"] == "error":
            return upload_result

        return {
            "status": "success",
            "data": {"tts_video_url": upload_result["data"]["url"]},
            "message": f"TTS video generated successfully with text: {current_text[:50]}..."
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error generating TTS video: {str(e)}"
        }
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Failed to clean up temporary file {temp_file}: {e}")


def tts(text: str, speaker_id: str):
    """
    Synthesizes speech from text using a pre-defined voice.

    Args:
        text: The text to synthesize.
        speaker_id: The speaker ID to use for TTS.

    Returns:
        The synthesized audio data as a byte array.
    """
    app_id = os.environ.get("TTS_APP_KEY")
    access_key = os.environ.get("TTS_ACCESS_KEY")
    resource_id = os.environ.get("RESOURCE_ID")
    speaker = speaker_id

    if not app_id or not access_key or not resource_id:
        return None

    url = "https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/unidirectional"

    headers = {
        "X-Api-App-Id": app_id,
        "X-Api-Access-Key": access_key,
        "X-Api-Resource-Id": resource_id,
        "X-Api-App-Key": "aGjiRDfUWi",
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }

    additions = {
        "disable_markdown_filter": True,
        "enable_language_detector": True,
        "enable_latex_tn": True,
        "disable_default_bit_rate": True,
        "max_length_to_filter_parenthesis": 0,
        "cache_config": {
            "text_type": 1,
            "use_cache": True
        }
    }

    additions_json = json.dumps(additions)

    payload = {
        "user": {"uid": "12345"},
        "req_params": {
            "text": text,
            "speaker": speaker,
            "additions": additions_json,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000
            }
        }
    }
    session = requests.Session()
    response = None
    try:
        response = session.post(url, headers=headers, json=payload, stream=True)

        audio_data = bytearray()
        for chunk in response.iter_lines(decode_unicode=True):
            if not chunk:
                continue
            data = json.loads(chunk)
            if data.get("code", 0) == 0 and "data" in data and data["data"]:
                chunk_audio = base64.b64decode(data["data"])
                audio_data.extend(chunk_audio)
            if data.get("code", 0) == 20000000:
                break
            if data.get("code", 0) > 0:
                print(f"error response:{data}")
                break

        return audio_data

    except Exception as e:
        print(f"request error: {e}")
        return None
    finally:
        if response:
            response.close()
        session.close()


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()
    # Example usage:
    output_dir = "tts_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Test get_voice_speaker
    speakers = get_voice_speaker("English", "Female")
    print("Available speakers:", speakers)

    # Test TTS generation
    print('')
    for voice in VOICE_MAP:
        audio = tts("This is a test.", voice["speaker_id"])
        if audio:
            with open(os.path.join(output_dir, f"{voice['voice']}.mp3"), "wb") as f:
                f.write(audio)

        break

    # video URL for testing
    video_url = 'https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4'
    res = get_tts_video(
        video_url=video_url,
        speaker_id='zh_female_shaoergushi_mars_bigtts',
        text="I love dance, dance dance.I love dance, dance dance.I love dance, dance dance.I love dance, dance dance.I love dance, dance dance.",
        can_summarize=True
    )

    print(res)