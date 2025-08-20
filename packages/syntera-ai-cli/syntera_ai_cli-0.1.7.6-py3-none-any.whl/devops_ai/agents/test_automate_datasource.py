import requests
import json
from requests.auth import HTTPBasicAuth

def create_grafana_datasource(grafana_url, username, password, datasource_payload):
    url = f"{grafana_url}/api/datasources"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(datasource_payload),
        auth=HTTPBasicAuth(username, password)
    )

    if response.status_code == 200:
        print(f"✅ Datasource '{datasource_payload['name']}' created successfully.")
    elif response.status_code == 409:
        print(f"⚠️ Datasource '{datasource_payload['name']}' already exists.")
    else:
        print(f"❌ Failed to create datasource '{datasource_payload['name']}'. Status: {response.status_code}, Response: {response.text}")


def fetch_dashboard_from_grafana_com(dashboard_id, grafana_com_url="https://grafana.com/api/dashboards/"):
    url = f"{grafana_com_url}{dashboard_id}/revisions/latest/download"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"✅ Successfully fetched dashboard {dashboard_id}")
        return response.json()
    else:
        print(f"❌ Failed to fetch dashboard {dashboard_id}. Status: {response.status_code}")
        return None


def create_dashboard(grafana_url, username, password, dashboard_json):
    url = f"{grafana_url}/api/dashboards/db"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "dashboard": dashboard_json,
        "folderId": 0,
        "overwrite": True
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload),
        auth=HTTPBasicAuth(username, password)
    )

    if response.status_code in [200, 202]:
        print(f"✅ Dashboard '{dashboard_json.get('title')}' created successfully.")
    else:
        print(f"❌ Failed to create dashboard. Status: {response.status_code}, Response: {response.text}")


# def build_logs_dashboard():
#     return {
#         "id": None,
#         "uid": "logs-dashboard-frontend-backend",
#         "title": "Frontend and Backend Logs",
#         "tags": ["logs", "loki"],
#         "timezone": "browser",
#         "schemaVersion": 36,
#         "version": 0,
#         "refresh": "5s",
#         "panels": [
#             {
#                 "type": "logs",
#                 "title": "Backend Logs",
#                 "datasource": {"type": "loki", "uid": "loki"},
#                 "targets": [
#                     {
#                         "expr": '{container="backend"}',
#                         "refId": "A"
#                     }
#                 ],
#                 "gridPos": {"x": 0, "y": 0, "w": 24, "h": 9}
#             },
#             {
#                 "type": "logs",
#                 "title": "Frontend Logs",
#                 "datasource": {"type": "loki", "uid": "loki"},
#                 "targets": [
#                     {
#                         "expr": '{container="frontend"}',
#                         "refId": "B"
#                     }
#                 ],
#                 "gridPos": {"x": 0, "y": 9, "w": 24, "h": 9}
#             }
#         ]
#     }


if __name__ == "__main__":
    grafana_url = "http://localhost:3001"
    username = "admin"
    password = "admin"

    # 1. Create Prometheus datasource
    create_grafana_datasource(grafana_url, username, password, {
        "name": "Prometheusyyy",
        "type": "prometheus",
        "access": "proxy",
        "url": "http://prometheus:9090",
        "basicAuth": False,
        "jsonData": {
            "httpMethod": "POST"
        }
    })

    # # 2. Create Loki datasource
    # create_grafana_datasource(grafana_url, username, password, {
    #     "name": "Loki",
    #     "type": "loki",
    #     "access": "proxy",
    #     "url": "http://loki:3100",
    #     "basicAuth": False,
    #     "uid": "loki",
    #     "jsonData": {}
    # })

    # 3. Create Prometheus Dashboard from Grafana.com
    prometheus_dashboard_id = 1860
    dashboard_json = fetch_dashboard_from_grafana_com(prometheus_dashboard_id)

    if dashboard_json:
        dashboard_json["title"] = dashboard_json.get("title", "Prometheus Metrics")
        create_dashboard(grafana_url, username, password, dashboard_json)

    # # 4. Create Loki Log Dashboard for frontend and backend
    # log_dashboard = build_logs_dashboard()
    # create_dashboard(grafana_url, username, password, log_dashboard)
