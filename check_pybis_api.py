from pybis import Openbis

o = Openbis('https://main.datastore.bam.de/')
print("=" * 80)
print("new_sample() signature:")
print("=" * 80)
help(o.new_sample)

print("\n" + "=" * 80)
print("get_samples() signature:")
print("=" * 80)
help(o.get_samples)

print("\n" + "=" * 80)
print("get_sample() signature:")
print("=" * 80)
help(o.get_sample)
