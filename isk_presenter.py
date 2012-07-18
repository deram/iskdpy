from pprint import pprint
from isk_types import *
import cache

import json

class Presenter():
    current=None
    def __init__(self):
        self.group=0
        self.slide=-1
        json_data=open("cache/main.json").read()
        data = json.loads(json_data, "utf8")
        self.display=Display(data)
        #self.display=cache.fill_cache_and_get_display()

    def get_all_slides(self):
        return self.display.get_all_slides()

    def get_presentation(self):
        return self.display.get_presentation()

    def get_current_group(self):
        return self.get_presentation()[self.group]

    def get_current_slide(self):
        return self.get_presentation()[self.group][self.slide]

    def get_next(self):
        valid_slide=False
        while (not valid_slide):
            n_groups = len(self.get_presentation())
            n_slides = len(self.get_current_group())
            self.slide += 1
            if ( self.slide >= n_slides ):
                self.slide = 0
                self.group += 1
            if ( self.group >= n_groups ):
                self.slide = 0
                self.group = 0
                print "Presentation wrapped"
            valid_slide = self.get_current_slide().valid()

        ret = self.get_current_slide()
        print "Next: %s" % ret
        return ret

def CurrentPresenter():
    if (not Presenter.current):
        Presenter.current = Presenter()
    return Presenter.current

