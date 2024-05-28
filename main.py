import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

load_dotenv()

def main():
    groq_key = os.environ['GROQ_API_KEY']
    st.title("AI Interview Bot")

    system_prompt = """You are an interviewer who will generate a multiple choice question to interview a candidate, given the skill and skill level of the candidate.
    If the candidate chooses the correct answer, you will respond with another question of higher difficulty level.
    If the candidate chooses the wrong answer, you will respond with another question of similar or lower difficulty level.
    You will generate a specified number of questions in total.
    """

    conversational_memory_length = 5
    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key='chat_history', return_messages=True)

    groq_chat = ChatGroq(
        groq_api_key=groq_key,
        model_name='llama3-8b-8192'
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name='chat_history'),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ]
    )

    conversation = LLMChain(
        llm=groq_chat,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    def generate_question(skill, skill_level, skill_level_num):
        user_question = f"Generate an interview question on {skill} - {skill_level} : {skill_level_num}/10 level"
        response = conversation.predict(human_input=user_question)
        return response

    def assess_answer(question, answer):
        check_prompt = f"Question: {question}\nAnswer: {answer}\nWas the answer correct? Respond with 'yes' or 'no'."
        assessment = conversation.predict(human_input=check_prompt)
        return 'yes' in assessment.lower()

    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
        st.session_state.question_count = 0
        st.session_state.current_question = None
        st.session_state.current_level = 5
        st.session_state.skill_level_description = ''
        st.session_state.answers = []

        

    if not st.session_state.show_chat:
        with st.form(key="skill_form"):
            skill = st.text_input("Enter your skill:")
            level = st.slider("Skill level", min_value=1, max_value=10, value=5)
            next_button = st.form_submit_button("Begin Interview")
            reset_button = st.form_submit_button("Reset")

            if reset_button:
                st.session_state["skill"] = ""
                st.session_state.text_input =""
                st.session_state["level"] = 5
                st.experimental_rerun()

            if next_button:
                st.session_state["skill"] = skill
                st.session_state["level"] = level
                if level < 5:
                    st.session_state.skill_level_description = 'Beginner'
                elif level < 8:
                    st.session_state.skill_level_description = 'Intermediate'
                else:
                    st.session_state.skill_level_description = 'Advanced'

                st.session_state.show_chat = True
                st.experimental_rerun()

    if st.session_state.show_chat:
        if st.session_state.question_count >= 10:
            st.write("Interview completed. Thank you!")
            if st.button("Start Again"):
                reset()
        else:
            if st.session_state.current_question is None:
                st.session_state.current_question = generate_question(st.session_state.skill, st.session_state.skill_level_description, st.session_state.level)
                st.write(f"Question {st.session_state.question_count + 1}: {st.session_state.current_question}")
            else:
                st.write(f"Question {st.session_state.question_count + 1}: {st.session_state.current_question}")

            chat_input = st.text_input("Enter your answer:")
            send_button = st.button("Send")

            if send_button:
                if chat_input:
                    is_correct = assess_answer(st.session_state.current_question, chat_input)
                    st.session_state.answers.append(chat_input)
                    st.write(f"Your answer is {'correct' if is_correct else 'incorrect'}.")

                    if is_correct:
                        st.session_state.level = min(st.session_state.level + 1, 10)
                    else:
                        st.session_state.level = max(st.session_state.level - 1, 1)

                    st.session_state.current_question = None
                    st.session_state.question_count += 1
                    st.session_state.chat_input=""
                    st.experimental_rerun()

def reset():
    st.session_state.show_chat = False
    st.session_state.question_count = 0
    st.session_state.current_question = None
    st.session_state.current_level = 5
    st.session_state.skill_level_description = ''
    st.session_state.answers = []
    st.session_state["skill"] = ""
    st.session_state["level"] = 5
    st.experimental_rerun()

if __name__ == '__main__':
    main()
