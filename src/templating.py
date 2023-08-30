import os

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


def template_ingress(name, base_dns_path):
    dns_name = f"{name}-streamlit.{base_dns_path}"
    ingress_dict = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"{name}",
            "annotations": {
                "alb.ingress.kubernetes.io/scheme": "internal",
                "alb.ingress.kubernetes.io/target-type": "ip",
                "alb.ingress.kubernetes.io/listen-ports": '[{"HTTP": 80}, {"HTTPS":443}]',
                "alb.ingress.kubernetes.io/ssl-redirect": "443",
                "external-dns.alpha.kubernetes.io/hostname": dns_name,
                # TODO: Allow users to pass through these annotations from the chart level
                # "alb.ingress.kubernetes.io/inbound-cidrs": "<REPLACE ME>",
                # "alb.ingress.kubernetes.io/certificate-arn": "<FIGURE OUT IF THIS IS NEEDED>"
            },
            "namespace": "streamlit"
        },
        "spec": {
            "ingressClassName": "alb",
            "rules": [
                {
                    "host": dns_name,
                    "http": {
                        "paths": [
                            {
                                "path": "/*",
                                "pathType": "ImplementationSpecific",
                                "backend": {
                                    "service": {
                                        "name": f"{name}",
                                        "port": {
                                            "number": 80
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    return ingress_dict
