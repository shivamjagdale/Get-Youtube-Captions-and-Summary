import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re
import os
import json

# Set your API key here
working_dir = os.path.dirname(os.path.abspath(__file__))
config_path = f"{working_dir}/config.json"
with open(config_path, "r") as f:
    config_data = json.load(f)

GOOGLE_API_KEY = config_data[
    "GOOGLE_API_KEY"]  # Replace with your actual API key

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)


def extract_video_id(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    return None


def get_captions(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL"

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        captions = " ".join([entry['text'] for entry in transcript])
        return captions
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
        captions = get_captions(video_url)
        st.text_area("Captions:", value=captions, height=200)

        if not captions.startswith("Error"):
            summary = summarize_text(captions)
            st.subheader("Here's the summary of the video:")
            st.write(summary)
    else:
        st.warning("Please enter a YouTube video URL")
