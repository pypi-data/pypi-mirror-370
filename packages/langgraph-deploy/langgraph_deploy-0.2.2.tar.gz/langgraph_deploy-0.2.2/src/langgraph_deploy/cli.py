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


def _check_output(argv: List[str], env: Optional[dict] = None) -> subprocess.CompletedProcess:
    print("$", *argv)
    cp = subprocess.run(argv, env=env, capture_output=True, text=True)
    return cp


def _delegate_to_official(argv: List[str]) -> int:
    """
    Delegate to official langgraph CLI for non-deploy subcommands.
    Try `python -m langgraph` first to avoid recursively calling this wrapper.
    Falls back to `langgraph` binary if module entry is absent.
    """
    env = dict(os.environ)
    env["LANGGRAPH_DEPLOY_WRAPPER_BYPASS"] = "1"

    rc = _call_returncode([sys.executable, "-m", "langgraph", *argv], env=env)
    if rc == 0 or rc is None:
        return rc

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


def _ensure_image(tag: str, cfg_file: str, prefer_shell: bool = False):
    if _local_image_exists(tag):
        return
    print(f"Local image '{tag}' not found; building...")
    if prefer_shell:
        # Transparently show the exact shell command (as in v1)
        _run(f"langgraph build -t {tag} -c {cfg_file}")
    else:
        # Safer: delegate to the official module to avoid PATH shadowing recursion
        rc = _delegate_to_official(["build", "-t", tag, "-c", cfg_file])
        if rc != 0:
            raise SystemExit(f"`langgraph build` failed with code {rc}")


def _resolve_image_tag(args, cfg: dict) -> str:
    if args.image:
        return args.image
    if os.environ.get("LG_IMAGE"):
        return os.environ["LG_IMAGE"]
    tags = cfg.get("docker_image_tags") or []
    if isinstance(tags, list) and tags:
        return tags[0]
    return "langgraph-app:latest"


def _ensure_apis(project: str):
    apis = ["artifactregistry.googleapis.com", "run.googleapis.com"]
    _run(f"gcloud services enable {' '.join(apis)} --project {project} -q")


def _repo_exists(repo: str, project: str, region: str) -> bool:
    cp = _check_output([
        "gcloud", "artifacts", "repositories", "describe", repo,
        "--location", region, "--project", project, "--format=value(name)"
    ])
    return cp.returncode == 0 and cp.stdout.strip() != ""


def _ensure_repo(repo: str, project: str, region: str, fmt: str = "docker", description: Optional[str] = None):
    if _repo_exists(repo, project, region):
        print(f"Artifact Registry repository '{repo}' already exists in {region}.")
        return
    print(f"Artifact Registry repository '{repo}' not found in {region}; creating...")
    cmd = f"gcloud artifacts repositories create {repo} --repository-format={fmt} --location={region} --project {project} -q"
    if description:
        cmd += f" --description {shlex.quote(description)}"
    _run(cmd)
    print(f"✅ Created Artifact Registry repo: {repo} ({fmt}, {region})")


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
    p.add_argument("--no-create-repo", action="store_true", help="Do not create Artifact Registry repository automatically")
    p.add_argument("--no-enable-apis", action="store_true", help="Skip enabling Artifact Registry / Cloud Run APIs")
    p.add_argument("--build-via-shell", action="store_true", help="Run `langgraph build` via shell for transparent logs")
    args = p.parse_args(argv)

    cfg = _read_config(Path(args.config))
    image_tag = _resolve_image_tag(args, cfg)

    prefer_shell_build = args.build_via_shell or os.environ.get("LG_DEPLOY_SHELL_BUILD") == "1"

    if not args.no_build:
        _ensure_image(image_tag, args.config, prefer_shell=prefer_shell_build)

    project = args.project or os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("Specify `--project` or set GCP_PROJECT / GOOGLE_CLOUD_PROJECT")

    region = args.region
    repo = args.repo

    if not args.no_enable_apis:
        _ensure_apis(project)

    if not args.no_create_repo:
        _ensure_repo(repo, project, region, fmt="docker", description="created by langgraph-deploy")

    # Compute remote tag and push
    if ":" in image_tag:
        name, tag = image_tag.split(":", 1)
    else:
        name, tag = image_tag, "latest"
    ar_host = f"{region}-docker.pkg.dev"
    remote = f"{ar_host}/{project}/{repo}/{name}:{tag}"

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

    cmd += " --command=\"langgraph\",\"up\""
    cmd += " --set-env-vars \"REDIS_URL=redis://localhost:6379\""
    cmd += " --set-env-vars \"DATABASE_URL=sqlite:///./db.sqlite3\""
    _run(cmd)
    print("✅ Deployed to Cloud Run")
    return 0


def main():
    if os.environ.get("LANGGRAPH_DEPLOY_WRAPPER_BYPASS") == "1":
        os.execv(sys.executable, [sys.executable, "-m", "langgraph", *sys.argv[1:]])

    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        sys.exit(deploy(sys.argv[2:]))

    sys.exit(_delegate_to_official(sys.argv[1:]))


if __name__ == "__main__":
    main()
