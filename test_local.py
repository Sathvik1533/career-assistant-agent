"""
Local testing script for Career Assistant Agent

Usage:
    python test_local.py --resume path/to/resume.pdf --role "Software Engineer" --github "username"
"""

import argparse
import json
import os
from dotenv import load_dotenv

from agent import run_career_analysis
from utils import extract_text_from_pdf, format_output_for_display

# Load environment variables
load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Career Assistant Agent - Local Test")
    parser.add_argument("--resume", required=True, help="Path to resume PDF")
    parser.add_argument("--role", required=True, help="Target job role")
    parser.add_argument("--github", required=True, help="GitHub username")
    parser.add_argument("--output", default="report.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    # Validate API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        return
    
    print(f"\n📋 Configuration:")
    print(f"  Resume: {args.resume}")
    print(f"  Role: {args.role}")
    print(f"  GitHub: {args.github}")
    print(f"  Output: {args.output}")
    
    # Extract resume text
    try:
        print(f"\n📄 Extracting text from PDF...")
        resume_text = extract_text_from_pdf(args.resume)
        print(f"  Extracted {len(resume_text)} characters")
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return
    
    # Run analysis
    try:
        report = run_career_analysis(
            resume_text=resume_text,
            target_role=args.role,
            github_username=args.github
        )
        
        # Save to JSON
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {args.output}")
        
        # Display summary
        print("\n" + "="*80)
        print(format_output_for_display(report))
        
        print(f"\n✅ Analysis complete! Check {args.output} for full details.")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
