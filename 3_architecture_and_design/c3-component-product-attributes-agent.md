
# C3 - Component Diagram - Product Attributes Agent

![C3 - Component Diagram - Product Attributes Agent](../images/architecture/c3-component-product-attributes-agent.png)

This diagram outlines the Product Attributes Agent:

1. **Product Supervisor** routes product-specific requests.
2. The agent communicates with:
   - **Product Details Tool** for product specifications.
      - Uses semantic search to find the most relevant product based on the product description.
   - **Product Lookup Tool** to fetch product information based on Product ID.
      - Returns the product details from the **Product Database**.
3. All data is retrieved from the **Product Database** to ensure real-time updates.

The **Product Details Tool** retrieves product information from the **Product Database** in a number of stages. 

1. First, it fetches the product details from the **Product Database** chunks of the preprocessed product descriptions using hybrid search (vector search and keyword search).
   - Optional price and rating limits can be applied to the search results.
2. Then, it finds the parent product ID for the product, and fetches the product details from the **Product Database**.
3. Aspect relevance is determined for each product, using an LLM to validate the relevancy to the query for each item in parallel.
4. The results are sorted based on a desired criteria (e.g. relevance to the query, rating, price, etc.) and returned to the **Product Attributes Agent**.