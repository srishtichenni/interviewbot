import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def get_llama_response(skill,level, num):
    response = client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":"you are a helpful assistant to a recruiter. given the skill, skill level and number of questions, you will generate the questions, to help the recruiter assess the candidate."
            },
            {
                "role":"user",
                "content":f"""
                Generate {num} {level}-level interview Questions on {skill}:
                """
            }
        ],

        model = "llama3-8b-8192",

        temperature = 0.5,
        max_tokens = 1024,
        stream = False
    )
    return response.choices[0].message.content

st.set_page_config(page_title="InterviewBot", page_icon=":memo:")

with st.sidebar:
    st.title("LLM Assisted Interview Bot")

    skill = st.text_input("Enter skill:")
    level = st.selectbox("Select level:", ["Beginner", "Intermediate", "Advanced"])
    qns = st.slider("Number of Questions:",min_value=1,max_value=10,value=5)
    submit = st.button("Generate")

qns = int(qns)

client = Groq(
    api_key = os.getenv("GROQ_API_KEY")
)

st.header("Generated Questions")
if submit:
    st.subheader(f"{skill} - {level} level:")

    with st.spinner("Generating..."):
        st.write(get_llama_response(skill, level, qns))

