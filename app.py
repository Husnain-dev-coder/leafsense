"""
LeafSense — AI Backend v7.0
Uses Groq AI (FREE - 14400 requests/day!)
Run: python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import io, os, json, base64
from datetime import datetime

app  = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# ✏️ PASTE YOUR GROQ API KEY HERE
# Get FREE key from: console.groq.com
# ─────────────────────────────────────────────
GROQ_API_KEY = "YOUR_GROQ_KEY_HERE"

# ─────────────────────────────────────────────
# DISEASE DATABASE
# ─────────────────────────────────────────────
DISEASE_INFO = {
    "Tomato___Bacterial_spot":{"display":"Tomato — Bacterial Spot","crop":"Tomato","severity":"Moderate","description":"Caused by Xanthomonas bacteria. Small dark water-soaked spots on leaves and fruit.","treatment":["Apply copper bactericide spray immediately.","Remove heavily infected leaves.","Avoid overhead irrigation."],"prevention":"Use disease-free seeds. Avoid wetting foliage."},
    "Tomato___Early_blight":{"display":"Tomato — Early Blight","crop":"Tomato","severity":"Moderate","description":"Caused by Alternaria solani. Dark bullseye-pattern lesions on lower leaves.","treatment":["Apply chlorothalonil fungicide every 7 days.","Remove infected lower leaves.","Water at base only."],"prevention":"Stake plants for airflow. Rotate crops 3 years."},
    "Tomato___Late_blight":{"display":"Tomato — Late Blight","crop":"Tomato","severity":"Severe","description":"Caused by Phytophthora infestans. Rapidly destroys entire plants.","treatment":["Apply copper fungicide IMMEDIATELY.","Remove and bag all infected material.","Do NOT compost infected plants."],"prevention":"Plant resistant varieties. Avoid planting near potatoes."},
    "Tomato___Leaf_Mold":{"display":"Tomato — Leaf Mold","crop":"Tomato","severity":"Moderate","description":"Caused by Passalora fulva. Yellow patches on upper leaf surface.","treatment":["Apply copper-based fungicide.","Reduce humidity.","Remove infected leaves."],"prevention":"Keep humidity below 85%. Space plants adequately."},
    "Tomato___Septoria_leaf_spot":{"display":"Tomato — Septoria Leaf Spot","crop":"Tomato","severity":"Moderate","description":"Caused by Septoria lycopersici. Small circular spots with dark borders.","treatment":["Apply chlorothalonil fungicide.","Remove infected lower leaves.","Avoid wetting foliage."],"prevention":"Stake plants. Rotate crops. Remove debris."},
    "Tomato___Spider_mites Two-spotted_spider_mite":{"display":"Tomato — Spider Mites","crop":"Tomato","severity":"Moderate","description":"Tetranychus urticae. Bronze stippling on leaves with fine webbing.","treatment":["Spray water jet on leaf undersides.","Apply neem oil weekly.","Use miticide for severe cases."],"prevention":"Maintain adequate soil moisture. Monitor regularly."},
    "Tomato___Target_Spot":{"display":"Tomato — Target Spot","crop":"Tomato","severity":"Moderate","description":"Caused by Corynespora cassiicola. Concentric ring spots on leaves.","treatment":["Apply chlorothalonil fungicide.","Remove infected material.","Improve air circulation."],"prevention":"Avoid dense planting. Rotate crops."},
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus":{"display":"Tomato — Yellow Leaf Curl Virus","crop":"Tomato","severity":"Severe","description":"Viral disease spread by whiteflies. Severe leaf curling and yellowing.","treatment":["Remove infected plants immediately.","Control whiteflies with neem oil.","Use yellow sticky traps."],"prevention":"Plant virus-resistant varieties. Control whitefly from day one."},
    "Tomato___Tomato_mosaic_virus":{"display":"Tomato — Mosaic Virus","crop":"Tomato","severity":"Severe","description":"Viral disease causing mottled green mosaic pattern on leaves.","treatment":["Remove infected plants.","Disinfect tools with bleach solution.","Control aphid vectors."],"prevention":"Use certified virus-free seeds."},
    "Tomato___healthy":{"display":"Tomato — Healthy","crop":"Tomato","severity":"None","description":"Your tomato plant looks perfectly healthy!","treatment":["No treatment needed!"],"prevention":"Continue regular watering and weekly scouting."},
    "Potato___Early_blight":{"display":"Potato — Early Blight","crop":"Potato","severity":"Moderate","description":"Caused by Alternaria solani. Dark concentric ring lesions on leaves.","treatment":["Apply chlorothalonil fungicide.","Remove infected leaves.","Avoid overhead watering."],"prevention":"Use certified seed potatoes. 3-year crop rotation."},
    "Potato___Late_blight":{"display":"Potato — Late Blight","crop":"Potato","severity":"Severe","description":"Caused by Phytophthora infestans. Rapidly destroys plants and tubers.","treatment":["Apply metalaxyl IMMEDIATELY.","Remove ALL infected material.","Consider early harvest."],"prevention":"Plant resistant varieties. Use preventive fungicides."},
    "Potato___healthy":{"display":"Potato — Healthy","crop":"Potato","severity":"None","description":"Your potato plant looks healthy!","treatment":["No treatment required."],"prevention":"Scout regularly during wet cool periods."},
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot":{"display":"Corn — Gray Leaf Spot","crop":"Corn","severity":"Moderate","description":"Caused by Cercospora zeae-maydis. Rectangular gray-tan lesions.","treatment":["Apply strobilurin fungicide.","Rotate crops.","Till crop debris."],"prevention":"Plant resistant hybrids. Improve drainage."},
    "Corn_(maize)___Common_rust_":{"display":"Corn — Common Rust","crop":"Corn","severity":"Moderate","description":"Caused by Puccinia sorghi. Cinnamon-brown pustules on leaves.","treatment":["Apply propiconazole fungicide.","Scout fields regularly."],"prevention":"Plant rust-resistant hybrids. Early planting."},
    "Corn_(maize)___Northern_Leaf_Blight":{"display":"Corn — Northern Leaf Blight","crop":"Corn","severity":"Severe","description":"Caused by Exserohilum turcicum. Large cigar-shaped tan lesions.","treatment":["Apply azoxystrobin at tassel stage.","Destroy infected debris."],"prevention":"Plant resistant hybrids. Rotate crops."},
    "Corn_(maize)___healthy":{"display":"Corn — Healthy","crop":"Corn","severity":"None","description":"Your corn plant looks healthy!","treatment":["No treatment required."],"prevention":"Maintain balanced nutrition. Scout regularly."},
    "Apple___Apple_scab":{"display":"Apple — Apple Scab","crop":"Apple","severity":"Moderate","description":"Caused by Venturia inaequalis. Dark scabby lesions on leaves and fruit.","treatment":["Apply captan fungicide every 7-10 days.","Rake fallen leaves.","Prune for air circulation."],"prevention":"Avoid overhead irrigation. Apply lime-sulfur before bud break."},
    "Apple___Black_rot":{"display":"Apple — Black Rot","crop":"Apple","severity":"Severe","description":"Caused by Botryosphaeria obtusa. Affects fruit, leaves, and bark.","treatment":["Remove mummified fruit and infected branches.","Apply copper fungicide.","Disinfect pruning tools."],"prevention":"Maintain tree vigor. Remove cankers promptly."},
    "Apple___Cedar_apple_rust":{"display":"Apple — Cedar Apple Rust","crop":"Apple","severity":"Moderate","description":"Caused by Gymnosporangium. Bright orange spots on leaves.","treatment":["Apply myclobutanil fungicide.","Remove nearby cedar trees."],"prevention":"Plant rust-resistant apple cultivars."},
    "Apple___healthy":{"display":"Apple — Healthy","crop":"Apple","severity":"None","description":"Your apple plant looks healthy!","treatment":["No treatment required."],"prevention":"Continue regular monitoring and fertilization."},
    "Grape___Black_rot":{"display":"Grape — Black Rot","crop":"Grape","severity":"Severe","description":"Caused by Guignardia bidwellii. Brown leaf spots and black fruit.","treatment":["Apply mancozeb from bud break.","Remove mummified berries.","Prune for air circulation."],"prevention":"Apply fungicide from bud break through veraison."},
    "Grape___Esca_(Black_Measles)":{"display":"Grape — Black Measles","crop":"Grape","severity":"Severe","description":"Fungal complex. Tiger-stripe leaves and dark berry spots.","treatment":["Remove severely infected vines.","Protect pruning wounds."],"prevention":"Avoid large pruning wounds."},
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)":{"display":"Grape — Leaf Blight","crop":"Grape","severity":"Moderate","description":"Caused by Pseudocercospora vitis. Dark brown spots with yellow halos.","treatment":["Apply mancozeb fungicide.","Remove infected leaves.","Improve air circulation."],"prevention":"Maintain good vine training."},
    "Grape___healthy":{"display":"Grape — Healthy","crop":"Grape","severity":"None","description":"Your grapevine looks healthy!","treatment":["No treatment required."],"prevention":"Maintain preventive fungicide during humid seasons."},
    "Pepper,_bell___Bacterial_spot":{"display":"Pepper — Bacterial Spot","crop":"Pepper","severity":"Moderate","description":"Caused by Xanthomonas. Dark water-soaked lesions on leaves.","treatment":["Apply copper bactericide.","Avoid overhead irrigation.","Remove infected leaves."],"prevention":"Use disease-free transplants. Rotate crops."},
    "Pepper,_bell___healthy":{"display":"Pepper — Healthy","crop":"Pepper","severity":"None","description":"Your bell pepper looks healthy!","treatment":["No treatment required."],"prevention":"Water consistently and fertilize monthly."},
}

# ─────────────────────────────────────────────
# LOAD LOCAL MODEL
# ─────────────────────────────────────────────
MODEL       = None
CLASS_NAMES = []

def load_model():
    global MODEL, CLASS_NAMES
    if os.path.exists("class_names.json"):
        with open("class_names.json") as f:
            CLASS_NAMES = json.load(f)
        print(f"✅ {len(CLASS_NAMES)} class names loaded")
    if os.path.exists("plant_disease_model.h5"):
        try:
            import tensorflow as tf
            MODEL = tf.keras.models.load_model(
                "plant_disease_model.h5",
                compile=False
            )
            print("✅ Local model loaded!")
        except Exception as e:
            print(f"⚠️  Model load error: {e}")


# ─────────────────────────────────────────────
# GROQ VISION — Plant Disease Detection
# ─────────────────────────────────────────────
def analyze_with_groq(image_bytes):
    """Send image to Groq LLaMA Vision for plant disease diagnosis."""
    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)

        # Convert image to base64
        img     = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Resize to reduce tokens
        img.thumbnail((800, 800))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        print("🤖 Calling Groq Vision...")

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": """You are LeafSense, an expert agricultural AI 
specializing in plant disease detection. Always respond ONLY with valid JSON.
No text before or after the JSON."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """Analyze this plant image. Respond ONLY with this JSON:
{
    "disease": "disease name or Healthy PlantName",
    "crop": "Tomato or Potato or Corn or Apple or Grape or Pepper or Other",
    "confidence": 90,
    "severity": "None or Mild or Moderate or Severe",
    "description": "1-2 sentence scientific description",
    "treatment": ["step 1", "step 2", "step 3"],
    "prevention": "one sentence prevention tip",
    "is_plant": true
}
Rules:
- confidence is number 0-100
- severity None only for healthy
- is_plant false if no plant in image
- ONLY return JSON nothing else"""
                        }
                    ]
                }
            ],
            max_tokens=600,
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()

        # Clean markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        print(f"✅ Groq: {result.get('disease')} ({result.get('confidence')}%)")
        return result

    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        return None
    except Exception as e:
        print(f"Groq error: {e}")
        return None


# ─────────────────────────────────────────────
# LOCAL MODEL FALLBACK
# ─────────────────────────────────────────────
def run_local_model(image_bytes):
    try:
        img   = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr   = np.array(img.resize((224,224)), dtype=np.float32) / 255.0
        arr   = np.expand_dims(arr, axis=0)
        preds = MODEL.predict(arr, verbose=0)[0]
        top5  = np.argsort(preds)[::-1][:5]

        top_cls = CLASS_NAMES[top5[0]]
        conf    = float(preds[top5[0]])
        info    = DISEASE_INFO.get(top_cls, {
            "display":"Unknown","crop":"Unknown","severity":"Unknown",
            "description":"Disease detected.",
            "treatment":["Consult a local agronomist."],
            "prevention":"Regular monitoring recommended."
        })

        alts = []
        for i in top5[1:4]:
            cls   = CLASS_NAMES[i]
            info2 = DISEASE_INFO.get(cls, {})
            alts.append({
                "disease"   : info2.get("display", cls),
                "crop"      : info2.get("crop",""),
                "confidence": round(float(preds[i])*100, 1)
            })

        return {
            "disease"    : info["display"],
            "crop"       : info.get("crop",""),
            "confidence" : round(conf*100, 1),
            "severity"   : info["severity"],
            "description": info["description"],
            "treatment"  : info["treatment"],
            "prevention" : info["prevention"],
        }, alts

    except Exception as e:
        print(f"Local model error: {e}")
        return None, []


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    groq_ready = GROQ_API_KEY != "YOUR_GROQ_KEY_HERE"
    return jsonify({
        "app"  : "LeafSense AI v7.0",
        "groq" : "ready" if groq_ready else "not configured",
        "model": "loaded" if MODEL else "not loaded",
    })


@app.route("/api/health")
def health():
    groq_ready = GROQ_API_KEY != "YOUR_GROQ_KEY_HERE"
    return jsonify({
        "status"   : "optimal",
        "groq"     : "ready" if groq_ready else "not configured",
        "model"    : "loaded" if MODEL else "not loaded",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/detect", methods=["POST"])
def detect():
    image_bytes = None

    if "image" in request.files:
        f = request.files["image"]
        if f.filename == "":
            return jsonify({"error": "No file selected"}), 400
        image_bytes = f.read()
    elif request.is_json:
        data = request.get_json()
        if "image" in data:
            b64 = data["image"]
            if "," in b64:
                b64 = b64.split(",")[1]
            image_bytes = base64.b64decode(b64)

    if not image_bytes:
        return jsonify({"error": "No image provided"}), 400

    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception:
        return jsonify({"error": "Invalid image file"}), 400

    diagnosis    = None
    alternatives = []
    mode         = "unknown"

    # Try Groq first
    groq_ready = GROQ_API_KEY != "YOUR_GROQ_KEY_HERE"
    if groq_ready:
        result = analyze_with_groq(image_bytes)
        if result and result.get("is_plant", True):
            diagnosis = {
                "disease"    : result.get("disease","Unknown"),
                "crop"       : result.get("crop","Unknown"),
                "confidence" : result.get("confidence", 0),
                "severity"   : result.get("severity","Unknown"),
                "description": result.get("description",""),
                "treatment"  : result.get("treatment",[]),
                "prevention" : result.get("prevention",""),
            }
            mode = "groq_vision"

    # Fallback to local model
    if diagnosis is None and MODEL is not None:
        diagnosis, alternatives = run_local_model(image_bytes)
        mode = "local_model"

    if diagnosis is None:
        return jsonify({
            "error": "Detection failed. Check Groq API key in App.py"
        }), 500

    return jsonify({
        "success"     : True,
        "timestamp"   : datetime.now().isoformat(),
        "mode"        : mode,
        "diagnosis"   : diagnosis,
        "alternatives": alternatives,
        "report_id"   : f"LS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    })


@app.route("/api/diseases")
def list_diseases():
    return jsonify({
        "total"   : len(DISEASE_INFO),
        "crops"   : ["Tomato","Potato","Corn","Apple","Grape","Pepper"],
        "diseases": [
            {"id":k,"name":v["display"],
             "crop":v["crop"],"severity":v["severity"]}
            for k,v in DISEASE_INFO.items()
        ]
    })


if __name__ == "__main__":
    print("\n"+"="*55)
    print("  🌿 LeafSense AI Backend v7.0")
    print("  Groq LLaMA Vision (FREE 14400/day!)")
    print("="*55)
    load_model()
    groq_ready = GROQ_API_KEY != "YOUR_GROQ_KEY_HERE"
    print(f"\n  🚀 Groq Vision  : {'✅ Ready' if groq_ready else '⚠️  Add API key'}")
    print(f"  🧠 Local Model  : {'✅ Loaded' if MODEL else '⚠️  Not loaded'}")
    print(f"  📡 API URL      : http://127.0.0.1:5000")
    print("="*55+"\n")
    app.run(debug=True, host="127.0.0.1", port=5000)