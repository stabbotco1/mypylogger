#!/usr/bin/env python3
"""
Kiro IDE Research Script
Searches for recent information about Kiro IDE to help create getting started documentation.
"""

import json
import time
from datetime import datetime
from urllib.parse import quote_plus

import requests


def search_web(query, max_results=10):
    """Search using DuckDuckGo's instant answer API (no API key required)"""
    results = []

    # Try DuckDuckGo HTML search
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Simple extraction - look for common patterns
            content = response.text
            if "kiro" in content.lower() and "ide" in content.lower():
                results.append(
                    {
                        "source": "DuckDuckGo Search",
                        "query": query,
                        "found_content": True,
                        "status": "Success - found Kiro IDE references",
                    }
                )
            else:
                results.append(
                    {
                        "source": "DuckDuckGo Search",
                        "query": query,
                        "found_content": False,
                        "status": "No specific Kiro IDE content found",
                    }
                )
    except Exception as e:
        results.append(
            {
                "source": "DuckDuckGo Search",
                "query": query,
                "error": str(e),
                "status": "Failed",
            }
        )

    return results


def check_common_sites():
    """Check common sites that might have Kiro information"""
    sites_to_check = [
        "https://kiro.ai",
        "https://www.kiro.ai",
        "https://kiro.dev",
        "https://kirolabs.com",
        "https://docs.kiro.ai",
        "https://github.com/kiro-ide",
        "https://github.com/kirolabs",
    ]

    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    for url in sites_to_check:
        try:
            response = requests.get(
                url, headers=headers, timeout=10, allow_redirects=True
            )
            results.append(
                {
                    "url": url,
                    "status_code": response.status_code,
                    "accessible": response.status_code == 200,
                    "final_url": response.url,
                    "title_found": (
                        "<title>" in response.text.lower()
                        if response.status_code == 200
                        else False
                    ),
                }
            )
            time.sleep(1)  # Be respectful
        except Exception as e:
            results.append({"url": url, "accessible": False, "error": str(e)})

    return results


def search_package_managers():
    """Check if Kiro is available through package managers"""
    results = []

    # Check npm
    try:
        npm_url = "https://registry.npmjs.org/kiro"
        response = requests.get(npm_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results.append(
                {
                    "package_manager": "npm",
                    "package_name": "kiro",
                    "found": True,
                    "latest_version": data.get("dist-tags", {}).get(
                        "latest", "unknown"
                    ),
                    "description": data.get("description", "No description"),
                }
            )
        else:
            results.append(
                {
                    "package_manager": "npm",
                    "package_name": "kiro",
                    "found": False,
                    "status_code": response.status_code,
                }
            )
    except Exception as e:
        results.append(
            {
                "package_manager": "npm",
                "package_name": "kiro",
                "found": False,
                "error": str(e),
            }
        )

    # Check PyPI
    try:
        pypi_url = "https://pypi.org/pypi/kiro/json"
        response = requests.get(pypi_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results.append(
                {
                    "package_manager": "PyPI",
                    "package_name": "kiro",
                    "found": True,
                    "latest_version": data.get("info", {}).get("version", "unknown"),
                    "description": data.get("info", {}).get(
                        "summary", "No description"
                    ),
                }
            )
        else:
            results.append(
                {
                    "package_manager": "PyPI",
                    "package_name": "kiro",
                    "found": False,
                    "status_code": response.status_code,
                }
            )
    except Exception as e:
        results.append(
            {
                "package_manager": "PyPI",
                "package_name": "kiro",
                "found": False,
                "error": str(e),
            }
        )

    return results


def main():
    """Main research function"""
    print("🔍 Starting Kiro IDE research...")

    research_data = {
        "timestamp": datetime.now().isoformat(),
        "research_date": "September 24, 2025",
        "searches_performed": [],
        "website_checks": [],
        "package_manager_checks": [],
        "summary": {},
        "recommendations": [],
    }

    # Search queries to try
    search_queries = [
        "Kiro IDE getting started 2025",
        "Kiro IDE installation guide",
        "Kiro IDE documentation",
        "Kiro AI IDE download",
        "Kiro IDE tutorial",
        "Kiro IDE setup",
    ]

    print("📝 Performing web searches...")
    for query in search_queries:
        print(f"  Searching: {query}")
        results = search_web(query)
        research_data["searches_performed"].extend(results)
        time.sleep(2)  # Be respectful

    print("🌐 Checking common websites...")
    website_results = check_common_sites()
    research_data["website_checks"] = website_results

    print("📦 Checking package managers...")
    package_results = search_package_managers()
    research_data["package_manager_checks"] = package_results

    # Analyze results
    accessible_sites = [
        site for site in website_results if site.get("accessible", False)
    ]
    found_packages = [pkg for pkg in package_results if pkg.get("found", False)]

    research_data["summary"] = {
        "accessible_websites": len(accessible_sites),
        "found_packages": len(found_packages),
        "total_searches": len(search_queries),
        "successful_searches": len(
            [
                s
                for s in research_data["searches_performed"]
                if s.get("found_content", False)
            ]
        ),
    }

    # Generate recommendations
    if accessible_sites:
        research_data["recommendations"].append(
            f"Found {len(accessible_sites)} accessible Kiro-related websites"
        )

    if found_packages:
        research_data["recommendations"].append(
            f"Found {len(found_packages)} Kiro packages in package managers"
        )

    if not accessible_sites and not found_packages:
        research_data["recommendations"].append(
            "No direct Kiro IDE resources found - may need alternative research methods"
        )

    # Write results to file
    output_file = "kiro_research_results.json"
    with open(output_file, "w") as f:
        json.dump(research_data, f, indent=2)

    print(f"\n✅ Research complete! Results saved to: {output_file}")
    print("📊 Summary:")
    print(f"  - Accessible websites: {research_data['summary']['accessible_websites']}")
    print(f"  - Found packages: {research_data['summary']['found_packages']}")
    print(
        f"  - Successful searches: {research_data['summary']['successful_searches']}/{research_data['summary']['total_searches']}"
    )

    print("\n📋 Next steps:")
    print(f"  1. Review the {output_file} file")
    print("  2. Share the contents with your AI assistant")
    print("  3. Use the findings to create getting started documentation")

    return output_file


if __name__ == "__main__":
    main()
