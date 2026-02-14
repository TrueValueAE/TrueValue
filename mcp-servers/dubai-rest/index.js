#!/usr/bin/env node

/**
 * Dubai REST API MCP Server
 * Provides title deed verification and property ownership data
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

const API_KEY = process.env.DUBAI_REST_API_KEY;
const BASE_URL = "https://dubairest.gov.ae/api";

class DubaiRESTServer {
  constructor() {
    this.server = new Server(
      {
        name: "dubai-rest-api",
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
          name: "verify_title_deed",
          description: "Verify property ownership and title deed authenticity",
          inputSchema: {
            type: "object",
            properties: {
              title_deed_number: {
                type: "string",
                description: "Title deed number",
              },
              property_id: {
                type: "string",
                description: "Property ID (DEWA premise number or Makani number)",
              },
            },
            required: ["title_deed_number"],
          },
        },
        {
          name: "check_encumbrances",
          description: "Check for mortgages, liens, or other encumbrances on property",
          inputSchema: {
            type: "object",
            properties: {
              title_deed_number: {
                type: "string",
                description: "Title deed number",
              },
            },
            required: ["title_deed_number"],
          },
        },
        {
          name: "ownership_history",
          description: "Get ownership chain and transaction history",
          inputSchema: {
            type: "object",
            properties: {
              property_id: {
                type: "string",
                description: "Property ID",
              },
              years_back: {
                type: "number",
                description: "Number of years to look back (default: 5)",
              },
            },
            required: ["property_id"],
          },
        },
        {
          name: "property_valuation",
          description: "Get official property valuation from DLD",
          inputSchema: {
            type: "object",
            properties: {
              property_id: {
                type: "string",
                description: "Property ID",
              },
            },
            required: ["property_id"],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "verify_title_deed":
            return await this.verifyTitleDeed(args);
          case "check_encumbrances":
            return await this.checkEncumbrances(args);
          case "ownership_history":
            return await this.getOwnershipHistory(args);
          case "property_valuation":
            return await this.getPropertyValuation(args);
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

  async verifyTitleDeed(args) {
    const response = await axios.get(
      `${BASE_URL}/property/title-deed/${args.title_deed_number}`,
      {
        headers: {
          "Authorization": `Bearer ${API_KEY}`,
          "Content-Type": "application/json",
        },
      }
    );

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data, null, 2),
        },
      ],
    };
  }

  async checkEncumbrances(args) {
    const response = await axios.get(
      `${BASE_URL}/property/encumbrances/${args.title_deed_number}`,
      {
        headers: {
          "Authorization": `Bearer ${API_KEY}`,
        },
      }
    );

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data, null, 2),
        },
      ],
    };
  }

  async getOwnershipHistory(args) {
    const yearsBack = args.years_back || 5;
    const response = await axios.get(
      `${BASE_URL}/property/ownership-history/${args.property_id}`,
      {
        headers: {
          "Authorization": `Bearer ${API_KEY}`,
        },
        params: {
          years: yearsBack,
        },
      }
    );

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data, null, 2),
        },
      ],
    };
  }

  async getPropertyValuation(args) {
    const response = await axios.get(
      `${BASE_URL}/property/valuation/${args.property_id}`,
      {
        headers: {
          "Authorization": `Bearer ${API_KEY}`,
        },
      }
    );

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Dubai REST API MCP server running on stdio");
  }
}

const server = new DubaiRESTServer();
server.run().catch(console.error);
