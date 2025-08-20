import os
from openai import OpenAI
from . import profiles as _prof


__all__ = ["generate_dynamic_page"]

profile = _prof.get_profile('code') or _prof.get_profile('analytics') or _prof.get_profile('chat')
if not profile:
    print("Error: setup a coder LLM")      
code_profile = profile

def generate_page_html1(page_title: str, website_description: str) -> str:

    client = _prof.get_client(code_profile)
    model = code_profile['model']

    prompt = f"""
        Generate the webpage following the guidelines given, ensuring images are sourced also.
        The output must be a single HTML file containing all HTML, CSS (using Tailwind CSS via CDN), and JavaScript (using React via CDN) with no external dependencies beyond CDNs. The page must reflect the essence of the page title in relation to the website's objectives, include a hero section and subsections, and use free, high-quality images from Unsplash or Pexels (licensed for commercial use). Ensure animations (e.g., fade-ins, hover effects) are included, and the design is responsive for all devices. Do not include headers or footers, as they are provisioned by the website. Avoid variable names that might clash with existing ones (e.g., use unique names like 'heroSection', 'subSectionContent'). Follow these guidelines:\n

        **Input**
        - Page Title: {page_title}\n
        - Website Objectives: {website_description}\n\n
            **Page Title**: {page_title}\n

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


def generate_page_html(page_title, website_objectives):

    client = _prof.get_client(code_profile)
    model = code_profile['model']

    prompt = f"""
    Generate the webpage following the guidelines given, ensuring images are sourced also.
    The output must be a single HTML file containing all HTML, CSS (using Tailwind CSS via CDN), and JavaScript (using React via CDN) with no external dependencies beyond CDNs. The page must reflect the essence of the page title in relation to the website's objectives, include a hero section and subsections, and use free, high-quality images from Unsplash or Pexels (licensed for commercial use). Ensure animations (e.g., fade-ins, hover effects) are included, and the design is responsive for all devices. Do not include headers or footers, as they are provisioned by the website. Avoid variable names that might clash with existing ones (e.g., use unique names like 'heroSection', 'subSectionContent'). Follow these guidelines:\n

    **Input**
    - Page Title: {page_title}\n
    - Website Objectives: {website_objectives}\n\n

    **Requirements**
    - Create a single HTML file with embedded React 
    - Use JSX via:
        CDN: (https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js and https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js) 
        Babel: (https://cdn.jsdelivr.net/npm/@babel/standalone@7.20.6/babel.min.js)
        Tailwind CSS: (https://cdn.tailwindcss.com).
    - Structure the page with a hero section (prominent headline, description, call-to-action) and subsections relevant to the page title and objectives.
    - Use modern JavaScript syntax and JSX for reusable components (e.g., HeroComponent, SubSectionComponent).
    - Ensure the design is vibrant, professional, and consistent with the website's theme (infer theme from objectives, e.g., calming colors for health-related sites).
    - Include animations (e.g., fade-ins using Tailwind or JavaScript) without overwhelming the page.
    - Source images from Unsplash and/or Pexels, and place them appropriately (e.g., hero section background, subsection images).
    - Ensure responsiveness using Tailwind's responsive classes (e.g., sm:, md:, lg:).
    - Avoid <form> onSubmit due to sandbox restrictions; use buttons with click handlers instead.
    - Use className instead of class in JSX.
    - Verify the code is complete, functional, and ready to be saved as an HTML file and viewed in a browser.
    - For the page title: {page_title}, generate content that aligns with the objectives: \n{website_objectives}.\n\n

    **Output Format**
    Return only the complete HTML content as a string, wrapped in triple backticks (```), with no additional explanation or comments outside the HTML code. Ensure the HTML includes all necessary scripts, styles, and JSX components.

    ```
    <!-- Complete HTML content here -->
    ```
    """

    try:
        response = client.chat.completions.create(
            model=model, 
            messages=[
                {"role": "system", "content": "You are a senior web developer tasked with creating a single-file responsive webpage."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.8
        )
        html_content = response.choices[0].message.content.strip()
        return html_content
    
    except Exception as e:
        return f"Error generating webpage: {str(e)}"
