import requests
from flask import Flask, request, jsonify
import ddddocr
app = Flask(__name__)

ocr_model_default = ddddocr.DdddOcr(det=False)
ocr_model_beta = ddddocr.DdddOcr(beta=True)
det = ddddocr.DdddOcr(det=True, ocr=False)
slide = ddddocr.DdddOcr(det=False, ocr=False)
@app.route('/ocr', methods=['POST'])
def ddocr():
    try:
        img = request.form.get('img')
        model = request.form.get('model', 'default')
        png_type = request.form.get('png_type', 'default')
        response = requests.get(img, timeout=10)
        if img:
            if response.status_code != 200:
                return jsonify({"error": f"Failed to fetch image. HTTP status code: {response.status_code}"}), 400
            image = response.content
            # 初始化 ddddocr 模型
            if model=="beta":
                #模型2
                ocr = ocr_model_beta
            else:
                #默认模型
                ocr = ocr_model_default
            # image = open(img, "rb").read()
            if png_type=="png_fix":
                result = ocr.classification(image, png_fix=True)
            else:
                result = ocr.classification(image)
            print(result)
            return jsonify({"result": result})
        else:
            return jsonify({"error": "Image Not Found"})
    except:
        return jsonify({"error": "unknown"})
@app.route('/bbox', methods=['POST'])
def bbox():
    try:
        img = request.form.get('img')
        if img:
            response = requests.get(img, timeout=10)
            if response.status_code != 200:
                return jsonify({"error": f"Failed to fetch image. HTTP status code: {response.status_code}"}), 400
            image = response.content
            bboxes = det.detection(image)
            print(bboxes)
            return jsonify({"result": bboxes})
        else:
            return jsonify({"error": "Image Not Found"})
    except:
        return jsonify({"error": "unknown"})
@app.route('/slide', methods=['POST'])
def slidefun():
    try:
        target = request.form.get('target')
        background=request.form.get('background')
        model=request.form.get('model', 'model1')
        simple_target=request.form.get('type', 'default')
        if target and background:
            response_t = requests.get(target, timeout=10)
            response_b = requests.get(background, timeout=10)
            if response_t.status_code != 200 or response_b.status_code != 200:
                return jsonify({"error": f"Failed to fetch image. HTTP status code: target:{response_t.status_code} background:{response_b.status_code}"}), 400
            response_t= response_t.content
            response_b= response_b.content
            if simple_target=="simple_target":
                if model == "model2":
                    res = slide.slide_comparison(response_t, response_b, simple_target=True)
                else:
                    res = slide.slide_match(response_t, response_b, simple_target=True)
            else:
                if model=="model2":
                    res = slide.slide_comparison(response_t, response_b)
                else:
                    res = slide.slide_match(response_t, response_b)
            print(res)
            return jsonify({"result": res})
        else:
            return jsonify({"error": "Image Not Found"})
    except:
        return jsonify({"error": "unknown"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8052)
