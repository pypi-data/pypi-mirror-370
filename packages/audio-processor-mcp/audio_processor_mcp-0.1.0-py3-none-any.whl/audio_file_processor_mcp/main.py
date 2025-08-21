from mcp.server.fastmcp import FastMCP, Context
import ffmpeg
import os # For checking file existence if needed, though ffmpeg handles it
import shutil # For cleaning up temporary directories
import logging
from logging.handlers import RotatingFileHandler

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)          # 防止 basicConfig 被早期初始化抵消
file_handler = RotatingFileHandler("debug.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.propagate = False  

FFMPEG_PATH_DIR = os.environ.get('FFMPEG_PATH')

def _resolve_binary(explicit_bin: str | None, path_dir: str | None, base_name: str) -> str:
    if explicit_bin:
        return explicit_bin
    if path_dir:
        candidate_names = [base_name]
        if os.name == 'nt':  # Windows prefers .exe
            candidate_names = [f"{base_name}.exe", base_name]
        for name in candidate_names:
            candidate_path = os.path.join(path_dir, name)
            if os.path.exists(candidate_path):
                return candidate_path
    which_path = shutil.which(base_name)
    if which_path:
        return which_path
    # Fallback to base name; may still work if OS can resolve via PATHEXT
    return base_name

FFMPEG_BIN = _resolve_binary(os.environ.get('FFMPEG_BIN'), FFMPEG_PATH_DIR, 'ffmpeg')
FFPROBE_BIN = _resolve_binary(os.environ.get('FFPROBE_BIN'), FFMPEG_PATH_DIR, 'ffprobe')
# Configure ffmpeg-python to use the resolved binaries
os.environ['FFMPEG_BINARY'] = FFMPEG_BIN
os.environ['FFPROBE_BINARY'] = FFPROBE_BIN

# --- ffmpeg/ffprobe helpers that always use resolved binaries ---
def _ffmpeg_run(stream_spec, **kwargs):
    """Run ffmpeg with an explicit binary path to avoid env propagation issues."""
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BIN, **kwargs)

def _ffprobe_probe(path: str, **kwargs):
    """Probe media with explicit ffprobe binary."""
    return ffmpeg.probe(path, cmd=FFPROBE_BIN, **kwargs)

# Create an MCP server instance
mcp = FastMCP("AudioProcessing")


@mcp.tool()
def convert_audio_properties(
    input_audio_path: str,
    output_audio_path: str,
    target_format: str,
    bitrate: str | None = None,
    sample_rate: int | None = None,
    channels: int | None = None,
    sample_format: str | None = None,
) -> str:
    """Convert audio format and properties (bitrate/sample_rate/channels). WAV doesn't support bitrate, use sample_format instead.

    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the converted audio file.
        target_format: Desired output audio format (e.g., 'mp3', 'wav', 'aac').
        bitrate: Target audio bitrate (e.g., '128k', '192k'). Optional. Not applicable to WAV/PCM.
        sample_rate: Target audio sample rate in Hz (e.g., 44100, 48000). Optional.
        channels: Number of audio channels (1 for mono, 2 for stereo). Optional.
        sample_format: For WAV/PCM, choose sample format such as 's16'|'s24'|'s32'|'flt'. Optional.
    Returns:
        A status message indicating success or failure.
    """
    try:
        # Check if output file already exists
        if os.path.exists(output_audio_path):
            raise RuntimeError(f"Error: Output file already exists at {output_audio_path}. Please choose a different path or delete the existing file.")
        
        stream = ffmpeg.input(input_audio_path)
        kwargs: dict = {}

        tgt_fmt = (target_format or "").lower()
        is_wav = tgt_fmt in {"wav", "wave"} or output_audio_path.lower().endswith(".wav")

        if is_wav and bitrate:
            raise RuntimeError("Error: WAV/PCM doesn't support bitrate; please use sample_format (e.g., 's16'/'s24'/'s32'/'flt')")

        # 通用属性
        if sample_rate:
            kwargs["ar"] = sample_rate
        if channels:
            kwargs["ac"] = channels
        kwargs["format"] = target_format

        # Sample format/encoder mapping for WAV
        if is_wav and sample_format:
            sf = sample_format.lower()
            pcm_map = {
                "s16": "pcm_s16le",
                "s24": "pcm_s24le",
                "s32": "pcm_s32le",
                "flt": "pcm_f32le",
            }
            if sf in pcm_map:
                kwargs["acodec"] = pcm_map[sf]
            else:
                # Pass sample_fmt directly, let ffmpeg decide appropriate pcm_*
                kwargs["sample_fmt"] = sf
        else:
            # Non-WAV formats support bitrate
            if bitrate:
                kwargs["audio_bitrate"] = bitrate

        output_stream = stream.output(output_audio_path, **kwargs)
        _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)
        return f"Audio converted successfully to {output_audio_path} with format {target_format} and specified properties."
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        logger.error(f"FFmpeg error in convert_audio_properties: {error_message}")
        raise RuntimeError(f"Error converting audio properties: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in convert_audio_properties: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in convert_audio_properties: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


# --- Granular Audio Property Tools ---
@mcp.tool()
def convert_audio_format(input_audio_path: str, output_audio_path: str, target_format: str) -> str:
    """Converts an audio file to the specified target format with appropriate codec.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the converted audio file.
        target_format: Desired output audio format (e.g., 'mp3', 'wav', 'aac', 'm4a', 'wma', 'flac', 'ogg').
    Returns:
        A status message indicating success or failure.
    """
    try:
        # Check if output file already exists
        if os.path.exists(output_audio_path):
            raise RuntimeError(f"Error: Output file already exists at {output_audio_path}. Please choose a different path or delete the existing file.")
        
        # Format to codec mapping
        format_codec_map = {
            'mp3': 'libmp3lame',
            'aac': 'aac',
            'm4a': 'aac',  # M4A typically uses AAC codec
            'wma': 'wmav2',  # Windows Media Audio v2
            'wav': 'pcm_s16le',  # WAV with 16-bit PCM
            'flac': 'flac',
            'ogg': 'libvorbis',
            'opus': 'libopus'
        }
        
        # Get appropriate codec for the target format
        codec = format_codec_map.get(target_format.lower())
        
        # Build output parameters
        output_params = {}
        
        if codec:
            output_params['acodec'] = codec
            
        # Special container format handling
        if target_format.lower() == 'm4a':
            output_params['f'] = 'mp4'  # M4A is AAC in MP4 container
        elif target_format.lower() == 'aac':
            output_params['f'] = 'adts'  # AAC files use ADTS container
        elif target_format.lower() == 'wma':
            output_params['f'] = 'asf'  # WMA is in ASF container
        # For other formats, use the target_format as container format
        else:
            output_params['f'] = target_format.lower()
        
        # Convert the audio
        stream = ffmpeg.input(input_audio_path)
        output_stream = stream.output(output_audio_path, **output_params)
        _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)
        
        return f"Audio format converted to {target_format} and saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        logger.error(f"FFmpeg error in convert_audio_format: {error_message}")
        raise RuntimeError(f"Error converting audio format: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in convert_audio_format: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in convert_audio_format: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

@mcp.tool()
def set_audio_bitrate(input_audio_path: str, output_audio_path: str, bitrate: str) -> str:
    """Sets the bitrate for an audio file with appropriate codec selection.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new bitrate.
        bitrate: Target audio bitrate (e.g., '128k', '192k', '320k').
    Returns:
        A status message indicating success or failure.
    """
    try:
        # Check if output file already exists
        if os.path.exists(output_audio_path):
            raise RuntimeError(f"Error: Output file already exists at {output_audio_path}. Please choose a different path or delete the existing file.")
        
        # Validate bitrate format
        import re
        if not re.match(r'^\d+[kmKM]?$', bitrate):
            raise RuntimeError(f"Error: Invalid bitrate format '{bitrate}'. Use format like '128k', '192k', '320k'")
        
        # Check if output format supports bitrate
        lossless_extensions = ['.wav', '.flac', '.ape', '.alac']
        output_ext = os.path.splitext(output_audio_path)[1].lower()
        
        if output_ext in lossless_extensions:
            raise RuntimeError(f"Error: {output_ext.upper()} format doesn't support bitrate; please use convert_audio_properties with sample_format instead")

        # Determine appropriate codec based on output format
        format_codec_map = {
            '.mp3': 'libmp3lame',
            '.aac': 'aac',
            '.m4a': 'aac',
            '.wma': 'wmav2',
            '.ogg': 'libvorbis',
            '.opus': 'libopus'
        }
        
        output_params = {'audio_bitrate': bitrate}
        
        # Add codec if we have a mapping for this format
        if output_ext in format_codec_map:
            output_params['acodec'] = format_codec_map[output_ext]
        
        # Special container format handling
        if output_ext == '.m4a':
            output_params['f'] = 'mp4'
        elif output_ext == '.wma':
            output_params['f'] = 'asf'

        _ffmpeg_run(ffmpeg.input(input_audio_path).output(output_audio_path, **output_params), capture_stdout=True, capture_stderr=True)
        return f"Audio bitrate set to {bitrate} and saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        logger.error(f"FFmpeg error in set_audio_bitrate: {error_message}")
        raise RuntimeError(f"Error setting audio bitrate: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in set_audio_bitrate: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in set_audio_bitrate: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

@mcp.tool()
def set_audio_sample_rate(input_audio_path: str, output_audio_path: str, sample_rate: int) -> str:
    """Sets the sample rate for an audio file.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new sample rate.
        sample_rate: Target audio sample rate in Hz (e.g., 44100, 48000).
    Returns:
        A status message indicating success or failure.
    """
    try:
        # Check if output file already exists
        if os.path.exists(output_audio_path):
            raise RuntimeError(f"Error: Output file already exists at {output_audio_path}. Please choose a different path or delete the existing file.")
        
        # Validate input file exists
        if not os.path.exists(input_audio_path):
            raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
        
        # Validate sample rate
        if sample_rate <= 0 or sample_rate > 384000:  # Reasonable upper limit
            raise RuntimeError(f"Error: Invalid sample rate {sample_rate}. Must be between 1 and 384000 Hz")
        
        # Common sample rates validation
        common_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 384000]
        if sample_rate not in common_rates:
            logger.warning(f"Uncommon sample rate {sample_rate} Hz specified. Common rates are: {common_rates}")
        
        _ffmpeg_run(ffmpeg.input(input_audio_path).output(output_audio_path, ar=sample_rate), capture_stdout=True, capture_stderr=True)
        return f"Audio sample rate set to {sample_rate} Hz and saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        logger.error(f"FFmpeg error in set_audio_sample_rate: {error_message}")
        raise RuntimeError(f"Error setting audio sample rate: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in set_audio_sample_rate: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in set_audio_sample_rate: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

@mcp.tool()
def set_audio_channels(input_audio_path: str, output_audio_path: str, channels: int) -> str:
    """Sets the number of channels for an audio file (1 for mono, 2 for stereo, etc.).
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new channel layout.
        channels: Number of audio channels (1=mono, 2=stereo, 6=5.1, 8=7.1).
    Returns:
        A status message indicating success or failure.
    """
    try:
        # Check if output file already exists
        if os.path.exists(output_audio_path):
            raise RuntimeError(f"Error: Output file already exists at {output_audio_path}. Please choose a different path or delete the existing file.")
        
        # Validate input file exists
        if not os.path.exists(input_audio_path):
            raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
        
        # Validate channel count
        if channels <= 0 or channels > 32:  # Reasonable upper limit
            raise RuntimeError(f"Error: Invalid channel count {channels}. Must be between 1 and 32")
        
        # Common channel configurations
        channel_descriptions = {
            1: "mono",
            2: "stereo", 
            3: "3.0 (L, R, C)",
            4: "4.0 surround", 
            5: "5.0 surround",
            6: "5.1 surround",
            7: "7.0 surround",
            8: "7.1 surround"
        }
        
        description = channel_descriptions.get(channels, f"{channels}-channel")
        logger.info(f"Converting to {description} audio")
        
        _ffmpeg_run(ffmpeg.input(input_audio_path).output(output_audio_path, ac=channels), capture_stdout=True, capture_stderr=True)
        return f"Audio channels set to {channels} ({description}) and saved to {output_audio_path}"
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        logger.error(f"FFmpeg error in set_audio_channels: {error_message}")
        raise RuntimeError(f"Error setting audio channels: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in set_audio_channels: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in set_audio_channels: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def get_audio_info(audio_path: str) -> str:
    """Get detailed information about an audio file using ffprobe.
    
    Args:
        audio_path: Path to the audio file to analyze.
        
    Returns:
        A JSON string containing detailed audio file information including format, streams, metadata, etc.
    """
    try:
        if not os.path.exists(audio_path):
            raise RuntimeError(f"Error: Audio file not found at {audio_path}")
            
        # Use ffprobe to get detailed information
        # Note: ffmpeg.probe already returns JSON by default, so we don't need print_format='json'
        info = _ffprobe_probe(audio_path)
        
        # Extract key information for better readability
        format_info = info.get('format', {})
        streams = info.get('streams', [])
        
        # Find audio stream
        audio_stream = None
        for stream in streams:
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        # Build a summary with consistent format
        audio_data = {
            'file_path': audio_path,
            'format': {
                'format_name': format_info.get('format_name', 'Unknown'),
                'duration': format_info.get('duration', 'Unknown'),
                'size': format_info.get('size', 'Unknown'),
                'bit_rate': format_info.get('bit_rate', 'Unknown'),
                'tags': format_info.get('tags', {})
            },
            'audio_stream': {
                'codec_name': audio_stream.get('codec_name', 'Unknown') if audio_stream else 'No audio stream',
                'codec_long_name': audio_stream.get('codec_long_name', 'Unknown') if audio_stream else 'No audio stream',
                'sample_rate': audio_stream.get('sample_rate', 'Unknown') if audio_stream else 'No audio stream',
                'channels': audio_stream.get('channels', 'Unknown') if audio_stream else 'No audio stream',
                'channel_layout': audio_stream.get('channel_layout', 'Unknown') if audio_stream else 'No audio stream',
                'bit_rate': audio_stream.get('bit_rate', 'Unknown') if audio_stream else 'No audio stream',
                'sample_fmt': audio_stream.get('sample_fmt', 'Unknown') if audio_stream else 'No audio stream'
            } if audio_stream else None,
            'raw_info': info  # Include full raw information
        }
        
        # Return with consistent format including isError field
        summary = {
            'isError': False,
            'data': audio_data
        }
        
        return json.dumps(summary, indent=2, ensure_ascii=False)
        
    except ffmpeg.Error as e:
        stderr_output = e.stderr.decode('utf8') if e.stderr else "No stderr output"
        error_message = f"ffprobe failed. Command: {e.cmd}. Return code: {e.returncode}. Stderr: {stderr_output}."
        logger.error(f"FFmpeg error in get_audio_info: {error_message}")
        raise RuntimeError(f"Error getting audio info: ffprobe failed - {stderr_output}")
    except FileNotFoundError:
        logger.error(f"File not found in get_audio_info: {audio_path}")
        raise RuntimeError(f"Error: Audio file not found at {audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in get_audio_info: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred in get_audio_info: {str(e)}")


def main():
    """Main entry point for the MCP server."""
    mcp.run()

# Main execution block to run the server
if __name__ == "__main__":
    main() 