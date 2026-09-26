# Model
Wheat equilibrium model for European countries, focusing on run price movements and market integration. It uses a Error correction model to study long-run spatial price equilibrium between European countries for the wheat market of bread making quality wheat, using data from the European commission for price and trade flows. 

## Background
This analysis is built upon my previous spatial disequilibrium analysis. Where I examin how the error term of a spatial lag model differ between countries, and compare it to the mean error term of all countries in a fashion to create a Spatial Disequilibrium Index (SDI). Since mean reversion was present in this SDI, I also tested whether the variable had predicitive power which turned out to be the case. 
Upon further investigation, I found that my analysis was lacking in terms of both method and data on certain areas. This is why I developed this newer slightly more sofisticated model, with a new method and updated data.

## Theory 
So the theory of spatial equilibrium between markets and the law of one price is not something new. Where prices for the same commodity in theory should converge to the point where the difference is equal to the cost of transportation. This is quite simply illustrated with a world where we only have two countries. Where if equilibrium price in country A is below the equilibrium price of country B to a factor higher than the transportation cost, then trade should be conducted until prices converge such that the price in country A should be exactly the price in country B - the transportation cost and a spatial equilibrium between the markets emerge. 

Of course in a real world scenario you have webs of countries with different supply and demand curves operating simultaniously creating different prices as well as different rates of change in price, all with different transportation costs between them. To complicate matters even further, these countries can act as hubs for other countries creating a entire network between markets. Lastly, we also have temporal issues to deal with, such as storage economics. Where market participants can speculate and store goods, in order to sell them at a more advantagous times. This all creates a beutiful cluster of different components making up the price of wheat which we have today, and which market operators have to navigate. 

## Mission
My mission with this analysis is to try to establish a long-run price equilibrium between European markets, and then study how fast different countries usually traverse back towards an equilibrium once a deviation has been made. While from this it is not possible to untagnle how and from which component the price deviation stems from, I will at least study the recovery phase for any long-run trends.
This could be beneficial for farmers or farmer associated trading organistaions. Since if harvest happen during a disequilibrium, the knowledge of recovery time could assist in determining the strategy for sellig. For example in determining wheather to store the harvest, sell it locally, or export it. But it could also assist when for example dealing with hedges. Since the regional market for wheat (MATIF) lies in France, a hedge againt say wheat in Finland may only be conducted through the french market. Therefore determining recovery time in any local disequilibrium both in France and in Finland could help in making such hedge.

## Data
To do this analysis I will take advantage of data from EUROSTAT for country specific wheat prices going back until 2005, as well as trade flows of wheat between European countries going back the same lenght. 
In order to not confuse global macro price events with regional deviations in wheat prices, I will extract the MATIF price movements from the local farm-gate prices. This new price will be refered to as the idiosyncratic price. Meaning price movement which is not a common movement across all countries. Since I already know that prices move togheter with the global market, but I am rather more interested in how prices shift because of local price changes. So rather then wanting to capture how European prices are effected by wide inflation for example, I want to see how prices are effected by local unpredicted yield for example and how the market responds to that. 

To then establish the relationship between countries, I use trade flow between countries as well as distance in order to construct a gravity fitted spatial weight matrix. Where I regress the trade flow on geographical distance between countries, weather they share a river, or if they are costal in order to circumvent endogenity problems. 

## Method:
I use a Error Correction Model (ECM) to then build my model. The idea here is to first establish the equilibrum relationship betwenn countries in idiosyncratic price. When this is done, I will investigate how deviations from this relationship corrects itself over time.
### Long-run relationship
To test this long-run relationship, I just run the panel data regression specified below:

$$
y_{i,t} = \beta_0 + \beta_1 Wy_{i,t} + 0\theta fixed effects_i + \mu_{i,t}
$$

Where y is the idiosyncratic price, and W is the gravity fitted spatial weight matrix. The long-run relationship can then be shown in $$\beta_1$$ and for my model corresponds to 0.43 and is significant at the 97% level.
The interpretation of this is that in general, when spatially weighted idiosyncratic price increases with 1 euro, the idiosyncratic price of the local market increases with 0.43 Euro.

### Short-run deviations

You then save the $$\mu_{i,t} $$ from the previous model, which is the idiosyncratic price movement in location i which deviates from the spatially weighted idiosyncratic price movements, which should correspond to a spatial disequilibrium. 

I then take the change in each variable and run my next regression which looks like this:

$$
dy_{i,t} = \beta_0 + \beta_1 \mu_{i,t-1} + \beta_2 dWy_{i,t-1} + \beta_3 dy_{i,t-1} + \beta_4 dy_{i,t-2} + \epsilon_{i,t}
$$

Here $$y_{i,t}$$ still stands for idiosyncratic price, $$Wy_{i,t-1}$$ stands for spatially weighted idiosyncratic price of neighbours, the d stands for the difference between t and t-1, and $$\epsilon_{i,t}$$ is the error term.

Interpretation of these coefficients are a bit tricky, so i will explain them here. 
The coefficient of $$\mu$$ shows the speed of adjustment from a disequilibrium, meaning how fast a deviation from the relationship between $$y_{i,t}$$ and $$Wy_{i,t}$$ is corrected.
The coefficent from $$dWy_{i,t-1}$$ shows short-run spatial transmission, how much a change in the spatially weighted idiosyncratic price effects the change in local idiosyncratic price. 
The coefficient for $$dy_{i,t-1}$$ and $$dy_{i,t-2}$$ shows the own price dynamic, how momentum transfer intertemporally in a country in terms of idiosyncratic price. 

## Results

Okay, so from my model the $$\beta_1$$ is around -0.29, meaning that when deviation from the equilibrium price happens in a country, 29% of the previous-period disequilibrium is corrected per month, meaning that half the correction is apporximatly done within 2 months time. This coefficient is also significant and within a 95% confidence interval of -0.37 to -0.2. 
For $$\beta_2$$ we have a positive coefficient of 0.03, meaning that a positive price change in Europe can correspond to a positive price change in the local country, but this coefficient is not significant so we may assume no statistical relationship at least. 
The coefficients $$\beta_3$$ is significant and around -0.073, while $$\beta_4$$ is not significant, showing that there is some intertemporal price dynamic that is being picked up, but it disappears quite quickly.

The interesting patterns does however emerge once we examine how $$\beta_1$$ differes between countries. Where is it very high around -0.55 in Estonia, Germany, and France. But quite low in places like Bulgaria, Romania, and Finland at around -0.11. Indicating that the market integration differs quite heavily between countries, and therefore the motivation for market actors to adjust to deviations in equilibriums. 

The resulting half life speed for every country in the dataset can be found in a map below:
<img src="src/output/alpha_map.png" alt="Revision speed" width="800">

As can be seen, many countries on the edge appears to have a very low adjustment speeds, but there are limitations too these results which brings me to my next sections

### Limitations 
As can be seen, the edge cities are slow on traversing to equilibrium. However, the equilibrium is defined by all the countries in the dataset, therefore a country that shares alot of borders with countries outside the dataset may skew somewhat. Another limitation is that the frequency is of the data is monthly, which may be sensitive to this type of analysis.

## Conclusion
While the model has some limitations, the results suggest that European countries on average correct for spatial disequilibriums at a rate of about 29%, this rate does however vary extensly depending on geographical area. Where countries like Estonia seem to adjust very quickly to spatial disequilibriums, while countries like Bulgaria adjusts slower. This project does not at this point go into detail on what the cause of disequilibriums where, and if this would change the speed of adjustment. For this is a problem more apporpriatly addressed by a new project. 
