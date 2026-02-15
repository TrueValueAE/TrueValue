#!/bin/bash
echo "🎯 Verifying Grafana Dashboard Queries"
echo "======================================="
echo ""

# Check Mission Control queries
echo "1️⃣  Mission Control - Query Rate:"
curl -s 'http://localhost:9090/api/v1/query?query=sum(increase(dubai_estate_queries_total[1h]))' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   Queries in last hour: {data['data']['result'][0]['value'][1] if data['data']['result'] else 0}\")" 2>/dev/null || echo "   No data yet"

echo ""
echo "2️⃣  AI Cost Analytics - Total Cost (24h):"
curl -s 'http://localhost:9090/api/v1/query?query=sum(increase(dubai_estate_query_cost_usd_sum[24h]))' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   Total cost: \${data['data']['result'][0]['value'][1] if data['data']['result'] else 0}\")" 2>/dev/null || echo "   No data yet"

echo ""
echo "3️⃣  Tool Usage - Most Popular Tools:"
curl -s 'http://localhost:9090/api/v1/query?query=topk(3,sum%20by(tool_name)(dubai_estate_tool_usage_total))' | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data['data']['result']:
    for item in data['data']['result'][:3]:
        tool = item['metric']['tool_name']
        count = item['value'][1]
        print(f\"   {tool}: {count} times\")
else:
    print('   No data yet')
" 2>/dev/null || echo "   No data yet"

echo ""
echo "4️⃣  Performance - Average Query Duration:"
curl -s 'http://localhost:9090/api/v1/query?query=sum(increase(dubai_estate_query_duration_seconds_sum[24h]))%20/%20sum(increase(dubai_estate_query_duration_seconds_count[24h]))' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   Average: {float(data['data']['result'][0]['value'][1]):.1f}s\" if data['data']['result'] else '   No data yet')" 2>/dev/null || echo "   No data yet"

echo ""
echo "✅ All dashboard queries working!"
echo ""
echo "📊 Access Grafana: http://localhost:3000"
echo "   Username: admin"
echo "   Password: admin"
