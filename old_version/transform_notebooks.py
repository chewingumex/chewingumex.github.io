#!/usr/bin/env python3
"""
Transform original R-Markdown notebook HTML files into v3 dark-theme versions.
- Keeps all notebook content, code chunks, and visualisations untouched.
- Swaps the old Bootstrap navbar/footer for the v3 design.
- Injects dark-mode CSS overrides.
- Fixes relative asset paths (now one level deeper in v3/).
- Output: v3/{slug}_full_version.html
"""

import re, os

ROOT = '/Users/jondoff/Documents/chewingumex.github.io'
V3   = os.path.join(ROOT, 'v3')

PROJECTS = [
    'churn',
    'covid',
    'credit_risk',
    'film_segmentation',
    'food_prep',
    'gaming_ab',
    'iccmx',
    'transactions_forecast',
]

# ── Strings to inject ─────────────────────────────────────────────────────────

FONT_AND_SHARED = '''\
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;1,300&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;1,9..40,300&display=swap" rel="stylesheet">
<link rel="stylesheet" href="shared.css">'''

DARK_CSS = '''\
<style>
/* ═══════════════════════════════════════════════════
   NOTEBOOK DARK OVERRIDES  (injected by transform script)
   ═══════════════════════════════════════════════════ */

/* base */
body {
  background: #080c10 !important;
  color: #cdd6f4 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 300 !important;
  padding-top: 72px;
}
body::before {
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none; z-index: 0; opacity: 0.6;
}
.container, .container-fluid, #content { position: relative; z-index: 1; }

/* typography */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Syne', sans-serif !important;
  color: #f0f4ff !important;
  font-weight: 700 !important;
  letter-spacing: -0.01em;
}
h1.title {
  font-size: clamp(1.8rem, 4vw, 3rem) !important;
  letter-spacing: -0.02em !important;
}
h4.author, h4.date { color: #6a7a99 !important; font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; font-weight: 400 !important; letter-spacing: 0.08em !important; }
p, li { color: #cdd6f4 !important; line-height: 1.8; }
a { color: #00e5ff !important; text-decoration: none !important; }
a:hover { color: #ffffff !important; }
hr { border-color: #1c2840 !important; }
strong, b { color: #f0f4ff !important; font-weight: 600 !important; }

/* code blocks */
pre {
  background: #0b1219 !important;
  border: 1px solid #1c2840 !important;
  border-radius: 6px !important;
  color: #cdd6f4 !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 0.82rem !important;
  padding: 1.25rem !important;
  line-height: 1.6 !important;
}
code {
  background: rgba(0,229,255,0.08) !important;
  color: #00e5ff !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 0.82rem !important;
  padding: 0.15em 0.4em !important;
  border-radius: 3px !important;
  border: none !important;
}
pre > code {
  background: transparent !important;
  color: #cdd6f4 !important;
  padding: 0 !important;
}
/* syntax highlighting tokens */
.hljs-keyword, .kw      { color: #7b61ff !important; }
.hljs-built_in, .bu     { color: #7b61ff !important; }
.hljs-string, .st       { color: #f59e0b !important; }
.hljs-number, .dv, .fl  { color: #00e5ff !important; }
.hljs-comment, .co      { color: #4a5a78 !important; font-style: italic !important; }
.hljs-function, .fu     { color: #a78bfa !important; }
.hljs-operator, .op     { color: #e2e8f0 !important; }
.hljs-variable, .va     { color: #cdd6f4 !important; }

/* output from code chunks */
pre.r, pre.python, pre.bash { border-left: 3px solid #7b61ff !important; }
pre.sourceCode              { border-left: 3px solid #7b61ff !important; }

/* tables */
table { color: #cdd6f4 !important; border-collapse: collapse !important; width: 100% !important; }
.table { background: transparent !important; color: #cdd6f4 !important; }
.table > thead > tr > th {
  background: #0b1219 !important; color: #f0f4ff !important;
  border-color: #1c2840 !important;
  font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important;
  letter-spacing: 0.08em !important; text-transform: uppercase !important;
  padding: 0.75rem 1rem !important;
}
.table > tbody > tr > td { border-color: #1c2840 !important; padding: 0.65rem 1rem !important; }
.table-striped > tbody > tr:nth-of-type(odd) { background: rgba(11,18,25,0.6) !important; }
.table-hover > tbody > tr:hover { background: rgba(0,229,255,0.05) !important; }
.dataTable thead th { background: #0b1219 !important; color: #f0f4ff !important; border-color: #1c2840 !important; }
.dataTables_wrapper { color: #cdd6f4 !important; }
.dataTables_filter input, .dataTables_length select {
  background: #0e1520 !important; border: 1px solid #1c2840 !important;
  color: #cdd6f4 !important; border-radius: 4px !important;
}
.paginate_button { color: #6a7a99 !important; }
.paginate_button.current, .paginate_button:hover { background: #0e1520 !important; color: #00e5ff !important; border-color: #1c2840 !important; }

/* bootstrap components */
.well { background: #0b1219 !important; border-color: #1c2840 !important; color: #cdd6f4 !important; }
.panel { background: transparent !important; border-color: #1c2840 !important; }
.panel-default > .panel-heading { background: #0b1219 !important; border-color: #1c2840 !important; color: #f0f4ff !important; }
.panel-body { color: #cdd6f4 !important; }
.alert-info { background: rgba(0,229,255,0.06) !important; border-color: rgba(0,229,255,0.2) !important; color: #cdd6f4 !important; }
.label-default { background: #1c2840 !important; }
.badge { background: #1c2840 !important; }

/* tab panels */
.nav-tabs { border-color: #1c2840 !important; }
.nav-tabs > li > a { color: #6a7a99 !important; border-color: transparent !important; background: transparent !important; }
.nav-tabs > li > a:hover { color: #00e5ff !important; border-color: #1c2840 !important; background: #0b1219 !important; }
.nav-tabs > li.active > a, .nav-tabs > li.active > a:hover { color: #f0f4ff !important; background: #0b1219 !important; border-color: #1c2840 #1c2840 #0b1219 !important; }
.tab-content { border: 1px solid #1c2840 !important; border-top: none !important; background: #0b1219 !important; padding: 1.5rem !important; }

/* plots & charts — keep transparent so they look native on dark bg */
.plotly, .js-plotly-plot { background: transparent !important; }
svg text { fill: #cdd6f4 !important; }
svg .gridlayer path { stroke: #1c2840 !important; }
img { opacity: 0.92; }

/* table of contents */
#TOC {
  background: #0b1219 !important; border: 1px solid #1c2840 !important;
  border-radius: 6px !important; padding: 1.5rem !important; margin-bottom: 2rem !important;
}
#TOC ul { list-style: none !important; padding-left: 1rem !important; }
#TOC li { margin: 0.4rem 0 !important; }
#TOC a { color: #6a7a99 !important; font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; }
#TOC a:hover { color: #00e5ff !important; }
/* rmarkdown floating toc */
.tocify { background: #0b1219 !important; border-color: #1c2840 !important; border-radius: 6px !important; }
.tocify-item > a { color: #6a7a99 !important; font-size: 0.8rem !important; }
.tocify-item.active > a, .tocify-subheader .tocify-item.active > a { color: #00e5ff !important; }

/* notebook-wrapper padding */
.col-lg-10.col-lg-offset-1,
.col-lg-8.col-lg-offset-2 { padding-top: 2rem; }

/* section dividers within notebook */
.section.level2 { border-top: 1px solid #1c2840; padding-top: 2.5rem; margin-top: 2.5rem; }

/* scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #080c10; }
::-webkit-scrollbar-thumb { background: #1c2840; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00e5ff; }
</style>'''

NEW_NAV = '''\
  <div class="glow-orb a"></div>
  <div class="glow-orb b"></div>

  <nav>
    <a href="index.html" class="nav-logo">JD<span>.</span></a>
    <ul class="nav-links">
      <li><a href="work.html" class="active">Work</a></li>
      <li><a href="about.html">About</a></li>
      <li><a href="contact.html">Contact</a></li>
    </ul>
  </nav>'''

NEW_FOOTER = '''\
  <footer>
    <span>© 2025 JD · Data Science Portfolio · London, UK</span>
    <div class="footer-links">
      <a href="https://github.com/chewingumex" target="_blank">GitHub ↗</a>
      <a href="https://www.linkedin.com/in/jondavidoff" target="_blank">LinkedIn ↗</a>
      <a href="https://www.doctorswithoutborders.org/" target="_blank">MSF ♥</a>
    </div>
  </footer>'''

# ── Transformation ─────────────────────────────────────────────────────────────

def transform(slug):
    src = os.path.join(ROOT, f'{slug}.html')
    dst = os.path.join(V3,   f'{slug}_full_version.html')

    print(f'  Reading  {slug}.html  ({os.path.getsize(src) // 1024}KB)…')
    with open(src, encoding='utf-8') as f:
        html = f.read()

    # 1. Fix relative asset paths (file moves from root → v3/)
    html = html.replace('href="assets/', 'href="../assets/')
    html = html.replace("href='assets/", "href='../assets/")
    html = html.replace('src="assets/',  'src="../assets/')
    html = html.replace("src='assets/",  "src='../assets/")

    # 2. Remove old stylesheet links we're replacing
    html = re.sub(r'<link[^>]+href="../assets/css/main\.css"[^>]*/?>',   '', html)
    # Keep bootstrap.css — notebook grid layout depends on it.
    # Remove old hover zoom scripts
    html = re.sub(r'<script[^>]+src="../assets/js/hover\.zoom[^"]*"[^>]*></script>\s*', '', html)
    # Remove old jQuery (shared.css doesn't need it; bootstrap.min.js brings its own)
    html = re.sub(r'<script[^>]+src="https://code\.jquery\.com/[^"]*"[^>]*></script>\s*', '', html)

    # 3. Inject fonts + shared.css + dark overrides just before </head>
    injection = FONT_AND_SHARED + '\n' + DARK_CSS
    html = html.replace('</head>', injection + '\n</head>', 1)

    # 4. Replace old Bootstrap navbar
    # Pattern: <div class="navbar navbar-inverse..."> ... </div><!--/.nav-collapse --> </div> </div>
    html = re.sub(
        r'<div\s+class="navbar\s+navbar-inverse[^"]*"[^>]*>.*?<!--/\.nav-collapse\s*-->\s*</div>\s*</div>',
        NEW_NAV,
        html,
        count=1,
        flags=re.DOTALL
    )

    # 5. Replace old footer
    footer_start = html.find('<div id="footer">')
    if footer_start != -1:
        # Find the first script/comment block that follows the footer
        after_footer = html.find('<!-- Bootstrap core JavaScript', footer_start)
        if after_footer == -1:
            after_footer = html.find('<script src="../assets/js/bootstrap', footer_start)
        if after_footer == -1:
            after_footer = html.find('<!-- dynamically load mathjax', footer_start)
        if after_footer != -1:
            segment   = html[footer_start:after_footer]
            last_div  = segment.rfind('</div>')
            footer_end = footer_start + last_div + len('</div>')
            html = html[:footer_start] + NEW_FOOTER + html[footer_end:]
        else:
            print(f'    WARNING: could not locate end of footer in {slug}')
    else:
        print(f'    WARNING: no footer found in {slug}')

    print(f'  Writing  {slug}_full_version.html…')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  Done     ({os.path.getsize(dst) // 1024}KB)\n')

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f'Transforming {len(PROJECTS)} notebooks → v3/\n')
    for slug in PROJECTS:
        transform(slug)
    print('All done.')
