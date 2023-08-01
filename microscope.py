import subprocess
import re
import platform
import win32con
import argparse

def find_usb_webcams():
    output: str = ""
    try:
        # Execute the ffmpeg command to list DirectShow devices
        cmd = 'ffmpeg -list_devices true -f dshow -i dummy'
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            output = e.output.decode('utf-8')
        else:
            raise e
    # print(output)
    # Use regular expressions to extract camera alternative names matching microscope usb vendor id and product id
    pattern = r'\"(.*usb#vid_0c45&pid_1a90.*)\"'
    matches = re.findall(pattern, output)
    #print(matches)
    return matches

def start_ffplay_stream(camera_name, left_offset):

    # Construct the ffplay command
    ffplay_cmd = [
        'ffplay',
         '-f', 'dshow',
          '-vcodec', 'mjpeg',
         '-video_size', '1280x960',
          '-i', f'video={camera_name}',
          '-vf', 'drawgrid=w=iw/2:h=ih/2:t=1:c=white@0.5,crop=960:960',
          '-noborder',
           '-left', str(left_offset)
    ]

    if platform.system() == 'Windows':
        # On Windows, use CREATE_NEW_CONSOLE and SW_MINIMIZE flags to create a new minimized terminal window for ffplay
        creation_flags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup_info.wShowWindow = win32con.SW_MINIMIZE
    else:
        creation_flags = 0  # Not used on non-Windows platforms
        startup_info = None

    # Start ffplay command asynchronously and capture the output
    print(ffplay_cmd)
    ffplay_process = subprocess.Popen(ffplay_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)


def start_mjpeg_streams(reverse: bool):
    webcams = find_usb_webcams()
    start_ffplay_stream(webcams[0],0 if reverse else 960)
    start_ffplay_stream(webcams[1],960 if reverse else 0)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Start MJPEG streams from USB webcams with optional reverse option.")
    parser.add_argument("-reverse", action="store_true", help="Reverse the positioning of cameras.")
    args = parser.parse_args()

    # Start the MJPEG streams with the parsed reverse flag
    start_mjpeg_streams(reverse=args.reverse)