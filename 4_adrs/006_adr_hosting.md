# ADR006 - Host Backend Services on GCP and Frontend on Firebase Deploy

## Status  
Accepted  

## Context and Problem Statement  
Hosting the AI assistant requires robust and scalable platforms for both backend and frontend components. The challenge is to select hosting solutions that align with the system’s scalability, simplicity, and integration needs while minimizing complexity and maintenance overhead.  

### Requirements  
- Backend hosting should support scalable and efficient APIs, align with existing tools, and integrate seamlessly with the development pipeline.  
- Frontend hosting must handle static content efficiently, provide real-time update capabilities, and minimize deployment complexity.  
- The hosting solutions should balance cost, scalability, and ease of maintenance.  

### Business or Technical Assumptions  
- The backend requires high scalability and seamless integration with other cloud-based tools used by the team.  
- The frontend is relatively static and does not require dynamic backend-like hosting capabilities.  
- The existing infrastructure favors GCP, making it a natural choice for backend hosting.  

## Decision Drivers  
- Integration: Compatibility with existing tools and workflows.  
- Scalability: Both backend and frontend solutions must handle future growth.  
- Simplicity: Reduce deployment and maintenance complexity.  
- Cost: Hosting solutions should provide value without unnecessary overhead.  

## Considered Options  

### Backend Hosting  

1. **AWS**  
   - **Advantages:** Comparable capabilities to GCP, widely used in the industry.  
   - **Disadvantages:** Less alignment with the existing infrastructure and team expertise.

2. **Azure**  
   - **Advantages:** Scalable and integrates well with Microsoft tools.  
   - **Disadvantages:** Less synergy with the current workflow tools used by ShopWise.

3. **GCP (Selected Option)**  
   - **Advantages:** Aligns with existing tools and infrastructure, supports seamless scalability, and integrates efficiently with the development pipeline.  
   - **Disadvantages:** Requires team expertise in GCP to maximize benefits.

### Frontend Hosting  

1. **Firebase Deploy (Selected Option)**  
   - **Advantages:** Developer-friendly, ideal for hosting static content with real-time updates, and easy to set up and maintain.  
   - **Disadvantages:** Limited to static or semi-dynamic content, not suitable for highly dynamic applications.

2. **Cloud Run**  
   - **Advantages:** Provides dynamic scaling for applications.  
   - **Disadvantages:** Overkill for the relatively static nature of the frontend.

3. **Heroku**  
   - **Advantages:** Easy to deploy and scalable.  
   - **Disadvantages:** Primarily designed for dynamic applications, making it less suitable for static frontend hosting.

4. **Self-hosted Solutions**  
   - **Advantages:** Full control over hosting environment.  
   - **Disadvantages:** Increases complexity and maintenance overhead.

## Decision  
The backend will be hosted on GCP for its scalability, alignment with the existing infrastructure, and seamless integration with current workflows. The frontend will be hosted on Firebase Deploy for its simplicity, developer-friendly setup, and suitability for static content hosting.  

### Reasons  
- GCP provides strong support for scalable APIs and aligns with the team’s existing tools and expertise.  
- Firebase Deploy simplifies frontend deployment, offering real-time updates and efficient static content hosting.  
- This combination ensures minimal complexity while maintaining scalability and performance.  

## Consequences  

### Positive Impacts  
- Backend and frontend hosting solutions are scalable and efficient, supporting future growth.  
- Seamless integration with existing tools and workflows reduces development and deployment friction.  
- Simplified deployment for the frontend with Firebase Deploy ensures rapid updates and maintenance.  

### Trade-offs and Limitations  
- Separate platforms for backend (GCP) and frontend (Firebase) require distinct monitoring and cost management processes.  
- Firebase Deploy’s capabilities are limited to static or semi-dynamic frontend needs, requiring alternative solutions for more dynamic applications in the future.  
