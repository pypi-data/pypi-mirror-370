from .delete import deleteMethods
from .get import getMethods
from .list import listMethods
from .update import updateMethods

class UsersMethods(
	deleteMethods,
	getMethods,
	listMethods,
	updateMethods
):
	pass
