import os
import streamlit as st
import yt_dlp
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Shorts Maker", page_icon="🎬", layout="centered")
st.title("🎬 YouTube Shorts Generator")

yt_url = st.text_input("YouTube video ka Link yahan paste karein:")
num_clips = st.slider("Kitne Shorts chahiye?", min_value=1, max_value=5, value=2)

if st.button("🚀 Shorts Banayein"):
    if not yt_url:
        st.warning("Kripya YouTube video ka link dalen!")
    else:
        try:
            # Purani file ho toh delete karein
            if os.path.exists("input_video.mp4"):
                os.remove("input_video.mp4")

            # Updated yt-dlp configuration for Streamlit Cloud
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'input_video.%(ext)s',
                'force_overwrites': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_warnings': True,
                'quiet': True,
                'merge_output_format': 'mp4',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web']
                    }
                }
            }

            with st.spinner("Video download ho rhi hai..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])

            # File download verification
            if not os.path.exists("input_video.mp4"):
                st.error("YouTube se video download nahi ho saki. Kripya doosra link try karein!")
            else:
                st.success("Video Download Ho Gayi!")
                st.subheader("Aapke Shorts Tayar Hain:")

                with VideoFileClip("input_video.mp4") as video:
                    total_duration = video.duration
                    clip_length = 30  # Har short 30 seconds ka

                    for i in range(num_clips):
                        start_time = i * clip_length
                        end_time = min(start_time + clip_length, total_duration)

                        if start_time >= total_duration:
                            break

                        output_filename = f"short_{i+1}.mp4"
                        clip = video.subclip(start_time, end_time)

                        # 9:16 Aspect Ratio Crop
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

                        st.write(f"**Short #{i+1}** ({start_time:.1f}s - {end_time:.1f}s)")
                        st.video(output_filename)

                        with open(output_filename, "rb") as file:
                            st.download_button(
                                label=f"⬇️ Download Short #{i+1}",
                                data=file,
                                file_name=output_filename,
                                mime="video/mp4",
                                key=f"dl_{i}"
                            )

        except Exception as e:
            st.error(f"Error aaya: {e}")