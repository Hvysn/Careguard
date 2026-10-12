import os
import streamlit as st
from rag import rag_engine

# ---------------------------------------------------------
# Page Configuration & Styling (White + Light Pink Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="CareGuard Policy & Claims RAG",
    page_icon="🌸",
    layout="wide"
)

# Custom CSS for Light, White & Soft Pink/Rose UI
st.markdown("""
<style>
    /* Background & Global Colors */
    .stApp {
        background-color: #fffafb;
        color: #334155;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Header card */
    .header-box {
        background-color: #ffffff;
        border: 1px solid #ffe4e6;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(244, 63, 94, 0.05);
        margin-bottom: 1.5rem;
    }
    .header-title {
        color: #1e293b;
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0;
    }
    .header-subtitle {
        color: #fb7185;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.2rem;
    }

    /* Content Cards */
    .content-card {
        background: #ffffff;
        border: 1px solid #ffe4e6;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(244, 63, 94, 0.04);
    }
    
    /* Human Review Flag */
    .flag-card {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        color: #9f1239;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    /* Citation badge */
    .citation-badge {
        background: #fff1f2;
        border: 1px solid #ffe4e6;
        padding: 0.75rem;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }

    /* Buttons */
    .stButton > button {
        background-color: #f43f5e !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.25rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #e11d48 !important;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.25) !important;
    }
    
    /* Text input */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        border: 1px solid #fecdd3 !important;
        border-radius: 10px !important;
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# UI Header
# ---------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="background: #ffe4e6; padding: 10px; border-radius: 12px; font-size: 24px;">🌸</div>
        <div>
            <div class="header-title">CareGuard Policy & Claims RAG</div>
            <div class="header-subtitle">AI Healthcare Policy Adjudication & Grounded Evidence Retrieval</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Layout: Left column (Query Input) & Right column (Results)
# ---------------------------------------------------------
col1, col2 = st.columns([5, 7], gap="medium")

sample_prompts = [
    "What documents are required for reimbursement claims?",
    "What is the waiting period for pre-existing diseases and cataract surgery?",
    "Are cosmetic surgeries covered under policy exclusions?",
    "What are the room rent and ICU limit restrictions?"
]

with col1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("##### 🔍 Policy Document Query")
    st.caption("Ask questions about coverage, exclusions, waiting periods, or claim checklists.")
    
    user_query = st.text_area(
        "Enter your policy question:",
        value=st.session_state.get("selected_prompt", "What documents are required for reimbursement claims?"),
        height=110,
        label_visibility="collapsed"
    )
    
    search_clicked = st.button("🌸 Search Policies & SOPs", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Prompts
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("##### 💡 Standard Policy Inquiries")
    for prompt in sample_prompts:
        if st.button(f"👉 {prompt}", key=prompt, use_container_width=True):
            user_query = prompt
            search_clicked = True
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if search_clicked and user_query.strip():
        with st.spinner("Retrieving indexed policy embeddings from ChromaDB..."):
            result = rag_engine.query(user_query)
            
            # 1. Human review banner if flagged
            if result.get("requires_human_review"):
                st.markdown("""
                <div class="flag-card">
                    ⚠️ <b>Human Review Recommended:</b> This inquiry references conditions or exclusions that require verification by an authorized claims analyst.
                </div>
                """, unsafe_allow_html=True)
            
            # 2. Grounded Answer
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("##### 📋 Policy Determination & Checklist")
            st.markdown(result.get("answer", "No answer found."))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 3. Citations
            citations = result.get("citations", [])
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown(f"##### 📄 Verified Policy Citations ({len(citations)})")
            
            for c in citations:
                st.markdown(f"""
                <div class="citation-badge">
                    <b style="color: #9f1239;">📄 {c['source']}</b> &nbsp;•&nbsp; <span style="color: #64748b;">Page {c['page']}</span><br>
                    <i style="color: #475569;">"{c['content_preview']}"</i>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif not search_clicked:
        st.markdown("""
        <div class="content-card" style="text-align: center; padding: 3rem 1rem; color: #94a3b8;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">📖</div>
            <h4 style="color: #475569; margin-bottom: 0.25rem;">Awaiting Inquiry</h4>
            <p style="font-size: 0.85rem;">Submit a question on the left or click a standard prompt to inspect policy citations.</p>
        </div>
        """, unsafe_allow_html=True)
