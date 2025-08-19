import json
import os
import sys
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional


def _run(cmd: str, env: Optional[dict] = None):
    print(f"$ {cmd}")
    subprocess.check_call(shlex.split(cmd), env=env)


def _call_returncode(argv: List[str], env: Optional[dict] = None) -> int:
    print("$", *argv)
    return subprocess.call(argv, env=env)


def _delegate_to_official(argv: List[str]) -> int:
    """
    Delegate to official langgraph CLI for non-deploy subcommands.
    Try `python -m langgraph` first to avoid recursively calling this wrapper.
    Falls back to `langgraph` binary if module entry is absent.
    """
    env = dict(os.environ)
    env["LANGGRAPH_DEPLOY_WRAPPER_BYPASS"] = "1"

    # Prefer module form
    rc = _call_returncode([sys.executable, "-m", "langgraph", *argv], env=env)
    if rc == 0 or rc is None:
        return rc

    # Fallback to binary (in case module dispatch is unavailable)
    return _call_returncode(["langgraph", *argv], env=env)


def _read_config(cfg_path: Path) -> dict:
    if not cfg_path.exists():
        return {}
    with cfg_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _local_image_exists(tag: str) -> bool:
    try:
        out = subprocess.check_output(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"])
        images = out.decode().splitlines()
        return tag in images
    except Exception:
        return False


def _ensure_image(tag: str, cfg_file: str):
    if not _local_image_exists(tag):
        # Kick `langgraph build` via delegation (so we reuse the official implementation)
        print(f"Local image '{tag}' not found; running `langgraph build -t {tag}`...")
        rc = _delegate_to_official(["build", "-t", tag, "-c", cfg_file])
        if rc != 0:
            raise SystemExit(f"`langgraph build` failed with code {rc}")


def _resolve_image_tag(args, cfg: dict) -> str:
    if args.image:
        return args.image
    if os.environ.get("LG_IMAGE"):
        return os.environ["LG_IMAGE"]
    # Custom helper key in config (optional)
    tags = cfg.get("docker_image_tags") or []
    if isinstance(tags, list) and tags:
        return tags[0]
    return "langgraph-app:latest"


def deploy(argv: List[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="langgraph deploy", description="Deploy a LangGraph Docker image to Cloud Run")
    p.add_argument("--config", "-c", default="langgraph.json")
    p.add_argument("--image", help="Docker image tag (default resolved from config/env)")
    p.add_argument("--project", help="GCP project id")
    p.add_argument("--region", default=os.environ.get("CLOUD_RUN_REGION", "asia-northeast1"), help="Cloud Run region")
    p.add_argument("--service", required=True, help="Cloud Run service name")
    p.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8123")), help="Container port")
    p.add_argument("--min-instances", type=int, default=0)
    p.add_argument("--max-instances", type=int, default=10)
    p.add_argument("--allow-unauthenticated", action="store_true")
    p.add_argument("--cpu", default=None)
    p.add_argument("--memory", default=None)
    p.add_argument("--concurrency", type=int, default=None)
    p.add_argument("--repo", default=os.environ.get("AR_REPOSITORY", "langgraph"), help="Artifact Registry repo name")
    p.add_argument("--no-build", action="store_true", help="Do not auto-build when image is missing")
    args = p.parse_args(argv)

    cfg = _read_config(Path(args.config))
    image_tag = _resolve_image_tag(args, cfg)

    if not args.no_build:
        _ensure_image(image_tag, args.config)

    project = args.project or os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("Specify `--project` or set GCP_PROJECT / GOOGLE_CLOUD_PROJECT")

    region = args.region
    repo = args.repo

    # Compute remote tag
    if ":" in image_tag:
        name, tag = image_tag.split(":", 1)
    else:
        name, tag = image_tag, "latest"
    ar_host = f"{region}-docker.pkg.dev"
    remote = f"{ar_host}/{project}/{repo}/{name}:{tag}"

    # Push to Artifact Registry
    _run(f"gcloud auth configure-docker {ar_host} -q")
    _run(f"docker tag {image_tag} {remote}")
    _run(f"docker push {remote}")

    # Deploy to Cloud Run
    cmd = f"gcloud run deploy {args.service} --image {remote} --region {region} --platform managed --port {args.port}"
    if args.allow_unauthenticated:
        cmd += " --allow-unauthenticated"
    if args.min_instances is not None:
        cmd += f" --min-instances {args.min_instances}"
    if args.max_instances is not None:
        cmd += f" --max-instances {args.max_instances}"
    if args.cpu:
        cmd += f" --cpu {args.cpu}"
    if args.memory:
        cmd += f" --memory {args.memory}"
    if args.concurrency:
        cmd += f" --concurrency {args.concurrency}"
    if project:
        cmd += f" --project {project}"

    _run(cmd)
    print("✅ Deployed to Cloud Run")
    return 0


def main():
    # Prevent delegation loop if our wrapper ends up calling itself
    if os.environ.get("LANGGRAPH_DEPLOY_WRAPPER_BYPASS") == "1":
        # Directly attempt to run the official CLI module
        # (This path should only be reached when we explicitly delegate.)
        os.execv(sys.executable, [sys.executable, "-m", "langgraph", *sys.argv[1:]])

    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        sys.exit(deploy(sys.argv[2:]))

    # Any other subcommand -> delegate to the official CLI
    sys.exit(_delegate_to_official(sys.argv[1:]))


if __name__ == "__main__":
    main()
