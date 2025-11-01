```mermaid
graph TD
    A[Utilisateur] --> B[Application Flask]
    B --> C[(SQLite - MVP)]
    B -.-> D[(PostgreSQL - Production)]
    B -.-> E{Intégrations API futures}
    E -.-> E1[OpenWeatherMap]
    E -.-> E2[Twilio / SendGrid]
```

> **Note** : La base de données SQLite est utilisée pour le MVP afin de simplifier le développement. La migration vers PostgreSQL et l'intégration d'API externes (météo, communication) sont prévues pour la phase de production.
