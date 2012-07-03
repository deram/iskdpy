

class Slideshow():
    current=None
    def __init__(self, show=""):
        self.slides = ['slide_23_full.jpg', 'slide_28_full.jpg', 'slide_30_full.png']
        self.slide_number=-1

    def get_next(self):
        self.slide_number=(self.slide_number + 1) % len(self.slides)
	return self.slides[self.slide_number]

def CurrentSlideshow():
    Slideshow.current
    if (not Slideshow.current):
        Slideshow.current = Slideshow()
    return Slideshow.current

