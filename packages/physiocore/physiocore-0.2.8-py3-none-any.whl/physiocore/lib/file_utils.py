import os

import cv2
from .platform_utils import save_video_codec
from playsound import playsound


def create_output_files(cap, save_video):
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    input_fps = int(cap.get(cv2.CAP_PROP_FPS))
    # If webcam returns 0 fps, default to 30
    if input_fps <= 0:
        input_fps = 30


    # Split filename and extension
    base_name, extension = os.path.splitext(save_video)
    
    # Create output paths with suffixes
    video_path = f"{base_name}_raw{extension}"
    debug_video_path = f"{base_name}_debug{extension}"

     # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
    output = cv2.VideoWriter(video_path, save_video_codec, input_fps, (frame_width,frame_height))
    output_with_info = cv2.VideoWriter(debug_video_path, save_video_codec, input_fps, (frame_width,frame_height))

    return output, output_with_info

def release_files(output, output_with_info):
    # Release the video capture and writer objects
    output.release()
    output_with_info.release()
    cv2.destroyAllWindows()


def announce():
    try:
        sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "short-sample.wav")
        playsound(sound_path)
    except Exception as e:
        print(f"Error playing sound: {e}")
    
