from cocos.actions import CallFunc, FadeOutTRTiles, FadeOutBLTiles, StopGrid, FadeIn, Reverse
from cocos.director import director
from cocos.scenes import transitions

__all__= [ 'FadeTRTransition', 'FadeBLTransition', 'CrossFadeTransition']

class FadeTRTransition(transitions.TransitionScene):
	'''Fade the tiles of the outgoing scene from the left-bottom corner the to top-right corner.
	'''
	def __init__( self, *args, **kwargs ):
		super(FadeTRTransition, self ).__init__( *args, **kwargs)

		width, height = director.get_window_size()
		aspect = width / float(height)
		x,y = int(9*aspect), 9

		a = self.get_action(x,y)

#		a = Accelerate( a)
		self.out_scene.do( a + \
							CallFunc(self.finish) + \
							StopGrid() )

	def start(self):
		# don't call super. overriding order
		self.add( self.in_scene, z=0 )
		self.add( self.out_scene, z=1 )

	def get_action(self,x,y):
		return FadeOutTRTiles( grid=(x,y), duration=self.duration )

class FadeBLTransition(FadeTRTransition):
	'''Fade the tiles of the outgoing scene from the top-right corner to the bottom-left corner.
	'''
	def get_action(self,x,y):
		return FadeOutBLTiles( grid=(x,y), duration=self.duration )


class CrossFadeTransition(transitions.TransitionScene):
	'''Crossfade scenes
	'''
	def __init__( self, *args, **kwargs ):
		super(CrossFadeTransition, self ).__init__( *args, **kwargs)

		a=FadeIn(self.duration)
		self.in_scene.do(a + CallFunc(self.finish))
	

def getTransition(name):
	if name == 'FadeBLTransition': return FadeBLTransition
	if name == 'FadeTRTransition': return FadeTRTransition
	if name == 'CrossFadeTransition': return CrossFadeTransition
	if name in transitions.__all__:
		return getattr(transitions, name)

