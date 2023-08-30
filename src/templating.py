import os

import yaml


def template_deployment(name, repo, branch, code_dir):
    deployment_dict = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{name}",
            "namespace": "streamlit",
            "labels": {
                "app": f"{name}"
            }
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": f"{name}"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": f"{name}"
                    }
                },
                "spec": {
                    "serviceAccountName": "streamlit-serviceaccount",
                    "containers": [
                        {
                            "name": "git-sync",
                            "image": "registry.k8s.io/git-sync:v3.1.3",
                            "volumeMounts": [
                                {
                                    "name": "code",
                                    "mountPath": "/tmp/code"
                                }
                            ],
                            "env": [
                                {"name": "GIT_SYNC_REPO", "value": f"{repo}"},
                                {"name": "GIT_SYNC_BRANCH", "value": f"{branch}"},
                                {"name": "GIT_SYNC_ROOT", "value": "/tmp/code"},
                                {"name": "GIT_SYNC_DEST", "value": "repo"},
                                {"name": "GIT_KNOWN_HOSTS", "value": "false"},
                                {"name": "GIT_SYNC_WAIT", "value": "60"}
                            ]
                        },
                        {
                            "name": "streamlit",
                            "image": "python:3.9-slim",
                            "env": [
                                {"name": "IN_HUB", "value": "True"},
                                {"name": "CODE_DIR", "value": f"repo/{code_dir}"},
                                {"name": "ENTRYPOINT", "value": "main.py"}
                            ],
                            "command": ["/app/launch/launch.sh"],
                            "ports": [{"containerPort": 80}],
                            "volumeMounts": [
                                {"name": "code", "mountPath": "/app"},
                                {"name": "launch", "mountPath": "/app/launch"}
                            ]
                        }
                    ],
                    "volumes": [
                        {"name": "code", "emptyDir": {}},
                        {
                            "name": "launch",
                            "configMap": {
                                "name": "streamlit-launch-script",
                                "defaultMode": "0500"
                            }
                        }
                    ]
                }
            }
        }
    }
    return deployment_dict


def template_service(name):
    service_dict = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{name}",
            "namespace": "streamlit"
        },
        "spec": {
            "ports": [
                {
                    "port": 80,
                    "targetPort": 80,
                    "protocol": "TCP"
                }
            ],
            "type": "NodePort",
            "selector": {
                "app": f"{name}"
            }
        }
    }
    return service_dict


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
