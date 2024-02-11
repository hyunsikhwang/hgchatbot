import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
from deep_translator import GoogleTranslator


st.set_page_config(page_title="Summarise and translate with HuggingChat", page_icon="random")

email = st.secrets["hg_email"]
passwd = st.secrets["hg_passwd"]

# Log in to huggingface and grant authorization to huggingchat
sign = Login(email, passwd)
cookies = sign.login()
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

# start a new conversation
id = chatbot.new_conversation()
chatbot.change_conversation(id)

def translation(sentence):
    translated = GoogleTranslator(source='en', target='ko').translate(sentence)

    return translated

st.header("HuggingChat Bot Test")

msg = st.chat_input("Input what you want to summarise")

prompt = 'Condense the provided text into concise bullet points, selecting a fitting emoji for each using the contents:'


if msg:
    msg = f'''{prompt}

    {msg}
'''
    msg_en = chatbot.chat(msg)

    st.markdown("### 원문")
    st.write(msg_en)

    msg_ko = translation(str(msg_en))
    st.markdown("### 번역")
    st.write(msg_ko)
