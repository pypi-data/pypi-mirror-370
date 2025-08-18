import os

# === Fungsi Helper ===
def read_template(file_path):
    """Baca file template dengan path absolut atau relatif terhadap modul ini."""
    if not os.path.isabs(file_path):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def get_starter_structure_js_tlwnd():
    """Bangun struktur starter kit, baca file template hanya saat dipanggil."""
    base = os.path.join("starter", "Jsvanilla-tailwind")
    
    return {
        "app": {
            "__init__.py": read_template(os.path.join(base, "app", "__init__.py")),
            "extensions.py": read_template(os.path.join(base, "app", "extensions.py")),
            "blueprints.py": read_template(os.path.join(base, "app", "blueprints.py")),
            "controllers": {
                "counter_controller.py": read_template(os.path.join(base, "app", "controllers", "counter_controller.py"))
            },
            "routes": {
                "counter_routes.py": read_template(os.path.join(base, "app", "routes", "counter_routes.py"))
            },
            "services": {},
            "models": {},
            "templates": {
                "base.html": read_template(os.path.join(base, "app", "templates", "base.html")),
                "counter.html": read_template(os.path.join(base, "app", "templates", "counter.html")),
            },
            "static": {
                "css": {
                    "input.css": read_template(os.path.join(base, "app", "static", "css", "input.css")),
                    "style.css": "/* Tailwind compiled css (auto-generated) */",
                },
                "js": {
                    "counter.js": read_template(os.path.join(base, "app", "static", "js", "counter.js")),
                    "effects.js": read_template(os.path.join(base, "app", "static", "js", "effects.js")),
                },
            },
        },
        "config": {
            "__init__.py": "",
            "default.py": read_template(os.path.join(base, "config", "default.py")),
        },
        "main.py": read_template(os.path.join(base, "main.py")),
        "requirements.txt": read_template(os.path.join(base, "requirements.txt")),
        ".env": read_template(os.path.join(base, ".env")),
        "package.json": read_template(os.path.join(base, "package.json")),
        "tailwind.config.js": read_template(os.path.join(base, "tailwind.config.js")),
        "postcss.config.js": read_template(os.path.join(base, "postcss.config.js")),
    }

def create_structure(base_path, structure):
    """Rekursif buat folder dan file sesuai struktur."""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)  # pastikan folder ada
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created: {path}")
