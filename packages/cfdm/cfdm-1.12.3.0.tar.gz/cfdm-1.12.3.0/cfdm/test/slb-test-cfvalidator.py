import cfdm

from pprint import pprint

f = cfdm.read("external_missing.nc")[0]
pprint(f.dataset_compliance())
