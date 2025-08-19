import cfdm

from pprint import pprint


g = cfdm.read("test_file_badnaming.nc")
for f in g:
    out = f.dataset_compliance()
    print(out)
    pprint(out)

g = cfdm.read("geometry_1.nc")[0]
out = g[0].dataset_compliance()
print(out)
pprint(out)

g = cfdm.read("ugrid_1.nc")[0]
out = g[0].dataset_compliance()
print(out)
pprint(out)

g = cfdm.read("ugrid_2.nc")[0]
out = g[0].dataset_compliance()
print(out)
pprint(out)

g = cfdm.read("DSG_timeSeries_indexed.nc")[0]
out = g[0].dataset_compliance()
print(out)
pprint(out)
