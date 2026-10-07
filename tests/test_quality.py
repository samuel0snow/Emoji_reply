import unittest
from kaomoji_reply.quality import review


class QualityTests(unittest.TestCase):
    def test_thanks_role(self):
        result,changes=review('同事感谢我帮忙。',{'sentences':['谢谢！'],'emotion':'thanks','face_sentence':0})
        self.assertTrue(result['sentences'][0].startswith('不客气'))
        self.assertTrue(changes)

    def test_role_grounding(self):
        result,changes=review('朋友伤心，不想被劝开心。',{'sentences':['我理解，你愿意独自面对就好。'],'emotion':'comfort','face_sentence':0})
        self.assertNotIn('独自面对',''.join(result['sentences']))
        self.assertEqual(changes[0]['method'],'保守支持性模板')

    def test_preserve_provided_fact(self):
        result,changes=review('朋友说想独自面对，有些伤心。',{'sentences':['理解你想独自面对。'],'emotion':'comfort','face_sentence':0})
        self.assertFalse(changes)

    def test_canned_tail(self):
        result,changes=review('朋友通过面试。',{'sentences':['太好了！','祝你前程似锦！'],'emotion':'happy','face_sentence':1})
        self.assertEqual(result['sentences'],['太好了！'])
        self.assertEqual(result['face_sentence'],0)
