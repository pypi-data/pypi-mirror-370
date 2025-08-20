import json
import os


PROVIDERS_MODELS = {
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4.1-nano",
        "gpt-4.1-mini",
        "gpt-4.1",
        #"gpt-o3",
        #"gpt-o4-mini",
        #"gpt-o4-mini-high",
    ],
    "google": [
        "gemma-3n-e4b-it",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ],
    "xai": [
        "grok-3-mini-fast",
        "grok-3-mini",
        "grok-3",
    ],
    "deepseek": [
        "deepseek-chat",
    ],
}

PURPOSE_TAGS = [
    "chat",
    "code",
    "sentiment",
    "analytics",
    "summary"  
]

EMBEDDING_MODELS = {
    "openai": [
    "text-embedding-3-small",
    "text-embedding-3-large",
    ]
}


# Read-only model descriptions for LLM-profile builder
# -----------------------------------------------------------------------------
MODEL_DESCRIPTIONS = {
    # OpenAI
    "gpt-4o-mini":"Cost-efficient multimodal; $0.15/1M input, $0.60/1M output. Ideal for prototyping vision+text apps on a budget.",
    "gpt-4o":"Multimodal powerhouse; $5.00/1M input, $15.00/1M output. Best for high-fidelity chat, complex reasoning & image tasks.",
    "gpt-4.1-nano":"Ultra-fast low-cost (1M-token); $0.10/1M in, $0.40/1M out. Perfect for high-throughput, low-latency tasks.",
    "gpt-4.1-mini":"Balanced speed/intel (1M-token context); $0.40/1M in, $1.60/1M out. Great for apps needing wide context at moderate cost.",
    "gpt-4.1":"Top general-purpose (1M-token context); $2.00/1M in, $8.00/1M out. Excels at large-doc comprehension, coding, reasoning.",
    "gpt-o3":"High-accuracy reasoning (200K-token); $2.00/1M in, $8.00/1M out. Best for math, code gen, structured data outputs.",
    "gpt-o4-mini":"Fast lean reasoning (200K-token); $1.10/1M in, $4.40/1M out. Ideal for vision+code when o3 is overkill.",
    "gpt-o4-mini-high":"Enhanced mini-engine; $2.50/1M in (est.), $10.00/1M out (est.). Suited for interactive assistants with visual reasoning.",

    # Google
    "gemma-3n-e4b-it":"""Gemma is free.
      Best for:         Use case:  
      - Low latency   | - Visual and text processing 
      - Multilingual  | - Text translation
      - Summarization | - Summarizing text research content
    """,
    "gemini-2.0-flash-lite":"""$0.075 In, $0.30 Out. CoD: Aug 2024"
      Best for:              Use case: 
      - Long Context       | - rocess 10,000 lines of code
      - Realtime streaming | - Call tools natively
      - Native tool use    | - Stream images and video in realtime
    """,
    "gemini-2.0-flash": """$0.10 In, $0.40 Out. CoD: Aug 2024
      Best for:                    Use case:
      - Multimodal understanding | - Process 10,000 lines of code
      - Realtime streaming       | - Call tools natively, like Search
      - Native tool use          | - Stream images & vids in R time  
    """,
    "gemini-2.5-flash-lite": """($0.10 In, $0.40 Out)/1M (est.) CoD: Jan 2025.
      Best for:                        Use case:
      - Large scale processing         - Data transformation
      - Low latency, high volume       - Translation
          tasks with thinking          - Summarizationt
    """,
    "gemini-2.5-flash":"""$0.30. $2.50 Out CoD: Jan 2024.
      Best for:                           Use case:
      - Large scale processing            - Reason over complex problems
      - Low latency, high volume tasks    - Show thinking process
      - Agentic use cases                 - Call tools natively
    """,
    "gemini-2.5-pro":"""$3.00 In /1M (est.). Advanced analytics, detailed reports & multi-step reasoning.
        Best for:
        - Coding
        - Reasoning
        - Multimodal understanding
        Use case:
        - Reason over complex problems
        - Tackle difficult code, math and STEM problems
        - Use the long context for analyzing large datasets, codebases or documents
    """,

    # XAI
    "grok-3-mini-fast":"$0.20/1M (est.). Ultra-low latency chat, real-time monitoring & streaming apps.",
    "grok-3-mini":"$0.40/1M (est.). Budget-friendly chat & assistant tasks with good accuracy.",
    "grok-3":"$1.00/1M (est.). General-purpose chat & content gen with balanced speed/quality.",
    "grok-4":"$2.00/1M (est.). High-accuracy reasoning, code gen & long-form content creation.",

    # DeepSeek
    "deepseek-chat":"DeepSeek Chat; $1.20/1M (est.). Optimized for private-data Q&A, enterprise search & document ingestion.",
}

