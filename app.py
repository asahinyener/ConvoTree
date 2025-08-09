#!/usr/bin/env python3
# ConvoCompressor-R demo server
# ─────────────────────────────────────────────────────────────────────────────
import os, json, datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, request, jsonify, Response
from openai import OpenAI
import networkx as nx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="/static")

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OPENAI_API_KEY environment variable is not set.")
    print("Set it with: export OPENAI_API_KEY=your_api_key_here")
    # Use a dummy key for testing imports
    api_key = "dummy_key_for_testing"

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Define the model to use (GPT-5)
GPT_MODEL = "gpt-5"

# Ensure static folder exists
Path(app.static_folder).mkdir(parents=True, exist_ok=True)

PROMPT_PATH = Path("prompts/compressor_prompt.txt")
if not os.path.exists(PROMPT_PATH):
    raise SystemExit("Missing compressor_prompt.txt – add your system prompt.")
SYSTEM_PROMPT = Path(PROMPT_PATH).read_text(encoding="utf-8")

TEMPLATE_PATH = Path("prompts/resume_prompt.txt")
if not TEMPLATE_PATH.exists():
    raise SystemExit(
        "Missing prompts/resume_promt.txt – please create it before running the server."
    )

# Everything for a single run lives inside static/runs/<timestamp>/
BASE_RUNS_DIR = Path(app.static_folder) / "runs"
BASE_RUNS_DIR.mkdir(parents=True, exist_ok=True)

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
    # Include more KG facts (up to 15 instead of 7) for better context
    bullets = [f"• {t.replace('|', ' → ')}" for t in kg[:15]]
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
        model=GPT_MODEL,
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
        model=GPT_MODEL,
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
    # Redirect to the static index.html file
    return Response(
        '<script>window.location.href = "/static/index.html";</script>'
        '<p>Redirecting to <a href="/static/index.html">demo page</a>...</p>',
        mimetype="text/html"
    )

@app.route("/api", methods=["GET"])
def api_docs() -> Response:
    html = (
        "<h3>ConvoCompressor-R API</h3>"
        "<p>Artefacts for each run live under <code>/static/runs/&lt;timestamp&gt;/</code>.</p>"
        "<ul>"
        "<li><code>/compress</code> – POST JSON list (or {'messages':[ ... ]})</li>"
        "<li><code>/compress_txt</code> – POST plain/text (copy-paste transcript)</li>"
        "<li><code>/resume</code> – POST {bundle_path, next_user, sequential_compression}</li>"
        "<ul>"
        "<li>Set <code>sequential_compression=true</code> to update the KG with each new exchange</li>"
        "</ul>"
        "</ul>"
        "<p><a href='/static/index.html'>Go to Demo</a></p>"
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
    sequential_compression = data.get("sequential_compression", False)

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
    
    # If sequential compression is enabled, update the KG with new information
    if sequential_compression:
        # Create a new conversation with the previous messages and the new exchange
        messages = []
        if "trace" in bundle:
            # Convert trace to messages format
            for trace_item in bundle.get("trace", []):
                parts = trace_item.split("|", 2)
                if len(parts) >= 3:
                    turn_num, role, content = parts
                    messages.append({"role": role, "content": content})
        
        # Add the new exchange
        messages.append({"role": "user", "content": next_user})
        messages.append({"role": "assistant", "content": out["assistant_reply"]})
        
        # Recompress the entire conversation to update the KG
        updated_bundle = compress_chat(messages)
        
        # Merge the updated KG with the original bundle
        bundle["kg"] = updated_bundle.get("kg", [])
        bundle["ds"] = updated_bundle.get("ds", {})
        bundle["links"] = updated_bundle.get("links", [])
        bundle["trace"] = updated_bundle.get("trace", [])
        bundle["dp"] = updated_bundle.get("dp", "")
        
        # Save the updated bundle and regenerate assets
        paths = save_bundle_and_assets(bundle, bundle_path.parent.name)
        
        return jsonify({
            "assistant_reply": out["assistant_reply"],
            "resume_prompt_path": resume_rel,
            "kg_path": str(paths["kg_txt"].relative_to(app.static_folder)),
            "kg_image": f"/static/{paths['kg_png'].relative_to(app.static_folder)}",
            "bundle_path": str(paths["bundle"].relative_to(app.static_folder)),
        })
    
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
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 12000))
    print(f"Starting server on http://0.0.0.0:{port}")
    # Set CORS headers to allow iframe embedding
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    app.run(host="0.0.0.0", port=port, debug=True)
