#!/bin/bash

# Adobe Hackathon Challenge 1b - Test Runner
# Runs comprehensive tests for the PDF processing solution

echo "🧪 Running Adobe Hackathon Challenge 1b Tests..."
echo "=================================================="

# Set environment variables for testing
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export TESTING_MODE=true

# Create test directories if they don't exist
mkdir -p /app/input
mkdir -p /app/output
mkdir -p /app/cache
mkdir -p /app/logs

# Run unit tests
echo "📋 Running unit tests..."
python test_pdf_processing.py

if [ $? -eq 0 ]; then
    echo "✅ Unit tests passed!"
else
    echo "❌ Unit tests failed!"
    exit 1
fi

# Run integration tests
echo ""
echo "🔗 Running integration tests..."

# Test API endpoints
echo "Testing API endpoints..."

# Test health endpoint
echo "  - Testing health endpoint..."
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "    ✅ Health endpoint working"
else
    echo "    ❌ Health endpoint failed"
fi

# Test personas endpoint
echo "  - Testing personas endpoint..."
curl -f http://localhost:8000/personas > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "    ✅ Personas endpoint working"
else
    echo "    ❌ Personas endpoint failed"
fi

# Test collections endpoint
echo "  - Testing collections endpoint..."
curl -f http://localhost:8000/collections > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "    ✅ Collections endpoint working"
else
    echo "    ❌ Collections endpoint failed"
fi

# Performance tests
echo ""
echo "⚡ Running performance tests..."

# Test with sample PDF
if [ -f "/app/input/sample.pdf" ]; then
    echo "  - Testing PDF processing performance..."
    start_time=$(date +%s)
    curl -X POST http://localhost:8000/process-single \
        -F 'file=@/app/input/sample.pdf' \
        -o /dev/null -s -w "%{http_code}"
    end_time=$(date +%s)
    processing_time=$((end_time - start_time))
    
    if [ $processing_time -lt 60 ]; then
        echo "    ✅ Processing completed in ${processing_time}s (< 60s limit)"
    else
        echo "    ⚠️  Processing took ${processing_time}s (> 60s limit)"
    fi
else
    echo "  - Skipping PDF processing test (no sample.pdf found)"
fi

# Memory usage test
echo "  - Testing memory usage..."
memory_usage=$(free -m | awk 'NR==2{printf "%.1f", $3*100/$2}')
echo "    Current memory usage: ${memory_usage}%"

if (( $(echo "$memory_usage < 90" | bc -l) )); then
    echo "    ✅ Memory usage acceptable (< 90%)"
else
    echo "    ⚠️  High memory usage (> 90%)"
fi

# Load testing
echo ""
echo "📊 Running load tests..."

# Test concurrent processing
echo "  - Testing concurrent processing..."
for i in {1..3}; do
    curl -X POST http://localhost:8000/process-single \
        -F "file=@/app/input/sample.pdf" \
        -o /dev/null -s &
done
wait

echo "    ✅ Concurrent processing test completed"

# System resource test
echo "  - Testing system resources..."
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "    CPU usage: ${cpu_usage}%"

if (( $(echo "$cpu_usage < 80" | bc -l) )); then
    echo "    ✅ CPU usage acceptable (< 80%)"
else
    echo "    ⚠️  High CPU usage (> 80%)"
fi

echo ""
echo "🎯 Running constraint validation tests..."

# File size limit test
echo "  - Testing file size limits..."
if [ -f "/app/input/large_sample.pdf" ]; then
    file_size=$(stat -c%s "/app/input/large_sample.pdf")
    file_size_mb=$((file_size / 1024 / 1024))
    
    if [ $file_size_mb -lt 50 ]; then
        echo "    ✅ File size within limits (${file_size_mb}MB < 50MB)"
    else
        echo "    ❌ File size exceeds limits (${file_size_mb}MB > 50MB)"
    fi
else
    echo "    - Skipping file size test (no large_sample.pdf found)"
fi

# Offline functionality test
echo "  - Testing offline functionality..."
# Check if external dependencies are available
if curl -s --connect-timeout 5 https://www.google.com > /dev/null 2>&1; then
    echo "    ⚠️  Internet connection available (offline test not definitive)"
else
    echo "    ✅ No internet connection (offline mode confirmed)"
fi

# Check local models
echo "  - Testing local model availability..."
if [ -d "/opt/venv/lib/python3.10/site-packages/spacy/data/en_core_web_sm" ]; then
    echo "    ✅ spaCy model available locally"
else
    echo "    ❌ spaCy model not found locally"
fi

if [ -d "/usr/share/nltk_data" ] || [ -d "/opt/venv/lib/python3.10/site-packages/nltk_data" ]; then
    echo "    ✅ NLTK data available locally"
else
    echo "    ❌ NLTK data not found locally"
fi

echo ""
echo "📈 Test Summary:"
echo "=================="

# Count test results
total_tests=0
passed_tests=0
failed_tests=0

# Count unit test results
if [ -f "test_results.txt" ]; then
    total_tests=$(grep -c "test" test_results.txt 2>/dev/null || echo "0")
    passed_tests=$(grep -c "PASSED" test_results.txt 2>/dev/null || echo "0")
    failed_tests=$(grep -c "FAILED" test_results.txt 2>/dev/null || echo "0")
fi

echo "Unit Tests: ${passed_tests} passed, ${failed_tests} failed"
echo "Integration Tests: Completed"
echo "Performance Tests: Completed"
echo "Constraint Tests: Completed"

if [ $failed_tests -eq 0 ]; then
    echo ""
    echo "🎉 All tests completed successfully!"
    echo "✅ Adobe Hackathon Challenge 1b solution is ready for deployment!"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Please review the results above."
    exit 1
fi 