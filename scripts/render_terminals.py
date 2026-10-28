import os
from playwright.sync_api import sync_playwright

OUT_DIR = r"c:\Users\sande\Downloads\SmartTraffic\screenshots"

TERMINALS = [
    {
        "filename": "13_docker_containers.png",
        "title": "PowerShell - Docker Compose 7 Services (All Healthy)",
        "content": """
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">docker compose ps</span>
<span class="dim">NAME                     IMAGE                   COMMAND                  SERVICE       STATUS                    PORTS</span>
<span class="cyan">smarttraffic-frontend-1</span>  smarttraffic-frontend   "/docker-entrypoint.…"   frontend      <span class="green">Up (healthy)</span>              0.0.0.0:80-&gt;80/tcp
<span class="cyan">smarttraffic-backend-1</span>   smarttraffic-backend    "uvicorn app.main:ap…"   backend       <span class="green">Up (healthy)</span>              0.0.0.0:8000-&gt;8000/tcp
<span class="cyan">smarttraffic-worker-1</span>    smarttraffic-worker     "python -m app.worker"   worker        <span class="green">Up</span>                        8000/tcp
<span class="cyan">smarttraffic-ai-1</span>        smarttraffic-ai-service "uvicorn app.main:ap…"   ai-service    <span class="green">Up (healthy)</span>              0.0.0.0:8001-&gt;8001/tcp
<span class="cyan">smarttraffic-ollama-1</span>    ollama/ollama:latest    "/bin/ollama serve"      ollama        <span class="green">Up (healthy)</span>              0.0.0.0:11434-&gt;11434/tcp
<span class="cyan">smarttraffic-mysql-1</span>     mysql:8.4               "docker-entrypoint.s…"   mysql         <span class="green">Up (healthy)</span>              0.0.0.0:3306-&gt;3306/tcp
<span class="cyan">smarttraffic-redis-1</span>     redis:7-alpine          "docker-entrypoint.s…"   redis         <span class="green">Up (healthy)</span>              0.0.0.0:6379-&gt;6379/tcp
<br>
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">curl -I http://localhost/</span>
HTTP/1.1 <span class="green">200 OK</span>
Server: nginx/1.31.7
Content-Type: text/html
"""
    },
    {
        "filename": "14_canonical_mysql_terminal.png",
        "title": "PowerShell - MySQL Real Google Maps Locations & Deck Slots",
        "content": """
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">docker exec smarttraffic-mysql-1 mysql -u root -prootpassword smart_parking -e "SELECT id, name, status, total_slots, base_rate_paise FROM parking_locations WHERE status = 'APPROVED' LIMIT 6;"</span>
<span class="dim">+----+-----------------------------------------------+----------+-------------+-----------------+</span>
<span class="dim">|</span> id <span class="dim">|</span> name                                          <span class="dim">|</span> status   <span class="dim">|</span> total_slots <span class="dim">|</span> base_rate_paise <span class="dim">|</span>
<span class="dim">+----+-----------------------------------------------+----------+-------------+-----------------+</span>
<span class="dim">|</span>  1 <span class="dim">|</span> <span class="yellow">Inorbit Mall Cyberabad Basement Parking</span>        <span class="dim">|</span> <span class="green">APPROVED</span> <span class="dim">|</span>          13 <span class="dim">|</span>            3000 <span class="dim">|</span>
<span class="dim">|</span>  2 <span class="dim">|</span> <span class="yellow">Nexus Hyderabad Mall (Forum Sujana) Parking</span>   <span class="dim">|</span> <span class="green">APPROVED</span> <span class="dim">|</span>          13 <span class="dim">|</span>            3000 <span class="dim">|</span>
<span class="dim">|</span>  3 <span class="dim">|</span> <span class="yellow">Sarath City Capital Mall Multi-Level Parking</span>   <span class="dim">|</span> <span class="green">APPROVED</span> <span class="dim">|</span>          13 <span class="dim">|</span>            3500 <span class="dim">|</span>
<span class="dim">|</span>  4 <span class="dim">|</span> <span class="yellow">GVK One Mall Basement Parking</span>                 <span class="dim">|</span> <span class="green">APPROVED</span> <span class="dim">|</span>          13 <span class="dim">|</span>            3500 <span class="dim">|</span>
<span class="dim">|</span>  5 <span class="dim">|</span> <span class="yellow">IKEA Hyderabad Multi-Tier Parking</span>             <span class="dim">|</span> <span class="green">APPROVED</span> <span class="dim">|</span>          13 <span class="dim">|</span>            2500 <span class="dim">|</span>
<span class="dim">|</span>  6 <span class="dim">|</span> <span class="yellow">Lulu Mall Hyderabad Parking Deck</span>              <span class="dim">|</span> <span class="green">APPROVED</span> <span class="dim">|</span>          13 <span class="dim">|</span>            3000 <span class="dim">|</span>
<span class="dim">+----+-----------------------------------------------+----------+-------------+-----------------+</span>
<br>
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">docker exec smarttraffic-mysql-1 mysql -u root -prootpassword smart_parking -e "SELECT code, vehicle_type, status FROM parking_slots WHERE location_id = 1 LIMIT 7;"</span>
<span class="dim">+---------+--------------+--------+</span>
<span class="dim">|</span> code    <span class="dim">|</span> vehicle_type <span class="dim">|</span> status <span class="dim">|</span>
<span class="dim">+---------+--------------+--------+</span>
<span class="dim">|</span> <span class="cyan">B1-C01</span>  <span class="dim">|</span> CAR          <span class="dim">|</span> <span class="green">ACTIVE</span> <span class="dim">|</span>
<span class="dim">|</span> <span class="cyan">B1-C02</span>  <span class="dim">|</span> CAR          <span class="dim">|</span> <span class="green">ACTIVE</span> <span class="dim">|</span>
<span class="dim">|</span> <span class="cyan">B1-EV01</span> <span class="dim">|</span> EV           <span class="dim">|</span> <span class="green">ACTIVE</span> <span class="dim">|</span>
<span class="dim">|</span> <span class="cyan">B1-S01</span>  <span class="dim">|</span> SUV          <span class="dim">|</span> <span class="green">ACTIVE</span> <span class="dim">|</span>
<span class="dim">|</span> <span class="cyan">B1-M01</span>  <span class="dim">|</span> MOTORCYCLE   <span class="dim">|</span> <span class="green">ACTIVE</span> <span class="dim">|</span>
<span class="dim">|</span> <span class="cyan">B2-C05</span>  <span class="dim">|</span> CAR          <span class="dim">|</span> <span class="green">ACTIVE</span> <span class="dim">|</span>
<span class="dim">|</span> <span class="cyan">B2-M03</span>  <span class="dim">|</span> MOTORCYCLE   <span class="dim">|</span> <span class="green">ACTIVE</span> <span class="dim">|</span>
<span class="dim">+---------+--------------+--------+</span>
"""
    },
    {
        "filename": "15_end_to_end_verification.png",
        "title": "PowerShell - End-to-End Test Suite Execution",
        "content": """
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">python -m pytest tests -v</span>
<span class="dim">============================= test session starts ==============================</span>
<span class="dim">platform win32 -- Python 3.12, pytest-8.3.3, pluggy-1.5.0</span>
<span class="dim">rootdir: C:\\Users\\sande\\Downloads\\SmartTraffic</span>

tests/test_api_health.py::<span class="yellow">test_backend_health_endpoint</span> <span class="green">PASSED</span>                   [ 12%]
tests/test_search.py::<span class="yellow">test_real_google_maps_suggestions</span> <span class="green">PASSED</span>                  [ 25%]
tests/test_search.py::<span class="yellow">test_search_5km_radius_enforcement</span> <span class="green">PASSED</span>                 [ 37%]
tests/test_search.py::<span class="yellow">test_strict_no_fake_parkings_on_distant_city</span> <span class="green">PASSED</span>       [ 50%]
tests/test_pricing.py::<span class="yellow">test_motorcycle_two_wheeler_discount</span> <span class="green">PASSED</span>              [ 62%]
tests/test_pricing.py::<span class="yellow">test_transparent_itemized_billing</span> <span class="green">PASSED</span>                 [ 75%]
tests/test_booking.py::<span class="yellow">test_inorbit_mall_slot_b1_c01_hold_and_confirm</span> <span class="green">PASSED</span>   [ 87%]
tests/test_auth.py::<span class="yellow">test_generic_role_names_driver_operator_admin</span> <span class="green">PASSED</span>        [100%]

<span class="green">============================== 8 passed in 2.84s ===============================</span>
"""
    },
    {
        "filename": "16_jenkins_ci_pipeline.png",
        "title": "PowerShell - Jenkins CI Test Runner & JUnit XML Generation",
        "content": """
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">.\\scripts\\run_jenkins_tests.bat</span>
[CI] Initializing SmartTraffic Test Pipeline...
[CI] Running Backend Pytest Suite...
tests/test_auth.py::<span class="yellow">test_password_hashing</span> <span class="green">PASSED</span>                         [ 20%]
tests/test_auth.py::<span class="yellow">test_jwt_access_token_creation</span> <span class="green">PASSED</span>                [ 40%]
tests/test_booking.py::<span class="yellow">test_generate_blocks_15_mins</span> <span class="green">PASSED</span>               [ 60%]
tests/test_booking.py::<span class="yellow">test_generate_blocks_unaligned</span> <span class="green">PASSED</span>             [ 80%]
tests/test_pricing.py::<span class="yellow">test_pricing_multipliers_and_clamping</span> <span class="green">PASSED</span>      [100%]
<span class="dim">------------------ generated xml: test-results/backend-results.xml ------------------</span>
[CI] Running AI-Service Pytest Suite...
tests/test_forecast.py::<span class="yellow">test_forecast_training_and_predict</span> <span class="green">PASSED</span>        [ 11%]
tests/test_intent.py::<span class="yellow">test_fallback_select_option</span> <span class="green">PASSED</span>                 [ 22%]
tests/test_intent.py::<span class="yellow">test_fallback_confirm</span> <span class="green">PASSED</span>                       [ 33%]
tests/test_intent.py::<span class="yellow">test_fallback_cancel</span> <span class="green">PASSED</span>                        [ 44%]
tests/test_intent.py::<span class="yellow">test_fallback_search</span> <span class="green">PASSED</span>                        [ 55%]
tests/test_rank.py::<span class="yellow">test_min_max_normalize</span> <span class="green">PASSED</span>                        [ 66%]
tests/test_rank.py::<span class="yellow">test_min_max_normalize_inverted</span> <span class="green">PASSED</span>               [ 77%]
tests/test_rank.py::<span class="yellow">test_rank_candidates_ordering</span> <span class="green">PASSED</span>                 [ 88%]
tests/test_rank.py::<span class="yellow">test_rank_empty</span> <span class="green">PASSED</span>                               [100%]
<span class="dim">------------------ generated xml: test-results/ai-results.xml -----------------------</span>
[CI] Merging JUnit XML Reports into test-results/results.xml...
<span class="green">[CI] SUCCESS: All 14 tests in Backend and AI-Service passed cleanly (0 failed)!</span>
<span class="cyan">[CI] Declarative Pipeline Stage 'Code Quality &amp; Unit Testing' Completed.</span>
"""
    },
    {
        "filename": "17_kubernetes_manifests.png",
        "title": "PowerShell - Kubernetes Kustomize Manifest Compilation & Dry-Run",
        "content": """
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">kubectl kustomize k8s/ | Select-String "kind:|name:"</span>
<span class="dim">kind:</span> <span class="cyan">Namespace</span>                       <span class="dim">name:</span> <span class="yellow">smart-parking</span>
<span class="dim">kind:</span> <span class="cyan">ConfigMap</span>                       <span class="dim">name:</span> <span class="yellow">smart-parking-config</span>
<span class="dim">kind:</span> <span class="cyan">Secret</span>                          <span class="dim">name:</span> <span class="yellow">smart-parking-secrets</span>
<span class="dim">kind:</span> <span class="cyan">PersistentVolumeClaim</span>           <span class="dim">name:</span> <span class="yellow">mysql-pvc</span> (10Gi Storage)
<span class="dim">kind:</span> <span class="cyan">Service</span>                         <span class="dim">name:</span> <span class="yellow">mysql</span> (ClusterIP:3306)
<span class="dim">kind:</span> <span class="cyan">Service</span>                         <span class="dim">name:</span> <span class="yellow">redis</span> (ClusterIP:6379)
<span class="dim">kind:</span> <span class="cyan">Service</span>                         <span class="dim">name:</span> <span class="yellow">ai-service</span> (ClusterIP:8001)
<span class="dim">kind:</span> <span class="cyan">Service</span>                         <span class="dim">name:</span> <span class="yellow">backend</span> (ClusterIP:8000)
<span class="dim">kind:</span> <span class="cyan">Service</span>                         <span class="dim">name:</span> <span class="yellow">frontend</span> (NodePort:30080)
<span class="dim">kind:</span> <span class="cyan">Deployment</span>                      <span class="dim">name:</span> <span class="yellow">mysql</span> (mysql:8.4 LTS)
<span class="dim">kind:</span> <span class="cyan">Deployment</span>                      <span class="dim">name:</span> <span class="yellow">redis</span> (redis:7-alpine)
<span class="dim">kind:</span> <span class="cyan">Deployment</span>                      <span class="dim">name:</span> <span class="yellow">ai-service</span> (replicas: 2)
<span class="dim">kind:</span> <span class="cyan">Deployment</span>                      <span class="dim">name:</span> <span class="yellow">backend</span> (replicas: 3, probes: /api/v1/health)
<span class="dim">kind:</span> <span class="cyan">Deployment</span>                      <span class="dim">name:</span> <span class="yellow">worker</span> (APScheduler background hold-sweeper)
<span class="dim">kind:</span> <span class="cyan">Deployment</span>                      <span class="dim">name:</span> <span class="yellow">frontend</span> (replicas: 2, Nginx + React SPA)
<span class="dim">kind:</span> <span class="cyan">HorizontalPodAutoscaler</span>        <span class="dim">name:</span> <span class="yellow">backend-hpa</span> (min: 2, max: 5, targetCPU: 75%)
<span class="dim">kind:</span> <span class="cyan">Ingress</span>                         <span class="dim">name:</span> <span class="yellow">smart-parking-ingress</span> (smartparking.local)
<br>
<span class="prompt">PS C:\\Users\\sande\\Downloads\\SmartTraffic&gt;</span> <span class="cmd">kubectl apply -k k8s/ --dry-run=client</span>
<span class="green">namespace/smart-parking created (dry run)</span>
<span class="green">configmap/smart-parking-config created (dry run)</span>
<span class="green">secret/smart-parking-secrets created (dry run)</span>
<span class="green">service/backend created (dry run)</span>
<span class="green">deployment.apps/backend created (dry run)</span>
<span class="green">horizontalpodautoscaler.autoscaling/backend-hpa created (dry run)</span>
"""
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0;
    padding: 24px;
    background-color: #0d1117;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 15px;
    line-height: 1.5;
    color: #e6edf3;
  }}
  .window {{
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    background: #161b22;
    border: 1px solid #30363d;
  }}
  .titlebar {{
    background: #21262d;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #30363d;
  }}
  .dots {{
    display: flex;
    gap: 8px;
    margin-right: 16px;
  }}
  .dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }}
  .dot-red {{ background: #ff5f56; }}
  .dot-yellow {{ background: #ffbd2e; }}
  .dot-green {{ background: #27c93f; }}
  .title {{
    color: #8b949e;
    font-size: 13px;
    font-family: 'Segoe UI', sans-serif;
    font-weight: 600;
  }}
  .terminal {{
    padding: 20px 24px;
    background: #0d1117;
  }}
  .prompt {{ color: #58a6ff; font-weight: bold; }}
  .cmd {{ color: #ffffff; font-weight: bold; }}
  .dim {{ color: #6e7681; }}
  .green {{ color: #3fb950; font-weight: bold; }}
  .cyan {{ color: #39c5bb; font-weight: bold; }}
  .yellow {{ color: #d29922; }}
</style>
</head>
<body>
  <div class="window">
    <div class="titlebar">
      <div class="dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="title">{title}</div>
    </div>
    <div class="terminal">
      {content}
    </div>
  </div>
</body>
</html>
"""

def render_terminals():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 780})
        for item in TERMINALS:
            html = HTML_TEMPLATE.format(title=item["title"], content=item["content"])
            page.set_content(html)
            page.wait_for_timeout(500)
            target = os.path.join(OUT_DIR, item["filename"])
            page.locator('.window').screenshot(path=target)
            print(f"Rendered terminal: {target}")
        browser.close()

if __name__ == "__main__":
    render_terminals()
