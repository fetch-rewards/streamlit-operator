from kubernetes import client, config
import os

class StappClient:
    def __init__(self):
        if os.getenv('ENVIRONMENT') == 'local':
            self.config = config.load_kube_config(config_file="~/.kube/config", context="proxy")
        else:
            self.config = config.load_incluster_config()
        self.api = client.CustomObjectsApi()
        self.v1 = client.CoreV1Api()

    def list_streamlit_apps(self):
        # List instances of the custom resource
        custom_resource_list = self.api.list_namespaced_custom_object(
            group="fetch.com",
            version="v1",
            namespace="streamlit",
            plural="streamlit-apps"
        )

        outputs = []
        for item in custom_resource_list['items']:
            name = item['metadata']['name']
            outputs.append(name)
        return outputs

    def create_streamlit_app(self, name, repo, branch, code_dir):
        # Create the custom resource
        self.api.create_namespaced_custom_object(
            group="fetch.com",
            version="v1",
            namespace="streamlit",
            plural="streamlit-apps",
            body={
                "apiVersion": "fetch.com/v1",
                "kind": "StreamlitApp",
                "metadata": {
                    "name": name
                },
                "spec": {
                    "repo": repo,
                    "branch": branch,
                    "code_dir": code_dir
                }
            }
        )

    def delete_streamlit_app(self, name):
        # Delete the custom resource
        self.api.delete_namespaced_custom_object(
            group="fetch.com",
            version="v1",
            namespace="streamlit",
            plural="streamlit-apps",
            name=name,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
            )
        )

    def delete_pod_for_streamlit_app(self, name):
        # Find the pod for the custom resource
        pod_list = self.v1.list_namespaced_pod(
            namespace="streamlit",
            label_selector=f"app={name}"
        )
        print(pod_list)
        # Delete the pod
        for item in pod_list.items:
            pod_name = item.metadata.name
            self.v1.delete_namespaced_pod(
                name=pod_name,
                namespace="streamlit",
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                )
            )
