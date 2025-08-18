try:
    import kubernetes
    print(
        "kubernetes python SDK: "
        f"version {kubernetes.__version__}"
        )
    from .crud import (
        list_services,
        list_pods,
        services_to_imagetags
    )
except ImportError:
    print("kubernetes python SDK not installed")
    print("Please run `pip install kubernetes`")


try:
    import kubernetes_asyncio
    print(
        "kubernetes_asyncio python SDK: "
        f"version {kubernetes_asyncio.__version__}"
        )
    from .crud_async import (
        list_services_async, list_pods_async,
        services_to_imagetags_async
        )
except ImportError:
    print("kubernetes_asyncio python SDK not installed")
    print("Please run `pip install kubernetes_asyncio`")
