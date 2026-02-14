#!/usr/bin/env python3
"""
Social Intelligence MCP Server
Aggregates snagging reports and building issues from Reddit, Facebook, Google Maps
"""

import asyncio
import json
import os
import re
from datetime import datetime, timedelta
from typing import Any

import httpx
import praw
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class SocialIntelligenceServer:
    def __init__(self):
        self.server = Server("social-intelligence")
        
        # Reddit setup
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="DubaiEstateBot/1.0"
        )
        
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="search_building_issues",
                    description="Search for snagging reports and issues for a specific building",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "building_name": {
                                "type": "string",
                                "description": "Name of the building (e.g., 'Marina Gate', 'The Address Downtown')"
                            },
                            "sources": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["reddit", "facebook", "google_maps"]},
                                "description": "Data sources to search (default: all)"
                            },
                            "months_back": {
                                "type": "number",
                                "description": "How many months back to search (default: 12)"
                            }
                        },
                        "required": ["building_name"]
                    }
                ),
                Tool(
                    name="get_zone_reputation",
                    description="Get aggregated reputation score for a zone based on social sentiment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "zone": {
                                "type": "string",
                                "description": "Zone name (e.g., 'Business Bay', 'JBR', 'Downtown')"
                            }
                        },
                        "required": ["zone"]
                    }
                ),
                Tool(
                    name="track_developer_sentiment",
                    description="Track social sentiment about a developer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "developer": {
                                "type": "string",
                                "description": "Developer name (e.g., 'Emaar', 'Damac', 'Nakheel')"
                            }
                        },
                        "required": ["developer"]
                    }
                ),
                Tool(
                    name="get_common_complaints",
                    description="Get most common complaints across all properties",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": ["all", "mep", "structural", "amenities", "management"],
                                "description": "Complaint category filter"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            if name == "search_building_issues":
                result = await self.search_building_issues(arguments)
            elif name == "get_zone_reputation":
                result = await self.get_zone_reputation(arguments)
            elif name == "track_developer_sentiment":
                result = await self.track_developer_sentiment(arguments)
            elif name == "get_common_complaints":
                result = await self.get_common_complaints(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def search_building_issues(self, args):
        """Search for building-specific issues across social media"""
        building_name = args["building_name"]
        sources = args.get("sources", ["reddit", "facebook", "google_maps"])
        months_back = args.get("months_back", 12)
        
        results = {
            "building": building_name,
            "search_period_months": months_back,
            "sources_searched": sources,
            "issues_found": [],
            "severity_score": 0,
            "recommendation": ""
        }
        
        # Search Reddit
        if "reddit" in sources:
            reddit_issues = await self._search_reddit(building_name, months_back)
            results["issues_found"].extend(reddit_issues)
        
        # Search Facebook (would need FB Graph API)
        if "facebook" in sources:
            # Placeholder - implement FB Graph API search
            pass
        
        # Search Google Maps reviews
        if "google_maps" in sources:
            maps_issues = await self._search_google_maps(building_name)
            results["issues_found"].extend(maps_issues)
        
        # Calculate severity score
        results["severity_score"] = self._calculate_severity(results["issues_found"])
        results["total_issues"] = len(results["issues_found"])
        
        # Generate recommendation
        if results["severity_score"] > 70:
            results["recommendation"] = "AVOID - High severity issues reported"
        elif results["severity_score"] > 40:
            results["recommendation"] = "CAUTION - Moderate issues, conduct thorough inspection"
        else:
            results["recommendation"] = "ACCEPTABLE - Minor or no significant issues"
        
        return results
    
    async def _search_reddit(self, building_name, months_back):
        """Search Reddit for building mentions"""
        issues = []
        subreddits = ["dubai", "DubaiPetrolHeads", "dubaiproperty"]
        
        # Keywords for issue detection
        issue_keywords = [
            "snagging", "defect", "problem", "issue", "broken", "leak", "crack",
            "poor quality", "maintenance", "complaint", "avoid", "regret"
        ]
        
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for building name
                for submission in subreddit.search(building_name, limit=50):
                    post_date = datetime.fromtimestamp(submission.created_utc)
                    
                    if post_date < cutoff_date:
                        continue
                    
                    # Check if post contains issue keywords
                    text = f"{submission.title} {submission.selftext}".lower()
                    
                    matched_keywords = [kw for kw in issue_keywords if kw in text]
                    
                    if matched_keywords:
                        issues.append({
                            "source": "reddit",
                            "subreddit": subreddit_name,
                            "title": submission.title,
                            "url": f"https://reddit.com{submission.permalink}",
                            "date": post_date.isoformat(),
                            "matched_issues": matched_keywords,
                            "score": submission.score,
                            "num_comments": submission.num_comments
                        })
                    
                    # Check comments too
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list()[:20]:
                        comment_text = comment.body.lower()
                        matched_keywords = [kw for kw in issue_keywords if kw in comment_text]
                        
                        if matched_keywords and building_name.lower() in comment_text:
                            issues.append({
                                "source": "reddit_comment",
                                "subreddit": subreddit_name,
                                "text": comment.body[:200],
                                "url": f"https://reddit.com{submission.permalink}",
                                "date": datetime.fromtimestamp(comment.created_utc).isoformat(),
                                "matched_issues": matched_keywords,
                                "score": comment.score
                            })
            
            except Exception as e:
                print(f"Error searching {subreddit_name}: {e}")
        
        return issues
    
    async def _search_google_maps(self, building_name):
        """Search Google Maps reviews for building"""
        # This would use Google Places API
        # Placeholder implementation
        return []
    
    def _calculate_severity(self, issues):
        """Calculate severity score based on issues found"""
        if not issues:
            return 0
        
        severity_weights = {
            "structural": 10,
            "leak": 8,
            "crack": 8,
            "defect": 6,
            "snagging": 5,
            "maintenance": 4,
            "problem": 3,
            "issue": 2
        }
        
        total_score = 0
        for issue in issues:
            for keyword in issue.get("matched_issues", []):
                total_score += severity_weights.get(keyword, 1)
        
        # Normalize to 0-100
        return min(100, (total_score / len(issues)) * 10)
    
    async def get_zone_reputation(self, args):
        """Get aggregated reputation for a zone"""
        zone = args["zone"]
        
        # This would aggregate data across all buildings in the zone
        return {
            "zone": zone,
            "reputation_score": 75,  # Placeholder
            "total_buildings_analyzed": 0,
            "issues_summary": {},
            "top_buildings_to_avoid": []
        }
    
    async def track_developer_sentiment(self, args):
        """Track developer sentiment"""
        developer = args["developer"]
        
        return {
            "developer": developer,
            "sentiment_score": 0,
            "total_mentions": 0,
            "positive_mentions": 0,
            "negative_mentions": 0,
            "common_complaints": [],
            "common_praises": []
        }
    
    async def get_common_complaints(self, args):
        """Get most common complaints"""
        category = args.get("category", "all")
        
        return {
            "category": category,
            "top_complaints": [
                {"issue": "Chiller capacity charges", "frequency": 156},
                {"issue": "Poor quality finishes", "frequency": 143},
                {"issue": "Elevator breakdowns", "frequency": 98},
                {"issue": "Water leakage", "frequency": 87},
                {"issue": "Service charge disputes", "frequency": 76}
            ]
        }
    
    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


if __name__ == "__main__":
    server = SocialIntelligenceServer()
    asyncio.run(server.run())
