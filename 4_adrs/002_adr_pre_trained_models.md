# ADR002 - Use Pre-Trained Models for Natural Language Understanding (NLU)

## Status  
Accepted  

## Context and Problem Statement  
Natural Language Understanding (NLU) is essential for accurately interpreting diverse customer queries. The challenge is to choose an approach that balances performance, development effort, and cost while ensuring adaptability to domain-specific needs.  

### Requirements  
- High accuracy in understanding diverse and complex language inputs.  
- Ability to adapt and improve using domain-specific data via both in-context learning and/or fine-tuning.
- Minimized time-to-market and development costs.  
- Scalability to handle growing user queries and evolving language models.  

### Business and Technical Assumptions  
- Pre-trained models will provide a baseline of advanced capabilities, requiring only minimal fine-tuning for domain-specific contexts (if necessary).  
- In-house model development is extremely resource-intensive and unnecessary given the availability of state-of-the-art pre-trained models.  
- Licensing and integration of external models will be manageable within the project’s constraints.  

## Decision Drivers  
- Performance: Models must deliver state-of-the-art NLU capabilities.  
- Cost-efficiency: Minimize time and resources spent on model development.  
- Scalability: The chosen approach must support growing demands and evolving use cases.  
- Flexibility: Ability to fine-tune or customize for domain-specific requirements.  

## Considered Options  

### 1. In-house Large Language Model (LLM)  
- **Advantages:** Complete control over the model’s architecture and data, no dependency on external providers.  
- **Disadvantages:** High development costs, time-intensive, requires extensive computational resources and expertise.

### 2. Pre-trained Models (e.g., Anthropic’s Claude, Google’s Gemini) (Selected Option)  
- **Advantages:** Access to state-of-the-art NLU capabilities, reduced development time, and fine-tuning options for domain-specific needs.  
- **Disadvantages:** Dependence on external providers, token costs, and limited control over underlying architecture.

### 3. Open-Source Pre-trained Models (e.g., Cohere, Hugging Face Transformers)  
- **Advantages:** Comparable performance and open-source options may reduce costs.  
- **Disadvantages:** May lack seamless integration features or preferred licensing terms.

## Decision  
Pre-trained models, such as Anthropic’s Claude Sonnet 3.5 and Google’s Gemini, will be used for NLU. These models will be used as-is with no fine-tuning, as the goal is to leverage the latest advancements in NLU without the need to develop custom models. Fine-tuning will be reserved for future work to increase domain-specific accuracy and relevance.

Furthermore, the choice of pre-trained models will be made based on the required capabilities and the cost-benefit analysis. For example, if the goal of a prompt is to perform a tool call using a specific tool, the model should be capable of reliably reasoning about the tool to call and then calling the tool such as Claude’s Sonnet 3.5. For simpler tasks, a cheaper, speedier model such as Google’s Gemini Flash will be sufficient.

In this implementation, we will be using Anthropic’s Claude Sonnet 3.5 as the core LLM driving agentic behaviour due to superior reasoning and tool-calling performance. Gemini 1.5 Flash will be used for routers and simple tasksdue to it's speed and low cost.

### Reasons  
- Proven performance with state-of-the-art benchmarks.  
- Significantly reduced development time compared to building in-house models.  
- Flexibility to fine-tune for specific business requirements.  
- Cost-effective when compared to the computational and human resource needs of custom model development.  

## Consequences  

### Positive Impacts  
- Faster deployment of NLU capabilities.  
- Access to advanced, continuously improving model architectures.  
- Lower development costs compared to building in-house solutions.  
- Easier scalability with managed service offerings from providers like Anthropic or Google.

### Trade-offs and Limitations  
- Dependence on external providers for updates and maintenance.  
- Licensing and usage costs associated with pre-trained models.  
- Limited control over the underlying architecture and core model functionality.  
