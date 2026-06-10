from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

# اگر فایل اصلی شما index.html است
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# برای دسترسی به همه فایل‌ها (css, js, images و ...)
@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)