# 🚀 Dubai Estate AI - Observability Quick Start

## ⚡ 3-Step Setup

```bash
# 1. Copy & edit environment file
cp .env.example .env
nano .env  # Add your API keys

# 2. Start everything
./start-observability.sh

# 3. Open Mission Control
open http://localhost:3000
```

**Login:** admin / admin (change this!)

---

## 📊 Dashboards

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| **Mission Control** | http://localhost:3000/d/mission-control | Main overview |
| **User Analytics** | http://localhost:3000/d/user-analytics | Users & business |
| **AI & Cost** | http://localhost:3000/d/ai-cost | AI usage & costs |
| **Prometheus** | http://localhost:9090 | Raw metrics |

---

## 🎯 Key Metrics At a Glance

### **Real-Time (Mission Control)**
- 🔥 Queries last hour
- ✅ Success rate
- 💰 Cost last hour
- 👥 Active users
- ⚡ Avg response time
- ❌ Errors

### **Business (User Analytics)**
- 📊 Signups (24h)
- 🎯 Active users
- ⬆️ Upgrades
- 💵 MRR
- 📈 Conversion rate

### **AI Costs (AI & Cost Dashboard)**
- 💰 Total cost (24h)
- 📊 Cost per query
- 🔢 Token usage
- 💸 Projected monthly cost

---

## 🛠️ Common Commands

```bash
# Start stack
./start-observability.sh

# Stop stack
./stop-observability.sh

# View logs
docker-compose logs -f app
docker-compose logs -f grafana

# Check status
docker-compose ps

# Restart specific service
docker-compose restart grafana

# Clean everything (WARNING: deletes data)
docker-compose down -v
```

---

## 📈 What's Tracked

### ✅ All Usage Metrics
- Total queries, success rate, errors
- Response times (P50, P95, P99)
- Active users, throughput

### ✅ All Product Features
- Tool usage (all 8 tools)
- Command usage (all commands)
- Feature adoption, combinations

### ✅ All End Users
- Signups, DAU, MAU
- Users by tier
- Retention, churn

### ✅ All Tools
- Individual tool metrics
- Success/failure rates
- Cost per tool

### ✅ All Commands
- `/start`, `/search`, `/analyze`, etc.
- Command frequency
- Success rates

### ✅ All AI & Costs
- Total costs, cost per query
- Token usage, cost by model
- Projected costs, efficiency

---

## 🎨 Custom Queries

### **Most Popular Features**
```promql
topk(10, sum by(tool_name) (increase(dubai_estate_tool_usage_total[24h])))
```

### **Conversion Rate**
```promql
sum(increase(dubai_estate_subscription_upgrades_total[24h]))
/
sum(increase(dubai_estate_query_limit_hits_total[24h]))
* 100
```

### **Cost Efficiency**
```promql
sum(increase(dubai_estate_queries_total[24h]))
/
sum(increase(dubai_estate_query_cost_usd_sum[24h]))
```

---

## 🚨 Set Up Alerts

1. Grafana → Alerting → Alert rules
2. Create new alert
3. Example conditions:
   - Error rate > 10%
   - Cost > $10/hour
   - P95 response time > 30s
   - No queries in 1 hour

---

## 📚 Full Documentation

- **Mission Control:** `MISSION_CONTROL_SETUP.md`
- **Complete Guide:** `GRAFANA_OBSERVABILITY_GUIDE.md`
- **Full Summary:** `OBSERVABILITY_COMPLETE.md`

---

## 🆘 Troubleshooting

### No data showing?
```bash
# Check Prometheus scraping
curl http://localhost:8000/metrics

# Check app logs
docker-compose logs app
```

### Grafana not loading?
```bash
docker-compose restart grafana
```

### High costs?
Check "AI & Cost Analytics" dashboard → "Most Expensive Queries"

---

## ✅ You're All Set!

**Your stack includes:**
- Grafana (dashboards)
- Prometheus (metrics)
- Loki (logs)
- Tempo (traces)
- Full instrumentation

**Cost:** $0/month 🎉

**Start now:**
```bash
./start-observability.sh
```
