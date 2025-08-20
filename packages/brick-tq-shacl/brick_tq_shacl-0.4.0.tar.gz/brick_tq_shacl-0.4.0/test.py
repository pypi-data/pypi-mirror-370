from brick_tq_shacl.topquadrant_shacl import infer, validate, infer2, validate2
from rdflib import Graph

data = Graph()
data.parse("air_quality_sensor_example.ttl", format="ttl")

shapes = Graph()
shapes.parse("Brick.ttl")

g = infer2(data, shapes)
print(g.serialize(format='ttl'))

valid, _, report = validate2(data, shapes)
print(report)
print(valid)
