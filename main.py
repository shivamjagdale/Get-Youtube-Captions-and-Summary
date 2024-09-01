import streamlit as st
from googleapiclient.discovery import build
import google.generativeai as genai
import re
from functools import lru_cache

# Set your API keys here
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]  # Add this to your Streamlit secrets

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Create YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def extract_video_id(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    return None

@lru_cache(maxsize=100)
def get_captions(video_id):
    try:
        captions = youtube.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()

        if not captions['items']:
            return "No captions available for this video."

        caption_id = captions['items'][0]['id']
        subtitle = youtube.captions().download(
            id=caption_id,
            tfmt='srt'
        ).execute()

        # Process the SRT format to extract text
        lines = subtitle.decode('utf-8').split('\n')
        text_lines = [line for line in lines if not line.strip().isdigit() and not '-->' in line]
        return ' '.join(text_lines)

    except Exception as e:
        return f"Error: {str(e)}"

def summarize_text(text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Summarize the following text in about 3-5 sentences:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

# Streamlit app
st.title("Get YouTube Video Captions and Summary")
st.write("Enter the URL of the YouTube video")

video_url = st.text_input("YouTube video URL")

if st.button("Get Captions and Summary"):
    if video_url:
        video_id = extract_video_id(video_url)
        if video_id:
            captions = get_captions(video_id)
            st.text_area("Captions:", value=captions, height=200)

            if not captions.startswith("Error") and not captions.startswith("No captions"):
                summary = summarize_text(captions)
                st.subheader("Here's the summary of the video:")
                st.write(summary)
        else:
            st.warning("Invalid YouTube URL")
    else:
        st.warning("Please enter a YouTube video URL")
