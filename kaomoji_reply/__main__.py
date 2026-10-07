import argparse
import json
from pathlib import Path
from .engine import decorate
from .model import local_server,reply
from .information import assess


def main():
    parser=argparse.ArgumentParser(description='情景文字 → 中文回应 → 颜文字')
    parser.add_argument('context',nargs='?')
    parser.add_argument('--input',type=Path,help='UTF-8情景文本文件')
    parser.add_argument('--batch',type=Path,help='JSON情景列表，每项包含name与context')
    parser.add_argument('--relationship',choices=['friend','colleague','neutral'],default='friend')
    parser.add_argument('--density','--strength',dest='strength',choices=['none','light','medium','high'],default='light')
    parser.add_argument('--all-densities',action='store_true',help='同一正文比较四档密度')
    parser.add_argument('--variant',type=int,default=2)
    parser.add_argument('--output',type=Path,default=Path('outputs/latest'))
    args=parser.parse_args()
    if sum(bool(x) for x in [args.context,args.input,args.batch])!=1: parser.error('提供context、--input或--batch其中一项')
    if args.batch: cases=json.loads(args.batch.read_text(encoding='utf-8-sig'))
    else: cases=[{'name':'回应','context':args.context or args.input.read_text(encoding='utf-8-sig')}]
    if not isinstance(cases,list) or not cases: parser.error('批量输入必须为非空列表')
    for case in cases:
        if not isinstance(case,dict) or not isinstance(case.get('context'),str) or not case['context'].strip(): parser.error('每项必须包含非空context')
        case.setdefault('name','回应')
        if case.get('relationship',args.relationship) not in ['friend','colleague','neutral']: parser.error('关系类型无效')
    if args.variant<0: parser.error('variant不能为负数')
    args.output.mkdir(parents=True,exist_ok=True)
    results=[]
    with local_server():
        for case in cases:
            if not isinstance(case.get('context'),str) or not case['context'].strip(): raise ValueError('情景不能为空')
            relationship=case.get('relationship',args.relationship)
            information,information_trace=assess(case['context'],relationship)
            if information.get('provisional_reply') or information['status']=='insufficient':
                parsed={'sentences':[information.get('provisional_reply','我想先了解一下具体情况，再回复你。')],'emotion':'neutral','face_sentence':0}
                trace={'method':'信息不足时的保守临时回应'}
            else:
                parsed,trace=reply(case['context'],relationship)
            result=decorate(parsed['sentences'],parsed.get('emotion'),parsed.get('face_sentence'),args.strength,args.variant,relationship)
            result['information']=information
            trace['information_assessment']=information_trace
            if args.all_densities:
                result['variants']={tier:decorate(parsed['sentences'],parsed['emotion'],parsed['face_sentence'],tier,args.variant,relationship) for tier in ['none','light','medium','high']}
            results.append(dict(case=case,**result,trace=trace))
            (args.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
            print(case['name']+'：\n'+result['decorated_reply'],flush=True)
            for suggestion in information['suggestions']:
                print('补充建议：'+suggestion['question']+'（'+suggestion['purpose']+'）',flush=True)
    lines=['# 情景回应实测','','模型生成正文，程序从授权颜文字词库中选择表情；原始响应保存于results.json。','']
    for item in results:
        lines+=['## '+item['case']['name'],'','情景：'+item['case']['context'],'','普通回应：','','```text',item['plain_reply'],'```','',
                '颜文字版本：','','```text',item['decorated_reply'],'```','','情绪类别：'+item['emotion'],'']
        for tier,version in item.get('variants',{}).items():
            lines += ['### '+version['density_label'],'','```text',version['decorated_reply'],'```','',f"新增颜文字：{version['metrics']['added_faces']}；网络替换：{version['metrics']['added_slang']}",'']
        info=item['information']
        lines += ['### 给使用者的补充建议','','信息状态：'+info['status']+'。'+info['reason'],'']
        lines += ['- '+s['question']+' '+s['purpose'] for s in info['suggestions']] or ['信息已足够，无需额外补充。']
        lines += ['']
    (args.output/'结果.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__': main()
