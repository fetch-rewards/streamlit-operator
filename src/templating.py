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
                                "defaultMode": 0o500
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
            "type": "ClusterIP",
            "selector": {
                "app": f"{name}"
            }
        }
    }
    return service_dict


def template_ingress(name, base_dns_path, ingress_annotations, suffix):
    dns_name = f"{name}{suffix}.{base_dns_path}"
    ingress_annotations = ingress_annotations or {}
    ingress_dict = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"{name}",
            "annotations": {
                "nginx.ingress.kubernetes.io/proxy-read-timeout": "3600",
                "nginx.ingress.kubernetes.io/proxy-send-timeout": "3600",
                "nginx.ingress.kubernetes.io/proxy-http-version": "1.1",
                "nginx.ingress.kubernetes.io/upstream-hash-by": "$arg_session_id",
                **ingress_annotations
            },
            "namespace": "streamlit"
        },
        "spec": {
            "ingressClassName": "nginx",
            "rules": [
                {
                    "host": dns_name,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
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
