# backend/app/company_logos.py
"""
Company logos and branding information.
Used to display company logos in interviews and support random company questions.
"""

COMPANY_LOGOS = {
    "Google": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.google.com&size=128",
    "Meta": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.meta.com&size=128",
    "Amazon": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.amazon.com&size=128",
    "Apple": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.apple.com&size=128",
    "Microsoft": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.microsoft.com&size=128",
    "Netflix": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.netflix.com&size=128",
    "Uber": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.uber.com&size=128",
    "Airbnb": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.airbnb.com&size=128",
    "Stripe": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.stripe.com&size=128",
    "Salesforce": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.salesforce.com&size=128",
    "Freshworks": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.freshworks.com&size=128",
    "Zoho": "https://www.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://www.zoho.com&size=128",
}

# All valid companies from CSV
VALID_COMPANIES_SET = {
    "Google", "Meta", "Amazon", "Apple", "Microsoft",
    "Netflix", "Uber", "Airbnb", "Stripe", "Salesforce",
    "Freshworks", "Zoho"
}

def get_company_logo(company_name: str) -> str:
    """
    Get the logo URL for a company.
    Returns favicon URL or a default placeholder if not found.
    """
    if not company_name:
        return get_default_logo()
    
    logo = COMPANY_LOGOS.get(company_name)
    if logo:
        return logo
    
    # Try case-insensitive match
    for key, value in COMPANY_LOGOS.items():
        if key.lower() == company_name.lower():
            return value
    
    return get_default_logo()


def get_default_logo() -> str:
    """
    Returns a default SVG logo (purple square with 'C' for Company).
    This is a base64-encoded SVG for offline use.
    """
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI4IiBmaWxsPSIjNjU2NUY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnRTaXplPSIxNiIgZm9udFdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5DPC90ZXh0Pjwvc3ZnPg=='


def is_valid_company(company_name: str) -> bool:
    """Check if a company is in our valid companies set."""
    if not company_name:
        return False
    return any(c.lower() == company_name.lower() for c in VALID_COMPANIES_SET)
