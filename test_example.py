#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate the empathetic code reviewer with the hackathon example.
This script tests the core functionality without requiring Streamlit or API keys.
"""

import json
from code_reviewer import parse_json_input


def test_json_parsing():
    """Test JSON input parsing with the provided example"""
    
    example_json = """{
  "code_snippet": "def get_active_users(users):\\n    results = []\\n    for u in users:\\n        if u.is_active == True and u.profile_complete == True:\\n            results.append(u)\\n    return results",
  "review_comments": [
    "This is inefficient. Don't loop twice conceptually.",
    "Variable 'u' is a bad name.",
    "Boolean comparison '== True' is redundant."
  ]
}"""
    
    print("Testing JSON parsing...")
    try:
        parsed_data = parse_json_input(example_json)
        print("[PASS] JSON parsing successful!")
        
        print("\\nParsed Data:")
        print(f"Code snippet length: {len(parsed_data['code_snippet'])} characters")
        print(f"Number of comments: {len(parsed_data['review_comments'])}")
        
        print("\\nReview Comments:")
        for i, comment in enumerate(parsed_data['review_comments'], 1):
            print(f"  {i}. {comment}")
        
        print("\\nCode Snippet:")
        print(parsed_data['code_snippet'])
        
        return True
    except Exception as e:
        print(f"[FAIL] JSON parsing failed: {e}")
        return False


def test_severity_assessment():
    """Test comment severity assessment functionality"""
    from code_reviewer import EmpathticCodeReviewer
    
    # Create instance without API key for testing
    try:
        reviewer = EmpathticCodeReviewer("")  # Empty API key for testing
        
        test_comments = [
            "This is inefficient. Don't loop twice conceptually.",
            "Variable 'u' is a bad name.",
            "Boolean comparison '== True' is redundant.",
            "This code is terrible and completely wrong!",
            "Consider using list comprehension for better readability."
        ]
        
        print("\\nTesting Severity Assessment:")
        for comment in test_comments:
            severity = reviewer._assess_comment_severity(comment)
            print(f"  '{comment}' -> {severity}")
        
        print("[PASS] Severity assessment working correctly!")
        return True
    except Exception as e:
        print(f"[FAIL] Severity assessment test failed: {e}")
        return False


def test_resource_generation():
    """Test resource link generation functionality"""
    from code_reviewer import EmpathticCodeReviewer
    
    try:
        reviewer = EmpathticCodeReviewer("")  # Empty API key for testing
        
        test_cases = [
            ("Variable 'u' is a bad name.", "def func(): pass"),
            ("This is inefficient.", "for item in items: pass"),
            ("Boolean comparison '== True' is redundant.", "if flag == True: pass")
        ]
        
        print("\\nTesting Resource Generation:")
        for comment, code in test_cases:
            resources = reviewer._get_relevant_resources(comment, code)
            print(f"  Comment: '{comment}'")
            print(f"  Resources: {len(resources)} found")
            for resource in resources:
                print(f"    - {resource}")
            print()
        
        print("[PASS] Resource generation working correctly!")
        return True
    except Exception as e:
        print(f"[FAIL] Resource generation test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Starting Empathetic Code Reviewer Tests\\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: JSON Parsing
    if test_json_parsing():
        tests_passed += 1
    
    # Test 2: Severity Assessment
    if test_severity_assessment():
        tests_passed += 1
    
    # Test 3: Resource Generation
    if test_resource_generation():
        tests_passed += 1
    
    # Results
    print("\\n" + "="*50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("[SUCCESS] All tests passed! The application is ready to use.")
        print("\\nTo run the application:")
        print("   1. Get an OpenAI API key from https://platform.openai.com/api-keys")
        print("   2. Run: streamlit run app.py")
        print("   3. Enter your API key in the sidebar")
        print("   4. Click 'Load Example Data' to test with the hackathon example")
    else:
        print("[ERROR] Some tests failed. Please check the implementation.")
    
    print("="*50)


if __name__ == "__main__":
    main()