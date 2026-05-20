"""Web Development domain interview prompt templates."""

SYSTEM_PROMPT = """You are an expert web development technical interviewer.
Cover frontend (HTML/CSS/JS, React), backend (APIs, databases), DevOps,
security, and system design for web applications. Be professional and concise."""

QUESTION_TEMPLATE = """Domain: Web Development
Difficulty: {difficulty}
Retrieved knowledge context:
{context}

Previous Q&A in this session:
{history}

Generate ONE new interview question for {difficulty} level.
Return ONLY the question text."""

FOLLOW_UP_TEMPLATE = """Domain: Web Development
Original question: {question}
Candidate answer: {answer}
Evaluation: {evaluation}

Generate ONE follow-up question probing gaps in the answer.
Return ONLY the follow-up question."""

FEEDBACK_TEMPLATE = """Domain: Web Development
Question: {question}
Answer: {answer}
Scores: technical={technical}, clarity={clarity}, confidence={confidence}, depth={depth}

Provide 2-3 sentences of constructive feedback."""
