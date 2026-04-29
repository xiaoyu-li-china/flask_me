from flask import request, jsonify
from app.workflow import workflow
from app.workflow.workflow_engine import workflow_engine

@workflow.route('/api/workflow/process', methods=['POST'])
def process_prompt():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "缺少提示词参数"}), 400
    
    prompt = data.get('prompt', '')
    if not prompt.strip():
        return jsonify({"error": "提示词不能为空"}), 400
    
    try:
        session = workflow_engine.process_prompt(prompt)
        return jsonify({
            "success": True,
            "session_id": session.session_id,
            "prompt": session.prompt,
            "output": session.output,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "feishu_sync": session.metadata.get("feishu_sync", "unknown")
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workflow.route('/api/workflow/session/<session_id>', methods=['GET'])
def get_session(session_id):
    session = workflow_engine.get_session(session_id)
    if not session:
        return jsonify({"error": "会话不存在"}), 404
    
    return jsonify({
        "success": True,
        "session_id": session.session_id,
        "prompt": session.prompt,
        "output": session.output,
        "status": session.status,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "metadata": session.metadata
    }), 200

@workflow.route('/api/workflow/session/<session_id>', methods=['PUT'])
def update_session(session_id):
    session = workflow_engine.get_session(session_id)
    if not session:
        return jsonify({"error": "会话不存在"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少更新数据"}), 400
    
    update_fields = {}
    if 'prompt' in data:
        update_fields['prompt'] = data['prompt']
    if 'output' in data:
        update_fields['output'] = data['output']
    if 'status' in data:
        update_fields['status'] = data['status']
    
    if not update_fields:
        return jsonify({"error": "没有可更新的字段"}), 400
    
    success = workflow_engine.update_feishu_record(session_id, **update_fields)
    
    return jsonify({
        "success": success,
        "message": "更新成功" if success else "更新失败"
    }), 200

@workflow.route('/api/workflow/sync', methods=['POST'])
def sync_to_feishu():
    data = request.get_json()
    if not data or 'record_ids' not in data:
        return jsonify({"error": "缺少record_ids参数"}), 400
    
    record_ids = data.get('record_ids', [])
    if not isinstance(record_ids, list) or len(record_ids) == 0:
        return jsonify({"error": "record_ids必须是非空数组"}), 400
    
    results = workflow_engine.sync_to_feishu_by_ids(record_ids)
    
    return jsonify({
        "success": True,
        "results": results
    }), 200

@workflow.route('/api/workflow/create', methods=['POST'])
def create_session():
    data = request.get_json()
    prompt = data.get('prompt', '') if data else ''
    
    session = workflow_engine.create_session(prompt)
    
    return jsonify({
        "success": True,
        "session_id": session.session_id,
        "prompt": session.prompt,
        "status": session.status,
        "created_at": session.created_at.isoformat()
    }), 201