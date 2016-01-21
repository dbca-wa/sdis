import os, json
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sdis.settings")
from pythia.models import (User, Program, District, Region, Division, Area)
from pythia.projects.models import (Project, 
    ScienceProject, CoreFunctionProject, CollaborationProject, 
    StudentProject, ProjectMembership)
# map project.regions pk to Areas
with open("production/regions.json", "rb") as regions:
    print("mapping regions...")
    rd = {}
    #for new_region in Area.objects.filter(area_type=Area.AREA_TYPE_DPAW_REGION):
    #    print("Found Area (Region): {0} - {1}".format(new_region, new_region.name))
    #    area_reg_dict[new_region.name] = new_region.pk
    for r in json.load(regions):
        print("Legacy region {0} - {1}".format(r["fields"]["name"], r["fields"]["slug"]))
        try:
            a = Area.objects.filter(area_type=Area.AREA_TYPE_DPAW_REGION).get(name=r["fields"]["name"])
            print("...matches new Area of type Region: {0}".format(a))
            rd[r["pk"]] = a.pk
        except:
            print("...does not match any Area")
    print(repr(rd))

