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
SUPPORTED_CANCER_TYPES = ["Lung", "Breast", "Colorectal"]
STAGES = ["Stage_1", "Stage_2", "Stage_3", "Stage_4", "Metastatic", "Unknown"]
THERAPY_STATUSES = ["therapy_not_working", 'therapy_working', 'newly_diagnosed', "Unknown"]
BOOLEAN_VALUES = ["true", "false", "Unknown"]
LINE_OF_THERAPY_OPTIONS = ["1st", "2nd", "3rd or later", "Unknown"]

# Configuration (use environment variables or configuration files in production)
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
BEDROCK_MODEL_ID = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
SESSION_ID = str(uuid.uuid4())

# Initialize Bedrock client
try:
    bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')
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
        "recent_surgery": "Unknown",
        "line_of_therapy": "Unknown",
        "tissue_testing_preference": "Unknown"
    }

def recommend_guardant_test(
    cancer_type: str,
    stage: str,
    therapy_status: str,
    recent_surgery: bool,
    line_of_therapy: str,
    tissue_testing_preference: bool
) -> str:
    """
    Recommends a Guardant test based on the provided attributes.
    """
    recommendation = "Further assessment needed"

    if stage == 'Stage_4' or stage == 'Metastatic':
        if therapy_status == 'therapy_not_working' or therapy_status == 'newly_diagnosed':
            recommendation = "Guardant360 CDx"
        elif therapy_status == 'responding_well':
            recommendation = "Guardant Monitoring Response"
    else:
        
        

def all_attributes_collected(attributes: Dict[str, Any]) -> bool:
    """
    Checks if all attributes have been collected.
    """
    return all(value != "Unknown" for value in attributes.values())

def extract_attributes_with_claude(chat_history: list) -> Dict[str, Any]:
    """
    Uses Bedrock Claude to extract attributes from the user's input, considering the entire chat history.
    """
    # Define the system prompt
    system_prompt = '''
You are an AI assistant that extracts specific attributes from user input.

Extract the following attributes from the user input and output them as a JSON object, and only output the JSON object with no additional text:

{
    "cancer_type": "Lung" / "Breast" / "Colorectal" / "Other" / "Unknown",
    "stage": "Stage_1" / "Stage_2" / "Stage_3" / "Stage_4" / "Metastatic" / "Unknown",
    "therapy_status": "therapy_not_working" / 'therapy_working' / 'newly_diagnosed' / "Unknown",
    "recent_surgery": "true" / "false" / "Unknown",
    "line_of_therapy": "1st" / "2nd" / "3rd or later" / "Unknown",
    "tissue_testing_preference": "true" / "false" / "Unknown"
}
Always choose "Unknown" if the user didn't provide the information.
Make sure the output is valid JSON.'''

    # Build the messages list including the system prompt and chat history
    messages = []

    # Add system prompt as a message
    # messages.append({
    #     "role": "system",
    #     "content": [{
    #         "type": "text",
    #         "text": system_prompt
    #     }]
    # })

    # Add chat history messages
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

    # Validate 'recent_surgery'
    recent_surgery = attributes.get('recent_surgery', 'Unknown')
    if recent_surgery in BOOLEAN_VALUES:
        validated_attributes['recent_surgery'] = recent_surgery
    else:
        validated_attributes['recent_surgery'] = 'Unknown'

    # Validate 'line_of_therapy'
    line_of_therapy = attributes.get('line_of_therapy', 'Unknown')
    if line_of_therapy in LINE_OF_THERAPY_OPTIONS:
        validated_attributes['line_of_therapy'] = line_of_therapy
    else:
        validated_attributes['line_of_therapy'] = 'Unknown'

    # Validate 'tissue_testing_preference'
    tissue_testing_preference = attributes.get('tissue_testing_preference', 'Unknown')
    if tissue_testing_preference in BOOLEAN_VALUES:
        validated_attributes['tissue_testing_preference'] = tissue_testing_preference
    else:
        validated_attributes['tissue_testing_preference'] = 'Unknown'

    return validated_attributes

def main():
    # Chat input from user
    user_input = st.chat_input('Enter your questions here...')
    if user_input:
        with st.chat_message('user'):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": 'user', "text": user_input})

        # Use Bedrock Claude to get attributes
        extracted_attributes = extract_attributes_with_claude(st.session_state.chat_history)
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
                    recent_surgery=st.session_state.attributes["recent_surgery"] == "true",
                    line_of_therapy=st.session_state.attributes["line_of_therapy"],
                    tissue_testing_preference=st.session_state.attributes["tissue_testing_preference"] == "true"
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
            # Ask for more information
            missing_info = [key.replace('_', ' ') for key, value in st.session_state.attributes.items() if value == "Unknown"]
            follow_up_question = f"Can you please provide more details about: {', '.join(missing_info)}?"

            with st.chat_message('assistant'):
                st.markdown(follow_up_question)
            st.session_state.chat_history.append({"role": 'assistant', "text": follow_up_question})

if __name__ == '__main__':
    main()