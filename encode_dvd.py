#!/usr/bin/python

import subprocess as sub
import re
import os.path

# Mount the DVD.
mount_command = "mount /dev/sr0 /media/cdrom"
sub.call(mount_command.split())

# Get the number of titles on the DVD.
vob_command = "vobcopy -I"
p = sub.Popen(vob_command.split(),stdout=sub.PIPE,stderr=sub.PIPE)
output, errors = p.communicate()
# For some reason the DVD info goes to stderr.
# Look for an integer followed by the word titles.
num_titles = int(re.search('[0-9]+ titles', errors,
                           re.IGNORECASE).group(0).split(" ")[0])
dvd_title = re.search('DVD-name: \S+', errors,
                       re.IGNORECASE).group(0).split(" ")[1]

for title_num in range(1, num_titles + 1):
    # For each episode on the DVD.
    filename = dvd_title + str(title_num)
    vob_file = filename + ".vob"
    if not os.path.isfile(vob_file):
        # Copy VOB file to the hard disk.
        print "Copying title %d to %s." % (title_num, vob_file)
        vob_command = "vobcopy -l -n %d" % title_num
        print vob_command
        sub.call(vob_command.split())
    wav_file = filename + ".wav"
    if not os.path.isfile(wav_file):
        # Extract the audio to a wav file.
        print "Extracting audio to %s." % wav_file
        wav_command = ("mplayer %s -benchmark -vc null -vo null -ao pcm:file=%s") \
                       % (vob_file, wav_file)
        print wav_command
        sub.call(wav_command.split())
    vid_file = filename + "_x264.mp4"
    if not os.path.isfile(vid_file):
        # Encode the video to x264.
        print "Saving x264 encoded video to %s." % vid_file
        vid_command = ("bin/ffmpeg -i %s -vcodec libx264 -preset fast"
                       + " -b:v 768K -y %s") % (vob_file, vid_file)
        print vid_command
        sub.call(vid_command.split())
    mp4_file = filename + ".mp4"
    if not os.path.isfile(mp4_file):
        # Combine the audio with the x264 encoded video.
        print "Combining audio and video in %s." % mp4_file
        mp4_command = "bin/ffmpeg -i %s -i %s -b:a 128K -vcodec copy %s" \
                      % (vid_file, wav_file, mp4_file)
        print mp4_command
        sub.call(mp4_command.split())

# Unmount the DVD.
umount_command = "umount /dev/sr0"
sub.call(umount_command.split())

