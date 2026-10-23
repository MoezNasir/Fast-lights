import streamlit as st
from app.main import query_spec
from app.schemas import QueryRequest
from app.products import PRODUCT_CATALOG

st.set_page_config(
    page_title="LumenRAG Enterprise | Lighting Technical Sales Assistant",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Injection
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #111827 0%, #090d16 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Header Card */
    .enterprise-header {
        background: linear-gradient(135deg, rgba(22, 32, 53, 0.85) 0%, rgba(14, 21, 36, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    .header-badge {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: #fbbf24;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        letter-spacing: 0.05em;
    }
    .header-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffffff;
        margin-top: 0.35rem;
    }
    .header-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    
    /* Metric Cards */
    .spec-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .spec-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
    }
    .spec-value {
        font-size: 0.95rem;
        color: #f8fafc;
        font-weight: 700;
        margin-top: 2px;
    }
    
    /* Grounded Pill */
    .grounded-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        font-weight: 600;
        font-size: 0.78rem;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
    }
</style>
""", unsafe_allow_html=True)

# Main Enterprise Header
st.markdown("""
<div class="enterprise-header">
    <span class="header-badge">LUMENRAG ENTERPRISE v1.0</span>
    <div class="header-title">💡 Commercial Lighting Technical RAG Co-Pilot</div>
    <div class="header-desc">AI-powered technical specification assistant strictly grounded in 13 approved architectural & commercial lighting product datasheets. Zero hallucination guarantee.</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Product Catalog Explorer
with st.sidebar:
    st.markdown("### 📚 Approved Product Catalog")
    st.caption("13 Verified Architectural & Commercial Submittals")
    
    selected_prod = st.selectbox(
        "Select Product to Inspect:",
        options=list(PRODUCT_CATALOG.keys()),
        format_func=lambda k: PRODUCT_CATALOG[k]["family"]
    )
    
    if selected_prod:
        meta = PRODUCT_CATALOG[selected_prod]
        st.markdown(f"#### {meta['family']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Category:** {meta['category'].title()}")
            st.markdown(f"**Wattages:** {', '.join(meta.get('power_consumption', []))}")
            st.markdown(f"**CRI:** {meta.get('cri', 'N/A')}")
            st.markdown(f"**IP Code:** {meta.get('ip', 'N/A')}")
        with c2:
            st.markdown(f"**Subcategory:** {meta.get('subcategory', 'Commercial').title()}")
            st.markdown(f"**Beam Angle:** {', '.join(meta.get('beam_angle', []))}")
            st.markdown(f"**CCT:** {', '.join(meta.get('cct', []))}")
            st.markdown(f"**Warranty:** {meta.get('warranty', 'N/A')}")
            
        st.markdown(f"**Input Voltage:** `{meta.get('input_voltage', 'AC220-240V')}`")
        st.markdown(f"**Dimming:** {', '.join(meta.get('dimming', [])) if meta.get('dimming') else 'Non-dimmable'}")
        st.markdown(f"**Datasheet Submittal:** `{meta.get('source_files', [''])[0]}`")

# Sample question quick chips
st.markdown("##### 🔍 Quick Technical Query Presets:")
cols = st.columns(4)
sample_queries = [
    "What is the beam angle of BrightSpace?",
    "Is LaserLux dimmable with DALI or TRIAC?",
    "What is the warranty and lifespan on Eco-Downlight?",
    "What are the cutout dimensions for BrightSpace 10W?",
]

if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""

for i, sq in enumerate(sample_queries):
    if cols[i].button(sq, key=f"chip_{i}", use_container_width=True):
        st.session_state["user_query"] = sq

query_input = st.text_input(
    "Ask any technical sales, dimension, optical or electrical question:",
    value=st.session_state.get("user_query", ""),
    placeholder="e.g. What is the CRI and IP rating of Value Downlight Pro?"
)

if st.button("Submit Inquiry", type="primary") and query_input.strip():
    with st.spinner("Executing FAISS semantic + BM25 lexical hybrid retrieval..."):
        req = QueryRequest(question=query_input.strip())
        response = query_spec(req)

    if response.status == "FOUND":
        conf_int = int(response.confidence * 100)
        st.markdown(f"""
        <div style="margin-top: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between;">
            <div class="grounded-badge">✓ Strict Datasheet Grounding Verified</div>
            <div style="color: #fbbf24; font-weight: 700; font-family: monospace;">Confidence: {conf_int}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(response.natural_response)

        with st.expander("📄 Document Grounding & Verification Metadata"):
            m1, m2, m3 = st.columns(3)
            with m1:
                st.write(f"**Product Identified:** `{response.product}`")
            with m2:
                st.write(f"**Specification Category:** `{response.specification}`")
            with m3:
                if response.source:
                    st.write(f"**Source Document:** `{response.source.document}` (Pg {response.source.page})")
            
            st.markdown("**Retrieved Datasheet Evidence Chunk:**")
            st.code(response.evidence, language="markdown")
    else:
        st.warning(response.message or "Specification details not found in the approved documentation.")
