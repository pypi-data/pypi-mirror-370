import logging
from subprocess import Popen, PIPE
import signal


# Start FFmpeg
def start_ffmpeg(params: list):
    # Get basic FFmpeg params
    ffmpeg_cmd = get_global_params() + params
    ffmpeg_proc = Popen(ffmpeg_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # try:
    #     outs, errs = ffmpeg_proc.communicate(timeout=30)
    # except TimeoutExpired:
    #     proc.kill()
    #     outs, errs = proc.communicate()
    return ffmpeg_proc


# STOP FFmpeg
def stop_ffmpeg(ffmpeg_proc):
    try:
        logging.info("Shutting down FFmpeg process...")

        ffmpeg_proc.send_signal(signal.SIGTERM)
        ffmpeg_proc.communicate(timeout=10)

    except Exception as e:
        logging.warning(f"FFmpeg was not shut down. Killing the process...{e}")
        try:
            ffmpeg_proc.kill()
            logging.info("FFmpeg process killed!")
        except Exception as e:
            logging.warning("Failed to kill FFmpeg process. Was probably not running")


# Basic FFmpeg params
def get_global_params() -> list:
    params_ffmpeg_cmd = ["ffmpeg"]
    params_global = [
        # "-loglevel", "repeat+level+warning",
        "-loglevel",
        "repeat+level+warning",
        "-y",
    ]
    return params_ffmpeg_cmd + params_global
