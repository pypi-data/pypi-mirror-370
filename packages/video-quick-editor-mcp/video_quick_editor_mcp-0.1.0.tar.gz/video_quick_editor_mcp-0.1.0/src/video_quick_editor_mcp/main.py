from mcp.server.fastmcp import FastMCP, Context
import ffmpeg
import os
import re
import tempfile
import shutil
import subprocess
import logging
from logging.handlers import RotatingFileHandler

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
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
        if os.name == 'nt':
            candidate_names = [f"{base_name}.exe", base_name]
        for name in candidate_names:
            candidate_path = os.path.join(path_dir, name)
            if os.path.exists(candidate_path):
                return candidate_path
    which_path = shutil.which(base_name)
    if which_path:
        return which_path
    return base_name

FFMPEG_BIN = _resolve_binary(os.environ.get('FFMPEG_BIN'), FFMPEG_PATH_DIR, 'ffmpeg')
FFPROBE_BIN = _resolve_binary(os.environ.get('FFPROBE_BIN'), FFMPEG_PATH_DIR, 'ffprobe')
os.environ['FFMPEG_BINARY'] = FFMPEG_BIN
os.environ['FFPROBE_BINARY'] = FFPROBE_BIN

def _ffmpeg_run(stream_spec, **kwargs):
    if 'overwrite_output' not in kwargs:
        kwargs['overwrite_output'] = True
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BIN, **kwargs)

def _ffmpeg_run_async(stream_spec, **kwargs):
    return ffmpeg.run_async(stream_spec, cmd=FFMPEG_BIN, **kwargs)

def _ffprobe_probe(path: str, **kwargs):
    return ffmpeg.probe(path, cmd=FFPROBE_BIN, **kwargs)

def _parse_time_to_seconds(time_str: str) -> float:
    if isinstance(time_str, (int, float)):
        return float(time_str)
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    return float(time_str)

def _get_media_properties(media_path: str) -> dict:
    try:
        probe = _ffprobe_probe(media_path)
        video_stream_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        audio_stream_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

        props = {
            'duration': float(probe['format'].get('duration', 0.0)),
            'has_video': video_stream_info is not None,
            'has_audio': audio_stream_info is not None,
            'width': int(video_stream_info['width']) if video_stream_info and 'width' in video_stream_info else 0,
            'height': int(video_stream_info['height']) if video_stream_info and 'height' in video_stream_info else 0,
            'avg_fps': 0,
            'sample_rate': int(audio_stream_info['sample_rate']) if audio_stream_info and 'sample_rate' in audio_stream_info else 44100,
            'channels': int(audio_stream_info['channels']) if audio_stream_info and 'channels' in audio_stream_info else 2,
            'channel_layout': audio_stream_info.get('channel_layout', 'stereo') if audio_stream_info else 'stereo'
        }
        if video_stream_info and 'avg_frame_rate' in video_stream_info and video_stream_info['avg_frame_rate'] != '0/0':
            num, den = map(int, video_stream_info['avg_frame_rate'].split('/'))
            if den > 0:
                props['avg_fps'] = num / den
            else:
                props['avg_fps'] = 30
        else:
            props['avg_fps'] = 30
        return props
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error probing file {media_path}: {e.stderr.decode('utf8') if e.stderr else str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error probing file {media_path}: {str(e)}")

mcp = FastMCP("VideoEditServer")

@mcp.tool()
def change_aspect_ratio(video_path: str, output_video_path: str, target_aspect_ratio: str,
                        resize_mode: str = 'pad', padding_color: str = 'black') -> str:
    """调整视频的画面纵横比。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        target_aspect_ratio: 目标纵横比字符串，格式 '宽:高'（如 '16:9'、'4:3'、'1:1'）。
        resize_mode: 调整模式，'pad' 表示等比缩放并补边，'crop' 表示居中裁剪以适配。
        padding_color: 当使用 'pad' 时的补边颜色（例如 'black'、'white'、'#RRGGBB'）。

    Returns:
        A status message indicating success or failure.
    """
    try:
        probe = _ffprobe_probe(video_path)
        video_stream_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if not video_stream_info:
            raise RuntimeError("Error: No video stream found in the input file.")

        original_width = int(video_stream_info['width'])
        original_height = int(video_stream_info['height'])

        num, den = map(int, target_aspect_ratio.split(':'))
        target_ar_val = num / den
        original_ar_val = original_width / original_height

        vf_filter = ""

        if resize_mode == 'pad':
            if abs(original_ar_val - target_ar_val) < 1e-4:
                try:
                    _ffmpeg_run(ffmpeg.input(video_path).output(output_video_path, c='copy'), capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Copied to {output_video_path}."
                except ffmpeg.Error:
                    _ffmpeg_run(ffmpeg.input(video_path).output(output_video_path), capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Re-encoded to {output_video_path}."

            if original_ar_val > target_ar_val:
                final_w = int(original_height * target_ar_val)
                final_h = original_height
                vf_filter = f"scale={final_w}:{final_h}:force_original_aspect_ratio=decrease,pad={final_w}:{final_h}:(ow-iw)/2:(oh-ih)/2:{padding_color}"
            else:
                final_w = original_width
                final_h = int(original_width / target_ar_val)
                vf_filter = f"scale={final_w}:{final_h}:force_original_aspect_ratio=decrease,pad={final_w}:{final_h}:(ow-iw)/2:(oh-ih)/2:{padding_color}"

        elif resize_mode == 'crop':
            if abs(original_ar_val - target_ar_val) < 1e-4:
                try:
                    _ffmpeg_run(ffmpeg.input(video_path).output(output_video_path, c='copy'), capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Copied to {output_video_path}."
                except ffmpeg.Error:
                    _ffmpeg_run(ffmpeg.input(video_path).output(output_video_path), capture_stdout=True, capture_stderr=True)
                    return f"Video aspect ratio already matches. Re-encoded to {output_video_path}."

            if original_ar_val > target_ar_val:
                new_width = int(original_height * target_ar_val)
                vf_filter = f"crop={new_width}:{original_height}:(iw-{new_width})/2:0"
            else:
                new_height = int(original_width / target_ar_val)
                vf_filter = f"crop={original_width}:{new_height}:0:(ih-{new_height})/2"
        else:
            raise RuntimeError(f"Error: Invalid resize_mode '{resize_mode}'. Must be 'pad' or 'crop'.")

        try:
            _ffmpeg_run(ffmpeg.input(video_path).output(output_video_path, vf=vf_filter, vcodec='libx264', pix_fmt='yuv420p', acodec='copy'), capture_stdout=True, capture_stderr=True)
            return f"Video aspect ratio changed (audio copy) to {target_aspect_ratio} using {resize_mode}. Saved to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                _ffmpeg_run(ffmpeg.input(video_path).output(output_video_path, vf=vf_filter, vcodec='libx264', pix_fmt='yuv420p'), capture_stdout=True, capture_stderr=True)
                return f"Video aspect ratio changed (audio re-encoded) to {target_aspect_ratio} using {resize_mode}. Saved to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode_all.stderr.decode('utf8') if e_recode_all.stderr else str(e_recode_all)
                raise RuntimeError(f"Error changing aspect ratio. Audio copy attempt failed: {err_acopy_msg}. Full re-encode attempt also failed: {err_recode_msg}.")
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error changing aspect ratio: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: Input video file not found at {video_path}")
    except ValueError:
        raise RuntimeError(f"Error: Invalid target_aspect_ratio format. Expected 'num:den' (e.g., '16:9').")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

@mcp.tool()
def add_subtitles(video_path: str, srt_file_path: str, output_video_path: str, font_style: dict = None) -> str:
    """将 SRT 字幕烧录到视频上。

    Args:
        video_path: 输入视频文件路径。
        srt_file_path: 字幕文件路径（SRT 格式）。
        output_video_path: 输出视频文件路径。
        font_style: 字幕样式配置字典（可选）。支持键：
            - font_name: 字体名（如 'Arial'）。
            - font_size: 字号（整数）。
            - font_color: 主颜色（如 'white' 或 ASS 颜色值）。
            - outline_color: 描边颜色。
            - outline_width: 描边宽度（整数）。
            - shadow_color: 阴影颜色。
            - alignment: 对齐方式（ASS 对齐值，1~9）。
            - margin_v/margin_l/margin_r: 边距（整数）。

    Returns:
        A status message indicating success or failure.
    """
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        if not os.path.exists(srt_file_path):
            raise RuntimeError(f"Error: SRT subtitle file not found at {srt_file_path}")

        input_stream = ffmpeg.input(video_path)
        style_args = []
        if font_style:
            if 'font_name' in font_style: style_args.append(f"FontName={font_style['font_name']}")
            if 'font_size' in font_style: style_args.append(f"FontSize={font_style['font_size']}")
            if 'font_color' in font_style: style_args.append(f"PrimaryColour={font_style['font_color']}")
            if 'outline_color' in font_style: style_args.append(f"OutlineColour={font_style['outline_color']}")
            if 'outline_width' in font_style: style_args.append(f"Outline={font_style['outline_width']}")
            if 'shadow_color' in font_style: style_args.append(f"ShadowColour={font_style['shadow_color']}")
            if 'shadow_offset_x' in font_style or 'shadow_offset_y' in font_style:
                shadow_val = font_style.get('shadow_offset_x', font_style.get('shadow_offset_y', 1))
                style_args.append(f"Shadow={shadow_val}")
            if 'alignment' in font_style: style_args.append(f"Alignment={font_style['alignment']}")
            if 'margin_v' in font_style: style_args.append(f"MarginV={font_style['margin_v']}")
            if 'margin_l' in font_style: style_args.append(f"MarginL={font_style['margin_l']}")
            if 'margin_r' in font_style: style_args.append(f"MarginR={font_style['margin_r']}")

        safe_srt_path = srt_file_path.replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:')
        vf_filter_value = f"subtitles='{safe_srt_path}'"
        if style_args:
            vf_filter_value += f":force_style='{','.join(style_args)}'"

        output_stream = input_stream.output(
            output_video_path,
            vf=vf_filter_value,
            vcodec='libx264',
            pix_fmt='yuv420p',
            acodec='copy'
        )
        try:
            _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)
            return f"Subtitles added successfully (audio copied) to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            output_stream_recode_audio = input_stream.output(
                output_video_path,
                vf=vf_filter_value,
                vcodec='libx264',
                pix_fmt='yuv420p',
                acodec='aac'
            )
            try:
                _ffmpeg_run(output_stream_recode_audio, capture_stdout=True, capture_stderr=True)
                return f"Subtitles added successfully (audio re-encoded) to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode_all.stderr.decode('utf8') if e_recode_all.stderr else str(e_recode_all)
                raise RuntimeError(f"Error adding subtitles. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}")
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error adding subtitles: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: A specified file was not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

@mcp.tool()
def add_text_overlay(video_path: str, output_video_path: str, text_elements: list[dict]) -> str:
    """为视频添加按时间区间显示的文本叠加。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        text_elements: 文本元素列表，每个元素为字典，常见键：
            - text: 文本内容（必填）。
            - start_time/end_time: 起止时间（秒或 'HH:MM:SS'）。
            - font_size: 字号（整数，默认 24）。
            - font_color: 字体颜色（默认 'white'）。
            - x_pos/y_pos: 位置表达式或像素（默认居中/底部上方）。
            - box: 是否显示背景框（布尔）。
            - box_color/box_border_width: 背景框颜色与边框宽度。
            - font_file: 字体文件路径（可选）。

    Returns:
        A status message indicating success or failure.
    """
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        if not text_elements:
            raise RuntimeError("Error: No text elements provided for overlay.")

        input_stream = ffmpeg.input(video_path)
        drawtext_filters = []

        for element in text_elements:
            text = element.get('text')
            start_time = element.get('start_time')
            end_time = element.get('end_time')
            if text is None or start_time is None or end_time is None:
                raise RuntimeError(f"Error: Text element is missing required keys (text, start_time, end_time).")
            safe_text = text.replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
            # 将时间统一转换为秒
            start_sec = _parse_time_to_seconds(start_time)
            end_sec = _parse_time_to_seconds(end_time)

            filter_params = [
                f"text='{safe_text}'",
                f"fontsize={element.get('font_size', 24)}",
                f"fontcolor={element.get('font_color', 'white')}",
                f"x={element.get('x_pos', '(w-text_w)/2')}",
                f"y={element.get('y_pos', 'h-text_h-10')}",
                f"enable=between(t\\,{start_sec}\\,{end_sec})"
            ]
            if element.get('box', False):
                filter_params.append("box=1")
                filter_params.append(f"boxcolor={element.get('box_color', 'black@0.5')}")
                if 'box_border_width' in element:
                    filter_params.append(f"boxborderw={element['box_border_width']}")
            if 'font_file' in element:
                font_path = element['font_file'].replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:')
                filter_params.append(f"fontfile='{font_path}'")
            drawtext_filter = f"drawtext={':'.join(filter_params)}"
            drawtext_filters.append(drawtext_filter)

        final_vf_filter = ','.join(drawtext_filters)

        try:
            stream = input_stream.output(
                output_video_path,
                vf=final_vf_filter,
                vcodec='libx264',
                pix_fmt='yuv420p',
                acodec='copy'
            )
            _ffmpeg_run(stream, capture_stdout=True, capture_stderr=True)
            return f"Text overlays added successfully to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                stream_recode = input_stream.output(
                    output_video_path,
                    vf=final_vf_filter,
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    acodec='aac'
                )
                _ffmpeg_run(stream_recode, capture_stdout=True, capture_stderr=True)
                return f"Text overlays added successfully to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode_all.stderr.decode('utf8') if e_recode_all.stderr else str(e_recode_all)
                raise RuntimeError(f"Error adding text overlays. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}")
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error processing text overlays: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: Input video file not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

@mcp.tool()
def add_image_overlay(video_path: str, output_video_path: str, image_path: str,
                      position: str = 'top_right', opacity: float = None,
                      start_time: str = None, end_time: str = None,
                      width: str = None, height: str = None) -> str:
    """为视频添加图片叠加（水印/徽标）。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        image_path: 叠加图片路径（支持透明通道）。
        position: 预设位置 'top_left'|'top_right'|'bottom_left'|'bottom_right'|'center'，或 'x=..:y=..' 自定义。
        opacity: 透明度（0.0~1.0）。
        start_time: 生效开始时间（秒或 'HH:MM:SS'）。
        end_time: 生效结束时间（秒或 'HH:MM:SS'）。
        width/height: 目标尺寸（像素或表达式；只设其一时另一边按比例自适应）。

    Returns:
        A status message indicating success or failure.
    """
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        if not os.path.exists(image_path):
            raise RuntimeError(f"Error: Overlay image file not found at {image_path}")

        main_input = ffmpeg.input(video_path)
        overlay_input = ffmpeg.input(image_path)
        processed_overlay = overlay_input

        if width or height:
            # ffmpeg scale 使用 w/h 参数，而非 width/height
            w_val = width if width else '-1'
            h_val = height if height else '-1'
            processed_overlay = processed_overlay.filter('scale', w=w_val, h=h_val)

        if opacity is not None and 0.0 <= opacity <= 1.0:
            processed_overlay = processed_overlay.filter('format', 'rgba')
            processed_overlay = processed_overlay.filter('colorchannelmixer', aa=str(opacity))

        overlay_x_pos = '0'
        overlay_y_pos = '0'
        if position == 'top_left':
            overlay_x_pos, overlay_y_pos = '10', '10'
        elif position == 'top_right':
            overlay_x_pos, overlay_y_pos = 'main_w-overlay_w-10', '10'
        elif position == 'bottom_left':
            overlay_x_pos, overlay_y_pos = '10', 'main_h-overlay_h-10'
        elif position == 'bottom_right':
            overlay_x_pos, overlay_y_pos = 'main_w-overlay_w-10', 'main_h-overlay_h-10'
        elif position == 'center':
            overlay_x_pos, overlay_y_pos = '(main_w-overlay_w)/2', '(main_h-overlay_h)/2'
        elif ':' in position:
            pos_parts = position.split(':')
            for part in pos_parts:
                if part.startswith('x='): overlay_x_pos = part.split('=')[1]
                if part.startswith('y='): overlay_y_pos = part.split('=')[1]

        overlay_filter_kwargs = {'x': overlay_x_pos, 'y': overlay_y_pos}
        if start_time is not None or end_time is not None:
            # 将起止时间转换为秒
            actual_start_sec = _parse_time_to_seconds(start_time) if start_time is not None else 0
            if end_time is not None:
                actual_end_sec = _parse_time_to_seconds(end_time)
                enable_expr = f"between(t,{actual_start_sec},{actual_end_sec})"
            else:
                enable_expr = f"gte(t,{actual_start_sec})"
            overlay_filter_kwargs['enable'] = enable_expr

        try:
            video_with_overlay = ffmpeg.filter([main_input, processed_overlay], 'overlay', **overlay_filter_kwargs)
            # 若输入无音频，则仅输出视频流
            probe = _ffprobe_probe(video_path)
            has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])
            if has_audio:
                output_node = ffmpeg.output(video_with_overlay, main_input.audio, output_video_path, vcodec='libx264', pix_fmt='yuv420p', acodec='copy')
            else:
                output_node = ffmpeg.output(video_with_overlay, output_video_path, vcodec='libx264', pix_fmt='yuv420p')
            _ffmpeg_run(output_node, capture_stdout=True, capture_stderr=True)
            return f"Image overlay added successfully to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                video_with_overlay_fallback = ffmpeg.filter([main_input, processed_overlay], 'overlay', **overlay_filter_kwargs)
                probe = _ffprobe_probe(video_path)
                has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])
                if has_audio:
                    output_node_fallback = ffmpeg.output(video_with_overlay_fallback, main_input.audio, output_video_path, vcodec='libx264', pix_fmt='yuv420p', acodec='aac')
                else:
                    output_node_fallback = ffmpeg.output(video_with_overlay_fallback, output_video_path, vcodec='libx264', pix_fmt='yuv420p')
                _ffmpeg_run(output_node_fallback, capture_stdout=True, capture_stderr=True)
                return f"Image overlay added successfully to {output_video_path}"
            except ffmpeg.Error as e_recode:
                err_acopy_msg = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode_msg = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
                raise RuntimeError(f"Error adding image overlay. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}")
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error processing image overlay: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: An input file was not found (video: '{video_path}', image: '{image_path}'). Please check paths.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in add_image_overlay: {str(e)}")

@mcp.tool()
def concatenate_videos(video_paths: list[str], output_video_path: str,
                       transition_effect: str = None, transition_duration: float = None) -> str:
    """拼接视频序列，并可选两段间的过渡效果。

    Args:
        video_paths: 输入视频路径列表（至少 1 个）。
        output_video_path: 输出视频文件路径。
        transition_effect: 过渡效果（可选）。支持 'dissolve'|'fade'|'wipeleft'|'wiperight'|'wipeup'|'wipedown'|'slideleft'|'slideright'|'slideup'|'slidedown' 等。
        transition_duration: 过渡时长（秒，>0；仅在指定 transition_effect 且两段时有效）。

    Returns:
        A status message indicating success or failure.
    """
    if not video_paths:
        raise RuntimeError("Error: No video paths provided for concatenation.")
    if len(video_paths) < 1:
        raise RuntimeError("Error: At least one video is required.")
    if transition_effect and transition_duration is None:
        raise RuntimeError("Error: transition_duration is required when transition_effect is specified.")
    if transition_effect and transition_duration <= 0:
        raise RuntimeError("Error: transition_duration must be positive.")

    valid_transitions = {
        'dissolve', 'fade', 'fadeblack', 'fadewhite', 'fadegrays', 'distance',
        'wipeleft', 'wiperight', 'wipeup', 'wipedown',
        'slideleft', 'slideright', 'slideup', 'slidedown',
        'smoothleft', 'smoothright', 'smoothup', 'smoothdown',
        'circlecrop', 'rectcrop', 'circleopen', 'circleclose',
        'vertopen', 'vertclose', 'horzopen', 'horzclose',
        'diagtl', 'diagtr', 'diagbl', 'diagbr',
        'hlslice', 'hrslice', 'vuslice', 'vdslice',
        'pixelize', 'radial', 'hblur'
    }
    if transition_effect and transition_effect not in valid_transitions:
        raise RuntimeError(f"Error: Invalid transition_effect '{transition_effect}'. Valid options: {', '.join(sorted(valid_transitions))}")

    for video_path in video_paths:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")

    if len(video_paths) == 1:
        try:
            _ffmpeg_run(ffmpeg.input(video_paths[0]).output(output_video_path, vcodec='libx264', acodec='aac'), capture_stdout=True, capture_stderr=True)
            return f"Single video processed and saved to {output_video_path}"
        except ffmpeg.Error as e:
            raise RuntimeError(f"Error processing single video: {e.stderr.decode('utf8') if e.stderr else str(e)}")

    if transition_effect and len(video_paths) == 2:
        temp_dir = tempfile.mkdtemp()
        try:
            video1_path = video_paths[0]
            video2_path = video_paths[1]
            props1 = _get_media_properties(video1_path)
            props2 = _get_media_properties(video2_path)
            if not props1['has_video'] or not props2['has_video']:
                raise RuntimeError("Error: xfade transition requires both inputs to be videos.")
            if transition_duration >= props1['duration']:
                raise RuntimeError(f"Error: Transition duration ({transition_duration}s) cannot be equal or longer than the first video's duration ({props1['duration']}).")

            has_audio = props1['has_audio'] and props2['has_audio']
            target_w = max(props1['width'], props2['width'], 640)
            target_h = max(props1['height'], props2['height'], 360)
            target_fps = max(props1['avg_fps'], props2['avg_fps'], 30)
            if target_fps <= 0:
                target_fps = 30

            norm_video1_path = os.path.join(temp_dir, "norm_video1.mp4")
            try:
                subprocess.run([
                    FFMPEG_BIN,
                    '-i', video1_path,
                    '-vf', f'scale={target_w}:{target_h}',
                    '-r', str(target_fps),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac',
                    '-y',
                    norm_video1_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error normalizing first video: {e.stderr.decode('utf8') if e.stderr else str(e)}")

            norm_video2_path = os.path.join(temp_dir, "norm_video2.mp4")
            try:
                subprocess.run([
                    FFMPEG_BIN,
                    '-i', video2_path,
                    '-vf', f'scale={target_w}:{target_h}',
                    '-r', str(target_fps),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac',
                    '-y',
                    norm_video2_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error normalizing second video: {e.stderr.decode('utf8') if e.stderr else str(e)}")

            norm_props1 = _get_media_properties(norm_video1_path)
            norm_video1_duration = norm_props1['duration']
            if transition_duration >= norm_video1_duration:
                raise RuntimeError(f"Error: Transition duration ({transition_duration}s) is too long for the normalized first video ({norm_video1_duration}s).")

            offset = norm_video1_duration - transition_duration
            # 标注视频与音频输出标签，便于 -map 精确映射
            filter_complex = f"[0:v][1:v]xfade=transition={transition_effect}:duration={transition_duration}:offset={offset}[v]"
            cmd = [
                FFMPEG_BIN,
                '-i', norm_video1_path,
                '-i', norm_video2_path,
                '-filter_complex'
            ]
            if has_audio:
                filter_complex += f";[0:a][1:a]acrossfade=d={transition_duration}:c1=tri:c2=tri[a]"
                cmd.extend([filter_complex, '-map', '[v]', '-map', '[a]'])
            else:
                cmd.extend([filter_complex, '-map', '[v]'])
            cmd.extend(['-c:v', 'libx264', '-c:a', 'aac', '-y', output_video_path])

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                return f"Videos concatenated successfully with '{transition_effect}' transition to {output_video_path}"
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error during xfade process: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            except Exception as e:
                raise RuntimeError(f"An unexpected error occurred during xfade concatenation: {str(e)}")
        finally:
            shutil.rmtree(temp_dir)

    temp_dir = tempfile.mkdtemp()
    try:
        normalized_paths = []
        first_props = _get_media_properties(video_paths[0])
        target_w = first_props['width'] if first_props['width'] > 0 else 1280
        target_h = first_props['height'] if first_props['height'] > 0 else 720
        target_fps = first_props['avg_fps'] if first_props['avg_fps'] > 0 else 30
        if target_fps <= 0:
            target_fps = 30

        for i, video_path in enumerate(video_paths):
            norm_path = os.path.join(temp_dir, f"norm_{i}.mp4")
            try:
                subprocess.run([
                    FFMPEG_BIN,
                    '-i', video_path,
                    '-vf', f'scale={target_w}:{target_h}',
                    '-r', str(target_fps),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac',
                    '-y',
                    norm_path
                ], check=True, capture_output=True)
                normalized_paths.append(norm_path)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error normalizing video {i}: {e.stderr.decode('utf8') if e.stderr else str(e)}")

        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_path, 'w') as f:
            for path in normalized_paths:
                f.write(f"file '{path}'\n")

        try:
            subprocess.run([
                FFMPEG_BIN,
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',
                '-y',
                output_video_path
            ], check=True, capture_output=True)
            return f"Videos concatenated successfully to {output_video_path}"
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error during concatenation: {e.stderr.decode('utf8') if e.stderr else str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during standard concatenation: {str(e)}")
    finally:
        shutil.rmtree(temp_dir)

@mcp.tool()
def change_video_speed(video_path: str, output_video_path: str, speed_factor: float) -> str:
    """改变视频的播放速度（同时处理音频）。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        speed_factor: 倍速因子（>0，例如 2.0 表示 2 倍速，0.5 表示半速）。

    Returns:
        A status message indicating success or failure.
    """
    if speed_factor <= 0:
        raise RuntimeError("Error: Speed factor must be positive.")
    if not os.path.exists(video_path):
        raise RuntimeError(f"Error: Input video file not found at {video_path}")
    try:
        atempo_value = speed_factor
        atempo_filters = []
        if speed_factor < 0.5:
            while atempo_value < 0.5:
                atempo_filters.append("atempo=0.5")
                atempo_value *= 2
            if atempo_value < 0.99:
                atempo_filters.append(f"atempo={atempo_value}")
        elif speed_factor > 2.0:
            while atempo_value > 2.0:
                atempo_filters.append("atempo=2.0")
                atempo_value /= 2
            if atempo_value > 1.01:
                atempo_filters.append(f"atempo={atempo_value}")
        else:
            atempo_filters.append(f"atempo={speed_factor}")

        input_stream = ffmpeg.input(video_path)
        video = input_stream.video.setpts(f"{1.0/speed_factor}*PTS")
        # 检查是否有音频轨
        probe = _ffprobe_probe(video_path)
        has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])
        if has_audio:
            audio = input_stream.audio
            for filter_str in atempo_filters:
                # 解析每个 atempo 滤镜的具体值
                if filter_str == "atempo=0.5":
                    tempo_val = 0.5
                elif filter_str == "atempo=2.0":
                    tempo_val = 2.0
                elif filter_str.startswith("atempo="):
                    tempo_val = float(filter_str.replace("atempo=", ""))
                else:
                    tempo_val = speed_factor
                audio = audio.filter("atempo", tempo_val)
            output = ffmpeg.output(video, audio, output_video_path)
        else:
            output = ffmpeg.output(video, output_video_path)
        _ffmpeg_run(output, capture_stdout=True, capture_stderr=True)
        return f"Video speed changed by factor {speed_factor} and saved to {output_video_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error changing video speed: {error_message}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while changing video speed: {str(e)}")

@mcp.tool()
def remove_silence(media_path: str, output_media_path: str,
                   silence_threshold_db: float = -30.0,
                   min_silence_duration_ms: int = 500) -> str:
    """移除音频/视频中的静音时段。

    Args:
        media_path: 输入媒体文件路径（音频或视频）。
        output_media_path: 输出媒体文件路径。
        silence_threshold_db: 静音判定阈值（dBFS，默认 -30.0）。
        min_silence_duration_ms: 触发删除的最小静音时长（毫秒，默认 500）。

    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(media_path):
        raise RuntimeError(f"Error: Input media file not found at {media_path}")
    if min_silence_duration_ms <= 0:
        raise RuntimeError("Error: Minimum silence duration must be positive.")

    min_silence_duration_s = min_silence_duration_ms / 1000.0
    try:
        silence_detection_process = (
            ffmpeg
            .input(media_path)
            .filter('silencedetect', n=f'{silence_threshold_db}dB', d=min_silence_duration_s)
            .output('-', format='null')
            .run_async(pipe_stderr=True)
        )
        _, stderr_bytes = silence_detection_process.communicate()
        stderr_str = stderr_bytes.decode('utf8')
        silence_starts = [float(x) for x in re.findall(r"silence_start: (\d+\.?\d*)", stderr_str)]
        silence_ends = [float(x) for x in re.findall(r"silence_end: (\d+\.?\d*)", stderr_str)]

        if not silence_starts:
            try:
                _ffmpeg_run(ffmpeg.input(media_path).output(output_media_path, c='copy'), capture_stdout=True, capture_stderr=True)
                return f"No significant silences detected (or file is entirely silent/loud). Original media copied to {output_media_path}."
            except ffmpeg.Error as e_copy:
                raise RuntimeError(f"No significant silences detected, but error copying original file: {e_copy.stderr.decode('utf8') if e_copy.stderr else str(e_copy)}")

        probe = _ffprobe_probe(media_path)
        duration_str = probe['format']['duration']
        total_duration = float(duration_str)

        sound_segments = []
        current_pos = 0.0
        for i in range(len(silence_starts)):
            start_silence = silence_starts[i]
            end_silence = silence_ends[i] if i < len(silence_ends) else total_duration
            if start_silence > current_pos:
                sound_segments.append((current_pos, start_silence))
            current_pos = end_silence
        if current_pos < total_duration:
            sound_segments.append((current_pos, total_duration))
        if not sound_segments:
            raise RuntimeError(f"Error: No sound segments were identified to keep. The media might be entirely silent according to the thresholds, or too short.")

        video_select_filter_parts = []
        audio_select_filter_parts = []
        for start, end in sound_segments:
            video_select_filter_parts.append(f'between(t,{start},{end})')
            audio_select_filter_parts.append(f'between(t,{start},{end})')
        video_select_expr = "+".join(video_select_filter_parts)
        audio_select_expr = "+".join(audio_select_filter_parts)

        input_media = ffmpeg.input(media_path)
        has_video = any(s['codec_type'] == 'video' for s in probe['streams'])
        has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])

        output_streams = []
        if has_video:
            processed_video = input_media.video.filter('select', video_select_expr).filter('setpts', 'PTS-STARTPTS')
            output_streams.append(processed_video)
        if has_audio:
            processed_audio = input_media.audio.filter('aselect', audio_select_expr).filter('asetpts', 'PTS-STARTPTS')
            output_streams.append(processed_audio)
        if not output_streams:
            raise RuntimeError("Error: The input media does not seem to have video or audio streams.")

        _ffmpeg_run(ffmpeg.output(*output_streams, output_media_path), capture_stdout=True, capture_stderr=True)
        return f"Silent segments removed. Output saved to {output_media_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error removing silence: {error_message}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while removing silence: {str(e)}")

@mcp.tool()
def add_b_roll(main_video_path: str, broll_clips: list[dict], output_video_path: str) -> str:
    """按时间在主视频上叠加 B-roll 画面。

    Args:
        main_video_path: 主视频文件路径。
        broll_clips: B-roll 配置列表。每项常见键：
            - clip_path: B-roll 视频路径。
            - insert_at_timestamp: 插入时间（秒或 'HH:MM:SS'）。
            - duration: 叠加时长（秒）。
            - position: 叠加位置（'fullscreen'|'top-left'|'top-right'|'bottom-left'|'bottom-right'|'center'）。
            - scale: 缩放系数（浮点，默认全屏 1.0，非全屏默认 0.5）。
            - transition_in/transition_out: 过渡类型（'fade' 或省略）。
            - transition_duration: 过渡时长（秒，默认 0.5）。
            - audio_mix: 音频混合占比（0.0 表示不混合）。
        output_video_path: 输出视频文件路径。

    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(main_video_path):
        raise RuntimeError(f"Error: Main video file not found at {main_video_path}")
    if not broll_clips:
        try:
            _ffmpeg_run(ffmpeg.input(main_video_path).output(output_video_path, c='copy'), capture_stdout=True, capture_stderr=True)
            return f"No B-roll clips provided. Main video copied to {output_video_path}"
        except ffmpeg.Error as e:
            raise RuntimeError(f"No B-roll clips, but error copying main video: {e.stderr.decode('utf8') if e.stderr else str(e)}")

    valid_positions = {'fullscreen', 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'}
    valid_transitions = {'fade', 'slide_left', 'slide_right', 'slide_up', 'slide_down'}
    try:
        temp_dir = tempfile.mkdtemp()
        try:
            main_props = _get_media_properties(main_video_path)
            if not main_props['has_video']:
                raise RuntimeError(f"Error: Main video {main_video_path} has no video stream.")
            main_width = main_props['width']
            main_height = main_props['height']

            processed_clips = []
            for i, broll_item in enumerate(sorted(broll_clips, key=lambda x: _parse_time_to_seconds(x['insert_at_timestamp']))):
                clip_path = broll_item['clip_path']
                if not os.path.exists(clip_path):
                    raise RuntimeError(f"Error: B-roll clip not found at {clip_path}")
                broll_props = _get_media_properties(clip_path)
                if not broll_props['has_video']:
                    continue

                start_time = _parse_time_to_seconds(broll_item['insert_at_timestamp'])
                duration = _parse_time_to_seconds(broll_item.get('duration', str(broll_props['duration'])))
                position = broll_item.get('position', 'fullscreen')
                if position not in valid_positions:
                    raise RuntimeError(f"Error: Invalid position '{position}' for B-roll {clip_path}")

                temp_clip = os.path.join(temp_dir, f"processed_broll_{i}.mp4")
                scale_factor = broll_item.get('scale', 1.0 if position == 'fullscreen' else 0.5)
                scale_filter_parts = []
                if position == 'fullscreen':
                    scale_filter_parts.append(f"scale={main_width}:{main_height}")
                else:
                    scale_filter_parts.append(f"scale=iw*{scale_factor}:ih*{scale_factor}")

                transition_in = broll_item.get('transition_in')
                transition_out = broll_item.get('transition_out')
                transition_duration = float(broll_item.get('transition_duration', 0.5))
                if transition_in == 'fade':
                    scale_filter_parts.append(f"fade=t=in:st=0:d={transition_duration}")
                if transition_out == 'fade':
                    fade_out_start = max(0, float(broll_props['duration']) - transition_duration)
                    scale_filter_parts.append(f"fade=t=out:st={fade_out_start}:d={transition_duration}")
                filter_string = ",".join(scale_filter_parts)

                try:
                    subprocess.run([
                        FFMPEG_BIN,
                        '-i', clip_path,
                        '-vf', filter_string,
                        '-c:v', 'libx264',
                        '-c:a', 'aac',
                        '-y',
                        temp_clip
                    ], check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"Error processing B-roll {i}: {e.stderr.decode('utf8') if e.stderr else str(e)}")

                overlay_x = "0"
                overlay_y = "0"
                if position == 'top-left':
                    overlay_x, overlay_y = "10", "10"
                elif position == 'top-right':
                    overlay_x, overlay_y = "main_w-overlay_w-10", "10"
                elif position == 'bottom-left':
                    overlay_x, overlay_y = "10", "main_h-overlay_h-10"
                elif position == 'bottom-right':
                    overlay_x, overlay_y = "main_w-overlay_w-10", "main_h-overlay_h-10"
                elif position == 'center':
                    overlay_x, overlay_y = "(main_w-overlay_w)/2", "(main_h-overlay_h)/2"

                processed_clips.append({
                    'path': temp_clip,
                    'start_time': start_time,
                    'duration': duration,
                    'position': position,
                    'overlay_x': overlay_x,
                    'overlay_y': overlay_y,
                    'transition_in': transition_in,
                    'transition_out': transition_out,
                    'transition_duration': transition_duration,
                    'audio_mix': float(broll_item.get('audio_mix', 0.0))
                })

            if not processed_clips:
                try:
                    shutil.copy(main_video_path, output_video_path)
                    return f"No valid B-roll clips to overlay. Main video copied to {output_video_path}"
                except Exception as e:
                    raise RuntimeError(f"No valid B-roll clips, but error copying main video: {str(e)}")

            filter_parts = []
            main_overlay = "[0:v]"
            for i, clip in enumerate(processed_clips):
                current_label = f"[v{i}]"
                overlay_index = i + 1
                overlay_filter = (
                    f"{main_overlay}[{overlay_index}:v]overlay="
                    f"x={clip['overlay_x']}:y={clip['overlay_y']}:"
                    f"enable='between(t,{clip['start_time']},{clip['start_time'] + clip['duration']})'"
                )
                if i < len(processed_clips) - 1:
                    overlay_filter += current_label
                    main_overlay = current_label
                else:
                    overlay_filter += "[v]"
                filter_parts.append(overlay_filter)

            filter_complex = ";".join(filter_parts)
            audio_output = []
            if main_props['has_audio']:
                audio_output = ['-map', '0:a']

            input_files = ['-i', main_video_path]
            for clip in processed_clips:
                input_files.extend(['-i', clip['path']])

            cmd = [
                FFMPEG_BIN,
                *input_files,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                *audio_output,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-y',
                output_video_path
            ]
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                return f"B-roll clips added successfully as overlays. Output at {output_video_path}"
            except subprocess.CalledProcessError as e:
                error_message = e.stderr.decode('utf8') if e.stderr else str(e)
                raise RuntimeError(f"Error in final B-roll composition: {error_message}")
        finally:
            shutil.rmtree(temp_dir)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error adding B-roll overlays: {error_message}")
    except ValueError as e:
        raise RuntimeError(f"Error with input values (e.g., time format): {str(e)}")
    except RuntimeError as e:
        raise RuntimeError(f"Runtime error during B-roll processing: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in add_b_roll: {str(e)}")

@mcp.tool()
def add_basic_transitions(video_path: str, output_video_path: str, transition_type: str, duration_seconds: float) -> str:
    """为整段视频添加淡入或淡出过渡效果。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        transition_type: 过渡类型，'fade_in' 或 'fade_out'。
        duration_seconds: 过渡时长（秒，>0）。

    Returns:
        A status message indicating success or failure.
    """
    if not os.path.exists(video_path):
        raise RuntimeError(f"Error: Input video file not found at {video_path}")
    if duration_seconds <= 0:
        raise RuntimeError("Error: Transition duration must be positive.")
    try:
        props = _get_media_properties(video_path)
        video_total_duration = props['duration']
        if duration_seconds > video_total_duration:
            raise RuntimeError(f"Error: Transition duration ({duration_seconds}s) cannot exceed video duration ({video_total_duration}s).")
        input_stream = ffmpeg.input(video_path)
        video_stream = input_stream.video
        audio_stream = input_stream.audio
        if transition_type == 'fade_in' or transition_type == 'crossfade_from_black':
            processed_video = video_stream.filter('fade', type='in', start_time=0, duration=duration_seconds)
        elif transition_type == 'fade_out' or transition_type == 'crossfade_to_black':
            fade_start_time = video_total_duration - duration_seconds
            processed_video = video_stream.filter('fade', type='out', start_time=fade_start_time, duration=duration_seconds)
        else:
            raise RuntimeError(f"Error: Unsupported transition_type '{transition_type}'. Supported: 'fade_in', 'fade_out'.")

        output_streams = []
        if props['has_video']:
            output_streams.append(processed_video)
        if props['has_audio']:
            output_streams.append(audio_stream)
        if not output_streams:
            raise RuntimeError("Error: No suitable video or audio streams found to apply transition.")
        try:
            output_kwargs = {'vcodec': 'libx264', 'pix_fmt': 'yuv420p'}
            if props['has_audio']:
                output_kwargs['acodec'] = 'copy'
            _ffmpeg_run(ffmpeg.output(*output_streams, output_video_path, **output_kwargs), capture_stdout=True, capture_stderr=True)
            return f"Transition '{transition_type}' applied successfully. Output: {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                _ffmpeg_run(ffmpeg.output(*output_streams, output_video_path, vcodec='libx264', pix_fmt='yuv420p'), capture_stdout=True, capture_stderr=True)
                return f"Transition '{transition_type}' applied successfully. Output: {output_video_path}"
            except ffmpeg.Error as e_recode:
                err_acopy = e_acopy.stderr.decode('utf8') if e_acopy.stderr else str(e_acopy)
                err_recode = e_recode.stderr.decode('utf8') if e_recode.stderr else str(e_recode)
                raise RuntimeError(f"Error applying transition. Audio copy failed: {err_acopy}. Full re-encode failed: {err_recode}.")
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error applying basic transition: {error_message}")
    except ValueError as e:
        raise RuntimeError(f"Error with input values: {str(e)}")
    except RuntimeError as e:
        raise RuntimeError(f"Runtime error during transition processing: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in add_basic_transitions: {str(e)}")

def main():
    """Main entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()


