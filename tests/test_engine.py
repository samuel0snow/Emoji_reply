import unittest
from kaomoji_reply.engine import decorate, existing_faces


class EngineTests(unittest.TestCase):
    def test_thanks(self):
        result=decorate(['不用客气，你们喜欢就好！'],'thanks')
        self.assertIsNotNone(result['face'])
        self.assertIn('不用客气',result['decorated_reply'])

    def test_serious_override(self):
        result=decorate(['金属杯不能放进微波炉。'],'happy',strength='medium')
        self.assertEqual(result['face'],'(・_・)')
        self.assertTrue(result['decorated_reply'].startswith(result['plain_reply']))

    def test_comfort(self):
        result=decorate(['你愿意的话，可以和我说说。'],'comfort',strength='medium')
        self.assertEqual(result['face'],'(｡´･ω･)ﾉﾞ')
        self.assertEqual(decorate(['你愿意的话，可以和我说说。'],'comfort')['face'],'(｡´･ω･)ﾉﾞ')

    def test_none_preserves_text(self):
        lines=['谢谢！这个朋友好可爱。']
        result=decorate(lines,'thanks',strength='none')
        self.assertTrue(result['decorated_reply'].startswith(lines[0]))
        self.assertEqual(result['metrics']['added_faces'],1)
        self.assertEqual(result['metrics']['added_slang'],0)

    def test_negation(self):
        self.assertEqual(decorate(['我不开心，也不喜欢这个礼物。'],'happy')['face'],'(｡´･ω･)ﾉﾞ')

    def test_mixed_fact_placement(self):
        result=decorate(['生日快乐！明天下午3点见。'],'happy',strength='high')
        self.assertEqual(result['faces'][0]['sentence'],0)
        self.assertEqual(result['decorated_reply'].splitlines()[-1],'明天下午3点见。')

    def test_colleague_no_slang(self):
        result=decorate(['这个朋友很可爱，谢谢！'],'thanks',strength='high',relationship='colleague')
        self.assertEqual(result['metrics']['added_slang'],0)

    def test_density_budgets(self):
        lines=['谢谢你一直认真帮我准备这个小礼物，大家都很喜欢！','这个礼物我会好好收着，也想给你看看。','太好了，这次终于顺利做完了，真的好开心！','朋友说大家已经准备好了，等有机会再一起聊聊。','回头见，期待下次继续一起做这些可爱的小东西！']
        counts=[decorate(lines,'happy',strength=t)['metrics']['added_faces'] for t in ['none','light','medium','high']]
        self.assertEqual(counts,[1,1,2,3])

    def test_existing_face(self):
        result=decorate(['谢谢你；)'],'thanks')
        self.assertEqual(result['decorated_reply'].count('；)'),1)
        self.assertIsNone(result['face'])

    def test_numbers_and_quotes(self):
        result=decorate(['标签写着“这个朋友很可爱”，明天下午3点见。'],'greeting',strength='medium')
        self.assertIn('这个朋友很可爱',result['decorated_reply'])
        self.assertIn('明天下午3点',result['decorated_reply'])

    def test_invalid_index(self):
        with self.assertRaises(ValueError): decorate(['你好。'],'greeting',8)

    def test_neutral_no_decoration(self):
        result=decorate(['收到，谢谢告知。'],'neutral',strength='high')
        self.assertEqual(result['metrics']['added_faces'],1)
        self.assertEqual(result['metrics']['added_slang'],0)

    def test_paragraph_minimum_all_tiers_and_emotions(self):
        for tier in ['none','light','medium','high']:
            for emotion in ['happy','thanks','greeting','comfort','neutral','serious']:
                with self.subTest(tier=tier,emotion=emotion):
                    result=decorate(['明天下午3点见。'],emotion,strength=tier)
                    self.assertTrue(existing_faces(result['decorated_reply']))
                    self.assertEqual(result['metrics']['added_faces'],1)

    def test_provisional_invitation_smiles(self):
        result=decorate(['谢谢邀请，我考虑一下再回复你。'],'neutral')
        self.assertIn(result['face'],['(*´ `)','(´◡͐`)','(*´꒳`*)','(*´∇`*)'])

    def test_existing_neutral_face_no_duplicate(self):
        result=decorate(['收到。(・_・)'],'neutral',strength='none')
        self.assertEqual(result['decorated_reply'],'收到。(・_・)')
        self.assertEqual(result['metrics']['added_faces'],0)

    def test_quotes_and_links_are_not_replaced(self):
        result=decorate(['谢谢，标签是“这个朋友可爱”，链接 https://example.com/这个。'],'thanks',strength='high')
        self.assertIn('“这个朋友可爱”',result['decorated_reply'])
        self.assertIn('https://example.com/这个',result['decorated_reply'])

    def test_comfort_face_is_on_support(self):
        result=decorate(['没考好确实会难过。','你想说的话，我听着。'],'comfort',strength='high')
        self.assertEqual(result['faces'][0]['sentence'],1)
        self.assertEqual(result['metrics']['added_slang'],0)


if __name__=='__main__': unittest.main()
