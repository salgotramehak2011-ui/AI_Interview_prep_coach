"""Cybersecurity domain interview prompt templates."""

SYSTEM_PROMPT = """You are an expert cybersecurity technical interviewer.
Cover network security, cryptography, threat modeling, incident response,
compliance, penetration testing, and secure architecture. Be professional."""

QUESTION_TEMPLATE = """Domain: Cybersecurity
Difficulty: {difficulty}
Retrieved knowledge context:
{context}

Previous Q&A in this session:
{history}

Generate ONE cybersecurity interview question at {difficulty} level.
Return ONLY the question text."""

FOLLOW_UP_TEMPLATE = """Domain: Cybersecurity
Original question: {question}
Candidate answer: {answer}
Evaluation: {evaluation}

Generate ONE follow-up question on weak areas.
Return ONLY the follow-up question."""

FEEDBACK_TEMPLATE = """Domain: Cybersecurity
Question: {question}
Answer: {answer}
Scores: technical={technical}, clarity={clarity}, confidence={confidence}, depth={depth}

Provide 2-3 sentences of constructive feedback."""
