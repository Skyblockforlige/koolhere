import os
import sys
import time
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Lock
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
app   = Flask(__name__)
HANDWRITING_ENV      = "handwriting"
OUTPUT_DIR      = Path("handwriting_from_image/axidrawtests")
TEMP_SVG      = OUTPUT_DIR / "api_generated.svg"
CLEANED_SVG      = OUTPUT_DIR / "api_cleaned.svg"
DEFAULT_PORT      = "COM3"
DEFAULT_BIAS      = 0.65
DEFAULT_STYLE      = 5
FIXED_Y_OFFSET_MM      = 82.55
plot_lock   = Lock()
current_status = {
    "is_plotting": False,
    "current_text": None,
    "last_plot_time": None,
    "last_error": None
}
def split_lines_simple(text, limit=40):
    text = str(text).replace("\r", "")
    chunks = text.split("\n")
    final_lines = []
    for part in chunks:
        part = part.strip()
        if part == "":
            continue
        words = part.split()
        now = ""
        for word in words:
            if now == "":
                now = word
            else:
                maybe = now + " " + word
                if len(maybe) <= limit:
                    now = maybe
                else:
                    final_lines.append(now)
                    now = word
        if now != "":
            final_lines.append(now)
    return final_lines
def clean_svg(svg_path, output_path=None):
    if output_path is None:
        output_path = svg_path
    tree = ET.parse(svg_path)
    root = tree.getroot()
    bad = []
    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        if tag in ["rect", "line", "circle", "polygon", "polyline"]:
            bad.append(elem)
    for elem in bad:
        parent = None
        for maybe_parent in root.iter():
            if elem in maybe_parent:
                parent = maybe_parent
                break
        if parent is not None:
            try:
                parent.remove(elem)
            except:
                pass
    root.set("width", "150mm")
    root.set("height", "150mm")
    if "viewBox" in root.attrib:
        root.set("viewBox", root.get("viewBox").replace(",", " "))
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    return str(output_path)
def write_temp_script(lines, bias, style, output_path):
    temp_script = Path("temp_generate.py")
    text = f'''
import sys
import warnings
import os
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from demo import Hand
text_lines = {lines}
bias = {bias}
style = {style}
output_path = r"{output_path}"
hand = Hand()
biases = [bias] * len(text_lines)
styles = [style] * len(text_lines)
hand.write(filename=output_path, lines=text_lines, biases=biases, styles=styles)
print("SUCCESS")
'''
    temp_script.write_text(text)
    return temp_script
def generate_handwriting(lines, bias=DEFAULT_BIAS, style=DEFAULT_STYLE, output_path=None):
    if output_path is None:
        output_path = str(TEMP_SVG)
    temp_script = write_temp_script(lines, bias, style, output_path)
    conda_base = os.environ.get("CONDA_PREFIX", r"C:\Users\mrmaa\Anaconda3")
    activate_script = os.path.join(conda_base, "Scripts", "activate.bat")
    batch_script = Path("temp_run.bat")
    batch_text = f'''@echo off
call "{activate_script}" {HANDWRITING_ENV}
python "{temp_script}"
'''
    batch_script.write_text(batch_text)
    try:
        result = subprocess.run(
            [str(batch_script)],
            capture_output=True,
            text=True,
            timeout=120,
            shell=True
        )
        if result.returncode != 0:
            raise Exception(result.stderr if result.stderr else "generation failed")
        if not Path(output_path).exists():
            raise Exception("svg was not created")
        return str(output_path)
    finally:
        if temp_script.exists():
            temp_script.unlink()
        if batch_script.exists():
            batch_script.unlink()
def plot_svg(svg_path, port=DEFAULT_PORT, offset_y_mm=FIXED_Y_OFFSET_MM):
    result = subprocess.run(
        [
            "python",
            "plot_no_scale.py",
            str(svg_path),
            "--port",
            str(port),
            "--offset-y",
            str(offset_y_mm)
        ],
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode != 0:
        raise Exception(result.stderr if result.stderr else "plot failed")
    return str(svg_path)
def get_lines_from_request(data):
    if "lines" in data:
        lines = data.get("lines")

        if isinstance(lines, list):
            out = []
            for item in lines:
                piece = str(item).strip()
                if piece != "":
                    out.append(piece)
            return out

    if "text" in data:

        return split_lines_simple(data.get("text", ""))

    if "smart_text" in data:

        return split_lines_simple(data.get("smart_text", "").replace("\\n", "\n"))

    return []

@app.route("/", methods=["GET"])
def home():

    return jsonify(
        {
            "name": "AxiDraw Handwriting Plotter API",
            "version": "simple",
            "routes": ["/plot", "/health", "/status"]
        }
    )

@app.route("/health", methods=["GET"])
def health():

    return jsonify(
        {
            "status": "healthy",
            "time": datetime.now().isoformat(),
            "is_plotting": current_status["is_plotting"]
        }
    )

@app.route("/status", methods=["GET"])
def status():

    return jsonify(current_status)

@app.route("/plot", methods=["POST"])
def plot_text():

    start = time.time()

    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "no json"}), 400

        lines = get_lines_from_request(data)

        last_line = data.get("last_line")

        if last_line is not None:
            last_line = str(last_line).strip()
            if last_line != "":
                lines.append(last_line)

        if not lines:
            return jsonify({"status": "error", "message": "no text found"}), 400

        bias = data.get("bias", DEFAULT_BIAS)
        style = data.get("style", DEFAULT_STYLE)
        port = data.get("port", DEFAULT_PORT)
        y_offset_inches = data.get("y_offset_inches")

        if y_offset_inches is None:
            offset_y_mm = FIXED_Y_OFFSET_MM
        else:
            offset_y_mm = float(y_offset_inches) * 25.4

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with plot_lock:

            current_status["is_plotting"] = True
            current_status["current_text"] = lines
            current_status["last_error"] = None

            try:
                if TEMP_SVG.exists():
                    TEMP_SVG.unlink()

                if CLEANED_SVG.exists():
                    CLEANED_SVG.unlink()

                svg_path = generate_handwriting(
                    lines,
                    bias=bias,
                    style=style,
                    output_path=str(TEMP_SVG)
                )

                cleaned_path = clean_svg(svg_path, CLEANED_SVG)

                plot_svg(cleaned_path, port=port, offset_y_mm=offset_y_mm)

                total = round(time.time() - start, 2)

                current_status["last_plot_time"] = datetime.now().isoformat()

                return jsonify(
                    {
                        "status": "success",
                        "message": "done",
                        "svg_path": cleaned_path,
                        "plot_time_seconds": total,
                        "text_plotted": lines
                    }
                )

            except Exception as e:
                current_status["last_error"] = str(e)
                return jsonify(
                    {
                        "status": "error",
                        "message": str(e),
                        "time": datetime.now().isoformat()
                    }
                ), 500

            finally:
                current_status["is_plotting"] = False
                current_status["current_text"] = None

    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": str(e),
                "time": datetime.now().isoformat()
            }
        ), 500

if __name__ == "__main__":

    print("AxiDraw Handwriting API")
    print("http://localhost:5000")
    print("simple mode")
    print("")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)