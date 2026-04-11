from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import re
import traceback
import pdfplumber
import docx
import os

# Orchestrator import
try:
    from orchestrator import run_sentinel_analysis 
except ImportError:
    print("❌ CRITICAL: orchestrator.py missing in folder!")

app = Flask(__name__)
CORS(app)

# --- ROBUST FILE EXTRACTION UTILITIES ---

def extract_text_from_pdf(file):
    try:
        file.seek(0) 
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        extracted_text = text.strip()
        print(f"🔍 [DEBUG] PDF Extracted Length: {len(extracted_text)}")
        return extracted_text
    except Exception as e:
        print(f"❌ PDF Error: {str(e)}")
        return ""

def extract_text_from_docx(file):
    try:
        file.seek(0)
        doc = docx.Document(file)
        text = [para.text for para in doc.paragraphs]
        return "\n".join(text)
    except Exception as e:
        print(f"❌ DOCX Error: {str(e)}")
        return ""

def extract_text_from_file(file):
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file)
    elif filename.endswith('.txt'):
        return file.read().decode('utf-8')
    return ""

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("📥 [SENTINEL] Analysis Started...")
        
        # 1. PEHLE FILE CHECK KARO
        resume_text = ""
        if 'resume_file' in request.files and request.files['resume_file'].filename != '':
            file = request.files['resume_file']
            resume_text = extract_text_from_file(file)
            print(f"📄 File found: {file.filename}")

        # 2. 🛡️ ROBUST FALLBACK (Agar PDF 0 characters de, toh manual textarea check karo)
        if not resume_text or len(resume_text.strip()) == 0:
            print("⚠️ PDF was empty or scanned. Checking manual textarea...")
            resume_text = request.form.get('resume', '')

        jd_text = request.form.get('jd', '')

        # 3. FINAL INPUT VALIDATION
        if not resume_text or len(resume_text.strip()) < 10:
            raise ValueError("Bhai, Resume missing hai ya bahut chhota hai!")
        if not jd_text or len(jd_text.strip()) < 10:
            raise ValueError("Bhai, Job Description (JD) toh daal de!")

        # 4. ORCHESTRATOR CALL
        print("🤖 Invoking CrewAI Agents...")
        raw_output = run_sentinel_analysis(resume_text, jd_text)
        
        # 5. CLEANUP AI OUTPUT (Regex logic)
        output_str = str(raw_output)
        json_match = re.search(r'\{.*\}', output_str, re.DOTALL)
        
        if json_match:
            result_dict = json.loads(json_match.group())
        else:
            raise ValueError("AI ne valid JSON nahi diya. Groq TPM limit check kar!")

        # 6. FINAL RESPONSE
        final_response = {
            "score": result_dict.get('score', 0),
            "skills": result_dict.get('skills', []),
            "insight": result_dict.get('insight', "Analysis Successful."),
            "questions": result_dict.get('questions', [])
        }

        print(f"📤 [SENTINEL] Scan Complete. Match: {final_response['score']}%")
        return jsonify(final_response)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        # print(traceback.format_exc()) # Debugging ke liye
        return jsonify({
            "score": 0, 
            "skills": ["Error Encountered"],
            "insight": f"System Alert: {str(e)}",
            "questions": ["Bhai terminal check kar, kuch fat gaya hai."]
        }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')