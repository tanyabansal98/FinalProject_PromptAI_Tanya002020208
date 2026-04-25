# Ethics & Responsible AI

## Privacy
- All data stored locally (SQLite, ChromaDB, JSON files) — nothing sent to external servers except LLM API calls
- In demo/Ollama mode, zero data leaves the machine
- API mode sends prompts to OpenAI — subject to their data usage policies

## Fairness
- Content generated across diverse topics without cultural bias
- Bloom's taxonomy ensures objective cognitive-level assessment
- Adaptive difficulty based on demonstrated performance, not assumptions

## Transparency
- Three modes clearly labeled — user knows when API is being called
- All generated content auto-saved as JSON — fully inspectable
- RAG citations show which reference documents informed assessor feedback
- Score breakdowns explain WHY, not just right/wrong

## Limitations
- AI-generated content may contain errors — not a substitute for expert instruction
- Quiz distractors may not always reflect real misconceptions
- Fine-tuned model is small (3B parameters) and may produce inconsistent formatting
- Multimodal features are basic (diagram + TTS) — not full multimedia courseware

## Academic Integrity
- Educational tool for learning, not for bypassing coursework
- Generated quizzes are practice tools, not certified assessments
- All content is AI-generated — clearly marked, not presented as human-authored
