from kubernetes.client.models import (
    V1Job, V1JobSpec, V1PodSpec, V1Container, 
    V1JobTemplateSpec, V1EnvFromSource, 
    V1ConfigMapEnvSource, V1EnvVar,
    V1VolumeMount, V1Volume
)


class SafeGetList(list):
    def __getitem__(self, item):
        try:
            value = super().__getitem__(item)
        except IndexError as ie:
            return None

        return value


class SafeGetDict(dict):
    def __getitem__(self, item):
        value = super().__getitem__(item)

        if isinstance(value, dict):
            return SafeGetDict(value)
        if isinstance(value, list):
            return SafeGetList(value)

        return value

    def __missing__(self, key):
        return None



def create_job(name: str, namespace: str, spec: dict, destination: str | list[str]):

    if isinstance(model_destination, str):
        model_destination = [destination]

    model_source = spec["modelSource"]

    args = (
        [f"--source={model_source}"] + 
        [f"--destination={dest}" for dest in model_destination]
    )

    job_template = SafeGetDict(spec["jobTemplate"])

    backoff_limit = job_template["backoffLimit"]
    ttl_seconds_after_finished = job_template["ttlSecondsAfterFinished"]
    restart_policy = job_template["template"]["spec"]["restartPolicy"]
    container_name = job_template["template"]["spec"]["containers"][0]["name"]
    container_image = job_template["template"]["spec"]["containers"][0]["image"]
    container_configmapref_name = job_template["template"]["spec"]["containers"][0]["envFrom"][0]["configMapRef"]["name"]


    job = V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=dict(
            name=name,
            namespace=namespace,
        ),
        spec=V1JobSpec(
            backoff_limit=backoff_limit,
            ttl_seconds_after_finished=ttl_seconds_after_finished,
            template=V1JobTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name=container_name,
                            image=container_image,
                            env=V1EnvVar(),
                            env_from=V1EnvFromSource(
                                config_map_ref=V1ConfigMapEnvSource(
                                    name=container_configmapref_name
                                )
                            ),
                            volume_mounts=V1VolumeMount(),
                            args=args,
                        )
                    ],
                    volumes=[V1Volume()],
                    restart_policy=restart_policy
                ),
            )
        ),
    )
    return job