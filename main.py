import pandas as pd
import numpy as np

import cv2
from PIL import Image

from glob import glob

import subprocess
import os
from tqdm import tqdm

# definitions
path = os.getcwd()

# constants
diff_threshold = 7
time_threshold = 1
frame_percentage = 0.01

if __name__ == '__main__':
    # read all videos in the videos folder
    videos = glob(f'{path}/videos/*')
    # every video that is not an mp4 will be converted to mp4 using ffmpeg
    for video in videos:
        print(video)
        if video.split('.')[-1] != 'mp4':
            subprocess.run(['ffmpeg', '-i', video, '-qscale', '0', f'{video.split(".")[0]}.mp4', '-loglevel', 'quiet'])
            os.remove(video)

    # clear everything in the frames folder
    for frame in glob(f'{path}/frames/*'):
        os.remove(frame)

    # read all mp4 videos in the videos folder
    videos = glob(f'{path}/videos/*.mp4')

    for video in videos:
        capture = cv2.VideoCapture(video)
        vid_name = video.split('/')[-1]
        print(f'Reading {vid_name}')

        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = capture.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        print(f'{duration:.2f} seconds, {fps:.2f} fps, {frame_count} frames')

        running_diff_capture = cv2.VideoCapture(video)
        diff_sum = 0
        prev_frame = None
        for frame in tqdm(range(frame_count), desc='Calculating difference threshold'):
            ret, img = running_diff_capture.read()
            if not ret:
                break
            if prev_frame is not None:
                diff_sum += cv2.absdiff(prev_frame, img).mean()
            prev_frame = img
        running_diff_capture.release()
        # calculate the difference threshold based on the percentage of the video that we want to capture
        diff_threshold = diff_sum / (frame_count * frame_percentage)

        prev_frame = None
        prev_frame_num = 0
        frame_written = 0
        for frame in tqdm(range(frame_count), desc='Writing frames'):
            ret, img = capture.read()
            if not ret:
                break
            # if we have not written a frame yet or the difference between the previous frame and
            # the current frame is greater than 1 we write the frame to the frames folder
            if (prev_frame is None) or ((cv2.absdiff(prev_frame, img).mean() > diff_threshold) and ((frame/fps - prev_frame_num/fps) > time_threshold)):
                prev_frame = img.copy()
                prev_frame_num = frame
                # before writing the frame, add an approximate timestamp to the frame
                cv2.putText(img, f'{frame/fps:.2f}s', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imwrite(f'{path}/frames/{vid_name.split(".")[0]}_{frame}.jpg', img)
                frame_written += 1
        print(f'Wrote {frame_written} frames')

        # creating a pdf with the frames in the correct order
        images = [Image.open(image) for image in sorted(glob(f'{path}/frames/{vid_name.split(".")[0]}*.jpg'), key=lambda x: int(x.split('_')[-1].split('.')[0]))]
        images[0].save(f'{path}/pdfs/{vid_name.split(".")[0]}.pdf', save_all=True, append_images=images[1:])
        print(f'Created {vid_name.split(".")[0]}.pdf')

        # clear everything in the frames folder
        for frame in glob(f'{path}/frames/*'):
            os.remove(frame)

        capture.release()