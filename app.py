
import os
import uuid
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="GenAI IT Helpdesk",
    page_icon="🛠️",
    layout="wide"
)

load_dotenv()

# Read API key from local .env or Streamlit Cloud Secrets
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    try:
        API_KEY = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        API_KEY = None

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

# --------------------------------------------------
# 2. CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #17365d;
    }

    .subtitle {
        color: #64748b;
        font-size: 15px;
    }

    .info-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
    }

    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. GEMINI CLIENT
# --------------------------------------------------

if not API_KEY:
    st.error("Gemini API key not found.")
    st.info(
        "Add GEMINI_API_KEY to your .env file "
        "and restart the application."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

# --------------------------------------------------
# 4. SYSTEM INSTRUCTIONS
# --------------------------------------------------

SYSTEM_INSTRUCTION = """
You are an intelligent IT Helpdesk Support Assistant.

Your responsibility is to help users resolve common IT issues.

You should support these categories:

1. Network and Internet
2. Hardware
3. Software
4. Login and Access
5. Email
6. Operating System
7. Printer
8. Other IT Issues

Your responsibilities:

- Understand the user's technical problem.
- Identify the likely issue category.
- Explain possible causes.
- Give clear step-by-step troubleshooting.
- Ask follow-up questions when necessary.
- Recommend priority: Low, Medium or High.
- Explain why a priority is recommended.
- Use simple language suitable for non-technical users.

IMPORTANT SAFETY RULES:

- Never ask users to share passwords or OTPs.
- Do not recommend disabling security software.
- Do not suggest destructive commands without
  explaining the risks.
- Recommend contacting IT support for serious
  security incidents or unresolved problems.
- Never claim that a problem is fixed unless
  the user confirms it.

Stay focused on IT support.
"""

# --------------------------------------------------
# 5. SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ticket" not in st.session_state:
    st.session_state.ticket = None

# --------------------------------------------------
# 6. GENERATE AI RESPONSE
# --------------------------------------------------

def generate_response(messages):

    conversation = ""

    for message in messages[-12:]:
        role = message["role"].upper()
        conversation += (
            f"\n{role}: {message['content']}\n"
        )

    prompt = f"""
    Here is the conversation between the user
    and the IT Helpdesk Assistant:

    {conversation}

    Respond to the latest user message.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4,
            max_output_tokens=1000
        )
    )

    if not response.text:
        raise ValueError("The AI returned an empty response.")

    return response.text


# --------------------------------------------------
# 7. GENERATE SUPPORT TICKET
# --------------------------------------------------

def generate_ticket(issue):

    prompt = f"""
    Create a professional IT support ticket
    based on the following user issue:

    {issue}

    Return these fields:

    Issue Summary:
    Category:
    Priority: Low, Medium or High
    Priority Reason:
    Recommended Action:
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=500
        )
    )

    return response.text


# --------------------------------------------------
# 8. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🛠️ IT Helpdesk")

    st.markdown("---")

    st.subheader("Project Information")

    st.write("Generative AI IT Helpdesk Chatbot")

    st.caption("AI-powered technical support assistant")

    st.markdown("---")

    st.subheader("Supported Issues")

    st.write("🌐 Network Problems")
    st.write("💻 Hardware Problems")
    st.write("📦 Software Problems")
    st.write("🔐 Login and Access")
    st.write("📧 Email Issues")
    st.write("🖨️ Printer Problems")

    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):

        st.session_state.messages = []
        st.session_state.ticket = None
        st.rerun()

    st.markdown("---")

    st.caption("Powered by Python, Streamlit and Gemini AI")


# --------------------------------------------------
# 9. MAIN DASHBOARD
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🤖 Generative AI IT Helpdesk</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your intelligent technical support assistant</div>',
    unsafe_allow_html=True
)

st.write("")

# Information cards

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Messages", len(st.session_state.messages))

with col2:
    st.metric(
        "User Queries",
        sum(
            1 for m in st.session_state.messages
            if m["role"] == "user"
        )
    )

with col3:
    st.metric(
        "Tickets Generated",
        1 if st.session_state.ticket else 0
    )

st.markdown("---")

# --------------------------------------------------
# 10. WELCOME MESSAGE
# --------------------------------------------------

if not st.session_state.messages:

    st.subheader("Welcome! How can I help you?")

    st.write(
        "Describe your technical problem below. "
        "I will help you identify and troubleshoot it."
    )

    st.markdown("### Try these example questions")

    examples = [
        "My laptop is connected to Wi-Fi but internet is not working.",
        "I forgot my Windows password.",
        "My computer is running very slowly.",
        "I cannot access my company email.",
        "My printer is not responding."
    ]

    for example in examples:
        st.markdown(f"- {example}")


# --------------------------------------------------
# 11. DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# --------------------------------------------------
# 12. USER CHAT INPUT
# --------------------------------------------------

user_input = st.chat_input(
    "Describe your IT problem here..."
)

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("AI is analyzing your issue..."):

            try:

                answer = generate_response(
                    st.session_state.messages
                )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error(
                    "Unable to generate an AI response."
                )

                st.caption(
                    "Check your internet connection, API key, "
                    "model availability and API quota."
                )

                st.code(str(error))

                st.session_state.messages.pop()

# --------------------------------------------------
# 13. TICKET GENERATION
# --------------------------------------------------

st.markdown("---")

st.subheader("🎫 IT Support Ticket Management")

if st.session_state.messages:

    latest_issue = next(
        (
            message["content"]
            for message in reversed(st.session_state.messages)
            if message["role"] == "user"
        ),
        None
    )

    if st.button(
        "Generate Support Ticket",
        use_container_width=True
    ):

        with st.spinner("Generating support ticket..."):

            try:

                ticket_details = generate_ticket(
                    latest_issue
                )

                st.session_state.ticket = {
                    "id": "IT-" + uuid.uuid4().hex[:8].upper(),
                    "date": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                    "details": ticket_details
                }

            except Exception as error:

                st.error("Unable to generate ticket.")
                st.code(str(error))

    if st.session_state.ticket:

        ticket = st.session_state.ticket

        st.success("Support ticket generated successfully!")

        st.markdown(f"**Ticket ID:** {ticket['id']}")
        st.markdown(f"**Created:** {ticket['date']}")
        st.markdown(ticket["details"])

        st.download_button(
            "Download Ticket",
            data=(
                f"Ticket ID: {ticket['id']}\n"
                f"Created: {ticket['date']}\n\n"
                f"{ticket['details']}"
            ),
            file_name=f"{ticket['id']}.txt",
            mime="text/plain"
        )

else:

    st.info("Ask the chatbot a question before generating a ticket.")

# --------------------------------------------------
# 14. FOOTER
# --------------------------------------------------

st.markdown("---")

st.caption(
    "GenAI IT Helpdesk Chatbot | "
    "Built using Python, Streamlit and Google Gemini API"
)