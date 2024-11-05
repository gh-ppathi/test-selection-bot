import streamlit as st
import pandas as pd
import base64

# Set page title
st.set_page_config(page_title="Customer Order", layout="centered")

# Function to convert local image to base64 string
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Path to your local image
image_path = "hackathonbackgroundimage.png"  # Change this to your local image path

# Get the base64 string of the image
img_base64 = get_base64_image(image_path)

# CSS to add a background image
page_bg_img = f'''
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: 100% 50%;
    background-position: top;  /* Center the image */
    background-repeat: no-repeat;  /* Do not repeat the image */
    height: 100vh;
}}
.main-container {{
    padding-right: 80px;  /* Adjust this value to move content to the right */
    padding-top: 270px;  /* Optional: Add some top padding for spacing */
}}
h1 {{
    font-size: 3em;  /* Increase the size of the main title */
}}
h2 {{
    font-size: 2.5em;  /* Increase the size of the tab headers */
}}
.stTextInput, .stNumberInput, .stButton {{
    font-size: 3.5em;  /* Increase the size of text inputs and buttons */
}}
/* Right-align the logout button */
#logout-button {{
    position: absolute;
    top: 20px;
    right: 200px;
    font-size: 1em;
    background-color: #f44336;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}}
#logout-button:hover {{
    background-color: #d32f2f;
}}
</style>
'''

# Function to check user credentials
def check_credentials(username):
    # Allow access only for specific users
    allowed_users = ["Doc1", "Doc2","salesrep1","salesrep2"]
    return username in allowed_users

# Main function for the Streamlit app
def main():
    # Login form
    if 'logged_in' not in st.session_state:
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
        st.markdown(page_bg_img, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)  # Start custom container

            # Add a logout button
            if st.button("Logout"):
                st.session_state.clear()  # Clear session state to log out the user
                st.success("You have been logged out. Please log in again.")

            # Retrieve the username from session state
            username = st.session_state.get('username', 'User')

            # Display greeting message
            st.title( f"Hi {username}, Welcome to Test Selection Assistant")


            # Ask the user if they are ordering for a new or existing customer
            st.write("***Would you like to explore GH tests for a new or existing patient?***")


            # Define tabs based on the username
            if username in ["salesrep1", "salesrep2"]:
                # Create tabs with an extra "My Territory Performance" tab for salesrep1 and salesrep2
                tabs = st.tabs(["New GH Patient", "My Territory Performance"])
                tab1, tab3 = tabs[0], tabs[1]
            else:
                # Create only "New GH Patient" and "Existing GH Patient" tabs for other users
                tabs = st.tabs(["New GH Patient", "Existing GH Patient"])
                tab1, tab2 = tabs[0], tabs[1]

            # New GH Patient Tab
            with tab1:
                st.write("Please use our GH Chatbot to explore our product suggestion")
                st.markdown('[Click here to explore product suggestions](http://35.91.174.54:8501)', unsafe_allow_html=True)

            # Existing GH Patient Tab (only accessible if not salesrep1 or salesrep2)
            if username not in ["salesrep1", "salesrep2"]:
                with tab2:
                    existing_customers = ["Patient A", "Patient B"]
                    selected_customer = st.selectbox("Select an existing Patient:", existing_customers)

                    if st.button("Submit"):
                        if selected_customer:
                            st.success(f"Looking up details for Patient: {selected_customer}")
                        else:
                            st.error("Please select a valid Patient.")

            # My Territory Performance Tab (only accessible to salesrep1 and salesrep2)
            if username in ["salesrep1", "salesrep2"]:
                with tab3:
                    st.write("Welcome to Territory Performance")
                    st.write("Here you can see your territory performance metrics.")
                    # Add additional content or metrics as required


            st.markdown('</div>', unsafe_allow_html=True)  # End custom container

if __name__ == "__main__":
    main()
