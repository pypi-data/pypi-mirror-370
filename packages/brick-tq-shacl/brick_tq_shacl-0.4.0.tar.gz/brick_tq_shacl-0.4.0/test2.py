from brick_tq_shacl.pyshacl import infer, validate
from rdflib import Graph

data = Graph()
data.parse("air_quality_sensor_example.ttl", format="ttl")

shapes = Graph()
shapes.parse("Brick.ttl")

inferred = infer(data, shapes)
print(inferred.serialize(format="turtle"))
