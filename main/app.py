import streamlit as st
import pandas as pd
import base64
import warnings
warnings.filterwarnings("ignore")

# Set page title and layout
st.set_page_config(page_title="Customer Order", layout="wide")

# CSS to style the logout button and align it to the right
page_bg_img = '''
<style>
/* Style for the title and logout button container */
.title-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Style for the logout button */
div.stButton > button {
    background-color: #f44336;
    color: white;
    padding: 2px 8px;
    border: none;
    border-radius: 2px;
    cursor: pointer;
}

div.stButton > button:hover {
    background-color: #d32f2f;
}

/* Increase font sizes */
h1 {
    font-size: 2.5em;  /* Adjusted size to fit better inline */
}
</style>
'''

# Function to check user credentials
def check_credentials(username):
    # Allow access only for specific users
    allowed_users = ["Doc1", "Doc2", "salesrep1", "salesrep2"]
    return username in allowed_users

# Main function for the Streamlit app
def main():
    # Apply custom CSS
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Login form
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.title("Please enter your login information")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                # For this example, we don't check the password
                if check_credentials(username):
                    st.session_state.logged_in = True
                    st.session_state.username = username  # Store the username in the session state
                else:
                    st.error("Invalid username or password.")
    else:
        # App content wrapped in a container for custom styling
        with st.container():
            # Create columns to adjust content position
            spacer_col, main_col = st.columns([1, 15])  # Adjusted ratios to make content wider and shift it right

            with main_col:
                # Container for the title and logout button
                title_placeholder = st.empty()
                with title_placeholder.container():
                    # Create a horizontal layout with title and logout button
                    title_col, logout_col = st.columns([15, 1])

                    # Retrieve the username from session state
                    username = st.session_state.get('username', 'User')

                    # Display greeting message
                    names = {
                        "Doc1": "Dr. Smith",
                        "Doc2": "Dr. Johnson",
                        "salesrep1": "Rob",
                        "salesrep2": "Alice"
                    }
                    territory = {
                        'salesrep1': 'Albany',
                        'salesrep2': 'San Francisco'
                    }
                    region = {
                        'salesrep1': 'Northeast',
                        'salesrep2': 'West'
                    }

                    # Safely get the display name
                    user_display_name = names.get(username, username)

                    with title_col:
                        st.markdown(f"<h1>Hi {user_display_name}, Welcome to Test Selection Assistant</h1>", unsafe_allow_html=True)

                    with logout_col:
                        st.write("")  # Add some vertical space
                        if st.button("Logout"):
                            st.session_state.clear()  # Clear session state to log out the user
                            st.success("You have been logged out. Please log in again.")
                            st.rerun()  # Refresh the app to reflect the logged-out state

                # Ask the user if they are ordering for a new or existing customer
                st.write("***Would you like to explore GH tests for a new or existing patient?***")

                # Define tabs based on the username
                if username in ["salesrep1", "salesrep2"]:
                    # Create tabs with an extra "My Territory Performance" tab for sales reps
                    tabs = st.tabs(["New GH Patient", "Sales Enhancer"])
                    tab1, tab3 = tabs[0], tabs[1]
                else:
                    # Create "New GH Patient" and "Existing GH Patient" tabs for other users
                    tabs = st.tabs(["New GH Patient", "Existing GH Patient"])
                    tab1, tab2 = tabs[0], tabs[1]

                # New GH Patient Tab
                with tab1:
                    st.write("Please use our GH Chatbot to explore our product portfolio and select the best test for your patient.")
                    # Use st.markdown with HTML link
                    st.markdown('<a href="http://35.91.174.54:8501" target="_blank"><button style="font-size:20px;">GH Test Selection Assistant</button></a>', unsafe_allow_html=True)

                # Existing GH Patient Tab (only for doctors)
                if username not in ["salesrep1", "salesrep2"]:
                    with tab2:
                        existing_customers = ["Patient A", "Patient B"]
                        selected_customer = st.selectbox("Select an existing Patient:", existing_customers)

                        if selected_customer == "Patient A":
                            st.header('Patient Summary:')
                            st.write('Patient A with CRC cancer started the journey at GH during stage III with a single **Reveal** monitoring test and came back when the cancer progressed to stage IV for **G360**. They then got on the 1st line lung and had no response to therapy thus getting an other **G360** and are currently following up with **Reveal**.')
                            st.image('https://2024-q4-hackathon-team5.s3.us-west-2.amazonaws.com/images/Patient+1.png', caption="Patient A's Patient Journey")
                        elif selected_customer == "Patient B":
                            st.header('Patient Summary:')
                            st.write('Patient B came in during late stage with CRC cancer and ordered **G360** and are currently monitoring through **Reveal** test. ')
                            st.image('https://2024-q4-hackathon-team5.s3.us-west-2.amazonaws.com/images/Patient+2.png', use_column_width=True, caption="Patient B's Patient Journey")

                # My Territory Performance Tab (only for sales reps)
                if username in ["salesrep1", "salesrep2"]:
                    with tab3:
                        st.title(f'{names[username]}, Here is your **{territory[username]}** Territory Overview')
                        st.image('https://2024-q4-hackathon-team5.s3.us-west-2.amazonaws.com/images/Field+Rep+Persona+at+NPI.png', caption="My Territory Performance")

if __name__ == "__main__":
    main()