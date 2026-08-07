import json
import streamlit as st
import google.generativeai as genai
import yt_dlp
from moviepy.editor import VideoFileClip

# UI Setup
st.set_page_config(page_title="Shorts Maker AI", page_icon="🎬", layout="centered")
st.title("🎬 AI YouTube Shorts Generator")

# Secrets Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Streamlit Secrets mein GEMINI_API_KEY nahi mili!")
    st.stop()

# API Key setup
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

yt_url = st.text_input("YouTube video ka Link yahan paste karein:")
num_clips = st.slider("Kitne Shorts chahiye?", min_value=1, max_value=5, value=2)

if st.button("🚀 Shorts Banayein"):
    if not yt_url:
        st.warning("Kripya YouTube video ka link dalen!")
    else:
        try:
            # 1. Video Download
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': 'input_video.mp4',
                'force_overwrites': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': True,
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
            }

            with st.spinner("Video download ho rhi hai..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])
            st.success("Video Download Ho Gayi!")

            # 2. AI Timestamps Selection
            with st.spinner("AI clips select kar raha hai..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = (
                    f"Analyze this request to select top {num_clips} viral moments from a video.\n"
                    "Return ONLY a valid JSON array with objects containing 'start' and 'end' keys in float seconds (15 to 45 seconds length each).\n"
                    "Example output format:\n"
                    '[{"start": 10.0, "end": 35.0}, {"start": 60.0, "end": 90.0}]'
                )
                
                response = model.generate_content(prompt)
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                timestamps = json.loads(clean_json)

            # 3. Video Processing & Download Buttons
            st.subheader("Aapke Shorts Tayar Hain:")
            
            for i, item in enumerate(timestamps):
                start_time = float(item['start'])
                end_time = float(item['end'])
                output_filename = f"short_{i+1}.mp4"
                
                with VideoFileClip("input_video.mp4") as video:
                    clip = video.subclip(start_time, end_time)
                    
                    # 9:16 Aspect Ratio Crop (Shorts Format)
                    w, h = clip.size
                    target_ratio = 9 / 16
                    current_ratio = w / h
                    
                    if current_ratio > target_ratio:
                        new_w = int(h * target_ratio)
                        crop_x = int((w - new_w) / 2)
                        clip = clip.crop(x1=crop_x, y1=0, x2=crop_x + new_w, y2=h)
                    else:
                        new_h = int(w / target_ratio)
                        crop_y = int((h - new_h) / 2)
                        clip = clip.crop(x1=0, y1=crop_y, x2=w, y2=crop_y + new_h)

                    clip.write_videofile(
                        output_filename, 
                        codec="libx264", 
                        audio_codec="aac",
                        preset="ultrafast",
                        logger=None
                    )

                # Screen Par Video Player + Download Button
                st.write(f"**Short #{i+1}** ({start_time:.1f}s - {end_time:.1f}s)")
                st.video(output_filename)
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label=f"⬇️ Download Short #{i+1}",
                        data=file,
                        file_name=output_filename,
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error aaya: {e}")