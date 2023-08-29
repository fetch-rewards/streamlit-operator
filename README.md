# Streamlit Operator

The Kubernetes Streamlit operator enables you deploy easily deploy your apps and keep them up in sync with your code.
With a minimal amount of config for each app, it handles deployment, plus ingress and DNS. 

It will also install a "Streamlit Hub" app in your cluster, that allows you to view all running apps as well as launch
new apps from the UI.

## Installation

Details to come

## Prerequisites

This app has been developed under the assumption that you're running a cluster on EKS in AWS. It will likely work on other clusters
with minimal changes, but this has not been tested.

## Usage

The operator is built around one StreamlitApp CRD that takes required configuration for each app. 

Currently users must specify four pieces of config:

- `name`: The name of the app. This will be used as the name of the deployment, service, ingress, and DNS record.
- `repo`: The git style URL of the repo containing the app code. This is used to clone the repo into the container. e.g. `git@github.com:MyOrg/my-app.git`
- `branch`: The branch of the repo to use. Typical usecase will be to track main, but users can also work off development branches.
- `code_dir`: The directory within the repo that contains the app code. This is used to run `streamlit run` within the container. e.g. `my-app` 
  - Note that the operator assumes your app's entrypoint is `main.py` within this directory. This will be configurable in the future.

## Architecture

![Architecture](docs/imgs/architecture.png)



## Helm Usage

[Helm](https://helm.sh) must be installed to use the charts.  Please refer to
Helm's [documentation](https://helm.sh/docs) to get started.

Once Helm has been set up correctly, add the repo as follows:

    helm repo add <alias> https://<orgname>.github.io/helm-charts

If you had already added this repo earlier, run `helm repo update` to retrieve
the latest versions of the packages.  You can then run `helm search repo
<alias>` to see the charts.

To install the <chart-name> chart:

    helm install my-<chart-name> <alias>/<chart-name>

To uninstall the chart:

    helm delete my-<chart-name>
