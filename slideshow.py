import json
from pprint import pprint

class Slideshow():
    current=None
    def __init__(self, show=""):
        self.group_number=1
        self.slide_number=0
        if(not show):
            json_data=open("cache/main.json").read()
        else:
            json_data=show
        self.data = json.loads(json_data)
        pprint(self.data)

    def get_all_slides(self):
        ret={}
        for group in self.get_groups().values():
            for slide in group['slides'].values():
                ret[slide['id']] = slide
        return ret



    def get_groups(self):
        return self.data['groups']

    def get_group(self,num):
        return self.get_groups()['group_%d' % num]

    def get_group_slides(self, num):
        return self.get_group(num)['slides']

    def get_slide(self, group, slide):
        return self.get_group_slides(group)['slide_%d' % slide]

    def get_next(self):
        presentationlen=len(self.get_groups())
        grouplen=len(self.get_group(self.group_number))
        self.slide_number += 1
        if ( self.slide_number > grouplen ):
            self.slide_number = 1
            self.group_number += 1
        if ( self.group_number > presentationlen ):
            self.slide_number = 1
            self.group_number = 1
        return "cache/%d.png" % self.get_slide(self.group_number, self.slide_number)['id']

def CurrentSlideshow():
    Slideshow.current
    if (not Slideshow.current):
        Slideshow.current = Slideshow()
    return Slideshow.current

