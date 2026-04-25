# Prompt Engineering in LearnForge

## Overview

LearnForge uses 5 engineered system prompts across 3 agents plus a unified LLM backend that handles JSON response parsing, retry logic, and multi-backend routing.

## Prompts

### 1. Curriculum System Prompt (`prompts/curriculum_system.txt`)
- **Role:** Expert instructional designer
- **Technique:** Constrained JSON output with Bloom's taxonomy mapping
- **Key constraint:** Modules must escalate cognitive demand (remember → understand → apply → analyze → evaluate → create)
- **Output schema:** Strict JSON with modules containing id, title, objectives, prerequisites, bloom_level, estimated_minutes

### 2. Lesson System Prompt (`prompts/lesson_system.txt`)
- **Role:** Expert educator
- **Technique:** Level-adaptive content generation with structured sections
- **Key constraint:** Match depth/vocabulary to learner level. Include concrete examples. End with summary and takeaways.
- **Output schema:** JSON with sections (heading, content, key_concepts, examples), summary, key_takeaways

### 3. Quiz System Prompt (`prompts/quiz_system.txt`)
- **Role:** Assessment expert
- **Technique:** Bloom's taxonomy-tagged question generation with misconception-based distractors
- **Key constraint:** Mix question types (multiple_choice, true_false, short_answer). Make distractors plausible. Include explanations.
- **Output schema:** JSON with questions containing id, question, type, options, correct_answer, explanation, bloom_level, difficulty

### 4. Flashcard System Prompt (`prompts/flashcard_system.txt`)
- **Role:** Spaced repetition expert
- **Technique:** Concise question/answer pairs with progressive difficulty
- **Key constraint:** Front must be a clear question. Back must be concise. Hint gives a nudge without revealing the answer.
- **Output schema:** JSON with cards containing id, front, back, hint, difficulty

### 5. Assessor System Prompt (`prompts/assessor_system.txt`)
- **Role:** Adaptive learning assessor with access to RAG reference material
- **Technique:** Rubric-grounded evaluation with citation requirements
- **Key constraint:** MUST reference retrieved documents. Score 0-5 with constructive feedback. Identify misconceptions explicitly. Tag knowledge gaps.
- **Output schema:** JSON with correct, score, feedback, explanation, misconception, bloom_level, gap_tags

## Design Principles

1. **JSON Mode everywhere:** All prompts enforce `response_format={"type": "json_object"}` — no parsing fragility
2. **Role + Constraints + Schema:** Every prompt follows this three-part structure
3. **Bloom's taxonomy integration:** Quiz questions and lessons are tagged with cognitive levels
4. **Misconception-driven assessment:** Assessor identifies common misconceptions, not just right/wrong
5. **Context management:** Assessor receives RAG-retrieved documents as context, preventing hallucinated feedback
6. **Graceful degradation:** Every agent has a `_fallback()` method returning valid structure if the LLM call fails
