import google.generativeai as genai
import json
import re
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError

# Load environment variables from .env
load_dotenv()

# Gemini API key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# AWS DynamoDB setup
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# DynamoDB table
TABLE_NAME = "quizie"
table = dynamodb.Table(TABLE_NAME)


class QuizGenerator:
    def __init__(self):
        self.questions_data = []

    def _generate_from_gemini(self, topic: str, num_questions: int):
        """Helper: Call Gemini to generate quiz questions."""
        prompt = f"""
        Create {num_questions} multiple-choice questions on the topic '{topic}'.
        The questions should gradually increase in difficulty from easy to medium to hard.
        For each question, provide:
        - Question text
        - 4 answer options (A, B, C, D)
        - The correct answer letter
        Format the output as a valid JSON list like this:
        [
          {{
            "question": "...",
            "options": ["...", "...", "...", "..."],
            "answer": "B"
          }}
        ]
        Return ONLY JSON. No explanations, no markdown formatting.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        output_text = getattr(response, "text", None)
        if not output_text and hasattr(response, "candidates"):
            output_text = response.candidates[0].content.parts[0].text

        if not output_text:
            raise ValueError("Gemini returned no text.")

        output_text = re.sub(r"^```json\s*|\s*```$", "", output_text.strip(), flags=re.DOTALL)

        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            print("DEBUG: Raw Gemini output:\n", output_text)
            raise ValueError("Failed to parse Gemini's response as JSON.")

    def generate_quiz(self, topic: str, num_questions: int):
        """If quiz exists → load from DynamoDB. Else → generate with Gemini and save."""
        try:
            quiz_id = f"{topic}_{num_questions}"
            response = table.get_item(Key={"quiz_id": quiz_id})
            if "Item" in response:
                self.questions_data = response["Item"]["questions"]
            else:
                self.questions_data = self._generate_from_gemini(topic, num_questions)
                table.put_item(Item={"quiz_id": quiz_id, "questions": self.questions_data})
            return self.questions_data
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not configured. Run `aws configure` or use .env")

    def generate_quiz_new(self, topic: str, num_questions: int):
        """Always generate new quiz with Gemini and overwrite in DynamoDB."""
        quiz_id = f"{topic}_{num_questions}"
        self.questions_data = self._generate_from_gemini(topic, num_questions)
        table.put_item(Item={"quiz_id": quiz_id, "questions": self.questions_data})
        return self.questions_data

    def question(self, number: int) -> str:
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["question"]
        raise IndexError("Question number out of range.")

    def options(self, number: int) -> list:
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["options"]
        raise IndexError("Question number out of range.")

    def correct_answer(self, number: int) -> str:
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["answer"]
        raise IndexError("Question number out of range.")
