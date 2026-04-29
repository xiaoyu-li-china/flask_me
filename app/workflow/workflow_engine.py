import uuid
import time
import json
from datetime import datetime
from app.utils.feishu_api import FeishuAPI

class WorkflowContext:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.prompt = ""
        self.output = ""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = "pending"
        self.metadata = {}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

class WorkflowEngine:
    def __init__(self):
        self.feishu = FeishuAPI()
        self.table_id = "tbluRCjMyaMmWX8h"
        self.contexts = {}

    def create_session(self, prompt=""):
        context = WorkflowContext()
        if prompt:
            context.prompt = prompt
        self.contexts[context.session_id] = context
        return context

    def get_session(self, session_id):
        return self.contexts.get(session_id)

    def process_prompt(self, prompt):
        session = self.create_session(prompt)
        session.status = "processing"
        
        try:
            output = self.execute_workflow(session)
            session.output = output
            session.status = "completed"
            
            success = self.save_to_feishu(session)
            if success:
                session.metadata["feishu_sync"] = "success"
            else:
                session.metadata["feishu_sync"] = "failed"
                
        except Exception as e:
            session.output = f"Error: {str(e)}"
            session.status = "failed"
            session.metadata["error"] = str(e)
        
        session.update()
        return session

    def execute_workflow(self, session):
        steps = [
            self.step_analyze_prompt,
            self.step_generate_output,
            self.step_format_result
        ]
        
        result = {}
        for step in steps:
            step_name = step.__name__
            try:
                step_result = step(session)
                result[step_name] = step_result
            except Exception as e:
                result[step_name] = {"error": str(e)}
        
        return json.dumps(result, ensure_ascii=False, indent=2)

    def step_analyze_prompt(self, session):
        return {
            "status": "completed",
            "prompt_length": len(session.prompt),
            "analysis_time": datetime.now().isoformat(),
            "summary": "Prompt analyzed successfully"
        }

    def step_generate_output(self, session):
        processed_output = {
            "processed_prompt": session.prompt,
            "generated_content": f"基于提示词 '{session.prompt[:50]}...' 生成的产物内容",
            "generation_time": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        return processed_output

    def step_format_result(self, session):
        return {
            "status": "formatted",
            "format": "json",
            "timestamp": datetime.now().isoformat(),
            "session_id": session.session_id
        }

    def save_to_feishu(self, session):
        try:
            record = {
                "提示词": session.prompt,
                "SessionID": session.session_id,
                "输出产物": session.output,
                "状态": session.status,
                "创建时间": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "更新时间": session.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            result = self.feishu.add_record(self.table_id, record)
            if result:
                session.metadata["feishu_record_id"] = result.get("record_id")
                return True
            return False
        except Exception as e:
            print(f"保存到飞书失败: {str(e)}")
            return False

    def update_feishu_record(self, session_id, **kwargs):
        session = self.get_session(session_id)
        if not session:
            return False
        
        record_id = session.metadata.get("feishu_record_id")
        if not record_id:
            return False
        
        try:
            update_data = {}
            if "prompt" in kwargs:
                update_data["提示词"] = kwargs["prompt"]
                session.prompt = kwargs["prompt"]
            if "output" in kwargs:
                update_data["输出产物"] = kwargs["output"]
                session.output = kwargs["output"]
            if "status" in kwargs:
                update_data["状态"] = kwargs["status"]
                session.status = kwargs["status"]
            
            if update_data:
                update_data["更新时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.feishu.update_record(self.table_id, record_id, update_data)
                session.update()
                return True
            return False
        except Exception as e:
            print(f"更新飞书记录失败: {str(e)}")
            return False

    def sync_to_feishu_by_ids(self, record_ids):
        results = []
        for record_id in record_ids:
            try:
                record = self.feishu.get_record(self.table_id, record_id)
                results.append({"record_id": record_id, "success": True, "data": record})
            except Exception as e:
                results.append({"record_id": record_id, "success": False, "error": str(e)})
        return results

workflow_engine = WorkflowEngine()