import kubernetes.client as kube_client

TRITON_HTTP_PORT = 8000
TRITON_SERVICE_NAME = "tritonserver"

TRITON_LABEL_SELECTOR = "app=tritonserver"
OPERATOR_CONFIGMAP_NAME = "operator-config"


def get_list_triton_pod_ip(namespace: str, port: int | str = TRITON_HTTP_PORT) -> list[str]:
    api = kube_client.CoreV1Api()
    pods: kube_client.V1PodList = api.list_namespaced_pod(namespace=namespace, label_selector=TRITON_LABEL_SELECTOR)

    ips = []
    for pod in pods.items:
        ip: kube_client.V1PodStatus = pod.status.pod_ip
        if port:
            ips.append(f"{ip}:{port}")
        else:
            ips.append(ip)

    return ips


def get_config_map_data(namespace: str, name: str) -> dict[str, str] | None:
    api = kube_client.CoreV1Api()
    config_maps: kube_client.V1ConfigMapList = api.list_namespaced_config_map(namespace=namespace)

    for config_map in config_maps.items:
        config_map: kube_client.V1ConfigMap

        metadata: kube_client.V1ObjectMeta = config_map.metadata
        if metadata.name == name:
            return config_map.data


