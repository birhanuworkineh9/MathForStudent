
"""
MathForStudent AI Tutor Service
================================

AI-powered educational support for:
- Mathematics
- Physics
- Chemistry
- Computer Science

Features:
- Text questions
- Image questions
- Grade 9 through University explanations
- Mathematics specialist-engine integration
- Input validation
- Image validation and size limits
- Safe error handling
- English step-by-step answers

Environment variables:
    OPENAI_API_KEY
    OPENAI_MODEL (default: gpt-4.1-mini)
"""

import os
import base64
import logging
import json

from openai import OpenAI


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DEFAULT_MODEL = "gpt-4.1-mini"

MAX_QUESTION_LENGTH = 12000
MAX_SUBJECT_LENGTH = 80
MAX_EDUCATION_LEVEL_LENGTH = 80
MAX_IMAGE_SIZE = 8 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_SUBJECTS = {
    "mathematics",
    "math",
    "physics",
    "chemistry",
    "computer science",
}


# ---------------------------------------------------------
# AI Tutor Instructions
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are MathForStudent, an advanced educational AI tutor.

Your students range from Grade 9 through University.

SUPPORTED SUBJECTS:

1. Mathematics
2. Physics
3. Chemistry
4. Computer Science

IMPORTANT TEACHING RULES:

- Answer in English only.
- Adapt explanations to the student's education level.
- Explain solutions step by step.
- Identify the relevant academic concept.
- Show formulas when necessary.
- Define important symbols and variables.
- Substitute values carefully.
- Show calculations clearly.
- Include correct units in Physics and Chemistry.
- Check final answers whenever possible.
- Distinguish exact answers from approximations.
- Never invent missing information.
- Never pretend an uncertain answer is guaranteed.
- If a question is incomplete, ask for clarification.
- If an image is unclear, request a clearer image.
- If a problem has multiple valid interpretations,
  explain the ambiguity.

MATHEMATICS:

Support algebra, equations, inequalities, functions,
trigonometry, geometry, calculus, statistics,
probability, matrices, vectors, complex numbers,
differential equations and advanced mathematics.

PHYSICS:

Explain concepts, equations, units, mechanics,
electricity, magnetism, waves, optics,
thermodynamics and modern physics.

CHEMISTRY:

Explain chemical equations, balancing,
stoichiometry, atomic structure, bonding,
moles, equilibrium, acids, bases and reactions.

COMPUTER SCIENCE:

Explain programming, algorithms, data structures,
databases, computer architecture, networking
and computational problem solving.

SPECIALIST ENGINE RESULTS:

If a Mathematics specialist-engine result is provided,
inspect it carefully before using it.

Do not blindly accept an incorrect result.
If it conflicts with your mathematical reasoning,
explain the conflict.

RESPONSE STRUCTURE:

1. Understanding the Question
2. Relevant Concept
3. Formula or Method
4. Step-by-Step Solution
5. Final Answer
6. Answer Check
7. Learning Tip

Use only the sections that are relevant to the question.
"""


# ---------------------------------------------------------
# Input Validation
# ---------------------------------------------------------

def validate_text(value, field_name, max_length):
    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be text."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            f"{field_name} is required."
        )

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} is too long."
        )

    return value


def validate_subject(subject):
    subject = validate_text(
        subject,
        "Subject",
        MAX_SUBJECT_LENGTH
    )

    if subject.lower() not in ALLOWED_SUBJECTS:
        raise ValueError(
            "Unsupported subject. Choose Mathematics, "
            "Physics, Chemistry, or Computer Science."
        )

    return subject


def validate_education_level(level):
    return validate_text(
        level,
        "Education level",
        MAX_EDUCATION_LEVEL_LENGTH
    )


# ---------------------------------------------------------
# Image Processing
# ---------------------------------------------------------

def encode_uploaded_image(image):
    """
    Validate and encode an uploaded image.

    Accepts Flask FileStorage-like objects.
    Returns a base64 data URL.
    """

    if image is None:
        return None

    mime_type = getattr(
        image,
        "mimetype",
        None
    )

    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "Unsupported image format. "
            "Upload JPG, PNG, WEBP, or GIF."
        )

    stream = getattr(
        image,
        "stream",
        image
    )

    try:
        if hasattr(stream, "seek"):
            stream.seek(0)

        image_bytes = stream.read(
            MAX_IMAGE_SIZE + 1
        )

    except (OSError, AttributeError) as error:
        raise ValueError(
            "Unable to read the uploaded image."
        ) from error

    if not image_bytes:
        raise ValueError(
            "The uploaded image is empty."
        )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(
            "Image is too large. Maximum size is 8 MB."
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("ascii")

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# ---------------------------------------------------------
# Mathematics Specialist Engine
# ---------------------------------------------------------

def get_mathematics_engine_result(
    question,
    subject
):
    """
    Try the symbolic Mathematics engine.

    Word problems that cannot be parsed are handled
    by the AI tutor instead.
    """

    if subject.strip().lower() not in {
        "mathematics",
        "math"
    }:
        return None

    if not question:
        return None

    try:
        from .math_service import solve_math_problem

        result = solve_math_problem(
            question,
            operation="auto"
        )

        if not isinstance(result, dict):
            logger.warning(
                "Mathematics engine returned invalid data."
            )
            return None

        if "answer" not in result:
            logger.warning(
                "Mathematics engine result has no answer."
            )
            return None

        return result

    except (ImportError, ValueError, TypeError,
            ArithmeticError, RecursionError) as error:

        logger.info(
            "Mathematics engine could not parse question: %s",
            error
        )

        return None

    except Exception:
        logger.exception(
            "Unexpected Mathematics engine error."
        )

        return None


# ---------------------------------------------------------
# OpenAI Client
# ---------------------------------------------------------

def create_openai_client():
    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=api_key,
        timeout=60.0,
        max_retries=2
    )


# ---------------------------------------------------------
# Main AI Tutor Function
# ---------------------------------------------------------

def solve_with_ai(
    question,
    subject,
    education_level,
    image=None
):
    """
    Solve a student's academic question.

    Parameters:
        question:
            Typed question from the student.

        subject:
            Mathematics, Physics, Chemistry,
            or Computer Science.

        education_level:
            Grade 9 through University.

        image:
            Optional uploaded image.

    Returns:
        AI-generated educational explanation as text.
    """

    # Validate subject and education level.
    subject = validate_subject(subject)

    education_level = validate_education_level(
        education_level
    )

    # Validate question.
    if question is None:
        question = ""

    if not isinstance(question, str):
        raise ValueError(
            "Question must be text."
        )

    question = question.strip()

    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(
            "Question is too long."
        )

    # Process optional image.
    image_data_url = encode_uploaded_image(
        image
    )

    if not question and image_data_url is None:
        raise ValueError(
            "Enter a question or upload an image."
        )

    # Get mathematics engine result if applicable.
    specialist_result = (
        get_mathematics_engine_result(
            question,
            subject
        )
        if question
        else None
    )

    # Prepare user message.
    user_text = (
        f"Subject: {subject}\n"
        f"Education level: {education_level}\n"
        f"Student question: "
        f"{question or 'Please read and solve the uploaded image.'}"
    )

    if specialist_result is not None:
        user_text += (
            "\n\nMathematics specialist-engine result:\n"
            + json.dumps(
                specialist_result,
                ensure_ascii=False,
                default=str
            )
            + "\nCheck this result before using it."
        )

    content = [
        {
            "type": "text",
            "text": user_text
        }
    ]

    if image_data_url:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data_url,
                    "detail": "high"
                }
            }
        )

    # Create client.
    client = create_openai_client()

    model = os.getenv(
        "OPENAI_MODEL",
        DEFAULT_MODEL
    ).strip()

    if not model:
        raise RuntimeError(
            "OPENAI_MODEL is incorrectly configured."
        )

    # Send request to OpenAI.
    try:
        response = client.chat.completions.create(
            model=model,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": content
                }
            ],

            temperature=0.2
        )

    except Exception as error:
        logger.exception(
            "OpenAI tutoring request failed."
        )

        raise RuntimeError(
            "The AI tutor is temporarily unavailable. "
            "Please try again."
        ) from error

    # Extract response.
    if not response.choices:
        raise RuntimeError(
            "AI returned no response choices."
        )

    answer = response.choices[0].message.content

    if not isinstance(answer, str):
        raise RuntimeError(
            "AI returned an invalid response."
        )

    answer = answer.strip()

    if not answer:
        raise RuntimeError(
            "AI returned an empty answer."
        )

    return answer


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------

__all__ = [
    "solve_with_ai",
    "validate_subject",
    "validate_education_level",
    "encode_uploaded_image",
    "get_mathematics_engine_result",
]

    

                