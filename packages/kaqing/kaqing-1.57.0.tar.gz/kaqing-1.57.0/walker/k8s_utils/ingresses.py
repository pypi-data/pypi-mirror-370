from kubernetes import client

from walker.utils import log2

# utility collection on ingresses; methods are all static
class Ingresses:
    def get_host(name: str, namespace: str):
        networking_v1_api = client.NetworkingV1Api()
        try:
            ingress = networking_v1_api.read_namespaced_ingress(name=name, namespace=namespace)
            return ingress.spec.rules[0].host
        except client.ApiException as e:
            print(f"Error getting Ingresses: {e}")

    def create_ingress(name: str, namespace: str, host: str, path: str, port: int, annotations: dict[str, str] = {}):
        networking_v1_api = client.NetworkingV1Api()

        body = client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(name=name, annotations=annotations),
            spec=client.V1IngressSpec(
                rules=[client.V1IngressRule(
                    host=host,
                    http=client.V1HTTPIngressRuleValue(
                        paths=[client.V1HTTPIngressPath(
                            path=path,
                            path_type="ImplementationSpecific",
                            backend=client.V1IngressBackend(
                                service=client.V1IngressServiceBackend(
                                    port=client.V1ServiceBackendPort(
                                        number=port,
                                    ),
                                    name=name)
                                )
                        )]
                    )
                )]
            )
        )

        networking_v1_api.create_namespaced_ingress(
            namespace=namespace,
            body=body
        )

    def delete_ingress(name: str, namespace: str):
        api = client.NetworkingV1Api()

        try:
            api_response = api.delete_namespaced_ingress(name=name, namespace=namespace)
            log2(f"{api_response.status} Ingress '{name}' in namespace '{namespace}' deleted successfully.")
        except client.ApiException as e:
            log2(f"Error deleting Ingress: {e}")