from flask import Flask, request, render_template_string, redirect, url_for
import html
import json

app = Flask(__name__)

# Predefined markdown snippets (based on the HackerOne markdown guide you provided)
SECTIONS = {
    "headers": {
        "title": "Headers",
        "sample": "# A First Level Header\n\n## A Second Level Header\n\n### Header 3\n"
    },
    "blockquotes": {
        "title": "Block Quotes",
        "sample": "> text in blockquote\n> more text in blockquote\n"
    },
    "emphasis": {
        "title": "Text Emphasis",
        "sample": "*This text is italicized*\n\n**This text is bold**\n\n~~This text is deleted~~\n\n==This text is highlighted==\n"
    },
    "unordered_lists": {
        "title": "Unordered Lists",
        "sample": "- Candy\n- Gum\n- Juice\n"
    },
    "ordered_lists": {
        "title": "Numbered Lists",
        "sample": "1. Red\n2. Green\n3. Blue\n"
    },
    "links": {
        "title": "Links",
        "sample": "This is an [example link](http://example.com/).\n\nReference style:\n\nI get 10 times more traffic from [Google][1] than from [Yahoo][2].\n\n[1]: http://google.com/\n[2]: http://search.yahoo.com/\n"
    },
    "code": {
        "title": "Code Blocks",
        "sample": "Inline `code` example.\n\n```\n# code block\nprint('hello')\n```\n\n```python\n# highlighted\ndef foo():\n    return 'bar'\n```\n"
    },
    "mentions": {
        "title": "User Mentions",
        "sample": "@demo-member reported the issue.\n"
    },
    "report_reference": {
        "title": "Report Reference",
        "sample": "#105887 is a publicly disclosed bug.\n"
    },
    "autolinking": {
        "title": "Auto-Linked References",
        "sample": "CVE-2011-0242 could perhaps be categorized as CWE-79 or CAPEC-63.\n"
    },
    "attachments": {
        "title": "Attachment / Inline Media",
        "sample": "{F1}\n\n(Use attachment references like {F1} to embed uploaded images/videos.)\n"
    },
    "tables": {
        "title": "Tables",
        "sample": "| First Header | Second Header |\n| --- | --- |\n| Content Cell | Content Cell |\n| Content Cell | Content Cell |\n"
    }
}

# Halloween-themed index HTML with floating slash menu (no right panel) and live preview to the right
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>🎃 Halloween Markdown Editor — Slash Menu + Preview</title>
  <link href="https://fonts.googleapis.com/css2?family=Creepster&family=Montserrat:wght@300;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root{--bg:#0b0f14;--accent:#ff8c1a;--muted:#bfbfbf}
    html,body{height:100%;margin:0;font-family:Montserrat,system-ui,Segoe UI,Roboto,Arial;background:linear-gradient(180deg,#071018,#050506);color:var(--muted);padding:22px;}
    header{display:flex;align-items:center;gap:16px;margin-bottom:12px}
    .logo{width:68px;height:68px;border-radius:12px;background:linear-gradient(135deg,#ff8c1a,#ff5e00);display:flex;align-items:center;justify-content:center;font-family:Creepster, cursive;font-size:32px;color:#111}
    h1{margin:0;font-family:Creepster, cursive;color:var(--accent);font-size:22px}
    .layout{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start}
    .editor-wrap{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:16px;border-radius:10px;border:1px solid rgba(255,255,255,0.03);position:relative}
    textarea#editor{width:100%;height:78vh;background:transparent;color:var(--muted);border:1px solid rgba(255,255,255,0.03);padding:12px;border-radius:8px;font-family:monospace;font-size:14px;box-sizing:border-box;resize:vertical}
    .hint{color:#cdbfa6;margin-top:6px;font-size:13px}
    .preview-wrap{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:16px;border-radius:10px;border:1px solid rgba(255,255,255,0.03);min-height:78vh}
    .preview-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
    .preview-box{background:#060709;padding:12px;border-radius:8px;height:calc(78vh - 56px);overflow:auto;border:1px solid rgba(255,255,255,0.03)}
    /* floating menu */
    .fm-menu{position:absolute;background:#0d0f12;border:1px solid rgba(255,255,255,0.04);box-shadow:0 8px 30px rgba(0,0,0,0.6);min-width:300px;border-radius:8px;padding:8px;z-index:9999}
    .fm-search{width:100%;padding:8px;border-radius:6px;border:1px solid rgba(255,255,255,0.03);background:transparent;color:var(--muted);margin-bottom:8px;box-sizing:border-box}
    .fm-item{padding:8px;border-radius:6px;margin-bottom:6px;color:var(--muted);cursor:pointer;border:1px dashed rgba(255,255,255,0.03);background:transparent}
    .fm-item:hover{background:rgba(255,140,26,0.06)}
    .hidden{display:none}
    @media(max-width:900px){ .layout{grid-template-columns:1fr} textarea#editor{height:60vh}.preview-box{height:200px} .fm-menu{min-width:220px} }
    /* styled rendered markdown */
    #preview :where(h1,h2,h3){color:#ffb67a}
    #preview pre{background:#0b0f13;padding:10px;border-radius:6px;border:1px solid rgba(255,255,255,0.02)}
    #preview code{background:#0b0f13;padding:2px 6px;border-radius:4px}
    /* table styles so GFM tables render nicely in preview */
    #preview table{width:100%;border-collapse:collapse;margin:8px 0}
    #preview th,#preview td{border:1px solid rgba(255,255,255,0.06);padding:8px;text-align:left;background:rgba(255,255,255,0.01)}
    #preview thead th{background:rgba(255,140,26,0.06);color:#ffdcb0}
    /* blockquote styles so quotes render clearly */
    #preview blockquote{
      border-left:4px solid rgba(255,140,26,0.12);
      margin:8px 0;
      padding:8px 12px;
      color:#e9decf;
      background:rgba(255,255,255,0.01);
      border-radius:6px;
      font-style:italic;
    }
    /* highlight (==text==) styling */
    #preview mark{background:rgba(255,200,100,0.12);color:#ffdcb0;padding:2px 6px;border-radius:4px}
  </style>
</head>
<body>
  <header>
    <div class="logo">🎃</div>
    <div>
      <h1>Halloween Markdown Editor</h1>
      <div class="hint">Type "/" to open an inline menu. Select a snippet to insert. Esc closes the menu. Preview updates live on the right.</div>
    </div>
  </header>

  <div class="layout">
    <div class="editor-wrap">
      <textarea id="editor" spellcheck="false"># Creepy Vulnerability Report

_Write your report here. Type "/" to insert markdown snippets (headers, lists, code, tables, attachments...)._
      </textarea>

      <!-- floating menu (hidden by default) -->
      <div id="fmMenu" class="fm-menu hidden" role="dialog" aria-hidden="true">
        <input id="fmSearch" class="fm-search" placeholder="Filter snippets..." />
        <div id="fmList">
          {% for key, s in sections.items() %}
            <div class="fm-item" data-key="{{ key }}">{{ s.title }}</div>
          {% endfor %}
        </div>
      </div>
    </div>

    <div class="preview-wrap">
      <div class="preview-header">
        <div style="font-weight:700;color:var(--accent)">Rendered Preview</div>
        <div style="color:#cdbfa6;font-size:13px">Live</div>
      </div>
      <div id="preview" class="preview-box"></div>
    </div>
  </div>

  <script>
    // enable GitHub Flavored Markdown with table support
    if (window.marked && marked.setOptions) {
      marked.setOptions({ gfm: true, tables: true, breaks: false, smartLists: true });
    }
    window.sections = {{ sections_json | safe }};
    const editor = document.getElementById('editor');
    const fmMenu = document.getElementById('fmMenu');
    const fmSearch = document.getElementById('fmSearch');
    const fmList = document.getElementById('fmList');
    const preview = document.getElementById('preview');
    // helper to convert HackerOne-style highlight ==text== into HTML <mark>
    function applyHighlight(md){
      return md.replace(/==([^=]+)==/g, '<mark>$1</mark>');
    }

    // approximate char width for monospace (px)
    function charWidth() {
      if (!window._cw) {
        const span = document.createElement('span');
        span.style.visibility = 'hidden';
        span.style.position = 'absolute';
        span.style.font = getComputedStyle(editor).font;
        span.textContent = 'M';
        document.body.appendChild(span);
        window._cw = span.getBoundingClientRect().width || 8;
        document.body.removeChild(span);
      }
      return window._cw || 8;
    }

    // position menu near caret by estimating line/column
    function positionMenuAtCaret() {
      const pos = editor.selectionStart;
      const val = editor.value.slice(0, pos);
      const lines = val.split('\\n');
      const lineIndex = lines.length - 1;
      const col = lines[lines.length - 1].length;
      const rect = editor.getBoundingClientRect();
      const style = getComputedStyle(editor);
      let lineHeight = parseFloat(style.lineHeight);
      if (isNaN(lineHeight)) lineHeight = parseFloat(style.fontSize) * 1.4;
      const scrollTop = editor.scrollTop;
      const top = rect.top + window.scrollY + (lineIndex * lineHeight) - scrollTop + lineHeight + 6;
      const left = rect.left + window.scrollX + (col * charWidth()) + 6;
      // keep menu inside viewport horizontally
      const menuW = fmMenu.getBoundingClientRect().width || 300;
      const maxLeft = window.innerWidth - menuW - 10;
      fmMenu.style.top = Math.max(8, top) + 'px';
      fmMenu.style.left = Math.min(left, maxLeft) + 'px';
    }

    function openMenu() {
      fmMenu.classList.remove('hidden');
      fmMenu.setAttribute('aria-hidden', 'false');
      positionMenuAtCaret();
      fmSearch.value = '';
      filterList('');
      fmSearch.focus();
    }
    function closeMenu() {
      fmMenu.classList.add('hidden');
      fmMenu.setAttribute('aria-hidden', 'true');
      editor.focus();
    }

    function filterList(q) {
      const ql = q.toLowerCase();
      Array.from(fmList.children).forEach(item => {
        const key = item.dataset.key.toLowerCase();
        const title = item.textContent.toLowerCase();
        item.style.display = (key.includes(ql) || title.includes(ql)) ? '' : 'none';
      });
    }

    // insert snippet replacing the slash + query after last slash up to caret
    function insertSnippet(snippet) {
      const el = editor;
      const pos = el.selectionStart;
      const val = el.value;
      const lastSlash = val.lastIndexOf('/', pos - 1);
      let before;
      let after = val.slice(pos);
      if (lastSlash !== -1) {
        before = val.slice(0, lastSlash);
      } else {
        before = val.slice(0, pos);
      }
      el.value = before + snippet + after;
      const newCaret = (before + snippet).length;
      el.focus();
      el.selectionStart = el.selectionEnd = newCaret;
      closeMenu();
      renderPreview();
    }

    // clicking item inserts snippet
    fmList.addEventListener('click', (ev) => {
      const item = ev.target.closest('.fm-item');
      if (!item) return;
      const key = item.dataset.key;
      const snippet = window.sections[key].sample || '';
      insertSnippet(snippet + "\\n");
    });

    // render markdown into preview
    function renderPreview() {
      try {
        const md = applyHighlight(editor.value || '');
        preview.innerHTML = marked.parse(md);
      } catch (e) {
        preview.textContent = editor.value || '';
      }
    }

    // typing in editor
    editor.addEventListener('input', (ev) => {
      renderPreview();
    });

    editor.addEventListener('keyup', (ev) => {
      if (ev.key === '/') {
        openMenu();
      } else {
        if (!fmMenu.classList.contains('hidden')) {
          positionMenuAtCaret();
          const pos = editor.selectionStart;
          const val = editor.value;
          const lastSlash = val.lastIndexOf('/', pos - 1);
          const query = (lastSlash !== -1) ? val.slice(lastSlash + 1, pos) : '';
          fmSearch.value = query;
          filterList(query.trim());
        }
      }
    });

    // keyboard handling for menu navigation
    fmSearch.addEventListener('keydown', (ev) => {
      if (ev.key === 'ArrowDown') {
        ev.preventDefault();
        const first = fmList.querySelector('.fm-item:not([style*="display: none"])');
        if (first) first.focus();
      } else if (ev.key === 'Escape') {
        closeMenu();
      }
    });

    // allow arrow keys and enter on items
    fmList.addEventListener('keydown', (ev) => {
      const target = ev.target.closest('.fm-item');
      if (!target) return;
      if (ev.key === 'ArrowDown') {
        ev.preventDefault();
        let next = target.nextElementSibling;
        while (next && next.style.display === 'none') next = next.nextElementSibling;
        if (next) next.focus();
      } else if (ev.key === 'ArrowUp') {
        ev.preventDefault();
        let prev = target.previousElementSibling;
        while (prev && prev.style.display === 'none') prev = prev.previousElementSibling;
        if (prev) prev.focus();
      } else if (ev.key === 'Enter') {
        ev.preventDefault();
        const key = target.dataset.key;
        const snippet = window.sections[key].sample || '';
        insertSnippet(snippet + "\\n");
      } else if (ev.key === 'Escape') {
        closeMenu();
      }
    });

    // make fm-items focusable
    Array.from(fmList.children).forEach(item => item.tabIndex = 0);

    // search input filters
    fmSearch.addEventListener('input', (ev) => {
      filterList(fmSearch.value);
    });

    // click outside close
    document.addEventListener('click', (ev) => {
      if (!fmMenu.contains(ev.target) && ev.target !== editor) {
        if (!fmMenu.classList.contains('hidden')) closeMenu();
      }
    });

    // reposition on window resize/scroll
    window.addEventListener('resize', () => {
      if (!fmMenu.classList.contains('hidden')) positionMenuAtCaret();
    });
    window.addEventListener('scroll', () => {
      if (!fmMenu.classList.contains('hidden')) positionMenuAtCaret();
    });

    // initial render
    renderPreview();
    closeMenu();
  </script>
</body>
</html>
"""

# Halloween-themed result HTML (unchanged)
RESULT_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>🎃 Generated Report</title>
  <link href="https://fonts.googleapis.com/css2?family=Creepster&family=Montserrat:wght@300;600&display=swap" relstylesheet>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root{--bg:#07080a;--panel:#0d1116;--accent:#ff8c1a;--muted:#d7cbb5}
    html,body{height:100%;margin:0;font-family:Montserrat,system-ui,Segoe UI,Roboto,Arial;background:linear-gradient(180deg,#05060a,#0b0f14);color:var(--muted);padding:20px}
    header{display:flex;align-items:center;gap:16px;margin-bottom:12px}
    .logo{width:72px;height:72px;border-radius:12px;background:linear-gradient(135deg,#ff8c1a,#ff5e00);display:flex;align-items:center;justify-content:center;font-family:Creepster, cursive;font-size:34px;color:#111}
    h1{margin:0;font-family:Creepster, cursive;color:var(--accent)}
    .grid{display:flex;gap:18px;align-items:flex-start}
    .panel{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.03); padding:14px;border-radius:10px;flex:1}
    textarea{width:100%;height:520px;font-family:monospace;padding:10px;border-radius:8px;background:transparent;color:var(--muted);border:1px solid rgba(255,255,255,0.03);box-sizing:border-box}
    #render{border:1px solid rgba(255,255,255,0.03);padding:12px;height:520px;overflow:auto;background:#060709;border-radius:8px}
    .controls{margin-bottom:10px}
    .btn{background:var(--accent);color:#111;border:none;padding:8px 12px;border-radius:8px;cursor:pointer;font-weight:700;margin-right:8px}
    .btn.ghost{background:transparent;border:1px solid rgba(255,255,255,0.04);color:var(--muted)}
    a.btn{display:inline-block;text-decoration:none}
    /* small spooky style for rendered markdown headings */
    #render h1,#render h2,#render h3{color:#ffb67a}
    #render pre{background:#0b0f13;padding:10px;border-radius:6px;border:1px solid rgba(255,255,255,0.02)}
    .badge{display:inline-block;background:#1a1a1a;border-radius:6px;padding:6px 8px;color:#ffcfa3;margin-right:8px}
    /* table styles for generated preview */
    #render table{width:100%;border-collapse:collapse;margin:8px 0}
    #render th,#render td{border:1px solid rgba(255,255,255,0.06);padding:8px;text-align:left;background:rgba(255,255,255,0.01)}
    #render thead th{background:rgba(255,140,26,0.06);color:#ffdcb0}
    /* blockquote styles for generated preview */
    #render blockquote{
      border-left:4px solid rgba(255,140,26,0.12);
      margin:8px 0;
      padding:8px 12px;
      color:#e9decf;
      background:rgba(255,255,255,0.01);
      border-radius:6px;
      font-style:italic;
    }
    /* highlight (==text==) styling for generated preview */
    #render mark{background:rgba(255,200,100,0.12);color:#ffdcb0;padding:2px 6px;border-radius:4px}
  </style>
</head>
<body>
  <header>
    <div class="logo">🎃</div>
    <div>
      <h1>Generated Markdown — Halloween Preview</h1>
      <div style="color:#cdbfa6">Copy, download, or tweak the markdown below. Beware: SPOOKY formatting ahead 👻</div>
    </div>
  </header>

  <div style="margin-bottom:12px">
    <a href="{{ url_for('index') }}" class="btn ghost">Back</a>
    <button class="btn" onclick="copyMarkdown()">Copy Markdown</button>
    <button class="btn" onclick="downloadMarkdown()">Download .md</button>
    <span style="margin-left:12px" class="badge">Halloween Theme</span>
  </div>

  <div class="grid">
    <div class="panel">
      <h3 style="margin-top:0">Raw Markdown</h3>
      <textarea id="md" spellcheck="false">{{ markdown_text }}</textarea>
    </div>
    <div class="panel" style="flex:0.9">
      <h3 style="margin-top:0">Rendered Preview</h3>
      <div id="render"></div>
    </div>
  </div>

  <script>
    // enable GitHub Flavored Markdown with table support
    if (window.marked && marked.setOptions) {
      marked.setOptions({ gfm: true, tables: true, breaks: false, smartLists: true });
    }
    // helper to convert ==text== into <mark>
    function applyHighlight(md){
      return md.replace(/==([^=]+)==/g, '<mark>$1</mark>');
    }
    const mdArea = document.getElementById('md');
    const render = document.getElementById('render');
    function renderMd(){
      const md = applyHighlight(mdArea.value || '');
      render.innerHTML = marked.parse(md);
    }
    mdArea.addEventListener('input', renderMd);
    renderMd();
    function copyMarkdown(){
      mdArea.select();
      document.execCommand('copy');
      alert('Markdown copied to clipboard 🎃');
    }
    function downloadMarkdown(){
      const blob = new Blob([mdArea.value], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'report.md';
      a.click();
      URL.revokeObjectURL(url);
    }
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    # pass JSON to client for menu insertion
    sections_json = json.dumps(SECTIONS)
    return render_template_string(INDEX_HTML, sections=SECTIONS, sections_json=sections_json)

@app.route("/generate", methods=["POST"])
def generate():
    title = request.form.get("title", "Vulnerability Report").strip()
    reporter = request.form.get("reporter", "").strip()
    url_field = request.form.get("url", "").strip()
    summary = request.form.get("summary", "").strip()
    selected = request.form.getlist("sections")

    parts = []
    parts.append(f"# {title}\n")
    if reporter:
        parts.append(f"_Reported by: @{reporter}_\n")
    if url_field:
        parts.append(f"**Affected URL:** {url_field}\n")
    if summary:
        parts.append("## Summary\n")
        parts.append(summary + "\n")

    if not selected:
        parts.append("> No sections selected. Please go back and select at least one Markdown feature to include.\n")
    else:
        parts.append("## Details\n")
        for key in selected:
            sect = SECTIONS.get(key)
            if sect:
                parts.append(f"### {sect['title']}\n")
                parts.append(sect['sample'] + "\n")

    # Example "Report Reference" and final notes
    parts.append("---\n")
    parts.append("If applicable, include attachments using {F1}, {F2}, etc. Reference CVEs/CWEs directly and HackerOne will auto-link.\n")

    md_text = "\n".join(parts)
    # escape for safe embedding inside textarea (render_template_string will handle it, but ensure no accidental unescaped sections)
    return render_template_string(RESULT_HTML, markdown_text=html.escape(md_text))

if __name__ == "__main__":
    # Run locally. On Windows, prefer reloader off to prevent double-run in some environments.
    app.run(host="127.0.0.1", port=5000, debug=True)
