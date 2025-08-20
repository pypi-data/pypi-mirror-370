from brick_tq_shacl import infer, validate
from ontoenv import OntoEnv, Config
from rdflib import Graph
env = OntoEnv(Config(
    offline=False,
    no_search=True,
))
data = Graph()
data.parse("nist-bdg1-1.ttl", format="ttl")

shapes = Graph()
shapes.parse("223p.ttl")
env.import_dependencies(shapes, fetch_missing=True, recursion_depth=2)
shapes.serialize("shapes.ttl")

#data = infer(data, shapes, min_iterations=5, max_iterations=100)
#data.serialize("post-infer.ttl")

valid, rgr, rstr = validate(data, shapes, min_iterations=5, max_iterations=100)
print(f"Result string: {rstr}")
print(f"Valid: {valid}")
#print(f"Result graph: {rgr.serialize(format='turtle')}")
