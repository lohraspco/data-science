# Applications of Data Science in Marketing
1. Customer Segmentation: Identify distinct groups of customers based on demographics, purchase behavior, or engagement
2. Market Segmentation:Cluster different regions or markets based on sales, preferences, or other metrics 
3. marketing mix modeling (MMM) and multi-touch attribution (MTA) : MTA focuses on individual customer journeys and attributing credit to specific touchpoints, while MMM analyzes the overall impact of marketing activities on business outcomes using aggregated data
4. Customer Lifetime Value
5. Causal Inference (Treatment Effects): Goal is to estimate the causal effect of a treatment or intervention. For example, What's the impact of a marketing campaign on customer spending? Techniques are:

    - Propensity Score Matching (PSM)
    - instrumental Variables (IV)
    - Difference-in-Differences (DiD)
    - Regression Discontinuity (RD)

 6. Survival Analysis:  Time until an event occurs (e.g., churn, death, product failure) which are modeled using Kaplan-Meier, Cox Proportional Hazards, Weibull. Key concepts are:
    - Censoring: You don’t observe the event for all units.
    - Hazard Rate: Instantaneous event probability.

7. Choice Modeling: Example: Predict which car model a customer will buy based on features and price
8. Selection Models: Purpose is to correct for sample selection bias.
    - Model: Heckman Selection Model
    - Use case: When the sample you observe isn’t random (e.g., only people who bought the product are surveyed).
    - Corrects: Bias introduced when the decision to appear in the sample is correlated with the outcome.



- Time Series: Data indexed over time (e.g., sales over months).
    - Techniques: ARIMA, Exponential Smoothing, VAR.

- Panel Data: Combines cross-sectional and time series data (e.g., sales per customer over time).
    - Techniques: Fixed/Random Effects, Difference-in-Differences.

- Regression Variants 
    - Censored Regression: Observations are partially observed (e.g., income above a threshold).
    - Model: Tobit

- Truncated Regression: Entire rows of data are missing beyond a threshold (e.g., survey only includes people earning <$100k).