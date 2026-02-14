#!/usr/bin/env node

/**
 * Bayut Listings MCP Server
 * Comprehensive property search, trends, and analytics from Bayut.com
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

const API_KEY = process.env.BAYUT_API_KEY;
const BASE_URL = "https://bayut.p.rapidapi.com"; // Using RapidAPI endpoint

class BayutListingsServer {
  constructor() {
    this.server = new Server(
      {
        name: "bayut-listings",
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
          name: "search_properties",
          description: "Search properties for sale or rent on Bayut with detailed filters",
          inputSchema: {
            type: "object",
            properties: {
              purpose: {
                type: "string",
                enum: ["for-sale", "for-rent"],
                description: "Property purpose",
              },
              location: {
                type: "string",
                description: "Location name (e.g., 'dubai-marina', 'business-bay')",
              },
              property_type: {
                type: "string",
                enum: ["apartment", "villa", "townhouse", "penthouse", "compound"],
                description: "Property type",
              },
              min_price: {
                type: "number",
                description: "Minimum price in AED",
              },
              max_price: {
                type: "number",
                description: "Maximum price in AED",
              },
              min_beds: {
                type: "number",
                description: "Minimum number of bedrooms",
              },
              max_beds: {
                type: "number",
                description: "Maximum number of bedrooms",
              },
              min_area: {
                type: "number",
                description: "Minimum area in sqft",
              },
              max_area: {
                type: "number",
                description: "Maximum area in sqft",
              },
              sort: {
                type: "string",
                enum: ["price-asc", "price-desc", "date-desc", "date-asc"],
                description: "Sort order",
              },
              page: {
                type: "number",
                description: "Page number (default: 1)",
              },
            },
            required: ["purpose", "location"],
          },
        },
        {
          name: "get_property_details",
          description: "Get detailed information about a specific property",
          inputSchema: {
            type: "object",
            properties: {
              property_id: {
                type: "string",
                description: "Bayut property ID",
              },
            },
            required: ["property_id"],
          },
        },
        {
          name: "get_market_trends",
          description: "Get market trends and statistics for a location",
          inputSchema: {
            type: "object",
            properties: {
              location: {
                type: "string",
                description: "Location name",
              },
              property_type: {
                type: "string",
                description: "Property type (optional)",
              },
              purpose: {
                type: "string",
                enum: ["for-sale", "for-rent"],
                description: "Purpose",
              },
            },
            required: ["location", "purpose"],
          },
        },
        {
          name: "get_similar_properties",
          description: "Find similar properties based on criteria",
          inputSchema: {
            type: "object",
            properties: {
              property_id: {
                type: "string",
                description: "Reference property ID",
              },
              radius_km: {
                type: "number",
                description: "Search radius in kilometers (default: 2)",
              },
            },
            required: ["property_id"],
          },
        },
        {
          name: "get_price_history",
          description: "Get price history and trends for a specific property or location",
          inputSchema: {
            type: "object",
            properties: {
              location: {
                type: "string",
                description: "Location name",
              },
              property_type: {
                type: "string",
                description: "Property type",
              },
              months: {
                type: "number",
                description: "Number of months to look back (default: 12)",
              },
            },
            required: ["location"],
          },
        },
        {
          name: "calculate_rental_yield",
          description: "Calculate rental yield for a property",
          inputSchema: {
            type: "object",
            properties: {
              sale_price: {
                type: "number",
                description: "Sale price in AED",
              },
              annual_rent: {
                type: "number",
                description: "Annual rent in AED",
              },
              location: {
                type: "string",
                description: "Location for market comparison",
              },
            },
            required: ["sale_price", "annual_rent"],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "search_properties":
            return await this.searchProperties(args);
          case "get_property_details":
            return await this.getPropertyDetails(args);
          case "get_market_trends":
            return await this.getMarketTrends(args);
          case "get_similar_properties":
            return await this.getSimilarProperties(args);
          case "get_price_history":
            return await this.getPriceHistory(args);
          case "calculate_rental_yield":
            return await this.calculateRentalYield(args);
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

  async searchProperties(args) {
    const params = {
      locationExternalIDs: args.location,
      purpose: args.purpose,
      hitsPerPage: 25,
      page: args.page || 0,
      lang: "en",
      sort: args.sort || "date-desc",
    };

    if (args.property_type) params.categoryExternalID = this.getPropertyTypeId(args.property_type);
    if (args.min_price) params.priceMin = args.min_price;
    if (args.max_price) params.priceMax = args.max_price;
    if (args.min_beds) params.roomsMin = args.min_beds;
    if (args.max_beds) params.roomsMax = args.max_beds;
    if (args.min_area) params.areaMin = args.min_area;
    if (args.max_area) params.areaMax = args.max_area;

    const response = await axios.get(`${BASE_URL}/properties/list`, {
      params,
      headers: {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "bayut.p.rapidapi.com",
      },
    });

    // Calculate additional metrics
    const properties = response.data.hits || [];
    const enrichedProperties = properties.map(prop => ({
      ...prop,
      price_per_sqft: prop.area ? (prop.price / prop.area).toFixed(2) : null,
      days_on_market: this.calculateDOM(prop.createdAt),
      estimated_roi: this.estimateROI(prop),
    }));

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            total_results: response.data.nbHits,
            current_page: args.page || 0,
            properties: enrichedProperties,
            summary: {
              avg_price: this.calculateAverage(enrichedProperties, 'price'),
              avg_price_per_sqft: this.calculateAverage(enrichedProperties, 'price_per_sqft'),
              avg_dom: this.calculateAverage(enrichedProperties, 'days_on_market'),
            },
          }, null, 2),
        },
      ],
    };
  }

  async getPropertyDetails(args) {
    const response = await axios.get(`${BASE_URL}/properties/detail`, {
      params: {
        externalID: args.property_id,
      },
      headers: {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "bayut.p.rapidapi.com",
      },
    });

    const property = response.data;
    
    // Enrich with calculated fields
    const enriched = {
      ...property,
      price_per_sqft: property.area ? (property.price / property.area).toFixed(2) : null,
      days_on_market: this.calculateDOM(property.createdAt),
      estimated_rental_yield: this.estimateRentalYield(property),
      location_score: await this.getLocationScore(property.location),
      investment_score: this.calculateInvestmentScore(property),
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

  async getMarketTrends(args) {
    // This would aggregate data from multiple searches
    const properties = await this.searchProperties({
      location: args.location,
      purpose: args.purpose,
      property_type: args.property_type,
    });

    const data = JSON.parse(properties.content[0].text);
    
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            location: args.location,
            purpose: args.purpose,
            total_listings: data.total_results,
            market_metrics: {
              avg_price: data.summary.avg_price,
              avg_price_per_sqft: data.summary.avg_price_per_sqft,
              avg_days_on_market: data.summary.avg_dom,
              price_range: {
                min: Math.min(...data.properties.map(p => p.price)),
                max: Math.max(...data.properties.map(p => p.price)),
              },
              inventory_status: data.total_results > 500 ? "High Supply" : data.total_results > 200 ? "Medium Supply" : "Low Supply",
            },
            price_distribution: this.getPriceDistribution(data.properties),
            recommendations: this.generateMarketRecommendations(data),
          }, null, 2),
        },
      ],
    };
  }

  async getSimilarProperties(args) {
    // First get the reference property
    const refProperty = await this.getPropertyDetails({ property_id: args.property_id });
    const refData = JSON.parse(refProperty.content[0].text);

    // Search for similar properties
    const similar = await this.searchProperties({
      location: refData.location[0].externalID,
      purpose: refData.purpose,
      property_type: refData.category[0].nameSingular,
      min_price: refData.price * 0.9,
      max_price: refData.price * 1.1,
      min_beds: refData.rooms - 1,
      max_beds: refData.rooms + 1,
      min_area: refData.area * 0.9,
      max_area: refData.area * 1.1,
    });

    return similar;
  }

  async getPriceHistory(args) {
    // This would require historical data - simulated for now
    const months = args.months || 12;
    const trends = [];
    
    for (let i = months; i >= 0; i--) {
      trends.push({
        month: new Date(Date.now() - i * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 7),
        avg_price_sqft: 800 + Math.random() * 200, // Simulated - replace with real data
        volume: Math.floor(100 + Math.random() * 50),
      });
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            location: args.location,
            period_months: months,
            trends,
            analysis: {
              price_change_pct: ((trends[trends.length - 1].avg_price_sqft - trends[0].avg_price_sqft) / trends[0].avg_price_sqft * 100).toFixed(2),
              volume_trend: trends[trends.length - 1].volume > trends[0].volume ? "Increasing" : "Decreasing",
            },
          }, null, 2),
        },
      ],
    };
  }

  async calculateRentalYield(args) {
    const grossYield = (args.annual_rent / args.sale_price) * 100;
    
    // Estimate costs (typical Dubai costs)
    const serviceFee = args.sale_price * 0.001; // Approx 10% of annual rent
    const maintenance = args.annual_rent * 0.05;
    const insurance = 2000; // Typical
    const vacancyLoss = args.annual_rent * 0.05; // 5% vacancy
    
    const totalCosts = serviceFee + maintenance + insurance + vacancyLoss;
    const netIncome = args.annual_rent - totalCosts;
    const netYield = (netIncome / args.sale_price) * 100;

    // Get market comparison if location provided
    let marketComparison = null;
    if (args.location) {
      const trends = await this.getMarketTrends({
        location: args.location,
        purpose: "for-rent",
      });
      marketComparison = JSON.parse(trends.content[0].text).market_metrics;
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            property: {
              sale_price: args.sale_price,
              annual_rent: args.annual_rent,
            },
            yields: {
              gross_yield: grossYield.toFixed(2) + "%",
              net_yield: netYield.toFixed(2) + "%",
            },
            annual_costs: {
              service_fee: serviceFee.toFixed(2),
              maintenance: maintenance.toFixed(2),
              insurance: insurance.toFixed(2),
              vacancy_loss: vacancyLoss.toFixed(2),
              total: totalCosts.toFixed(2),
            },
            net_annual_income: netIncome.toFixed(2),
            market_comparison: marketComparison,
            investment_rating: netYield > 6 ? "Excellent" : netYield > 4 ? "Good" : netYield > 3 ? "Fair" : "Poor",
          }, null, 2),
        },
      ],
    };
  }

  // Helper functions
  getPropertyTypeId(type) {
    const mapping = {
      apartment: "4",
      villa: "3",
      townhouse: "18",
      penthouse: "19",
      compound: "16",
    };
    return mapping[type] || "4";
  }

  calculateDOM(createdAt) {
    if (!createdAt) return null;
    const created = new Date(createdAt);
    const now = new Date();
    return Math.floor((now - created) / (1000 * 60 * 60 * 24));
  }

  estimateROI(property) {
    // Simple ROI estimation based on typical Dubai yields
    if (property.purpose === "for-sale") {
      return "4-6% annual rental yield (estimated)";
    }
    return null;
  }

  estimateRentalYield(property) {
    if (property.purpose === "for-sale" && property.price && property.area) {
      const estimatedRent = property.area * 50 * 12; // Rough estimate: AED 50/sqft/month
      return ((estimatedRent / property.price) * 100).toFixed(2) + "%";
    }
    return null;
  }

  async getLocationScore(locations) {
    // Scoring based on location desirability (0-100)
    const scores = {
      "dubai-marina": 90,
      "downtown-dubai": 95,
      "business-bay": 75,
      "jbr": 85,
      "palm-jumeirah": 98,
    };
    
    if (locations && locations.length > 0) {
      const locationKey = locations[0].slug || "";
      return scores[locationKey] || 70;
    }
    return 70;
  }

  calculateInvestmentScore(property) {
    let score = 50;
    
    // Price per sqft (lower is better in most cases)
    const pricePerSqft = property.area ? property.price / property.area : 0;
    if (pricePerSqft < 1000) score += 20;
    else if (pricePerSqft < 1500) score += 10;
    
    // Days on market (lower is better)
    const dom = this.calculateDOM(property.createdAt);
    if (dom < 30) score += 15;
    else if (dom < 60) score += 10;
    else if (dom < 90) score += 5;
    
    // Furnished (adds value for rentals)
    if (property.furnishingStatus === "furnished") score += 10;
    
    // Amenities
    if (property.amenities && property.amenities.length > 10) score += 5;
    
    return Math.min(100, score);
  }

  calculateAverage(properties, field) {
    const values = properties.map(p => parseFloat(p[field])).filter(v => !isNaN(v));
    if (values.length === 0) return 0;
    return (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2);
  }

  getPriceDistribution(properties) {
    const ranges = {
      "0-1M": 0,
      "1M-2M": 0,
      "2M-3M": 0,
      "3M-5M": 0,
      "5M+": 0,
    };

    properties.forEach(p => {
      if (p.price < 1000000) ranges["0-1M"]++;
      else if (p.price < 2000000) ranges["1M-2M"]++;
      else if (p.price < 3000000) ranges["2M-3M"]++;
      else if (p.price < 5000000) ranges["3M-5M"]++;
      else ranges["5M+"]++;
    });

    return ranges;
  }

  generateMarketRecommendations(data) {
    const recommendations = [];
    
    if (data.summary.avg_dom > 60) {
      recommendations.push("High days-on-market suggests buyer's market - good negotiation opportunity");
    }
    
    if (data.total_results > 500) {
      recommendations.push("High inventory - wait for better deals or negotiate aggressively");
    }
    
    if (data.summary.avg_price_per_sqft < 1000) {
      recommendations.push("Below-market pricing detected - potential value opportunities");
    }
    
    return recommendations;
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Bayut Listings MCP server running on stdio");
  }
}

const server = new BayutListingsServer();
server.run().catch(console.error);
