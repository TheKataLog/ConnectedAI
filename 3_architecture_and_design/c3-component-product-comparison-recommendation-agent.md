
# C3 - Component Diagram - Product Comparison & Recommendation Agent

![C3 - Component Diagram - Product Comparison Recommendation Agent ](../images/architecture/c3-component-product-comparison-recommendation-agent.png)

This diagram illustrates the architecture for product comparison and recommendation:

1. The **Product Supervisor** routes relevant queries to the **Product Comparison & Recommendation Agent**.
2. The agent:
   - Uses the **Product Comparison Tool** to generate side-by-side comparisons.
      - This tool searches based on provided product name, falling back on product description if needed.
   - Uses the **Product Recommendation Tool** to generate recommendations from a given product.
      - These recommendations are those in the same category, with similar prices and high ratings.
   - Uses the **Product Details Tool** to fetch product information based on a product description if needed.
3. Data is sourced from the **Product Database**.

