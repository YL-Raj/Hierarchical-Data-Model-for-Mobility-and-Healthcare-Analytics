from flask import Flask, request, render_template, jsonify
import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        data = parse_csv(file)
        return jsonify(data)
# def parse_csv(file):
#     file_content = file.read().decode('utf-8').splitlines()
#     csv_reader = csv.reader(file_content)
#     data = {
#         'numLayers': 0,
#         'numNodes': [],
#         'layerNames': [],
#         'nodeLabels': []
#     }
#     for row in csv_reader:
#         if row[0] == 'numLayers':
#             data['numLayers'] = int(row[1])
#         elif row[0] == 'numNodes':
#             data['numNodes'] = list(map(int, row[1:]))
#         elif row[0] == 'layerNames':
#             data['layerNames'] = row[1:]
#         elif row[0] == 'nodeLabels':
#             data['nodeLabels'].append(row[1:])
#     return data

def parse_csv(file):
    file_content = file.read().decode('utf-8').splitlines()
    csv_reader = csv.reader(file_content)
    data = {
        'numLayers': 0,
        'numNodes': [],
        'layerNames': [],
        'nodeLabels': []
    }
    for row in csv_reader:
        if row[0] == 'numLayers':
            data['numLayers'] = int(row[1])
        elif row[0] == 'numNodes':
            data['numNodes'] = [int(x) for x in row[1:] if x]
        elif row[0] == 'layerNames':
            data['layerNames'] = [x for x in row[1:] if x]
        elif row[0] == 'nodeLabels':
            data['nodeLabels'].append([x for x in row[1:] if x])
    print(data)  # Debug print to check the parsed data
    return data

if __name__ == '__main__':
    app.run(debug=True)