from .get import getMethods
from .list import listMethods
from .update import updateMethods

class UserApiKeysMethods(
	getMethods,
	listMethods,
	updateMethods
):
	pass
