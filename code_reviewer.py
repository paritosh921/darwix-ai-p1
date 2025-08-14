import json
import re
from openai import OpenAI
from typing import Dict, List, Optional


class EmpathticCodeReviewer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def _assess_comment_severity(self, comment: str) -> str:
        """Assess the severity/harshness of a review comment"""
        harsh_indicators = [
            'bad', 'terrible', 'awful', 'stupid', 'dumb', 'wrong', 'never',
            'always', 'completely', 'totally', 'absolutely', 'obviously'
        ]
        
        neutral_indicators = [
            'could', 'might', 'consider', 'suggest', 'perhaps', 'maybe',
            'improvement', 'better', 'optimize'
        ]
        
        comment_lower = comment.lower()
        
        harsh_count = sum(1 for indicator in harsh_indicators if indicator in comment_lower)
        neutral_count = sum(1 for indicator in neutral_indicators if indicator in comment_lower)
        
        if harsh_count > neutral_count:
            return "harsh"
        elif neutral_count > harsh_count:
            return "neutral"
        else:
            return "moderate"
    
    def _get_relevant_resources(self, comment: str, code_snippet: str) -> List[str]:
        """Generate relevant documentation links based on comment content"""
        resources = []
        
        comment_lower = comment.lower()
        code_lower = code_snippet.lower()
        
        # Python-specific resources
        if 'variable' in comment_lower or 'naming' in comment_lower:
            resources.append("[PEP 8 - Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)")
        
        if 'efficient' in comment_lower or 'performance' in comment_lower or 'loop' in comment_lower:
            resources.append("[Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)")
            
        if 'comprehension' in comment_lower or 'list comprehension' in comment_lower:
            resources.append("[List Comprehensions - Python Documentation](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)")
            
        if '== true' in code_lower or '== false' in code_lower:
            resources.append("[PEP 8 - Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)")
            
        if 'function' in comment_lower:
            resources.append("[PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)")
            
        return resources

    def _create_system_prompt(self, severity: str) -> str:
        """Create a system prompt tailored to the comment severity"""
        base_prompt = """You are a senior software engineer and mentor known for your empathetic and educational approach to code reviews. Your goal is to transform critical feedback into constructive, encouraging guidance that helps developers learn and grow.

Key principles:
1. Always start with something positive or encouraging
2. Explain the 'why' behind suggestions with clear technical reasoning
3. Provide concrete, improved code examples
4. Use inclusive language that builds confidence
5. Focus on learning opportunities rather than mistakes"""

        severity_adjustments = {
            "harsh": " Pay special attention to softening harsh language and being extra encouraging. The original feedback may have been blunt or discouraging, so focus on building the developer's confidence while still conveying the technical improvement needed.",
            "moderate": " Maintain a balanced, professional tone while being supportive and educational.",
            "neutral": " The original feedback was already fairly neutral, so focus on making it more educational and adding the 'why' behind suggestions."
        }
        
        return base_prompt + severity_adjustments.get(severity, "")

    def _generate_empathetic_review(self, code_snippet: str, comments: List[str]) -> str:
        """Generate empathetic review using OpenAI with sophisticated prompting"""
        
        # Assess overall severity
        severities = [self._assess_comment_severity(comment) for comment in comments]
        overall_severity = max(severities, key=severities.count)
        
        system_prompt = self._create_system_prompt(overall_severity)
        
        user_prompt = f"""Please transform the following code review comments into empathetic, educational feedback. For each comment, provide:

1. **Positive Rephrasing**: A gentle, encouraging version that maintains the technical point
2. **The 'Why'**: Clear explanation of the underlying software principle (performance, readability, maintainability, etc.)
3. **Suggested Improvement**: Concrete code example demonstrating the fix

Code Snippet:
```python
{code_snippet}
```

Original Comments:
{json.dumps(comments, indent=2)}

Format your response as markdown with a section for each comment using this structure:

---
### Analysis of Comment: "[original comment]"

**Positive Rephrasing:** [encouraging version]

**The 'Why':** [technical explanation]

**Suggested Improvement:**
```python
[improved code]
```

[If applicable, add relevant resources or additional context]

---

After addressing all comments, add a "Summary" section with an encouraging overall assessment of the code and the developer's progress."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating review: {str(e)}")

    def _enhance_with_resources(self, review_content: str, code_snippet: str, comments: List[str]) -> str:
        """Enhance the review with relevant resource links"""
        
        all_resources = []
        for comment in comments:
            resources = self._get_relevant_resources(comment, code_snippet)
            all_resources.extend(resources)
        
        # Remove duplicates while preserving order
        unique_resources = list(dict.fromkeys(all_resources))
        
        if unique_resources:
            resource_section = "\n\n## Additional Resources\n\nFor further learning, consider reviewing these resources:\n\n"
            for resource in unique_resources:
                resource_section += f"- {resource}\n"
            
            review_content += resource_section
        
        return review_content

    def generate_review_report(self, input_data: Dict) -> str:
        """Generate a complete empathetic review report"""
        
        try:
            # Validate input
            if "code_snippet" not in input_data or "review_comments" not in input_data:
                raise ValueError("Input must contain 'code_snippet' and 'review_comments' keys")
            
            code_snippet = input_data["code_snippet"]
            comments = input_data["review_comments"]
            
            if not isinstance(comments, list) or not comments:
                raise ValueError("'review_comments' must be a non-empty list")
            
            # Generate empathetic review
            review_content = self._generate_empathetic_review(code_snippet, comments)
            
            # Enhance with resources
            enhanced_review = self._enhance_with_resources(review_content, code_snippet, comments)
            
            # Add header
            final_report = f"# 📝 Empathetic Code Review Report\n\n{enhanced_review}"
            
            return final_report
            
        except Exception as e:
            raise Exception(f"Failed to generate review report: {str(e)}")


def parse_json_input(json_string: str) -> Dict:
    """Parse and validate JSON input"""
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")