from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.api_client import ApiClient
from forgebox.unpack import Unpack
import pandas as pd
from .utils import calc_delta
from typing import Dict, List


async def list_services_async(
    namespace: str
) -> pd.DataFrame:
    """
    Return the service list within the namespace
    The async version
    """
    await config.load_kube_config()

    async with ApiClient() as api_client:
        v1 = client.CoreV1Api(api_client)
        endpoint_res = await v1.list_namespaced_endpoints(namespace=namespace)
        services = list()
        for ep in endpoint_res.items:
            name, ports, version, create_ts = Unpack(ep.to_dict())(
                ["metadata", "name"],
                ["subsets", 0, "ports"],
                ["metadata", "resource_version"],
                ["metadata", "creation_timestamp"]
            )
            services.append(
                dict(
                    name=name,
                    ports=ports,
                    version=version,
                    create_ts=create_ts
                )
            )
        services_df = pd.DataFrame(services)
        services_df['age'] = services_df.create_ts.apply(calc_delta)
        return services_df


async def list_pods_async(
    namespace: str
) -> pd.DataFrame:
    await config.load_kube_config()

    async with ApiClient() as api_client:
        v1 = client.CoreV1Api(api_client)
        k8_res = await v1.list_namespaced_pod(namespace=namespace)
        pods = list()
        for item in k8_res.items:
            data = dict(zip(
                ["name", "version", "app", "created_ts",
                 "image", "ready", "started"],
                Unpack(item.to_dict())(
                    ["metadata", "name"],
                    ["metadata", "resource_version"],
                    ["metadata", "labels", "app"],
                    ["metadata", "creation_timestamp"],
                    ["spec", "containers", 0, "image"],
                    ["status", "container_statuses", 0, "ready"],
                    ["status", "container_statuses", 0, "started"],
                )))
            pods.append(data)
        pods_df = pd.DataFrame(pods)
        pods_df["image_tag"] = (
            pods_df["image"]
            .apply(lambda x: x.split("/")[1])
        )
        pods_df["age"] = pods_df["created_ts"].apply(calc_delta)
        return pods_df


async def services_to_imagetags_async(namespace: str) -> Dict[str, List[str]]:
    """
    Given a service name, return the image tag
    """
    await config.load_kube_config()

    async with ApiClient() as api_client:
        v1 = client.CoreV1Api(api_client)
        k8_res = await v1.list_namespaced_pod(namespace=namespace)
        services = dict()
        for item in k8_res.items:
            name, image = Unpack(item.to_dict())(
                ["metadata", "labels", "app"],
                ["spec", "containers", 0, "image"],
            )
            if name not in services:
                services[name] = list()
            services[name].append(image.split("/")[1])
        return services
