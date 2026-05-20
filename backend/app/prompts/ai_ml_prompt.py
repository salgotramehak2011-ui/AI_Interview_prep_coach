"""AI/ML domain interview prompt templates."""

SYSTEM_PROMPT = """You are an expert AI/ML technical interviewer.
Ask clear, realistic interview questions covering machine learning fundamentals,
deep learning, NLP, computer vision, MLOps, and data science best practices.
Adapt difficulty to the candidate level. Be professional and concise."""

QUESTION_TEMPLATE = """Domain: AI / Machine Learning
Difficulty: {difficulty}
Retrieved knowledge context:
{context}

Previous Q&A in this session:
{history}

Generate ONE new interview question that:
- Tests practical AI/ML knowledge
- Matches {difficulty} level
- Has not been asked before in this session
- References concepts from the context when relevant

Return ONLY the question text, no preamble."""

FOLLOW_UP_TEMPLATE = """Domain: AI / Machine Learning
Original question: {question}
Candidate answer: {answer}
Evaluation summary: {evaluation}

Generate ONE targeted follow-up question to probe deeper into weak areas.
Return ONLY the follow-up question."""

FEEDBACK_TEMPLATE = """Domain: AI / Machine Learning
Question: {question}
Answer: {answer}
Scores: technical={technical}, clarity={clarity}, confidence={confidence}, depth={depth}

Provide 2-3 sentences of constructive feedback for improvement."""
