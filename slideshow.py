import json
from pprint import pprint
from cache import slideid_to_file


class Slideshow():
    current=None
    def __init__(self, show=""):
        self.group_number=0
        self.slide_number=-1
        if(not show):
            json_data=open("cache/main.json").read()
        else:
            json_data=show
        self.data = json.loads(json_data)
        pprint(self.data)

    def get_all_slides(self):
        ret={}
        for group in self.get_groups():
            for slide in group['slides']:
                ret[slide['id']] = slide
        return ret

    def get_presentation_len(self):
        return self.data['total_groups']

    def get_group_len(self, groupid):
        return self.get_group(groupid)['total_slide']

    def get_groups(self):
        return self.data['groups']

    def get_group(self,num):
        return self.get_groups()[num]

    def get_group_slides(self, num):
        return self.get_group(num)['slides']

    def get_slide(self, group, slide):
        return self.get_group_slides(group)[slide]

    def get_next(self):
        presentationlen = self.get_presentation_len()
        grouplen = self.get_group_len(self.group_number)
        self.slide_number += 1
        if ( self.slide_number == grouplen ):
            self.slide_number = 0
            self.group_number += 1
        if ( self.group_number == presentationlen ):
            self.slide_number = 0
            self.group_number = 0
            print "Presentation wrapped"

        ret = slideid_to_file(self.get_slide(self.group_number, self.slide_number)['id'])
        print 'Group %d "%s": Slide %d "%s" - %s' % (self.group_number, self.get_group(self.group_number)['name'], self.slide_number, self.get_slide(self.group_number, self.slide_number)['name'], ret)
        return ret

def CurrentSlideshow():
    Slideshow.current
    if (not Slideshow.current):
        Slideshow.current = Slideshow()
    return Slideshow.current

