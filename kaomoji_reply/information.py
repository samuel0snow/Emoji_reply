"""Assess whether the situation supports a useful response, independently of styling."""
import json
import re
from .model import api


def refine(context,result):
    """Correct known false-sufficient cases; retain the original assessment in trace."""
    cleaned=re.sub(r'[，。！？!？\s]','',context)
    known_intent=any(w in context for w in ['婉拒','不想去','不解释理由','暂时待定','待确认','还没确认','不确定是否有空','还没确认有没有空'])
    known_social=any(w in context for w in ['晚安','生日','谢谢','感谢','难过','失落','伤心','开心不起来','很喜欢','特别喜欢'])
    apology_known='道歉' in context and any(w in context for w in ['迟到','忘记','弄坏','说错','打断','失约','没及时','误会'])
    if known_intent or known_social or apology_known:
        return {'status':'sufficient','reason':'已提供足以写出当前回应的场景或态度，不必追问更多细节。','suggestions':[],'assessment_method':'已知信息规则校正'}
    if any(w in context for w in ['联系我了','给我发消息了']) and not any(w in context for w in ['说：','说了','说他','说她','“','「']):
        return {'status':'provisional','reason':'知道对方联系了你，但不知道消息内容和你想如何回应。','suggestions':[
            {'question':'对方具体发了什么消息？','purpose':'回应实际内容。'},
            {'question':'你希望继续聊、保持距离，还是先礼貌回应？','purpose':'确定回应的态度和边界。'}],
            'provisional_reply':'我看到你的消息了。','assessment_method':'规则校正'}
    if '道歉' in context and not apology_known:
        return {'status':'provisional','reason':'可以先表达歉意，但不知道需要为什么事情道歉。','suggestions':[
            {'question':'发生了什么，你想为什么事情道歉？','purpose':'明确承担的责任，避免编造过错。'}],
            'provisional_reply':'对不起。','assessment_method':'规则校正'}
    if '报价' in context and not re.search(r'\d+\s*(?:元|块|人民币)',context):
        return {'status':'provisional','reason':'可以先确认报价需求，但没有具体价格或项目范围。','suggestions':[
            {'question':'客户问的是哪种产品或服务，具体规格是什么？','purpose':'明确报价范围。'},
            {'question':'有哪些已确定的价格和报价条件？','purpose':'避免编造金额或交易条件。'}],
            'provisional_reply':'我先确认一下具体报价，再回复你。','assessment_method':'规则校正'}
    if re.fullmatch(r'(?:请|帮我|帮忙|替我|麻烦你)*(?:回|回复|回应)(?:一下|对方|他|她|吧)*',cleaned):
        return {'status':'insufficient','reason':'没有提供对方的话或具体场景。','suggestions':[
            {'question':'对方说了什么，或者发生了什么？','purpose':'确定需要回应的内容。'}],
            'provisional_reply':'我想先了解一下具体情况，再回复你。','assessment_method':'规则校正'}
    invited=any(w in context for w in ['约我','约出去','邀请我','约我出去'])
    attitude=any(w in context for w in ['不想去','想去','答应','拒绝','婉拒','接受','没空','有空','待定','确认','不知道','不确定'])
    if invited and not attitude:
        return {'status':'provisional','reason':'知道有邀请，但不知道你想接受、拒绝还是暂时待定。','suggestions':[
            {'question':'你想接受、婉拒，还是暂时待定？','purpose':'确定回应的核心态度。'}],
            'provisional_reply':'谢谢邀请，我考虑一下再回复你。','assessment_method':'规则校正'}
    if '投诉' in context and len(cleaned)<25 and not any(w in context for w in ['因为','说','关于','质量','退款','物流','破损','延迟']):
        return {'status':'provisional','reason':'可以先确认收到反馈，但不知道投诉内容和希望的处理方式。','suggestions':[
            {'question':'客户具体投诉什么问题？','purpose':'回应实际问题，避免泛泛承诺。'},
            {'question':'你目前能提供哪些处理方式？','purpose':'避免承诺无法执行的补偿或结果。'}],
            'provisional_reply':'收到你的反馈，方便具体说说遇到了什么问题吗？','assessment_method':'规则校正'}
    return result


def assess(context,relationship='friend'):
    schema={'type':'object','properties':{
        'status':{'type':'string','enum':['sufficient','provisional','insufficient']},
        'reason':{'type':'string'},
        'suggestions':{'type':'array','maxItems':3,'items':{'type':'object','properties':{
            'question':{'type':'string'},'purpose':{'type':'string'}},'required':['question','purpose'],'additionalProperties':False}}
    },'required':['status','reason','suggestions'],'additionalProperties':False}
    system=('检查用户提供的待回应场景是否足以写出回应。只检查实际影响回复的信息，不追求所有细节。'
        'sufficient表示已足够回应，suggestions必须为空；provisional表示可先给保守回应，补充信息能改善；'
        'insufficient表示连对方说了什么或用户想表达什么都无法确定。建议是给使用工具的用户看的，不是写给聊天对方的内容。'
        '只提最多3个具体问题，并说明回答能改善什么。不能重复追问已经提供的信息。'
        '用户明确说尚未确认是否有空，回应可以表达待确认，不必追问具体时间或逼用户马上决定。'
        '简单感谢、生日祝福、晚安、倾听安慰通常信息足够。看不到图片仍可回应对方的心情，不必索要图片。'
        '不要要求姓名、身份证等无关隐私。仅输出要求的JSON。')
    request={'messages':[{'role':'system','content':system},
        {'role':'user','content':'朋友说谢谢你帮忙，请回复。'},
        {'role':'assistant','content':'{"status":"sufficient","reason":"可以回应感谢，不需要更多细节。","suggestions":[]}'},
        {'role':'user','content':'有人约我出去，帮我回。'},
        {'role':'assistant','content':'{"status":"provisional","reason":"可以先回应邀请，但不知道你是否想接受。","suggestions":[{"question":"你想接受、婉拒，还是暂时待定？","purpose":"确定回应的核心态度。"}]}'},
        {'role':'user','content':'帮我回复一下。'},
        {'role':'assistant','content':'{"status":"insufficient","reason":"没有提供对方的话或具体场景。","suggestions":[{"question":"对方说了什么，或者发生了什么？","purpose":"确定要回应的内容。"}]}'},
        {'role':'user','content':context}],
        'temperature':0,'max_tokens':384,'response_format':{'type':'json_schema','json_schema':{'name':'information','schema':schema}},
        'chat_template_kwargs':{'enable_thinking':False}}
    raw=api('/v1/chat/completions',request)
    if raw['choices'][0]['finish_reason']=='length': raise ValueError('信息评估被截断')
    result=json.loads(raw['choices'][0]['message']['content'])
    if result['status']=='sufficient': result['suggestions']=[]
    return refine(context,result),{'request':request,'response':raw}
