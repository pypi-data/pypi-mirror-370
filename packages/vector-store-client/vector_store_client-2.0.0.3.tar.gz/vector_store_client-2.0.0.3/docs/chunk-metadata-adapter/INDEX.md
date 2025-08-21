# Documentation Index

- [README (Overview, Glossary, Links)](README.md)
- [Project Goals & Metadata Structure](Metadata.md)
- [Component Interaction & Architecture](Component_Interaction.md)
- [Flat <-> Semantic Conversion Rules](flat_semantic_conversion.md)
- [Data Lifecycle & Statuses](data_lifecycle.en.md)
- [Usage Guide & Examples](Usage.md)

---

## File Overview

| File                        | Purpose / Content |
|-----------------------------|-------------------|
| [README.md](README.md)      | Project overview, glossary, navigation links |
| [Metadata.md](Metadata.md)  | Full field list, types, constraints, business logic, autofill, validation |
| [Component_Interaction.md](Component_Interaction.md) | Architecture, component roles, integration patterns |
| [flat_semantic_conversion.md](flat_semantic_conversion.md) | Rules for converting between flat and structured models, edge-cases |
| [data_lifecycle.en.md](data_lifecycle.en.md) | Lifecycle stages, statuses, filtering, state transitions |
| [Usage.md](Usage.md)        | Usage patterns, code examples, best practices |

---

## Quick Links

- [Glossary (EN)](README.md#glossary)
- [Glossary (RU)](README.ru.md#глоссарий)
- [Field Table](Metadata.md#detailed-field-descriptions)
- [Enum Values](Metadata.md#enum-fields)
- [Conversion Rules](flat_semantic_conversion.md)
- [Lifecycle Stages](data_lifecycle.en.md#lifecycle-stages)
- [Integration Examples](Component_Interaction.md#integration-examples)
- [Code Examples](Usage.md#basic-usage)

---

## Best Practices

- Always validate and autofill metadata using the builder
- Use flat model for storage, structured for analytics
- Follow lifecycle and status conventions
- See [Usage.md](Usage.md#performance-considerations) for optimization tips 