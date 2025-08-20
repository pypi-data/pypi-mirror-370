from brick_tq_shacl.topquadrant_shacl import infer, validate
import ontoenv
import rdflib

cfg = ontoenv.Config(temporary=True, offline=False)
env = ontoenv.OntoEnv(cfg)

g = rdflib.Graph()
g.parse("hvac223p.ttl")

o = rdflib.Graph()
o.parse("223p.ttl")
env.import_dependencies(o)
o.serialize("ontology.ttl", format="ttl")

ig = infer(g, o)
ig.serialize("hvac223p-inferred.ttl", format="ttl")

valid, _, report_str = validate(ig, o)
print(valid)
print(report_str)
