# Model
This project looks at the basis in European wheat markets, first from a view of how closely different basis moves with its neighbours (and as we will discuss, in effect how local price movements spreads co move), and then by looking at how the long run basis behave against the MATIF and what short-run deviation from the long run looks like for different countries. This will be done by using two different frameworks: A spatial co movement model for European wheat, focusing on basis co movements and market integration. It uses a spatial weight matrix to study spatial basis and how the basis co moves between European countries for wheat of bread making quality, using data from the European commission for price and trade flows, as well as MATIF prices. 
And:
A model focusing on how fast different European countries markets adjust to MATIF prices and their long-run relationship to MATIF (how the long-run basis behaves, and how short-run deviations are handeled). This to be able to show how the basis behave in a temporal setting. To see if for example how big the basis is for different countries in a long-run persepctive, but also to understand how deviation from the stable basis point is corrected, and to compute hedge ratios. 

## Background and Mission
This analysis is built upon my previous spatial disequilibrium analysis. Where I examin how the error term of a spatial lag model differ between countries, and compare it to the mean error term of all countries in a fashion to create a Spatial Disequilibrium Index (SDI). Since mean reversion was present in this SDI, I also tested whether the variable had predicitive power which turned out to be the case. 
Upon further investigation, I found that my analysis was lacking in terms of both method and data on certain areas. This is why I developed this newer project. Upon revision, I also thought that this analysis would be much more useful in discussing though the lence of basis. Since many wheat market actors around Europe has to hedge their wheat against the MATIF, but because of transportation cost and storage economics they therefore often has to deal with basis risks. 

To do this, I establish two seperate analysis stated above. These analysis could help farmers, and farmers associated cooperations in dealing with basis risk and hedging, but also possibly make the process of out of market of-loading easier. To get a better understanding of how the basis should look like in the country where the actors are currently at, and how fast any deviation from that long run basis is expected to be corrected, getting a fuller sense of the basis risk involved in a hedge against MATIF, which can aid in storage decisions. But it could also help in more effectivly search for out of market buyers and sellers, depending on the current price situations, since as we will discover, the local price and its relation to MATIF does appear to differ for different countries and under different temporal settings.
I will construct the full analysis by first looking at the spatial model for basis, then the temporal model, and lastly discuss the findings.


## Spatial Co movement analysis

#### Theory 
So, looking at the relationship between basis in differnet countries who share the same hedged market (MATIF) is essentially just looking at local price movements. Since the basis difference between country A and country B is the price difference between the two, if we formulate basis as below:

$$
Basis_i = Local Price_i - MATIF_{price}
$$

So the difference in basis between 2 countries should therefore just become this:


$$
Basis_A - Basis_B = Local Price_A - MATIF_{price} - (Local Price_B - MATIF_{price}) = Local Price_A - Local Price_B
$$

Therefore the theory of spatial price equilibrium between markets and the law of one price is what will drive this basis difference. Where prices for the same commodity in theory should converge to the point where the difference is equal to the cost of transportation. This is quite simply illustrated with a world where we only have two countries. Where if equilibrium price in country A is below the equilibrium price of country B to a factor higher than the transportation cost, then trade should be conducted until prices converge such that the price in country A should be exactly the price in country B - the transportation cost and a spatial equilibrium between the markets emerge. 

Of course in a real world scenario you have webs of countries with different supply and demand curves operating simultaniously creating different prices as well as different rates of change in price, all with different transportation costs between them. To complicate matters even further, these countries can act as hubs for other countries creating a entire network between markets. Lastly, we also have temporal issues to deal with, such as storage economics. Where market participants can speculate and store goods, in order to sell them at a more advantagous times. This all creates a beutiful cluster of different components making up the price of wheat which we have today, and which market operators have to navigate. 



#### Data
To do this analysis I will take advantage of data from EUROSTAT for country specific wheat prices going back until January of 2005 and is expressed in month and with the currency Euro, as well as trade flows of wheat between European countries going back the same lenght. 
In order to not confuse global macro price events with regional deviations in wheat prices, I will extract the MATIF price s from the local farm-gate prices, and simultaniusly define the Basis. Which also can be seen as the local part of the countries price movements (global price is defactored).

To then establish the relationship between countries, I construct a gravity fitted spatial weight matrix. Where I regress the trade flow on geographical distance between countries or weather they share a river in order to circumvent endogenity problems. The results shows that these factors explain trade flow very well, and that the model and its results are robust to weather one uses exports or imports to denote trade flow.

#### Method:
I use a spatial lag panel data regression to then build my model, this because it appears that the basis for all countries are I(0) for everyone, since the local price and MATIF in general does share a common stationary trend/relationship. The idea then is too look at how the basis in a specific country behaves in relation to the spatial weighted basis of all other countries. But I also include a fixed effect for each country, and for the time period when the war in Ukraine started. The equation then will look like this:

$$
y_{i,t} = \beta_0 + \beta_1 Wy_{i,t} + 0\theta fixed effects_i + \theta War in Ukraine_t + \mu_{i,t}
$$

Where y is the basis, and W is the gravity fitted spatial weight matrix, the war in ukraine dummy shows when the war in ukraine started, and the fixed effects are countries specific fixed effects. 
#### Results

Okay, so first and formost, the $$\beta_1$$ is at 0.945 which makes intuitive sense. It basically states that if the spatially weighted basis move by 1 euro, the basis in the current country simultaniusly move by 0.94 euro. The coefficient is also highly significant, and the 95% confidence level is from 0.8, to 1.08. So the co movement between neighbours is strong.
I also estimated the $$\beta_1$$ coefficients for each country seperatly, and this can be show in the map below.

The resulting indicator for co movement with neighbours for different countries in the dataset can be found in a map below:
<img src="src/output/alpha_map.png" alt="Spatial co-movement coefficients" width="800">

As can be seen, many countries close to where the MATIF market is located are not co moving as much with its neighbours in terms of basis (or neighbouring local price rather) such as Spain, Germany, and France. But countries further from MATIF show substantially stronger co-movement with their spatially connected markets


## MATIF basis analysis model (Temporal model)

#### Theory
The second model takes a temporal perspective and uses MATIF as the common reference market. The basis reflects the difference between the local physical wheat price and the MATIF futures price. In a frictionless market, this difference should be related to the costs of transporting and handling wheat between the local market and the MATIF reference market. In practice, storage costs, expectations, market frictions, contract structures and differences in local supply and demand can cause the basis to deviate from this relationship. 

#### Data
Here again, we use the same price data as in analysis one, but we do not have a need to construct a spatial weight matrix, so flow data etc is not included. 

#### Method
An error correction model is used here, since neither the local price, or the MATIF price in and of itself is stationary at I(0), but since we know that the basis is stationary, we have strong reason to belive that the variables are cointegrated, which after a test is confirmed. Therefore, I employ a Error correction model, in order to first capture the long-run relationship between local prices and then MATIF prices (often refered to in financial terms to the hedge ratio), and then use the finding to estimate how short-run deviation from the long-run relationship is corrected. 

Long-run model:

$$
y_{i,t} = \beta_0 + \beta_1 X_{i,t} + 0\theta fixed effects_i + \mu_{i,t}
$$

Short-run model:

$$
dy_{i,t} = \beta_0 + \beta_1 \mu_{i,t-1} + \beta_2 dX_{i,t-1} + \beta_3 dX_{i,t-2} +\theta Fixed effects_i + \theta War in Ukraine_t + \epsilon_{i,t}
$$

Here, y is the local farmgate price, X is the MATIF price, and d stands for the first differene.  $$\mu_{i,t}$$ represents the residual from the long-run relationship. Its lagged value is the error-correction term, capturing how far the local price was from its estimated long-run relationship with MATIF in the previous period. The coefficient on this term measures the speed at which that deviation is corrected.”

#### Results
Okay, so for the long-run model the results are quite straight forward, the $$\beta_1$$ coefficent corresponds to 0.89, meaning that if there is a 1 Euro increase in MATIF a month, there is also a 0.89 increase in farmgate prices on average between countries. But this is in no way weighted on quantity etc, so it is therefore more useful to explain this basis as within country mean basis, which is done in the map below:

<img src="src/output/alpha_map_MATIF_long_run.png" alt="Long-run Basis" width="800">

What we can see here is that France has a virtuly a 0% long-run basis to MATIF, which is expected since MATIF is located in France, but neighbouring country Germany has also a very low  long-run basis. On the other hand, Romania and Bulgaria has quite a great basis against MATIF. For Romania it is around 34%, and for Bulgaria lies around 30%. 

For the short-run model, it is useful to first explain what the coefficients of interest tell us, before interpreting them.
So the coefficient of interest here is the $$\beta_1$$. It shows the speed of adjustment, meaning the speed it takes for the model to correct the deivation from the long-run relationship. The average speed of adjustment here is around -0.29, meaning that 29% of a disqeuilibrium created in the previous period is corrected this period. But this speed of adjustment appears to differ quite alot between countries, when estimated seperatly for each country, the map below emerges.

<img src="src/output/alpha_map_MATIF.png" alt="Short-run Basis" width="800">

Here again, we can see that France speed of adjustment is almost at -1, corrects last months equilibriums at full in the current month, where the speed of adjustment is virtually 0. Again, it is also quite high for Germany, thirdly in speed of adjustment lies Sweden. Meaning that these countries corrects deviation from their long-run basis quite fast. At the bottom end we then see Bulgaria and Romania again, correcting only 15% of any deviation from their long-run basis in the first month on average.

## Discussion
Okay, first and foremost, looking at the secound model, we can see that a lower basis in a country is almost always associated with a high speed of adjustment. This lower basis also seems to be spatially tied to closeness to the MATIF market, where countries close to it experience a lower basis, and higher speed of adjustment if any deviation in basis where to arise. This is in accordance with the law of one price, since the markets (the local market and MATIF) should only be able to differ by a smaller amount if the transportation cost between them is low, therefore resulting in a much lower basis. A lower transport cost is also associated with lower transport times, also meaning that any deviations would be corrected much faster, and any spatial arbitrage quickly absorbed. 

Looking at the first model, we see a very fascinating result. An almost reverse relationship to the secound model appears in co movements (we cannot establish any directional movement here however), where countries close to MATIF are in relative terms not co moving with neighbours basis, while countries quite far away from MATIF co moves alot with neighbours. This should in theory not be the case, but it may be such that countries very close to MATIF use it more frequently, which means that there are more structural habits and system tieing their local markets to MATIF more strongly, than to other market directly in the area. 

What appears to emerge here is 2 different profiles of countries, either countries are tied to MATIF (especially if MATIF is relatively close), or the countries are tied to their neigbours in terms of basis through local price movement.

This could be information quite useful to participants on these markets. Since if you are a farmer who hedges on MATIF in longer periods, but operated in Sweden for example and you have graine stored. If your basis starts to increase, the estimated adjustment behaviour suggests that deviations tend to be corrected relatively quickly. Wheras if you are in Bulgaria for example, that may not be the case.
On the other hand, if you are in in Sweden and you see signs that neighbouring countries basis are shifting quite dramatically, you know that your countries basis will not co move quite as much, but if you are in Bulgaria and your neighbours basis starts too shift, yours will most likely also co move. 

## Conclusion
Different European markets and their corresponding basis seems to fall under different categories, where they either are tied very closely to MATIF, or to their neighbouring markets. There seem to be a tradeoff here which may be structural, there are systems in places and long standing contracts which makes basis move differently in different places depending on if you are more close geographially to MATIF or not, which partially ties back to the law of one price. The spatial pattern is also consistent with the gravity-based structure used to construct the spatial weight. Where many countries gravitate towards a shared centroid which is MATIF in terms of basis movement through MATIF price. But when the gravity pulling force of  MATIF start to become weak, countries start to gravitated more towards their neighbours instead, creating the geographiall patterns we see.
All in all however it seems that most countries are on average quite tied both to eachother and to an extend MATIF, even though differences are shown.
