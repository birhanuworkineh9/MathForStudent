import os
import base64

from openai import OpenAI


def solve_with_ai(
    question,
    subject,
    education_level,
    image=None
):
    """
    Solve student questions using an AI model.
    Supports text and image questions.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(api_key=api_key)

    system_prompt = """
You are MathForStudent, an expert educational AI tutor.

Your students range from Grade 9 to University.

Subjects:
1. Mathematics
2. Physics
3. Chemistry
4. Computer Science

Rules:
- Answer in English only.
- Explain every solution step by step.
- Identify the relevant concept.
- Show formulas when necessary.
- Explain calculations clearly.
- Check the final answer.
- Use the student's education level.
- If the image is unclear, ask for a clearer image.
- Never invent information when a question is unclear.

Use this response structure:

1. Understanding the Question
2. Relevant Concept
3. Formula or Method
4. Step-by-Step Solution
5. Final Answer
6. Learning Tip
"""

    user_content = [
        {
            "type": "text",
            "text": (
                f"Subject: {subject}\n"
                f"Education level: {education_level}\n"
                f"Question: {question or 'Please solve the uploaded image.'}"
            )
        }
    ]

    if image is not None:

        image_bytes = image.read()

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        mime_type = image.mimetype or "image/jpeg"

        image_url = (
            f"data:{mime_type};base64,{encoded_image}"
        )

        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })

    response = client.chat.completions.create(

        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-4.1-mini"
        ),

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_content
            }
        ],

        temperature=0.2
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError(
            "AI returned an empty answer."
        )

    return answer
