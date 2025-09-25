from fpdf import FPDF
from io import BytesIO
import unicodedata
import base64
import os
import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter   # ✅ NEW: for encryption

from utils import get_sendgrid_credentials

# Track whether password already sent (per recipient)
if "password_sent" not in st.session_state:
    st.session_state["password_sent"] = {}

# ✅ Generate password
def generate_password(aadhaar_last4: str, phone_last4: str) -> str:
    return f"{phone_last4}@{aadhaar_last4}"

# ✅ Encrypt PDF with password
# def encrypt_pdf(pdf_stream: BytesIO, password: str) -> BytesIO:
#     pdf_stream.seek(0)
#     reader = PdfReader(pdf_stream)
#     writer = PdfWriter()

#     for page in reader.pages:
#         writer.add_page(page)

#     writer.encrypt(password)

#     encrypted_stream = BytesIO()
#     writer.write(encrypted_stream)
#     encrypted_stream.seek(0)
#     return encrypted_stream



def generate_pdf(summary, risk_data, legal_updates=None, compliance_data=None):
    """Generate a PDF report with document analysis results"""
    pdf = FPDF()
    pdf.add_page()
    
    # Set up fonts
    pdf.set_font("Arial", "B", 16)

    # --- helper function inside ---
    import unicodedata
    from datetime import datetime
    from io import BytesIO

    def clean_text(text):
        if not text:
            return ""
        replacements = {
            "“": '"', "”": '"',
            "‘": "'", "’": "'",
            "–": "-", "—": "-",
            "•": "", "·": "",
            "→": "->",
            "…": "...",
            "©": "(c)", "®": "(R)", "™": "(TM)",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        # normalize any leftover unicode to plain ASCII
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # -------------------------------

    # Header
    pdf.cell(0, 10, "Legal Document Analysis Report", 0, 1, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
    pdf.ln(10)

    # Summary section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Document Summary", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean_text(summary))
    pdf.ln(10)

    # Risk Assessment section
    if risk_data:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Risk Assessment", 0, 1)
        pdf.set_font("Arial", "", 11)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Overall Risk Score: {risk_data.get('total_score', 'N/A')}/100", 0, 1)
        pdf.set_font("Arial", "", 11)

        pdf.cell(0, 8, "Risk Counts by Severity:", 0, 1)
        for severity, count in risk_data.get("severity_counts", {}).items():
            pdf.cell(0, 6, f"* {clean_text(severity)}: {count}", 0, 1)

        if risk_data.get("categories"):
            pdf.ln(5)
            pdf.cell(0, 8, "Risk Categories:", 0, 1)
            for category, score in risk_data.get("categories", {}).items():
                pdf.cell(0, 6, f"* {clean_text(category)}: {score}", 0, 1)

        pdf.ln(10)

    # Compliance section
    if compliance_data:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Compliance Requirements", 0, 1)
        pdf.set_font("Arial", "", 11)

        for category, data in compliance_data.items():
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"{clean_text(category)} Compliance", 0, 1)
            pdf.set_font("Arial", "", 11)

            if data.get('requirements'):
                pdf.cell(0, 8, "Key Requirements:", 0, 1)
                for req in data.get('requirements', []):
                    pdf.multi_cell(0, 6, f"* {clean_text(req)}")

            if data.get('relevant_regulations'):
                pdf.ln(3)
                pdf.cell(0, 8, "Relevant Regulations:", 0, 1)
                for reg in data.get('relevant_regulations', []):
                    pdf.multi_cell(0, 6, f"* {clean_text(reg)}")

            pdf.ln(5)

        pdf.ln(5)

    # Legal Updates section
    if legal_updates:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Recent Legal Updates", 0, 1)
        pdf.set_font("Arial", "", 11)

        for category, data in legal_updates.items():
            if data.get('updates'):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, f"{clean_text(category)} Updates", 0, 1)
                pdf.set_font("Arial", "", 11)

                for update in data.get('updates', []):
                    clean_title = clean_text(update.get('title', ''))
                    clean_source = clean_text(update.get('source', ''))

                    pdf.set_font("Arial", "B", 11)
                    pdf.multi_cell(0, 6, f"* {clean_title}")
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 6, f"  Source: {clean_source}")
                    pdf.ln(3)

                pdf.ln(5)

    try:
        # ✅ Directly get bytes from FPDF
        pdf_bytes = pdf.output(dest="S").encode("utf-8", "ignore")  # use utf-8 safe encode
        return BytesIO(pdf_bytes)
    except Exception as e:
        st.error(f"Failed to generate PDF: {str(e)}")
        return BytesIO(b"")


# st.write("DEBUG API Key:", sendgrid_api_key[:10] + "...")
# st.write("DEBUG Sender:", sender_email)


def send_email(recipient_email, attachment=None, subject=None, body=None, attachment_name=None):
    try:
        SENDGRID_API_KEY, SENDER_EMAIL = get_sendgrid_credentials()
    except ValueError as e:
        return False, f"⚠ {e}"

    if subject is None:
        subject = "📄 Legal Document Report"
    
    if body is None:
        body = """
        <h2>Legal Document Analysis Report</h2>
        <p>Please find attached your comprehensive legal document analysis report.</p>
        """

    message = Mail(
        from_email=SENDER_EMAIL,
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
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True, f"Email sent successfully. Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def create_email_text(summary=None, risk_assessment=None):
    email_html = """
    <h2>Legal Document Analysis Report</h2>
    <p>Dear User,</p>
    <p>Please find attached the analysis of your uploaded legal document.</p>
    """
    if summary:
        email_html += "<h3>Document Summary</h3><p>Summary included in PDF.</p>"
    if risk_assessment:
        email_html += "<h3>Risk Assessment</h3><p>Details included in PDF.</p>"
    email_html += "<p>Generated by AI Legal System.</p>"
    return email_html

# ✅ NEW WORKFLOW FUNCTION
def report_workflow(summary, risk_data, aadhaar_last4, phone_last4, recipient_email,
                    legal_updates=None, compliance_data=None, protect=True):
    pdf_report = generate_pdf(summary, risk_data, legal_updates, compliance_data)

    if protect:
        password = generate_password(aadhaar_last4, phone_last4)
        pdf_report = encrypt_pdf(pdf_report, password)
        st.info("🔑 Password Hint: Phone last 4 + '@' + Aadhaar last 4")

        # Send password only first time
        if recipient_email not in st.session_state["password_sent"]:
            send_email(
                recipient_email,
                subject="🔐 Your Report Password",
                body=f"<p>Your report password is: <b>{password}</b></p>",
            )
            st.session_state["password_sent"][recipient_email] = True

    return send_email(recipient_email, pdf_report, attachment_name="Legal_Report.pdf")
