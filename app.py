from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from pyngrok import ngrok

# --- Import our custom modules ---
from config.db2_connector import (
    validate_patient, 
    update_patient_record, 
    get_all_patient_ids, 
    get_patient_count, 
    get_count_by_diagnosis
)
from config.cos_uploader import upload_file_to_cos

# ===============================
# Flask setup
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "your_very_secret_key" 

UPLOAD_FOLDER = os.path.join(static_dir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ===============================
# Load trained model
# ===============================
MODEL_PATH = os.path.join(BASE_DIR, 'training_outputs', 'heart_mri_model.keras')
try:
    model = load_model(MODEL_PATH)
    print("AI model loaded successfully.")
except Exception as e:
    print(f"FATAL ERROR: Could not load AI model from {MODEL_PATH}.")
    model = None

# ===============================
# Helper functions
# ===============================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def predict_image(img_path):
    if model is None: return "Error", "Model not loaded", 0.0
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    pred = model.predict(img_array, verbose=0)[0][0]
    
    if pred < 0.5:
        result_class, predicted_class, confidence = 'Healthy', 'Normal', round((1 - pred) * 100, 2)
    else:
        result_class, predicted_class, confidence = 'Sick', 'Sick', round(pred * 100, 2)
    return result_class, predicted_class, confidence

def get_interpretation_text(result_class, confidence):
    if result_class == 'Healthy':
        if confidence >= 90: return "The AI model is highly confident that the MRI shows typical heart structure and function patterns consistent with healthy cardiac tissue."
        elif confidence >= 70: return "The AI model is reasonably confident that the MRI findings are normal."
        else: return "The AI model suggests normal findings, but with lower confidence. A routine review by a specialist is advised."
    else:
        if confidence >= 90: return "The AI model is highly confident that the MRI shows patterns indicating significant cardiac abnormalities. This requires immediate medical evaluation."
        elif confidence >= 70: return "The AI model is reasonably confident that the MRI displays patterns suggestive of cardiac issues. Further investigation is strongly recommended."
        else: return "The AI model has detected potential abnormalities, but with lower confidence. A specialist's review is essential."

def get_recommendations_text(result_class, confidence):
    if result_class == 'Healthy':
        if confidence < 70: return "As confidence is moderate, a follow-up with a cardiologist is a good precautionary step."
        else: return "Continue regular cardiac health monitoring and maintain a heart-healthy lifestyle."
    else:
        base = "Immediate consultation with a cardiologist is strongly recommended. "
        if confidence >= 90: return base + "The high confidence suggests that advanced cardiac tests may be necessary."
        elif confidence >= 70: return base + "Further diagnostic tests are likely required."
        else: return base + "A thorough review by a radiologist is the critical next step."

# ===============================
# Main Application Routes
# ===============================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['username'] = request.form['username']
            return redirect(url_for('upload'))
        else:
            flash("Invalid credentials", "error")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET'])
def upload():
    if 'username' not in session: return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session: return redirect(url_for('login'))
    
    patient_id = request.form.get('patient_id', '').strip()
    patient_details = validate_patient(patient_id)
    if not patient_details:
        flash(f"Patient ID '{patient_id}' not found in the database.", "error")
        return redirect(url_for('upload'))

    if 'file' not in request.files or not request.files['file'].filename:
        flash("No file selected.", "error")
        return redirect(url_for('upload'))
    
    file = request.files['file']
    if allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        local_file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(local_file_path)

        result_class, predicted_class, confidence = predict_image(local_file_path)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        cos_file_name = f"{patient_id}-{timestamp}-{original_filename}"
        image_url = upload_file_to_cos(local_file_path, cos_file_name)

        if not image_url:
            flash("Failed to upload image to cloud storage. Check terminal for details.", "error")
            return redirect(url_for('upload'))
            
        update_success = update_patient_record(patient_id, image_url, predicted_class, confidence)
        if not update_success:
            flash("Failed to update patient record in the database.", "error")
            return redirect(url_for('upload'))

        prediction_data = {
            'patient_id': patient_id, 'patient_name': patient_details['PATIENT_NAME'],
            'image_url': image_url, 'result_class': result_class,
            'predicted_class': predicted_class, 'confidence': confidence,
            'interpretation': get_interpretation_text(result_class, confidence),
            'recommendations': get_recommendations_text(result_class, confidence),
            'scan_date': datetime.datetime.now().strftime('%Y-%m-%d')
        }
        session['prediction_data'] = prediction_data
        
        return render_template('result.html', **prediction_data)

    flash("Invalid file type.", "error")
    return redirect(url_for('upload'))

@app.route('/download_report')
def download_report():
    if 'username' not in session: return redirect(url_for('login'))
    prediction_data = session.get('prediction_data')
    if not prediction_data: return redirect(url_for('upload'))
    return render_template('report.html', **prediction_data)

@app.route('/graphs')
def graphs():
    if 'username' not in session: return redirect(url_for('login'))
    graph_urls = {
        'loss_accuracy': url_for('training_outputs_files', filename='graphs/loss_accuracy.png'),
        'confusion_matrix': url_for('training_outputs_files', filename='graphs/confusion_matrix.png'),
        'precision_recall_f1': url_for('training_outputs_files', filename='graphs/precision_recall_f1.png')
    }
    return render_template('graphs.html', graph_urls=graph_urls)

@app.route('/training_outputs/<path:filename>')
def training_outputs_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'training_outputs'), filename)

# ===================================================================
# API ENDPOINTS FOR WATSONX ASSISTANT - FULLY IMPLEMENTED
# ===================================================================
@app.route('/api/get_patient_details', methods=['POST'])
def get_patient_details():
    data = request.get_json()
    if not data or 'patient_id' not in data:
        return jsonify({"error": "patient_id is required"}), 400
    
    patient_id = data.get('patient_id')
    patient_data = validate_patient(patient_id)
    if patient_data:
        patient_data['found'] = True
        return jsonify(patient_data)y
    else:
        return jsonify({"found": False, "error": "Patient not found"}), 404

@app.route('/api/get_all_patients', methods=['GET'])
def get_all_patients():
    patient_list = get_all_patient_ids()
    if patient_list is not None:
        return jsonify({"patient_ids": patient_list, "count": len(patient_list)})
    else:
        return jsonify({"error": "Failed to retrieve data"}), 500

@app.route('/api/get_patient_count', methods=['GET'])
def api_get_patient_count():
    count = get_patient_count()
    if count is not None:
        return jsonify({"count": count})
    else:
        return jsonify({"error": "Failed to retrieve data"}), 500

@app.route('/api/get_diagnosis_count', methods=['POST'])
def api_get_diagnosis_count():
    data = request.get_json()
    diagnosis = data.get('diagnosis_type') 
    if not diagnosis:
        return jsonify({"error": "diagnosis_type is required"}), 400
    
    count = get_count_by_diagnosis(diagnosis)
    if count is not None:
        return jsonify({"diagnosis": diagnosis, "count": count})
    else:
        return jsonify({"error": "Failed to retrieve data"}), 500

# ===============================
# Run app with ngrok
# ===============================
if __name__ == '__main__':
    port_no = 7070 
    NGROK_AUTHTOKEN = "33YUDai9RzghFx5WCQs2c1EvBFS_84y3rjXmgy1vz33rE5V66"
    os.environ["NGROK_AUTHTOKEN"] = NGROK_AUTHTOKEN
    ngrok.kill()
    
    public_url = ngrok.connect(port_no).public_url
    print(f"✅ Your Flask app is publicly accessible at: {public_url}")
    
    app.run(port=port_no)

