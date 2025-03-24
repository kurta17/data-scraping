import json
import re

def extract_company_info(data, keys=["name", "company", "companyName"]):
    """Recursively search for keys related to company information in the JSON data."""
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            # If the key indicates company info, save the value (or the whole dict if complex)
            if any(re.search(pattern, k, re.IGNORECASE) for pattern in keys):
                results.append({k: v})
            # Recurse into the value
            results.extend(extract_company_info(v, keys))
    elif isinstance(data, list):
        for item in data:
            results.extend(extract_company_info(item, keys))
    return results


# Load the HAR file
with open("data/www.companyinfo.ge.har", "r", encoding="utf-8") as f:
    har_data = json.load(f)

log = har_data.get("log", {})
entries = log.get("entries", [])

company_info_list = []

for entry in entries:
    response = entry.get("response", {})
    content = response.get("content", {})
    mime_type = content.get("mimeType", "")
    
    # Check if the response might be JSON
    if "json" in mime_type.lower():
        text = content.get("text", "")
        try:
            json_data = json.loads(text)
            companies = extract_company_info(json_data)
            if companies:
                company_info_list.extend(companies)
        except Exception as e:
            # Could not parse as JSON, continue with next entry
            continue
    else:
        # Sometimes the text is not marked as JSON but may contain JSON content.
        text = content.get("text", "")
        try:
            json_data = json.loads(text)
            companies = extract_company_info(json_data)
            if companies:
                company_info_list.extend(companies)
        except Exception:
            # If not JSON, optionally use regex to search for patterns that look like company names
            # Example: Searching for text between tags that might denote company names (this is very heuristic)
            potential_names = re.findall(r'Company\s*[:\-]\s*([\w\s,&]+)', text, re.IGNORECASE)
            if potential_names:
                for name in potential_names:
                    company_info_list.append({"company": name.strip()})

# Remove duplicates (optional)
unique_companies = []
seen = set()
for info in company_info_list:
    # Convert dictionary to tuple for hashable check (if possible)
    key = tuple(info.items())
    if key not in seen:
        seen.add(key)
        unique_companies.append(info)

print("Extracted Company Information:")
for company in unique_companies:
    print(company)
