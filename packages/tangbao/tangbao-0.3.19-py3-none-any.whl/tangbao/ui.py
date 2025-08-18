def _import_streamlit():
    """Lazily import streamlit only when needed."""
    try:
        import streamlit as st
        return st
    except ImportError:
        raise ImportError(
            "Streamlit is required for UI components. "
            "Please install it with 'pip install streamlit'"
        )

def render_prototype_banner():
    """Display prototype disclaimer in Streamlit UI."""
    st = _import_streamlit()
    st.info(
        "🚧 **Prototype Notice**: This application is for exploratory and research purposes only."
    )

# Usage Guidelines Template
# These guidelines should be customized based on your specific application
def get_usage_guidelines(main_purpose, business_process):
    return {
        "title": "⚠️ Important Usage Guidelines",
        "content": f"""
        ### Intended Use and Limitations
        1. This tool is designed to **{main_purpose}**

        2. It serves as a support tool and should not be used as the sole basis for **{business_process}**

        3. The AI components are meant to enhance, not replace, human expert judgment. All outputs should be validated by qualified professionals in accordance with GxP guidelines and regulatory requirements.
        """
    }

def render_guidance_modal(USAGE_GUIDELINES):
    """Render the guidance modal that appears on app startup."""
    st = _import_streamlit()
    if "guidance_accepted" not in st.session_state:
        st.session_state.guidance_accepted = False

    if not st.session_state.guidance_accepted:
        dialog = st.container()
        with dialog:
            st.markdown(f"## {USAGE_GUIDELINES['title']}")
            st.markdown(USAGE_GUIDELINES['content'])
            if st.button("I Understand and Accept"):
                st.session_state.guidance_accepted = True
                st.rerun()
        st.markdown("---")
    
    if "guidance_accepted" not in st.session_state or not st.session_state.guidance_accepted:
        st.error("⚠️ Please accept the usage guidelines above to proceed.")
        return False
    
    return True

def render_guidance_dropdown(USAGE_GUIDELINES):
    """Render the guidance dropdown in the sidebar."""
    st = _import_streamlit()
    with st.expander(USAGE_GUIDELINES['title'], expanded=False):
        st.markdown(USAGE_GUIDELINES['content'])
