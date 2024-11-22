price_pipeline = [
  {
    "$group": {
      "_id": "$Category",
      "maxPrice": { "$max": "$Price" },
      "minPrice": { "$min": "$Price" },
      "avgPrice": { "$avg": "$Price" },
      "priceArray": { "$push": "$Price" },
      "stdDevPrice": { "$stdDevPop": "$Price" }
    }
  },
  {
    "$project": {
      "_id": 1,
      "maxPrice": 1,
      "minPrice": 1,
      "avgPrice": 1,
      "stdDevPrice": 1,
      "rangePrice": { "$subtract": ["$maxPrice", "$minPrice"] },
      "numPrices": { "$size": "$priceArray" },
      "priceArray": 1
    }
  },
  {
    "$set": {
      "medianPrice": {
        "$let": {
          "vars": { "sortedPrices": { "$sortArray": { "input": "$priceArray", "sortBy": 1 } } },
          "in": {
            "$cond": {
              "if": { "$eq": [{ "$mod": [{ "$size": "$$sortedPrices" }, 2] }, 0] },
              "then": {
                "$avg": [
                  { "$arrayElemAt": ["$$sortedPrices", { "$divide": [{ "$size": "$$sortedPrices" }, 2] }] },
                  { "$arrayElemAt": ["$$sortedPrices", { "$subtract": [{ "$divide": [{ "$size": "$$sortedPrices" }, 2] }, 1] }] }
                ]
              },
              "else": {
                "$arrayElemAt": ["$$sortedPrices", { "$floor": { "$divide": [{ "$size": "$$sortedPrices" }, 2] } }]
              }
            }
          }
        }
      }
    }
  },
  {
    "$unset": "priceArray"
  }
]

rating_pipeline = [
    {
        "$group": {
            "_id": "$Category",
            "maxRating": {"$max": "$Rating"},
            "minRating": {"$min": "$Rating"},
            "averageRating": {"$avg": "$Rating"},
            "countRating": {"$sum": 1},
            "ratings": {"$push": "$Rating"}
        }
    },
    {
        "$project": {
            "maxRating": 1,
            "minRating": 1,
            "averageRating": 1,
            "countRating": 1,
            "ratings": 1,
            "rangeRating": {"$subtract": ["$maxRating", "$minRating"]},
            "stdDevRating": {"$stdDevPop": "$ratings"},
            "sortedRatings": {"$sortArray": {"input": "$ratings", "sortBy": 1}}
        }
    },
    {
        "$project": {
            "maxRating": {"$round": ["$maxRating", 2]},
            "minRating": {"$round": ["$minRating", 2]},
            "averageRating": {"$round": ["$averageRating", 2]},
            "countRating": 1,
            "rangeRating": {"$round": ["$rangeRating", 2]},
            "stdDevRating": {"$round": ["$stdDevRating", 2]},
            "medianRating": {
                "$cond": {
                    "if": {"$eq": [{"$mod": ["$countRating", 2]}, 0]},
                    "then": {
                        "$round": [
                            {
                                "$avg": [
                                    {"$arrayElemAt": ["$sortedRatings", {"$divide": ["$countRating", 2]}]},
                                    {"$arrayElemAt": ["$sortedRatings", {"$subtract": [{"$divide": ["$countRating", 2]}, 1]}]}
                                ]
                            },
                            2
                        ]
                    },
                    "else": {
                        "$round": [
                            {"$arrayElemAt": ["$sortedRatings", {"$trunc": {"$divide": ["$countRating", 2]}}]},
                            2
                        ]
                    }
                }
            }
        }
    }
]

stock_pipeline = [
    {
        "$group": {
            "_id": "$Category",
            "maxStock": {"$max": "$StockQuantity"},
            "minStock": {"$min": "$StockQuantity"},
            "avgStock": {"$avg": "$StockQuantity"},
            "stockArray": {"$push": "$StockQuantity"},
            "stdDevStock": {"$stdDevPop": "$StockQuantity"}
        }
    },
    {
        "$project": {
            "_id": 1,
            "maxStock": 1,
            "minStock": 1,
            "avgStock": 1,
            "stdDevStock": 1,
            "rangeStock": {"$subtract": ["$maxStock", "$minStock"]},
            "numProducts": {"$size": "$stockArray"},
            "stockArray": 1
        }
    },
    {
        "$set": {
            "medianStock": {
                "$let": {
                    "vars": {"sortedStocks": {"$sortArray": {"input": "$stockArray", "sortBy": 1}}},
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$mod": [{"$size": "$$sortedStocks"}, 2]}, 0]},
                            "then": {
                                "$avg": [
                                    {"$arrayElemAt": ["$$sortedStocks", {"$divide": [{"$size": "$$sortedStocks"}, 2]}]},
                                    {"$arrayElemAt": ["$$sortedStocks", {"$subtract": [{"$divide": [{"$size": "$$sortedStocks"}, 2]}, 1]}]}
                                ]
                            },
                            "else": {
                                "$arrayElemAt": ["$$sortedStocks", {"$floor": {"$divide": [{"$size": "$$sortedStocks"}, 2]}}]
                            }
                        }
                    }
                }
            }
        }
    },
    {
        "$project": {
            "_id": 1,
            "maxStock": {"$round": ["$maxStock", 2]},
            "minStock": {"$round": ["$minStock", 2]},
            "avgStock": {"$round": ["$avgStock", 2]},
            "stdDevStock": {"$round": ["$stdDevStock", 2]},
            "rangeStock": {"$round": ["$rangeStock", 2]},
            "medianStock": {"$round": ["$medianStock", 2]},
            "numProducts": 1
        }
    },
    {
        "$unset": "stockArray"
    }
]