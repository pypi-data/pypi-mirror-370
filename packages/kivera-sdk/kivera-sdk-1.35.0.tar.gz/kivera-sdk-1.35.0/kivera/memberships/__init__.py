from .create import createMethods
from .delete import deleteMethods
from .get import getMethods
from .list import listMethods
from .update import updateMethods

class MembershipsMethods(
	createMethods,
	deleteMethods,
	getMethods,
	listMethods,
	updateMethods
):
	pass
