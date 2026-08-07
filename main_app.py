import json
import streamlit as st
from google import genai
import yt_dlp
from moviepy import VideoFileClip

# UI Setup
st.set_page_config(page_title="Shorts Maker AI", page_icon="🎬", layout="centered")
st.title("🎬 AI YouTube Shorts Generator")

api_key = st.secrets["GEMINI_API_KEY"]

yt_url = st.text_input("YouTube video ka Link yahan paste karein:")
num_clips = st.slider("Kitne Shorts chahiye?", min_value=1, max_value=5, value=2)

if st.button("🚀 Shorts Banayein"):
    if not yt_url:
        st.warning("Kripya YouTube video ka link dalen!")
    else:
        try:
            client = genai.Client(api_key=api_key)

            # 1. Video Download
            with st.spinner("⏳ Video download ho raha hai..."):
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': 'input_video.mp4',
                    'force_overwrites': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])
                st.success("✅ Video download ho gaya!")

            # 2. AI Processing
            with st.spinner("🧠 Gemini AI best highlights dhoondh raha hai..."):
                uploaded_file = client.files.upload(file="input_video.mp4")
                
                prompt = f"""
                Analyze this video and find {num_clips} most engaging short segments suitable for YouTube Shorts (15-60 seconds each).
                Return ONLY a JSON list of objects with 'start' and 'end' keys in seconds. Example: [{{"start": 10, "end": 40}}]
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[uploaded_file, prompt]
                )
                
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                timestamps = json.loads(clean_json)

            # 3. Trimming Clips
            with st.spinner("✂️ Video clips cut ki ja rahi hain..."):
                video = VideoFileClip("input_video.mp4")
                
                for i, clip_data in enumerate(timestamps):
                    start_time = clip_data['start']
                    end_time = clip_data['end']
                    
                    if hasattr(video, 'subclipped'):
                        new_clip = video.subclipped(start_time, end_time)
                    else:
                        new_clip = video.subclip(start_time, end_time)
                        
                    output_filename = f"short_{i+1}.mp4"
                    new_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac")
                    
                    st.subheader(f"🎬 Short #{i+1}")
                    st.video(output_filename)
                
                video.close()
                st.success("🎉 Aapke Shorts taiyar hain!")

        except Exception as e:
            st.error(f"Error aaya: {e}")