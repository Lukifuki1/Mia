#!/usr/bin/env python3
"""
📐 MIA Enterprise AGI - Mathematical Semantic Layer Reconstruction
Formalna matematična rekonstrukcija semantičnega sloja
"""

import sys
import os
import json
import numpy as np
import sympy as sp
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial.distance import cosine, euclidean
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import defaultdict, Counter
import hashlib

# Dodaj MIA path
sys.path.insert(0, '.')

class SemanticRelationType(Enum):
    """Tipi semantičnih relacij"""
    SIMILARITY = "similarity"
    ENTAILMENT = "entailment"
    CONTRADICTION = "contradiction"
    HYPERNYMY = "hypernymy"
    HYPONYMY = "hyponymy"
    MERONYMY = "meronymy"
    HOLONYMY = "holonymy"
    SYNONYMY = "synonymy"
    ANTONYMY = "antonymy"
    CAUSALITY = "causality"

class SemanticSpace(Enum):
    """Semantični prostori"""
    LEXICAL = "lexical"
    CONCEPTUAL = "conceptual"
    CONTEXTUAL = "contextual"
    TEMPORAL = "temporal"
    MODAL = "modal"
    PRAGMATIC = "pragmatic"

@dataclass
class SemanticVector:
    """Semantični vektor"""
    id: str
    content: str
    vector: np.ndarray
    space: SemanticSpace
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SemanticRelation:
    """Semantična relacija"""
    id: str
    source: str
    target: str
    relation_type: SemanticRelationType
    strength: float
    confidence: float
    mathematical_proof: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SemanticTransformation:
    """Semantična transformacija"""
    id: str
    name: str
    input_space: SemanticSpace
    output_space: SemanticSpace
    transformation_matrix: np.ndarray
    mathematical_definition: str
    properties: Dict[str, Any] = field(default_factory=dict)

class MathematicalSemanticLayer:
    """Matematični semantični sloj"""
    
    def __init__(self, dimension: int = 512):
        self.logger = logging.getLogger("MIA.MathematicalSemanticLayer")
        self.dimension = dimension
        
        # Semantični prostori
        self.semantic_vectors: Dict[str, SemanticVector] = {}
        self.semantic_relations: Dict[str, SemanticRelation] = {}
        self.semantic_transformations: Dict[str, SemanticTransformation] = {}
        
        # Matematične strukture
        self.vector_space = self._initialize_vector_space()
        self.metric_tensor = self._initialize_metric_tensor()
        self.semantic_graph = nx.DiGraph()
        
        # Operatorji
        self.semantic_operators = self._initialize_semantic_operators()
        
        self.logger.info(f"Mathematical Semantic Layer initialized with dimension {dimension}")
    
    def _initialize_vector_space(self) -> Dict[str, Any]:
        """Inicializira vektorski prostor"""
        return {
            'dimension': self.dimension,
            'basis_vectors': np.eye(self.dimension),
            'metric': 'euclidean',
            'norm': 'l2',
            'inner_product': np.dot
        }
    
    def _initialize_metric_tensor(self) -> np.ndarray:
        """Inicializira metrični tenzor"""
        # Začni z evklidsko metriko
        return np.eye(self.dimension)
    
    def _initialize_semantic_operators(self) -> Dict[str, Callable]:
        """Inicializira semantične operatorje"""
        return {
            'similarity': self._similarity_operator,
            'composition': self._composition_operator,
            'negation': self._negation_operator,
            'entailment': self._entailment_operator,
            'projection': self._projection_operator,
            'rotation': self._rotation_operator,
            'scaling': self._scaling_operator,
            'translation': self._translation_operator
        }
    
    def create_semantic_vector(self, content: str, space: SemanticSpace, 
                             vector: Optional[np.ndarray] = None) -> SemanticVector:
        """Ustvari semantični vektor"""
        vector_id = hashlib.md5(content.encode()).hexdigest()
        
        if vector is None:
            # Generiraj vektor iz vsebine
            vector = self._encode_content(content, space)
        
        # Normaliziraj vektor
        vector = vector / np.linalg.norm(vector)
        
        # Izračunaj zaupanje
        confidence = self._calculate_vector_confidence(vector, content, space)
        
        semantic_vector = SemanticVector(
            id=vector_id,
            content=content,
            vector=vector,
            space=space,
            confidence=confidence,
            metadata={
                'created_at': datetime.now().isoformat(),
                'norm': np.linalg.norm(vector),
                'sparsity': np.count_nonzero(vector) / len(vector)
            }
        )
        
        self.semantic_vectors[vector_id] = semantic_vector
        self.semantic_graph.add_node(vector_id, **asdict(semantic_vector))
        
        return semantic_vector
    
    def _encode_content(self, content: str, space: SemanticSpace) -> np.ndarray:
        """Kodira vsebino v vektor"""
        if space == SemanticSpace.LEXICAL:
            return self._lexical_encoding(content)
        elif space == SemanticSpace.CONCEPTUAL:
            return self._conceptual_encoding(content)
        elif space == SemanticSpace.CONTEXTUAL:
            return self._contextual_encoding(content)
        elif space == SemanticSpace.TEMPORAL:
            return self._temporal_encoding(content)
        elif space == SemanticSpace.MODAL:
            return self._modal_encoding(content)
        elif space == SemanticSpace.PRAGMATIC:
            return self._pragmatic_encoding(content)
        else:
            return self._default_encoding(content)
    
    def _lexical_encoding(self, content: str) -> np.ndarray:
        """Leksikalno kodiranje"""
        # Preprosto bag-of-words z hash funkcijo
        words = re.findall(r'\w+', content.lower())
        vector = np.zeros(self.dimension)
        
        for word in words:
            hash_val = hash(word) % self.dimension
            vector[hash_val] += 1
        
        return vector
    
    def _conceptual_encoding(self, content: str) -> np.ndarray:
        """Konceptualno kodiranje"""
        # Simulacija konceptualnega kodiranja
        concepts = self._extract_concepts(content)
        vector = np.zeros(self.dimension)
        
        for i, concept in enumerate(concepts):
            if i < self.dimension:
                vector[i] = self._concept_weight(concept)
        
        return vector
    
    def _contextual_encoding(self, content: str) -> np.ndarray:
        """Kontekstualno kodiranje"""
        # Simulacija kontekstualnega kodiranja
        context_features = self._extract_context_features(content)
        vector = np.random.normal(0, 0.1, self.dimension)
        
        # Modificiraj vektor glede na kontekst
        for feature, weight in context_features.items():
            hash_val = hash(feature) % self.dimension
            vector[hash_val] += weight
        
        return vector
    
    def _temporal_encoding(self, content: str) -> np.ndarray:
        """Temporalno kodiranje"""
        # Simulacija temporalnega kodiranja
        temporal_markers = ['before', 'after', 'during', 'while', 'when', 'then', 'now', 'past', 'future']
        vector = np.zeros(self.dimension)
        
        for i, marker in enumerate(temporal_markers):
            if marker in content.lower() and i < self.dimension:
                vector[i] = content.lower().count(marker)
        
        return vector
    
    def _modal_encoding(self, content: str) -> np.ndarray:
        """Modalno kodiranje"""
        # Simulacija modalnega kodiranja
        modal_verbs = ['can', 'could', 'may', 'might', 'must', 'should', 'would', 'will']
        vector = np.zeros(self.dimension)
        
        for i, modal in enumerate(modal_verbs):
            if modal in content.lower() and i < self.dimension:
                vector[i] = content.lower().count(modal)
        
        return vector
    
    def _pragmatic_encoding(self, content: str) -> np.ndarray:
        """Pragmatično kodiranje"""
        # Simulacija pragmatičnega kodiranja
        pragmatic_features = {
            'question': '?' in content,
            'exclamation': '!' in content,
            'politeness': any(word in content.lower() for word in ['please', 'thank', 'sorry']),
            'formality': any(word in content.lower() for word in ['sir', 'madam', 'respectfully'])
        }
        
        vector = np.zeros(self.dimension)
        for i, (feature, present) in enumerate(pragmatic_features.items()):
            if i < self.dimension:
                vector[i] = 1.0 if present else 0.0
        
        return vector
    
    def _default_encoding(self, content: str) -> np.ndarray:
        """Privzeto kodiranje"""
        # Preprosto hash-based kodiranje
        hash_val = hash(content)
        np.random.seed(hash_val % (2**32))
        return np.random.normal(0, 1, self.dimension)
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Izvleče koncepte iz vsebine"""
        # Preprosta implementacija - v resnici bi uporabili NLP
        words = re.findall(r'\w+', content.lower())
        # Filtriraj stop words in vrni pomembne besede
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _extract_context_features(self, content: str) -> Dict[str, float]:
        """Izvleče kontekstualne značilke"""
        return {
            'length': len(content) / 1000,  # Normalizirano
            'complexity': len(content.split()) / 100,  # Število besed
            'punctuation': sum(1 for c in content if c in '.,!?;:') / len(content),
            'capitalization': sum(1 for c in content if c.isupper()) / len(content)
        }
    
    def _concept_weight(self, concept: str) -> float:
        """Izračuna težo koncepta"""
        # Preprosta implementacija - v resnici bi uporabili word embeddings
        return len(concept) / 10.0  # Daljše besede imajo večjo težo
    
    def _calculate_vector_confidence(self, vector: np.ndarray, content: str, space: SemanticSpace) -> float:
        """Izračuna zaupanje vektorja"""
        # Zaupanje na osnovi norm vektorja in dolžine vsebine
        norm_confidence = min(1.0, np.linalg.norm(vector) / 10.0)
        content_confidence = min(1.0, len(content) / 100.0)
        space_confidence = 0.8  # Privzeto zaupanje za prostor
        
        return (norm_confidence + content_confidence + space_confidence) / 3.0
    
    def create_semantic_relation(self, source_id: str, target_id: str, 
                                relation_type: SemanticRelationType) -> SemanticRelation:
        """Ustvari semantično relacijo"""
        if source_id not in self.semantic_vectors or target_id not in self.semantic_vectors:
            raise ValueError("Source or target vector not found")
        
        source_vector = self.semantic_vectors[source_id]
        target_vector = self.semantic_vectors[target_id]
        
        # Izračunaj moč relacije
        strength = self._calculate_relation_strength(source_vector, target_vector, relation_type)
        
        # Izračunaj zaupanje
        confidence = self._calculate_relation_confidence(source_vector, target_vector, relation_type, strength)
        
        # Generiraj matematični dokaz
        mathematical_proof = self._generate_mathematical_proof(source_vector, target_vector, relation_type, strength)
        
        relation_id = f"{source_id}_{relation_type.value}_{target_id}"
        
        relation = SemanticRelation(
            id=relation_id,
            source=source_id,
            target=target_id,
            relation_type=relation_type,
            strength=strength,
            confidence=confidence,
            mathematical_proof=mathematical_proof,
            metadata={
                'created_at': datetime.now().isoformat(),
                'source_space': source_vector.space.value,
                'target_space': target_vector.space.value
            }
        )
        
        self.semantic_relations[relation_id] = relation
        self.semantic_graph.add_edge(source_id, target_id, **asdict(relation))
        
        return relation
    
    def _calculate_relation_strength(self, source: SemanticVector, target: SemanticVector, 
                                   relation_type: SemanticRelationType) -> float:
        """Izračuna moč semantične relacije"""
        if relation_type == SemanticRelationType.SIMILARITY:
            return 1 - cosine(source.vector, target.vector)
        elif relation_type == SemanticRelationType.ENTAILMENT:
            return self._entailment_strength(source.vector, target.vector)
        elif relation_type == SemanticRelationType.CONTRADICTION:
            return self._contradiction_strength(source.vector, target.vector)
        elif relation_type == SemanticRelationType.HYPERNYMY:
            return self._hypernymy_strength(source.vector, target.vector)
        elif relation_type == SemanticRelationType.HYPONYMY:
            return self._hyponymy_strength(source.vector, target.vector)
        else:
            # Privzeta implementacija
            return abs(np.dot(source.vector, target.vector))
    
    def _entailment_strength(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Izračuna moč entailment relacije"""
        # Entailment: v1 → v2, če je v2 "vsebovan" v v1
        projection = np.dot(v1, v2) / np.dot(v2, v2) * v2
        return np.linalg.norm(projection) / np.linalg.norm(v1)
    
    def _contradiction_strength(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Izračuna moč contradiction relacije"""
        # Contradiction: negativna korelacija
        correlation = np.corrcoef(v1, v2)[0, 1]
        return max(0, -correlation)
    
    def _hypernymy_strength(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Izračuna moč hypernymy relacije"""
        # Hypernymy: v1 je splošnejši od v2
        # Splošnost merimo z entropijo
        entropy_v1 = self._calculate_entropy(v1)
        entropy_v2 = self._calculate_entropy(v2)
        return max(0, entropy_v1 - entropy_v2) / max(entropy_v1, entropy_v2)
    
    def _hyponymy_strength(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Izračuna moč hyponymy relacije"""
        # Hyponymy: obratno od hypernymy
        return self._hypernymy_strength(v2, v1)
    
    def _calculate_entropy(self, vector: np.ndarray) -> float:
        """Izračuna entropijo vektorja"""
        # Normaliziraj vektor v verjetnostno distribucijo
        probs = np.abs(vector) / np.sum(np.abs(vector))
        probs = probs[probs > 0]  # Odstrani ničle
        return -np.sum(probs * np.log2(probs))
    
    def _calculate_relation_confidence(self, source: SemanticVector, target: SemanticVector,
                                     relation_type: SemanticRelationType, strength: float) -> float:
        """Izračuna zaupanje relacije"""
        # Zaupanje na osnovi zaupanja vektorjev in moči relacije
        vector_confidence = (source.confidence + target.confidence) / 2.0
        strength_confidence = min(1.0, strength * 2.0)  # Močnejše relacije so bolj zanesljive
        
        return (vector_confidence + strength_confidence) / 2.0
    
    def _generate_mathematical_proof(self, source: SemanticVector, target: SemanticVector,
                                   relation_type: SemanticRelationType, strength: float) -> str:
        """Generiraj matematični dokaz relacije"""
        if relation_type == SemanticRelationType.SIMILARITY:
            return f"sim(v₁, v₂) = 1 - cos_dist(v₁, v₂) = {strength:.3f}"
        elif relation_type == SemanticRelationType.ENTAILMENT:
            return f"entail(v₁, v₂) = ||proj_v₂(v₁)|| / ||v₁|| = {strength:.3f}"
        elif relation_type == SemanticRelationType.CONTRADICTION:
            return f"contra(v₁, v₂) = max(0, -corr(v₁, v₂)) = {strength:.3f}"
        elif relation_type == SemanticRelationType.HYPERNYMY:
            return f"hyper(v₁, v₂) = (H(v₁) - H(v₂)) / max(H(v₁), H(v₂)) = {strength:.3f}"
        else:
            return f"rel(v₁, v₂) = |v₁ · v₂| = {strength:.3f}"
    
    def create_semantic_transformation(self, name: str, input_space: SemanticSpace, 
                                     output_space: SemanticSpace, 
                                     transformation_matrix: Optional[np.ndarray] = None) -> SemanticTransformation:
        """Ustvari semantično transformacijo"""
        if transformation_matrix is None:
            transformation_matrix = self._generate_transformation_matrix(input_space, output_space)
        
        # Generiraj matematično definicijo
        mathematical_definition = self._generate_transformation_definition(name, input_space, output_space)
        
        # Analiziraj lastnosti transformacije
        properties = self._analyze_transformation_properties(transformation_matrix)
        
        transformation_id = f"{input_space.value}_to_{output_space.value}_{name}"
        
        transformation = SemanticTransformation(
            id=transformation_id,
            name=name,
            input_space=input_space,
            output_space=output_space,
            transformation_matrix=transformation_matrix,
            mathematical_definition=mathematical_definition,
            properties=properties
        )
        
        self.semantic_transformations[transformation_id] = transformation
        
        return transformation
    
    def _generate_transformation_matrix(self, input_space: SemanticSpace, 
                                      output_space: SemanticSpace) -> np.ndarray:
        """Generiraj transformacijsko matriko"""
        # Preprosta implementacija - v resnici bi se naučili iz podatkov
        if input_space == output_space:
            return np.eye(self.dimension)
        else:
            # Naključna ortogonalna matrika
            matrix = np.random.normal(0, 1, (self.dimension, self.dimension))
            q, r = np.linalg.qr(matrix)
            return q
    
    def _generate_transformation_definition(self, name: str, input_space: SemanticSpace,
                                          output_space: SemanticSpace) -> str:
        """Generiraj matematično definicijo transformacije"""
        return f"T_{name}: {input_space.value} → {output_space.value}, T(v) = Av where A ∈ ℝ^{self.dimension}×{self.dimension}"
    
    def _analyze_transformation_properties(self, matrix: np.ndarray) -> Dict[str, Any]:
        """Analiziraj lastnosti transformacije"""
        eigenvalues = np.linalg.eigvals(matrix)
        
        return {
            'determinant': np.linalg.det(matrix),
            'trace': np.trace(matrix),
            'rank': np.linalg.matrix_rank(matrix),
            'condition_number': np.linalg.cond(matrix),
            'is_orthogonal': np.allclose(matrix @ matrix.T, np.eye(matrix.shape[0])),
            'is_symmetric': np.allclose(matrix, matrix.T),
            'eigenvalues_real': np.all(np.isreal(eigenvalues)),
            'spectral_radius': np.max(np.abs(eigenvalues))
        }
    
    # === SEMANTIČNI OPERATORJI ===
    
    def _similarity_operator(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Operator podobnosti"""
        return 1 - cosine(v1, v2)
    
    def _composition_operator(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """Operator kompozicije"""
        # Preprosta implementacija - element-wise produkt
        return v1 * v2
    
    def _negation_operator(self, v: np.ndarray) -> np.ndarray:
        """Operator negacije"""
        # Preprosta implementacija - obrnemo vektor
        return -v
    
    def _entailment_operator(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Operator entailment"""
        return self._entailment_strength(v1, v2)
    
    def _projection_operator(self, v: np.ndarray, subspace_basis: np.ndarray) -> np.ndarray:
        """Operator projekcije"""
        # Projekcija na podprostor
        projection_matrix = subspace_basis @ subspace_basis.T
        return projection_matrix @ v
    
    def _rotation_operator(self, v: np.ndarray, angle: float, axis: int = 0) -> np.ndarray:
        """Operator rotacije"""
        # Preprosta 2D rotacija v izbrani ravnini
        rotation_matrix = np.eye(len(v))
        if axis + 1 < len(v):
            c, s = np.cos(angle), np.sin(angle)
            rotation_matrix[axis, axis] = c
            rotation_matrix[axis, axis + 1] = -s
            rotation_matrix[axis + 1, axis] = s
            rotation_matrix[axis + 1, axis + 1] = c
        
        return rotation_matrix @ v
    
    def _scaling_operator(self, v: np.ndarray, scale: float) -> np.ndarray:
        """Operator skaliranja"""
        return scale * v
    
    def _translation_operator(self, v: np.ndarray, translation: np.ndarray) -> np.ndarray:
        """Operator translacije"""
        return v + translation
    
    # === ANALIZA IN VIZUALIZACIJA ===
    
    def analyze_semantic_space(self) -> Dict[str, Any]:
        """Analiziraj semantični prostor"""
        if not self.semantic_vectors:
            return {'error': 'No semantic vectors found'}
        
        vectors = np.array([sv.vector for sv in self.semantic_vectors.values()])
        
        # Osnovne statistike
        mean_vector = np.mean(vectors, axis=0)
        std_vector = np.std(vectors, axis=0)
        
        # Dimenzionalnost
        effective_dimension = np.sum(std_vector > 0.01)  # Dimenzije z varianco
        
        # Gostota
        pairwise_similarities = []
        vector_list = list(self.semantic_vectors.values())
        for i in range(len(vector_list)):
            for j in range(i + 1, len(vector_list)):
                sim = self._similarity_operator(vector_list[i].vector, vector_list[j].vector)
                pairwise_similarities.append(sim)
        
        # Analiza relacij
        relation_types = Counter(rel.relation_type.value for rel in self.semantic_relations.values())
        avg_relation_strength = np.mean([rel.strength for rel in self.semantic_relations.values()]) if self.semantic_relations else 0
        
        return {
            'total_vectors': len(self.semantic_vectors),
            'total_relations': len(self.semantic_relations),
            'effective_dimension': effective_dimension,
            'mean_similarity': np.mean(pairwise_similarities) if pairwise_similarities else 0,
            'std_similarity': np.std(pairwise_similarities) if pairwise_similarities else 0,
            'avg_relation_strength': avg_relation_strength,
            'relation_type_distribution': dict(relation_types),
            'vector_spaces': Counter(sv.space.value for sv in self.semantic_vectors.values()),
            'avg_confidence': np.mean([sv.confidence for sv in self.semantic_vectors.values()])
        }
    
    def visualize_semantic_space(self, output_file: str = "semantic_space.png"):
        """Vizualiziraj semantični prostor"""
        if len(self.semantic_vectors) < 2:
            self.logger.warning("Not enough vectors for visualization")
            return
        
        # Uporabi PCA za dimenzionalnost reduction
        from sklearn.decomposition import PCA
        
        vectors = np.array([sv.vector for sv in self.semantic_vectors.values()])
        labels = [sv.content[:20] + "..." if len(sv.content) > 20 else sv.content 
                 for sv in self.semantic_vectors.values()]
        
        # Reduciraj na 2D
        pca = PCA(n_components=2)
        vectors_2d = pca.fit_transform(vectors)
        
        # Vizualiziraj
        plt.figure(figsize=(12, 8))
        
        # Različne barve za različne prostore
        spaces = [sv.space.value for sv in self.semantic_vectors.values()]
        unique_spaces = list(set(spaces))
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_spaces)))
        
        for i, space in enumerate(unique_spaces):
            mask = [s == space for s in spaces]
            plt.scatter(vectors_2d[mask, 0], vectors_2d[mask, 1], 
                       c=[colors[i]], label=space, alpha=0.7, s=100)
        
        # Dodaj oznake
        for i, label in enumerate(labels):
            plt.annotate(label, (vectors_2d[i, 0], vectors_2d[i, 1]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Dodaj relacije
        for relation in self.semantic_relations.values():
            source_idx = list(self.semantic_vectors.keys()).index(relation.source)
            target_idx = list(self.semantic_vectors.keys()).index(relation.target)
            
            plt.arrow(vectors_2d[source_idx, 0], vectors_2d[source_idx, 1],
                     vectors_2d[target_idx, 0] - vectors_2d[source_idx, 0],
                     vectors_2d[target_idx, 1] - vectors_2d[source_idx, 1],
                     alpha=0.3, width=0.01, head_width=0.05, 
                     color='gray', length_includes_head=True)
        
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        plt.title('Mathematical Semantic Space Visualization')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def export_semantic_layer(self) -> Dict[str, Any]:
        """Izvozi semantični sloj"""
        return {
            'metadata': {
                'dimension': self.dimension,
                'created_at': datetime.now().isoformat(),
                'total_vectors': len(self.semantic_vectors),
                'total_relations': len(self.semantic_relations),
                'total_transformations': len(self.semantic_transformations)
            },
            'vector_space': {
                'dimension': self.vector_space['dimension'],
                'metric': self.vector_space['metric'],
                'norm': self.vector_space['norm']
            },
            'semantic_vectors': {
                vid: {
                    'id': sv.id,
                    'content': sv.content,
                    'vector': sv.vector.tolist(),
                    'space': sv.space.value,
                    'confidence': sv.confidence,
                    'metadata': sv.metadata
                }
                for vid, sv in self.semantic_vectors.items()
            },
            'semantic_relations': {
                rid: {
                    'id': rel.id,
                    'source': rel.source,
                    'target': rel.target,
                    'relation_type': rel.relation_type.value,
                    'strength': rel.strength,
                    'confidence': rel.confidence,
                    'mathematical_proof': rel.mathematical_proof,
                    'metadata': rel.metadata
                }
                for rid, rel in self.semantic_relations.items()
            },
            'semantic_transformations': {
                tid: {
                    'id': trans.id,
                    'name': trans.name,
                    'input_space': trans.input_space.value,
                    'output_space': trans.output_space.value,
                    'transformation_matrix': trans.transformation_matrix.tolist(),
                    'mathematical_definition': trans.mathematical_definition,
                    'properties': trans.properties
                }
                for tid, trans in self.semantic_transformations.items()
            },
            'analysis': self.analyze_semantic_space()
        }

def main():
    """Glavna funkcija za testiranje"""
    print("📐 === MATHEMATICAL SEMANTIC LAYER RECONSTRUCTION ===")
    print()
    
    # Nastavi logging
    logging.basicConfig(level=logging.INFO)
    
    # Ustvari semantični sloj
    semantic_layer = MathematicalSemanticLayer(dimension=128)
    
    # Test podatki
    test_contents = [
        ("Artificial intelligence is transforming technology", SemanticSpace.CONCEPTUAL),
        ("Machine learning algorithms process data", SemanticSpace.CONCEPTUAL),
        ("The cat sat on the mat", SemanticSpace.LEXICAL),
        ("Yesterday I went to the store", SemanticSpace.TEMPORAL),
        ("Can you help me with this problem?", SemanticSpace.PRAGMATIC),
        ("The system must be secure and reliable", SemanticSpace.MODAL)
    ]
    
    print("🔧 Ustvarjam semantične vektorje...")
    vectors = []
    for content, space in test_contents:
        vector = semantic_layer.create_semantic_vector(content, space)
        vectors.append(vector)
        print(f"   📊 {space.value}: {content[:30]}... (confidence: {vector.confidence:.3f})")
    
    print(f"\n🔗 Ustvarjam semantične relacije...")
    relations = []
    
    # Ustvari relacije med podobnimi vektorji
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            if vectors[i].space == vectors[j].space:
                relation = semantic_layer.create_semantic_relation(
                    vectors[i].id, vectors[j].id, SemanticRelationType.SIMILARITY
                )
                relations.append(relation)
                print(f"   🔗 {SemanticRelationType.SIMILARITY.value}: {relation.strength:.3f}")
    
    print(f"\n🔄 Ustvarjam semantične transformacije...")
    transformations = []
    
    # Ustvari transformacije med prostori
    space_pairs = [
        (SemanticSpace.LEXICAL, SemanticSpace.CONCEPTUAL),
        (SemanticSpace.CONCEPTUAL, SemanticSpace.PRAGMATIC),
        (SemanticSpace.TEMPORAL, SemanticSpace.MODAL)
    ]
    
    for input_space, output_space in space_pairs:
        transformation = semantic_layer.create_semantic_transformation(
            f"transform_{input_space.value}_to_{output_space.value}",
            input_space, output_space
        )
        transformations.append(transformation)
        print(f"   🔄 {transformation.name}: {transformation.properties['determinant']:.3f}")
    
    print(f"\n📊 Analiziram semantični prostor...")
    analysis = semantic_layer.analyze_semantic_space()
    
    print(f"   📈 Skupaj vektorjev: {analysis['total_vectors']}")
    print(f"   🔗 Skupaj relacij: {analysis['total_relations']}")
    print(f"   📏 Efektivna dimenzija: {analysis['effective_dimension']}")
    print(f"   🎯 Povprečna podobnost: {analysis['mean_similarity']:.3f}")
    print(f"   🔒 Povprečno zaupanje: {analysis['avg_confidence']:.3f}")
    
    print(f"\n🎨 Vizualiziram semantični prostor...")
    try:
        viz_file = semantic_layer.visualize_semantic_space()
        print(f"   🖼️ Diagram: {viz_file}")
    except Exception as e:
        print(f"   ⚠️ Vizualizacija ni mogoča: {e}")
    
    print(f"\n💾 Izvažam semantični sloj...")
    export_data = semantic_layer.export_semantic_layer()
    
    # Custom JSON encoder za numpy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif hasattr(obj, 'tolist'):
                return obj.tolist()
            return str(obj)  # Fallback za vse ostalo
    
    with open('mathematical_semantic_layer.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
    
    print(f"   📄 Izvoženo: mathematical_semantic_layer.json")
    
    print(f"\n✅ MATHEMATICAL SEMANTIC LAYER RECONSTRUCTION KONČANA!")
    print(f"   📐 Formalna matematična struktura vzpostavljena")
    print(f"   🔢 {analysis['total_vectors']} vektorjev v {analysis['effective_dimension']}D prostoru")
    print(f"   🔗 {analysis['total_relations']} semantičnih relacij")
    print(f"   🔄 {len(transformations)} semantičnih transformacij")

if __name__ == "__main__":
    main()