NoSQL (short for "Not Only SQL") is a type of database that is designed to handle large volumes of unstructured or semi-structured data efficiently

Types of NoSQL Databases (https://www.infoq.com/research/nosql-databases/):
1. Key-Value Stores (e.g., Redis, DynamoDB)
Data is stored as key-value pairs.
Great for caching and session management.
2. Document Stores (e.g., MongoDB, CouchDB)
Data is stored in JSON-like documents.
Ideal for content management, catalogs, and flexible data models.
3. Column-Family Stores (e.g., Cassandra, HBase)
Data is stored in columns rather than rows (optimized for read/write speed).
Used in big data applications.
4. Graph Databases (e.g., Neo4j, ArangoDB)
Data is stored as nodes and relationships.
Best for social networks, fraud detection, recommendation systems.

When to Use NoSQL?
✅ When you need high scalability and performance
✅ When dealing with large amounts of semi-structured or unstructured data
✅ When flexible schema is required
✅ For real-time applications, IoT, and big data analytics

![alt text](image.png)


~~~sql
MATCH (ee:Person) WHERE ee.name = 'Emil'
CREATE (js:Person { name: 'Johan', from: 'Sweden', learn: 'surfing' }),
(ir:Person { name: 'Ian', from: 'England', title: 'author' }),
(rvb:Person { name: 'Rik', from: 'Belgium', pet: 'Orval' }),
(ally:Person { name: 'Allison', from: 'California', hobby: 'surfing' }),
(ee)-[:FRIENDS_WITH {since: 2001}]->(js),
(ee)-[:COLLABORATES_WITH {project: 'Book'}]->(ir),
(js)-[:LEARNS_FROM {skill: 'surfing'}]->(ally),
(ir)-[:MENTORS]->(rvb),
(rvb)-[:LIVES_IN]->(belgium:Place {name: 'Belgium'}),
(ally)-[:PARTICIPATES_IN]->(surf_club:Club {name: 'Wave Riders'})
~~~