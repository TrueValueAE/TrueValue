#!/usr/bin/env node

/**
 * HTTP Wrapper for MCP Servers
 * Converts stdio-based MCP servers to HTTP endpoints
 * 
 * This allows your Telegram bot / API to call MCP servers via HTTP
 */

import express from 'express';
import { spawn } from 'child_process';
import cors from 'cors';

const app = express();
app.use(express.json());
app.use(cors());

/**
 * Generic MCP Server HTTP Wrapper
 * 
 * Takes a stdio-based MCP server and exposes it via HTTP
 */
class MCPServerHTTPWrapper {
  constructor(serverPath, serverCommand) {
    this.serverPath = serverPath;
    this.serverCommand = serverCommand;
    this.process = null;
  }

  start() {
    // Spawn the MCP server process
    this.process = spawn(this.serverCommand, [this.serverPath], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    this.process.stderr.on('data', (data) => {
      console.log(`[MCP Server] ${data.toString()}`);
    });
  }

  async callTool(toolName, toolInput) {
    return new Promise((resolve, reject) => {
      // Send request to MCP server via stdin
      const request = {
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: toolInput
        }
      };

      this.process.stdin.write(JSON.stringify(request) + '\n');

      // Listen for response on stdout
      const onData = (data) => {
        try {
          const response = JSON.parse(data.toString());
          this.process.stdout.off('data', onData);
          resolve(response.result);
        } catch (err) {
          reject(err);
        }
      };

      this.process.stdout.on('data', onData);

      // Timeout after 30 seconds
      setTimeout(() => {
        this.process.stdout.off('data', onData);
        reject(new Error('MCP server timeout'));
      }, 30000);
    });
  }
}

/**
 * SIMPLER APPROACH: Direct Implementation
 * 
 * Instead of wrapping stdio servers, implement tools directly in HTTP
 */

// Example: Bayut Search Endpoint
app.post('/api/bayut/search', async (req, res) => {
  const { location, purpose, min_price, max_price, property_type } = req.body;

  try {
    // Call Bayut API directly
    const axios = require('axios');
    const response = await axios.get('https://bayut.p.rapidapi.com/properties/list', {
      params: {
        locationExternalIDs: location,
        purpose,
        priceMin: min_price,
        priceMax: max_price,
        categoryExternalID: property_type,
        hitsPerPage: 25,
        page: 0,
        lang: 'en',
        sort: 'date-desc'
      },
      headers: {
        'X-RapidAPI-Key': process.env.BAYUT_API_KEY,
        'X-RapidAPI-Host': 'bayut.p.rapidapi.com'
      }
    });

    // Return enriched results
    res.json({
      success: true,
      data: response.data,
      meta: {
        total: response.data.nbHits,
        page: 0
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Example: Dubai REST Title Verification
app.post('/api/dubai-rest/verify-title', async (req, res) => {
  const { title_deed_number } = req.body;

  try {
    const axios = require('axios');
    const response = await axios.get(
      `https://dubairest.gov.ae/api/property/title-deed/${title_deed_number}`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.DUBAI_REST_API_KEY}`
        }
      }
    );

    res.json({
      success: true,
      data: response.data
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Example: Chiller Cost Calculator
app.post('/api/chiller/calculate', async (req, res) => {
  const { provider, area_sqft } = req.body;

  try {
    // Simple calculation (in production, scrape latest rates)
    const rates = {
      empower: {
        consumption_rate: 0.58, // fils per kWh
        fixed_capacity_charge: 85 // AED per TR per month
      },
      lootah: {
        consumption_rate: 0.52,
        fixed_capacity_charge: 0 // No fixed charges
      }
    };

    const rate = rates[provider];
    const estimated_tr = area_sqft / 285.7; // Typical conversion
    const estimated_consumption_kwh = area_sqft * 12; // per year

    const consumption_cost = estimated_consumption_kwh * rate.consumption_rate / 100;
    const capacity_cost = estimated_tr * rate.fixed_capacity_charge * 12;
    const total_annual = consumption_cost + capacity_cost;

    res.json({
      success: true,
      data: {
        provider,
        area_sqft,
        estimated_capacity_tr: estimated_tr.toFixed(2),
        annual_consumption_cost_aed: consumption_cost.toFixed(2),
        annual_capacity_cost_aed: capacity_cost.toFixed(2),
        total_annual_cost_aed: total_annual.toFixed(2),
        cost_per_sqft_per_year: (total_annual / area_sqft).toFixed(2),
        warning: (total_annual / area_sqft) > 15 ? 'HIGH' : 'ACCEPTABLE'
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// List all available tools
app.get('/api/tools', (req, res) => {
  res.json({
    tools: [
      {
        name: 'bayut_search',
        endpoint: '/api/bayut/search',
        description: 'Search Bayut properties'
      },
      {
        name: 'verify_title_deed',
        endpoint: '/api/dubai-rest/verify-title',
        description: 'Verify title deed via Dubai REST'
      },
      {
        name: 'calculate_chiller_cost',
        endpoint: '/api/chiller/calculate',
        description: 'Calculate chiller costs'
      }
      // ... list all tools
    ]
  });
});

const PORT = process.env.PORT || 8000;

app.listen(PORT, () => {
  console.log(`🚀 MCP HTTP Gateway running on port ${PORT}`);
  console.log(`📊 Available at: http://localhost:${PORT}`);
  console.log(`📋 Tools list: http://localhost:${PORT}/api/tools`);
});

export default app;
