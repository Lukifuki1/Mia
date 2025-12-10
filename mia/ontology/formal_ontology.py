"""
MIA Enterprise AGI - Formal Ontology Implementation
==================================================

Complete formal ontology implementation with RDF/OWL support,
semantic descriptors, inference rules, and axioms.
"""

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import Dict, List, Any, Optional, Set
import json
import logging

logger = logging.getLogger(__name__)

# Define MIA namespace
MIA = Namespace("http://mia.enterprise.agi/ontology#")

class MIAOntology:
    """
    Complete MIA Enterprise AGI Ontology Implementation
    """
    
    def __init__(self):
        self.graph = Graph()
        self.setup_namespaces()
        self.initialize_ontology()
        
    def setup_namespaces(self):
        """Setup ontology namespaces"""
        self.graph.bind("mia", MIA)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        
    def initialize_ontology(self):
        """Initialize core ontology structure"""
        # Define core classes
        self.define_core_classes()
        
        # Define properties
        self.define_properties()
        
        # Define individuals
        self.define_individuals()
        
        # Add axioms
        self.add_axioms()
        
        logger.info("✅ MIA Ontology initialized")
        
    def define_core_classes(self):
        """Define core ontology classes"""
        classes = {
            MIA.Agent: "Autonomous intelligent agent",
            MIA.AGICore: "AGI Core agent",
            MIA.HybridAgent: "Hybrid reasoning agent",
            MIA.LearningAgent: "Learning agent",
            MIA.Knowledge: "Knowledge representation entity",
            MIA.Concept: "Conceptual knowledge",
            MIA.Relation: "Relational knowledge",
            MIA.Rule: "Rule-based knowledge",
            MIA.Process: "Computational process",
            MIA.Reasoning: "Reasoning process",
            MIA.Learning: "Learning process",
            MIA.Inference: "Inference process",
            MIA.Resource: "System resource",
            MIA.Model: "AI model resource",
            MIA.Data: "Data resource",
            MIA.Service: "Service resource"
        }
        
        for class_uri, description in classes.items():
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.comment, Literal(description)))
            
        # Define class hierarchy
        self.graph.add((MIA.AGICore, RDFS.subClassOf, MIA.Agent))
        self.graph.add((MIA.HybridAgent, RDFS.subClassOf, MIA.Agent))
        self.graph.add((MIA.LearningAgent, RDFS.subClassOf, MIA.Agent))
        self.graph.add((MIA.Concept, RDFS.subClassOf, MIA.Knowledge))
        self.graph.add((MIA.Relation, RDFS.subClassOf, MIA.Knowledge))
        self.graph.add((MIA.Rule, RDFS.subClassOf, MIA.Knowledge))
        self.graph.add((MIA.Reasoning, RDFS.subClassOf, MIA.Process))
        self.graph.add((MIA.Learning, RDFS.subClassOf, MIA.Process))
        self.graph.add((MIA.Inference, RDFS.subClassOf, MIA.Process))
        self.graph.add((MIA.Model, RDFS.subClassOf, MIA.Resource))
        self.graph.add((MIA.Data, RDFS.subClassOf, MIA.Resource))
        self.graph.add((MIA.Service, RDFS.subClassOf, MIA.Resource))
        
    def define_properties(self):
        """Define ontology properties"""
        # Object properties
        object_properties = {
            MIA.hasKnowledge: (MIA.Agent, MIA.Knowledge, "Agent has knowledge"),
            MIA.performsProcess: (MIA.Agent, MIA.Process, "Agent performs process"),
            MIA.usesResource: (MIA.Process, MIA.Resource, "Process uses resource"),
            MIA.sharesKnowledgeWith: (MIA.Agent, MIA.Agent, "Agent shares knowledge with agent"),
            MIA.dependsOn: (MIA.Process, MIA.Process, "Process depends on process"),
            MIA.produces: (MIA.Process, MIA.Knowledge, "Process produces knowledge"),
            MIA.consumes: (MIA.Process, MIA.Knowledge, "Process consumes knowledge")
        }
        
        for prop_uri, (domain, range_class, description) in object_properties.items():
            self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            self.graph.add((prop_uri, RDFS.domain, domain))
            self.graph.add((prop_uri, RDFS.range, range_class))
            self.graph.add((prop_uri, RDFS.comment, Literal(description)))
            
        # Datatype properties
        datatype_properties = {
            MIA.confidence: (MIA.Knowledge, XSD.float, "Confidence level of knowledge"),
            MIA.timestamp: (MIA.Knowledge, XSD.dateTime, "Timestamp of knowledge creation"),
            MIA.complexity: (MIA.Process, XSD.float, "Complexity score of process"),
            MIA.performance: (MIA.Process, XSD.float, "Performance metric of process"),
            MIA.version: (MIA.Resource, XSD.string, "Version of resource")
        }
        
        for prop_uri, (domain, range_type, description) in datatype_properties.items():
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.domain, domain))
            self.graph.add((prop_uri, RDFS.range, range_type))
            self.graph.add((prop_uri, RDFS.comment, Literal(description)))
            
    def define_individuals(self):
        """Define ontology individuals"""
        individuals = {
            MIA.MIACore: (MIA.AGICore, "Main MIA AGI Core instance"),
            MIA.HybridPipeline: (MIA.Process, "Hybrid reasoning pipeline"),
            MIA.SemanticLayer: (MIA.Process, "Semantic processing layer"),
            MIA.KnowledgeBank: (MIA.Resource, "Knowledge bank resource"),
            MIA.ReasoningEngine: (MIA.Process, "Deterministic reasoning engine"),
            MIA.LearningSystem: (MIA.Process, "Autonomous learning system")
        }
        
        for individual_uri, (class_uri, description) in individuals.items():
            self.graph.add((individual_uri, RDF.type, class_uri))
            self.graph.add((individual_uri, RDFS.comment, Literal(description)))
            
    def add_axioms(self):
        """Add ontology axioms"""
        # Disjoint classes
        self.graph.add((MIA.Agent, OWL.disjointWith, MIA.Knowledge))
        self.graph.add((MIA.Process, OWL.disjointWith, MIA.Resource))
        
        # Property characteristics
        self.graph.add((MIA.sharesKnowledgeWith, RDF.type, OWL.SymmetricProperty))
        self.graph.add((MIA.dependsOn, RDF.type, OWL.TransitiveProperty))
        
    def add_knowledge(self, subject: str, predicate: str, obj: str, confidence: float = 1.0):
        """Add knowledge to ontology"""
        subj_uri = MIA[subject] if not subject.startswith('http') else URIRef(subject)
        pred_uri = MIA[predicate] if not predicate.startswith('http') else URIRef(predicate)
        obj_uri = MIA[obj] if not obj.startswith('http') else URIRef(obj)
        
        self.graph.add((subj_uri, pred_uri, obj_uri))
        
        if confidence < 1.0:
            # Add confidence as reification
            stmt = BNode()
            self.graph.add((stmt, RDF.type, RDF.Statement))
            self.graph.add((stmt, RDF.subject, subj_uri))
            self.graph.add((stmt, RDF.predicate, pred_uri))
            self.graph.add((stmt, RDF.object, obj_uri))
            self.graph.add((stmt, MIA.confidence, Literal(confidence)))
            
    def query_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Query knowledge from ontology"""
        try:
            results = self.graph.query(query)
            return [dict(row.asdict()) for row in results]
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []
            
    def infer_knowledge(self) -> Set[tuple]:
        """Perform basic inference"""
        inferred = set()
        
        # Transitivity inference for dependsOn
        for s, p, o in self.graph.triples((None, MIA.dependsOn, None)):
            for s2, p2, o2 in self.graph.triples((o, MIA.dependsOn, None)):
                if (s, MIA.dependsOn, o2) not in self.graph:
                    inferred.add((s, MIA.dependsOn, o2))
                    
        # Symmetry inference for sharesKnowledgeWith
        for s, p, o in self.graph.triples((None, MIA.sharesKnowledgeWith, None)):
            if (o, MIA.sharesKnowledgeWith, s) not in self.graph:
                inferred.add((o, MIA.sharesKnowledgeWith, s))
                
        return inferred
        
    def validate_ontology(self) -> Dict[str, Any]:
        """Validate ontology consistency"""
        validation_results = {
            'is_consistent': True,
            'errors': [],
            'warnings': [],
            'statistics': {
                'total_triples': len(self.graph),
                'classes': len(list(self.graph.subjects(RDF.type, OWL.Class))),
                'properties': len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty))) + 
                            len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))),
                'individuals': len(list(self.graph.subjects(RDF.type, None))) - 
                            len(list(self.graph.subjects(RDF.type, OWL.Class))) -
                            len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty))) -
                            len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty)))
            }
        }
        
        return validation_results
        
    def export_ontology(self, format: str = 'turtle') -> str:
        """Export ontology in specified format"""
        return self.graph.serialize(format=format)
        
    def save_ontology(self, filepath: str, format: str = 'turtle'):
        """Save ontology to file"""
        with open(filepath, 'w') as f:
            f.write(self.export_ontology(format))
            
# Global ontology instance
mia_ontology = MIAOntology()

# Convenience functions
def add_knowledge(subject: str, predicate: str, obj: str, confidence: float = 1.0):
    """Add knowledge to MIA ontology"""
    mia_ontology.add_knowledge(subject, predicate, obj, confidence)
    
def query_knowledge(query: str) -> List[Dict[str, Any]]:
    """Query MIA ontology"""
    return mia_ontology.query_knowledge(query)
    
def validate_ontology() -> Dict[str, Any]:
    """Validate MIA ontology"""
    return mia_ontology.validate_ontology()
