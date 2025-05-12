import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from transformers import pipeline
import random

# Title
st.title("🤖 AI LinkedIn Post Generator")

# Step 1: Topic Input
topic = st.text_input("Enter a marketing topic:", placeholder="e.g., MBSE in Cybersecurity")

# Step 2: Scrape and Summarize Articles (simple web search + scraping)
def search_google(topic):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = quote(topic)
    url = f"https://www.google.com/search?q={query}&num=5"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for g in soup.find_all('a'):
        href = g.get('href')
        if href and "/url?q=" in href:
            clean_url = href.split('/url?q=')[1].split('&')[0]
            if "google.com" not in clean_url:
                links.append(clean_url)
    return links[:3]

def summarize_url(url):
    try:
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([p.text for p in paragraphs])[:2000]
        return text
    except:
        return ""

# Step 3: Text Generation using Transformers (basic model for free use)
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
txt_gen = pipeline("text-generation", model="gpt2")

# Step 4: Image Generation (Craiyon fallback with suggestions)
def get_random_image_url(topic):
    sample_images = [
        "https://images.unsplash.com/photo-1591696205602-2f950c417cb9",
        "https://images.unsplash.com/photo-1581091870622-2c68e8e7f3b1",
        "https://images.unsplash.com/photo-1521790366329-5c4c122f8f63",
    ]
    return random.choice(sample_images) + "?auto=format&fit=crop&w=800&q=80"

# Step 5: Trigger post creation
if st.button("Generate Post") and topic:
    with st.spinner("Searching and summarizing..."):
        urls = search_google(topic)
        combined_text = " ".join([summarize_url(u) for u in urls])
        summary = summarizer(combined_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

    with st.spinner("Generating draft post..."):
        prompt = f"Write a LinkedIn post for professionals about: {topic}. Include insights like: {summary}"
        post = txt_gen(prompt, max_length=250, num_return_sequences=1)[0]['generated_text']

    image_url = get_random_image_url(topic)

    st.success("Here's your post preview:")
    st.image(image_url, caption="Suggested Image", use_column_width=True)
    st.text_area("Generated LinkedIn Post:", value=post, height=200)

    if st.button("Approve and Download"):
        st.download_button("Download Post Text", data=post, file_name="linkedin_post.txt")
        st.markdown(f"![Image]({image_url})")
        st.info("You can now manually copy this and post it to LinkedIn!")

    if st.button("Regenerate"):
        st.rerun()

st.markdown("---")
st.markdown("_This free app uses HuggingFace models and public image APIs. For full automation, a paid LinkedIn API account is required._")
