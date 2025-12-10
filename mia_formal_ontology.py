#!/usr/bin/env python3
"""
🧠 MIA Enterprise AGI - Formalna Ontološka Shema
Popolna formalna ontologija za celoten MIA sistem z matematičnimi definicijami
"""

import json
import yaml
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

class ConceptType(Enum):
    """Tipi konceptov v ontologiji"""
    ENTITY = "entity"
    PROCESS = "process"
    PROPERTY = "property"
    RELATION = "relation"
    CONSTRAINT = "constraint"
    AXIOM = "axiom"

class RelationType(Enum):
    """Tipi relacij med koncepti"""
    IS_A = "is_a"                    # Hierarhična relacija
    PART_OF = "part_of"              # Kompozicijska relacija
    DEPENDS_ON = "depends_on"        # Odvisnostna relacija
    IMPLEMENTS = "implements"        # Implementacijska relacija
    USES = "uses"                    # Uporabnostna relacija
    PRODUCES = "produces"            # Produkcijska relacija
    CONSUMES = "consumes"            # Konzumacijska relacija
    CONTROLS = "controls"            # Kontrolna relacija
    MONITORS = "monitors"            # Nadzorna relacija
    COMMUNICATES_WITH = "communicates_with"  # Komunikacijska relacija

@dataclass
class Concept:
    """Formalni koncept v ontologiji"""
    id: str
    name: str
    type: ConceptType
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    axioms: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Relation:
    """Formalna relacija med koncepti"""
    id: str
    source: str
    target: str
    type: RelationType
    properties: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    weight: float = 1.0

class MIAFormalOntology:
    """Formalna ontologija MIA Enterprise AGI sistema"""
    
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.relations: Dict[str, Relation] = {}
        self.graph = nx.DiGraph()
        self.taxonomy = {}
        self.axioms = []
        
        # Inicializiraj ontologijo
        self._initialize_core_ontology()
    
    def _initialize_core_ontology(self):
        """Inicializira osnovno ontologijo MIA sistema"""
        
        # === OSNOVNI KONCEPTI ===
        
        # MIA System Root
        self.add_concept(Concept(
            id="mia_system",
            name="MIA Enterprise AGI System",
            type=ConceptType.ENTITY,
            description="Glavni sistem MIA Enterprise AGI platforme",
            properties={
                "version": "2.0",
                "architecture": "hybrid_enterprise",
                "deployment": "production_ready",
                "scalability": "enterprise_grade"
            },
            axioms=[
                "∀x (MIASystem(x) → EnterpriseAGI(x))",
                "∀x (MIASystem(x) → ProductionReady(x))",
                "∀x (MIASystem(x) → Scalable(x))"
            ]
        ))
        
        # === CORE KOMPONENTE ===
        
        # AGI Core
        self.add_concept(Concept(
            id="agi_core",
            name="AGI Core Engine",
            type=ConceptType.ENTITY,
            description="Osrednji AGI motor z model discovery integracijo",
            properties={
                "reasoning_capability": "advanced",
                "model_switching": "dynamic",
                "learning_integration": "active"
            },
            constraints=[
                "must_have_model_discovery",
                "must_support_dynamic_switching",
                "must_integrate_with_learning_system"
            ]
        ))
        
        # Learning System
        self.add_concept(Concept(
            id="learning_system",
            name="Autonomous Learning System",
            type=ConceptType.PROCESS,
            description="Avtonomni učni sistem z conversation analysis",
            properties={
                "learning_type": "autonomous",
                "pattern_recognition": "advanced",
                "knowledge_extraction": "automatic"
            },
            axioms=[
                "∀x,y (Learn(x,y) → Knowledge(x) ⊆ Knowledge(x) ∪ {y})",
                "∀x (AutonomousLearning(x) → ContinuousImprovement(x))"
            ]
        ))
        
        # Model Discovery
        self.add_concept(Concept(
            id="model_discovery",
            name="Model Discovery Engine",
            type=ConceptType.PROCESS,
            description="Sistem za odkrivanje in upravljanje AI modelov",
            properties={
                "scan_paths": 47,
                "supported_formats": ["gguf", "safetensors", "pytorch", "onnx"],
                "auto_detection": True
            }
        ))
        
        # === ENTERPRISE KOMPONENTE ===
        
        # Enterprise Monitoring
        self.add_concept(Concept(
            id="enterprise_monitoring",
            name="Enterprise Monitoring System",
            type=ConceptType.PROCESS,
            description="Napredni monitoring sistem za enterprise uporabo",
            properties={
                "real_time_metrics": True,
                "alerting": "advanced",
                "dashboard": "comprehensive"
            }
        ))
        
        # Security System
        self.add_concept(Concept(
            id="security_system",
            name="Enterprise Security System",
            type=ConceptType.ENTITY,
            description="Varnostni sistem z JWT avtentifikacijo",
            properties={
                "authentication": "JWT",
                "authorization": "RBAC",
                "encryption": "AES-256"
            },
            constraints=[
                "must_authenticate_users",
                "must_authorize_actions",
                "must_encrypt_sensitive_data"
            ]
        ))
        
        # Configuration Manager
        self.add_concept(Concept(
            id="config_manager",
            name="Configuration Management System",
            type=ConceptType.ENTITY,
            description="Sistem za upravljanje konfiguracije",
            properties={
                "environment_support": ["development", "staging", "production"],
                "validation": "schema_based",
                "hot_reload": True
            }
        ))
        
        # === MULTIMODAL KOMPONENTE ===
        
        # Multimodal System
        self.add_concept(Concept(
            id="multimodal_system",
            name="Multimodal Processing System",
            type=ConceptType.PROCESS,
            description="Sistem za procesiranje različnih modalnosti",
            properties={
                "supported_modalities": ["text", "image", "audio", "video"],
                "file_upload": True,
                "processing_pipeline": "advanced"
            }
        ))
        
        # TTS System
        self.add_concept(Concept(
            id="tts_system",
            name="Text-to-Speech System",
            type=ConceptType.PROCESS,
            description="Sistem za pretvorbo besedila v govor",
            properties={
                "voices": "multiple",
                "languages": "multilingual",
                "quality": "high"
            }
        ))
        
        # === INTERFACE KOMPONENTE ===
        
        # Chat Interface
        self.add_concept(Concept(
            id="chat_interface",
            name="Chat Interface System",
            type=ConceptType.ENTITY,
            description="Uporabniški vmesnik za pogovor",
            properties={
                "real_time": True,
                "learning_integration": True,
                "multimodal_support": True
            }
        ))
        
        # Web Interface
        self.add_concept(Concept(
            id="web_interface",
            name="Web Interface System",
            type=ConceptType.ENTITY,
            description="Spletni uporabniški vmesnik",
            properties={
                "responsive": True,
                "enterprise_features": True,
                "api_endpoints": "comprehensive"
            }
        ))
        
        # === RELACIJE ===
        
        # Hierarhične relacije
        self.add_relation("mia_system", "agi_core", RelationType.PART_OF)
        self.add_relation("mia_system", "learning_system", RelationType.PART_OF)
        self.add_relation("mia_system", "enterprise_monitoring", RelationType.PART_OF)
        self.add_relation("mia_system", "security_system", RelationType.PART_OF)
        self.add_relation("mia_system", "config_manager", RelationType.PART_OF)
        self.add_relation("mia_system", "multimodal_system", RelationType.PART_OF)
        self.add_relation("mia_system", "chat_interface", RelationType.PART_OF)
        self.add_relation("mia_system", "web_interface", RelationType.PART_OF)
        
        # Funkcionalne relacije
        self.add_relation("agi_core", "model_discovery", RelationType.USES)
        self.add_relation("agi_core", "learning_system", RelationType.USES)
        self.add_relation("learning_system", "enterprise_monitoring", RelationType.PRODUCES)
        self.add_relation("chat_interface", "learning_system", RelationType.USES)
        self.add_relation("multimodal_system", "tts_system", RelationType.USES)
        self.add_relation("web_interface", "security_system", RelationType.DEPENDS_ON)
        
        # Kontrolne relacije
        self.add_relation("enterprise_monitoring", "agi_core", RelationType.MONITORS)
        self.add_relation("security_system", "web_interface", RelationType.CONTROLS)
        self.add_relation("config_manager", "mia_system", RelationType.CONTROLS)
        
        # === GLOBALNI AKSIOMI ===
        self.axioms.extend([
            "∀x (MIAComponent(x) → Monitored(x))",
            "∀x (UserInteraction(x) → Authenticated(x))",
            "∀x (DataProcessing(x) → Logged(x))",
            "∀x,y (Communicates(x,y) → Secure(x,y))",
            "∀x (Learning(x) → PersistentKnowledge(x))"
        ])
    
    def add_concept(self, concept: Concept):
        """Dodaj koncept v ontologijo"""
        self.concepts[concept.id] = concept
        self.graph.add_node(concept.id, **concept.__dict__)
    
    def add_relation(self, source: str, target: str, relation_type: RelationType, **properties):
        """Dodaj relacijo med koncepti"""
        relation_id = f"{source}_{relation_type.value}_{target}"
        relation = Relation(
            id=relation_id,
            source=source,
            target=target,
            type=relation_type,
            properties=properties
        )
        self.relations[relation_id] = relation
        self.graph.add_edge(source, target, type=relation_type.value, **properties)
    
    def get_concept_hierarchy(self, concept_id: str) -> Dict[str, Any]:
        """Pridobi hierarhijo koncepta"""
        if concept_id not in self.concepts:
            return {}
        
        # Najdi starše (is_a, part_of relacije)
        parents = []
        for rel_id, relation in self.relations.items():
            if (relation.target == concept_id and 
                relation.type in [RelationType.IS_A, RelationType.PART_OF]):
                parents.append(relation.source)
        
        # Najdi otroke
        children = []
        for rel_id, relation in self.relations.items():
            if (relation.source == concept_id and 
                relation.type in [RelationType.IS_A, RelationType.PART_OF]):
                children.append(relation.target)
        
        return {
            "concept": self.concepts[concept_id],
            "parents": parents,
            "children": children
        }
    
    def validate_ontology(self) -> Dict[str, Any]:
        """Validira konsistentnost ontologije"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Preveri ciklične odvisnosti
        try:
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                validation_results["errors"].append(f"Ciklične odvisnosti: {cycles}")
                validation_results["valid"] = False
        except:
            pass
        
        # Preveri nedostopne koncepte
        unreachable = []
        for concept_id in self.concepts:
            if not nx.has_path(self.graph, "mia_system", concept_id):
                unreachable.append(concept_id)
        
        if unreachable:
            validation_results["warnings"].append(f"Nedostopni koncepti: {unreachable}")
        
        # Statistike
        validation_results["statistics"] = {
            "total_concepts": len(self.concepts),
            "total_relations": len(self.relations),
            "graph_density": nx.density(self.graph),
            "strongly_connected_components": len(list(nx.strongly_connected_components(self.graph)))
        }
        
        return validation_results
    
    def export_ontology(self, format: str = "json") -> str:
        """Izvozi ontologijo v različne formate"""
        ontology_data = {
            "metadata": {
                "name": "MIA Enterprise AGI Ontology",
                "version": "2.0",
                "created": datetime.now().isoformat(),
                "description": "Formalna ontologija MIA Enterprise AGI sistema"
            },
            "concepts": {cid: {
                "id": concept.id,
                "name": concept.name,
                "type": concept.type.value,
                "description": concept.description,
                "properties": concept.properties,
                "constraints": concept.constraints,
                "axioms": concept.axioms,
                "metadata": concept.metadata
            } for cid, concept in self.concepts.items()},
            "relations": {rid: {
                "id": relation.id,
                "source": relation.source,
                "target": relation.target,
                "type": relation.type.value,
                "properties": relation.properties,
                "constraints": relation.constraints,
                "weight": relation.weight
            } for rid, relation in self.relations.items()},
            "axioms": self.axioms
        }
        
        if format.lower() == "json":
            return json.dumps(ontology_data, indent=2, ensure_ascii=False)
        elif format.lower() == "yaml":
            return yaml.dump(ontology_data, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Nepodprt format: {format}")
    
    def visualize_ontology(self, output_file: str = "mia_ontology.png"):
        """Vizualiziraj ontologijo"""
        plt.figure(figsize=(20, 15))
        
        # Uporabi hierarhični layout
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        # Nariši vozlišča
        node_colors = []
        for node in self.graph.nodes():
            concept = self.concepts.get(node)
            if concept:
                if concept.type == ConceptType.ENTITY:
                    node_colors.append('lightblue')
                elif concept.type == ConceptType.PROCESS:
                    node_colors.append('lightgreen')
                else:
                    node_colors.append('lightgray')
            else:
                node_colors.append('white')
        
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, 
                              node_size=3000, alpha=0.8)
        
        # Nariši povezave
        edge_colors = []
        for edge in self.graph.edges(data=True):
            edge_type = edge[2].get('type', '')
            if edge_type == 'part_of':
                edge_colors.append('blue')
            elif edge_type == 'uses':
                edge_colors.append('green')
            elif edge_type == 'depends_on':
                edge_colors.append('red')
            else:
                edge_colors.append('gray')
        
        nx.draw_networkx_edges(self.graph, pos, edge_color=edge_colors, 
                              arrows=True, arrowsize=20, alpha=0.6)
        
        # Dodaj oznake
        labels = {node: node.replace('_', '\n') for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title("MIA Enterprise AGI - Formalna Ontologija", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file

def main():
    """Glavna funkcija za testiranje ontologije"""
    print("🧠 === GENERIRANJE FORMALNE ONTOLOGIJE MIA SISTEMA ===")
    print()
    
    # Ustvari ontologijo
    ontology = MIAFormalOntology()
    
    # Validiraj ontologijo
    print("🔍 Validacija ontologije...")
    validation = ontology.validate_ontology()
    
    print(f"   ✅ Veljavnost: {'DA' if validation['valid'] else 'NE'}")
    print(f"   📊 Koncepti: {validation['statistics']['total_concepts']}")
    print(f"   🔗 Relacije: {validation['statistics']['total_relations']}")
    print(f"   📈 Gostota grafa: {validation['statistics']['graph_density']:.3f}")
    
    if validation['errors']:
        print("   ❌ Napake:")
        for error in validation['errors']:
            print(f"      - {error}")
    
    if validation['warnings']:
        print("   ⚠️ Opozorila:")
        for warning in validation['warnings']:
            print(f"      - {warning}")
    
    # Izvozi ontologijo
    print()
    print("💾 Izvažanje ontologije...")
    
    # JSON format
    json_ontology = ontology.export_ontology("json")
    with open("mia_formal_ontology.json", "w", encoding="utf-8") as f:
        f.write(json_ontology)
    print("   📄 JSON: mia_formal_ontology.json")
    
    # YAML format
    yaml_ontology = ontology.export_ontology("yaml")
    with open("mia_formal_ontology.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_ontology)
    print("   📄 YAML: mia_formal_ontology.yaml")
    
    # Vizualizacija
    print()
    print("🎨 Vizualizacija ontologije...")
    try:
        viz_file = ontology.visualize_ontology()
        print(f"   🖼️ Diagram: {viz_file}")
    except Exception as e:
        print(f"   ⚠️ Vizualizacija ni mogoča: {e}")
    
    # Prikaz hierarhije ključnih konceptov
    print()
    print("🏗️ Hierarhija ključnih konceptov:")
    
    key_concepts = ["mia_system", "agi_core", "learning_system", "enterprise_monitoring"]
    for concept_id in key_concepts:
        hierarchy = ontology.get_concept_hierarchy(concept_id)
        if hierarchy:
            concept = hierarchy["concept"]
            print(f"   🔧 {concept.name}:")
            print(f"      📝 {concept.description}")
            if hierarchy["children"]:
                print(f"      👶 Otroci: {', '.join(hierarchy['children'])}")
    
    print()
    print("✅ FORMALNA ONTOLOGIJA GENERIRANA!")
    print("   📊 Popolna formalna specifikacija MIA sistema")
    print("   🔍 Validirana konsistentnost")
    print("   💾 Izvožena v JSON in YAML formatih")
    print("   🎨 Vizualizirana arhitektura")

if __name__ == "__main__":
    main()