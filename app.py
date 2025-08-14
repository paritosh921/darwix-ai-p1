import streamlit as st
import json
import os
from code_reviewer import EmpathticCodeReviewer, parse_json_input


def load_example_data():
    """Load the example data from the hackathon problem statement"""
    return {
        "code_snippet": """def get_active_users(users):
    results = []
    for u in users:
        if u.is_active == True and u.profile_complete == True:
            results.append(u)
    return results""",
        "review_comments": [
            "This is inefficient. Don't loop twice conceptually.",
            "Variable 'u' is a bad name.",
            "Boolean comparison '== True' is redundant."
        ]
    }


def main():
    st.set_page_config(
        page_title="Empathetic Code Reviewer",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("📝 Empathetic Code Reviewer")
    st.markdown("""
    Transform critical code review feedback into constructive, educational guidance.  
    *Making code reviews more empathetic and educational for better team collaboration.*
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key. It will be used securely and not stored."
        )
        
        st.markdown("---")
        
        # Example data option
        if st.button("📋 Load Example Data", use_container_width=True):
            st.session_state['example_loaded'] = True
        
        st.markdown("---")
        
        # Instructions
        st.markdown("""
        ### 📖 How to Use:
        1. Enter your OpenAI API key above
        2. Paste JSON input with:
           - `code_snippet`: The code to review
           - `review_comments`: List of critical comments
        3. Click "Generate Review" to transform feedback
        4. Get empathetic, educational analysis!
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📥 Input")
        
        # Load example if requested
        if st.session_state.get('example_loaded', False):
            example_data = load_example_data()
            default_json = json.dumps(example_data, indent=2)
            st.session_state['example_loaded'] = False
        else:
            default_json = """{
  "code_snippet": "your code here",
  "review_comments": [
    "first critical comment",
    "second critical comment"
  ]
}"""
        
        # JSON input
        json_input = st.text_area(
            "JSON Input",
            value=default_json,
            height=400,
            help="Enter JSON with 'code_snippet' and 'review_comments' keys"
        )
        
        # Validate JSON in real-time
        try:
            if json_input.strip():
                parsed_data = parse_json_input(json_input)
                st.success("✅ Valid JSON format")
                
                # Show preview
                with st.expander("🔍 Preview Parsed Data"):
                    st.code(parsed_data.get('code_snippet', ''), language='python')
                    st.write("**Comments:**")
                    for i, comment in enumerate(parsed_data.get('review_comments', []), 1):
                        st.write(f"{i}. {comment}")
            
        except ValueError as e:
            st.error(f"❌ JSON Error: {str(e)}")
            parsed_data = None
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate Empathetic Review",
            use_container_width=True,
            type="primary",
            disabled=not (api_key and json_input.strip())
        )
    
    with col2:
        st.header("📤 Output")
        
        if generate_button:
            if not api_key:
                st.error("❌ Please enter your OpenAI API key")
                return
            
            try:
                # Validate input
                input_data = parse_json_input(json_input)
                
                # Show progress
                with st.spinner("🤖 AI is transforming your feedback... This may take a few seconds."):
                    # Initialize reviewer
                    reviewer = EmpathticCodeReviewer(api_key)
                    
                    # Generate review
                    review_report = reviewer.generate_review_report(input_data)
                
                # Display result
                st.success("✅ Review generated successfully!")
                st.markdown(review_report)
                
                # Download option
                st.download_button(
                    "📥 Download Report",
                    data=review_report,
                    file_name="empathetic_code_review.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
            except ValueError as e:
                st.error(f"❌ Input Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.write("Please check your API key and try again.")
        
        else:
            # Show placeholder or instructions
            if not api_key:
                st.info("👈 Please enter your OpenAI API key in the sidebar to get started.")
            elif not json_input.strip():
                st.info("👈 Please enter JSON input to generate a review.")
            else:
                st.info("👈 Click 'Generate Empathetic Review' to transform your feedback!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        Made with ❤️ for better code reviews | 
        <a href='#'>View Source Code</a> | 
        <a href='#'>Report Issues</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Initialize session state
    if 'example_loaded' not in st.session_state:
        st.session_state['example_loaded'] = False
    
    main()