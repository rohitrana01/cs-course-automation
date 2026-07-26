"""
modules/script_generator.py
Calls the Gemini or Anthropic Claude API to generate a structured 3rd-grade script
tailored to the configured NICHE — narration segments + chalkboard elements + diagrams + quizzes.
"""
import json
import re
import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, LLM_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, NICHE


def generate_script(topic: dict) -> dict:
    """
    Given a topic dict from curriculum.json, return structured script data for 3rd graders:
    {
      "video_title": str,
      "video_description": str,
      "tags": [str],
      "segments": [
        {
          "title": str,
          "narration": str,           # Kid-friendly explanation (~80-120 words)
          "character_pose": str,       # Character visual action (e.g. "excitedly pointing")
          "board_elements": [str],     # 2-3 short points/examples to draw on the board
          "diagram_prompt": str|null   # Description of a simple illustration sticker
        }
      ],
      "summary_points": [str],   # 3 key takeaways
      "quiz": [                  # 3 multiple choice questions for the CD-ROM portal
        {
          "question": str,
          "options": [str, str, str, str],
          "answer": int          # 0-indexed index of correct answer (0, 1, 2, or 3)
        }
      ],
      "next_topic": str          # Title of the next video
    }
    """
    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            print("[script_generator] GEMINI_API_KEY is not set. Using fallback script.")
            return _fallback_script(topic)
    else:
        if not ANTHROPIC_API_KEY:
            print("[script_generator] ANTHROPIC_API_KEY is not set. Using fallback script.")
            return _fallback_script(topic)

    prompt = f"""You are creating an extremely engaging, child-friendly 5-minute educational YouTube video script for 3rd graders (8-9 years old) in this niche: "{NICHE}".
Topic: "{topic['title']}"
Module: {topic['module']}
Level: {topic['level']}
Day: {topic['day']} of a 100-day course

STRICT SAFETY RULES:
- All content, character_pose, and diagram_prompt fields MUST be 100% G-rated, safe for work, wholesome, and elementary-school friendly.
- character_pose MUST be simple, innocent mascot actions (e.g. "pointing to chalkboard excitedly", "smiling warmly", "holding a book").
- diagram_prompt MUST be simple cute educational objects (e.g. "a cute yellow star icon", "a colorful computer sticker").

IMPORTANT: Return ONLY valid JSON — no markdown, no code fences, no explanation.

The JSON must match this exact structure:
{{
  "video_title": "Day {topic['day']}: {topic['title']} for Kids! | {NICHE}",
  "video_description": "Hey kids! In today's video we explore {topic['title']} in a fun and easy way! Part of our 100-day {NICHE} course.\\n\\nWhat you will learn today:\\n- [list 3 simple bullet points]\\n\\n#{NICHE.replace(' ', '')}ForKids #LearnWithMe",
  "tags": ["{NICHE.lower()} for kids", "educational video", "elementary school", "explainer", "for children"],
  "segments": [
    {{
      "title": "[Fun introductory title]",
      "narration": "[Write ~80-100 words starting with a massive hook. Tone must be highly enthusiastic, warm, and friendly.]",
      "character_pose": "smiling and waving happily at the camera, looking friendly and welcoming",
      "board_elements": [
        "Welcome to Day {topic['day']}!",
        "Today: {topic['title']}"
      ],
      "diagram_prompt": "a cartoon smiley face sticker, white background, vector"
    }},
    {{
      "title": "[Concept explanation segment]",
      "narration": "[Explain the core concept using a simple analogy. Keep narration ~100-120 words.]",
      "character_pose": "pointing to the chalkboard with an excited look, explaining a fun fact",
      "board_elements": [
        "[Simple rule or definition]",
        "[Short example]"
      ],
      "diagram_prompt": "a cute red apple wearing glasses, sticker style, white background"
    }},
    {{
      "title": "[Summary and Outro segment]",
      "narration": "[Summarize in very simple terms. Tease the next topic: {topic.get('next_topic', 'tomorrow')}. Invite kids to subscribe. Narration ~80-100 words.]",
      "character_pose": "smiling warmly and waving goodbye, looking happy and proud",
      "board_elements": [
        "Key point: [Simple summary statement]",
        "Next time: [Next topic name]"
      ],
      "diagram_prompt": "a cute gold star badge, sticker style, white background"
    }}
  ],
  "summary_points": [
    "[Key takeaway 1 — simple]",
    "[Key takeaway 2 — simple]",
    "[Key takeaway 3 — simple]"
  ],
  "quiz": [
    {{
      "question": "[Fun multiple choice question 1 based on the lesson]",
      "options": [
        "[Option A - Incorrect]",
        "[Option B - Correct answer]",
        "[Option C - Incorrect]",
        "[Option D - Incorrect]"
      ],
      "answer": 1
    }},
    {{
      "question": "[Fun multiple choice question 2 based on the lesson]",
      "options": [
        "[Option A - Correct answer]",
        "[Option B - Incorrect]",
        "[Option C - Incorrect]",
        "[Option D - Incorrect]"
      ],
      "answer": 0
    }},
    {{
      "question": "[Fun multiple choice question 3 based on the lesson]",
      "options": [
        "[Option A - Incorrect]",
        "[Option B - Incorrect]",
        "[Option C - Incorrect]",
        "[Option D - Correct answer]"
      ],
      "answer": 3
    }}
  ],
  "next_topic": "[Teaser title of the next topic]"
}}

Rules:
- Target 3rd-grade understanding: Avoid jargon.
- Include exactly 3 to 5 segments totaling ~300 words of narration.
- For each segment, provide `character_pose`, 2-3 `board_elements`, and a `diagram_prompt`.
- Provide EXACTLY 3 multiple-choice questions in the `quiz` list. Each question must have exactly 4 choices, and a 0-indexed correct `answer` index.
- Return ONLY the JSON object, nothing else."""

    if LLM_PROVIDER == "gemini":
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            raw = response.text.strip()
        except Exception as e:
            print(f"[script_generator] Gemini API error: {e}")
            return _fallback_script(topic)
    else:
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            message = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text.strip()
        except Exception as e:
            print(f"[script_generator] Anthropic API error: {e}")
            return _fallback_script(topic)

    # Strip accidental markdown fences
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[script_generator] JSON parse error: {e}")
        print(f"[script_generator] Raw response (first 500 chars): {raw[:500]}")
        data = _fallback_script(topic)

    return data


def _fallback_script(topic: dict) -> dict:
    """Minimal fallback if LLM's response can't be parsed."""
    return {
        "video_title": f"Day {topic['day']}: {topic['title']} for Kids! | {NICHE}",
        "video_description": f"Today we learn about {topic['title']} in a simple, fun way! Part of our 100-day {NICHE} course.",
        "tags": [NICHE.lower(), "education", "for kids"],
        "segments": [
            {
                "title": f"Let's Explore {topic['title']}!",
                "narration": f"Hi everyone! Welcome to Day {topic['day']} of our adventure! Today, we're going to explore the exciting world of {topic['title']}. Are you ready? Let's go!",
                "character_pose": "smiling and waving happily at the camera, looking friendly and welcoming",
                "board_elements": [
                    "Welcome to Day 2!",
                    f"Topic: {topic['title']}"
                ],
                "diagram_prompt": "a cute cartoon telescope, sticker style, white background"
            },
            {
                "title": "How Does it Work?",
                "narration": f"Think of {topic['title']} like a magical toolbox in {topic['module']}. It has special tools that help us do amazing things step-by-step, just like following a treasure map!",
                "character_pose": "pointing to the chalkboard with an excited look, explaining a fun fact",
                "board_elements": [
                    "A magical toolbox!",
                    "Follows a treasure map step-by-step"
                ],
                "diagram_prompt": "a treasure chest, cartoon sticker style, white background"
            },
            {
                "title": "You Did It!",
                "narration": f"You did a wonderful job today! Now we know the basics of {topic['title']}. Tomorrow we'll explore even more cool secrets, so hit that subscribe button to join us!",
                "character_pose": "smiling warmly and waving goodbye, looking happy and proud",
                "board_elements": [
                    "Great Job today!",
                    "Subscribe for tomorrow's quest!"
                ],
                "diagram_prompt": "a gold trophy, sticker style, white background"
            }
        ],
        "summary_points": [
            f"We learned about {topic['title']}.",
            "It works step-by-step like a map.",
            "Ready for more adventures!"
        ],
        "quiz": [
            {
                "question": f"What was the main topic we learned about today?",
                "options": ["Flying Cars", topic["title"], "Making Ice Cream", "Dinosaurs"],
                "answer": 1
            },
            {
                "question": "What did we compare our lesson to today?",
                "options": ["A magical toolbox", "A roller coaster", "A slice of pizza", "A sleeping cat"],
                "answer": 0
            },
            {
                "question": "What should you do to join tomorrow's lesson?",
                "options": ["Throw a shoe", "Climb a tree", "Subscribe to the channel!", "Go to sleep"],
                "answer": 2
            }
        ],
        "next_topic": "Our next big adventure!"
    }
