#!/usr/bin/env python3
import argparse
import json
from app.workflow.workflow_engine import workflow_engine

def run_workflow(prompt):
    print(f"开始处理提示词: {prompt[:50]}...")
    
    session = workflow_engine.process_prompt(prompt)
    
    print(f"\n工作流执行完成!")
    print(f"Session ID: {session.session_id}")
    print(f"状态: {session.status}")
    print(f"飞书同步: {session.metadata.get('feishu_sync', '未知')}")
    print(f"创建时间: {session.created_at}")
    
    if session.status == "completed":
        print(f"\n输出产物:")
        try:
            output_json = json.loads(session.output)
            print(json.dumps(output_json, ensure_ascii=False, indent=2))
        except:
            print(session.output)
    
    return session

def sync_records(record_ids):
    print(f"同步记录ID: {record_ids}")
    results = workflow_engine.sync_to_feishu_by_ids(record_ids)
    
    for result in results:
        if result["success"]:
            print(f"✓ 记录 {result['record_id']} 同步成功")
        else:
            print(f"✗ 记录 {result['record_id']} 同步失败: {result['error']}")

def main():
    parser = argparse.ArgumentParser(description="工作流执行器 - 自动获取提示词、sessionid、输出产物并填充到飞书表格")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    process_parser = subparsers.add_parser('process', help='处理提示词并保存到飞书')
    process_parser.add_argument('prompt', type=str, help='要处理的提示词')
    
    sync_parser = subparsers.add_parser('sync', help='根据记录ID同步到飞书')
    sync_parser.add_argument('record_ids', type=str, nargs='+', help='飞书表格记录ID列表')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        run_workflow(args.prompt)
    elif args.command == 'sync':
        sync_records(args.record_ids)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()