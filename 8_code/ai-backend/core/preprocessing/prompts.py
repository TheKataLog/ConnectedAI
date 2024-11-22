DESCRIPTION_ENRICHMENT_PROMPT = """ -- Instructions --
You are a retail product expert.
Transform the following product description into a fully formed description. 
Each sentence of the description should be fully factual, unambiguous, and include necessary details so that each sentence can be understood in isolation, without context. 
For example, if the description mentions features or claims, specify each feature or claim with enough detail to make sense alone.
Each sentence should contain the name of the product and the product category.
Do NOT make up any information that cannot be directly inferred from the description.

--Example--
{{
"Product Name": "Panasonic TX 65FZ952B",
"Product Category": "TVs",
"Product Description": "This is a high-definition LED TV with 4K resolution and smart features, ideal for streaming movies and gaming."
}}
Fully formed description: 
"The Panasonic TX 65FZ952B TV is a high-definition LED TV with 4K resolution, offering ultra-high definition for a detailed viewing experience. The Panasonic TX 65FZ952B TV includes smart features, enabling users to connect to the internet and access various streaming platforms. The Panasonic TX 65FZ952B TV is designed for streaming movies, providing high-quality visuals and smooth playback. The Panasonic TX 65FZ952B TV is well-suited for gaming, with its 4K resolution and LED display."

--Example--
{{
"Product Name": "CDA WC600",
"Product Category": "Dishwashers",
"Product Description": "The CDA WC600 is a fully-integrated, 15-place setting dishwasher rated AAA, providing efficient cleaning and convenience."
}}
Fully formed description: 
"The CDA WC600 is a fully-integrated dishwasher, meaning it is designed to be installed seamlessly behind a kitchen cabinet door for a streamlined appearance. The CDA WC600 dishwasher offers 15 place settings, providing ample capacity for large households or gatherings. The CDA WC600 dishwasher is rated AAA, indicating excellent performance in energy efficiency, washing, and drying. The CDA WC600 dishwasher, provides efficient and convenient cleaning of dishes and cutlery, removing food residue and leaving them sparkling clean."

--Example--
{{
"Product Name": "Fisher & Paykel RF610ADX4 Stainless Steel",
"Product Category": "Fridge Freezers",
"Product Description": "This French-style refrigerator freezer features a stainless steel finish and no ice dispenser, providing ample storage space for food and beverages in a sleek and modern design."
}}
Fully formed description: 
"The Fisher & Paykel RF610ADX4 Stainless Steel Fridge Freezer features a stainless steel finish, giving it a sleek and modern appearance. The Fisher & Paykel RF610ADX4 Stainless Steel Fridge Freezer is a French-style refrigerator freezer, which typically features side-by-side refrigerator doors and a bottom freezer drawer. The Fisher & Paykel RF610ADX4 Stainless Steel Fridge Freezer does not have an ice dispenser, maximizing the interior storage space. The Fisher & Paykel RF610ADX4 Stainless Steel Fridge Freezer provides ample storage space for food and beverages, accommodating the needs of households of various sizes."

--Example--
{{
"Product Name": "Easypix Aquapix W1024 Splash",
"Product Category": "Digital Cameras",
"Product Description": "A compact, 10.0 MPix digital underwater camera with a splash-resistant design, capable of interpolated 16.0x mixing and taking photos up to 3m depth, featuring a pink casing (Part number: 10013)."
}}
Fully formed description: 
"The Easypix Aquapix W1024 Splash Digital Camera is a compact digital camera, making it easy to carry and handle. The Easypix Aquapix W1024 Splash Digital Camera has 10.0 megapixels, capturing high-resolution images. The Easypix Aquapix W1024 Splash Digital Camera is an underwater camera designed for taking pictures and videos beneath the surface of the water. The Easypix Aquapix W1024 Splash Digital Camera has a splash-resistant design, protecting it from accidental water splashes. The Easypix Aquapix W1024 Splash Digital Camera is capable of interpolated 16.0x mixing, enhancing the zoom capabilities. The Easypix Aquapix W1024 Splash Digital Camera can take photos up to 3m depth, making it suitable for snorkeling and shallow diving. The Easypix Aquapix W1024 Splash Digital Camera features a pink casing, giving it a distinctive appearance. The Easypix Aquapix W1024 Splash Digital Camera has the part number 10013, which can be used for identification and ordering."

--Product Description to Transform--
{{
"Product Name": "{product_name}",
"Product Category": "{product_category}",
"Product Description": "{product_description}"
}}
"""


PRODUCT_NAME_ENRICHMENT_PROMPT = """ -- Instructions --
You are a retail product expert.
Transform the following product name into a corrected product name. 
The product name should have the brand, make, model, category, and any other relevant details.

--Example--
{{
"Current Product Name(s)": ["panasonic tx65fz952b/tx65fz952b", "panasonic tx 65fz952b 65 smart 4k ultra hd hdr oled tv"],
"Product Category": "TVs",
"Product Description(s)": ["This is a high-definition LED TV with 4K resolution and smart features, ideal for streaming movies and gaming.", "This Panasonic TX 65FZ952B is a 65 Smart 4K Ultra HD HDR OLED TV offering enhanced picture quality and smart connectivity features."]
}}
Corrected Product Name: 
"Panasonic TX-65FZ952B 65 inch Smart 4K Ultra HD HDR OLED TV"

--Product Description to Transform--
{{
"Current Product Name(s)": {product_names},
"Product Category": "{product_category}",
"Product Description(s)": {product_descriptions}
}}
"""