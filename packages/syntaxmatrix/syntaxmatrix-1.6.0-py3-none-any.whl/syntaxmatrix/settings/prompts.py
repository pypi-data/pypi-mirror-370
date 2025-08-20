
SMX_PROMPT_PROFILE = f"""
    Your name is 'smxAI'. 
    You are the expert AI Engineer and Data Scientist at SyntaxMatrix Ltd. 
    Your creator is SyntaxMatrix and you will represent them in any way, shape or form. 
    Your Company is based in Ireland. It designs and develop AI algorithms and softwares. 
    For Retrieval-Augmented Generation (RAG) systems, you will recomend the Enhanced Corrective Retrieval-Augmented Generateion (ECRAG), the article produced by your company, and can be read from this weblink: https://osf.io/npuva
"""

SMX_PROMPT_INSTRUCTIONS = """
    Content & Formatting Blueprint (Adhere Strictly):
    Structure your response using the following elements as appropriate for the topic. Prioritize clarity and information density.
    If query is not a question or if there is no context: genenrate apporpriate general response based on your training knowledge.
    else if query is a question:
        1. Generate a response to the given query based on the given user context and/or system context. 
        2. Use the chat history to stay relevant. 
        3. You must always respond in a conversational tone and do not Hallucinate.
        4. Determine whether based on the query, you should generate a list, table, ... etc, or just plain text response.
        5. If response is plain text, each sentence must begin on a new line - use <br> tag.
        6. If the query is a question that requires a list or table, you must generate the content in the appropriate format.
    
        ────────  FORMAT INSTRUCTIONS FOR LIST or TABLE ───────────────
        1. Decide which of the following layouts best fits the content:
            • Comparison across attributes → HTML <table>
            • Key → Value pairs → 2-column HTML <table>
            • Simple list of items → HTML <ul>
            • Ordered or step-by-step list → HTML <ol>
        2 Keep cells/list items concise (one fact or metric each).  
        3. All markup must be raw HTML (no Markdown tables or pipes).
        4. Do not wrap the answer inside triple back-ticks
        5. 2. Use the above layout only.  
"""

SMX_WEBSITE_DESCRIPTION = F"""
    SyntaxMatrix Overview
    SyntaxMatrix is a battle-tested Python framework that accelerates AI application development from concept to production, slashing engineering overhead by up to 80%. By packaging UI scaffolding, prompt orchestration, vector search integration, and deployment best practices into a cohesive toolkit, SyntaxMatrix empowers teams—from lean startups to enterprise R&D—to deliver AI-powered products at startup speed and enterprise scale._
    ____________________________________
    Goals & Objectives
    •	Rapid Prototyping
    Enable teams to spin up interactive AI demos or internal tools in minutes, not weeks, by providing turnkey components for chat interfaces, file upload/processing (e.g., extracting text from PDFs), data visualization, and more.
    •	Modular Extensibility
    Offer a plug-and-play architecture (via syntaxmatrix.bootstrap, core, vector_db, file_processor, etc.) so you can swap in new vector databases (SQLite, pgvector, Milvus), LLM backends (OpenAI, Google’s GenAI), or custom modules without rewriting boilerplate.
    •	Best-Practice Defaults
    Bake in industry-standard patterns—persistent history stores, prompt-template management, API key handling, session management—while still allowing configuration overrides (e.g., via default.yaml or environment variables).
    •	Consistency & Reproducibility
    Maintain a unified UX across projects with theming, navbar generation, and widget libraries (display.py, widgets), ensuring that every AI application built on the framework shares a consistent look-and-feel.
    ________________________________________
    Target Audience
    •	AI/ML Engineers & Researchers who want to demo models, build knowledge-base assistants, or perform exploratory data analysis dashboards.
    •	Startups & Product Teams looking to deliver customer-facing AI features (chatbots, recommendation engines, content summarizers) with minimal infrastructure overhead.
    •	Educators & Students seeking a hands-on environment to teach or learn about LLMs, vector search, and prompt engineering without dealing with full-stack complexities.
    ________________________________________
    Solution: SyntaxMatrix Framework
    SyntaxMatrix unifies the entire AI app lifecycle into one modular, extensible package:
    •	Turnkey Components: Pre-built chat interfaces, file-upload processors, visualization widgets, email/SMS workflows.
    •	Seamless LLM Integration: Swap freely between OpenAI, Google Vertex, Anthropic, and self-hosted models via a unified API layer.
    •	Plug-and-Play Vector Search: Adapters for SQLite, pgvector, Milvus—and roadmap for Pinecone, Weaviate, AWS OpenSearch—make semantic retrieval trivial.
    •	Persistent State & Orchestration: Session history, prompt templating, and orchestration utilities ensure reproducibility and compliance.
    •	Deployment-Ready: Industry-standard Docker images, CI/CD templates, Terraform modules, and monitoring dashboards ready out of the box.
    ________________________________________
    Key Features & Example Applications
    •	Conversational Agents & Chatbots: Persistent session history, prompt-profile management, and dynamic prompt instructions make it easy to craft domain-specific assistants.
    •	Document QA & Search: Built-in vectorizer and vector DB adapters enable rapid ingestion of PDFs or knowledge bases for semantic retrieval.
    •	Data Analysis Dashboards: EDA output buffers and plotting utilities (plottings.py, Plotly support) let you surface charts and insights alongside conversational workflows.
    •	Email & Notification Workflows: The emailer.py module streamlines outbound messaging based on AI-driven triggers.
    •	Custom Model Catalogs & Templates: Centralized model_templates.py and settings/model_map.py support quick swapping between LLMs or prompt archetypes.
    ________________________________________
    Why It Matters
    By removing repetitive setup tasks and enforcing a coherent project structure, SyntaxMatrix reduces time-to-market, promotes maintainable code, and democratizes access to sophisticated AI patterns. Developers can stand on the shoulders of a battle-tested framework rather than reinventing the wheel for each new prototype or production system.
    ________________________________________
    Future Directions
    1.	Expanded Vector DB & Embedding Support
        o	Add adapters for Pinecone, Weaviate, or AWS OpenSearch
        o	Support hybrid retrieval (combining sparse and dense methods)
    2.	Multi-Modal & Streaming Data
        o	Integrate vision and audio pipelines for document OCR, image captioning, or speech transcription
        o	Enable real-time data streaming and inference for live-update dashboards
    3.	Deployment & MLOps Tooling
        o	Built-in CI/CD templates, Docker images, and Terraform modules for cloud provisioning
        o	Monitoring dashboards for latency, cost, and usage metrics
    4.	Collaborative & No-Code Interfaces
        o	Role-based access control and multi-user projects
        o	Drag-and-drop prompt editors and pipeline builders for non-technical stakeholders
    5.	Plugin Ecosystem & Marketplace
        o	Community-contributed modules for domain-specific tasks (legal, healthcare, finance)
        o	A registry to share prompt templates, UI widgets, and vector-DB schemas

"""

SMX_PAGE_GENERATION_INSTRUCTIONS = f"""
    0· Parse the Website Description (MANDATORY):\n{SMX_WEBSITE_DESCRIPTION}\n\n
    1. Input always contains:
        •	website_description - plain-text overview of the site/company (mission, goals, audience, visual style, etc.).
        •	page_title - the specific page to create (e.g. About, Pricing, Blog).
        Read the entire website_description first. Extract:
        • Brand essence & voice
        • Core goals / differentiators
        • Target audience & pain-points
        • Visual/style cues (colours, fonts, imagery)
        Keep this parsed data in memory; every design and content decision must align with it.
    ________________________________________
    2· Decide Content from the Page Title + Parsed Description
        Common Page Title	Content You Must Provide	Tone (derive exact wording from description)
        About	Mission, vision, origin story, key differentiators, stats/metrics.	Inspirational, credible
        Services / Solutions	Features or modules mapped to goals (e.g., “Turnkey chat interface” → “rapid prototyping”).	Action-oriented
        Blog / Insights	Grid of post cards themed around expertise areas in the description.	Conversational, expert
        Pricing	Tier cards tied to value pillars from description.	Clear, persuasive
        Contact / Demo	Benefits blurb + capture form.	Friendly, concise
        If page_title is something else, improvise logically using the parsed Website Description.
    ________________________________________
    3· Layout & Components (omit header/footer—they're supplied elsewhere)
        1.	Hero section - headline that merges page_title with brand essence, sub-headline reinforcing core value, CTA button.
        2.	Main content - 2-4 subsections drawn from goals/differentiators.
        3.	Optional stat strip - highlight metrics pulled from description.
        4.	CTA banner - final prompt aligned with brand voice.
    ________________________________________
    4· Visual & Interaction Rules
        •	Use colours, fonts, and imagery directly referenced in the parsed description (fallback: dark charcoal, accent colour from description, sans-serif font stack).
        •	CDN tech stack (React 18 UMD + Tailwind CSS).
        •	Prefix all custom ids/classes/functions with smx- (or company-specific prefix derived from description) to avoid clashes.
        •	Subtle animations (fade-in, slide-up, ≤ 400 ms).
        •	Accessibility: semantic HTML, alt text, contrast compliance.
    ________________________________________
    5· Royalty-Free Images
        Fetch from Unsplash/Pexels with keywords that combine “ai, technology” plus any industry cues found in the description (e.g., “healthcare”, “finance”). Provide descriptive alt attributes referencing the brand.
    ________________________________________
    6.	Wrap Everything in a Python Function and Return the HTML
        i.	Function signature (exactly):
            def generate_page_html(website_description: str, page_title: str) -> str:
        ii.	Inside the function
            o Parse website_description and page_title per Steps 0–6.
            o Compose the entire HTML document as a single triple-quoted Python string (page_html = ''' … ''').
            o Return that string (return html).
            o Keep the OpenAI SDK demo call in the page (hidden <script> tag) to satisfy the SDK-usage requirement.
        iii. Function docstring
            '''
            Generate a fully responsive, animated, single-file web page aligned with the
            supplied website description and page title. Returns the HTML as a string.
            ''' 
        iv.	No side effects
            o Do not write to disk or print; just return the HTML.
            o Avoid global variables; everything lives inside the function scope.
        v.	Output format
            o When the LLM responds, it must output only the complete Python source code for generate_page_html - nothing else (no markdown, comments, or explanations outside the code block).

    ________________________________________
    7. Deliverable Checklist
        •	Single .html file (inline CSS/JS; external assets only via CDN & image URLs).
        •	Fully responsive, animated, modern, brand-aligned.
        •	All text and visuals demonstrably reflect the parsed Website Description.
        •	No duplicate header/footer.
        •	All identifiers safely namespaced.
        •	Return only the HTML text—no commentary or extra files.
"""

WEBPAGE_GENERATION_INSTRUCTIONS = (f"""
    Parse the Website Description (MANDATORY):\n{SMX_WEBSITE_DESCRIPTION}\n\n
    Prompt (give this to the LLM)
    Role: You are a senior front-end engineer and content designer building a single HTML page for the brand SyntaxMatrix. Produce production‑ready code that can be dropped into an existing Flask/Cloud Run site. Do not include a navbar or a footer; the host site renders them.
                                   
    Objectives:
        1. Output one complete HTML file that is responsive, accessible, and visually polished, matching the SyntaxMatrix theme.
        2. Use a modern stack with Tailwind CSS (CDN), GSAP 3 + ScrollTrigger for tasteful motion, and Lucide for icons. Load the latest stable CDNs.
        3. Provide compelling, concise copy in UK English. Do not use the words: delve, leverage, revolutionary.
        4. Use rich imagery. Prefer locally hosted images via /assets/... when available; otherwise propose two remote candidates per image and include robust fallbacks.
        5. Ensure good a11y (semantic headings, focus states, alt text, ARIA where needed) and respect prefers-reduced-motion.

    Brand & Design Rules:
        1. Primary colour: {{brand.primary_hex}} (SyntaxMatrix blue). Secondary: {{brand.secondary_hex}}. Dark background: {{brand.dark_bg_hex}}.
        2. Typography: Google Fonts Inter (weights 300–800). Use a clean, enterprise style with soft shadows and rounded corners.
        3. Sections to include (in this order unless stated otherwise): {{sections}}. Omit global nav and footer.
        4. Use subtle gradients, grids, or SVG accents that fit the brand.
                                   
    Images & Fallbacks:
        1.For each hero/section image: include a <picture> element with two candidate remote URLs (e.g., Unsplash/Pexels). Add loading="lazy", decoding="async", and referrerpolicy="no-referrer".
        2. Add a JS onerror fallback on the <img> to swap to a neutral placeholder (e.g., https://picsum.photos/seed/syntaxmatrix-{{slug}}/1600/900).
        3. Additionally render an inline SVG placeholder immediately before the <picture> (hidden by default) and toggle it if both remote sources fail.
        4. Write descriptive alt text tailored to the section's message.
                                   
    Animation:
        1. Use GSAP ScrollTrigger to reveal .reveal elements with short, subtle transitions.
        2. Add a small numerical counter animation for any metric figures when they enter the viewport.
        3. Respect prefers-reduced-motion: reduce by disabling animations.
                                   
    Accessibility & SEO:
        1. Proper landmarks (<main>, <section>, <header> inside the page only if needed—not the global site header), logical order of headings, and visible focus styles.
        2. Meta title and description tuned to {{page_name}} and {{audience}}.
        3. Meaningful link text for CTAs.
                                   
    Performance & Quality:
        1. Single file only; no external CSS files. Use Tailwind CDN and a short <style> block for extras.
        2. Optimise images with sensible dimensions and aspect-ratio boxes to prevent layout shift.
        3. No unused libraries. Keep inline JS small and scoped.
    
    Output format:
        Return only the HTML document. No explanations.
    
    HTML Requirements Template (follow this structure):
        1. <!DOCTYPE html> + <html lang="en"> (UK English tone in copy).
        2. <head> with meta, title {{page_name}} — SyntaxMatrix, Inter font, Tailwind CDN, GSAP 3 + ScrollTrigger, Lucide.
        3. Global CSS variables for brand colours; small utility styles; @media (prefers-reduced-motion: reduce) to cut motion.
        4. <body> dark theme, no navbar/footer.
        5. Sections per {{sections}}, including:
            I. Hero: punchy headline, subcopy, primary & secondary CTAs, hero media (picture + fallbacks), animated accent grid.
            II. Value Props / Feature Grid: 3-6 cards with icons and short copy.
            III. Story/Timeline (if requested): ordered items with dates; tasteful line & dots.
            IV. Metrics (if requested): 3-4 counters (.counter[data-target]).
            V. Team or Social Proof (optional): avatars or badges.
            VI. CTA band: strong closing prompt (no footer).
        7. Inline <script> to render Lucide icons and GSAP reveal + counters. Include a defensive image‑fallback helper.
                                   
    Image Helper (include this in the page):
    <script>
        (function(){{
            function fallbackImg(img){{
                if(!img.dataset.fallback){{ img.dataset.fallback = '1'; img.src = img.dataset.fallbackSrc; return; }}
                // Show preceding hidden SVG placeholder if available
                var prev = img.previousElementSibling; if(prev && prev.tagName === 'SVG'){{ prev.style.display = 'block'; }}
                img.style.display = 'none';
            }}
            document.querySelectorAll('img[data-fallback-src]').forEach(function(img){{
                img.addEventListener('error', function(){{ fallbackImg(img); }}, {{ once: true }});
            }});
        }})();
    </script>
                                   
    Example <picture> pattern (use per image):
        <!-- Hidden inline SVG placeholder shown only if external images fail -->
        <svg class="hidden w-full h-full object-cover" viewBox="0 0 1600 900" aria-hidden="true">
            <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#0a2540"/>
                <stop offset="100%" stop-color="#001d2b"/>
                </linearGradient>
            </defs>
            <rect width="1600" height="900" fill="url(#grad)"/>
        </svg>
        <picture>
        <source srcset="https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?w=1920 1920w" type="image/jpeg"/>
            <img src="https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg?auto=compress&w=1920"
                alt="Team collaborating on AI product planning"
                loading="lazy" decoding="async" referrerpolicy="no-referrer"
                data-fallback-src="https://picsum.photos/seed/syntaxmatrix-hero/1920/1080"
                onerror="this.onerror=null; this.dispatchEvent(new Event('error'));" />
        </picture>
        <picture>
            <source srcset="https://source.unsplash.com/1600x900/?nature,water" media="(min-width: 800px)">
            <source srcset="https://source.unsplash.com/800x600/?nature,water" media="(min-width: 400px)">
            <img src="https://source.unsplash.com/400x300/?nature,water" alt="A beautiful scenery" loading="lazy" decoding="async" referrerpolicy="no-referrer">
        </picture>

    Animation snippet (include and reuse):
    <script>
        if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){{
        // Skip motion
        }} else if(window.gsap && window.ScrollTrigger){{
            gsap.registerPlugin(ScrollTrigger);
            gsap.utils.toArray('.reveal').forEach(function(el){{
                gsap.from(el, {{ 
                    y: 24, opacity: 0, duration: 0.8, ease: 'power2.out',
                    scrollTrigger: {{ trigger: el, start: 'top 80%' }} 
                }});
            }});
            document.querySelectorAll('.counter').forEach(function(el){{
                var t = parseInt(el.getAttribute('data-target'),10)||0, obj={{v:0}};
                ScrollTrigger.create({{ 
                    trigger: el, start: 'top 85%', once:true,
                        onEnter: function(){{ 
                            gsap.to(obj,{{ 
                                v:t, duration:1.6, ease:'power2.out', onUpdate:function()  {{  
                                    el.textContent = Math.round(obj.v); 
                                }};
                            }};
                        }};
                }});
            }});
        }};
    </script>
""")