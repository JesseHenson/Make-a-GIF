import streamlit as st
import os
import base64
import tempfile
from PIL import Image
import numpy as np
from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx

## Session state ##
if 'clip_width' not in st.session_state:
    st.session_state.clip_width = 0
if 'clip_height' not in st.session_state:
    st.session_state.clip_height = 0
if 'clip_duration' not in st.session_state:
    st.session_state.clip_duration = 0
if 'clip_fps' not in st.session_state:
    st.session_state.clip_fps = 0
if 'clip_total_frames' not in st.session_state:
    st.session_state.clip_total_frames = 0  

# App title
st.title('GIF Creator')



def convert_vid(uploaded_file):
  # Saving to temporary file
  file_name, file_extension = os.path.splitext(uploaded_file.name)
  tfile = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) 
  tfile.write(uploaded_file.read())
  
  ## Open file ##
  st.session_state.clip = VideoFileClip(tfile.name)
  st.session_state.clip_duration = st.session_state.clip.duration


def generate_gif():
  temp_clip = st.session_state.clip.subclip(st.session_state.selected_export_range[0], 
                      st.session_state.selected_export_range[1]).speedx(st.session_state.selected_speedx)
  frames = []
  for frame in temp_clip.iter_frames():
      frames.append(np.array(frame))
  
  image_list = []

  for frame in frames:
      im = Image.fromarray(frame)
      image_list.append(im)

  image_list[0].save('export.gif', format = 'GIF', save_all = True, loop = 0, append_images = image_list)

  ## Download ##
  st.subheader('Download')
  file_ = open('export.gif', 'rb')
  contents = file_.read()
  data_url = base64.b64encode(contents).decode("utf-8")
  file_.close()
  st.markdown(
      f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
      unsafe_allow_html=True,
  )
  
  fsize = round(os.path.getsize('export.gif')/(1024*1024), 1)
  st.info(f'File size of generated GIF: {fsize} MB', icon='💾')
  print('Ran Generate GIF')

with st.form('my_form'):
  ## Upload file ##
  st.header('Upload file')
  uploaded_file = st.file_uploader("Choose a file", type=['avi','wmv','mov','mp4','mkv'])
  submitted = st.form_submit_button('Submit')
  if submitted:
      convert_vid(uploaded_file)

# Display GIF parameters once the file is loaded
if 'clip' in st.session_state: 
  # Sidebar widgets
  st.sidebar.header('Input parameters')
  st.session_state.selected_resolution_scaling = st.sidebar.slider('Scaling of video resolution', 0.0, 2.0, 0.5 )
  st.session_state.selected_speedx = st.sidebar.slider('Playback speed', 0.1, 10.0, 2.0)
  st.session_state.selected_export_range = st.sidebar.slider('Duration range to export in seconds', 0, int(st.session_state.clip_duration), (0, int(st.session_state.clip_duration) ))

  ## Resizing of video
  tmp_clip = st.session_state.clip.resize(st.session_state.selected_resolution_scaling)
      
  clip_width = tmp_clip.w
  clip_height = tmp_clip.h
  clip_duration = tmp_clip.duration
  clip_total_frames = tmp_clip.duration * tmp_clip.fps
  clip_fps = st.sidebar.slider('FPS', 10, 60, 20)
    
  ## Display output
  st.subheader('Metrics')
  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric('Width', clip_width, 'pixels')
  col2.metric('Height', clip_height, 'pixels')
  col3.metric('Duration', clip_duration, 'seconds')
  col4.metric('FPS', clip_fps, '')
  col5.metric('Total Frames', clip_total_frames, 'frames')


  # Extract video frame as a display image
  st.subheader('Preview')
  with st.expander('Show image'):
    selected_frame = st.slider('Preview a time frame (s)', 0, int(st.session_state.clip_duration), int(np.median(st.session_state.clip_duration)) )
    tmp_clip.save_frame('frame.gif', t=selected_frame)
    frame_image = Image.open('frame.gif')
    st.image(frame_image)

  ## Print image parameters ##
  st.subheader('Image parameters')
  with st.expander('Show image parameters'):
    st.write(f'File name: `{uploaded_file.name}`')
    st.write('Image size:', frame_image.size)
    st.write('Video resolution scaling', st.session_state.selected_resolution_scaling)
    st.write('Speed playback:', st.session_state.selected_speedx)
    st.write('Export duration:', st.session_state.selected_export_range)
    st.write('Frames per second (FPS):', st.session_state.clip_fps)
  





if ('clip' in st.session_state and 
    'selected_export_range' in st.session_state and 
    'selected_speedx' in st.session_state and 
    'selected_resolution_scaling' in st.session_state):
  with st.form('gen_gif'):
    ## Export animated GIF ##
      st.subheader('Generate GIF')
      submitted = st.form_submit_button('Generate Animated GIF')
      if submitted:
          st.session_state.clip = tmp_clip
          generate_gif()



