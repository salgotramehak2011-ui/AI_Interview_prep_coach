"""Domain prompt registry."""

from app.core.constants import Domain
from app.prompts import ai_ml_prompt, cybersecurity_prompt, web_dev_prompt


def get_domain_prompts(domain: str):
    mapping = {
        Domain.AI_ML.value: ai_ml_prompt,
        Domain.WEB_DEV.value: web_dev_prompt,
        Domain.CYBERSECURITY.value: cybersecurity_prompt,
    }
    module = mapping.get(domain)
    if not module:
        raise ValueError(f"No prompts for domain: {domain}")
    return module
