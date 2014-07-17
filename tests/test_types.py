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
		self.slide=Slide(**test_dict)
		self.slide_unicode=u'Slide "Galleria automaatti 5/5" (658) Group "Gallerian automaattikuvat" (102) file: 658.png (12:07:05)'
		self.override=OverrideSlide(**test_dict)
		self.override_unicode=u'OverrideSlide "Galleria automaatti 5/5" file: 658.png'

	def test_slide_datas(self):
		self.assertEqual(str(self.slide), self.slide_unicode)
		self.slide.ready=False
		self.assertFalse(self.slide.ready)
		self.assertEqual(str(self.slide), self.slide_unicode + " NOT READY")
		
		self.assertTrue(self.slide.show_clock)
		
		self.slide.effect_id=9
		self.assertEqual(self.slide.effect, 'unknown')

		self.assertFalse(self.slide.is_override)
		
		self.slide.type='video'
		self.assertEqual(self.slide.filename, '658.mp4')

		self.assertFalse(self.slide.uptodate)
		self.slide.filename='README'
		self.slide.updated_at=10000
		self.assertTrue(self.slide.uptodate)

	def test_override_slide_data(self):
		self.assertTrue(self.slide != self.override)
		self.assertEqual(str(self.override), self.override_unicode)
		self.assertEqual(self.override.id, 658)
		self.assertTrue(self.override.is_override)
		self.assertEqual(self.override.ready, self.override.valid)


class TestDisplay(unittest.TestCase):
	def setUp(self):
		slide=Slide()
		oslide=OverrideSlide()
		presentation=Presentation(slides=[slide])
		self.dpy=Display(presentation=presentation, override_queue=[oslide])
		self.dpy2=Display()

	def test_display_attribs(self):
		self.assertEqual(self.dpy.updated_at, 0)
		self.assertEqual(len(self.dpy.all_slides), 1)
		self.assertEqual(self.dpy.updated_at, 0)
		self.assertEqual(self.dpy.presentation.total_slides, 1)
		self.assertEqual(str(self.dpy), 'Display "unnamed" (0) Updated: 01/01/70-00:00:00\n Overrides: 1\n OverrideSlide "unnamed" file: 0.png\n Presentation "unnamed" (0) Slides: 1\n  Slide "unnamed" (0) Group "unnamed" (0) file: 0.png (00:00:00)')

	def test_empty_display_attribs(self):
		self.assertEqual(self.dpy2.updated_at, 0)
		self.assertEqual(len(self.dpy2.all_slides), 0)
		self.assertEqual(self.dpy2.updated_at, 0)
		self.assertEqual(len(self.dpy2.presentation), 0)
		self.assertEqual(self.dpy2.presentation.total_slides, 0)
		self.assertEqual(str(self.dpy2), 'Display "unnamed" (0) Updated: 01/01/70-00:00:00\n Overrides: 0\n Presentation "unnamed" (0) Slides: 0')

