import os
import json
import http.client
import ssl
import logging

EXPECTED_CONTAINER_ID_LENGTH = 64
INVALID_CONTAINER_ID = "0000000000000000000000000000000000000000000000000000000000000000"
POD_NAME = os.environ.get("HOSTNAME", None)
API_SERVER_URL = os.environ.get("KUBERNETES_SERVICE_HOST", None)
API_SERVER_PORT = os.environ.get("KUBERNETES_SERVICE_PORT", None)
NAMESPACE_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
TOKEN_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/token'
CA_CERT = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
MOUNTINFO_PATH = "/proc/self/mountinfo"
CGROUP_PATH = "/proc/self/cgroup"

logger = logging.getLogger('appdynamics.agent')


def get_pod_id():
    if not os.path.exists(CA_CERT) or not os.path.exists(TOKEN_PATH) or not os.path.exists(NAMESPACE_PATH):
        logger.warning('Kube API File Path not exist')
        return None

    if API_SERVER_URL is None or API_SERVER_PORT is None or POD_NAME is None:
        logger.warning('Kube API environment variables not present')
        return None

    with open(NAMESPACE_PATH, 'r') as file:
        pod_namespace = file.read()

    context = ssl.create_default_context(cafile=CA_CERT)

    conn = http.client.HTTPSConnection(API_SERVER_URL, API_SERVER_PORT, context=context)

    headers = {
        "Authorization": "",
        "Accept": "application/json",
    }

    with open(TOKEN_PATH, 'r') as file:
        token = file.read()

    headers["Authorization"] = "Bearer {}".format(token)

    url = "/api/v1/namespaces/{}/pods/{}".format(pod_namespace, POD_NAME)

    conn.request("GET", url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    if res.status == 200:
        try:
            response = json.loads(data.decode("utf-8"))
            container_id = response["status"]["containerStatuses"][0]["containerID"].split('://')[1]

            if len(container_id) == EXPECTED_CONTAINER_ID_LENGTH:
                return container_id
            logger.warning("Unable to fetch container id from KubeApi")
            return None
        except:
            logger.warning("Unable to fetch container id from KubeApi")
            return None
    logger.warning('Unable to fetch container id from KubeApi')
    return None


def get_container_id_cgroupv2():
    if not os.path.exists(MOUNTINFO_PATH):
        logger.warning('CGroupv2 File Path not exist')
        return None

    with open(MOUNTINFO_PATH, "r") as file:
        mountinfo_contents = file.read()

    container_id = None
    lines = mountinfo_contents.split("\n")
    for line in lines:
        if "containers/" in line:
            container_id = line.split("containers/")[1].split("/")[0]
            break

    if len(container_id) == EXPECTED_CONTAINER_ID_LENGTH:
        return container_id
    logger.warning('Unable to fetch container id from CGroupv2')
    return None


def get_container_id_cgroupv1():
    logger = logging.getLogger('appdynamics.agent')

    if not os.path.exists(CGROUP_PATH):
        logger.warning('CGroupv1 File Path not exist')
        return None

    with open(CGROUP_PATH, "r") as file:
        cgroup_contents = file.read()

    container_id = None
    lines = cgroup_contents.split("\n")
    for line in lines:
        if "/docker/" in line:
            index = line.find("/docker/") + len("/docker/")

            container_id = line[index:]
            break

    if container_id and len(container_id) == EXPECTED_CONTAINER_ID_LENGTH:
        return container_id
    logger.warning('Unable to fetch container id from CGroupv1')
    return None


def get_container_id():
    # Option1: Fetch container id from kube api
    # Option2: Fetch container id from cgroupv1
    # Option3: Fetch container id from cgroupv2
    containerId = None
    try:
        containerId = get_pod_id() or get_container_id_cgroupv1() or get_container_id_cgroupv2()
    except:
        logger.warning('Container ID not found')

    if containerId is not None:
        return containerId

    return INVALID_CONTAINER_ID
