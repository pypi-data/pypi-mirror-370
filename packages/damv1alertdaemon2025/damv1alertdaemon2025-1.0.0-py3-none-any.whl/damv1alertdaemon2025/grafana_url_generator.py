# grafana_url_generator.py
import urllib.parse
import json
from datetime import datetime
import pytz

def generate_grafana_explore_url(grafana_base_url, datasource_uid, query_expr, start_time_wib, end_time_wib, org_id=1):
    jakarta = pytz.timezone('Asia/Jakarta')
    start_dt_local = jakarta.localize(datetime.strptime(start_time_wib, "%Y-%m-%d %H:%M:%S"))
    end_dt_local = jakarta.localize(datetime.strptime(end_time_wib, "%Y-%m-%d %H:%M:%S"))

    start_utc = start_dt_local.astimezone(pytz.utc)
    end_utc = end_dt_local.astimezone(pytz.utc)

    start_str = start_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = end_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    payload = {
        "b99": {
            "datasource": {
                "type": "loki",
                "uid": datasource_uid
            },
            "queries": [
                {
                    "refId": "A",
                    "expr": query_expr,
                    "queryType": "range",
                    "datasource": {
                        "type": "loki",
                        "uid": datasource_uid
                    },
                    "editorMode": "code",
                    "direction": "backward"
                }
            ],
            "range": {
                "from": start_str,
                "to": end_str
            }
        }
    }

    encoded_panes = urllib.parse.quote(json.dumps(payload))
    final_url = f"{grafana_base_url}/explore?schemaVersion=1&panes={encoded_panes}&orgId={org_id}"

    return final_url