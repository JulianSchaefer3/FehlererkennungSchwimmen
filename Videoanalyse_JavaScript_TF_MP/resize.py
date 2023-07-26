import moviepy.editor as mp
import sys

filename = sys.argv[1] 
#filename = #Hier Filename
folder = filename.split("/")
folder_comp =""
for i in range(len(folder)-1):
    folder_comp += folder[i] + "/"
#print(folder[len(folder)-1])
clip = mp.VideoFileClip(filename +".mp4")
clip_resized = clip.resize(height=720) # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
clip_resized.write_videofile(folder_comp + "resized/" + folder[len(folder)-1] + "_movie_resized.mp4")