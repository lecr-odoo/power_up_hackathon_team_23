import streamlit as st
from streamlit_chat import message
import requests
import random
import openai

openai.api_key = ""


# Check the prompt and the response sent back to make sure that it is sanitary
def checkPrompt(prompt):

    # Create another loop for the request going through
    prompt = prompt.lower()
    for word in blacklisted_words:
        if word in prompt:
            return False
    return True

# Send the prompt that the user sends to chatgpt
def sendRequest(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"] if response["choices"] else "Server is overloaded"


blacklisted_words = ["damn", "bomb", "butt", "shit"]

st.set_page_config(
    page_title="Buffalo Prep",
    page_icon=":robot:"
)


st.header("Buffalo Prep")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def query(payload):

    if not checkPrompt(payload["inputs"]["text"]):
        return "Please do not use any blacklisted words"

    # Parse the response that would be sent back to the user after sending their response
    response = sendRequest(payload["inputs"]["text"])

    while not checkPrompt(response):
        # Keep calling ChatGPT again to get a sanitary response
        response = sendRequest(payload["inputs"]["text"])

    return response


def get_text():
    input_text = st.text_input("", key="input")
    return input_text


user_input = get_text()

if user_input:
    output = query({
        "inputs": {
            "past_user_inputs": st.session_state.past,
            "generated_responses": st.session_state.generated,
            "text": user_input,
        },
        "parameters": {"repetition_penalty": 1.33},
    })

    st.session_state.past.append(user_input)
    # Writing the responses to a file.
    with open('responses.txt', 'a') as f:
        f.write("\n")
        f.write("Input:" + user_input)
        f.write("\n")
        f.write("Response:" + output)
    st.session_state.generated.append(output)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')



