import pandas as pd
from core.test_generation.order_test_generation import order_test_set_generation
from core.test_generation.customer_test_generation import customer_test_set_generation
from core.env import PROJECT_ID, LOCATION

if __name__ == "__main__":

    base_path='data'

    # Prepare the order data
    order_data_df = pd.read_csv(f"{base_path}/synthetic-orders-data.csv")
    order_data_df.columns = [i.strip() for i in order_data_df.columns]
    # Prepare the product data
    product_data_df = pd.read_csv(f"{base_path}/synthetic-product-data.csv")
    product_data_df.columns = [i.strip() for i in product_data_df.columns]

    # Generate the test set for the order data
    ## 6. Order Status Check
    df_result = order_test_set_generation("""Can you tell me the status of my order with Order ID XXX?""", 10, PROJECT_ID, LOCATION, order_data_df)
    df_result.insert(0, "set", "OrderStatusCheck")
    df_result.to_excel(f"{base_path}/test_sets/order-status-check-test-set.xlsx", index=False)

    ## 7. Tracking and Shipping Information
    df_result = order_test_set_generation("""When is my order with Order ID XXX expected to be delivered?""", 10, PROJECT_ID, LOCATION, order_data_df)
    df_result.insert(0, "set", "TrackingAndShippingInformation")
    df_result.to_excel(f"{base_path}/test_sets/tracking-and-shipping-information-test-set.xlsx", index=False)

    ## 8. Return Eligibility
    df_result = order_test_set_generation("""Is my order with Order ID XXX eligible for return?""", 10, PROJECT_ID, LOCATION, order_data_df)
    df_result.insert(0, "set", "ReturnEligibility")
    df_result.to_excel(f"{base_path}/test_sets/return-eligibility-test-set.xlsx", index=False)

    ## 9. Order History
    df_result = customer_test_set_generation("""Can you list my previous orders? My customer id is XXX.""", 10, PROJECT_ID, LOCATION, order_data_df)
    df_result.insert(0, "set", "OrderHistory")
    df_result.to_excel(f"{base_path}/test_sets/order-history-test-set.xlsx", index=False)

    ## 10. Shipping Delay Enquiry
    df_result = order_test_set_generation("""My order with Order ID XXX seems delayed. Can you provide an update on when it might ship?""", 10, PROJECT_ID, LOCATION, order_data_df)
    df_result.insert(0, "set", "ShippingDelayEstimate")
    df_result.to_excel(f"{base_path}/test_sets/shipping-delay-estimate-test-set.xlsx", index=False)

    ## 11. Order Assistance for Multiple Items
    df_result = order_test_set_generation("""I ordered multiple items in Order ID XXX. Can you check if each item has shipped?""", 10, PROJECT_ID, LOCATION, order_data_df)
    df_result.insert(0, "set", "OrderAssistanceMultipleItems")
    df_result.to_excel(f"{base_path}/test_sets/order-assistance-multiple-items-test-set.xlsx", index=False)