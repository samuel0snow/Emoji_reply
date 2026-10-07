"""Small, auditable guards for observed conversational failures."""
import re

CANNED=re.compile(r'[^。！？]*?(?:前程似锦|幸福永驻|快乐常伴)[^。！？]*[。！？]?')
UNSUPPORTED=('没人理解','独自面对','没人关心','你一定会成功')


def review(context,parsed):
    result=dict(parsed); result['sentences']=list(parsed['sentences']); changes=[]
    if any(w in context for w in ['不想去','婉拒']) and any(w in context for w in ['不编造理由','不解释理由']) and any(w in ''.join(result['sentences']) and w not in context for w in ['其他安排','工作忙','身体不舒服','有事']):
        before=result['sentences']
        result.update(sentences=['谢谢邀请，不过这次我就不去了。'],emotion='neutral',face_sentence=0)
        changes.append({'reason':'拒绝时编造了未提供的理由','before':before,'after':result['sentences'],'method':'无理由婉拒模板'})
    if any(w in context for w in ['看不到','没有给我看','未见']) and '能看见' in ''.join(result['sentences']):
        before=result['sentences']
        result.update(sentences=['看来你真的很喜欢它呀！'],emotion='happy',face_sentence=0)
        changes.append({'reason':'未收到图片却声称看见','before':before,'after':result['sentences'],'method':'回应心情模板'})
    if any(word in context for word in ['感谢我','谢谢我']) and ''.join(result['sentences']).strip('。！! ') in {'谢谢','谢谢你','感谢你'}:
        before=result['sentences']
        result.update(sentences=['不客气，能帮上忙就好！'],emotion='thanks',face_sentence=0)
        changes.append({'reason':'回应别人对我的感谢时角色反转','before':before,'after':result['sentences'],'method':'保守回应感谢模板'})
    for index,line in enumerate(result['sentences']):
        cleaned=CANNED.sub('',line).strip()
        if cleaned!=line:
            result['sentences'][index]=cleaned
            changes.append({'reason':'删除套话','before':line,'after':cleaned})
    result['sentences']=[s for s in result['sentences'] if s]
    negative=any(word in context for word in ['难过','失落','伤心','开心不起来','没考好'])
    unsupported=next((phrase for phrase in UNSUPPORTED if phrase in ''.join(result['sentences']) and phrase not in context),None)
    if negative and unsupported:
        before=result['sentences']
        result.update(sentences=['听起来你现在不好受。','你想说的话，我听着。'],emotion='comfort',face_sentence=1)
        changes.append({'reason':'未提供的情绪或处境判断：'+unsupported,'before':before,'after':result['sentences'],'method':'保守支持性模板'})
    if not result['sentences']:
        # A canned-only response should be regenerated, not silently fabricated.
        raise ValueError('回应只包含套话，请重新生成')
    if negative: result['emotion']='comfort'
    if any(word in context for word in ['确认收到','收到通知']): result['emotion']='neutral'
    result['face_sentence']=min(result.get('face_sentence',0),len(result['sentences'])-1)
    return result,changes
