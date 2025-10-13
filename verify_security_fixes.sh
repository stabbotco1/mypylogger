#!/bin/bash

echo "=== Checking urlparse import ==="
grep "from urllib.parse import urlparse" tests/test_badge_infrastructure.py || echo "Need to add import!"

echo -e "\n=== Fixed line 77 ==="
sed -n '75,80p' tests/test_badge_infrastructure.py

echo -e "\n=== Fixed line 352 ==="
sed -n '350,355p' tests/test_badge_infrastructure.py

echo -e "\n=== Fixed line 423 ==="
sed -n '421,426p' tests/test_performance_and_security_validation.py

echo -e "\n=== Fixed line 645 ==="
sed -n '643,650p' tests/test_documentation_validation.py

echo -e "\n=== Verification complete ==="
