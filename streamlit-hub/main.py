import streamlit as st
from stapp_client import StappClient

st.title("Streamlit Hub")

stapp_client = StappClient()
apps = stapp_client.list_streamlit_apps()

for idx, item in enumerate(apps):
    if item != "hub":
        st.divider()
        with st.container():
            name = item
            st.write(f"Name: {name}")
            #TODO: Get this from a configmap or something, should be specified on the helm install
            st.write(f"URL: https://{name}-streamlit.<YOURDOMAIN>")
            if st.button(f"Restart app {name}"):
                stapp_client.delete_pod_for_streamlit_app(name)
                st.write("Restarting app...")
            if st.button(f"DANGER!!!: Delete {name}"):
                stapp_client.delete_streamlit_app(name)
                st.write(f"Deleted {name}")
                st.write("Make take a minute or two to clear from UI")



with st.sidebar:
    st.header("Create a new Streamlit App")
    st.write("Create a new Streamlit App by filling out the form below.")
    st.write("Note: This will take a few minutes to build and deploy.")

    app_name = st.text_input("App Name (EX: my-app)")
    repo = st.text_input("Git Repo URL (EX: git@bitbucket.org\:<YOURCOMPANY>/<YOURPROJECT>.git)")
    branch = st.text_input("Git Branch (EX: feature/my-dev-branch)")
    code_dir = st.text_input("Code Directory (EX: src/streamlit-app)")

    #check that all fields are filled out
    if not app_name:
        st.error("App Name is required")
    if not repo:
        st.error("Git Repo URL is required")
    if not branch:
        st.error("Git Branch is required")
    if not code_dir:
        st.error("Code Directory is required")

    if app_name and repo and branch and code_dir:
        if st.button("Create Streamlit App"):
             # Create the custom resource
            stapp_client.create_streamlit_app(app_name, repo, branch, code_dir)

