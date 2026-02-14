#!/usr/bin/env python3
"""
Test the bot locally by simulating a query
"""

import asyncio
import sys
sys.path.insert(0, '.')

from main import handle_query

async def test():
    print("Testing handle_query with simple chiller calculation...")
    print("="*50)

    try:
        result = await handle_query(
            "Calculate chiller cost for 1500 sqft Empower property",
            user_id="test_user"
        )
        print("\n✅ SUCCESS! Response received:")
        print("="*50)
        print(result)
        print("="*50)
        print(f"\nResponse length: {len(result)} characters")

        # Check for Markdown issues
        problematic_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        issues = []
        for char in problematic_chars:
            if char in result:
                count = result.count(char)
                issues.append(f"  {char}: {count} occurrences")

        if issues:
            print("\n⚠️  Potential Markdown issues:")
            for issue in issues[:10]:  # Show first 10
                print(issue)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
