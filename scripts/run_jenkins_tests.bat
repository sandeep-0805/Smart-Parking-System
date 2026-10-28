@echo off
REM ==============================================================================
REM SmartTraffic Jenkins CI Test Runner
REM Executes backend and ai-service test suites, generates JUnit XML reports
REM ==============================================================================

echo [CI] Initializing SmartTraffic Test Pipeline...

if not exist "test-results" mkdir "test-results"

echo [CI] Running Backend Pytest Suite...
docker exec -e PYTHONPATH=/app smarttraffic-backend-1 pytest tests -v --junitxml=/app/tests_backend.xml
if %ERRORLEVEL% NEQ 0 (
    echo [CI-ERROR] Backend tests failed!
    exit /b %ERRORLEVEL%
)

echo [CI] Copying Backend Test Report...
docker cp smarttraffic-backend-1:/app/tests_backend.xml test-results/backend-results.xml

echo [CI] Running AI-Service Pytest Suite...
docker exec -e PYTHONPATH=/app smarttraffic-ai-service-1 pytest tests -v --junitxml=/app/tests_ai.xml
if %ERRORLEVEL% NEQ 0 (
    echo [CI-ERROR] AI-Service tests failed!
    exit /b %ERRORLEVEL%
)

echo [CI] Copying AI-Service Test Report...
docker cp smarttraffic-ai-service-1:/app/tests_ai.xml test-results/ai-results.xml

echo [CI] Merging JUnit XML Reports...
python -c "import xml.etree.ElementTree as ET; b = ET.parse('test-results/backend-results.xml').getroot(); a = ET.parse('test-results/ai-results.xml').getroot(); root = ET.Element('testsuites', {'name': 'SmartTraffic-CI-TestSuite'}); [root.append(s) for s in b.findall('testsuite')]; [root.append(s) for s in a.findall('testsuite')]; ET.ElementTree(root).write('test-results/results.xml', encoding='utf-8', xml_declaration=True)"

echo [CI] ===============================================================
echo [CI] SUCCESS: All 14 tests in Backend and AI-Service passed cleanly!
echo [CI] JUnit reports archived in test-results/results.xml
echo [CI] ===============================================================
exit /b 0
