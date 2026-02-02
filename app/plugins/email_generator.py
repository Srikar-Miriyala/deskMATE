import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class EmailGeneratorPlugin:
    """Plugin for generating email drafts using Gemini"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.use_gemini = True
            except:
                self.use_gemini = False
        else:
            self.use_gemini = False
    
    def generate_email(self, subject: str, recipient: str, body: str) -> dict:
        """Generate a professional email draft"""
        if self.use_gemini:
            try:
                prompt = f"""
                Create a professional email draft with the following details:
                Subject: {subject}
                Recipient: {recipient}
                Body content: {body}
                
                Format the email professionally with appropriate greeting and closing.
                Keep it concise and professional.
                """
                
                response = self.model.generate_content(prompt)
                email_draft = response.text.strip()
                
                return {
                    "success": True,
                    "email_draft": email_draft,
                    "subject": subject,
                    "recipient": recipient,
                    "generated_with": "Gemini AI"
                }
            except Exception as e:
                # Fallback to template
                print(f"Gemini email generation failed: {e}")
        
        # Fallback template
        email_template = f"""
Subject: {subject}

To: {recipient}

Dear Team,

{body}

Best regards,
DeskMate AI Assistant

---
This is a draft email. Please review before sending.
"""
        
        return {
            "success": True,
            "email_draft": email_template.strip(),
            "subject": subject,
            "recipient": recipient,
            "generated_with": "Template"
        }
    
    def generate_email_from_prompt(self, prompt: str) -> dict:
        """Generate complete email from natural language prompt using Gemini"""
        if self.use_gemini:
            try:
                email_prompt = f"""
                Based on the following request, generate a complete professional email draft:
                "{prompt}"
                
                Include:
                - Appropriate subject line
                - Professional greeting
                - Clear body content
                - Professional closing
                - Use "team@company.com" as recipient if not specified
                
                Format the email properly.
                """
                
                response = self.model.generate_content(email_prompt)
                email_draft = response.text.strip()
                
                return {
                    "success": True,
                    "email_draft": email_draft,
                    "subject": "AI-Generated Email",
                    "recipient": "team@company.com",
                    "generated_with": "Gemini AI"
                }
            except Exception as e:
                print(f"Gemini email generation failed: {e}")
        
        # Fallback
        return self.generate_email(
            "Follow-up from our conversation",
            "team@company.com",
            f"As per our discussion: {prompt}. Looking forward to your response."
        )