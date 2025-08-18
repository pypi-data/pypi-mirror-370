import re

import httpx

images = [
    "adguard/adguardhome",
    "louislam/dockge",
    "jc21/nginx-proxy-manager",
    "portainer/portainer-ce",
    "louislam/uptime-kuma",
    "vaultwarden/server",
]


def get_latest_docker_image(image: str) -> str | None:
    version_regex = re.compile(r"\w?(\d*\.+\d*)+")
    url = "https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags"
    if "/" in image:
        namespace = image.split("/")[0]
        repository = image.split("/")[1]
    else:
        namespace = "library"
        repository = image
    formatted_url = url.format(namespace=namespace, repository=repository)
    latest_response = httpx.get(f"{formatted_url}/latest")
    digest = ""
    if latest_response.status_code == 200 and "digest" in latest_response.json():
        digest = latest_response.json()["digest"]
    response = httpx.get(f"{formatted_url}", params={"page_size": 100})
    if response.status_code == 200:
        for docker_image in response.json()["results"]:
            if (
                "digest" in docker_image
                and "name" in docker_image
                and docker_image["digest"] == digest
            ):
                if docker_image["name"] != "latest" and re.fullmatch(
                    version_regex, docker_image["name"]
                ):
                    return docker_image["name"]
    return None
