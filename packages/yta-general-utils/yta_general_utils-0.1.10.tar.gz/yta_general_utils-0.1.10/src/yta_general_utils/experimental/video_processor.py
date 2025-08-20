"""
This file has been commented to delete the code in a near future
and avoid the use of 'cv2' so we can remove it as a requirement.
"""

# from yta_general_utils.temp import create_tmp_filename
# from yta_general_utils.video_processor import extract_audio_from_video
# from moviepy import VideoFileClip, CompositeVideoClip, CompositeAudioClip, AudioFileClip
# from yta_general_utils.experimental.tiktok import download_tiktok_video, process_tiktok_video_url

# import numpy as np
# import os
# import random
# import cv2
# import math


# # TODO: This should be moved to multimedia because
# # it is video related
# def build_short_from_tiktok_video(tiktok_url, overlay_video_filename):
#     """
#     This method receives a tiktok video url and creates a new video to be shared as short
#     that contains the original video and an overlay gameplay or content to customize it.
#     """
#     OVERLAY_CROPPED_VIDEO = create_tmp_filename('overlay_cropped.mp4')
#     OVERLAY_RESCALED_VIDEO = create_tmp_filename('overlay_rescaled.mp4')
    
#     # Check if exist and has been processed to avoid processing it again
#     tiktok_video_data = process_tiktok_video_url(tiktok_url)
#     # database_tiktok_video = db_select('tiktok_videos', 'video_id', tiktok_video_data['video_id'])
#     # if database_tiktok_video and database_tiktok_video['status'] == 'generated':
#     #     print('The video ' + tiktok_video_data['video_id'] + ' from user @' + database_tiktok_video['username'] + ' has already been uploaded. Stopping process...')
#     #     return
    
#     output_video_filename = tiktok_video_data['username'] + '_' + tiktok_video_data['video_id'] + '_one.mp4'

#     # *. Download tiktok video
#     downloaded_video_filename = download_tiktok_video(tiktok_url)
#     main_video = VideoFileClip(downloaded_video_filename)
    
#     if main_video.duration >= 60:
#         print('Sorry, main video is 60 seconds or longer...')
#         return

#     # 1. Rescale overlay to main_video width
#     overlay_video = VideoFileClip(overlay_video_filename)
#     random_start = random.randint(0, (int) (overlay_video.duration - main_video.duration))
#     overlay_video = overlay_video.subclip(random_start, random_start + main_video.duration)
#     overlay_video.write_videofile(OVERLAY_CROPPED_VIDEO)

#     resize(OVERLAY_CROPPED_VIDEO, OVERLAY_RESCALED_VIDEO, new_width = main_video.w)
#     overlay_rescaled_video = VideoFileClip(OVERLAY_RESCALED_VIDEO)

#     # 2. Join videos
#     final_clip = CompositeVideoClip([main_video.set_position((0, -100)), overlay_rescaled_video.set_position('bottom')])
#     final_clip.write_videofile(output_video_filename, fps = 30)

#     # 3. Store in database that video as created
#     # db_insert('tiktok_videos', ['video_id', 'username', 'status'], [tiktok_video_data['video_id'], tiktok_video_data['username'], 'generated'])

#     #  TODO: Remove files
#     try:
#         os.remove(OVERLAY_CROPPED_VIDEO)
#         os.remove(OVERLAY_RESCALED_VIDEO)
#         #os.remove(downloaded_video_filename)
#     except:
#         print('Error deleting files')

# def resize(video_filename, output_filename = 'video_resized.mp4', new_width = None, new_height = None):
#     if not new_width and not new_height:
#         return
    
#     clip = VideoFileClip(video_filename)

#     if new_width and not new_height:
#         new_height = math.ceil((clip.h * new_width) / clip.w)
#     elif new_height and not new_width:
#         new_width = math.ceil((clip.w * new_height) / clip.h)

#     # moviepy resize method does not allow odd numbers
#     if new_width % 2 != 0:
#         new_width -= 1
#     if new_height % 2 != 0:
#         new_height -= 1
    
#     clip.resize(width = new_width, height = new_height).write_videofile(output_filename)

# def deeply_process_green_screen(original_filename, output_filename):
#     """
#     I receive a green screen transition 'original_filename' and I process it to turn
#     that green screen into a black background to, later, improve processing it with
#     mask filter.

#     This method is useful for clean transitions (maybe with not many colors). This
#     need more testing.
#     """
#     TMP_VIDEO_FILE = create_tmp_filename('tmp_deep_transition_without_audio.avi')
#     TMP_AUDIO_FILE = create_tmp_filename('tmp_deep_transition_audio.mp3')

#     # TODO: Sorry but this time output must be .avi, thank you
#     if not output_filename.endswith('.avi'):
#         print('Sorry, output must be .avi')
#         exit()

#     cap = cv2.VideoCapture(original_filename)
#     # grab one frame
#     _, frame = cap.read()
#     h,w = frame.shape[:2]
#     h = int(h)
#     w = int(w)
    
#     res = (w, h)
#     # Videowriter to build the output
#     fourcc = cv2.VideoWriter_fourcc(*'XVID')
#     out = cv2.VideoWriter(TMP_VIDEO_FILE, fourcc, 30.0, res)
    
#     # We only git the most common color in first frame (it should be the green)
#     green_screen_color = None
#     done = False
#     while not done:
#         # Get the current frame
#         ret, img = cap.read()
#         if not ret:
#             done = True
#             continue

#         # Turn into HSV
#         hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#         h,s,v = cv2.split(hsv)

#         # I choose manually (only in the first frame) the 
#         biggest = -1
#         if green_screen_color == None:
#             # Get unique colors in frame
#             unique_colors, counts = np.unique(s, return_counts=True)

#             for a in range(len(unique_colors)):
#                 if counts[a] > biggest:
#                     biggest = counts[a]
#                     green_screen_color = int(unique_colors[a])

#         # This margin was manually chosen (according to results)
#         margin = 70
#         mask = cv2.inRange(s, green_screen_color - margin, green_screen_color + margin)

#         # Smooth out the mask and invert
#         kernel = np.ones((3,3), np.uint8)
#         mask = cv2.dilate(mask, kernel, iterations = 1)
#         mask = cv2.medianBlur(mask, 5)
#         mask = cv2.bitwise_not(mask)

#         # Crop out the image and fill with color (black) to make it work well
#         #crop = np.full_like(img, [0, 255, 0])
#         crop = np.zeros_like(img)
#         # I think here is filling with BLACK, maybe I can fill it with pure GREEN
#         crop[mask == 255] = img[mask == 255]
#         out.write(crop)

#     # Free resources
#     cap.release()
#     out.release()

#     # Append audio we lost
#     extract_audio_from_video(original_filename, TMP_AUDIO_FILE)
#     append_audio(TMP_VIDEO_FILE, TMP_AUDIO_FILE, output_filename)

#     # Here we have the file stored with the green background now as black background
#     # TODO: Maybe we can use that mask to get a transparency layer with another library
#     # as opencv does not support it (as I read)
#     return True

# def append_audio(video_filename, audio_filename, output_filename = 'with_audio.mp4'):
#     """
#     Receives a video, replaces its audio with the audio in 'input_audio' file
#     and creates a new video with the 'output_video' name.
#     """
#     # TODO: Do this with an array of accepted extensions, please
#     if not video_filename.endswith('.mp4') and not video_filename.endswith('.mov') and not video_filename.endswith('.avi') and not video_filename.endswith('webm'):
#         video_filename += '.mp4'
    
#     # TODO: Create an 'accepted_video_extensions' and 'accepted_audio_extensions' and use them
#     if not audio_filename.endswith('.mp3') and not audio_filename.endswith('.wav') and not audio_filename.endswith('.m4a'):
#         audio_filename += '.mp3'

#     if output_filename == video_filename:
#         print('Output video name cannot be the same as input!')
#         return None
    
#     # TODO: Investigate a way of appending with ffmpeg because it
#     # seems to be so much faster than moviepy

#     #from subprocess import run
#     #parameters = ['ffmpeg', '-i', video_filename, '-i', audio_filename, '-c:v', 'libvpx', '-crf', '15', #'-b:v', '1M', 'copy', output_filename]
#     #run(parameters)
#     #ffmpeg -i video.mp4 -i audio.m4a -c copy output.mp4


#     videoclip = VideoFileClip(video_filename)
#     # This is a fix of bad audio ending due to ffmpeg error with moviepy
#     # See this: https://github.com/Zulko/moviepy/issues/1936
#     #audiounfixedclip = AudioFileClip(input_audio)
#     #audiounfixedclip = audiounfixedclip.subclip(0, audiounfixedclip.duration)
#     #audioclip = CompositeAudioClip([audiounfixedclip])
#     audioclip = CompositeAudioClip([AudioFileClip(audio_filename)])
#     videoclip.audio = CompositeAudioClip([audioclip])

#     videoclip.to_videofile(
#         output_filename,
#         #codec = "libx264",
#         #temp_audiofile = WIP_FOLDER + 'temp-audio.m4a',
#         #remove_temp = True,
#         #audio_codec = 'aac' # pcm_s16le or pcm_s32le 'aac' previously
#     )