# 💳 Setting Up Anthropic API Credits

## Quick Start

You have $5 in Anthropic API credits - perfect for testing! Here's what you need to know:

### ✅ What's Already Done

- Bot is configured to use Anthropic API
- Error handling is in place
- If credits run low, users get a clear message

### 📊 Cost Per Query

- **Typical query:** $0.02-0.04
- **Your $5 credit:** ~125-250 queries
- **More than enough for testing!**

### 🔍 Monitor Your Usage

Check your credits at: **https://console.anthropic.com/settings/billing**

You'll see:
- Current balance
- Usage history
- Cost per request

### 💰 When You Need More Credits

Two options:

1. **Add More Credits** (Pay-as-you-go)
   - Go to console.anthropic.com/settings/billing
   - Click "Add Credits"
   - Add $10, $20, $50, etc.
   - Good for: Testing, low-volume production

2. **Monthly Plan** (Better for production)
   - Pay monthly fee
   - Lower per-request costs
   - Good for: High-volume production

## 🧪 Testing Tips

### Start Small
```
/start
/help
Calculate chiller cost for 1500 sqft Empower property
```
These simple queries cost ~$0.01-0.02 each.

### Test Full Analysis
```
/analyze Marina Gate Tower 1
Find 2BR in Marina under 2M
```
These complex queries cost ~$0.03-0.05 each.

### Monitor As You Go
- Check console.anthropic.com after every 10-20 queries
- Watch how costs scale with query complexity
- Adjust as needed

## ⚠️ Error Messages You Might See

### Low Credits Warning
```
❌ API Credits Issue

The Anthropic API credits are running low.

📧 Please contact support or try again later.

Error: Insufficient API credits
```

**What to do:** Add more credits at console.anthropic.com

### Rate Limit
```
⏱️ Rate Limit Reached

Too many requests. Please wait a moment and try again.
```

**What to do:** Wait 10-30 seconds, then retry

### Timeout
```
⏱️ Request Timeout

The analysis took too long. Please try a simpler query.
```

**What to do:** Break complex queries into smaller parts

## 📈 Production Planning

### For Your Subscription Model

**Free Tier (3 queries/day):**
- Cost to you: $0.06-0.12/user/day
- Revenue: $0 (lead generation)
- **Net cost:** ~$2-4/user/month

**Basic Tier (20 queries/day):**
- Cost to you: $0.40-0.80/user/day
- Revenue: AED 99/month (~$27)
- **Net profit:** ~$15-23/user/month

**Pro Tier (100 queries/day):**
- Cost to you: $2-4/user/day
- Revenue: AED 299/month (~$81)
- **Net profit:** ~$30-60/user/month

### Cost Optimization

1. **Cache responses** (Redis) - save 30-50% on repeated queries
2. **Use Haiku for simple tasks** - 10x cheaper than Sonnet
3. **Batch API calls** - better rate limits
4. **User education** - teach them to ask efficient questions

## 🎯 Your $5 Credit Plan

**Week 1 Testing:**
- Test all 8 commands (50 queries) = ~$1-2
- Test error scenarios (20 queries) = ~$0.40-0.80
- Test with friends (30 queries) = ~$0.60-1.20
- **Total:** ~$2-4

**Week 2-3 Testing:**
- Remaining ~$1-3 = 50-150 more queries
- Test subscription tiers
- Test edge cases
- Refine prompts

**After Testing:**
- Add $10-20 for initial production
- Monitor for 1 week
- Scale based on actual usage

## 🚀 Ready to Test!

Your bot is now configured with:
- ✅ $5 Anthropic API credits
- ✅ Full error handling
- ✅ User-friendly error messages
- ✅ All 8 analysis tools working

**Go test it on Telegram!** 🎉

---

**Need help?**
- Check console.anthropic.com for usage
- Read bot logs: `tail -f bot.log`
- Monitor errors in real-time
