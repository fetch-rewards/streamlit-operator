import os
import kopf
import kubernetes
import yaml


def template_deployment(name, repo, branch, code_dir):
    path = os.path.join(os.path.dirname(__file__), "templates", 'deployment.yaml')
    tmpl = open(path, 'rt').read()
    deployment_text = tmpl.format(
        name=name,
        repo=repo,
        branch=branch,
        code_dir=code_dir
    )
    deployment_data = yaml.safe_load(deployment_text)
    return deployment_data


def template_service(name):
    path = os.path.join(os.path.dirname(__file__), "templates", 'service.yaml')
    tmpl = open(path, 'rt').read()
    service_text = tmpl.format(
        name=name,
    )
    service_data = yaml.safe_load(service_text)
    return service_data


def template_ingress(name):
    path = os.path.join(os.path.dirname(__file__), "templates", 'ingress.yaml')
    tmpl = open(path, 'rt').read()
    ingress_text = tmpl.format(
        name=name,
    )
    ingress_data = yaml.safe_load(ingress_text)
    return ingress_data


@kopf.on.create('streamlit-apps')
def create_fn(spec, name, namespace, logger, **kwargs):
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
