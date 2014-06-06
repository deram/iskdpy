import unittest
import json
from iskdpy.types import *

class TestSlide(unittest.TestCase):
	def setUp(self):
		test_json='''{
        "id": 658,
        "name": "Galleria automaatti 5/5",
        "master_group": 61,
        "group": 102,
        "group_name": "Gallerian automaattikuvat",
        "position": 7,
        "ready": true,
        "deleted": false,
        "created_at": 1391104407,
        "updated_at": 1391342825,
        "duration": 20,
        "effect_id": 1,
        "images_updated_at": 1391342825,
        "show_clock": true,
        "type": "image"
			}'''
		test_dict=json.loads(test_json, 'utf8')
		self.slide=Slide(test_dict)
		self.slide_unicode=u'Slide "Galleria automaatti 5/5" (658) Group "Gallerian automaattikuvat" (102) Position 7 file: 658.png (12:07:05) '
		self.override=OverrideSlide(test_dict)
		self.override_unicode=u'OverrideSlide "Galleria automaatti 5/5" Position 7 file: 658.png'

	def test_slide_datas(self):
		self.assertEqual(str(self.slide), self.slide_unicode)
		self.slide.set_attribs(dict(ready=False))
		self.assertFalse(self.slide.is_ready())
		self.assertEqual(str(self.slide), self.slide_unicode + "NOT READY")
		
		self.assertTrue(self.slide.get_clock())
		
		self.slide.set_attribs(dict(effect_id=9))
		self.assertEqual(self.slide.get_effect(), 'unknown')

		self.assertFalse(self.slide.is_override())
		
		self.slide.set_attribs(dict(type='video'))
		self.assertEqual(self.slide.get_filename(), '658.mp4')

		self.assertFalse(self.slide.is_uptodate())
		self.slide.set_attribs(dict(filename='README', updated_at=10000))
		self.assertTrue(self.slide.is_uptodate())

	def test_override_slide_data(self):
		self.assertTrue(self.slide != self.override)
		self.assertEqual(str(self.override), self.override_unicode)
		self.assertEqual(self.override.get_override_id(), 0)
		self.assertTrue(self.override.is_override())
		self.assertEqual(self.override.is_ready(), self.override.is_valid())


class TestDisplay(unittest.TestCase):
	def setUp(self):
		slide=Slide({})
		oslide=OverrideSlide({})
		presentation=Presentation([slide])
		self.dpy=Display(presentation, [oslide])
		self.dpy2=Display()

	def test_display_attribs(self):
		self.assertEqual(self.dpy.get_updated_at(), 0)
		self.assertEqual(len(self.dpy.get_all_slides()), 1)
		self.assertEqual(self.dpy.get_updated_at(), 0)
		self.assertEqual(self.dpy.get_presentation().get_total_slides(), 1)
		self.assertEqual(str(self.dpy), 'Display "unnamed" (0) Updated: 01/01/70-00:00:00\n Overrides: 1\n OverrideSlide "unnamed" Position 0 file: 0.png\n Presentation "unnamed" (0) Slides: 1\n  Slide "unnamed" (0) Group "" (0) Position 0 file: 0.png (00:00:00) ')

	def test_empty_display_attribs(self):
		self.assertEqual(self.dpy2.get_updated_at(), 0)
		self.assertEqual(len(self.dpy2.get_all_slides()), 0)
		self.assertEqual(self.dpy2.get_updated_at(), 0)
		self.assertEqual(len(self.dpy2.get_presentation()), 0)
		self.assertEqual(self.dpy2.get_presentation().get_total_slides(), 0)
		self.assertEqual(str(self.dpy2), 'Display "unnamed" (0) Updated: 01/01/70-00:00:00\n Overrides: 0\n Presentation "unnamed" (0) Slides: 0')

