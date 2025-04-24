import os
import requests
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from groq import Groq
from IPython.display import Markdown, display
from dotenv import load_dotenv
import streamlit as st


load_dotenv(override=True)
api_key = os.getenv('GROQ_API_KEY')
# Initialize Groq client
groq_client = Groq(api_key=api_key)

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


class Website:
    def __init__(self,url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content,'html.parser')
        self.title = soup.title.string if soup.title else 'No title found'
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator='\n',strip=True)

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."


def message_for(website):
    return [
        {'role':'system','content':system_prompt},
        {'role':'user','content':user_prompt_for(website)}
    ]


def summarize(url):
    website = Website(url)
    response = groq_client.chat.completions.create(
        model = 'llama-3.1-8b-instant',
        messages = message_for(website)
    )
    return response.choices[0].message.content

st.set_page_config(page_title="Web Summarizer", page_icon="📝", layout="centered")
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    </style>
""", unsafe_allow_html=True)

st.title("📝 Website Summarizer with Groq + Streamlit")
st.caption("Enter a URL below and get a summarized version of the page content.")
url = st.text_input("Enter a webpage URL")

if st.button("Summarize"):
    if url:
        with st.spinner("Fetching and summarizing..."):
            try:
                summary = summarize(url)
                st.subheader("📌 Summary")
                st.write(summary)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please enter a valid URL.")