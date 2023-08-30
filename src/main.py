import kopf
import kubernetes

from src.templating import template_deployment, template_service, template_ingress


@kopf.on.create('streamlit-apps')
def create_fn(spec, name, namespace, logger, **kwargs):
    # Override the namespace, since the operator won't have permissions to create the apps anywhere else anyway
    namespace = "streamlit"

    # Get params from spec
    repo = spec.get('repo', None)
    branch = spec.get('branch', None)
    code_dir = spec.get('code_dir', None)

    if not repo:
        raise kopf.PermanentError(f"Repo must be set. Got {repo!r}.")
    if not branch:
        raise kopf.PermanentError(f"Branch must be set. Got {branch!r}.")
    if not code_dir:
        raise kopf.PermanentError(f"Code directory must be set. Got {code_dir!r}.")

    # Template the deployment
    deployment_data = template_deployment(name, repo, branch, code_dir)
    kopf.adopt(deployment_data)

    # Template the service
    service_data = template_service(name)
    kopf.adopt(service_data)

    # Template the ingress
    ingress_data = template_ingress(name)
    kopf.adopt(ingress_data)

    api = kubernetes.client.CoreV1Api()
    apps_api = kubernetes.client.AppsV1Api()
    networking_api = kubernetes.client.NetworkingV1Api()
    # Create the deployment
    deployment_obj = apps_api.create_namespaced_deployment(
        namespace=namespace,
        body=deployment_data,
    )

    # Create the service
    service_obj = api.create_namespaced_service(
        namespace=namespace,
        body=service_data,
    )

    # Create the ingress
    ingress_obj = networking_api.create_namespaced_ingress(
        namespace=namespace,
        body=ingress_data,
    )

    return {
        'ingress-name': ingress_obj.metadata.name,
        'service-name': service_obj.metadata.name,
        'deployment-name': deployment_obj.metadata.name
    }
