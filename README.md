# Model Deployment Operator

## Overview

The Model Deployment Operator is a prototype system designed to automate the deployment and management of Nvidia Triton models on Kubernetes. By using configuration files stored in a Git repository, the system ensures that model deployments are consistent, version-controlled, and easily auditable. This approach simplifies the process of updating models, rolling back changes, and maintaining a history of deployments, making it easier to manage machine learning models at scale.

## Features & Current State

- **Early Prototype**: The project is in its early prototype stage and may not work as expected.
- **Deployment Scripts**: Scripts for deploying models are included, but more features and refinements are planned.
- **Documentation**: Basic documentation is available, but will be expanded as the project evolves.
- **Custom CRD Generation**: Uses Pydantic models to easily create and manage Custom Resource Definitions (CRDs) for Kubernetes.
- **Triton Model Config JSON Schema**: Provides a pre-built JSON schema for configuring Triton models, generated from the official model configuration protocol.
- **Protobuf Conversion Tools**: Includes tools to convert protobuf messages into JSON or YAML formats, making it easier to work with different data formats.

## Getting Started

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/ogvalt/model-deployment-operator.git
    ```

2. **Navigate to the Directory**:
    ```bash
    cd model-deployment-operator
    ```

3. **Follow the Examples**: Check the `examples` directory for sample configurations and deployment scripts.

4. **Deploy Using Helm**:
    ```bash
    helm install model-deployment-operator ./helm
    ```

## Contributing

Contributions are welcome! Please open issues and pull requests to help improve this project.

## References

1. [How to check what branches a commit belongs to](https://stackoverflow.com/questions/7131703/how-to-know-which-branch-a-git-log-commit-belongs-to)


## Research
1. How to create CRD from pydantic model:
   * https://github.com/nolar/kopf/issues/524
   * https://github.com/asteven/kopf_resources/blob/master/kopf_resources/registry.py