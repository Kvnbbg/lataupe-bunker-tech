from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    # Access query parameters
    id_param = request.args.get('id')
    vscode_browser_req_id = request.args.get('vscodeBrowserReqId')
    
    # Log the parameters (optional)
    app.logger.info(f"Received request with id: {id_param} and vscodeBrowserReqId: {vscode_browser_req_id}")
    
    # Return a response
    return jsonify({
        "message": "Welcome to Lataupe Bunker Tech!",
        "id": id_param,
        "vscodeBrowserReqId": vscode_browser_req_id
    })

if __name__ == '__main__':
    app.run(debug=True)