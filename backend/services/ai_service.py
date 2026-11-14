from openai import OpenAI


def explain_with_ai(question, subject, engine_result=None):
    from flask import current_app

    api_key = current_app.config.get("OPENAI_API_KEY")
    model = current_app.config.get("OPENAI_MODEL")

    if not api_key:
        return {
            "status": "needs_ai",
            "message": (
                "AI service is not configured. "
                "Please configure OPENAI_API_KEY."
            ),
            "engine_result": engine_result
        }

    try:
        client = OpenAI(api_key=api_key)

        system_prompt = """
You are MathForStudent, an educational tutor.

Audience: Grade 9 through university students.

Rules:
1. Explain in clear English.
2. Show steps and formulas.
3. Define symbols.
4. Substitute known values.
5. Include units in physics and chemistry.
6. Check the final answer when possible.
7. Never invent missing information.
8. Ask for missing values when necessary.
9. If a question is outside your reliable knowledge,
   clearly say so.
10. Teach the method, not only the final answer.
"""

        context = ""

        if engine_result:
            context = (
                "\nSpecialist calculation result:\n"
                + str(engine_result)
                + "\nExplain this result and preserve its numerical value."
            )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": (
                        f"Subject: {subject}\n"
                        f"Question: {question}\n"
                        f"{context}"
                    )
                }
            ],
            temperature=0.2
        )

        return {
            "status": "success",
            "subject": subject,
            "explanation": response.choices[0].message.content
        }

    except Exception:
        return {
            "status": "error",
            "message": (
                "The AI service could not process this request. "
                "Check the API configuration and try again."
            )
        }

    

                