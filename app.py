import streamlit as st

# Configure the page settings
st.set_page_config(
    page_title="ECS Streamlit App", 
    page_icon="🚀", 
    layout="centered"
)

st.title("🚀 Hello from AWS ECS!")
st.write("This Streamlit application is successfully running in a Docker container on AWS Elastic Container Service.")

st.header("Deployment Details")
st.markdown("""
* **Infrastructure:** Provisioned via Terraform
* **CI/CD:** Deployed using GitHub Actions
* **Container Orchestration:** AWS ECS
""")

st.divider()

# Add some basic interactivity to test the app
name = st.text_input("Enter your name to test interactivity:")
if name:
    st.success(f"Welcome to the cloud, {name}! Your CI/CD pipeline is working perfectly.")
