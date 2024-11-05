import os
import uuid
import json
import logging

import boto3
import streamlit as st
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SUPPORTED_CANCER_TYPES = ["Lung", "Breast", "Colorectal", "Other"]
STAGES = ["Stage_2_3", "Stage_4"]
THERAPY_STATUSES = ["newly_diagnosed", "had_surgery", "had_therapy", "had_both", "therapy_not_working", "in_therapy"]

stage_2_3_therapy_statuses = ["Newly Diagnosed", "Had Surgery", "Had Therapy", "Had Both Surgery and Therapy"]
stage_4_therapy_statuses = ["Newly Diagnosed", "Not Responding to Therapy", "In Therapy"]

# Configuration (use environment variables or configuration files in production)
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
BEDROCK_MODEL_ID = 'anthropic.claude-3-5-sonnet-20241022-v2:0'

# Initialize Bedrock client
try:
    bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)
except Exception as e:
    logger.error(f"Error initializing Bedrock client: {e}")
    st.error("An error occurred while initializing the application. Please try again later.")
    st.stop()

# Streamlit app
st.subheader('Test Selection Assistant', divider='rainbow')

# Initialize chat history and attributes in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'attributes' not in st.session_state:
    st.session_state.attributes = {
        "cancer_type": "Unknown",
        "stage": "Unknown",
        "therapy_status": "Unknown",
    }

def recommend_guardant_test(
    cancer_type: str,
    stage: str,
    therapy_status: str,
) -> str:
    """
    Recommends a Guardant test based on the provided attributes.
    """
    recommendation = "Further assessment needed"
    
    if cancer_type in ["Lung", "Breast", "Colorectal"]:
        if stage == "Stage_2_3":
            if therapy_status == "newly_diagnosed":
                recommendation = "Guardant360 or Guardant360 CDx"
            else: 
                recommendation = "Guardant Reveal"
        elif stage == "Stage_4":
            if therapy_status == "newly_diagnosed" or therapy_status == "therapy_not_working":
                recommendation = "Guardant360 or Guardant360 CDx"
            elif therapy_status == "in_therapy":
                recommendation = "Guardant360 Response"
    else:
        recommendation = 'Guardant360 CDx & TissueNext'
    
    return recommendation
    
def extract_attributes_with_claude(chat_history: list) -> Dict[str, Any]:
    """
    Uses Bedrock Claude to extract attributes from the user's input, considering the entire chat history.
    """
    # Define the system prompt
    system_prompt = '''
You are an AI assistant that extracts specific attributes from user input.

Extract the following attributes from the user input and output them as a JSON object:

{{
    "cancer_type": "Lung" / "Breast" / "Colorectal" / "Other" / "Unknown",
    "stage": "Stage_2_3" / "Stage_4" / "Unknown",
    "therapy_status": if stage_2_3: "newly_diagnosed" / "had_surgery" / "had_therapy" / "had_both" / "Unknown"
                        if stage_4: "newly_diagnosed" / "therapy_not_working" / "in_therapy" / "Unknown",
}}
Always choose "Unknown" if the user didn't provide the information.
Make sure the output is valid JSON.'''

    # Build the messages list including the system prompt and chat history
    messages = []

    for message in chat_history:
        messages.append({
            "role": message['role'],
            "content": [{
                "type": "text",
                "text": message['text']
            }]
        })

    body = json.dumps({
        "messages": messages,
        "anthropic_version": "bedrock-2023-05-31",
        "system":            system_prompt,
        "max_tokens":        2000,
        "temperature":       0.1,
        "top_p":             0.9
    })

    try:
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            accept='application/json',
            contentType='application/json',
            body=body
        )

        response_body = json.loads(response['body'].read())
        text_output = response_body['content'][0]['text']

        # Log the text output for debugging
        logger.info(f"Text output from model: {text_output}")

        # Parse the JSON output from the model's response
        attributes = json.loads(text_output)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        logger.error(f"Text output received: {text_output}")
        st.error("An error occurred while processing your input. Please try again.")
        attributes = {}
    except Exception as e:
        logger.error(f"Error invoking Bedrock model: {e}")
        st.error("An error occurred while processing your request. Please try again later.")
        attributes = {}

    return attributes

def validate_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and normalizes the extracted attributes.
    """
    validated_attributes = {}

    # Validate 'cancer_type'
    cancer_type = attributes.get('cancer_type', 'Unknown')
    if cancer_type in SUPPORTED_CANCER_TYPES + ['Other', 'Unknown']:
        validated_attributes['cancer_type'] = cancer_type
    else:
        validated_attributes['cancer_type'] = 'Unknown'

    # Validate 'stage'
    stage = attributes.get('stage', 'Unknown')
    if stage in STAGES:
        validated_attributes['stage'] = stage
    else:
        validated_attributes['stage'] = 'Unknown'

    # Validate 'therapy_status'
    therapy_status = attributes.get('therapy_status', 'Unknown')
    if therapy_status in THERAPY_STATUSES:
        validated_attributes['therapy_status'] = therapy_status
    else:
        validated_attributes['therapy_status'] = 'Unknown'

    return validated_attributes

def all_attributes_collected(attributes: Dict[str, Any]) -> bool:
    """
    Checks if all attributes have been collected.
    """
    return all(value != "Unknown" for value in attributes.values())

def main():
    # Initialize chat history and attributes if they don't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'attributes' not in st.session_state:
        st.session_state.attributes = {'cancer_type': 'Unknown', 'stage': 'Unknown', 'therapy_status': 'Unknown'}
    
    # Display all previous chat messages
    for chat in st.session_state.chat_history:
        with st.chat_message(chat['role']):
            st.markdown(chat['text'])
    
    # Display the initial assistant message only once
    if 'welcome_message_displayed' not in st.session_state:
        with st.chat_message('assistant'):
            initial_message = "Hi! Welcome to GH Test Selection Assistant! Please start with your patient's cancer type and stage."
            st.markdown(initial_message)
        st.session_state.chat_history.append({"role": 'assistant', "text": initial_message})
        st.session_state.welcome_message_displayed = True  # Set the flag
    
    # Chat input from user
    user_input = st.chat_input('Enter your message here...')
    if user_input:
        with st.chat_message('user'):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": 'user', "text": user_input})
    
        # Use Bedrock Claude to get attributes
        extracted_attributes = extract_attributes_with_claude(chat_history=st.session_state.chat_history)
        if not extracted_attributes:
            return  # Error already handled
    
        # Validate and update attributes in session state
        validated_attributes = validate_attributes(extracted_attributes)
        for key in st.session_state.attributes:
            if validated_attributes.get(key, "Unknown") != "Unknown":
                st.session_state.attributes[key] = validated_attributes[key]
    
        # Check if all attributes are collected
        if all_attributes_collected(st.session_state.attributes):
            # Run the recommendation function
            try:
                recommendation = recommend_guardant_test(
                    cancer_type=st.session_state.attributes["cancer_type"],
                    stage=st.session_state.attributes["stage"],
                    therapy_status=st.session_state.attributes["therapy_status"],
                )
            except Exception as e:
                logger.error(f"Error in recommendation function: {e}")
                st.error("An error occurred while generating the recommendation. Please try again later.")
                return
    
            with st.chat_message('assistant'):
                st.markdown(recommendation)
            st.session_state.chat_history.append({"role": 'assistant', "text": recommendation})
    
            # Reset attributes for the next interaction
            st.session_state.attributes = {key: "Unknown" for key in st.session_state.attributes}
        else:
            for key, value in st.session_state.attributes.items():
                if value == "Unknown":
                    with st.chat_message('assistant'):
                        question = f"Can you please provide more details about: {key.replace('_', ' ')}?"
                        st.markdown(question)
                        st.session_state.chat_history.append({"role": 'assistant', "text": question})
                        if key == "cancer_type":
                            options = f"Please select from the following options: {', '.join(SUPPORTED_CANCER_TYPES)}"
                            st.markdown(options)
                            st.session_state.chat_history.append({"role": 'assistant', "text": options})
                        elif key == "stage":
                            options = f"Please select from the following options: {', '.join(STAGES)}"
                            st.markdown(options)
                            st.session_state.chat_history.append({"role": 'assistant', "text": options})
                        elif key == "therapy_status":
                            if st.session_state.attributes["stage"] == "Stage_2_3":
                                options = f"Please select from the following options: {', '.join(stage_2_3_therapy_statuses)}"
                            elif st.session_state.attributes["stage"] == "Stage_4":
                                options = f"Please select from the following options: {', '.join(stage_4_therapy_statuses)}"
                            st.markdown(options)
                            st.session_state.chat_history.append({"role": 'assistant', "text": options})

if __name__ == '__main__':
    main()