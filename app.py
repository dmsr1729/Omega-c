import streamlit as st
import os
import json
import re
from collections import Counter
import streamlit.components.v1 as components
from modules.document_manager import (
    save_uploaded_document,
    update_document_status,
    get_all_documents,
    get_document,
    delete_document
)
from modules.llm import extract_concept_relationships
from modules.embeddings import generate_query_embedding
from modules.llm import generate_answer
from modules.document_processor import process_document
from modules.vector_store import create_vector_store, save_vector_store, load_vector_store
# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Omega-C | AI Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION STATE
# ==========================================
if "document_processed" not in st.session_state:
    st.session_state.document_processed = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "document_store" not in st.session_state:
    st.session_state.document_store = None
if "document_name" not in st.session_state:
    st.session_state.document_name = None
if "active_document_id" not in st.session_state:
    st.session_state.active_document_id = None
if "ai_relationships" not in st.session_state:
    st.session_state.ai_relationships = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* GLOBAL */

.stApp {
    background: #050B14;
    color: #E5F3FF;
    overflow-x: hidden;
}

/* ANIMATED BACKGROUND */

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;

    background:
        radial-gradient(
            circle at 20% 30%,
            rgba(0, 180, 220, 0.13),
            transparent 35%
        ),
        radial-gradient(
            circle at 80% 70%,
            rgba(20, 90, 180, 0.13),
            transparent 35%
        );

    animation: ambientMove 12s ease-in-out infinite alternate;
}

/* DIGITAL GRID */

.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;

    background-image:
        linear-gradient(
            rgba(70, 180, 210, 0.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(70, 180, 210, 0.035) 1px,
            transparent 1px
        );

    background-size: 45px 45px;
}

/* CONTENT LAYER */

[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stSidebar"] {
    position: relative;
    z-index: 1;
}

/* ANIMATIONS */

@keyframes ambientMove {
    from {
        background-position: 0% 0%, 100% 100%;
    }

    to {
        background-position: 100% 100%, 0% 0%;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes softPulse {
    0%, 100% {
        opacity: 0.65;
    }

    50% {
        opacity: 1;
    }
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: rgba(8, 19, 33, 0.96);
    border-right: 1px solid #153047;
}

.sidebar-brand {
    font-size: 28px;
    font-weight: 800;
    color: #54D6E8;
    letter-spacing: 2px;
}

.sidebar-caption {
    color: #8299AD;
    font-size: 10px;
    letter-spacing: 2px;
}

/* HEADINGS */

.main-title {
    font-size: 36px;
    font-weight: 700;
    color: #E5F3FF;
    letter-spacing: 1px;
    animation: fadeIn 0.8s ease;
}

.subtitle {
    color: #8299AD;
    font-size: 14px;
    animation: fadeIn 1s ease;
}

/* PANELS */

.panel {
    background: linear-gradient(
        145deg,
        rgba(13, 27, 42, 0.92),
        rgba(9, 20, 33, 0.92)
    );

    backdrop-filter: blur(14px);

    border: 1px solid rgba(50, 150, 190, 0.22);
    border-radius: 16px;

    padding: 22px;
    min-height: 220px;

    animation: fadeIn 0.8s ease;

    transition: all 0.3s ease;
}

.panel:hover {
    border-color: rgba(60, 210, 240, 0.55);
    transform: translateY(-3px);
}

.panel-title {
    color: #54D6E8;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 15px;
}

/* GRAPH */

.graph-area {
    height: 350px;

    background: radial-gradient(
        circle at center,
        #102B40,
        #07111D 75%
    );

    border: 1px solid #19415A;
    border-radius: 16px;

    display: flex;
    justify-content: center;
    align-items: center;

    color: #54D6E8;
}

/* METRICS */

.metric {
    background: rgba(12, 27, 41, 0.88);
    border: 1px solid #17354B;

    padding: 20px;
    border-radius: 12px;
    text-align: center;

    transition: all 0.3s ease;
}

.metric:hover {
    border-color: #36CBE5;

    box-shadow:
        0 0 20px rgba(54, 203, 229, 0.13);

    transform: translateY(-4px);
}

.metric-value {
    color: #54D6E8;
    font-size: 27px;
    font-weight: bold;
}

.metric-label {
    color: #8299AD;
    font-size: 12px;
    letter-spacing: 1px;
}

/* BUTTONS */

.stButton > button {
    background: linear-gradient(
        110deg,
        #0D2638,
        #10384B
    );

    color: #DDF8FF;

    border: 1px solid #20516A;
    border-radius: 10px;

    transition: all 0.25s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        110deg,
        #10445A,
        #087F9B
    );

    border-color: #54D6E8;

    box-shadow:
        0 0 12px rgba(84, 214, 232, 0.25),
        0 0 25px rgba(84, 214, 232, 0.12);

    transform: translateY(-2px);
}

.stButton > button:active {
    transform: scale(0.96);
}

/* ACTIVE NAVIGATION */

div[data-testid="stSidebar"] .stButton > button {
    text-align: left;
    min-height: 42px;
}

/* STATUS */

.status {
    color: #43D9A3;
    font-size: 13px;
    animation: softPulse 2s infinite;
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea {
    background: #0D1B2A;
    color: #E5F3FF;
    border: 1px solid #20516A;
    border-radius: 10px;
}

/* UPLOAD */

[data-testid="stFileUploader"] {
    background: rgba(13, 27, 42, 0.7);
    border: 1px dashed #20516A;
    border-radius: 12px;
    padding: 10px;
}

/* REDUCED MOTION */

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">🧠 OMEGA-C</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-caption">AI KNOWLEDGE INTELLIGENCE</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Navigation")
    if st.button("🏠  Dashboard", key="nav_dashboard", use_container_width=True):
     st.session_state.page = "Dashboard"

    if st.button("📚  My Documents", key="nav_documents", use_container_width=True):
        st.session_state.page = "My Documents"

    if st.button("💬  Chat Assistant", key="nav_chat", use_container_width=True):
        st.session_state.page = "Chat Assistant"

    if st.button("🕸️  Knowledge Graph", key="nav_graph", use_container_width=True):
        st.session_state.page = "Knowledge Graph"

    if st.button("✨  Intelligent Insights", key="nav_insights", use_container_width=True):
        st.session_state.page = "Intelligent Insights"
    st.divider()

    st.markdown("### Document Upload")

    uploaded_files = st.file_uploader(
        "Upload PDF Documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or multiple PDF documents.",
        key="pdf_uploader"
    )

    st.session_state.uploaded_files = uploaded_files or []

    if uploaded_files:
        st.success(f"{len(uploaded_files)} PDF(s) selected.")

    st.divider()

    st.markdown(
        '<p class="status">● System Interface Online</p>',
        unsafe_allow_html=True
    )

    st.caption("Omega-C v1.0")

# ==========================================
# KNOWLEDGE GRAPH GENERATOR
# ==========================================

def build_knowledge_graph(chunks):

    stopwords = {
        "this", "that", "with", "from", "have", "will",
        "your", "about", "there", "their", "which",
        "when", "where", "what", "were", "been",
        "being", "also", "into", "than", "then",
        "them", "they", "these", "those", "such",
        "some", "more", "most", "only", "each",
        "while", "because", "between", "through",
        "using", "used", "very", "other", "would",
        "could", "should", "after", "before", "under"
    }

    # Step 1: Extract words from document chunks
    word_count = Counter()

    for chunk in chunks:

        words = re.findall(r'\b[a-zA-Z]{4,}\b', chunk.lower())

        for word in words:

            if word not in stopwords:
                word_count[word] += 1

    # Step 2: Select the 12 most common concepts
    concepts = [
        word for word, count in word_count.most_common(12)
    ]

    # Step 3: Find concepts appearing together
    co_occurrence = Counter()

    for chunk in chunks:

        words = set(
            re.findall(r'\b[a-zA-Z]{4,}\b', chunk.lower())
        )

        present = sorted(set(concepts) & words)

        for i in range(len(present)):

            for j in range(i + 1, len(present)):

                pair = (present[i], present[j])

                co_occurrence[pair] += 1

    # Step 4: Keep the 20 strongest connections
    edges = sorted(
        co_occurrence.items(),
        key=lambda item: item[1],
        reverse=True
    )[:20]

    return concepts, edges


def render_knowledge_graph(concepts, edges, relationships):

    import json

    nodes = [
        {
            "id": 0,
            "label": "DOCUMENT",
            "center": True
        }
    ]

    for index, concept in enumerate(concepts):

        nodes.append({
            "id": index + 1,
            "label": str(concept).upper(),
            "center": False
        })

    links = []

    # Document connections
    for index in range(len(concepts)):

        links.append({
            "source": 0,
            "target": index + 1,
            "type": "document",
            "label": "Contains document concept"
        })

    concept_ids = {
        str(concept).lower(): index + 1
        for index, concept in enumerate(concepts)
    }

    # Co-occurrence connections
    for pair, weight in edges:

        source_name = str(pair[0]).lower()
        target_name = str(pair[1]).lower()

        if source_name not in concept_ids:
            continue

        if target_name not in concept_ids:
            continue

        links.append({
            "source": concept_ids[source_name],
            "target": concept_ids[target_name],
            "type": "cooccurrence",
            "label": "Frequently appears together"
        })

    # AI semantic relationships
    for relation in relationships:

        source_name = relation["source"].lower()
        target_name = relation["target"].lower()

        if source_name not in concept_ids:
            continue

        if target_name not in concept_ids:
            continue

        links.append({
            "source": concept_ids[source_name],
            "target": concept_ids[target_name],
            "type": "semantic",
            "label": relation["relationship"]
        })

    nodes_json = json.dumps(nodes).replace("<", "\\u003c")
    links_json = json.dumps(links).replace("<", "\\u003c")

    html = """
    <!DOCTYPE html>
    <html>

    <head>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: transparent;
            font-family: Arial, sans-serif;
            color: #E5F7FF;
        }

        .graph-container {
            position: relative;
            width: 100%;
            height: 620px;
            display: flex;
            flex-direction: column;
            background:
                radial-gradient(
                    circle at center,
                    rgba(0, 180, 255, 0.09),
                    transparent 65%
                ),
                #071522;

            border: 1px solid rgba(0, 210, 255, 0.25);
            border-radius: 18px;
            overflow: hidden;
        }

        .graph-header {
            display: flex;
            justify-content: space-between;
            padding: 17px 22px;
            align-items: center;
            border-bottom: 1px solid rgba(0, 200, 255, 0.15);
        }

        .graph-title {
            font-size: 16px;
            font-weight: bold;
            color: #4DEBFF;
        }

        .graph-subtitle {
            font-size: 11px;
            color: #7895AA;
            margin-top: 5px;
        }

        .graph-status {
            font-size: 11px;
            color: #42F5B3;
        }

        .graph-main {
            display: flex;
            flex: 1;
            min-height: 0;
        }

        .canvas-area {
            position: relative;
            flex: 1;
            min-width: 0;
        }

        canvas {
            width: 100%;
            height: 100%;
            display: block;
            cursor: pointer;
        }

        .details-panel {
            width: 255px;
            padding: 22px;
            background: rgba(9, 29, 45, 0.88);
            border-left: 1px solid rgba(0, 200, 255, 0.17);
            overflow-y: auto;
        }

        .details-heading {
            color: #4DEBFF;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .node-icon {
            width: 55px;
            height: 55px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 25px;
            background: rgba(0, 210, 255, 0.12);
            border: 1px solid rgba(0, 210, 255, 0.4);
            margin-bottom: 16px;
            box-shadow: 0 0 25px rgba(0, 210, 255, 0.12);
        }

        .node-name {
            font-size: 16px;
            font-weight: bold;
            color: white;
            word-break: break-word;
            margin-bottom: 10px;
        }

        .node-description {
            font-size: 12px;
            color: #91AABD;
            line-height: 1.7;
        }

        .connection-title {
            color: #4DEBFF;
            font-size: 12px;
            margin-top: 25px;
            margin-bottom: 12px;
        }

        .connection-item {
            font-size: 11px;
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(0, 180, 255, 0.07);
            border: 1px solid rgba(0, 200, 255, 0.13);
            border-radius: 8px;
            color: #C8E9F5;
            line-height: 1.5;
        }

        .hint {
            font-size: 11px;
            color: #66879B;
            line-height: 1.7;
        }

        .legend {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            padding: 12px 20px;
            border-top: 1px solid rgba(0, 200, 255, 0.12);
            font-size: 10px;
            color: #8AA9BC;
        }

        .legend span {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }

        @media(max-width: 650px) {

            .details-panel {
                width: 180px;
                padding: 12px;
            }

            .graph-header {
                padding: 12px;
            }
        }

    </style>

    </head>

    <body>

    <div class="graph-container">

        <div class="graph-header">

            <div>
                <div class="graph-title">
                    ✦ Neural Knowledge Network
                </div>

                <div class="graph-subtitle">
                    Explore connections between discovered concepts
                </div>
            </div>

            <div class="graph-status">
                ● NETWORK ACTIVE
            </div>

        </div>

        <div class="graph-main">

            <div class="canvas-area">
                <canvas id="graph"></canvas>
            </div>

            <div class="details-panel">

                <div class="details-heading">
                    ◈ CONCEPT EXPLORER
                </div>

                <div id="details">

                    <div class="node-icon">✦</div>

                    <div class="node-name">
                        Explore your knowledge
                    </div>

                    <div class="hint">
                        Select any glowing node in the network
                        to discover its relationships and
                        connected concepts.
                    </div>

                </div>

            </div>

        </div>

        <div class="legend">

            <span>
                <i class="dot" style="background:#00E5FF"></i>
                Document
            </span>

            <span>
                <i class="dot" style="background:#9B7BFF"></i>
                Concepts
            </span>

            <span>
                <i class="dot" style="background:#42F5B3"></i>
                AI Relationships
            </span>

            <span>
                <i class="dot" style="background:#FFB86B"></i>
                Related Concepts
            </span>

        </div>

    </div>

    <script>

        const canvas = document.getElementById("graph");
        const ctx = canvas.getContext("2d");

        const nodes = __NODES__;
        const links = __LINKS__;

        const details = document.getElementById("details");

        let width = 0;
        let height = 0;

        let selectedNode = null;
        let hoveredNode = null;

        let particles = [];

        const colors = [
            "#00D9FF",
            "#9B7BFF",
            "#42F5B3",
            "#FFB86B",
            "#5C9DFF"
        ];

        // Initialize particles
        for (let i = 0; i < 35; i++) {

            particles.push({
                x: Math.random(),
                y: Math.random(),
                speed: 0.0002 + Math.random() * 0.0005,
                size: Math.random() * 2
            });

        }

        // Resize graph
        function resize() {

            const rect = canvas.getBoundingClientRect();

            width = rect.width;
            height = rect.height;

            const dpr = window.devicePixelRatio || 1;

            canvas.width = width * dpr;
            canvas.height = height * dpr;

            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

            const cx = width / 2;
            const cy = height / 2;

            const radius = Math.min(width * 0.34, height * 0.37, 190);

            nodes[0].x = cx;
            nodes[0].y = cy;

            const concepts = nodes.filter(n => !n.center);

            concepts.forEach((node, index) => {

                const angle =
                    (Math.PI * 2 * index / concepts.length)
                    - Math.PI / 2;

                const distance = radius * (
                    0.75 + Math.random() * 0.25
                );

                node.x = cx + Math.cos(angle) * distance;
                node.y = cy + Math.sin(angle) * distance;

                node.baseX = node.x;
                node.baseY = node.y;

                node.color = colors[index % colors.length];

            });

        }

        // Find connected relationships
        function getConnections(nodeId) {

            return links.filter(link =>
                link.source === nodeId ||
                link.target === nodeId
            );

        }

        // Update information panel
        function showDetails(node) {

            if (!node) {

                details.innerHTML = `
                    <div class="node-icon">✦</div>
                    <div class="node-name">Explore your knowledge</div>
                    <div class="hint">
                        Select any glowing node to explore
                        its connections.
                    </div>
                `;

                return;
            }

            const connections = getConnections(node.id);

            const connectedIds = new Set();

            connections.forEach(link => {

                connectedIds.add(
                    link.source === node.id
                        ? link.target
                        : link.source
                );

            });

            let connectionHTML = "";

            connections.forEach(link => {

                const otherId =
                    link.source === node.id
                        ? link.target
                        : link.source;

                const otherNode = nodes.find(
                    n => n.id === otherId
                );

                if (!otherNode || otherNode.center) return;

                connectionHTML += `
                    <div class="connection-item">
                        <strong>${otherNode.label}</strong>
                        <br>
                        ${link.label || "Related concept"}
                    </div>
                `;

            });

            details.innerHTML = `

                <div class="node-icon">◈</div>

                <div class="node-name">
                    ${node.label}
                </div>

                <div class="node-description">
                    This concept is part of your document's
                    knowledge network.
                </div>

                <div class="connection-title">
                    CONNECTED CONCEPTS (${connectedIds.size})
                </div>

                ${connectionHTML || `
                    <div class="hint">
                        No direct connections discovered.
                    </div>
                `}

            `;

        }

        // Draw floating particles
        function drawParticles() {

            particles.forEach(p => {

                p.y -= p.speed;

                if (p.y < 0) {
                    p.y = 1;
                    p.x = Math.random();
                }

                ctx.beginPath();

                ctx.arc(
                    p.x * width,
                    p.y * height,
                    p.size,
                    0,
                    Math.PI * 2
                );

                ctx.fillStyle = "rgba(0,210,255,0.35)";
                ctx.fill();

            });

        }

        // Draw connections
        function drawLinks(time) {

            links.forEach(link => {

                const source = nodes.find(
                    n => n.id === link.source
                );

                const target = nodes.find(
                    n => n.id === link.target
                );

                if (!source || !target) return;

                const active =
                    selectedNode === source.id ||
                    selectedNode === target.id ||
                    hoveredNode === source.id ||
                    hoveredNode === target.id;

                let color = "rgba(65,120,160,0.17)";

                if (link.type === "semantic") {
                    color = active
                        ? "#42F5B3"
                        : "rgba(66,245,179,0.55)";
                }

                if (link.type === "cooccurrence") {
                    color = active
                        ? "#FFB86B"
                        : "rgba(255,184,107,0.22)";
                }

                if (link.type === "document") {
                    color = active
                        ? "#00E5FF"
                        : "rgba(0,210,255,0.12)";
                }

                ctx.beginPath();

                ctx.moveTo(source.x, source.y);
                ctx.lineTo(target.x, target.y);

                ctx.strokeStyle = color;
                ctx.lineWidth = active ? 2.5 : 1;

                ctx.shadowBlur = active ? 12 : 0;
                ctx.shadowColor = color;

                ctx.stroke();

                ctx.shadowBlur = 0;

                // Animated particles on semantic links
                if (link.type === "semantic") {

                    const progress = (time * 0.00025) % 1;

                    const px = source.x +
                        (target.x - source.x) * progress;

                    const py = source.y +
                        (target.y - source.y) * progress;

                    ctx.beginPath();

                    ctx.arc(px, py, 2.5, 0, Math.PI * 2);

                    ctx.fillStyle = "#42F5B3";
                    ctx.shadowBlur = 12;
                    ctx.shadowColor = "#42F5B3";

                    ctx.fill();

                    ctx.shadowBlur = 0;

                }

            });

        }

        // Draw concept nodes
        function drawNodes(time) {

            nodes.forEach((node, index) => {

                const active =
                    selectedNode === node.id ||
                    hoveredNode === node.id;

                const connected = selectedNode !== null &&
                    getConnections(selectedNode).some(
                        link =>
                            link.source === node.id ||
                            link.target === node.id
                    );

                const pulse = Math.sin(time * 0.002 + index) * 2;

                const radius = node.center
                    ? 25
                    : 12 + pulse * 0.3;

                const color = node.center
                    ? "#00E5FF"
                    : node.color;

                ctx.beginPath();

                ctx.arc(
                    node.x,
                    node.y,
                    radius + (active ? 5 : 0),
                    0,
                    Math.PI * 2
                );

                ctx.fillStyle = node.center
                    ? "rgba(0,180,255,0.20)"
                    : color + "25";

                ctx.shadowBlur = active ? 35 : 20;
                ctx.shadowColor = color;

                ctx.fill();

                ctx.shadowBlur = 0;

                ctx.strokeStyle = active
                    ? "#FFFFFF"
                    : color;

                ctx.lineWidth = active ? 2.5 : 1.5;

                ctx.stroke();

                // Center glow
                ctx.beginPath();

                ctx.arc(
                    node.x,
                    node.y,
                    node.center ? 5 : 3,
                    0,
                    Math.PI * 2
                );

                ctx.fillStyle = color;
                ctx.fill();

                // Labels
                ctx.font = active
                    ? "bold 11px Arial"
                    : "10px Arial";

                ctx.textAlign = "center";

                ctx.fillStyle = active || connected
                    ? "#FFFFFF"
                    : "#9CB8CC";

                ctx.fillText(
                    node.label.length > 19
                        ? node.label.substring(0, 17) + "..."
                        : node.label,
                    node.x,
                    node.y + radius + 17
                );

            });

        }

        // Animation loop
        function animate(time) {

            ctx.clearRect(0, 0, width, height);

            drawParticles();
            drawLinks(time);
            drawNodes(time);

            requestAnimationFrame(animate);

        }

        // Mouse interaction
        function getNodeAt(x, y) {

            for (let i = nodes.length - 1; i >= 0; i--) {

                const node = nodes[i];

                const dx = x - node.x;
                const dy = y - node.y;

                if (Math.sqrt(dx * dx + dy * dy) < 25) {
                    return node;
                }

            }

            return null;

        }

        canvas.addEventListener("mousemove", function(event) {

            const rect = canvas.getBoundingClientRect();

            hoveredNode = getNodeAt(
                event.clientX - rect.left,
                event.clientY - rect.top
            );

            canvas.style.cursor = hoveredNode
                ? "pointer"
                : "default";

        });

        canvas.addEventListener("click", function(event) {

            const rect = canvas.getBoundingClientRect();

            const node = getNodeAt(
                event.clientX - rect.left,
                event.clientY - rect.top
            );

            if (node) {

                selectedNode = node.id;

                showDetails(node);

            } else {

                selectedNode = null;

                showDetails(null);

            }

        });

        window.addEventListener("resize", resize);

        resize();

        requestAnimationFrame(animate);

    </script>

    </body>
    </html>
    """

    html = html.replace("__NODES__", nodes_json)
    html = html.replace("__LINKS__", links_json)

    components.html(
        html,
        height=640,
        scrolling=False
    )
# ==========================================
# PAGE HEADER HELPER
# ==========================================

def page_header(title, description):

    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="subtitle">{description}</div>',
        unsafe_allow_html=True
    )

    st.write("")


# ==========================================
# DASHBOARD
# ==========================================

if st.session_state.page == "Dashboard":

    page_header(
        "Knowledge Intelligence",
        "Explore documents, discover connections and interact with your knowledge."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric">
            <div class="metric-value">00</div>
            <div class="metric-label">DOCUMENTS</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric">
            <div class="metric-value">00</div>
            <div class="metric-label">KNOWLEDGE NODES</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric">
            <div class="metric-value">ONLINE</div>
            <div class="metric-label">SYSTEM STATUS</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    left, right = st.columns([2.2, 1])

    with left:

        st.markdown(
            '<div class="panel-title">🕸️ Knowledge Graph</div>',
            unsafe_allow_html=True
        )

        if st.session_state.document_processed and st.session_state.document_store:

            dashboard_store = st.session_state.document_store

            dashboard_chunks = [
                chunk["text"] if isinstance(chunk, dict) else chunk
                for chunk in dashboard_store.chunks
            ]

            dashboard_concepts, dashboard_edges = build_knowledge_graph(
                dashboard_chunks
            )

            dashboard_relationships = (
                st.session_state.ai_relationships or []
            )

            render_knowledge_graph(
                dashboard_concepts,
                dashboard_edges,
                dashboard_relationships
            )

        else:
            st.markdown("""
            <div class="panel">
                <div class="graph-area">
                    <div style="text-align:center;">
                        <div style="font-size:55px;">✧</div>
                        <h3>Knowledge Visualization</h3>
                        <p style="color:#8299AD;">
                            Process a document to explore its connections.
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:

        if st.session_state.document_processed and st.session_state.document_store:

            insight_store = st.session_state.document_store

            total_chunks = len(insight_store.chunks)

            total_words = sum(
                len(
                    (chunk["text"] if isinstance(chunk, dict) else chunk).split()
                )
                for chunk in insight_store.chunks
            )

            insight_chunks = [
                chunk["text"] if isinstance(chunk, dict) else chunk
                for chunk in insight_store.chunks
            ]

            insight_concepts, _ = build_knowledge_graph(insight_chunks)

            total_concepts = len(insight_concepts)

            intelligence_score = min(
                100,
                total_chunks * 5 + total_concepts * 3
            )

            top_keywords = Counter(
                word
                for chunk in insight_chunks
                for word in re.findall(r'\b[a-zA-Z]{5,}\b', chunk.lower())
                if word not in {
                    "which", "there", "their", "these", "those",
                    "about", "would", "could", "should", "being",
                    "using", "other", "where", "while", "after"
                }
            ).most_common(5)

            keyword_html = ""

            for word, count in top_keywords:

                keyword_html += f"""
                <span style="
                    display:inline-block;
                    padding:7px 11px;
                    margin:4px;
                    border:1px solid rgba(84,214,232,0.25);
                    border-radius:20px;
                    background:rgba(8,127,155,0.13);
                    color:#9CECF5;
                    font-size:11px;
                ">
                    {word.title()} <b>· {count}</b>
                </span>
                """

            insights_html = f"""
            <div style="
                background:linear-gradient(145deg,#0C1B2A,#102D40);
                border:1px solid #20516A;
                border-radius:20px;
                padding:21px;
                min-height:430px;
                font-family:Arial,sans-serif;
                color:#E5F3FF;
                box-shadow:0 10px 35px rgba(0,0,0,0.22);
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">
                    <div style="font-size:16px;font-weight:700;">
                        ✦ Intelligence Insights
                    </div>

                    <div style="
                        color:#43D9A3;
                        font-size:10px;
                        letter-spacing:1px;
                    ">
                        ● ACTIVE
                    </div>
                </div>

                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    padding:24px 0;
                ">
                    <div style="
                        width:135px;
                        height:135px;
                        border-radius:50%;
                        background:conic-gradient(
                            #54D6E8 {intelligence_score}%,
                            #19364A {intelligence_score}% 100%
                        );
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        box-shadow:0 0 28px rgba(84,214,232,0.16);
                    ">
                        <div style="
                            width:113px;
                            height:113px;
                            border-radius:50%;
                            background:#102638;
                            display:flex;
                            flex-direction:column;
                            align-items:center;
                            justify-content:center;
                        ">
                            <div style="
                                color:#54D6E8;
                                font-size:32px;
                                font-weight:800;
                            ">
                                {intelligence_score}%
                            </div>

                            <div style="
                                color:#8299AD;
                                font-size:9px;
                                letter-spacing:1px;
                            ">
                                INTELLIGENCE
                            </div>
                        </div>
                    </div>
                </div>

                <div style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:10px;
                ">

                    <div style="
                        background:rgba(255,255,255,0.035);
                        border:1px solid #1B4055;
                        border-radius:12px;
                        padding:13px;
                    ">
                        <div style="font-size:20px;color:#54D6E8;font-weight:700;">
                            {total_chunks}
                        </div>
                        <div style="font-size:10px;color:#8299AD;">
                            TEXT CHUNKS
                        </div>
                    </div>

                    <div style="
                        background:rgba(255,255,255,0.035);
                        border:1px solid #1B4055;
                        border-radius:12px;
                        padding:13px;
                    ">
                        <div style="font-size:20px;color:#54D6E8;font-weight:700;">
                            {total_concepts}
                        </div>
                        <div style="font-size:10px;color:#8299AD;">
                            KEY CONCEPTS
                        </div>
                    </div>

                    <div style="
                        background:rgba(255,255,255,0.035);
                        border:1px solid #1B4055;
                        border-radius:12px;
                        padding:13px;
                    ">
                        <div style="font-size:20px;color:#54D6E8;font-weight:700;">
                            {total_words:,}
                        </div>
                        <div style="font-size:10px;color:#8299AD;">
                            TOTAL WORDS
                        </div>
                    </div>

                    <div style="
                        background:rgba(255,255,255,0.035);
                        border:1px solid #1B4055;
                        border-radius:12px;
                        padding:13px;
                    ">
                        <div style="font-size:20px;color:#43D9A3;font-weight:700;">
                            READY
                        </div>
                        <div style="font-size:10px;color:#8299AD;">
                            DOCUMENT STATUS
                        </div>
                    </div>

                </div>

                <div style="
                    margin-top:23px;
                    margin-bottom:10px;
                    font-size:12px;
                    color:#54D6E8;
                    font-weight:700;
                ">
                    ✧ DISCOVERED KEYWORDS
                </div>

                <div>
                    {keyword_html if keyword_html else '<span style="color:#8299AD;">No keywords found.</span>'}
                </div>

                <div style="
                    margin-top:22px;
                    padding-top:13px;
                    border-top:1px solid #1B4055;
                    display:flex;
                    justify-content:space-between;
                    font-size:10px;
                    color:#8299AD;
                ">
                    <span>OMEGA-C ANALYTICS ENGINE</span>
                    <span style="color:#43D9A3;">● OPERATIONAL</span>
                </div>

            </div>
            """

            components.html(insights_html, height=500, scrolling=False)

        else:

            st.markdown("""
            <div style="
                background:linear-gradient(145deg,#0C1B2A,#102D40);
                border:1px solid #20516A;
                border-radius:20px;
                padding:35px 20px;
                text-align:center;
                min-height:430px;
            ">
                <div style="font-size:55px;color:#54D6E8;">
                    ✧
                </div>

                <h3 style="color:#E5F3FF;">
                    Intelligence Awaits
                </h3>

                <p style="color:#8299AD;font-size:12px;">
                    Upload and process a PDF to unlock
                    your document intelligence dashboard.
                </p>

                <div style="
                    display:inline-block;
                    margin-top:20px;
                    padding:9px 17px;
                    border:1px solid #20516A;
                    border-radius:20px;
                    color:#54D6E8;
                    font-size:11px;
                ">
                    ◉ SYSTEM STANDBY
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# MY DOCUMENTS
# ==========================================

## ==========================================
# MY DOCUMENTS
# ==========================================

# ==========================================
# MY DOCUMENTS
# ==========================================

elif st.session_state.page == "My Documents":

    page_header(
        "My Documents",
        "Upload, store and manage your knowledge sources."
    )

    st.markdown("### 📤 Selected PDFs")

    selected_files = st.session_state.get("uploaded_files", [])

    if selected_files:
        st.info(f"{len(selected_files)} PDF(s) selected.")
        for selected_file in selected_files:
            st.write(f"📄 {selected_file.name}")

        if st.button("💾 Save All Selected PDFs", use_container_width=True):
            try:
                saved_count = 0
                with st.spinner("Saving PDFs to your permanent library..."):
                    for selected_file in selected_files:
                        save_uploaded_document(selected_file)
                        saved_count += 1

                st.success(f"{saved_count} PDF(s) saved to your library.")
                st.rerun()

            except Exception as e:
                st.error(f"Document saving failed: {e}")
    else:
        st.info("Choose one or more PDFs using the sidebar uploader.")

    st.divider()
    st.markdown("### 📚 Your Document Library")

    documents = get_all_documents()

    if not documents:
        st.info("Your document library is empty.")
    else:
        st.caption(f"{len(documents)} document(s) stored on this computer.")

        for document in documents:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"**📄 {document['name']}**")
                    st.caption(
                        f"Uploaded: {document.get('uploaded_at', '')[:10]} "
                        f"· ID: {document['id'][:8]}"
                    )

                with col2:
                    if document.get("status") == "Processed":
                        st.success("✅ Processed")
                    else:
                        st.warning("⏳ Uploaded")

                with col3:
                    if document.get("status") != "Processed":
                        if st.button("Process", key=f"process_{document['id']}"):
                            try:
                                pdf_path = os.path.join(
                                    os.getcwd(), document["pdf_path"]
                                )
                                vector_path = os.path.join(
                                    os.getcwd(), document["vector_store_path"]
                                )

                                with st.spinner(
                                    f"Processing {document['name']}..."
                                ):
                                    chunks, embeddings = process_document(pdf_path)
                                    store = create_vector_store(chunks, embeddings)
                                    save_vector_store(store, vector_path)

                                update_document_status(
                                    document["id"],
                                    len(chunks),
                                    len(embeddings[0]) if embeddings else 0
                                )

                                st.session_state.document_store = store
                                st.session_state.document_name = document["name"]
                                st.session_state.active_document_id = document["id"]
                                st.session_state.document_processed = True
                                st.session_state.ai_relationships = None
                                st.success("Document processed successfully.")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Processing failed: {e}")

                    if st.button("🗑️", key=f"delete_{document['id']}",
                                 help="Delete this document permanently"):
                        st.session_state[f"confirm_delete_{document['id']}"] = True

                if st.session_state.get(f"confirm_delete_{document['id']}", False):
                    st.warning(f"Delete **{document['name']}** and its saved data?")
                    confirm_col, cancel_col = st.columns(2)
                    with confirm_col:
                        if st.button("Confirm delete", key=f"confirm_{document['id']}"):
                            delete_document(document["id"])
                            if st.session_state.active_document_id == document["id"]:
                                st.session_state.document_processed = False
                                st.session_state.document_store = None
                                st.session_state.document_name = None
                                st.session_state.active_document_id = None
                                st.session_state.ai_relationships = None
                            st.session_state[f"confirm_delete_{document['id']}"] = False
                            st.rerun()
                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_{document['id']}"):
                            st.session_state[f"confirm_delete_{document['id']}"] = False
                            st.rerun()

                st.divider()

        processed_docs = [
            doc for doc in documents if doc.get("status") == "Processed"
        ]

        if processed_docs:
            st.markdown("### 🎯 Active Chat Document")
            options = {doc["name"] + " · " + doc["id"][:8]: doc for doc in processed_docs}
            labels = list(options.keys())
            current_index = 0
            for index, label in enumerate(labels):
                if options[label]["id"] == st.session_state.active_document_id:
                    current_index = index
                    break

            selected_label = st.selectbox(
                "Choose which document the Chat Assistant and Knowledge Graph should use:",
                labels,
                index=current_index,
                key="active_doc_selector"
            )
            selected_doc = options[selected_label]

            if selected_doc["id"] != st.session_state.active_document_id:
                try:
                    vector_path = os.path.join(
                        os.getcwd(), selected_doc["vector_store_path"]
                    )
                    st.session_state.document_store = load_vector_store(vector_path)
                    st.session_state.document_name = selected_doc["name"]
                    st.session_state.active_document_id = selected_doc["id"]
                    st.session_state.document_processed = True
                    st.session_state.ai_relationships = None
                    st.session_state.chat_history = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not load this document: {e}")

# ==========================================
# CHAT ASSISTANT
# ==========================================

# ==========================================
# CHAT ASSISTANT
# ==========================================

elif st.session_state.page == "Chat Assistant":

    page_header(
        "AI Chat Assistant",
        "Ask questions and get intelligent answers from your documents."
    )

    if not st.session_state.document_processed:

        st.warning("Please process a PDF document before starting a conversation.")

    else:

        st.markdown("### 🧠 Omega-C Assistant")
        st.caption("Your personal document intelligence assistant.")
        st.divider()

        # Display previous conversation
        for message in st.session_state.chat_history:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        query = st.chat_input("Ask something about your document...")

        if query:

            with st.chat_message("user"):
                st.markdown(query)

            st.session_state.chat_history.append({
                "role": "user",
                "content": query
            })

            with st.chat_message("assistant"):

                with st.spinner("Searching your knowledge..."):

                    try:

                        # Step 1: Generate question embedding
                        query_embedding = generate_query_embedding(query)

                        # Step 2: Retrieve relevant chunks
                        results = st.session_state.document_store.search(
                            query_embedding,
                            top_k=3
                        )

                        # Step 3: Prepare context with page numbers
                        context_parts = []

                        for result in results:

                            page = result.get("page", "Unknown")

                            context_parts.append(
                                f"[Page {page}]\n{result['text']}"
                            )

                        context = "\n\n".join(context_parts)

                        # Step 4: Generate AI answer
                        answer = generate_answer(query, context)

                        st.markdown(answer)

                        # Step 5: Display source citations
                        st.markdown("---")
                        st.markdown("### 📚 Sources")

                        document_name = st.session_state.get(
                            "document_name",
                            "Active Document"
                        )

                        for index, result in enumerate(results, start=1):

                            page = result.get("page", "Page unavailable")

                            snippet = result["text"].strip()

                            if len(snippet) > 250:
                                snippet = snippet[:250] + "..."

                            with st.expander(
                                f"📄 {document_name} — Page {page}"
                            ):

                                st.caption(f"Source {index}")
                                st.write(snippet)

                        # Step 6: Save answer and citations in history
                        response_content = answer + "\n\n---\n\n### 📚 Sources\n"

                        for index, result in enumerate(results, start=1):

                            page = result.get("page", "Page unavailable")

                            response_content += (
                                f"\n- {document_name} — Page {page}"
                            )

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response_content
                        })

                    except Exception as e:

                        st.error(f"Something went wrong: {e}")

        # Clear conversation
        if st.button("🗑️ Clear Conversation"):

            st.session_state.chat_history = []

            st.rerun()
# ==========================================
# INTELLIGENT INSIGHTS
# ==========================================

elif st.session_state.page == "Intelligent Insights":

    page_header(
        "Intelligent Insights",
        "Discover patterns, topics and hidden information inside your documents."
    )

    if not st.session_state.document_processed:

        st.warning("Please process a PDF document first.")

    else:

        store = st.session_state.document_store

        # Extract text from chunks
        chunk_texts = [
            chunk["text"] if isinstance(chunk, dict) else chunk
            for chunk in store.chunks
        ]

        # Collect document statistics
        full_text = " ".join(chunk_texts)

        words = re.findall(r"\b[a-zA-Z]{4,}\b", full_text.lower())

        stopwords = {
            "this", "that", "with", "from", "have", "will",
            "your", "about", "there", "their", "which",
            "when", "where", "what", "were", "been",
            "being", "also", "into", "than", "then",
            "them", "they", "these", "those", "such",
            "some", "more", "most", "only", "each",
            "while", "because", "between", "through",
            "using", "used", "very", "other", "would",
            "could", "should", "after", "before", "under"
        }

        filtered_words = [
            word for word in words if word not in stopwords
        ]

        word_counts = Counter(filtered_words)

        top_topics = word_counts.most_common(6)

        # Page statistics
        page_counts = Counter()

        for chunk in store.chunks:

            if isinstance(chunk, dict):
                page = chunk.get("page")

                if page is not None:
                    page_counts[page] += len(chunk["text"].split())

        total_pages = len(page_counts)
        total_chunks = len(store.chunks)
        total_words = len(full_text.split())
        total_concepts = len(word_counts)

        # ======================================
        # TOP METRIC CARDS
        # ======================================

        st.markdown("### 📊 Document Overview")

        c1, c2, c3, c4 = st.columns(4)

        metrics = [
            (c1, "📄", total_pages, "PAGES ANALYZED"),
            (c2, "🧩", total_chunks, "TEXT CHUNKS"),
            (c3, "✦", total_concepts, "UNIQUE TERMS"),
            (c4, "⌁", f"{total_words:,}", "TOTAL WORDS")
        ]

        for col, icon, value, label in metrics:

            with col:

                st.markdown(
                    f"""
                    <div style="
                        background:linear-gradient(
                            145deg,
                            rgba(15,38,57,0.95),
                            rgba(8,20,35,0.95)
                        );
                        border:1px solid rgba(84,214,232,0.25);
                        border-radius:18px;
                        padding:22px 16px;
                        min-height:145px;
                        box-shadow:0 8px 30px rgba(0,0,0,0.15);
                    ">
                        <div style="font-size:25px;">{icon}</div>
                        <div style="
                            font-size:29px;
                            font-weight:800;
                            color:#54D6E8;
                            margin-top:8px;
                        ">{value}</div>
                        <div style="
                            color:#8299AD;
                            font-size:10px;
                            letter-spacing:1.4px;
                            margin-top:5px;
                        ">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.write("")

        # ======================================
        # TOPIC DISTRIBUTION
        # ======================================

        st.markdown("### 🎯 Topic Distribution")

        left, right = st.columns([1, 1])

        with left:

            st.markdown("""
            <div style="
                background:rgba(12,27,41,0.85);
                border:1px solid #173F55;
                border-radius:18px;
                padding:22px;
            ">
                <div style="color:#54D6E8;font-size:17px;font-weight:700;">
                    Most Discussed Topics
                </div>
                <div style="color:#8299AD;font-size:12px;margin-top:5px;">
                    Distribution based on word frequency
                </div>
            """, unsafe_allow_html=True)

            if top_topics:

                colors = [
                    "#54D6E8",
                    "#8B7CFF",
                    "#43D9A3",
                    "#FFB86B",
                    "#FF729F",
                    "#5C9DFF"
                ]

                total_frequency = sum(
                    count for _, count in top_topics
                )

                gradient_parts = []
                current_position = 0

                for index, (word, count) in enumerate(top_topics):

                    percentage = count / total_frequency * 100
                    next_position = current_position + percentage

                    gradient_parts.append(
                        f"{colors[index]} {current_position:.2f}% "
                        f"{next_position:.2f}%"
                    )

                    current_position = next_position

                gradient = ", ".join(gradient_parts)

                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        justify-content:center;
                        padding:25px;
                    ">
                        <div style="
                            width:210px;
                            height:210px;
                            border-radius:50%;
                            background:conic-gradient({gradient});
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            box-shadow:0 0 35px rgba(84,214,232,0.12);
                        ">
                            <div style="
                                width:135px;
                                height:135px;
                                border-radius:50%;
                                background:#0B1928;
                                display:flex;
                                flex-direction:column;
                                align-items:center;
                                justify-content:center;
                            ">
                                <div style="
                                    color:#54D6E8;
                                    font-size:28px;
                                    font-weight:800;
                                ">{len(top_topics)}</div>
                                <div style="
                                    color:#8299AD;
                                    font-size:10px;
                                ">TOP TOPICS</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                for index, (word, count) in enumerate(top_topics):

                    percentage = count / total_frequency * 100

                    st.markdown(
                        f"""
                        <div style="
                            display:flex;
                            justify-content:space-between;
                            padding:6px 3px;
                            color:#D8EAF5;
                            font-size:12px;
                        ">
                            <span>
                                <span style="color:{colors[index]}">●</span>
                                &nbsp;{word.title()}
                            </span>
                            <span style="color:#8299AD;">
                                {percentage:.1f}%
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("</div>", unsafe_allow_html=True)

        # ======================================
        # KEYWORD ANALYTICS
        # ======================================

        with right:

            keyword_rows = ""

            if top_topics:

                maximum = top_topics[0][1]

                for word, count in top_topics:

                    percentage = count / maximum * 100

                    keyword_rows += f"""
                    <div style="margin-bottom:19px;">

                        <div style="
                            display:flex;
                            justify-content:space-between;
                            color:#D8EAF5;
                            font-size:12px;
                            margin-bottom:7px;
                        ">
                            <span>{word.title()}</span>
                            <span style="color:#54D6E8;">
                                {count} occurrences
                            </span>
                        </div>

                        <div style="
                            height:9px;
                            background:#142C40;
                            border-radius:20px;
                            overflow:hidden;
                        ">
                            <div style="
                                width:{percentage}%;
                                height:100%;
                                background:linear-gradient(
                                    90deg,
                                    #087F9B,
                                    #54D6E8
                                );
                                border-radius:20px;
                                box-shadow:0 0 12px rgba(84,214,232,0.35);
                            "></div>
                        </div>

                    </div>
                    """

            keyword_html = f"""
<div style="
    background:rgba(12,27,41,0.85);
    border:1px solid #173F55;
    border-radius:18px;
    padding:22px;
    min-height:430px;
">
    <div style="color:#54D6E8;font-size:17px;font-weight:700;">
        ✦ Keyword Analytics
    </div>

    <div style="color:#8299AD;font-size:12px;margin-top:5px;">
        Frequently occurring terms in your document
    </div>

    <br>

    {keyword_rows}

</div>
"""

            components.html(keyword_html, height=430, scrolling=False)

        st.write("")

        # ======================================
        # PAGE-WISE CONTENT ANALYSIS
        # ======================================

        st.markdown("### 📈 Page-wise Content Analysis")

        if page_counts:

            max_words = max(page_counts.values())

            st.markdown("""
            <div style="
                background:rgba(12,27,41,0.85);
                border:1px solid #173F55;
                border-radius:18px;
                padding:24px;
            ">
            """, unsafe_allow_html=True)

            for page, count in sorted(page_counts.items()):

                percentage = count / max_words * 100

                st.markdown(
                    f"""
                    <div style="margin-bottom:17px;">

                        <div style="
                            display:flex;
                            justify-content:space-between;
                            color:#D8EAF5;
                            font-size:12px;
                            margin-bottom:7px;
                        ">
                            <span>PAGE {page}</span>
                            <span style="color:#54D6E8;">
                                {count:,} words
                            </span>
                        </div>

                        <div style="
                            height:10px;
                            background:#142C40;
                            border-radius:20px;
                            overflow:hidden;
                        ">
                            <div style="
                                width:{percentage}%;
                                height:100%;
                                background:linear-gradient(
                                    90deg,
                                    #8B7CFF,
                                    #54D6E8
                                );
                                border-radius:20px;
                            "></div>
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

        else:

            st.info(
                "Page-wise statistics are available after processing "
                "a document with page metadata."
            )

        # ======================================
        # DOCUMENT HIGHLIGHTS
        # ======================================

        st.markdown("### 💡 Document Highlights")

        if top_topics:

            highlight_cols = st.columns(3)

            for index, (word, count) in enumerate(top_topics[:3]):

                with highlight_cols[index]:

                    st.markdown(
                        f"""
                        <div style="
                            background:linear-gradient(
                                145deg,
                                rgba(17,42,61,0.95),
                                rgba(9,22,37,0.95)
                            );
                            border:1px solid rgba(84,214,232,0.2);
                            border-radius:16px;
                            padding:20px;
                            min-height:140px;
                        ">
                            <div style="color:#54D6E8;font-size:23px;">
                                ✦
                            </div>
                            <div style="
                                color:#FFFFFF;
                                font-size:18px;
                                font-weight:700;
                                margin-top:10px;
                            ">{word.title()}</div>
                            <div style="
                                color:#8299AD;
                                font-size:12px;
                                margin-top:7px;
                            ">
                                Appears {count} times in the document
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.caption(
            "Insights are calculated locally from the processed document. "
            "Word frequency indicates discussion frequency, not importance."
        )
# ==========================================
# KNOWLEDGE GRAPH
# ==========================================
# ==========================================
# KNOWLEDGE GRAPH
# ==========================================

elif st.session_state.page == "Knowledge Graph":

    page_header(
        "Knowledge Graph",
        "Explore AI-discovered concepts and their relationships."
    )

    if not st.session_state.document_processed:

        st.warning("Please process a PDF document first.")

    else:

        store = st.session_state.document_store

        chunk_texts = [
        chunk["text"] if isinstance(chunk, dict) else chunk
        for chunk in store.chunks
        ]

        concepts, edges = build_knowledge_graph(chunk_texts) 

        # Cache relationships to avoid repeated Gemini API calls
        if "ai_relationships" not in st.session_state:
            st.session_state.ai_relationships = None

        if st.session_state.ai_relationships is None:

            with st.spinner("Gemini is discovering relationships..."):

                try:
                        st.session_state.ai_relationships = extract_concept_relationships(
                            chunk_texts,
                            concepts
    )
                except Exception as e:

                    st.error(f"Relationship extraction failed: {e}")
                    st.stop()

        relationships = st.session_state.ai_relationships

        st.markdown("### 🕸️ AI Knowledge Network")

        st.caption(
            f"{len(concepts)} concepts | "
            f"{len(relationships)} AI relationships"
        )

        render_knowledge_graph(
            concepts,
            edges,
            relationships
        )

        st.divider()

        st.markdown("### 🧠 AI-Discovered Relationships")

        if relationships:

            for relation in relationships:

                st.markdown(
                    f"""
                    <div class="metric">
                        <div class="metric-label">
                            {relation["source"].upper()}
                        </div>
                        <div class="metric-value">
                            {relation["relationship"]}
                        </div>
                        <div class="metric-label">
                            {relation["target"].upper()}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.info("No meaningful relationships were identified.")

        st.divider()

        st.markdown("### Extracted Concepts")

        cols = st.columns(4)

        for index, concept in enumerate(concepts):

            with cols[index % 4]:

                st.markdown(
                    f"""
                    <div class="metric">
                        <div class="metric-value">✦</div>
                        <div class="metric-label">
                            {concept.upper()}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ==========================================
# FOOTER
# ==========================================

st.write("")

st.markdown("""
<div style="
    text-align:center;
    color:#536D82;
    font-size:11px;
    padding:20px;
">
    OMEGA-C · AI KNOWLEDGE INTELLIGENCE · POWERED BY GEMINI
</div>
""", unsafe_allow_html=True)
