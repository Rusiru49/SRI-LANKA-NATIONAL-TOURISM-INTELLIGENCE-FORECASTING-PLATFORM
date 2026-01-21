# Updated streamlit_app.py with new color palette for professional dark theme

# Importing necessary libraries
import streamlit as st
# other imports...

# Set the page configuration
st.set_page_config(page_title='SRI LANKA NATIONAL TOURISM INTELLIGENCE', layout='wide')

# CSS to set professional dark theme colors
st.markdown('''
<style>
/* Background color */
body {
    background-color: #121212;
}

/* Tabs & buttons */
.stTabs [class*='stText'] {
    color: #E8EAF0;
}
.stButton, .stTabs [class*='stTab'] {
    background-color: #4A90E2;
    color: #FFFFFF;
}

/* Badges & indicators */
.stBadge {
    background-color: #7B68EE;
    color: #E8EAF0;
}

/* Headers */
h1, h2, h3 {
    color: #FFFFFF;
}

/* Text colors */
.stText {
    color: #E8EAF0;
}

/* Success messages */
.stSuccess {
    color: #50C878;
}
</style>
''', unsafe_allow_html=True)

# Your application logic, components, etc.

# Example component
st.title('SRI LANKA NATIONAL TOURISM INTELLIGENCE')
# other application code...