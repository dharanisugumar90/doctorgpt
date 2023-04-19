import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI

if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

st.set_page_config(page_title="SchoolGPT", page_icon=":robot:")
st.header("MySchoolGPT Text")

col1, col2 = st.columns(2)

with col1:
    st.markdown("Often professionals would like to improve their skills, but don't have the skills to do so. \n\n This tool \
                will help you understand any product, platform, vmware specific skills by answering your queries. This tool \
                is powered by [LangChain](https://langchain.com/) and [OpenAI](https://openai.com) and made by \
                DharaniSugumar. \n\n")


# with col2:
#     st.image(image='TweetScreenshot.png', width=500, caption='https://twitter.com/DannyRichman/status/1598254671591723008')

# st.markdown("## Enter Your Email To Convert")

# def get_api_key():
#     input_text = st.text_input(label="OpenAI API Key ",  placeholder="Ex: sk-2twmA8tfCb8un4...", key="openai_api_key_input")
#     return input_text
#
# openai_api_key = get_api_key()

# col1, col2 = st.columns(2)
# with col1:
#     option_tone = st.selectbox(
#         'Which tone would you like your email to have?',
#         ('Formal', 'Informal'))
#
# with col2:
#     option_dialect = st.selectbox(
#         'Which English Dialect would you like?',
#         ('American', 'British'))

def get_text():
    """
    Get the user input text.
    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                               placeholder="Your AI assistant here! Ask me anything ...",
                               label_visibility='hidden')
    return input_text


def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.store = {}
    st.session_state.entity_memory.buffer.clear()


with st.sidebar.expander(" 🛠️ Settings ", expanded=False):
    # Option to preview memory store
    if st.checkbox("Preview memory store"):
        st.write(st.session_state.entity_memory.store)
    # Option to preview memory buffer
    if st.checkbox("Preview memory buffer"):
        st.write(st.session_state.entity_memory.buffer)
    MODEL = st.selectbox(label='Model',
                         options=['gpt-3.5-turbo', 'text-davinci-003', 'text-davinci-002', 'code-davinci-002'])
    K = st.number_input(' (#)Summary of prompts to consider', min_value=3, max_value=1000)

# Set up the Streamlit app layout
st.title("🧠 School GPT 🤖")
st.markdown(
    ''' 
    > :black[**A Chatbot that remembers,**  *powered by -  [LangChain]('https://langchain.readthedocs.io/en/latest/modules/memory.html#memory') + 
    [OpenAI]('https://platform.openai.com/docs/models/gpt-3-5') + 
    [Streamlit]('https://streamlit.io')*]
    ''')
# st.markdown(" > Powered by -  🦜 LangChain + OpenAI + Streamlit")

# Ask the user to enter their OpenAI API key
API_O = st.sidebar.text_input(":blue[Enter Your OPENAI API-KEY :]",
                              placeholder="Paste your OpenAI API key here (sk-...)",
                              type="password")  # Session state storage would be ideal

if API_O:
    # Create an OpenAI instance
    llm = OpenAI(temperature=0,
                 openai_api_key=API_O,
                 model_name=MODEL,
                 verbose=False)

    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)

    # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
        llm=llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=st.session_state.entity_memory
    )
else:
    st.markdown(''' 
        ```
        - 1. Enter API Key + Hit enter 🔐 

        - 2. Ask anything via the text input widget

        Your API-key is not stored in any form by this app. However, for transparency ensure to delete your API once used.
        ```
        
        ''')
st.sidebar.warning('API key required to try this app.The API key is not stored in any form.')
# st.sidebar.info("Your API-key is not stored in any form by this app. However, for transparency ensure to delete your API once used.")

st.sidebar.button("New Chat", on_click=new_chat, type='primary')
user_input = get_text()
if user_input:
    output = Conversation.run(input=user_input)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

    # Allow to download as well
download_str = []
# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        st.info(st.session_state["past"][i], icon="🧐")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])

    # Can throw error - requires fix
    download = '\n'.join(download_str)
    if download:
        st.download_button('Download', download_str)
