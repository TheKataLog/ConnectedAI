# ADR007 - Use LangFuse for Evaluation and MLOps Platform

## Status  
Accepted  

## Context and Problem Statement  
The AI assistant requires a platform for offline evaluation to ensure that the model operates as expected and to identify areas for improvement without requiring a full deployment. Additionally, tracing capabilities are needed to support debugging and monitoring during development and production.  

### Requirements  
- Enable offline evaluation to validate model performance and identify improvement areas.  
- Provide robust tracing for debugging and monitoring.  
- Align with existing infrastructure for cost-effectiveness and security.  
- Allow self-hosted deployment to maintain control over sensitive data.  

### Business and Technical Assumptions  
- Offline evaluation is essential for iterative improvement without requiring deployment.  
- Tracing capabilities must integrate seamlessly with existing workflows.  
- A self-deployable solution is preferred to ensure data security and minimize operational costs.  

## Decision Drivers  
- Evaluation capabilities: The platform must support offline model validation and analysis.  
- Tracing and monitoring: Essential for identifying issues and improving performance.  
- Cost-effectiveness: Minimize operational expenses while maximizing functionality.  
- Integration: Compatibility with existing infrastructure and workflows.  

## Considered Options  

### 1. LangFuse (Selected Option)  
- **Advantages:** Self-deployable, cost-effective, secure, and supports robust evaluation and tracing.  
- **Disadvantages:** Requires additional effort to deploy and maintain a local instance.

### 2. Phoenix Arize  
- **Advantages:** Can be self-hosted and integrated with existing infrastructure.  
- **Disadvantages:** Less well-documented and supported compared to other options, increasing the potential for implementation challenges.

### 3. LangSmith  
- **Advantages:** Highly documented, well-supported, and easy to integrate with existing infrastructure.  
- **Disadvantages:** Limited free tier and higher costs for advanced features compared to other options.

## Decision  
LangFuse was selected as the evaluation and MLOps platform due to its balance of cost-effectiveness, self-deployability, and robust support for evaluation and tracing.  

### Reasons  
- LangFuse offers a secure, self-deployable solution that aligns with the need for low-cost offline evaluation and tracing.  
- Its capabilities meet the requirements for debugging, monitoring, and iterative model improvement.  
- The ability to integrate with existing infrastructure reduces operational overhead and ensures seamless adoption.  

## Consequences  

### Positive Impacts  
- Enables offline model evaluation, supporting iterative development and improvement.  
- Provides robust tracing for debugging and monitoring, enhancing system reliability.  
- Self-deployable, maintaining control over sensitive data and reducing operational costs.  

### Trade-offs and Limitations  
- Requires additional development effort to deploy and maintain a local instance.  
- LangFuse may have less documentation and community support compared to some alternatives, potentially slowing troubleshooting for complex use cases.  
