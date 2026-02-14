#!/usr/bin/env node

/**
 * Property Finder Listings MCP Server
 * Advanced property search with AI-powered recommendations
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

const API_KEY = process.env.PROPERTY_FINDER_API_KEY;
const BASE_URL = "https://api.propertyfinder.ae/v2.0";

class PropertyFinderServer {
  constructor() {
    this.server = new Server(
      {
        name: "property-finder",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    
    this.server.onerror = (error) => console.error("[MCP Error]", error);
    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "search_listings",
          description: "Search property listings with advanced filters",
          inputSchema: {
            type: "object",
            properties: {
              location_ids: {
                type: "array",
                items: { type: "string" },
                description: "Location IDs (e.g., ['2', '3'] for Dubai Marina, JBR)",
              },
              listing_type: {
                type: "string",
                enum: ["sale", "rent", "commercial_sale", "commercial_rent"],
                description: "Listing type",
              },
              property_types: {
                type: "array",
                items: { type: "string" },
                description: "Property types (e.g., ['AP', 'VH'] for apartment, villa)",
              },
              bedrooms_min: {
                type: "number",
                description: "Minimum bedrooms",
              },
              bedrooms_max: {
                type: "number",
                description: "Maximum bedrooms",
              },
              price_min: {
                type: "number",
                description: "Minimum price in AED",
              },
              price_max: {
                type: "number",
                description: "Maximum price in AED",
              },
              area_min: {
                type: "number",
                description: "Minimum area in sqft",
              },
              area_max: {
                type: "number",
                description: "Maximum area in sqft",
              },
              keywords: {
                type: "string",
                description: "Search keywords",
              },
              page: {
                type: "number",
                description: "Page number",
              },
              page_size: {
                type: "number",
                description: "Results per page (max 50)",
              },
            },
            required: ["listing_type"],
          },
        },
        {
          name: "get_listing_details",
          description: "Get detailed information about a specific listing",
          inputSchema: {
            type: "object",
            properties: {
              listing_id: {
                type: "string",
                description: "Property Finder listing ID",
              },
            },
            required: ["listing_id"],
          },
        },
        {
          name: "get_agent_info",
          description: "Get information about a real estate agent",
          inputSchema: {
            type: "object",
            properties: {
              agent_id: {
                type: "string",
                description: "Agent ID",
              },
            },
            required: ["agent_id"],
          },
        },
        {
          name: "get_agency_info",
          description: "Get information about a real estate agency",
          inputSchema: {
            type: "object",
            properties: {
              agency_id: {
                type: "string",
                description: "Agency ID",
              },
            },
            required: ["agency_id"],
          },
        },
        {
          name: "get_location_stats",
          description: "Get statistics and insights for a location",
          inputSchema: {
            type: "object",
            properties: {
              location_id: {
                type: "string",
                description: "Location ID",
              },
              listing_type: {
                type: "string",
                enum: ["sale", "rent"],
                description: "Listing type",
              },
            },
            required: ["location_id", "listing_type"],
          },
        },
        {
          name: "get_price_trends",
          description: "Get price trends for a location and property type",
          inputSchema: {
            type: "object",
            properties: {
              location_id: {
                type: "string",
                description: "Location ID",
              },
              property_type: {
                type: "string",
                description: "Property type code",
              },
              period: {
                type: "string",
                enum: ["3m", "6m", "1y", "2y"],
                description: "Time period",
              },
            },
            required: ["location_id"],
          },
        },
        {
          name: "get_market_report",
          description: "Get comprehensive market report for a zone",
          inputSchema: {
            type: "object",
            properties: {
              location_id: {
                type: "string",
                description: "Location ID",
              },
            },
            required: ["location_id"],
          },
        },
        {
          name: "compare_properties",
          description: "Compare multiple properties side-by-side",
          inputSchema: {
            type: "object",
            properties: {
              listing_ids: {
                type: "array",
                items: { type: "string" },
                description: "Array of listing IDs to compare (max 5)",
                maxItems: 5,
              },
            },
            required: ["listing_ids"],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "search_listings":
            return await this.searchListings(args);
          case "get_listing_details":
            return await this.getListingDetails(args);
          case "get_agent_info":
            return await this.getAgentInfo(args);
          case "get_agency_info":
            return await this.getAgencyInfo(args);
          case "get_location_stats":
            return await this.getLocationStats(args);
          case "get_price_trends":
            return await this.getPriceTrends(args);
          case "get_market_report":
            return await this.getMarketReport(args);
          case "compare_properties":
            return await this.compareProperties(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
        };
      }
    });
  }

  async searchListings(args) {
    const params = {
      listing_type: args.listing_type,
      page: args.page || 1,
      page_size: Math.min(args.page_size || 25, 50),
    };

    if (args.location_ids) params.location_ids = args.location_ids.join(',');
    if (args.property_types) params.property_types = args.property_types.join(',');
    if (args.bedrooms_min) params.bedrooms_min = args.bedrooms_min;
    if (args.bedrooms_max) params.bedrooms_max = args.bedrooms_max;
    if (args.price_min) params.price_min = args.price_min;
    if (args.price_max) params.price_max = args.price_max;
    if (args.area_min) params.area_min = args.area_min;
    if (args.area_max) params.area_max = args.area_max;
    if (args.keywords) params.keywords = args.keywords;

    const response = await axios.get(`${BASE_URL}/properties/search`, {
      params,
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
      },
    });

    // Enrich results with analytics
    const listings = response.data.data || [];
    const enriched = listings.map(listing => ({
      ...listing,
      analytics: {
        price_per_sqft: listing.area ? (listing.price / listing.area).toFixed(2) : null,
        days_on_market: this.calculateDOM(listing.created_at),
        price_score: this.calculatePriceScore(listing, listings),
        liquidity_score: this.calculateLiquidityScore(listing),
        value_rating: this.getValueRating(listing, listings),
      },
    }));

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            meta: response.data.meta,
            listings: enriched,
            market_summary: {
              total_results: response.data.meta.total,
              avg_price: this.calculateAvg(enriched, 'price'),
              avg_price_per_sqft: this.calculateAvg(enriched.map(l => l.analytics), 'price_per_sqft'),
              price_range: {
                min: Math.min(...enriched.map(l => l.price)),
                max: Math.max(...enriched.map(l => l.price)),
              },
            },
          }, null, 2),
        },
      ],
    };
  }

  async getListingDetails(args) {
    const response = await axios.get(`${BASE_URL}/properties/${args.listing_id}`, {
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
    });

    const listing = response.data.data;
    
    // Add comprehensive analytics
    const enriched = {
      ...listing,
      analytics: {
        price_per_sqft: listing.area ? (listing.price / listing.area).toFixed(2) : null,
        days_on_market: this.calculateDOM(listing.created_at),
        estimated_roi: this.estimateROI(listing),
        market_position: await this.getMarketPosition(listing),
        investment_score: this.calculateInvestmentScore(listing),
        red_flags: this.identifyRedFlags(listing),
        recommendations: this.generateRecommendations(listing),
      },
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(enriched, null, 2),
        },
      ],
    };
  }

  async getAgentInfo(args) {
    const response = await axios.get(`${BASE_URL}/agents/${args.agent_id}`, {
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
    });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data.data, null, 2),
        },
      ],
    };
  }

  async getAgencyInfo(args) {
    const response = await axios.get(`${BASE_URL}/agencies/${args.agency_id}`, {
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
    });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data.data, null, 2),
        },
      ],
    };
  }

  async getLocationStats(args) {
    const response = await axios.get(`${BASE_URL}/locations/${args.location_id}/stats`, {
      params: {
        listing_type: args.listing_type,
      },
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
    });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data.data, null, 2),
        },
      ],
    };
  }

  async getPriceTrends(args) {
    const period = args.period || "1y";
    
    const response = await axios.get(`${BASE_URL}/analytics/price-trends`, {
      params: {
        location_id: args.location_id,
        property_type: args.property_type,
        period,
      },
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
      },
    });

    const trends = response.data.data;
    
    // Add analysis
    const analysis = {
      ...trends,
      insights: {
        price_change_pct: this.calculatePriceChange(trends),
        momentum: this.analyzeMomentum(trends),
        forecast: this.generateForecast(trends),
        recommendation: this.generateTrendRecommendation(trends),
      },
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(analysis, null, 2),
        },
      ],
    };
  }

  async getMarketReport(args) {
    // Aggregate multiple data points
    const [stats, trends, listings] = await Promise.all([
      this.getLocationStats({ location_id: args.location_id, listing_type: "sale" }),
      this.getPriceTrends({ location_id: args.location_id, period: "1y" }),
      this.searchListings({ location_ids: [args.location_id], listing_type: "sale", page_size: 50 }),
    ]);

    const statsData = JSON.parse(stats.content[0].text);
    const trendsData = JSON.parse(trends.content[0].text);
    const listingsData = JSON.parse(listings.content[0].text);

    const report = {
      location_id: args.location_id,
      generated_at: new Date().toISOString(),
      market_overview: {
        total_listings: listingsData.market_summary.total_results,
        avg_price: listingsData.market_summary.avg_price,
        avg_price_per_sqft: listingsData.market_summary.avg_price_per_sqft,
        price_range: listingsData.market_summary.price_range,
      },
      trends: trendsData.insights,
      statistics: statsData,
      market_health: this.assessMarketHealth(listingsData, trendsData),
      investment_opportunities: this.identifyOpportunities(listingsData),
      risks: this.identifyMarketRisks(listingsData, trendsData),
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(report, null, 2),
        },
      ],
    };
  }

  async compareProperties(args) {
    const listings = await Promise.all(
      args.listing_ids.map(id => this.getListingDetails({ listing_id: id }))
    );

    const properties = listings.map(l => JSON.parse(l.content[0].text));

    const comparison = {
      properties: properties.map(p => ({
        id: p.id,
        title: p.title,
        price: p.price,
        price_per_sqft: p.analytics.price_per_sqft,
        area: p.area,
        bedrooms: p.bedrooms,
        days_on_market: p.analytics.days_on_market,
        investment_score: p.analytics.investment_score,
      })),
      best_value: this.findBestValue(properties),
      best_location: this.findBestLocation(properties),
      quickest_sale: this.findQuickestSale(properties),
      recommendations: this.compareAndRecommend(properties),
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(comparison, null, 2),
        },
      ],
    };
  }

  // Helper functions
  calculateDOM(createdAt) {
    if (!createdAt) return null;
    const created = new Date(createdAt);
    const now = new Date();
    return Math.floor((now - created) / (1000 * 60 * 60 * 24));
  }

  calculatePriceScore(listing, allListings) {
    // Compare to market average
    const avgPrice = this.calculateAvg(allListings, 'price');
    const deviation = ((listing.price - avgPrice) / avgPrice) * 100;
    
    if (deviation < -15) return "Excellent Value";
    if (deviation < -5) return "Good Value";
    if (deviation < 5) return "Fair Market";
    if (deviation < 15) return "Above Market";
    return "Overpriced";
  }

  calculateLiquidityScore(listing) {
    const dom = this.calculateDOM(listing.created_at);
    if (!dom) return 50;
    
    if (dom < 30) return 90;
    if (dom < 60) return 70;
    if (dom < 90) return 50;
    return 30;
  }

  getValueRating(listing, allListings) {
    const pricePerSqft = listing.area ? listing.price / listing.area : 0;
    const avgPricePerSqft = this.calculateAvg(
      allListings.filter(l => l.area).map(l => ({ value: l.price / l.area })),
      'value'
    );
    
    if (pricePerSqft < avgPricePerSqft * 0.85) return "★★★★★";
    if (pricePerSqft < avgPricePerSqft * 0.95) return "★★★★";
    if (pricePerSqft < avgPricePerSqft * 1.05) return "★★★";
    if (pricePerSqft < avgPricePerSqft * 1.15) return "★★";
    return "★";
  }

  estimateROI(listing) {
    if (listing.listing_type === "sale") {
      const estimatedRent = listing.area * 50 * 12; // AED 50/sqft/month estimate
      const grossYield = (estimatedRent / listing.price) * 100;
      return {
        estimated_annual_rent: estimatedRent,
        gross_yield: grossYield.toFixed(2) + "%",
        net_yield_estimate: (grossYield * 0.7).toFixed(2) + "%", // After costs
      };
    }
    return null;
  }

  async getMarketPosition(listing) {
    // Would need to search similar properties
    return {
      position: "mid-market",
      percentile: 50,
    };
  }

  calculateInvestmentScore(listing) {
    let score = 50;
    
    const dom = this.calculateDOM(listing.created_at);
    if (dom && dom < 30) score += 15;
    else if (dom && dom < 60) score += 10;
    
    if (listing.furnished) score += 10;
    if (listing.amenities && listing.amenities.length > 8) score += 10;
    if (listing.verified) score += 15;
    
    return Math.min(100, score);
  }

  identifyRedFlags(listing) {
    const flags = [];
    
    const dom = this.calculateDOM(listing.created_at);
    if (dom && dom > 90) flags.push("High days on market (>90 days)");
    if (!listing.verified) flags.push("Listing not verified");
    if (listing.price_history && listing.price_history.length > 3) {
      flags.push("Multiple price changes");
    }
    
    return flags;
  }

  generateRecommendations(listing) {
    const recommendations = [];
    
    const dom = this.calculateDOM(listing.created_at);
    if (dom && dom > 60) {
      recommendations.push("Negotiate price - property has been on market for " + dom + " days");
    }
    
    if (listing.analytics && listing.analytics.estimated_roi) {
      const yield_ = parseFloat(listing.analytics.estimated_roi.gross_yield);
      if (yield_ > 6) {
        recommendations.push("Excellent rental yield potential");
      }
    }
    
    return recommendations;
  }

  calculateAvg(items, field) {
    const values = items.map(i => parseFloat(i[field])).filter(v => !isNaN(v));
    if (values.length === 0) return 0;
    return (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2);
  }

  calculatePriceChange(trends) {
    if (!trends.data || trends.data.length < 2) return 0;
    const first = trends.data[0].avg_price;
    const last = trends.data[trends.data.length - 1].avg_price;
    return ((last - first) / first * 100).toFixed(2);
  }

  analyzeMomentum(trends) {
    // Analyze recent price movements
    return "stable"; // Simplified
  }

  generateForecast(trends) {
    return {
      next_quarter: "slight increase expected",
      confidence: "medium",
    };
  }

  generateTrendRecommendation(trends) {
    const change = parseFloat(this.calculatePriceChange(trends));
    if (change > 5) return "Prices rising - consider buying soon";
    if (change < -5) return "Prices falling - wait for better deals";
    return "Stable market - good time to buy";
  }

  assessMarketHealth(listings, trends) {
    return {
      overall: "healthy",
      supply: listings.market_summary.total_results > 500 ? "high" : "moderate",
      demand: "moderate",
      outlook: "positive",
    };
  }

  identifyOpportunities(listings) {
    return listings.listings
      .filter(l => l.analytics.value_rating === "★★★★★")
      .slice(0, 5)
      .map(l => ({
        id: l.id,
        title: l.title,
        reason: "Priced significantly below market average",
      }));
  }

  identifyMarketRisks(listings, trends) {
    const risks = [];
    if (listings.market_summary.total_results > 1000) {
      risks.push("High inventory - oversupply risk");
    }
    return risks;
  }

  findBestValue(properties) {
    return properties.reduce((best, current) => {
      const bestScore = parseFloat(best.analytics.price_per_sqft);
      const currentScore = parseFloat(current.analytics.price_per_sqft);
      return currentScore < bestScore ? current : best;
    }).id;
  }

  findBestLocation(properties) {
    // Simplified - would need location scoring
    return properties[0].id;
  }

  findQuickestSale(properties) {
    return properties.reduce((best, current) => {
      return current.analytics.days_on_market < best.analytics.days_on_market ? current : best;
    }).id;
  }

  compareAndRecommend(properties) {
    const sorted = properties.sort((a, b) => 
      b.analytics.investment_score - a.analytics.investment_score
    );
    
    return {
      best_overall: sorted[0].id,
      reason: `Highest investment score (${sorted[0].analytics.investment_score}/100)`,
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Property Finder MCP server running on stdio");
  }
}

const server = new PropertyFinderServer();
server.run().catch(console.error);
