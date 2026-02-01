#!/bin/bash
# Run Selenium tests for MonPanierLocal

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 MonPanierLocal - Selenium Tests"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Check Firefox is installed (tests use Firefox/geckodriver)
if ! command -v firefox &> /dev/null; then
    echo "⚠️  Firefox not found. Tests may fail."
    echo "   Install with: sudo apt install firefox"
fi

# Set environment variables (default to production ports via Nginx)
export TEST_BASE_URL="${TEST_BASE_URL:-http://localhost:3500}"
export TEST_API_URL="${TEST_API_URL:-http://localhost:3500}"
export TEST_HEADLESS="${TEST_HEADLESS:-true}"

echo ""
echo "📋 Test Configuration:"
echo "   Base URL: $TEST_BASE_URL"
echo "   API URL: $TEST_API_URL"
echo "   Headless: $TEST_HEADLESS"
echo ""

# Check if services are running
echo "🔍 Checking services..."

if curl -s "$TEST_API_URL/health/" > /dev/null 2>&1; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is not running at $TEST_API_URL"
    echo "   Start with: ./start.sh"
    exit 1
fi

if curl -s "$TEST_BASE_URL" > /dev/null 2>&1; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is not running at $TEST_BASE_URL"
    echo "   Start with: ./start.sh"
    exit 1
fi

echo ""
echo "🚀 Running tests..."
echo ""

# Parse arguments
TEST_FILTER=""
EXTRA_ARGS=""
for arg in "$@"; do
    case $arg in
        --navigation)
            TEST_FILTER="test_01_navigation.py"
            ;;
        --auth)
            TEST_FILTER="test_02_authentication.py"
            ;;
        --map)
            TEST_FILTER="test_03_homepage_map.py"
            ;;
        --search)
            TEST_FILTER="test_04_search.py"
            ;;
        --producer)
            TEST_FILTER="test_05_producer_detail.py test_10_producer_edit.py"
            ;;
        --profile)
            TEST_FILTER="test_06_profile.py"
            ;;
        --api)
            TEST_FILTER="test_07_api_integration.py"
            ;;
        --forms)
            TEST_FILTER="test_08_forms.py"
            ;;
        --sidebar)
            TEST_FILTER="test_09_sidebar.py"
            ;;
        --products)
            TEST_FILTER="test_11_product_management.py"
            ;;
        --sales)
            TEST_FILTER="test_12_sale_modes.py"
            ;;
        --photos)
            TEST_FILTER="test_13_photo_management.py"
            ;;
        --geocoding)
            TEST_FILTER="test_14_address_geocoding.py"
            ;;
        --responsive)
            TEST_FILTER="test_15_responsive_accessibility.py"
            ;;
        --all)
            TEST_FILTER=""
            ;;
        --fast)
            EXTRA_ARGS="$EXTRA_ARGS -m 'not slow'"
            ;;
        --visible)
            export TEST_HEADLESS="false"
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $arg"
            ;;
    esac
done

# Run pytest with options
if [ -n "$TEST_FILTER" ]; then
    pytest \
        --tb=short \
        --html=report.html \
        --self-contained-html \
        -v \
        $TEST_FILTER \
        $EXTRA_ARGS
else
    pytest \
        --tb=short \
        --html=report.html \
        --self-contained-html \
        -v \
        $EXTRA_ARGS
fi

echo ""
echo "✅ Tests completed!"
echo "📊 Report saved to: $SCRIPT_DIR/report.html"
echo ""
echo "📈 Test Summary:"
echo "   Total test files: $(ls test_*.py 2>/dev/null | wc -l)"
echo "   Total tests: $(grep -r "def test_" test_*.py 2>/dev/null | wc -l)"
echo ""
echo "Usage:"
echo "   ./run_tests.sh              # Run all tests"
echo "   ./run_tests.sh --navigation # Run navigation tests only"
echo "   ./run_tests.sh --fast       # Skip slow tests"
echo "   ./run_tests.sh --visible    # Run with visible browser"
echo "   ./run_tests.sh -k 'login'   # Run tests matching 'login'"

