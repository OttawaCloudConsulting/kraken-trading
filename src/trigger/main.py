import os
import logging
from datetime import datetime

from fastapi import FastAPI, Response, status
from kubernetes import client, config
from kubernetes.client.rest import ApiException

CRONJOB_NAME = os.getenv("CRONJOB_NAME")
TARGET_NAMESPACE = os.getenv("TARGET_NAMESPACE")

app = FastAPI()

def configure_logger() -> logging.Logger:
    """Configures and returns the logger instance.

    Returns:
        A configured logger instance.
    """
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.info(f"🛠️ Logging level set to: {log_level}")
    return logger

logger = configure_logger()

if not CRONJOB_NAME:
    logger.error("❌ CRONJOB_NAME environment variable is not set.")
    raise RuntimeError("CRONJOB_NAME environment variable is required.")

if not TARGET_NAMESPACE:
    logger.error("❌ TARGET_NAMESPACE environment variable is not set.")
    raise RuntimeError("TARGET_NAMESPACE environment variable is required.")

@app.post("/trigger-sync")
def trigger_sync(response: Response):
    """Endpoint to manually trigger a job from the defined CronJob."""
    logger.info("🔁 Triggering sync from CronJob: %s", CRONJOB_NAME)

    try:
        # Load in-cluster Kubernetes config
        config.load_incluster_config()
        batch_v1 = client.BatchV1Api()

        # Retrieve the existing CronJob to copy its spec
        cronjob = batch_v1.read_namespaced_cron_job(name=CRONJOB_NAME, namespace=TARGET_NAMESPACE)

        # Construct a new Job from the CronJob template
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        job_name = f"{CRONJOB_NAME}-manual-{timestamp}"

        job = client.V1Job(
            metadata=client.V1ObjectMeta(
                name=job_name,
                labels={
                    "job-origin": "manual-trigger"
                },
            ),
            spec=client.V1JobSpec(
                template=cronjob.spec.job_template.spec,
                backoff_limit=cronjob.spec.job_template.spec.backoff_limit or 1
            )
        )

        # Create the Job in the namespace
        batch_v1.create_namespaced_job(namespace=TARGET_NAMESPACE, body=job)
        logger.info("✅ Manual job %s successfully created.", job_name)
        return {"message": "Manual job triggered successfully.", "job_name": job_name}

    except ApiException as e:
        logger.error("❌ Kubernetes API error: %s", e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Kubernetes API error", "details": str(e)}

    except Exception as ex:
        logger.error("❌ Unexpected error: %s", ex)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Unexpected error", "details": str(ex)}

def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()

