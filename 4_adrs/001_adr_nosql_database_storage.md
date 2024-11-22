# ADR001 - Use MongoDB (NoSQL) for Database Storage

## Context and Problem Statement
The AI assistant requires a database solution capable of:

- Storing and querying high-dimensional vector embeddings for semantic search and similarity matching.
- Managing traditional document storage for structured datasets, such as user orders and preferences.
- Accommodating evolving data structures to support new embedding models and dynamic business requirements.

The primary challenge is selecting a database that balances flexibility, scalability, and performance while efficiently handling both vector data and traditional document storage.

## Requirements
Analysis of the requirements and the desired functionality of the ShopWise AI assistant requires the backing of a database that can:
- Efficiently store and retrieve high-dimensional vector embeddings.
- Accommodate evolving data structures to support new embedding models and dynamic business requirements.
- Scale to handle large datasets as the system grows.
- Optimize performance to support low-latency queries at scale.
- Act as a transactional database for the AI assistant's agents to ensure data integrity as order and product data is updated.

## Business and Technical Assumptions
The ShopWise AI assistant will primarily store hierarchical and semi-structured data, reducing the need for strict relational integrity. It is assumed that the volume of embeddings and user data will grow significantly, and scalability is crucial. Indexing and query optimization will mitigate potential performance issues inherent in NoSQL databases.

Datasets that require strict relational integrity can be handled separately by a relational database suited specifically for analytical workloads.

## Decision Drivers
- Need for flexible schema to accommodate rapid iteration and new data types.
- Scalability for high volumes of embeddings and user data.
- Simplicity in managing semi-structured and hierarchical data.
- Performance considerations for vector search and traditional queries.

## Considered Options
1. SQL Databases (e.g., PostgreSQL)
- Advantages: Strong relational capabilities, ACID compliance, and robust support for structured queries.
- Disadvantages: Limited flexibility for hierarchical or nested data; vector search requires additional extensions like pgvector, increasing complexity.
2. Graph Databases (e.g., Neo4j)
- Advantages: Excellent for relationship-heavy queries and graph-based reasoning.
- Disadvantages: Introduces unnecessary complexity for a system that does not rely heavily on relationship traversal.
3. MongoDB (Selected Option)
- Advantages: Schema flexibility, scalability, and native support for hierarchical and semi-structured data.
- Disadvantages: Requires careful indexing and optimization for performance, especially for large datasets.

## Decision
MongoDB was selected as the database solution. It offers the flexibility, scalability, and performance characteristics required to handle both vector embeddings and traditional document storage effectively.

### Reasons
- Flexible schema design aligns with the evolving needs of the AI assistant.
- Supports hierarchical and nested data structures, simplifying data modeling.
- Scalable architecture is well-suited for high-volume data storage.
- Allows integration with vector search capabilities through third-party libraries or MongoDB Atlas features.

## Consequences
### Positive Impacts
- Simplified data modeling due to schema flexibility.
- Scalability ensures the system can grow with increasing data volumes.
- Compatibility with vector search enables efficient embedding storage and querying.
- Compatible with full-text search capabilities, enabling hybrid search.

### Trade-offs and Limitations
- Performance depends on proper indexing and optimization strategies.
- Lacks strong ACID guarantees for complex transactional operations.
- Initial learning curve for teams unfamiliar with MongoDB’s NoSQL paradigm.
