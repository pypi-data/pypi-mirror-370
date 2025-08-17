#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re, ast, inspect, argparse, textwrap, pathlib, shutil, subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ========================= Django bootstrap =========================
# cli.py -> bootstrap_django()

def bootstrap_django(settings_override=None, extras_pythonpath=None):
    # 1) sys.path: manage.py dir + manage.py/src
    cwd = pathlib.Path.cwd()
    manage_dir = None
    for p in [cwd] + list(cwd.parents):
        if (p / "manage.py").exists():
            manage_dir = p
            break
    if manage_dir:
        sys.path.insert(0, str(manage_dir))
        if (manage_dir / "src").exists():
            sys.path.insert(0, str(manage_dir / "src"))

    # 2) DJANGO_SETTINGS_MODULE
    if settings_override:
        os.environ["DJANGO_SETTINGS_MODULE"] = settings_override
    dsm = os.environ.get("DJANGO_SETTINGS_MODULE")

    if not dsm:
        # прежняя эвристика поиска settings.py
        ...

    import django
    django.setup()


def get_view_by_url_name(name: str):
    from django.urls import get_resolver
    resolver = get_resolver()
    def iter_patterns(patterns):
        for p in patterns:
            if hasattr(p, 'url_patterns'):
                yield from iter_patterns(p.url_patterns)
            else:
                yield p
    for p in iter_patterns(resolver.url_patterns):
        try:
            if getattr(p, "name", None) == name:
                return p.callback
        except Exception:
            continue
    return None

# ========================= AST parsing =========================
@dataclass
class CallInfo:
    order: int
    full_name: str
    display: str

class CallCollector(ast.NodeVisitor):
    def __init__(self):
        self.calls: List[CallInfo] = []
        self._order = 0

    def visit_Call(self, node: ast.Call):
        self._order += 1
        name = self._qualify(node.func)
        disp = self._pretty(node.func)
        self.calls.append(CallInfo(self._order, name, disp))
        self.generic_visit(node)

    def _qualify(self, node: ast.AST) -> str:
        if isinstance(node, ast.Attribute):
            return f"{self._qualify(node.value)}.{node.attr}"
        if isinstance(node, ast.Name):
            return node.id
        return node.__class__.__name__

    def _pretty(self, node: ast.AST) -> str:
        if isinstance(node, ast.Attribute):
            return f"{self._pretty(node.value)}.{node.attr}"
        if isinstance(node, ast.Name):
            return node.id
        if hasattr(ast, "unparse"):
            try:
                return ast.unparse(node)
            except Exception:
                pass
        return self._qualify(node)

def extract_calls(src: str) -> List[CallInfo]:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    col = CallCollector()
    col.visit(tree)
    return col.calls

# ========================= C4 (Structurizr + Mermaid) =========================
def guess_c4(calls: List[CallInfo]) -> Tuple[List[str], List[Tuple[str,str,str]]]:
    containers = {}
    rels = set()

    def add_container(key: str, label: str):
        containers[key] = label

    add_container("VIEW", "Django View")
    add_container("API", "Django API")

    for c in calls:
        disp = c.display.lower()

        if "serializer" in disp:
            add_container("SERIALIZER", "Serializer")
            rels.add(("VIEW", "SERIALIZER", "serialize/validate"))

        if re.search(r"\bqueryset\b|\bobjects\.", disp) or ".filter" in disp or (".get(" in disp and "objects.get" in disp):
            add_container("DB", "Database (ORM)")
            rels.add(("VIEW", "DB", "ORM query"))

        if ("requests." in disp) or (".request(" in disp) or (".get(" in disp and "objects.get" not in disp and "request.get" not in disp):
            add_container("EXT", "External API")
            rels.add(("VIEW", "EXT", "HTTP call"))

        if ".publish" in disp or ".send" in disp:
            add_container("MQ", "Message Broker")
            rels.add(("VIEW", "MQ", "event/message"))

        if ".cache" in disp or "cache." in disp:
            add_container("CACHE", "Cache")
            rels.add(("VIEW", "CACHE", "read/write cache"))

        if ".save(" in disp or ".create(" in disp or ".update(" in disp:
            add_container("DB", "Database (ORM)")
            rels.add(("VIEW", "DB", "write"))

    rels.add(("VIEW", "API", "HTTP request/response"))

    cont_list = [f'{k} "{v}"' for k,v in containers.items()]
    rel_list = list(rels)
    return cont_list, rel_list

def build_structurizr_dsl(app: str, handle: str, calls: List[CallInfo]) -> str:
    containers, rels = guess_c4(calls)
    dsl = []
    dsl.append(f'workspace "{app}:{handle}" "Auto doc" {{')
    dsl.append("  model {")
    dsl.append(f'    softwareSystem "{app}" "Django app" {{')
    for c in containers:
        ident, label = c.split(" ", 1)
        dsl.append(f"      container {ident} {label}")
    for (a,b,label) in rels:
        lab = f' "{label}"' if label else ""
        dsl.append(f"      {a} -> {b}{lab}")
    dsl.append("    }")
    dsl.append("  }")
    dsl.append("  views {")
    dsl.append(f'    containerView "{app}" "containers" "Auto" {{')
    dsl.append("      include *")
    dsl.append("      autoLayout")
    dsl.append("    }")
    dsl.append("  }")
    dsl.append("}")
    return "\n".join(dsl)

def build_mermaid(calls: List[CallInfo]) -> str:
    containers, rels = guess_c4(calls)
    # нормализуем названия узлов: VIEW -> "Django View"
    labels = {}
    for c in containers:
        ident, label = c.split(" ", 1)
        labels[ident] = label.strip('"')
    lines = ["graph TD"]
    # узлы
    for ident, label in labels.items():
        lines.append(f'{ident}["{label}"]')
    # рёбра
    for (a,b,label) in rels:
        if label:
            lines.append(f'{a} -->|{label}| {b}')
        else:
            lines.append(f'{a} --> {b}')
    return "\n".join(lines)

# ========================= OpenAI (подробное описание) =========================
GEN_SYS = (
    "Ты пишешь инженерную документацию по коду Django без воды, но доступно и понятно."
    " Пиши по-русски, четко, структурно. Если в коде чего-то нет, не выдумывай."
)

GEN_TMPL = """Дано: Django endpoint {handle} приложения {app}.
Фрагменты кода (view + сопряжённые вызовы):
1) Максимально подробное доступное описание алгоритма: какой запрос принимает, что валидирует/нормализует, как обрабатывает данные, какие ветвления и пограничные случаи, что возвращает, какие побочные эффекты (запись в БД, вызовы внешних сервисов, кеш, сообщения/очереди).
2) Маркированный список: Последовательность действий (по шагам), упоминая КЛАССЫ и МЕТОДЫ/ФУНКЦИИ из кода.
3) Кратко в 4–6 пунктов: C4-описание (уровень Container) — клиент, контейнеры (API/View, Serializer, ORM/DB, внешние API/кэш/очередь при наличии) и их взаимодействия.
Только содержательные пункты, без предисловий и заключений.
"""


def call_openai_slim(system_prompt: str, user_prompt: str) -> Optional[str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":system_prompt},
                      {"role":"user","content":user_prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[warn] OpenAI error: {e}", file=sys.stderr)
        return None

# ========================= Markdown сборка =========================
def extract_section(full: str, idx: int) -> str:
    parts = [p.strip() for p in full.strip().split("\n\n") if p.strip()]
    if idx-1 < len(parts):
        return parts[idx-1]
    return ""

def build_markdown(app: str, alg_name: str, model_text: str,
                   diagram_mode: str, dsl: str,
                   mermaid_src: Optional[str], image_rel_path: Optional[str]) -> str:
    detailed = extract_section(model_text, 1) if model_text else "_(нет данных)_"
    steps = extract_section(model_text, 2) if model_text else "- _(нет данных)_"
    c4 = extract_section(model_text, 3) if model_text else "- API/View\n- Serializer (если есть)\n- ORM/DB\n- Внешние интеграции (если есть)"

    if diagram_mode == "structurizr":
        diag_block = f"![Диаграмма алгоритма]({image_rel_path})" if image_rel_path else "_(PNG-диаграмма не сгенерирована)_"
    else:
        diag_block = f"```mermaid\n{mermaid_src}\n```" if mermaid_src else "_(Mermaid-схема не сгенерирована)_"

    return textwrap.dedent(f"""\
    # {alg_name}

    ## Максимально подробное доступное описание алгоритма
    {detailed}

    ## Последовательность действий
    {steps}

    ## C4 (контейнерный уровень)
    {c4}

    ## Диаграмма
    {diag_block}

    ## Structurizr DSL (для диаграммы)
    ```dsl
    {dsl}
    ```
    """).strip() + "\n"

# ========================= Рендер Structurizr PNG через Docker =========================
def render_structurizr_png_via_docker(project_root: pathlib.Path, dsl_path: pathlib.Path, out_png_path: pathlib.Path) -> Optional[pathlib.Path]:
    rel_dsl = dsl_path.relative_to(project_root).as_posix()
    out_dir = out_png_path.parent / "_diagrams_tmp"
    out_dir.mkdir(parents=True, exist_ok=True)
    rel_out = out_dir.relative_to(project_root).as_posix()

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{str(project_root)}:/data",
        "structurizr/cli",
        "export",
        "-workspace", f"/data/{rel_dsl}",
        "-format", "png",
        "-output", f"/data/{rel_out}",
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("[warn] Docker не найден. Пропускаю рендер PNG.", file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"[warn] Ошибка запуска structurizr/cli: {e}", file=sys.stderr)
        return None

    pngs = list(out_dir.glob("*.png"))
    if not pngs:
        print("[warn] PNG не найден в выходной директории Structurizr.", file=sys.stderr)
        return None

    pick = None
    for p in pngs:
        if "container" in p.name.lower() or "containers" in p.name.lower():
            pick = p; break
    if not pick:
        pick = pngs[0]

    shutil.copyfile(pick, out_png_path)
    for p in pngs:
        try: p.unlink()
        except: pass
    try: out_dir.rmdir()
    except: pass

    return out_png_path

# ========================= Главная =========================
def main():
    parser = argparse.ArgumentParser(description="Django API doc generator (Markdown + Structurizr PNG | Mermaid)")
    parser.add_argument("--app", required=True, help="Имя Django-приложения (папка)")
    parser.add_argument("--handle", required=True, help="Имя URL pattern (name=...)")
    parser.add_argument("--alg-name", required=True, help="Имя алгоритма (для файла)")
    parser.add_argument("--out-root", default=None, help="Корень проекта (по умолчанию cwd)")
    parser.add_argument("--render", choices=["docker","skip"], default="docker", help="Рендер Structurizr PNG (docker|skip)")
    parser.add_argument("--diagram", choices=["structurizr","mermaid"], default="structurizr", help="Тип диаграммы в .md")
    parser.add_argument("--settings", help="Модуль настроек Django, напр. otello_admin.settings")
    parser.add_argument("--pythonpath", help="Доп. пути через ; (Windows) или : (Unix)")
    args = parser.parse_args()

    if args.pythonpath:
        sep = ";" if os.name == "nt" else ":"
        for p in args.pythonpath.split(sep):
            if p: sys.path.insert(0, p)

    bootstrap_django(settings_override=args.settings)
    
    view = get_view_by_url_name(args.handle)
    if not view:
        print(f"Не найден view по name='{args.handle}'. Проверь urls.py.", file=sys.stderr)
        sys.exit(3)

    # исходники
    try:
        src = inspect.getsource(inspect.getmodule(view))
    except Exception:
        try:
            src = inspect.getsource(view)
        except Exception:
            src = "# (исходник недоступен через inspect)"

    src_short = src
    if len(src_short) > 12000:
        name = getattr(view, "__name__", "view")
        m = re.search(rf"def {name}\(.*?\):.*", src, re.S) or re.search(rf"class .*{name}.*:", src)
        if m:
            start = max(0, m.start()-4000)
            end = min(len(src), m.end()+4000)
            src_short = src[start:end]
        else:
            src_short = src[:12000]

    calls = extract_calls(src_short)
    dsl = build_structurizr_dsl(args.app, args.handle, calls)
    mermaid_src = build_mermaid(calls)

    # LLM
    model_text = call_openai_slim(GEN_SYS, GEN_TMPL.format(app=args.app, handle=args.handle, source=src_short))
    if not model_text:
        steps = "\n".join([f"- {c.display}()" for c in calls[:15]]) or "- (шаги не распознаны)"
        model_text = (
            "Алгоритм обрабатывает HTTP-запрос, выполняет валидацию и бизнес-логику, учитывает ветвления и пограничные случаи,"
            " возвращает ответ; возможны побочные эффекты: запись в БД, обращения к внешним сервисам, кеш, очереди.\n\n"
            + steps + "\n\n"
            + "- Клиент → Django API (View)\n- View → ORM/DB (чтение/запись)\n- View → Serializer (валидация/формат)\n- View → внешние сервисы/кэш/очередь (если есть)"
        )

    # Пути
    out_root = pathlib.Path(args.out_root) if args.out_root else pathlib.Path.cwd()
    app_docs = out_root / args.app / "docs"
    app_docs.mkdir(parents=True, exist_ok=True)
    md_path = app_docs / f"{args.alg_name}.md"
    dsl_path = app_docs / f"{args.alg_name}.dsl"
    png_path = app_docs / f"{args.alg_name}.png"

    # Пишем DSL
    dsl_path.write_text(dsl, encoding="utf-8")

    image_rel = None
    if args.diagram == "structurizr" and args.render == "docker":
        out_png = render_structurizr_png_via_docker(out_root, dsl_path, png_path)
        if out_png and out_png.exists():
            image_rel = f"./{args.alg_name}.png"

    content = build_markdown(args.app, args.alg_name, model_text,
                             args.diagram, dsl, mermaid_src, image_rel)
    md_path.write_text(content, encoding="utf-8")

    print(str(md_path))

if __name__ == "__main__":
    main()
