
import re as _re
import json as _json
from urllib.parse import urlparse
from . import profiles as _prof

__all__ = ["generate_page_html"]


_profile = {}

_SMX_RUNTIME_GUARD = '''
<script>
(function(){
  if (window.ReactDOM && ReactDOM.createRoot) {
    const _cr = ReactDOM.createRoot;
    ReactDOM.createRoot = function(container){
      if (container === document.body || container === document.documentElement){
        console.warn("SMX: Redirected React root from <body>/<html> to #smx-react-root");
        let host = document.getElementById('smx-react-root');
        if (!host){ host = document.createElement('div'); host.id='smx-react-root'; document.body.appendChild(host); }
        return _cr.call(this, host);
      }
      return _cr.call(this, container);
    };
  }
})();
</script>
'''.strip()

_SMX_FADEIN_CSS = '''
<style>
.smx-fade{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease;}
.smx-in{opacity:1;transform:none;}
@media (prefers-reduced-motion: reduce){.smx-fade{transition:none;transform:none;opacity:1;}}
</style>
'''.strip()

_SMX_LAYOUT_CSS = '''
<style>
.smx-hero{max-width:1200px;margin:0 auto;padding:clamp(1.5rem,3vw,2.5rem);}
.smx-hero .smx-img{aspect-ratio:16/9;width:100%;max-height:min(56vh,560px);object-fit:cover;border-radius:1rem;}
.smx-card{border-radius:1rem;box-shadow:0 6px 20px rgba(2,6,23,0.06);}
#smx-root,[id^="smx-"]{margin-top:clamp(16px,2vw,32px);margin-bottom:clamp(24px,3vw,48px);padding-inline:clamp(12px,2vw,24px);}
#smx-root .smx-container,[id^="smx-"] .smx-container{max-width:1200px;margin-inline:auto;}
</style>
'''.strip()

def smx_strip_fences(html: str) -> str:
    s = (html or '').strip()
    m = _re.match(r"^```[a-zA-Z0-9_-]*\s*(.*?)\s*```$", s, _re.S)
    if m:
        return m.group(1)
    return s.replace("```html", "").replace("```HTML", "").replace("```", "")

def smx_validate_html(html: str):
    errs = []
    if _re.search(r"ReactDOM\.createRoot\(\s*document\.(body|documentElement)\s*\)", html):
        errs.append("Do not mount React to <body> or <html>. Use #smx-react-root.")
    if _re.search(r"document\.write\s*\(", html, _re.I):
        errs.append("document.write is not allowed after initial load.")
    if _re.search(r"document\.body\.innerHTML\s*=", html):
        errs.append("Do not overwrite body.innerHTML.")
    if (("react-dom" in html) or ("ReactDOM" in html)) and ('id=\"smx-react-root\"' not in html):
        errs.append('Missing <div id=\"smx-react-root\"></div> for React mounting.')
    return errs

def smx_autofix_html(html: str) -> str:
    inject = _SMX_FADEIN_CSS + "\n" + _SMX_LAYOUT_CSS
    if ("react-dom" in html or "ReactDOM" in html) and ('id=\"smx-react-root\"' not in html):
        html = html.replace("</body>", '<div id=\"smx-react-root\"></div>\n</body>')
    html = _re.sub(
        r"ReactDOM\.createRoot\(\s*document\.(body|documentElement)\s*\)",
        'ReactDOM.createRoot(document.getElementById(\"smx-react-root\"))',
        html
    )
    if "</body>" in html:
        return html.replace("</body>", f"{inject}\n{_SMX_RUNTIME_GUARD}\n</body>")
    return f"{inject}\n{_SMX_RUNTIME_GUARD}\n{html}"

def _normalise_img_src(url: str) -> str:
    try:
        from urllib.parse import urlparse as _up
        u = _up(url)
        return (u.netloc.lower() + u.path).rstrip('/')
    except Exception:
        return url or ""

def smx_dedupe_images(html: str) -> str:
    img_pat = _re.compile(r'<img\b[^>]*\bsrc\s*=\s*([\'"])(.*?)\1[^>]*>', _re.I)
    fb_pat  = _re.compile(r'\bdata-fallbacks\s*=\s*([\'"])(.*?)\1', _re.I | _re.S)

    parts, last_end, seen_norm, unique_count = [], 0, set(), 0

    def _replace_src(tag: str, old: str, new: str) -> str:
        return _re.sub(r'(\bsrc\s*=\s*[\'"])' + _re.escape(old) + r'([\'"])', r"\1" + new + r"\2", tag, count=1)

    for m in img_pat.finditer(html):
        parts.append(html[last_end:m.start()])
        tag = m.group(0)
        src_val = m.group(2).strip()
        norm = _normalise_img_src(src_val)

        if norm in seen_norm:
            fb_m = fb_pat.search(tag)
            chosen = None
            if fb_m:
                try:
                    cands = _json.loads(fb_m.group(2).replace("&quot;", '"').replace("&apos;", "'"))
                    for cand in cands:
                        if isinstance(cand, str) and _normalise_img_src(cand) not in seen_norm:
                            chosen = cand; break
                except Exception:
                    chosen = None
            if not chosen:
                unique_count += 1
                chosen = f"https://picsum.photos/seed/smx-{unique_count}/1200/700"
            tag = _replace_src(tag, src_val, chosen)
            seen_norm.add(_normalise_img_src(chosen))
        else:
            seen_norm.add(norm)

        parts.append(tag)
        last_end = m.end()

    parts.append(html[last_end:])
    return "".join(parts)

def smx_ensure_min_images(html: str, min_images: int = 5) -> str:
    if not _re.search(r'<section[^>]+id=["\']smx-[^"\']+["\']', html, _re.I):
        return html
    if len(list(_re.finditer(r'<img\b', html, _re.I))) >= min_images:
        return html

    needed = min_images - len(list(_re.finditer(r'<img\b', html, _re.I)))
    figs = []
    for i in range(1, needed + 1):
        seed = f"smx-gallery-{i}"
        figs.append(f'''
        <figure class="smx-figure smx-fade">
          <img class="smx-img"
               src="https://picsum.photos/seed/{seed}/1200/700"
               data-fallbacks='["https://picsum.photos/seed/{seed}-alt/1200/700",
                                "data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%271200%27 height=%27700%27%3E%3Crect fill=%27%23eef2f7%27 width=%27100%25%27 height=%27100%25%27/%3E%3Ctext x=%2750%25%27 y=%2750%25%27 dominant-baseline=%27middle%27 text-anchor=%27middle%27 fill=%27%23677%27 font-size=%2732%27%3EImage%20Placeholder%3C/text%3E%3C/svg%3E"]'
               alt="Gallery image {i}">
        </figure>
        '''.strip())

    gallery = f'''
    <section class="smx-gallery smx-container" aria-label="Image Gallery">
      <div class="smx-grid">
        {' '.join(figs)}
      </div>
    </section>
    '''.strip()

    return _re.sub(r'(</section>\s*)', gallery + r'\1', html, count=1, flags=_re.I)

def smx_inject_card_icons(html: str) -> str:
    def _add_icon(match):
        card = match.group(0)
        if _re.search(r'<svg\b', card):
            return card
        svg = ('<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" '
               'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
               'style="margin-right:8px;vertical-align:-2px;"><path d="M12 2l7 4v6c0 5-3.5 9-7 10-3.5-1-7-5-7-10V6l7-4z"/></svg>')
        return _re.sub(r'(<h3\b[^>]*>)', r'\1' + svg, card, count=1)
    
    pattern = _re.compile(r'<(?:div|article)\b[^>]*\bclass=["\'][^"\']*smx-card[^"\']*["\'][^>]*>.*?</(?:div|article)>', _re.I | _re.S)
    return pattern.sub(_add_icon, html)

def smx_lightboxify(html: str) -> str:
    def _wrap(fig):
        tag = fig.group(0)
        if _re.search(r'</a>\s*</figure>\s*$', tag, _re.S):
            return tag
        src_m = _re.search(r'src=([\'"])(.*?)\1', tag, _re.I)
        alt_m = _re.search(r'alt=([\'"])(.*?)\1', tag, _re.I)
        if not src_m:
            return tag
        src = src_m.group(2)
        alt = alt_m.group(2) if alt_m else ""
        return _re.sub(r'(<img\b[^>]*>)', f'<a href="{src}" data-glightbox="title: {alt}">\\1</a>', tag, count=1)
    pattern = _re.compile(r'<figure\b[^>]*class=["\'][^"\']*smx-figure[^"\']*["\'][^>]*>.*?</figure>', _re.I | _re_S)
    return pattern.sub(_wrap, html)

def smx_inject_extras(html: str, slug: str, extras: list) -> str:
    extras = extras or []
    tags = []
    if "aos" in extras:
        tags += [
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css">',
            '<script src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"></script>',
        ]
    if "embla" in extras:
        tags += ['<script src="https://cdn.jsdelivr.net/npm/embla-carousel@8.1.6/embla.umd.js"></script>']
    if "glightbox" in extras:
        tags += [
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/glightbox/dist/css/glightbox.min.css">',
            '<script src="https://cdn.jsdelivr.net/npm/glightbox/dist/js/glightbox.min.js"></script>',
        ]

    init_template = '''
    <script>(function(){
        var root = document.getElementById("__SLUG__"); if(!root) return;
        if (window.AOS) {
            root.querySelectorAll('.smx-fade').forEach(function(el){ el.setAttribute('data-aos','fade-up'); });
            AOS.init({ disableMutationObserver: true, once: true, startEvent: 'smx:ready' });
        }
        if (window.GLightbox) { GLightbox({ selector: '#__SLUG__ [data-glightbox]' }); }
        if (window.EmblaCarousel) {
            root.querySelectorAll('.smx-carousel .smx-carousel__viewport').forEach(function(view){
            try { EmblaCarousel(view, { loop:true, align:'start' }); } catch(e){ console.warn('SMX Embla', e); }
            });
        }
        document.dispatchEvent(new Event('smx:ready'));
        })();
    </script>
    '''.strip().replace("__SLUG__", slug)

    payload = "\n".join(tags + [init_template])
    if "</body>" in html:
        return html.replace("</body>", payload + "\n</body>")
    return html + payload

PROMPT_RULES = '''
Non-negotiable Output Contract
- Return only HTML that can be inserted inside an existing <main> element.
- Do not include <!doctype>, <html>, <head>, or <body>.
- Do not include triple backticks, code fences, YAML, or explanations of any kind.
- No global resets; never style html, body, * selectors.
- Scope all styles and scripts to a single top-level container: <section id="smx-{{slug}}" class="smx">...</section>
  where {{slug}} is a kebab-case version of the page title.
- Include JavaScript, it must be vanilla JS and must only affect elements inside #smx-{{slug}}.

Design & Structure
- Your entire design MUST be fully responsive: desktop and mobile.
- Build a hero with a contained banner: image must have rounded corners, aspect-ratio ≈16:9, and max-height ≤ 56vh.
- Place hero text beside or above the image for good balance; ensure readable contrast.
- Add 4-6 rich content blocks (feature grid, highlights, updates). Maintain heading order.
- Use semantic HTML (sections, subsections articles, figures, h2-h4) and accessible labelling (aria-*, meaningful alt).
- Avoid heavy frameworks. If utility classes appear, also provide a small scoped CSS fallback.

Styling Rules (scoped)
- Add a <style> block inside the returned HTML. Prefix every selector with #smx-{{slug}}.
- Provide CSS variables on #smx-{{slug}}: --smx-primary, --smx-secondary, --smx-bg, --smx-fg.
- Include a tiny fade-in reveal: elements with .smx-fade start hidden and animate into view.
- Decide and animate which ever other area/feature you want. 

Images & Asset Reliability
- For each important image, provide multiple candidates via data-fallbacks AND a safe default src.
- Never leave src empty. Avoid dead links.
- If an image fails to load, the inline script must try the next URL from data-fallbacks.
- Provide descriptive alt text; decorative images may use alt="" and role="presentation".
- Do not reuse the same image URL (ignoring querystrings) twice on the same page.
- Aim for at least five total images across hero, feature cards, highlight, or an extra gallery.
'''.strip()

PROMPT_REQUIRED_SCRIPT = '''
Required Fallback Script (place once, scoped to #smx-{{slug}}; no fences)
<script>(function(){
  const root = document.querySelector('#smx-{{slug}}'); if(!root) return;
  root.querySelectorAll('img[data-fallbacks]').forEach(img=>{
    const list = (()=>{try{return JSON.parse(img.getAttribute('data-fallbacks'));}catch{return [];}})();
    let i=0; img.addEventListener('error', function onErr(){ if(i<list.length){img.src=list[i++];} else {img.removeEventListener('error', onErr);} });
  });
  const IO = 'IntersectionObserver' in window ? new IntersectionObserver(es=>{
    es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('smx-in'); IO.unobserve(e.target); } });
  },{rootMargin:'-5% 0px'}) : null;
  if(IO){ root.querySelectorAll('.smx-fade').forEach(el=>IO.observe(el)); }
  else { root.querySelectorAll('.smx-fade').forEach(el=>el.classList.add('smx-in')); }
})();</script>
'''.strip()

PROMPT_SCOPED_CSS = '''
Scoped CSS (place in same HTML; no fences)
<style>
  #smx-{{slug}} {
    --smx-primary: __PRIMARY__;
    --smx-secondary: __SECONDARY__;
    --smx-bg:#ffffff; --smx-fg:#0f172a; color:var(--smx-fg); background:var(--smx-bg);
  }
  #smx-{{slug}} .smx-hero { border-radius:1.25rem; padding:clamp(2rem,4vw,4rem); background:linear-gradient(135deg,var(--smx-primary),var(--smx-secondary)); color:#fff; }
  #smx-{{slug}} .smx-grid { display:grid; gap:clamp(1rem,2vw,2rem); grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); }
  #smx-{{slug}} .smx-card { background:#fff; border:1px solid #e5e7eb; border-radius:1rem; padding:1.25rem; box-shadow:0 6px 20px rgba(2,6,23,0.06); }
  #smx-{{slug}} .smx-figure { margin:0; }
  #smx-{{slug}} .smx-img { width:100%; height:auto; display:block; border-radius:.75rem; object-fit:cover; }
  #smx-{{slug}} .smx-cta { display:inline-block; padding:.8rem 1.2rem; border-radius:.8rem; background:#fff; color:var(--smx-primary); font-weight:600; text-decoration:none; }
  #smx-{{slug}} .smx-fade { opacity:0; transform: translateY(14px); transition: opacity .6s ease, transform .6s ease; }
  #smx-{{slug}} .smx-in   { opacity:1; transform:none; }
  @media (prefers-reduced-motion: reduce){ #smx-{{slug}} .smx-fade { transition:none; transform:none; opacity:1; } }
</style>
'''.strip()

def _build_prompt(page_title: str, website_description: str, brand_primary: str = "", brand_secondary: str = "") -> str:
    primary = (brand_primary or "#2563eb").strip()
    secondary = (brand_secondary or "#14b8a6").strip()

    header = (
        "You generate a modern, responsive, accessible content section to be embedded into an existing website.\n"
        "The host site already provides navbar, footer, and global CSS. Your output must be RAW HTML only\n"
        "(to be placed inside <main>), with its own SCOPED styles and tiny vanilla JS. Use UK English.\n\n"
        f"Inputs\n- Page Title: {page_title}\n- Website Mission/Vision/Goals: {website_description}\n"
        f"- Optional brand colours: primary '{primary}', secondary '{secondary}'\n\n"
    )

    content_requirements = '''
        Content to Produce inside #smx-{{slug}}
        1) Hero with balanced layout (text + contained image), one .smx-cta, and a hero image using the fallback pattern.
        2) Feature grid (3-4 cards) describing capabilities or topics.
        3) Highlight/Showcase section with one image and supporting text.
        4) Updates/testimonials.
        Headings must be in logical order (no skipping levels).

        Final step
        - Validate your HTML mentally; ensure no triple backticks or extra prose.
        - Output only the HTML for <section id="smx-{{slug}}" class="smx">…</section>.
    '''.strip()

    prompt = header + PROMPT_RULES + "\n\n" + PROMPT_REQUIRED_SCRIPT + "\n\n" + PROMPT_SCOPED_CSS + "\n\n" + content_requirements
    prompt = prompt.replace("__PRIMARY__", primary).replace("__SECONDARY__", secondary)
    return prompt

def google_generate_code(client, model, instructions):
    response = client.models.generate_content(
        model=model,
        contents=instructions
    )
    return response.text.strip()

def gpt_models_latest_generate_code(client, model, instructions):
    response = client.responses.create(
        model=model,
        input=instructions,
        reasoning={ "effort": "low" },
        text={ "verbosity": "medium", },
    )
    return response.output_text.strip()

def openai_sdk_generate_code(client, model, instructions):
    try:
        response = client.chat.completions.create(
            model=model, 
            contents=[
                {"role": "system", "content": "You are a senior web developer tasked with creating a single-file responsive webpage."},
                {"role": "user", "content": instructions}
            ],
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating webpage: {str(e)}"



def generate_page_html1(page_title:str,website_description:str,brand_primary:str="",brand_secondary:str="",extras=None)->str:
    prof = _profile
    if not prof:
        return "No profile to generate page"

    _client = _prof.get_client(_profile)
    _model = _profile["model"]
    
    try:
        prompt = _build_prompt(page_title, website_description, brand_primary, brand_secondary)
        resp = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": "You are a senior front-end engineer creating an embedded content section. Follow the instructions exactly."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=4096,
        )
        html = smx_strip_fences(resp.choices[0].message.content or "")

        _ = smx_validate_html(html)
        html = smx_autofix_html(html)
        html = smx_dedupe_images(html)
        html = smx_ensure_min_images(html, min_images=5)

        try:
            html = smx_inject_card_icons(html)
        except Exception:
            pass

        if extras:
            m = _re.search(r'<section[^>]+id=["\'](smx-[^"\']+)["\']', html, _re.I)
            slug = m.group(1) if m else "smx-root"
            if "glightbox" in extras:
                html = smx_lightboxify(html)
            html = smx_inject_extras(html, slug, extras)

        return html
    except Exception as e:
        return f"Error generating webpage: {e}"


def generate_page_html2(page_title: str, website_description: str) -> str:

    prof = _profile
    if not prof:
        return "No profile to generate page"

    client = _prof.get_client(_profile)
    model = _profile["model"]

    prompt = f"""
        Generate the webpage following the guidelines given, ensuring images are sourced also.
        The output must be a single HTML file containing all HTML, CSS (using Tailwind CSS via CDN), and JavaScript (using React via CDN) with no external dependencies beyond CDNs. The page must reflect the essence of the page title in relation to the website's objectives, include a hero section and subsections, and use free, high-quality images from Unsplash or Pexels (licensed for commercial use). Ensure animations (e.g., fade-ins, hover effects) are included, and the design is responsive for all devices. Do not include headers or footers, as they are provisioned by the website. Avoid variable names that might clash with existing ones (e.g., use unique names like 'heroSection', 'subSectionContent'). Follow these guidelines:\n

        **Input**
        - Page Title: {page_title}\n
        - Website Objectives: {website_description}\n\n

        **Instructions**:
        1.  **Output Format**: The entire output must be a single HTML file. Include all CSS and JavaScript within the HTML file using `<style>` and `<script>` tags.
        2.  **Modern Design**: Use a modern, vibrant, and professional design. The layout should be clean and visually appealing.
        3.  **Responsive**: The page must be fully responsive and work on desktop, tablet, and mobile devices. Use media queries to ensure proper display on all screen sizes. [15]
        4.  **Dynamic and Animated**: Incorporate subtle animations and transitions (e.g., fade-ins on scroll, hover effects) to make the page dynamic and engaging.
        5.  **Content Structure**:
            *   **Hero Section**: A prominent introductory section with a compelling headline, a brief description, and a call-to-action button.
            *   **Main Content**: Subsections that elaborate on the page's topic. For an "About" page, this could include a mission, vision, and team section. For a "Services" page, it should list the services with descriptions. Improvise and create placeholder content if not enough information is provided in the objectives.
            *   **No Header/Footer**: Do not include `<header>` or `<footer>` tags as these are assumed to be provided by the website where this page will be embedded.
        6.  **Images**:
            *   Source high-quality, royalty-free images from Unsplash or Pexels.
            *   Use appropriate placeholder image URLs directly in the `src` attributes of the `<img>` tags. For example: `https://images.unsplash.com/photo-12345?q=80&w=1920...`
            *   Ensure images are relevant to the content and theme of the website.
        7.  **Code Style**:
            *   Use HTML5 semantic tags (`<section>`, `<article>`, etc.). [14]
            *   For styling, you can use inline CSS or a `<style>` block. You can also use a CSS framework like Tailwind CSS via a CDN link.
            *   For JavaScript, ensure variable and function names are unique to avoid conflicts with existing scripts on the website (e.g., use a unique prefix like `myUniquePage_`).
            *   Include CDN links for any external libraries if necessary (e.g., React, though vanilla JS is preferred for simplicity). [1]
        8.  **Review and Refine**: 
            Before generating the final code, mentally review the requirements to ensure the output will be high-quality, functional, and visually appealing.
        9   Your code must begin with the <html> and closes with </tml> tag. 
            Do not include and preamble, no comments or profix. No trailing backticks. All content must be inside the html tags.
            You must return just the html code.

        **Output Format**
        Return only the complete HTML content as a string, wrapped in triple backticks (```), with no additional explanation or comments outside the HTML code. Ensure the HTML includes all necessary scripts, styles, and JSX components.

        ```
        <!-- Complete HTML content here -->
        ```
    """
    try:
        # API call to OpenAI's chat completions endpoint [4, 9]
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior web developer tasked with creating a single-file responsive webpage."},
                {"role": "user", "content": prompt}
            ]
        )

        if chat_completion.choices:
            html_content = chat_completion.choices[0].message.content.strip() 

            return html_content
        else:
            return "Error: Unable to generate a response from the API."

    except Exception as e:
        return f"An error occurred: {e}"


def generate_page_html(page_title, website_description):
    global _profile
    if not _profile:
        profile = _prof.get_profile("coding") or _prof.get_profile("admin") 
        if not profile:
            return
        _profile = profile

    ai_code_id = f" You are a senior web developer tasked with creating a single-file responsive webpage. "
    instructions = f"""
    Generate the webpage following the guidelines given, ensuring images are sourced also.
    The output must be a single HTML file containing all HTML, CSS (using Tailwind CSS via CDN), and JavaScript (using React via CDN) with no external dependencies beyond CDNs. The page must reflect the essence of the page title in relation to the website's objectives, include a hero section and subsections, and use free, high-quality images from Unsplash or Pexels (licensed for commercial use). Ensure animations (e.g., fade-ins, hover effects) are included, and the design is responsive for all devices. Do not include headers or footers, as they are provisioned by the website. Avoid variable names that might clash with existing ones (e.g., use unique names like 'heroSection', 'subSectionContent'). Follow these guidelines:\n

    **Input**
    - Page title: {page_title}
    - Website description: {website_description}

        **Requirements**
    - Never mount React to document.body or document.documentElement; mount only to <div id="smx-react-root"></div>.
    - Include <div id="smx-react-root"></div> if React/ReactDOM are used.
    - Prefer vanilla JS for simple effects (scroll/hover). If you use React, mount via createRoot(document.getElementById('smx-react-root')).
    - Do not call document.write() or overwrite document.body.innerHTML.
    - Start elements with class .fade-in hidden (opacity:0, translateY(20px)) and reveal with transitions.

    **Requirements**
        - Create a single HTML file with embedded React 
        - Use JSX via:
            CDN: (https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js and https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js) 
            Babel: (https://cdn.jsdelivr.net/npm/@babel/standalone@7.20.6/babel.min.js)
            Tailwind CSS: (https://cdn.tailwindcss.com).
        - Structure the page with a hero section (prominent headline, description, call-to-action) and subsections relevant to the page title and objectives.
        - Use modern JavaScript syntax and JSX for reusable components (e.g., HeroComponent, SectionComponent, SubSectionComponent).
        - Ensure the design is vibrant, professional, and consistent with the website's theme (infer theme from objectives, e.g., calming colors for health-related sites).
        - Include animations (e.g., fade-ins using Tailwind or JavaScript) without overwhelming the page.
        - Source images from Unsplash and/or Pexels, and place them appropriately (e.g., hero section background, subsection images).
        - Ensure responsiveness using Tailwind's responsive classes (e.g., sm:, md:, lg:).
        - Avoid <form> onSubmit due to sandbox restrictions; use buttons with click handlers instead.
        - Use className instead of class in JSX.
        - Verify the code is complete, functional, and ready to be saved as an HTML file and viewed in a browser.
        
        Now, for this page title: {page_title}\n, generate html content that aligns with the given website description:\n 
            {website_description}.\n\n

        **Output Format**
        Return only the complete HTML content as a string, with no additional explanation or comments outside the HTML code. Ensure the HTML includes all necessary scripts, styles, and JSX components.
    """

    from syntaxmatrix.settings import model_map as mm, prompts

    _client = _prof.get_client(_profile)
    _provider = _profile["provider"]
    _model = _profile["model"]
    
    html_content = ""

    def google_generate_code():
        response = _client.models.generate_content(
            model=_model, 
            contents=f"{ai_code_id}\n\n{instructions}\n\n"  
        )
        return response.text

    def gpt_models_latest_generate_code(reasoning_effort = "medium", verbosity = "medium"):
        from syntaxmatrix.gpt_models_latest import extract_output_text as _out, set_args
        try:                 
            args = set_args(
                model=_model,
                instructions=ai_code_id,
                input=instructions,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
            )
        
            resp = _client.responses.create(**args)
            code = _out(resp)
            return code
        except Exception as e:
            return f"Error!"

    def openai_sdk_generate_code():
        try:
            response = _client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": ai_code_id},
                    {"role": "user", "content": instructions},
                    ],
                temperature=0.0,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error!"

    if _provider == "google":
        return google_generate_code()
    elif _model in mm.GPT_MODELS_LATEST:
        return gpt_models_latest_generate_code()
    else:
        return openai_sdk_generate_code()
