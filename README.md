# Model
This project has two prongs of looking at local basis in European wheat market from a spatial and then a temporal view: A Wheat equilibrium model for European countries, focusing on local run price movements (basis) and market integration. It uses a Error correction model to study long-run spatial basis equilibrium between European countries for wheat of bread making quality wheat, using data from the European commission for price and trade flows, as well as MATIF prices. 
And:
A model focusing on how fast different European countries react to MATIF prices and their long run relationship to MATIF. This to be able to show how the basis behave in a temporal setting. To see if for example how big the basis is for different countries in a long run persepctive, but also to understand how deviation from the stable basis point is corrected. 

## Background and Mission
This analysis is built upon my previous spatial disequilibrium analysis. Where I examin how the error term of a spatial lag model differ between countries, and compare it to the mean error term of all countries in a fashion to create a Spatial Disequilibrium Index (SDI). Since mean reversion was present in this SDI, I also tested whether the variable had predicitive power which turned out to be the case. 
Upon further investigation, I found that my analysis was lacking in terms of both method and data on certain areas. This is why I developed this newer slightly more sofisticated model, with a new method and updated data. Upon revision, I also thought that this analysis would be much more useful in discussing though the lence of basis. Since many wheat market actors around Europe has to hedge their wheat against the MATIF, but because of transportation cost and storage economics they therefore often has to deal with basis risks. 

To do this, I establish two seperate analysis, one set out to answer how the basis between 19 European countries relates to eachother spatially, their long run equilibrium to eachother, and how fast deviations (or price disequilibriums) in that basis is corrected (This esentially is an analysis of how local price fluctioantions transmitt throughtout space, and at which rate. Since the MATIF price term of the basis is equal across countries). 


The other analysis is done to look at how the basis behave in different European countries. To establish the long run relationship in price between farmgate price and MATIF thoughtought the 10 European countries, and how fast any deviation from that long run relationship is corrected (short term dynamics). 

These analysis could help farmers, and farmers associated cooperations in dealing with basis risk and hedging, but also possibly make the process of out of market of-loading easier. To get a better understanding of how the long run basis should look like in the country where the actors are currently at, and how fast any deviation from that long run basis is expected to be corrected, getting a fuller sense of the basis risk involved in a hedge against MATIF. But these analysis could also help in determining the moment of unloading and if wheat should be stored or not. Say for example if a deviation in price has occured in Finland and wheat has just been harvested in Sweden. My spatial price model should help in determining how fast such a price deviation where to hit Sweden, and if for example one is selling to Swedish actors, the results could help indicate the movement in Swedish prices for next month. 

I will construct the full analysis by first looking at the spatial model, then the temporal model, and lastly comparing the two. 


## Spatial Price Disequilibrium analysis (Spatial model)

#### Theory 
So, looking at the relationship between basis in differnet countries is essentially just looking at price. Since the basis difference between country A and country B is the price difference between the two, if we formulate basis as below:

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
To do this analysis I will take advantage of data from EUROSTAT for country specific wheat prices going back until 2005, as well as trade flows of wheat between European countries going back the same lenght. 
In order to not confuse global macro price events with regional deviations in wheat prices, I will extract the MATIF price movements from the local farm-gate prices, and simultaniusly define the Basis. Which also can be seen as the local part of the countries price movements (global price is defactored).

To then establish the relationship between countries, I construct a gravity fitted spatial weight matrix. Where I regress the trade flow on geographical distance between countries, weather they share a river, or if they are costal in order to circumvent endogenity problems. 

#### Method:
I use a Error Correction Model (ECM) to then build my model, this because it appears that the basis for all countries are not I(0) for everyone, even it they are for quite a few, but both in theory (though the law of one price) and in practice, the basis are cointegrated geographically. The idea now is to first establish the long-run spatial equilibrum betwenn countries basis. When this is done, I will investigate how deviations from this equilibrium corrects itself over time.

##### Long-run relationship
To test this long-run equilibrium, I just run the panel data regression specified below:

$$
y_{i,t} = \beta_0 + \beta_1 Wy_{i,t} + 0\theta fixed effects_i + \mu_{i,t}
$$

Where y is the basis, and W is the gravity fitted spatial weight matrix. The long-run relationship can then be shown in $$\beta_1$$ and for my model corresponds to 0.43 and is significant at the 97% level.
The interpretation of this is that in general, when spatially weighted basis increases with 1 euro, the basi of the current market increases with 0.43 Euro.

##### Short-run deviations

I then save the $$\mu_{i,t} $$ from the previous model, which is the movement in basis in location i which deviates from the spatially weighted basis movements, which should correspond to a long-run spatial disequilibrium. 

I then take the change in each variable and run my next regression which looks like this:

$$
dy_{i,t} = \beta_0 + \beta_1 \mu_{i,t-1} + \beta_2 dWy_{i,t-1} + \beta_3 dy_{i,t-1} + \beta_4 dy_{i,t-2} +\theta Fixed effects_i + \theta War in Ukraine_t + \epsilon_{i,t}
$$

Here $$y_{i,t}$$ still stands for basis, $$Wy_{i,t-1}$$ stands for spatially weighted basis of neighbours, the d stands for the difference between t and t-1, and $$\epsilon_{i,t}$$ is the error term.

Interpretation of these coefficients are a bit tricky, so i will explain them here. 
The coefficient of $$\mu$$ shows the speed of adjustment from a disequilibrium, meaning how fast a deviation from the relationship between $$y_{i,t}$$ and $$Wy_{i,t}$$ is corrected.
The coefficent from $$dWy_{i,t-1}$$ shows short-run spatial transmission, how much a change in the spatially weighted basis effects the change in local basis. 
The coefficient for $$dy_{i,t-1}$$ and $$dy_{i,t-2}$$ shows the own price dynamic, how momentum transfer intertemporally in a country in terms of basis. 
We also include country specific fixed effects, and a dummy variable indicating the month the war in Ukraine started, since this spooked traders and it felt appropriate to isolate this effect. 

#### Results

Okay, so from my model the $$\beta_1$$ is around -0.26, meaning that when deviation from the equilibrium happens in a country, 26% of the previous-period disequilibrium is corrected per month, meaning that half the correction is apporximatly done within 2.3 months time. This coefficient is also significant and within a 95% confidence interval of -0.3421 to -0.1773.
For $$\beta_2$$ we have a positive coefficient of -0.1, meaning that a positive basis change in Europe can correspond to a negative basis change in the local country.
The coefficients $$\beta_3$$ is significant and around -0.14, while $$\beta_4$$ it is at -0.1, showing that there is some intertemporal dynamic in the basis that is being picked up.

The interesting patterns does however emerge once we examine how $$\beta_1$$ differes between countries. Where is it very high around -0.55 in Estonia, Sweden, and Poland. But quite low in places like Germany, Hungary, and Finland at around 0. Indicating that the market integration differs quite heavily between countries, and therefore the motivation for market actors to adjust to deviations in equilibriums. 

The resulting half life speed for every country in the dataset can be found in a map below:
<img src="src/output/alpha_map.png" alt="Revision speed" width="800">

As can be seen, many countries on the edge appears to have a very low adjustment speeds, but there are limitations too these results which brings me to my next sections

##### Limitations 
As can be seen, the edge cities are slow on traversing to equilibrium. However, the equilibrium is defined by all the countries in the dataset, therefore a country that shares alot of borders with countries outside the dataset may skew somewhat. Another limitation is that the frequency is of the data is monthly, which may be sensitive to this type of analysis.


## MATIF price analysis model (Temporal model)

#### Theory
The theory here is quite similar, it also relies on the law of one price, but from a centered persepctive which is France. Here we need to understand how basis occurs fully, which all lies in the different countries capabilities/incentives to adjust to the MATIF market in France. We know in a perfect market, that the basis ( difference between the local price and the MATIF price) should not be smaller or greater than the transport cost (including loading, fees, etc.) for the local country too France. But, we also know because of storage economics, expectations, and slow reaciton speeds this can in practice happen. Which can partially be explained by for example storage economics. With that said, not all trade is conducted on MATIF, and trade often happen outside markets in different agreements with long standing contract for example which can also skew results. 

#### Data
Here again, we use the same price data as in analysis one, but we do not have a need to construct a spatial weight matrix, so flow data etc is not included. 

#### Method
An error correction model is used here as well, but for a slighly different reason. The dependent variable in this case is the farmgate price for breadmaking wheat in a specific country, and the independent variable is the MATIF price, none of which are I(0) on its own, but both are cointegrated so therefore a ECM is apporpriate here as well constructed in this fashion.

Long run model:
$$
y_{i,t} = \beta_0 + \beta_1 X_{i,t} + 0\theta fixed effects_i + \mu_{i,t}
$$

Short run model:
$$
dy_{i,t} = \beta_0 + \beta_1 \mu_{i,t-1} + \beta_2 dX_{i,t-1} + \beta_3 dX_{i,t-1} +\theta Fixed effects_i + \theta War in Ukraine_t + \epsilon_{i,t}
$$


Here, y is the local farmgate price, X is the MATIF price, and d stands for the difference between now and one period back (I(1)).  All other variables are expressed the same as in the model previously

#### Results
Okay, so for the long run model, the $$\beta_1$$ coefficent corresponds to 0.89, meaning that if there is a 1 Euro increase in MATIF a month, there is also a 0.89 increase in farmgate prices. Differently expressed, the average basis between the European countries is at around 11% (1-0.89). But this is in no way weighted on quantity etc, so it is therefore more useful to explain this basis as within country mean basis, which is done in the map below:

## Conclusion
While the model has some limitations, the results suggest that European countries on average correct for spatial disequilibriums at a rate of about 29%, this rate does however vary extensly depending on geographical area. Where countries like Estonia seem to adjust very quickly to spatial disequilibriums, while countries like Bulgaria adjusts slower. This project does not at this point go into detail on what the cause of disequilibriums where, and if this would change the speed of adjustment. For this is a problem more apporpriatly addressed by a new project. 
