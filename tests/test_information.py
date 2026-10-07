import unittest
from kaomoji_reply.information import refine


class InformationTests(unittest.TestCase):
    def setUp(self):
        self.enough={'status':'sufficient','reason':'可以回应','suggestions':[]}

    def test_missing_scene(self):
        result=refine('帮我回复一下。',self.enough)
        self.assertEqual(result['status'],'insufficient')
        self.assertTrue(result['suggestions'])

    def test_invitation_missing_intent(self):
        result=refine('有人约我出去，帮我回。',self.enough)
        self.assertEqual(result['status'],'provisional')
        self.assertNotIn('过去',result['provisional_reply'])

    def test_pending_is_known(self):
        self.assertEqual(refine('朋友约我明天见，我不确定有没有空，先待确认。',self.enough)['suggestions'],[])

    def test_known_rejection(self):
        self.assertEqual(refine('朋友约我吃饭，我不想去。',self.enough)['suggestions'],[])

    def test_complaint_missing_details(self):
        self.assertEqual(len(refine('客户投诉了，帮我回复。',self.enough)['suggestions']),2)

    def test_photo_not_required(self):
        self.assertEqual(refine('朋友发了看不到的照片，说很喜欢挂件。',self.enough)['suggestions'],[])

    def test_known_apology_not_reasked(self):
        result=refine('迟到十分钟，想诚恳道歉。',{'status':'insufficient','reason':'缺少信息','suggestions':[{'question':'为什么道歉？','purpose':'原因'}]})
        self.assertEqual(result['status'],'sufficient')

    def test_unknown_apology(self):
        self.assertEqual(refine('想向同学道歉。',self.enough)['status'],'provisional')

    def test_price_never_invented(self):
        result=refine('客户问报价。',self.enough)
        self.assertNotRegex(result['provisional_reply'],r'\d')
        self.assertEqual(len(result['suggestions']),2)

    def test_unknown_contact(self):
        self.assertEqual(refine('前任联系我了。',self.enough)['status'],'provisional')
