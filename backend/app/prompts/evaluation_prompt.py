"""Evaluation prompt templates (domain-agnostic)."""

SYSTEM_PROMPT = """You are an expert technical interview evaluator.
Score answers objectively on four dimensions (0-100 each):
technical_correctness, communication_clarity, confidence, depth_of_knowledge.
Respond ONLY with valid JSON, no markdown fences."""

EVALUATION_TEMPLATE = """Evaluate this interview answer.

Domain: {domain}
Difficulty: {difficulty}
Question: {question}
Answer: {answer}
Reference context (from knowledge base):
{context}
{voice_info}

Return JSON with this exact structure:
{{
  "technical_correctness": <0-100>,
  "communication_clarity": <0-100>,
  "confidence": <0-100>,
  "depth_of_knowledge": <0-100>,
  "feedback": "<2-4 sentences>",
  "weak_concepts": ["concept1", "concept2"]
}}"""

ROADMAP_TEMPLATE = """Based on these weak areas for user in {domain}:
{weak_areas}

Generate a JSON array of learning roadmap items:
[{{"concept": "...", "priority": "high|medium|low", "resources": ["..."], "estimated_weeks": 1}}]
Return ONLY valid JSON array."""
