import json
import streamlit as st
from google import genai
import yt_dlp
from moviepy.editor import VideoFileClip

# UI Setup
st.set_page_config(page_title="Shorts Maker AI", page_icon="🎬", layout="centered")
st.title("🎬 AI YouTube Shorts Generator")

# Streamlit Secrets se API key lein
api_key = st.secrets["GEMINI_API_KEY"]

yt_url = st.text_input("YouTube video ka Link yahan paste karein:")
num_clips = st.slider("Kitne Shorts chahiye?", min_value=1, max_value=5, value=2)

if st.button("🚀 Shorts Banayein"):
    if not yt_url:
        st.warning("Kripya YouTube video ka link dalen!")
    else:
        try:
            # 1. Gemini Client Initialize
            client = genai.Client(api_key=api_key)

            # 2. Video Download Options
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': 'input_video.mp4',
                'force_overwrites': True,
            }

            with st.spinner("Video download ho rhi hai..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])
            st.success("Video Download ho gayi!")

            # 3. Gemini AI se Viral Timestamps maangein
            with st.spinner("AI best moments dhoondh raha hai..."):
                prompt = f"""
                Analyze this request to select top {num_clips} viral moments from a video.
                Return ONLY a JSON array with objects containing 'start' and 'end' keys in float seconds (15 to 45 seconds length each).
                Example: [{"start": 10.0, "end": 35.0}, {"start": 60.0, "end": 90.0}]
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                # Clean and parse JSON
                text_response = response.text.replace("```json", "").replace("```", "").strip()
                timestamps = json.loads(text_response)

            # 4. Process Clips
            st.subheader("Aapke Shorts Tayar Hain:")
            
            for i, item in enumerate(timestamps):
                start_time = float(item['start'])
                end_time = float(item['end'])
                
                output_filename = f"short_{i+1}.mp4"
                
                # MoviePy Processing
                with VideoFileClip("input_video.mp4") as video:
                    clip = video.subclip(start_time, end_time)
                    
                    # 9:16 Crop
                    w, h = clip.size
                    target_aspect_ratio = 9 / 16
                    current_aspect_ratio = w / h
                    
                    if current_aspect_ratio > target_aspect_ratio:
                        new_w = int(h * target_aspect_ratio)
                        crop_x1 = int((w - new_w) / 2)
                        clip = clip.crop(x1=crop_x1, y1=0, x2=crop_x1 + new_w, y2=h)
                    else:
                        new_h = int(w / target_aspect_ratio)
                        crop_y1 = int((h - new_h) / 2)
                        clip = clip.crop(x1=0, y1=crop_y1, x2=w, y2=crop_y1 + new_h)

                    clip.write_videofile(
                        output_filename, 
                        codec="libx264", 
                        audio_codec="aac",
                        preset="ultrafast",
                        logger=None
                    )

                st.write(f"**Short #{i+1}** (Time: {start_time:.1f}s - {end_time:.1f}s)")
                st.video(output_filename)

        except Exception as e:
            st.error(f"Error aaya: {e}")