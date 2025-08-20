from .get import getMethods
from .list import listMethods
from .update import updateMethods

class OrganizationsMethods(
	getMethods,
	listMethods,
	updateMethods
):
	pass
