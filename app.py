#!/usr/bin/env python3
# ConvoCompressor-R demo server
# ─────────────────────────────────────────────────────────────────────────────
import os, json, datetime
from pathlib import Path
from typing import List, Dict, Any

from flask import Flask, request, jsonify, Response
from openai import OpenAI
import networkx as nx
import matplotlib
from enhanced_chat import ConversationManager, EnhancedChatSystem

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="/static")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_PATH = Path("prompts/compressor_prompt.txt")
if not os.path.exists(PROMPT_PATH):
    raise SystemExit("Missing compressor_prompt.txt – add your system prompt.")
SYSTEM_PROMPT = Path(PROMPT_PATH).read_text(encoding="utf-8")

TEMPLATE_PATH = Path("prompts/resume_prompt.txt")
if not TEMPLATE_PATH.exists():
    raise SystemExit(
        "Missing prompts/resume_prompt.txt – please create it before running the server."
    )

# Everything for a single run lives inside static/runs/<timestamp>/
BASE_RUNS_DIR = Path(app.static_folder) / "runs"
BASE_RUNS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize conversation manager for persistent KG approach
conversation_manager = ConversationManager()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers – KG visual + resume prompt
# ─────────────────────────────────────────────────────────────────────────────
def draw_kg(triples: List[str], outfile: Path) -> None:
    """Render a simple force-layout PNG of the KG triples."""
    if not triples:
        return
    G = nx.DiGraph()
    for trip in triples:
        try:
            s, p, o = (x.strip() for x in trip.split("|", 2))
        except ValueError:
            continue
        G.add_edge(s, o, label=p)
    pos = nx.spring_layout(G, k=0.6, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightblue")
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="-|>")
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_size=6
    )
    plt.axis("off")
    plt.tight_layout()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outfile, dpi=150)
    plt.close()


def build_resume_prompt(kg: List[str], ds: Dict[str, Any]) -> str:
    tmpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    bullets = [f"• {t.replace('|', ' → ')}" for t in kg[:7]]
    facts = "\n".join(bullets) if bullets else "(none)"
    return (
        tmpl.replace("{{facts}}", facts)
            .replace("{{ds_json}}", json.dumps(ds, ensure_ascii=False))
    )


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI wrappers
# ─────────────────────────────────────────────────────────────────────────────
def compress_chat(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({"messages": messages})},
        ],
    )
    return json.loads(resp.choices[0].message.content)


def resume_chat(bundle: Dict[str, Any], next_user: str) -> Dict[str, str]:
    prompt = build_resume_prompt(bundle.get("kg", []), bundle.get("ds", {}))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": next_user},
        ],
    )
    return {"assistant_reply": resp.choices[0].message.content}


# ─────────────────────────────────────────────────────────────────────────────
# Core storage helper – save everything inside one folder
# ─────────────────────────────────────────────────────────────────────────────
def save_bundle_and_assets(bundle: Dict[str, Any], stem: str) -> Dict[str, Path]:
    run_dir = BASE_RUNS_DIR / stem
    run_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "bundle": run_dir / "bundle.json",
        "kg_txt": run_dir / "kg.txt",
        "kg_png": run_dir / "kg.png",
        "resume_txt": run_dir / "resume.txt",
    }

    # write files
    paths["bundle"].write_text(json.dumps(bundle, ensure_ascii=False, indent=2))
    paths["kg_txt"].write_text("\n".join(bundle.get("kg", [])))
    draw_kg(bundle.get("kg", []), paths["kg_png"])
    resume_prompt = build_resume_prompt(bundle.get("kg", []), bundle.get("ds", {}))
    paths["resume_txt"].write_text(resume_prompt)

    return paths


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index() -> Response:
    html = (
        "<h3>ConvoCompressor-R</h3>"
        "<p>Artefacts for each run live under <code>/static/runs/&lt;timestamp&gt;/</code>.</p>"
        "<ul>"
        "<li><code>/compress</code> – POST JSON list (or {'messages':[ ... ]})</li>"
        "<li><code>/compress_txt</code> – POST plain/text (copy-paste transcript)</li>"
        "<li><code>/resume</code> – POST {bundle_path, next_user}</li>"
        "<li><code>/chat</code> – POST {conversation_id, message} – Persistent KG chat</li>"
        "<li><code>/conversation/{id}/history</code> – GET conversation history</li>"
        "<li><code>/conversation/{id}/export</code> – GET conversation data export</li>"
        "</ul>"
    )
    return Response(html, mimetype="text/html")


@app.route("/compress", methods=["POST"])
def compress_route():
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({"error": "No JSON body."}), 400

    messages = data if isinstance(data, list) else data.get("messages", [])
    if not isinstance(messages, list):
        return jsonify({"error": "'messages' must be a list."}), 400

    bundle, paths = run_pipeline(messages)
    return jsonify(public_payload(paths))


@app.route("/compress_txt", methods=["POST"])
def compress_txt_route():
    transcript = request.get_data(as_text=True)
    if not transcript.strip():
        return jsonify({"error": "Empty body."}), 400

    messages = [{"role": "user", "content": transcript}]
    bundle, paths = run_pipeline(messages)
    return jsonify(public_payload(paths))


@app.route("/resume", methods=["POST"])
def resume_route():
    data = request.get_json(force=True, silent=True) or {}
    bundle_rel = str(data.get("bundle_path", "")).lstrip("/")  # runs/<stem>/bundle.json
    next_user = data.get("next_user", "").strip()

    if not bundle_rel or not next_user:
        return jsonify({"error": "Provide bundle_path and next_user."}), 400

    # Resolve inside /static
    bundle_path = Path(app.static_folder) / bundle_rel
    if not bundle_path.exists():
        return jsonify({"error": f"bundle_path not found. {bundle_path}"}), 404

    try:
        bundle = json.loads(bundle_path.read_text())
    except Exception as e:
        return jsonify({"error": f"Failed to read bundle: {e}"}), 500

    out = resume_chat(bundle, next_user)

    # Append reply to resume.txt
    resume_path = bundle_path.parent / "resume.txt"
    resume_path.write_text(
        resume_path.read_text(encoding="utf-8") + "\n---\nNEXT ASSISTANT REPLY:\n" + out["assistant_reply"],
        encoding="utf-8",
    )

    resume_rel = str(resume_path.relative_to(app.static_folder))

    return jsonify(
        {
            "assistant_reply": out["assistant_reply"],
            "resume_prompt_path": resume_rel,
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def run_pipeline(messages: List[Dict[str, str]]):
    bundle = compress_chat(messages)
    stem = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = save_bundle_and_assets(bundle, stem)
    return bundle, paths


def public_payload(paths: Dict[str, Path]):
    return {
        "bundle_path": str(paths["bundle"].relative_to(app.static_folder)),
        "kg_path": str(paths["kg_txt"].relative_to(app.static_folder)),
        "resume_prompt_path": str(paths["resume_txt"].relative_to(app.static_folder)),
        "kg_image": f"/static/{paths['kg_png'].relative_to(app.static_folder)}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Persistent KG Chat Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def persistent_chat():
    """Enhanced chat with persistent knowledge graph"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    
    conversation_id = data.get("conversation_id")
    message = data.get("message", "").strip()
    
    if not conversation_id or not message:
        return jsonify({"error": "Both conversation_id and message are required"}), 400
    
    try:
        result = conversation_manager.send_message(conversation_id, message)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Chat processing failed: {str(e)}"}), 500


@app.route("/conversation/<conversation_id>/history", methods=["GET"])
def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    try:
        chat = conversation_manager.get_conversation(conversation_id)
        limit = request.args.get("limit", 20, type=int)
        history = chat.get_conversation_history(limit)
        
        return jsonify({
            "conversation_id": conversation_id,
            "history": history,
            "total_turns": len(history)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get history: {str(e)}"}), 500


@app.route("/conversation/<conversation_id>/export", methods=["GET"])
def export_conversation(conversation_id: str):
    """Export complete conversation data"""
    try:
        chat = conversation_manager.get_conversation(conversation_id)
        export_data = chat.export_conversation_data()
        
        return jsonify(export_data)
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500


@app.route("/conversation/<conversation_id>/summary", methods=["GET"])
def get_conversation_summary(conversation_id: str):
    """Get conversation summary and statistics"""
    try:
        chat = conversation_manager.get_conversation(conversation_id)
        summary = chat.kg.get_conversation_summary()
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": f"Failed to get summary: {str(e)}"}), 500


@app.route("/conversations", methods=["GET"])
def list_conversations():
    """List all active conversations"""
    try:
        conversations = conversation_manager.list_conversations()
        return jsonify({
            "active_conversations": conversations,
            "count": len(conversations)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to list conversations: {str(e)}"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=True)
