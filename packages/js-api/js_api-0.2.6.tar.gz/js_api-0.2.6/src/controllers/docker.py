from fastapi import APIRouter, HTTPException, Security

from util import docker
from util.auth import get_token_header

router = APIRouter(prefix="/docker", dependencies=[Security(get_token_header)])


@router.get("/")
async def get_latest_docker_version(docker_image: str):
    if docker_image.strip() == "":
        raise HTTPException(
            status_code=422, detail="Missing docker_image query parameter"
        )
    docker_parts = docker_image.split(":")
    current_version = ""
    if len(docker_parts) > 1:
        current_version = docker_parts[-1]
    image = docker_image.split(":")[0]
    latest_version = docker.get_latest_docker_image(image)
    if latest_version is None:
        raise HTTPException(
            status_code=404, detail=f"{docker_image} not found in Docker Hub"
        )
    newer_version = latest_version != current_version
    return {
        "image": f"{image}:{latest_version}",
        "latest_image_version": latest_version,
        "newer_version": newer_version,
    }
