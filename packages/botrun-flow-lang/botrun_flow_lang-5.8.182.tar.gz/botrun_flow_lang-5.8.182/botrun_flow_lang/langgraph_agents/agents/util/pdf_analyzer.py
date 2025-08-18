import anthropic
import base64
import httpx


import os
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()


def analyze_pdf_with_claude(
    pdf_data: str, user_input: str, model_name: str = "claude-sonnet-4-20250514"
):
    """
    Analyze a PDF file using Claude API

    Args:
        pdf_data: Base64-encoded PDF data
        user_input: User's query about the PDF content

    Returns:
        str: Claude's analysis of the PDF content based on the query
    """
    # Initialize Anthropic client
    client = anthropic.Anthropic()

    # Send to Claude
    message = client.messages.create(
        model=model_name,
        max_tokens=4096,  # Increased token limit for detailed analysis
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {"type": "text", "text": user_input},
                ],
            }
        ],
    )

    print(
        f"analyze_pdf_with_claude============> input_token: {message.usage.input_tokens} output_token: {message.usage.output_tokens}",
    )
    return message.content[0].text


def analyze_pdf_with_gemini(
    pdf_data: str, user_input: str, model_name: str = "gemini-2.5-flash"
):
    """
    Analyze a PDF file using Gemini API

    Args:
        pdf_data: Base64-encoded PDF data
        user_input: User's query about the PDF content
        model_name: Gemini model name to use

    Returns:
        str: Gemini's analysis of the PDF content based on the query
    """
    # 放到要用的時候才 import，不然loading 會花時間
    from google import genai
    from google.genai import types

    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI"),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = genai.Client(
        credentials=credentials,
        project="scoop-386004",
        location="us-central1",
    )
    response = client.models.generate_content(
        model=model_name,
        contents=[
            user_input,
            types.Part(
                inline_data={
                    "mime_type": "application/pdf",
                    "data": pdf_data,
                }
            ),
        ],
    )
    # Log token usage if available
    if hasattr(response, "usage_metadata"):
        print(
            f"analyze_pdf_with_gemini============> input_token: {response.usage_metadata.prompt_token_count} output_token: {response.usage_metadata.candidates_token_count}",
        )

    return response.text


def analyze_pdf(pdf_url: str, user_input: str):
    """
    Analyze a PDF file using multiple models in order of preference based on PDF_ANALYZER_MODEL env var

    If PDF_ANALYZER_MODEL contains comma-separated models, it will try them in order,
    falling back to the next one if the previous fails.

    Args:
        pdf_url: URL to the PDF file
        user_input: User's query about the PDF content

    Returns:
        str: Analysis of the PDF content based on the query
    """
    try:
        # Download and encode the PDF file from URL
        pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")

        # Get models list from environment variable
        models_str = os.getenv("PDF_ANALYZER_MODEL", "gemini-2.5-flash")
        print(f"[analyze_pdf] 分析PDF使用模型: {models_str}")
        models = [model.strip() for model in models_str.split(",")]

        last_error = None

        # Try each model in order
        for model in models:
            try:
                if model.startswith("gemini-"):
                    print(f"Trying to analyze PDF with Gemini model: {model}")
                    return analyze_pdf_with_gemini(pdf_data, user_input, model)
                elif model.startswith("claude-"):
                    print(f"Trying to analyze PDF with Claude model: {model}")
                    return analyze_pdf_with_claude(pdf_data, user_input, model)
                else:
                    print(f"Unknown model type: {model}, skipping")
                    continue
            except Exception as e:
                import traceback

                traceback.print_exc()
                error_msg = f"Error analyzing PDF with {model}: {str(e)}"
                print(error_msg)
                last_error = error_msg
                # Continue to the next model in the list
                continue

        # If we've reached here, all models failed
        return (
            f"Error analyzing PDF with all specified models. Last error: {last_error}"
        )

    except Exception as e:
        print(f"Error downloading PDF: {str(e)}")
        return f"Error downloading PDF: {str(e)}"
