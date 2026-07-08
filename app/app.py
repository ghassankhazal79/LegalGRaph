from flask import Flask,request,render_template,jsonify
import os

def create_app():
    app=Flask(__name__)
    DATA_DIR=os.getenv('DATA_DIR','data')

    @app.get("/entities")
    def entities_page():
        import json
        from pathlib import Path
        p = Path(DATA_DIR) / "entities.json"
        if not p.exists():
            return render_template("entities.html", summary={}, entities=[], labels=[], q="", selected_label="", message="Run python scripts/04_extract_entities_graph.py")
        data = json.load(open(p, "r", encoding="utf-8"))
        q = (request.args.get("q") or "").strip()
        label = (request.args.get("label") or "").strip()
        entities = data.get("entities", [])
        if q:
            entities = [e for e in entities if q in e["text"]]
        if label:
            entities = [e for e in entities if e["label"] == label]
        labels = sorted(data.get("summary", {}).get("label_counts", {}).keys())
        return render_template("entities.html", summary=data.get("summary", {}), entities=entities[:500], labels=labels, q=q, selected_label=label)

    @app.get("/entity/<entity_id>")
    def entity_detail(entity_id):
        import json
        from pathlib import Path
        p = Path(DATA_DIR) / "entities.json"
        data = json.load(open(p, "r", encoding="utf-8"))
        entity = next((e for e in data.get("entities", []) if e["id"] == entity_id), None)
        if entity is None:
            return "Entity not found", 404
        return render_template("entity_detail.html", entity=entity)

    @app.get("/entity-graph")
    def entity_graph():
        return render_template("entity_graph.html")

    @app.get("/api/entity-graph")
    def api_entity_graph():
        import json
        from pathlib import Path
        p = Path(DATA_DIR) / "entity_graph.json"
        if not p.exists():
            return jsonify({"nodes": [], "edges": []})
        return jsonify(json.load(open(p, "r", encoding="utf-8")))


    return app

if __name__=='__main__':
    create_app().run(debug=True)



if __name__ == "__main__":
    import socket
    import webbrowser
    import threading
    import time

    def find_free_port():
        preferred_ports = [8765, 8899, 9000, 9876, 10000, 12000, 15000, 18080, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000]
        env_port = os.getenv("PORT")
        if env_port:
            try:
                preferred_ports.insert(0, int(env_port))
            except ValueError:
                pass

        for port in preferred_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(("127.0.0.1", port))
                    return port
            except OSError:
                continue

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    selected_port = find_free_port()
    print("=" * 70)
    print(f"Legal AI is starting on: http://127.0.0.1:{selected_port}")
    print(f"Entities page:          http://127.0.0.1:{selected_port}/entities")
    print(f"Entity graph:           http://127.0.0.1:{selected_port}/entity-graph")
    print("=" * 70)

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://127.0.0.1:{selected_port}")

    threading.Thread(target=open_browser, daemon=True).start()
    app = create_app()
    app.run(host="127.0.0.1", port=selected_port, debug=False, use_reloader=False)
