from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
from bson.objectid import ObjectId

# Khởi tạo Flask app và cho phép CORS
app = Flask(__name__)
CORS('*')

# MongoDB connection
mongo_url = "mongodb+srv://ip6ofme:JL1S4hjMWRoko8AJ@cluster0.x0vo0.mongodb.net/"
client = pymongo.MongoClient(mongo_url)
db = client["test"]
pdf_collection = db["PdfDetails"]
voter_collection = db["Voters"]

@app.route('/')
def home():
    return "Welcome to the IDEATHON API!"
# API để upload file và lưu thông tin vào MongoDB
@app.route('/upload-files', methods=['POST'])
def upload_file():
    # Chỉ lưu thông tin vào MongoDB
    title = request.form.get('title')
    group = request.form.get('group')
    firebase_url = request.form.get('url')
    new_pdf = {
        'title': title,
        'group': group,
        'url': firebase_url,
        'votes': 0
    }
    result = pdf_collection.insert_one(new_pdf)
    return jsonify({'status': 'ok', 'id': str(result.inserted_id)})

# API để tăng số lượng vote của file dựa trên ID
@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    file_id = data.get('id')

    try:
        file = pdf_collection.find_one({'_id': ObjectId(file_id)})
        if not file:
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        pdf_collection.update_one({'_id': ObjectId(file_id)}, {'$inc': {'votes': 1}})
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API để lấy số lượng votes của file theo ID
@app.route('/get-votes', methods=['GET'])
def get_votes():
    file_id = request.args.get('id')

    try:
        file = pdf_collection.find_one({'_id': ObjectId(file_id)})
        if not file:
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        return jsonify({'status': 'ok', 'votes': file.get('votes', 0)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API để lấy danh sách tất cả các file
@app.route('/get-files', methods=['GET'])
def get_files():
    try:
        files = pdf_collection.find({})
        file_list = []
        for file in files:
            file_list.append({
                'id': str(file['_id']),
                'title': file['title'],
                'group': file['group'],
                'url': file['url'],
                'votes': file.get('votes', 0)
            })
        return jsonify({'status': 'ok', 'data': file_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API mới để đăng ký người bình chọn
@app.route('/register-voter', methods=['POST'])
def register_voter():
    data = request.json
    name = data.get('name')
    group = data.get('group')
    role = data.get('role')  # Thêm trường role
    
    new_voter = {
        'name': name,
        'group': group,
        'role': role,  # Lưu role vào MongoDB
        'number_of_votes': 0
    }
    result = voter_collection.insert_one(new_voter)
    return jsonify({'status': 'ok', 'id': str(result.inserted_id)})

# API mới để bình chọn
@app.route('/vote-by-voter', methods=['POST'])
def vote_by_voter():
    data = request.json
    voter_id = data.get('voter_id')
    file_id = data.get('file_id')
    
    voter = voter_collection.find_one({'_id': ObjectId(voter_id)})
    if not voter:
        return jsonify({'status': 'error', 'message': 'Voter not found'}), 404
    
    max_votes = 5 if voter['role'] == 'judge' else 2
    
    if voter['number_of_votes'] >= max_votes:
        return jsonify({'status': 'error', 'message': 'Maximum votes reached'}), 400
    
    # Tăng số lượt bình chọn của người dùng
    voter_collection.update_one({'_id': ObjectId(voter_id)}, {'$inc': {'number_of_votes': 1}})
    
    # Tăng số lượt bình chọn cho file
    pdf_collection.update_one({'_id': ObjectId(file_id)}, {'$inc': {'votes': 1}})
    
    return jsonify({'status': 'ok', 'message': 'Vote recorded successfully'})

# API để lấy thông tin người bình chọn
@app.route('/get-voter', methods=['GET'])
def get_voter():
    voter_id = request.args.get('id')
    voter = voter_collection.find_one({'_id': ObjectId(voter_id)})
    if not voter:
        return jsonify({'status': 'error', 'message': 'Voter not found'}), 404
    return jsonify({
        'status': 'ok',
        'name': voter['name'],
        'group': voter['group'],
        'role': voter['role'],  # Thêm role vào phản hồi
        'number_of_votes': voter['number_of_votes']
    })

# Khởi chạy server
if __name__ == "__main__":
    app.run(port=5000, debug=True)
