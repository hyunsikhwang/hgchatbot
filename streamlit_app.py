import streamlit as st
from hugchat import hugchat
from hugchat.login import Login
from deep_translator import GoogleTranslator
import trafilatura as tft
import time


st.set_page_config(page_title="Summarize with HuggingChat", page_icon="random")

email = st.secrets["hg_email"]
passwd = st.secrets["hg_passwd"]

# Save cookies to the local directory
cookie_path_dir = "./cookies_snapshot"
try:
    chatbot = hugchat.ChatBot(cookie_path=f"{cookie_path_dir}/{email}.json")
except:
    # Log in to huggingface and grant authorization to huggingchat
    sign = Login(email, passwd)
    cookies = sign.login()
    sign.saveCookiesToDir(cookie_path_dir)
    # cookies = sign.loadCookiesFromDir(cookie_path_dir) # This will detect if the JSON file exists, return cookies if it does and raise an Exception if it's not.
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

system_prompt = '''
Please summarize the content of the user's sentences in 5 to 10 bullet points or less and translate in Korean. You don't necessarily have to stick to the 10 bullet points, just create enough bullet points to fit the length of the entire sentence.
At the end of your answer, please select a key sentence from the whole paper and print it at the end, starting with the heading "Key Sentence: ".
If the user asks a questions in English, provide a Korean translation of your response. If the user asks a question in Korean, you don't need to add a translation.
'''

chatbot.switch_llm(2)

# start a new conversation
id = chatbot.new_conversation(system_prompt=system_prompt)
# assign a latest conversation
id = chatbot.get_remote_conversations(replace_conversation_list=True)[0]
chatbot.change_conversation(id)
# st.write(id.history)

def translation(sentence):
    translated = GoogleTranslator(source='en', target='ko').translate(sentence)

    return translated

def stream_data(msgTxt):
    for word in msgTxt.split():
        yield word + "\n"
        time.sleep(0.02)


st.header("Summary with HuggingChat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if msg := st.chat_input("Input what you want to summarize"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": msg})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(msg)

    # prompt = 'Condense the provided text into concise bullet points, selecting a fitting emoji for each using the contents:'
    # prompt = 'Condense the provided text into English and Korean separately using concise bullet points, and use the content to select the appropriate emoji for each:'

    if str(msg)[:7] == 'http://' or str(msg)[:8] == 'https://':
        downloaded = tft.fetch_url(msg)
        txt = tft.extract(downloaded)
        st.session_state.messages.append({"role": "user", "content": txt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(txt)
    else:
        txt = msg

    # msg_res = chatbot.chat(txt)
    msg_res = chatbot.query(txt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # response = st.write_stream(stream_data(msg_res['text']))
        response = st.write(msg_res['text'])

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": msg_res['text']})
