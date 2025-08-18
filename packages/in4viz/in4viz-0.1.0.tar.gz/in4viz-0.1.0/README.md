# in4viz

Python library for ER diagram visualization with SVG output. Features a stencil-based architecture for flexible and customizable entity-relationship diagram generation.

## Features

- **Entity-Relationship Diagrams**: Create professional ER diagrams with tables, columns, and relationships
- **Japanese/English Support**: Full support for both logical names (Japanese) and physical names (English)
- **SVG Output**: Generate scalable vector graphics that look crisp at any size
- **Flexible Styling**: Customizable table layouts with automatic width calculation
- **Relationship Types**: Support for various cardinality types using IE notation (1, 0..1, 1..*, 0..*, etc.)
- **Auto Layout**: Smart positioning with FK relationship-aware placement
- **Type-Safe**: Full type hints for better development experience

## Installation

```bash
pip install in4viz
```

## Quick Start

```python
from in4viz import ERDiagram, Table, Column, LineType, Cardinality

# Create a new ER diagram
diagram = ERDiagram()

# Define tables
users_table = Table(
    name='users',
    logical_name='ユーザー',
    columns=[
        Column('id', 'ユーザーID', 'INT', primary_key=True, nullable=False),
        Column('username', 'ユーザー名', 'VARCHAR(50)', nullable=False, index=True),
        Column('email', 'メールアドレス', 'VARCHAR(100)', nullable=False, index=True),
        Column('created_at', '作成日時', 'TIMESTAMP', nullable=False)
    ]
)

posts_table = Table(
    name='posts',
    logical_name='投稿',
    columns=[
        Column('id', '投稿ID', 'INT', primary_key=True, nullable=False),
        Column('user_id', 'ユーザーID', 'INT', nullable=False, foreign_key=True),
        Column('title', 'タイトル', 'VARCHAR(200)', nullable=False),
        Column('content', '本文', 'TEXT', nullable=True),
    ]
)

# Add tables to diagram
diagram.add_table(users_table)
diagram.add_table(posts_table)

# Add relationships with cardinality
diagram.add_edge('posts', 'users', LineType.STRAIGHT, Cardinality('*', '1'))

# Generate SVG
diagram.save_svg('er_diagram.svg')
```

## API Reference

### ERDiagram

Main class for creating and managing ER diagrams.

```python
class ERDiagram:
    def __init__(self, default_line_type: LineType = LineType.STRAIGHT)
    def add_table(self, table: Table, x: int = None, y: int = None) -> str
    def add_edge(self, from_node_id: str, to_node_id: str, line_type: LineType = None, cardinality: Cardinality = None)
    def save_svg(self, output: str)
    def render_svg(self) -> str
```

### Table

Represents a database table with columns.

```python
@dataclass
class Table:
    name: str              # Physical table name
    logical_name: str      # Logical table name (for display)
    columns: List[Column]  # List of table columns
```

### Column

Represents a table column with properties.

```python
@dataclass
class Column:
    name: str              # Physical column name
    logical_name: str      # Logical column name (for display)
    type: str              # Data type (e.g., 'VARCHAR(50)', 'INT')
    primary_key: bool = False
    nullable: bool = True
    foreign_key: bool = False
    index: bool = False
```

### LineType

Enumeration for relationship line styles.

```python
class LineType(Enum):
    STRAIGHT = "straight"  # Direct line
    CRANK = "crank"       # Angled line
    SPLINE = "spline"     # Curved line
```

### Cardinality

Defines relationship cardinality using IE notation.

```python
@dataclass
class Cardinality:
    from_side: str = "1"  # "1", "0..1", "1..*", "0..*"
    to_side: str = "1"    # "1", "0..1", "1..*", "0..*"
```

## Advanced Usage

### Custom Table Positioning

```python
# Manually position tables
diagram.add_table(users_table, x=100, y=50)
diagram.add_table(posts_table, x=400, y=50)
```

### Multiple Relationship Types

```python
# One-to-many relationship
diagram.add_edge('posts', 'users', LineType.STRAIGHT, Cardinality('*', '1'))

# Many-to-many through junction table
diagram.add_edge('post_categories', 'posts', LineType.CRANK, Cardinality('*', '1'))
diagram.add_edge('post_categories', 'categories', LineType.CRANK, Cardinality('*', '1'))
```

### Styling Features

- **Primary Key Separation**: Primary key columns are automatically separated with a horizontal line
- **NOT NULL Indicators**: Black squares indicate non-nullable columns
- **Foreign Key Markers**: "FK" labels on foreign key columns
- **Index Indicators**: "IDX" labels on indexed columns
- **Smart Layout**: Tables with FK relationships are positioned adjacently

## Requirements

- Python >= 3.8
- No external dependencies

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
