
## Task 2: AST Node Definitions and Serialization

### Objective
Replace simple parser output with proper Pydantic AST node definitions and implement JSON serialization for AST caching.

### Prerequisites
- Task 1 completed successfully
- Parser generating basic AST structures

### Deliverables

**1. AST Node Definitions**
```
minimidl/ast/
├── __init__.py
├── nodes.py                 # All Pydantic AST node classes
└── serialization.py         # JSON save/load functionality
```

**2. Pydantic AST Node Classes**
Create comprehensive node hierarchy:
- `ASTNode` (base class)
- `Namespace`, `Interface`, `Enum`, `Typedef`, `Constant`
- `Method`, `Property`, `Parameter`
- `Type`, `ArrayType`, `DictType`, `SetType`, `NullableType`
- `EnumValue`, `ConstantValue`
- `ForwardDeclaration`

**3. Parser Integration**
- Update parser.py to generate proper AST nodes
- Transformer class to convert Lark tree to AST
- Type validation and semantic analysis

**4. JSON Serialization**
- AST to JSON conversion with proper type handling
- JSON to AST deserialization
- File-based caching system

**5. Enhanced Testing**
- AST node validation tests
- Serialization round-trip tests
- Semantic analysis tests (type checking, forward references)

### Success Criteria
- All IDL constructs represented as proper AST nodes
- JSON serialization preserves all AST information
- Parser performs basic semantic validation
- AST nodes have comprehensive type hints
- Full test coverage for all node types

### Example AST Structure
```python
@dataclass
class Interface(ASTNode):
    name: str
    methods: List[Method]
    properties: List[Property]
    forward_declarations: List[str]
    
@dataclass
class Method(ASTNode):
    name: str
    return_type: Type
    parameters: List[Parameter]
    
@dataclass
class Type(ASTNode):
    name: str
    nullable: bool = False
    
@dataclass
class ArrayType(Type):
    element_type: Type
```