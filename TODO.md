# ✅ Manual Trigger Feature - Implementation Checklist

This checklist tracks all the required tasks to implement an internal sync trigger for the Kraken Trading API using a Kubernetes CronJob.

---

## 📌 Configuration & Design

- [x] Define architecture and behavior of the manual trigger endpoint.
- [x] Confirm Kubernetes version supports `create job --from=cronjob`.
- [x] Decide to re-use existing CronJob instead of duplicating job spec.
- [x] Choose to expose a lightweight internal-only API to trigger jobs.
- [x] Define internal service-to-service communication using ClusterIP.
- [x] Define monitoring via response of `kubectl create job` command.

---

## 🛠️ Kubernetes Resources

- [x] **Service**
  - [x] Create a ClusterIP service to expose the trigger API endpoint internally.
  - [x] Ensure service is scoped only to the namespace.

- [x] **Deployment**
  - [x] Create a new lightweight containerized FastAPI or Flask service.
  - [x] Mount necessary ServiceAccount for `kubectl`/`K8s API` access.
  - [x] Inject namespace and cronjob name via environment variables or ConfigMap.

- [x] **Role & RoleBinding**
  - [x] Create a Role to allow the pod to `create jobs` from the named CronJob.
  - [x] Bind the Role to the ServiceAccount used by the API pod.

- [x] **ConfigMap**
  - [x] Store optional settings (e.g. target CronJob name, namespace, logging level).

---

## 🧪 API Endpoint

- [x] Create `/trigger-sync` endpoint using FastAPI or Flask.
- [x] Implement job trigger using Kubernetes Python client:
  - [x] Load in-cluster configuration.
  - [x] Call `create_namespaced_job` using `from=cronjob` template logic.
- [x] Return HTTP 200 if successful, appropriate error codes otherwise.

---

## 🧪 Testing & Integration

- [ ] Update Streamlit `settings.py`:
  - [ ] Replace text input field with hardcoded internal service URL or ConfigMap value.
  - [ ] Test successful manual sync via Streamlit UI.

- [ ] Monitor:
  - [ ] Confirm job creation.
  - [ ] Ensure logs show job execution of trade and reward sync.

---

## 🔐 Security

- [ ] Ensure service is not externally exposed (ClusterIP only).
- [ ] Confirm only necessary RBAC permissions are granted (minimal privilege).
- [ ] Optionally add a basic internal auth token to the API trigger (low priority).

---

## 🧼 Cleanup & Documentation

- [ ] Document the new resources in `kustomization.yaml`.
- [ ] Add a new section to `README.md` describing manual sync trigger.
- [ ] Optionally add observability hooks (e.g. logs, job state polling in future).