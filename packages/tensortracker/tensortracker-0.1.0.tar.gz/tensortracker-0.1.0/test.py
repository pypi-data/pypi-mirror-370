import tensortracker as tt
import pprint

diff = tt.resolve_diff(path, path2)

print(diff.dest_hash)
print(diff.origin_hash)

for tensor in diff.changes:
    print(diff.changes[tensor].data)
    
