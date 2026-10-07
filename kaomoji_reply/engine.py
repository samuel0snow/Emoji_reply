"""Density budgets, sentence-aware placement, and conservative lexical styling."""
import json
import math
import re
from pathlib import Path

BANK=json.loads((Path(__file__).parent/'data/style_bank.json').read_text(encoding='utf-8'))
EMOTIONS={'happy','thanks','greeting','comfort','neutral','serious'}
PROFILES={
    'none':{'label':'最少点缀','faces':0,'slang':0,'chars_per_face':0},
    'light':{'label':'轻点缀','faces':1,'slang':1,'chars_per_face':100},
    'medium':{'label':'适中','faces':2,'slang':2,'chars_per_face':45},
    'high':{'label':'活泼','faces':3,'slang':3,'chars_per_face':28},
}
PROTECTED=re.compile(r'“[^”]*”|「[^」]*」|"[^"\n]*"|https?://[^\s，。！？]+|`[^`]*`')
WARNING=re.compile(r'请勿|切勿|禁止|烫伤|危险|密码|转账|过敏|剂量|不能.{0,8}(?:放|用|吃|喝|碰)|不要.{0,8}(?:放|用|吃|喝|碰)')
NEGATIVE=re.compile(r'不(?:太|怎么|是|能|会)?(?:开心|高兴|快乐|喜欢)|开心不起来|难过|失落|伤心|没考好|失败|分手|去世')
FACT=re.compile(r'\d|明天|下午|上午|今晚|尺寸|材质|颜色|截止|确认时间|确认后|确认了再|几点')
SIGNALS=[
    ('comfort',re.compile(r'愿意.{0,8}(?:说|聊)|慢慢来|不用急|陪你聊|抱抱|先休息|可以和.{0,5}说说|我听着|听你说')),
    ('thanks',re.compile(r'谢谢|感谢|不用谢|不用客气|不客气|喜欢就好')),
    ('happy',re.compile(r'生日快乐|恭喜|太好了|太棒了|开心呀|开心哦|过得开心|玩得开心|好开心|真开心')),
    ('greeting',re.compile(r'你好|早上好|晚上好|晚安|再见|回头见|到时见|见面')),
    ('soft',re.compile(r'可爱|好喜欢|很喜欢|喜欢这|喜欢它|小礼物')),
]


def existing_faces(text):
    found=[f['text'] for f in BANK['faces'] if f['text'] in text]
    found+=re.findall(r'[；;]\)|\([^\n()]{0,25}[ωᵕ꒳≧^・∀∇╥][^\n()]{0,25}\)',text)
    return list(dict.fromkeys(found))


def units_for(sentences):
    units=[]
    for parent,text in enumerate(sentences):
        protected=[(m.start(),m.end()) for m in PROTECTED.finditer(text)]
        for face in existing_faces(text):
            protected.extend((m.start(),m.end()) for m in re.finditer(re.escape(face),text))
        start=0
        for pos,char in enumerate(text):
            if char in '。！？!?\n' and not any(a<=pos<b for a,b in protected):
                chunk=text[start:pos+1].strip()
                if chunk: units.append({'parent':parent,'text':chunk})
                start=pos+1
        if text[start:].strip(): units.append({'parent':parent,'text':text[start:].strip()})
    return units


def suitability(text,emotion):
    """Return category, priority, reason. Facts and warnings never get a face."""
    if WARNING.search(text): return None,0,'警告句'
    if FACT.search(text): return None,0,'数字、时间或事实说明'
    bare=PROTECTED.sub('',text)
    if not bare.strip('，。！？!? '): return None,0,'引用或链接'
    for kind,pattern in SIGNALS:
        if pattern.search(bare):
            if NEGATIVE.search(bare) and kind!='comfort': return None,0,'负面或否定语境'
            if emotion=='comfort' and kind not in {'comfort','thanks'}: return None,0,'安慰语境不庆祝'
            return kind,5 if kind in {'happy','thanks','comfort'} else 4,'明确表达信号'
    if NEGATIVE.search(bare): return None,0,'负面事实陈述'
    return None,0,'缺少合适表达信号'


def _tokenizer():
    try:
        import jieba
    except ImportError:
        return None
    return jieba


def decorate(sentences,emotion='neutral',face_sentence=0,strength='light',variant=0,relationship='friend'):
    if not isinstance(sentences,list) or not sentences or not all(isinstance(s,str) and s.strip() for s in sentences):
        raise ValueError('回应必须是非空句子列表')
    if emotion not in EMOTIONS: raise ValueError('未知情绪类别')
    if type(face_sentence)!=int or not 0<=face_sentence<len(sentences): raise ValueError('表情位置越界')
    if strength not in PROFILES: raise ValueError('未知密度档位')
    if relationship not in {'friend','colleague','neutral'}: raise ValueError('未知关系类型')
    if type(variant)!=int or variant<0: raise ValueError('备选序号不能为负数')
    plain='\n'.join(s.strip() for s in sentences)
    profile=PROFILES[strength]
    units=units_for(sentences)
    global_serious=emotion=='serious'
    found=existing_faces(plain)
    # Short text stays at one face even at high density. Higher tiers allow
    # more expressions only when length and safe placement opportunities grow.
    face_budget=0 if not profile['faces'] else min(profile['faces'],max(1,math.ceil(len(plain)/profile['chars_per_face'])))
    if relationship!='friend': face_budget=min(face_budget,1)
    if emotion=='neutral': face_budget=0
    if emotion=='comfort': face_budget=min(face_budget,1) if strength in {'medium','high'} and relationship=='friend' else 0
    if global_serious or found: face_budget=0
    placements=[]; decisions=[]
    for index,unit in enumerate(units):
        kind,score,reason=suitability(unit['text'],emotion)
        decisions.append({'unit':index,'text':unit['text'],'category':kind,'reason':reason})
        if kind and (kind!='comfort' or emotion=='comfort'):
            placements.append((score+(0.25 if unit['parent']==face_sentence else 0),index,kind))
    chosen=[]
    for score,index,kind in sorted(placements,reverse=True):
        if len(chosen)>=face_budget: break
        if any(abs(index-other[0])<=1 for other in chosen): continue
        chosen.append((index,kind))
    chosen.sort()
    output=[u['text'] for u in units]; changes=[]; used=set(); slang_count=0
    token=_tokenizer() if profile['slang'] and relationship=='friend' and emotion not in {'comfort','neutral'} and not global_serious else None
    priority={'可爱':0,'看看':1,'朋友':2,'这个':3,'我':4,'的':5}  # avoid gratuitous 是→似
    for index,line in enumerate(output):
        if token is None or slang_count>=profile['slang'] or WARNING.search(line) or FACT.search(line) or existing_faces(line): continue
        protected=[(m.start(),m.end()) for m in PROTECTED.finditer(line)]
        candidates=[]
        for word,start,end in token.tokenize(line):
            item=next((x for x in BANK['replacements'] if x['from']==word and word in priority),None)
            if item and word not in used and not any(start<b and end>a for a,b in protected):
                candidates.append((priority[word],start,end,item))
        if candidates:
            _,start,end,item=min(candidates,key=lambda x:(x[0],x[1]))
            output[index]=line[:start]+item['to']+line[end:]
            slang_count+=1; used.add(item['from'])
            changes.append({'sentence':index,'from':item['from'],'to':item['to'],'source':BANK['sources'][item['origin']]})
    faces=[]
    category_map={'happy':'happy','thanks':'smile','soft':'smile','greeting':'aisatsu','comfort':'support'}
    used_faces=set()
    for index,kind in chosen:
        pool=[f for f in BANK['faces'] if f.get('category')==category_map[kind] and f['origin']=='kaomoji_collection']
        if not pool: continue
        face=next((pool[(variant+offset)%len(pool)] for offset in range(len(pool)) if pool[(variant+offset)%len(pool)]['text'] not in used_faces),None)
        if not face: continue
        used_faces.add(face['text'])
        output[index]=output[index].rstrip('。')+' '+face['text']
        entry={'sentence':index,'face':face['text'],'category':kind,'source':BANK['sources'][face['origin']]}
        changes.append(entry); faces.append(entry)
    decorated=plain if strength=='none' else '\n'.join(output)
    minimum_added=False
    if not found and not faces:
        # The paragraph-wide minimum overrides zero-face density and placement
        # suppression. Append outside the body so facts/quotes stay untouched.
        negative=emotion=='comfort' or bool(NEGATIVE.search(plain))
        serious=global_serious or bool(WARNING.search(plain))
        if serious:
            face={'text':'(・_・)','origin':'builtin'}
            kind='serious'; source='kaomoji_reply/engine.py'
        else:
            category='support' if negative else 'smile'
            pool=[f for f in BANK['faces'] if f.get('category')==category and f['origin']=='kaomoji_collection']
            face=pool[variant%len(pool)]
            kind='comfort' if negative else 'neutral'
            source=BANK['sources'][face['origin']]
        decorated=decorated+' '+face['text']
        entry={'sentence':len(units)-1,'face':face['text'],'category':kind,'source':source,'reason':'整段至少一个颜文字'}
        faces.append(entry); changes.append(entry)
        minimum_added=True
    return {'plain_reply':plain,'decorated_reply':decorated,'emotion':emotion,'density':strength,'density_label':profile['label'],
            'face':faces[0]['face'] if faces else None,'face_sentence':faces[0]['sentence'] if faces else None,
            'faces':faces,'changes':changes,'suppressed':bool(found),'normal_placement_suppressed':global_serious or bool(found),
            'metrics':{'face_budget':max(face_budget,1) if not found else 0,'added_faces':len(faces),'added_slang':slang_count,'existing_faces':len(found),'units':len(units),'minimum_face_added':minimum_added},
            'placement_decisions':decisions,'note':'整段至少一个颜文字；已有则不追加。密度控制额外点缀，缺少合适位置时按语气在整段末尾补一个。'}
