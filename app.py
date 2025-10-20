import streamlit as st
from transformers import BertTokenizer, TFBertForSequenceClassification
import tensorflow as tf
import os
import groq

# --- Page Configuration ---
st.set_page_config(
    page_title="Spam & Legitimacy Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Groq API Key Handling ---
groq_api_key = st.secrets["GROQ_API_KEY"]

# --- Caching Functions ---
@st.cache_resource
def load_model():
    """Loads the BERT model and tokenizer for spam classification."""
    model_path = os.path.join('Bert')
    tokenizer_path = os.path.join('Tokenizer')
    try:
        model = TFBertForSequenceClassification.from_pretrained(model_path)
        tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
        return model, tokenizer
    except Exception as e:
        st.error(f"Error loading spam classification model: {e}")
        return None, None

@st.cache_data
def check_company_legitimacy(company_name, api_key):
    """Queries Groq's Llama 3B model to check if a company is legitimate."""
    if not api_key:
        return "Groq API key not provided."
    try:
        client = groq.Client(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Is {company_name} a legitimate company? Provide a brief summary of your findings.",
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

# --- UI Layout ---
st.title("Spam & Legitimacy Analyzer")
st.markdown("Your all-in-one tool to classify messages and verify company legitimacy.")

# --- Main Content ---
col1, col2 = st.columns(2)

# --- Spam Classification ---
with col1:
    st.header("Spam Classifier")
    st.markdown("Enter a message to classify it as spam or not.")
    
    model, tokenizer = load_model()
    
    if model and tokenizer:
        message = st.text_area("Message:", height=150, placeholder="Enter your message here...")
        if st.button("Classify Message", key="classify"):
            if message:
                inputs = tokenizer(message, return_tensors='tf', truncation=True, padding=True, max_length=512)
                outputs = model(inputs)
                logits = outputs.logits
                prediction = tf.argmax(logits, axis=1).numpy()[0]
                
                if prediction == 1:
                    st.error("🚨 This message is classified as **Spam**.")
                else:
                    st.success("✅ This message is classified as **Ham** (Not Spam).")
            else:
                st.warning("Please enter a message to classify.")
    else:
        st.error("Spam classification model could not be loaded. Please check the model files.")

# --- Company Legitimacy Checker ---
with col2:
    st.header("Company Legitimacy Checker")
    st.markdown("Enter a company name to check if it's a legitimate entity.")
    
    company_name = st.text_input("Company Name:", placeholder="e.g., Google, Microsoft")
    
    if st.button("Check Legitimacy", key="legitimacy"):
        if company_name:
            if groq_api_key:
                with st.spinner(f"Investigating {company_name}..."):
                    legitimacy_report = check_company_legitimacy(company_name, groq_api_key)
                    st.subheader("Legitimacy Report:")
                    st.markdown(legitimacy_report)
            else:
                st.error("Please enter your Groq API key in the sidebar to use this feature.")
        else:
            st.warning("Please enter a company name.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "Created by Sarvagya"
)