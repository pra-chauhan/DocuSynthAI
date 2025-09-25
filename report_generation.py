# from fpdf import FPDF
# from io import BytesIO
# import unicodedata
# import base64
# import os
# import streamlit as st
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
# from datetime import datetime
# from PyPDF2 import PdfReader, PdfWriter   # ✅ NEW: for encryption

# from utils import get_sendgrid_credentials

# # Track whether password already sent (per recipient)
# if "password_sent" not in st.session_state:
#     st.session_state["password_sent"] = {}

# # ✅ Generate password
# def generate_password(aadhaar_last4: str, phone_last4: str) -> str:
#     return f"{phone_last4}@{aadhaar_last4}"

# # ✅ Encrypt PDF with password
# # def encrypt_pdf(pdf_stream: BytesIO, password: str) -> BytesIO:
# #     pdf_stream.seek(0)
# #     reader = PdfReader(pdf_stream)
# #     writer = PdfWriter()

# #     for page in reader.pages:
# #         writer.add_page(page)

# #     writer.encrypt(password)

# #     encrypted_stream = BytesIO()
# #     writer.write(encrypted_stream)
# #     encrypted_stream.seek(0)
# #     return encrypted_stream



# def generate_pdf(summary, risk_data, legal_updates=None, compliance_data=None):
#     """Generate a PDF report with document analysis results"""
#     pdf = FPDF()
#     pdf.add_page()
    
#     # Set up fonts
#     pdf.set_font("Arial", "B", 16)

#     # --- helper function inside ---
#     import unicodedata
#     from datetime import datetime
#     from io import BytesIO

#     def clean_text(text):
#         if not text:
#             return ""
#         replacements = {
#             "“": '"', "”": '"',
#             "‘": "'", "’": "'",
#             "–": "-", "—": "-",
#             "•": "*", "·": "*",
#             "→": "->",
#             "…": "...",
#             "©": "(c)", "®": "(R)", "™": "(TM)",
#         }
#         for k, v in replacements.items():
#             text = text.replace(k, v)
#         # normalize any leftover unicode to plain ASCII
#         return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
#     # -------------------------------

#     # Header
#     pdf.cell(0, 10, "Legal Document Analysis Report", 0, 1, "C")
#     pdf.set_font("Arial", "", 12)
#     pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
#     pdf.ln(10)

#     # Summary section
#     pdf.set_font("Arial", "B", 14)
#     pdf.cell(0, 10, "Document Summary", 0, 1)
#     pdf.set_font("Arial", "", 11)
#     pdf.multi_cell(0, 6, clean_text(summary))
#     pdf.ln(10)

#     # Risk Assessment section
#     if risk_data:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Risk Assessment", 0, 1)
#         pdf.set_font("Arial", "", 11)

#         pdf.set_font("Arial", "B", 12)
#         pdf.cell(0, 8, f"Overall Risk Score: {risk_data.get('total_score', 'N/A')}/100", 0, 1)
#         pdf.set_font("Arial", "", 11)

#         pdf.cell(0, 8, "Risk Counts by Severity:", 0, 1)
#         for severity, count in risk_data.get("severity_counts", {}).items():
#             pdf.cell(0, 6, f"* {clean_text(severity)}: {count}", 0, 1)

#         if risk_data.get("categories"):
#             pdf.ln(5)
#             pdf.cell(0, 8, "Risk Categories:", 0, 1)
#             for category, score in risk_data.get("categories", {}).items():
#                 pdf.cell(0, 6, f"* {clean_text(category)}: {score}", 0, 1)

#         pdf.ln(10)

#     # Compliance section
#     if compliance_data:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Compliance Requirements", 0, 1)
#         pdf.set_font("Arial", "", 11)

#         for category, data in compliance_data.items():
#             pdf.set_font("Arial", "B", 12)
#             pdf.cell(0, 8, f"{clean_text(category)} Compliance", 0, 1)
#             pdf.set_font("Arial", "", 11)

#             if data.get('requirements'):
#                 pdf.cell(0, 8, "Key Requirements:", 0, 1)
#                 for req in data.get('requirements', []):
#                     pdf.multi_cell(0, 6, f"* {clean_text(req)}")

#             if data.get('relevant_regulations'):
#                 pdf.ln(3)
#                 pdf.cell(0, 8, "Relevant Regulations:", 0, 1)
#                 for reg in data.get('relevant_regulations', []):
#                     pdf.multi_cell(0, 6, f"* {clean_text(reg)}")

#             pdf.ln(5)

#         pdf.ln(5)

#     # Legal Updates section
#     if legal_updates:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Recent Legal Updates", 0, 1)
#         pdf.set_font("Arial", "", 11)

#         for category, data in legal_updates.items():
#             if data.get('updates'):
#                 pdf.set_font("Arial", "B", 12)
#                 pdf.cell(0, 8, f"{clean_text(category)} Updates", 0, 1)
#                 pdf.set_font("Arial", "", 11)

#                 for update in data.get('updates', []):
#                     clean_title = clean_text(update.get('title', ''))
#                     clean_source = clean_text(update.get('source', ''))

#                     pdf.set_font("Arial", "B", 11)
#                     pdf.multi_cell(0, 6, f"* {clean_title}")
#                     pdf.set_font("Arial", "", 10)
#                     pdf.multi_cell(0, 6, f"  Source: {clean_source}")
#                     pdf.ln(3)

#                 pdf.ln(5)

#     try:
#         # ✅ Directly get bytes from FPDF
#         pdf_bytes = pdf.output(dest="S").encode("utf-8", "ignore")  # use utf-8 safe encode
#         return BytesIO(pdf_bytes)
#     except Exception as e:
#         st.error(f"Failed to generate PDF: {str(e)}")
#         return BytesIO(b"")


# # st.write("DEBUG API Key:", sendgrid_api_key[:10] + "...")
# # st.write("DEBUG Sender:", sender_email)


# def send_email(recipient_email, attachment=None, subject=None, body=None, attachment_name=None):
#     try:
#         SENDGRID_API_KEY, SENDER_EMAIL = get_sendgrid_credentials()
#     except ValueError as e:
#         return False, f"⚠ {e}"

#     if subject is None:
#         subject = "📄 Legal Document Report"
    
#     if body is None:
#         body = """
#         <h2>Legal Document Analysis Report</h2>
#         <p>Please find attached your comprehensive legal document analysis report.</p>
#         """

#     message = Mail(
#         from_email=SENDER_EMAIL,
#         to_emails=recipient_email,
#         subject=subject,
#         html_content=body
#     )
    
#     if attachment:
#         attachment.seek(0)
#         pdf_data = attachment.read()
#         encoded_pdf = base64.b64encode(pdf_data).decode()
        
#         file_attachment = Attachment(
#             FileContent(encoded_pdf),
#             FileName(attachment_name or "Legal_Report.pdf"),
#             FileType("application/pdf"),
#             Disposition("attachment")
#         )
#         message.attachment = file_attachment

#     try:
#         sg = SendGridAPIClient(SENDGRID_API_KEY)
#         response = sg.send(message)
#         return True, f"Email sent successfully. Status code: {response.status_code}"
#     except Exception as e:
#         return False, f"Error sending email: {str(e)}"

# def create_email_text(summary=None, risk_assessment=None):
#     email_html = """
#     <h2>Legal Document Analysis Report</h2>
#     <p>Dear User,</p>
#     <p>Please find attached the analysis of your uploaded legal document.</p>
#     """
#     if summary:
#         email_html += "<h3>Document Summary</h3><p>Summary included in PDF.</p>"
#     if risk_assessment:
#         email_html += "<h3>Risk Assessment</h3><p>Details included in PDF.</p>"
#     email_html += "<p>Generated by AI Legal System.</p>"
#     return email_html

# # ✅ NEW WORKFLOW FUNCTION
# def report_workflow(summary, risk_data, aadhaar_last4, phone_last4, recipient_email,
#                     legal_updates=None, compliance_data=None, protect=True):
#     pdf_report = generate_pdf(summary, risk_data, legal_updates, compliance_data)

#     if protect:
#         password = generate_password(aadhaar_last4, phone_last4)
#         pdf_report = encrypt_pdf(pdf_report, password)
#         st.info("🔑 Password Hint: Phone last 4 + '@' + Aadhaar last 4")

#         # Send password only first time
#         if recipient_email not in st.session_state["password_sent"]:
#             send_email(
#                 recipient_email,
#                 subject="🔐 Your Report Password",
#                 body=f"<p>Your report password is: <b>{password}</b></p>",
#             )
#             st.session_state["password_sent"][recipient_email] = True

#     return send_email(recipient_email, pdf_report, attachment_name="Legal_Report.pdf")

# from fpdf import FPDF
# from io import BytesIO
# import base64
# import os
# import streamlit as st
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
# from datetime import datetime

# from utils import get_sendgrid_credentials

# def generate_pdf(summary, risk_data, legal_updates=None, compliance_data=None):
#     """Generate a PDF report with document analysis results"""
#     pdf = FPDF()
#     pdf.add_page()
    
#     # Set up fonts
#     pdf.set_font("Arial", "B", 16)
    
#     # Header
#     pdf.cell(0, 10, "Legal Document Analysis Report", 0, 1, "C")
#     pdf.set_font("Arial", "", 12)
#     pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
#     pdf.ln(10)
    
#     # Summary section
#     pdf.set_font("Arial", "B", 14)
#     pdf.cell(0, 10, "Document Summary", 0, 1)
#     pdf.set_font("Arial", "", 11)
    
#     # Replace Unicode bullet points with ASCII alternatives
#     clean_summary = summary.replace("•", "").replace("\u2022", "")
    
#     # Add summary text with word wrapping
#     pdf.multi_cell(0, 6, clean_summary)
#     pdf.ln(10)
    
#     # Risk Assessment section
#     if risk_data:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Risk Assessment", 0, 1)
#         pdf.set_font("Arial", "", 11)
        
#         # Overall risk score
#         pdf.set_font("Arial", "B", 12)
#         pdf.cell(0, 8, f"Overall Risk Score: {risk_data.get('total_score', 'N/A')}/100", 0, 1)
#         pdf.set_font("Arial", "", 11)
        
#         # Risk counts by severity
#         pdf.cell(0, 8, "Risk Counts by Severity:", 0, 1)
#         for severity, count in risk_data.get("severity_counts", {}).items():
#             # Replace Unicode bullet points with ASCII alternatives
#             pdf.cell(0, 6, f"* {severity}: {count}", 0, 1)
        
#         # Risk categories
#         if risk_data.get("categories"):
#             pdf.ln(5)
#             pdf.cell(0, 8, "Risk Categories:", 0, 1)
#             for category, score in risk_data.get("categories", {}).items():
#                 # Replace Unicode bullet points with ASCII alternatives
#                 pdf.cell(0, 6, f"* {category}: {score}", 0, 1)
        
#         pdf.ln(10)
    
#     # Compliance section
#     if compliance_data:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Compliance Requirements", 0, 1)
#         pdf.set_font("Arial", "", 11)
        
#         for category, data in compliance_data.items():
#             pdf.set_font("Arial", "B", 12)
#             pdf.cell(0, 8, f"{category} Compliance", 0, 1)
#             pdf.set_font("Arial", "", 11)
            
#             # Requirements
#             if data.get('requirements'):
#                 pdf.cell(0, 8, "Key Requirements:", 0, 1)
#                 for req in data.get('requirements', []):
#                     # Replace Unicode bullet points with ASCII alternatives
#                     clean_req = req.replace("•", "").replace("\u2022", "")
#                     pdf.multi_cell(0, 6, f"* {clean_req}")
            
#             # Regulations
#             if data.get('relevant_regulations'):
#                 pdf.ln(3)
#                 pdf.cell(0, 8, "Relevant Regulations:", 0, 1)
#                 for reg in data.get('relevant_regulations', []):
#                     # Replace Unicode bullet points with ASCII alternatives
#                     clean_reg = reg.replace("•", "").replace("\u2022", "")
#                     pdf.multi_cell(0, 6, f"* {clean_reg}")
            
#             pdf.ln(5)
        
#         pdf.ln(5)
    
#     # Legal Updates section
#     if legal_updates:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Recent Legal Updates", 0, 1)
#         pdf.set_font("Arial", "", 11)
        
#         for category, data in legal_updates.items():
#             if data.get('updates'):
#                 pdf.set_font("Arial", "B", 12)
#                 pdf.cell(0, 8, f"{category} Updates", 0, 1)
#                 pdf.set_font("Arial", "", 11)
                
#                 for update in data.get('updates', []):
#                     # Replace Unicode bullet points with ASCII alternatives
#                     clean_title = update.get('title', '').replace("•", "").replace("\u2022", "")
#                     clean_source = update.get('source', '').replace("•", "").replace("\u2022", "")
                    
#                     pdf.set_font("Arial", "B", 11)
#                     pdf.multi_cell(0, 6, f"* {clean_title}")
#                     pdf.set_font("Arial", "", 10)
#                     pdf.multi_cell(0, 6, f"  Source: {clean_source}")
#                     pdf.ln(3)
                
#                 pdf.ln(5)
    
#     # Try to generate PDF with error handling
#     try:
#         pdf_data = pdf.output(dest="S").encode("latin1")  # Generate PDF as a string
#         return BytesIO(pdf_data)
#     except UnicodeEncodeError:
#         # If encoding fails, try a more aggressive character replacement approach
#         try:
#             # Create a new PDF with even more aggressive character replacement
#             return generate_pdf_with_ascii_only(summary, risk_data, legal_updates, compliance_data)
#         except Exception as e:
#             st.error(f"Failed to generate PDF: {str(e)}")
#             return BytesIO(b"Error generating PDF report")

# def generate_pdf_with_ascii_only(summary, risk_data, legal_updates=None, compliance_data=None):
#     """Fallback PDF generator that strictly uses ASCII characters only"""
#     pdf = FPDF()
#     pdf.add_page()
    
#     # Set up fonts
#     pdf.set_font("Arial", "B", 16)
    
#     # Header
#     pdf.cell(0, 10, "Legal Document Analysis Report", 0, 1, "C")
#     pdf.set_font("Arial", "", 12)
#     pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
#     pdf.ln(10)
    
#     # Function to sanitize text for latin-1 encoding
#     def sanitize_text(text):
#         if not isinstance(text, str):
#             return str(text)
#         # Replace common Unicode characters with ASCII equivalents
#         replacements = {
#             '\u2022': '-',  # bullet point
#             '\u2018': "'",  # left single quote
#             '\u2019': "'",  # right single quote
#             '\u201c': '"',  # left double quote
#             '\u201d': '"',  # right double quote
#             '\u2013': '-',  # en dash
#             '\u2014': '--', # em dash
#             '\u2026': '...' # ellipsis
#         }
#         for unicode_char, ascii_char in replacements.items():
#             text = text.replace(unicode_char, ascii_char)
        
#         # Remove any remaining non-latin1 characters
#         return ''.join(c for c in text if ord(c) < 256)
    
#     # Summary section with sanitized text
#     pdf.set_font("Arial", "B", 14)
#     pdf.cell(0, 10, "Document Summary", 0, 1)
#     pdf.set_font("Arial", "", 11)
#     pdf.multi_cell(0, 6, sanitize_text(summary))
#     pdf.ln(10)
    
#     # Risk Assessment section
#     if risk_data:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Risk Assessment", 0, 1)
#         pdf.set_font("Arial", "", 11)
        
#         # Overall risk score
#         pdf.set_font("Arial", "B", 12)
#         pdf.cell(0, 8, f"Overall Risk Score: {risk_data.get('total_score', 'N/A')}/100", 0, 1)
#         pdf.set_font("Arial", "", 11)
        
#         # Risk counts by severity
#         pdf.cell(0, 8, "Risk Counts by Severity:", 0, 1)
#         for severity, count in risk_data.get("severity_counts", {}).items():
#             pdf.cell(0, 6, f"- {sanitize_text(severity)}: {count}", 0, 1)
        
#         # Risk categories
#         if risk_data.get("categories"):
#             pdf.ln(5)
#             pdf.cell(0, 8, "Risk Categories:", 0, 1)
#             for category, score in risk_data.get("categories", {}).items():
#                 pdf.cell(0, 6, f"- {sanitize_text(category)}: {score}", 0, 1)
        
#         pdf.ln(10)
    
#     # Compliance section with sanitized text
#     if compliance_data:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Compliance Requirements", 0, 1)
        
#         for category, data in compliance_data.items():
#             pdf.set_font("Arial", "B", 12)
#             pdf.cell(0, 8, f"{sanitize_text(category)} Compliance", 0, 1)
#             pdf.set_font("Arial", "", 11)
            
#             # Requirements
#             if data.get('requirements'):
#                 pdf.cell(0, 8, "Key Requirements:", 0, 1)
#                 for req in data.get('requirements', []):
#                     pdf.multi_cell(0, 6, f"- {sanitize_text(req)}")
            
#             # Regulations
#             if data.get('relevant_regulations'):
#                 pdf.ln(3)
#                 pdf.cell(0, 8, "Relevant Regulations:", 0, 1)
#                 for reg in data.get('relevant_regulations', []):
#                     pdf.multi_cell(0, 6, f"- {sanitize_text(reg)}")
            
#             pdf.ln(5)
    
#     # Legal Updates section with sanitized text
#     if legal_updates:
#         pdf.set_font("Arial", "B", 14)
#         pdf.cell(0, 10, "Recent Legal Updates", 0, 1)
        
#         for category, data in legal_updates.items():
#             if data.get('updates'):
#                 pdf.set_font("Arial", "B", 12)
#                 pdf.cell(0, 8, f"{sanitize_text(category)} Updates", 0, 1)
#                 pdf.set_font("Arial", "", 11)
                
#                 for update in data.get('updates', []):
#                     pdf.set_font("Arial", "B", 11)
#                     pdf.multi_cell(0, 6, f"- {sanitize_text(update.get('title', ''))}")
#                     pdf.set_font("Arial", "", 10)
#                     pdf.multi_cell(0, 6, f"  Source: {sanitize_text(update.get('source', ''))}")
#                     pdf.ln(3)
                
#                 pdf.ln(5)
    
#     # Generate PDF
#     pdf_data = pdf.output(dest="S").encode("latin1")
#     return BytesIO(pdf_data)

# def send_email(recipient_email, attachment=None, subject=None, body=None, attachment_name=None):
#     """
#     Send an email with optional attachment using SendGrid
#     Returns a tuple of (success_boolean, message_string)
#     """
#     try:
#         sendgrid_api_key, sender_email = get_sendgrid_credentials()
#     except ValueError as e:
#         return False, f"⚠ {e}"

#     # Default values if not provided
#     if subject is None:
#         subject = "📄 Legal Document Report"
    
#     if body is None:
#         body = """
#         <h2>Legal Document Analysis Report</h2>
#         <p>Please find attached your comprehensive legal document analysis report, which includes:</p>
#         <ul>
#             <li>Document summary</li>
#             <li>Risk analysis</li>
#             <li>Compliance requirements</li>
#             <li>Relevant legal updates</li>
#         </ul>
#         <p>Thank you for using our service.</p>
#         """
    
#     # Create message
#     message = Mail(
#         from_email=sender_email,
#         to_emails=recipient_email,
#         subject=subject,
#         html_content=body
#     )
    
#     # Add attachment if provided
#     if attachment:
#         attachment.seek(0)
#         pdf_data = attachment.read()
#         encoded_pdf = base64.b64encode(pdf_data).decode()
        
#         file_attachment = Attachment(
#             FileContent(encoded_pdf),
#             FileName(attachment_name or "Legal_Report.pdf"),
#             FileType("application/pdf"),
#             Disposition("attachment")
#         )
#         message.attachment = file_attachment

#     try:
#         sg = SendGridAPIClient(sendgrid_api_key)
#         response = sg.send(message)
#         return True, f"Email sent successfully. Status code: {response.status_code}"
#     except Exception as e:
#         return False, f"Error sending email: {str(e)}"

# def create_email_text(summary=None, risk_assessment=None):
#     """Create HTML email content based on available analysis components"""
#     email_html = """
#     <h2>Legal Document Analysis Report</h2>
#     <p>Dear User,</p>
#     <p>Please find attached the analysis of your uploaded legal document.</p>
#     """
    
#     if summary:
#         email_html += "<h3>Document Summary</h3>"
#         email_html += f"<p>A summary of your document has been included in the attached PDF.</p>"
    
#     if risk_assessment:
#         email_html += "<h3>Risk Assessment</h3>"
#         email_html += f"<p>A comprehensive risk assessment has been included in the attached PDF.</p>"
    
#     email_html += """
#     <p>This report was generated by the AI-Driven Legal Document Analysis System.</p>
#     <p>Thank you for using our service.</p>
#     """
    
#     return email_html

from fpdf import FPDF
from io import BytesIO
import base64
import os
import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from datetime import datetime

from utils import get_sendgrid_credentials

# ------------------------------
# Utility: Sanitize text for PDF
# ------------------------------
def sanitize_text(text):
    """Ensure text is PDF-safe by converting/removing unsupported characters."""
    if not isinstance(text, str):
        return str(text)
    replacements = {
        '\u2022': '-',   # bullet point
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2013': '-',   # en dash
        '\u2014': '--',  # em dash
        '\u2026': '...', # ellipsis
        '₹': 'Rs.',      # Indian Rupee symbol
        '§': 'Section'   # Section symbol
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return ''.join(c if ord(c) < 65535 else '?' for c in text)

# ------------------------------
# PDF Class with Unicode font
# ------------------------------
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        # Load Unicode-capable font (DejaVuSans recommended)
        font_path = os.path.join("fonts", "DejaVuSans.ttf")
        if os.path.exists(font_path):
            self.add_font("DejaVu", "", font_path, uni=True)
            self.set_font("DejaVu", "", 12)
        else:
            # fallback if font missing
            self.set_font("Arial", "", 12)

# ------------------------------
# PDF Generation
# ------------------------------
def generate_pdf(summary, risk_data, legal_updates=None, compliance_data=None):
    """Generate a PDF report with document analysis results"""
    pdf = PDF()

    # Header
    pdf.set_font("", "B", 16)
    pdf.cell(0, 10, "Legal Document Analysis Report", 0, 1, "C")
    pdf.set_font("", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
    pdf.ln(10)

    # Summary section
    pdf.set_font("", "B", 14)
    pdf.cell(0, 10, "Document Summary", 0, 1)
    pdf.set_font("", "", 11)
    pdf.multi_cell(0, 6, sanitize_text(summary))
    pdf.ln(10)

    # Risk Assessment section
    if risk_data:
        pdf.set_font("", "B", 14)
        pdf.cell(0, 10, "Risk Assessment", 0, 1)
        pdf.set_font("", "", 11)

        # Overall risk score
        pdf.set_font("", "B", 12)
        pdf.cell(0, 8, f"Overall Risk Score: {risk_data.get('total_score', 'N/A')}/100", 0, 1)
        pdf.set_font("", "", 11)

        # Risk counts by severity
        pdf.cell(0, 8, "Risk Counts by Severity:", 0, 1)
        for severity, count in risk_data.get("severity_counts", {}).items():
            pdf.cell(0, 6, f"* {sanitize_text(severity)}: {count}", 0, 1)

        # Risk categories with examples
        if risk_data.get("categories"):
            pdf.ln(5)
            pdf.cell(0, 8, "Risk Categories:", 0, 1)
            for category, data in risk_data.get("categories", {}).items():
                pdf.set_font("", "B", 12)
                pdf.cell(0, 6, f"* {sanitize_text(category)}: {data['score']}", 0, 1)
                pdf.set_font("", "", 11)
                if "examples" in data:
                    for ex in data["examples"]:
                        pdf.multi_cell(0, 6, f"    - {sanitize_text(ex)}")

        pdf.ln(10)

    # Compliance section
    if compliance_data:
        pdf.set_font("", "B", 14)
        pdf.cell(0, 10, "Compliance Requirements", 0, 1)

        for category, data in compliance_data.items():
            pdf.set_font("", "B", 12)
            pdf.cell(0, 8, f"{sanitize_text(category)} Compliance", 0, 1)
            pdf.set_font("", "", 11)

            if data.get('requirements'):
                pdf.cell(0, 8, "Key Requirements:", 0, 1)
                for req in data.get('requirements', []):
                    pdf.multi_cell(0, 6, f"- {sanitize_text(req)}")

            if data.get('relevant_regulations'):
                pdf.ln(3)
                pdf.cell(0, 8, "Relevant Regulations:", 0, 1)
                for reg in data.get('relevant_regulations', []):
                    pdf.multi_cell(0, 6, f"- {sanitize_text(reg)}")

            pdf.ln(5)

        pdf.ln(5)

    # Legal Updates section
    if legal_updates:
        pdf.set_font("", "B", 14)
        pdf.cell(0, 10, "Recent Legal Updates", 0, 1)

        for category, data in legal_updates.items():
            if data.get('updates'):
                pdf.set_font("", "B", 12)
                pdf.cell(0, 8, f"{sanitize_text(category)} Updates", 0, 1)
                pdf.set_font("", "", 11)

                for update in data.get('updates', []):
                    pdf.set_font("", "B", 11)
                    pdf.multi_cell(0, 6, f"- {sanitize_text(update.get('title', ''))}")
                    pdf.set_font("", "", 10)
                    pdf.multi_cell(0, 6, f"  Source: {sanitize_text(update.get('source', ''))}")
                    pdf.ln(3)

                pdf.ln(5)

    # Generate PDF as BytesIO (no latin-1 encoding)
    try:
        pdf_data = pdf.output(dest="S").encode("latin-1", "replace")
        return BytesIO(pdf_data)
    except Exception as e:
        st.error(f"⚠ Failed to generate PDF: {str(e)}")
        return BytesIO(b"Error generating PDF report")

# ------------------------------
# Email Sending
# ------------------------------
def send_email(recipient_email, attachment=None, subject=None, body=None, attachment_name=None):
    """Send an email with optional attachment using SendGrid"""
    try:
        sendgrid_api_key, sender_email = get_sendgrid_credentials()
    except ValueError as e:
        return False, f"⚠ {e}"

    if subject is None:
        subject = "📄 Legal Document Report"

    if body is None:
        body = """
        <h2>Legal Document Analysis Report</h2>
        <p>Please find attached your comprehensive legal document analysis report, which includes:</p>
        <ul>
            <li>Document summary</li>
            <li>Risk analysis</li>
            <li>Compliance requirements</li>
            <li>Relevant legal updates</li>
        </ul>
        <p>Thank you for using our service.</p>
        """

    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject=subject,
        html_content=body
    )

    if attachment:
        attachment.seek(0)
        pdf_data = attachment.read()
        encoded_pdf = base64.b64encode(pdf_data).decode()

        file_attachment = Attachment(
            FileContent(encoded_pdf),
            FileName(attachment_name or "Legal_Report.pdf"),
            FileType("application/pdf"),
            Disposition("attachment")
        )
        message.attachment = file_attachment

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        return True, f"Email sent successfully. Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# ------------------------------
# Email Content Builder
# ------------------------------
def create_email_text(summary=None, risk_assessment=None):
    """Create HTML email content based on available analysis components"""
    email_html = """
    <h2>Legal Document Analysis Report</h2>
    <p>Dear User,</p>
    <p>Please find attached the analysis of your uploaded legal document.</p>
    """

    if summary:
        email_html += "<h3>Document Summary</h3>"
        email_html += f"<p>A summary of your document has been included in the attached PDF.</p>"

    if risk_assessment:
        email_html += "<h3>Risk Assessment</h3>"
        email_html += f"<p>A comprehensive risk assessment has been included in the attached PDF.</p>"

    email_html += """
    <p>This report was generated by the AI-Driven Legal Document Analysis System.</p>
    <p>Thank you for using our service.</p>
    """

    return email_html
