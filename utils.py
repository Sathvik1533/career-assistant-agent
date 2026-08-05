"""
Utility functions for the Career Assistant Agent:
- PDF parsing
- Output validation
- Response formatting
"""

import pdfplumber
from typing import Dict, Any, List
import json
import re


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Extracted text as string
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from PDF")
        
        return text.strip()
    
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")


def validate_tool_outputs(outputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that all tool outputs are properly structured.
    
    Args:
        outputs: Dictionary of tool outputs
    
    Returns:
        Validation result with status and any errors
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    required_tools = [
        "job_search",
        "skill_gap_analysis",
        "project_ideas",
        "github_check"
    ]
    
    # Check all tools executed
    for tool in required_tools:
        if tool not in outputs:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing output from: {tool}")
        elif not outputs[tool]:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Empty output from: {tool}")
        elif "error" in str(outputs[tool]).lower():
            validation_result["warnings"].append(f"Possible error in {tool}: {outputs[tool][:100]}")
    
    return validation_result


def synthesize_report(outputs: Dict[str, Any], resume_text: str, target_role: str, github_username: str) -> Dict[str, Any]:
    """
    Combine all tool outputs into a comprehensive career report.
    
    Args:
        outputs: Dictionary of all tool outputs
        resume_text: Original resume text
        target_role: Target job role
        github_username: GitHub username
    
    Returns:
        Synthesized report as dictionary
    """
    report = {
        "metadata": {
            "target_role": target_role,
            "github_username": github_username,
            "resume_length": len(resume_text),
        },
        "job_opportunities": parse_json_safely(outputs.get("job_search", "{}")),
        "skill_analysis": parse_json_safely(outputs.get("skill_gap_analysis", "{}")),
        "project_recommendations": parse_json_safely(outputs.get("project_ideas", "{}")),
        "github_portfolio": parse_json_safely(outputs.get("github_check", "{}")),
        "summary": generate_summary(outputs, target_role)
    }
    
    return report


def parse_json_safely(text: str) -> Dict[str, Any]:
    """
    Safely parse JSON from text, handling LLM responses that may include markdown.
    
    Args:
        text: Text that may contain JSON
    
    Returns:
        Parsed JSON as dictionary, or error dict if parsing fails
    """
    try:
        # Try direct parsing first
        return json.loads(text)
    except:
        # Try to extract JSON from markdown code blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except:
                pass
        
        # Try to find JSON object
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except:
                pass
        
        # Return raw text if all else fails
        return {"raw_text": text, "parse_error": True}


def generate_summary(outputs: Dict[str, Any], target_role: str) -> str:
    """
    Generate a human-readable summary of all findings.
    
    Args:
        outputs: Dictionary of all tool outputs
        target_role: Target job role
    
    Returns:
        Summary text
    """
    summary_parts = []
    
    summary_parts.append(f"# Career Analysis Report for {target_role}\n")
    
    # Job opportunities
    job_data = parse_json_safely(outputs.get("job_search", "{}"))
    if "jobs" in job_data:
        summary_parts.append(f"\n## Found {len(job_data['jobs'])} relevant job opportunities")
    
    # Skill gaps
    skill_data = parse_json_safely(outputs.get("skill_gap_analysis", "{}"))
    if "match_percentage" in skill_data:
        summary_parts.append(f"\n## Skill Match: {skill_data['match_percentage']}%")
    if "missing_skills" in skill_data:
        summary_parts.append(f"Missing skills: {', '.join(skill_data['missing_skills'][:5])}")
    
    # Projects
    project_data = parse_json_safely(outputs.get("project_ideas", "{}"))
    if "projects" in project_data:
        summary_parts.append(f"\n## Recommended {len(project_data['projects'])} portfolio projects")
    
    # GitHub
    github_data = parse_json_safely(outputs.get("github_check", "{}"))
    if "public_repos" in github_data:
        summary_parts.append(f"\n## GitHub Profile: {github_data.get('public_repos', 0)} public repositories")
    
    return "\n".join(summary_parts)


def format_output_for_display(report: Dict[str, Any]) -> str:
    """
    Format the report for console display.
    
    Args:
        report: The synthesized report
    
    Returns:
        Formatted text for display
    """
    output = []
    output.append("=" * 80)
    output.append("📊 CAREER ASSISTANT ANALYSIS REPORT")
    output.append("=" * 80)
    output.append("")
    
    # Metadata
    meta = report.get("metadata", {})
    output.append(f"Target Role: {meta.get('target_role', 'N/A')}")
    output.append(f"GitHub: @{meta.get('github_username', 'N/A')}")
    output.append("")
    
    # Summary
    output.append(report.get("summary", "No summary available"))
    output.append("")
    
    # Detailed sections
    output.append("\n" + "=" * 80)
    output.append("For full details, see the JSON output")
    output.append("=" * 80)
    
    return "\n".join(output)


# Export functions
__all__ = [
    "extract_text_from_pdf",
    "validate_tool_outputs",
    "synthesize_report",
    "parse_json_safely",
    "generate_summary",
    "format_output_for_display"
]
