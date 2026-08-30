---
title: "A real test: examining ways to monetize a maps product"
date: 2021-01-24
categories:
  - product-articles
---

You have probably been given a problem when applying for a product-manager role, and you needed to complete a task based on it. The exercise below is an analysis of a real task for Cafe Bazaar.

The problem statement of this task said:

> For the second stage of the product-manager interview, we need to know and evaluate your analyses in a setting other than the interview. In that spirit, please examine the following problem in a text file, in 3 to 15 pages, within a maximum of 14 days:
> 
> Suppose we have a maps product whose main capabilities are routing and search.
> 
> Present three different methods for monetizing this product. Compare these methods and choose the more suitable one. Also, in your examination, specify at what point in the product’s life you should move toward each monetization method, along with the reason. Design a feasible roadmap (Roadmap) for releasing each of these monetization methods. If a method requires a new capability in the product, include implementing that capability in your planning.
> 
> At this stage our goal is to examine your approach, analytical power, inference, and attention to detail in the items above, so please try to keep these in mind while doing this task. You may need more data for some of the items above; you can estimate them. Also, if you used a particular data point or assumption, please cite the source in the text.

# Introduction and assumptions

To solve this exercise and to reduce assumptions and conjectures, the product in question is treated as similar to Balad’s position, and competitors are treated as the current players in Iran. Our assumption is that the product has two years of activity and 4 million users and is, by a small margin, first or second in the market. Other assumptions and estimates are given in the text.

Our next assumption is that, similar to foreign examples, earning money from the user in these systems is difficult, and because it is not a proven path it has a high cost, although this can be tested with a few MVPs on Iranian users. So the strategy taken is that by subsidizing the user side we can increase the map’s media power and earn money from another side.

![](images/JObfgikzxDclg31fLy0Akm5UC0nnqUhDrikvYorR8jxQMYqzUW5gdzj3VSxOGp4Jl4ZGBlL1iGnwiPeo1Vm9emxqfuE2Z2Q1ydfkHmCUwti514WkHCCfDqu7xblfEG2fvElbGGE8)

In current conditions, in my view the product is in an early stage (Early adopter / Introduction) and has not yet reached product–market fit in the Iranian market, because despite the many users it has, it has not yet reached sustainable monetization, and in addition, given potential customers, it has a small market share. For that reason the monetization models are presented with the assumption that the product is in the stage of finding product–market fit.

In cost–benefit analysis a kind of enhanced ScoreCard model is used, described in [this Virgool post](https://product.alibaba.ir/prioritize-backlog-part2-udexyi7nfzog).

## How to weight and prioritize capabilities

|  | **Benefit** | **Cost** |
| --- | --- | --- |
| **Value** | **revenue** | **Customer** | **Strategic** | **Org needs** | **Operation reduce** | **Developer** | **Business** | **Operation** | **Risk** |
| **500** | **60** | **20** | **20** | **0** | **0** | **20** | **30** | **40** | 10 |

### Benefit

Given that the focus of this exercise was on monetization, in the benefit section the highest coefficient was given to revenue. Even so, because growth of this revenue depends on the value created for the customer, and if a method is strategic it can also take a large market share, these two criteria formed the next coefficients. Organization need (which includes items such as financial transparency) and reducing operations were not the focus of this task and received a weight of zero.

### Cost

The main cost in this analysis is placed on the operations section, and the reason is Cafe Bazaar’s weakness in operations and operational matters outside the organization, similar to what was seen in the *Resid* product. After that, business has a larger share of cost, and finally developers, because they are Cafe Bazaar’s main advantage, were given the lowest cost. A small coefficient was also considered for risk, with the assumption that because the product is in an early stage (Early adopter / Introduction) it is ready for the risk of new and ambiguous monetization methods.

# Three different ways to monetize

To find these three models we examine similar foreign businesses through benchmarking.

At present the most important player in this domain is Google Maps. After that, other businesses such as Moovit or Citymapper have focused on this topic in a more specialized way.

It may be possible to monetize from the user as well, but because this is not common in these products I have not mentioned it in my examinations, although in practice I would prefer to examine this in a few MVPs on Iranian users as well, beyond global information.

In addition, given that I was previously the founder of a similar product, I have collected information about the revenue methods of these models. The product, named *Keraaye-chi*, was an app for showing the cheapest online taxi based on the user’s origin and destination and comparing the price of these services with taxis. The app was supposed to have more capabilities such as metro and bus prices and the arrival times of these services.

In that spirit, by examining Google Maps’ revenue model ([1](https://www.feedough.com/how-google-maps-works-makes-money/) and [2](https://www.investopedia.com/articles/investing/061115/how-does-google-maps-makes-money.asp) and [3](https://www.kamilfranek.com/how-google-maps-makes-money/)) the following occurred to me.

Monetization methods:

- Ranking businesses higher in search ($3.5 billion of Google revenue)
- Creating business pages and connecting with the audience
- Selling information to government, B2G
    - This does not seem to be a sustainable method for monetization, and the government also does not have the necessary trust and approach. Besides, for this work to be attractive a lot of data needs to have been collected, which, given the assumption that the app is less than a year old, is not logical and is more effective at the maturity stage.
- Partnership with online taxi companies, bike-sharing, and other stakeholders
    - Given that the players in this domain have shrunk to two main players, it is not attractive.
- Selling API (route, map, and places; Google has $0.8 billion in revenue)
    - Given the presence of many players and the investment of some (such as Snapp) in building a new map, it is not attractive.
- Showing some points as pinned with a logo on the map (chain locations)
- Announcing brand names by the voice guidance

## Ranking businesses higher in search along with suggesting an offer

Ranking businesses higher in exchange for a fee is one of the most common ways to earn money from a map. This capability works as follows: for example, when the user searches the word “restaurant” to see the best restaurants around them, the app shows the restaurant that advertised above the other results. Although this capability is very common, it has more users at the software’s maturity stage. For example, it seems Foursquare and Google Maps currently have more serious sources for search based on user reviews. So to reach this capability you have to complete the map’s content, which at present, for example, Balad has not reached.

### Cost–benefit analysis

| **Value** | **revenue** | **Customer** | **Strategic** | **Org needs** | **Operation reduce** | **Developer** | **Business** | **Operation** | **Risk** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **500** | **60** | **20** | **20** | **0** | **0** | **20** | **30** | **40** | 10 |
| \-30 | 3 | 3 | 3 | 0 | 0 | 4 | 2 | 4 | 3 |

### SWOT analysis

| Shortage of IT solutions for local businesses; no similar solution; people migrating to Iranian routing apps | High user base in maps and attractiveness of viewers for businesses; strong technical team; suitable infrastructure for scaling |
| --- | --- |
| Local businesses’ pessimism toward startups; most local businesses being traditional | Weak marketing and operations team; current map users not concentrated |

### User personas and user journey

Ali is a shopkeeper on Valiasr Street who sells clothing. He has recently opened this shop and wants to introduce it to others. Although with the current state of online stores he has no chance of dream sales, it has occurred to him that by focusing on a showroom and letting people try and touch the goods he can attract good customers; even so, for such work he can only attract people who are near him. One day, while trying Google Maps in Turkey, he noticed that through this tool he could also pull many people, including tourists, toward his store, so he allocated part of his profit to this work.

Reza loves wandering the city. Many times he searches a restaurant or cafe or store in apps or on the internet to go to new places; even so, he always has trouble finding new experiences and cannot easily find up-to-date offers on the internet.

### Competitive situation

At present in Iran there is no solution for this capability. Domestic maps such as Neshan and Daal lack this capability, and Google Maps and Foursquare also see little use because of payment problems. Although Foursquare attracted some attention from domestic businesses for a while, because of the drop in its market share in Iran this has become somewhat fainter.

### Product life-cycle analysis

This capability needs a suitable user base and is better used at Growth time so more businesses are encouraged to spend in this system and, with suitable return, get more retention. Even so, because the current product in question is number one in the market and the business owner’s spend model is also performance marketing based on the amount per click, the product can be launched with this amount of users but in a concentrated way and in particular neighborhoods.

### Market research on the monetization situation

There are 20,000 stores and local businesses in Tehran and 2 million businesses nationwide. If we receive an average of 1 million tomans per month we will have access to a market worth 2,000 billion tomans in the country and 20 billion tomans in Tehran.

### Implementing version 1: showing an ad tag in some searches in a particular neighborhood

We assume the map has the most users and the most time in the app (a criterion for engagement) in Tehran. In the first version a landing page about the benefits of this plan is implemented, which, along with design, takes two weeks from three people (one designer, two front-end programmers). After this, given that local businesses must be acquired locally in the same way, a 20-person acquisition team is gathered to focus on one of the high-search streets or neighborhoods. This team goes into stores and shops and introduces the system along with the benefits and a signup link.

After shopkeepers sign up they enter an activation process, and a three-person account-manager team manages campaign setup. In this version there is no panel on the shopkeeper side; after transferring the amount they coordinate the order by phone, and in a panel available to the company’s support staff the campaign is defined and a payment link is sent to businesses. So in this version there is no campaign panel.

**Metric: number of stores acquired / conversion of results containing an ad**

**KPI: presenting 6,000 stores to information registration / bringing 600 stores to a one-week trial model / retention and creating a one-month campaign from 60 stores / 1 percent click conversion rate on the ad**

**Cost: 80 million tomans for one month**

**Revenue: 60 million tomans (assuming AOV of 1 million tomans)**

### Implementing version 2: creating a panel for businesses to define a campaign

In this capability businesses can automatically sign up in the panel and define their campaign. Exactly like what was previously used in Adad ad networks and other systems. For that reason an accounting system is needed for business signup. This capability can be integrated with Cafe Bazaar’s ads system. After signing up, the user charges their account, then specifies their business location on the map and also enters other information such as business name, category, phone number, site, social networks, and hours of activity.

If the user searches a keyword such as “restaurant” or “kebab” or “family box” or other keywords, they see results on the map and see ads in the first result. In this section the user can also enter a compelling sentence that is shown under their name as an offer, for example: 50 percent off all women’s leather bags.

After that they enter the time and hours the campaign is active and the keywords, and finally after entering the cost per click they run the campaign.

To implement this panel we need one month of two backend programmers and one front-end, and two weeks of a designer, as well as six account-support people (assuming each account-support person creates and manages three accounts a day).

**Metric: number of stores acquired / conversion of results containing an ad**

**KPI: creating 600 campaigns per month / 2 percent click conversion rate on ads**

**Cost: 48 million tomans (assuming 10 million tomans salary for programmer and designer and 4 million tomans salary for support)**

**Revenue: 600 million tomans (assuming AOV of 1 million tomans)**

### Implementing version 3: creating a dedicated offer and showing ads based on user attributes

In this version the business owner can show more targeted and specific ads to the audience. These ads differ based on the user’s gender, age, and interests.

For this capability, gender and age must be collected in the user profile, and interests analyzed based on recent searches.

In this version the business owner can define various discount codes with different scenarios, unique or public, in the panel.

In that case, for example, the user searches the word “restaurant” and the first ad contains a discount code for buying from that restaurant.

Also in this version, if the offer is highly clicked, the offer is also shown as a bubble for some users on the map itself, to produce higher engagement and conversion.

To implement this version we need to implement discount-code infrastructure, management, and cancellation, which is done with two backend programmers and one front-end for one month and one product designer for two weeks. Also, given the growth in the number of stores, we need to increase account-support people to 20 (assuming processes and training have improved and each of these people answers more than 10 businesses a day).

Also in this version we assume this capability has reached other cities in the country as well, and businesses from those cities are also creating campaigns. To reach this number, local marketing campaigns must also be defined, and it is not easily achievable.

**Metric: number of stores acquired / conversion of results containing an ad**

**KPI: creating 6,000 campaigns per month / 5 percent conversion of results containing an ad**

**Cost: 115 million tomans (assuming 10 million tomans salary for programmer and designer and 4 million tomans salary for support)**

**Revenue: 6 billion tomans (assuming AOV of 1 million tomans)**

## Creating brand icons and announcing particular locations in voice guidance

In this capability a number of map pins change to particular brands, and the voice guidance also refers to these locations in its directions.

The customer for this capability is large and often chain businesses such as Refah, Kourosh, Shahrvand, and similar stores, banks, and so on.

One advantage of this model is that it has a simple implementation and no complex business mechanism. If the product has good brand awareness, this capability seems attractive to businesses, so it is not necessary to have a large user base or for users to have a high engagement rate. For example, the Balad app currently has a suitable brand given brand-ad advertising.

### Cost–benefit analysis

|  | **Benefit** | **Cost** |
| --- | --- | --- |
| **Value** | **revenue** | **Customer** | **Strategic** | **Org needs** | **Operation reduce** | **Developer** | **Business** | **Operation** | **Risk** |
| **500** | **60** | **20** | **20** | **0** | **0** | **20** | **30** | **40** | 10 |
| 200 | 4 | 4 | 4 | 0 | 0 | 2 | 5 | 0 | 1 |

### SWOT analysis

| Marketing channels saturated for chain and large businesses; serious, large-scale competition among chain businesses; attractiveness of the map as a new, modern channel | Strong technical team; suitable infrastructure for scaling; suitable brand to attract large businesses; high use of voice assistant |
| --- | --- |
| Low attractiveness of the map as media because it is nascent | Weak marketing and negotiation team; not enough users to attract large businesses |

### User personas

The Kourosh chain-store company, in tight competition with other chain stores, has saturated all marketing channels and is looking for new advertising methods. The company’s whole advantage is the breadth and number of branches, and it wants to make this known to local people. The company is looking for a platform that can show the user’s store locations on a map. Even so, if it offers an app in this area it would also have to spend a lot on marketing it, and it may not be cost-effective alone, so it tries to use other map platforms.

### Product life-cycle analysis

This capability is one of the few that can be implemented at the very beginning of the life cycle. The reason is that it depends more on how the media is positioned and the class of the media as seen by the organization and the negotiators and commercial relationships than on user base. So regardless of user count, the map media can be positioned in a valuable place so that chain businesses pay high amounts to be present in this media.

### Implementing version 1: offline collaboration and showing the icon statically

In this version, after a contract with the relevant store and organization, the company logo is received and placed in the app. In this version no panel or capability is given to the company, and the signup and management process is done entirely offline. To implement this capability one backend developer and one front-end developer are needed for two weeks. Two negotiators are also needed to finalize contracts, which may take about three months.

Because this capability is done more with the goal of brand awareness, it has little tracking capability. Given the spend of organizations of this size, it seems that from each one-year contract (which of course depends a great deal on the size of the organization) one could monetize between 200 and 500 million tomans.

**Metric: user click conversion rate on brand pins**

**KPI: 1 percent click conversion rate on the icon / 1 collaboration contract**

**Three-month cost (until the goal is reached): 70 million tomans (10 million tomans developer cost and 10 million tomans negotiator and operational costs)**

**Revenue: 300 million tomans**

### Implementing version 2: announcing discounts, festivals, and prizes as a popup during routing

In addition to the previous method, it is attractive for these organizations to be able to inform the user of the many festivals, discounts, and prizes they have and, at the right time, pull the user to the store or bank or other relevant location.

So in this version a panel must be given to the set so they can register their announcements in that section. After the contract, which is still done offline, the user in the relevant panel can specify a message and also specify its audience so that if those people are nearby the message is shown to them.

To implement this capability we need two backend developers and one Android developer for one month and one product designer. Negotiators must also follow up for about six months to finalize 10 contracts.

**Metric: user click conversion rate on brand pins**

**KPI: 5 percent click conversion rate on the icon / 10 collaboration contracts**

**Six-month cost (until the goal is reached): 160 million tomans (10 million tomans developer cost and 10 million tomans negotiator and operational costs)**

**Revenue: 5 billion tomans (assuming companies became more serious)**

## Business pages and connecting with the audience

Smaller businesses can, at a low cost, build dedicated pages for themselves and that way gain identity locally for people in the same neighborhood.

Given that this system is similar to the system implemented for Divar, a good connection can also be made between these two systems, and for example by registering their business on Divar the user also gets a dedicated page on the Balad map and from there sells their goods or chats with potential customers. The advantage of this method relative to Divar is providing a setting in which the user can decide based on nearby businesses, and a stronger local connection is created.

The advantage of combining this capability with the map is that the user can find local businesses and, if a problem arises, follow up in person, and has more confidence buying from these businesses.

Because it is low-cost, this capability can also be well received outside Tehran.

### Cost–benefit analysis

|  | **Benefit** | **Cost** |
| --- | --- | --- |
| **Value** | **revenue** | **Customer** | **Strategic** | **Org needs** | **Operation reduce** | **Developer** | **Business** | **Operation** | **Risk** |
| **500** | **60** | **20** | **20** | **0** | **0** | **20** | **30** | **40** | 10 |
| 250 | 4 | 5 | 3 | 0 | 1 | 4 | 1 | 0 | 4 |

### SWOT analysis

| Drop in local-business sales because of COVID; drop in local-business sales because of the growth of online stores | Relatively high user base in maps and attractiveness of viewers for businesses; strong technical team; ready chat infrastructure; ready store infrastructure |
| --- | --- |
| Fading identity of local businesses and these businesses being forgotten in people’s minds | Weak marketing team; weak engagement in the current product |

### Market research on the monetization situation

Because this capability can put a lot of capability in the business’s hands at low cost, it has a much larger market size and can easily attract half of Iran’s 2 million businesses, which provides an annual market size of 1,200 billion tomans.

### Implementing version 1: showing a special badge to businesses and the ability to chat with customers

In this version business owners can, by paying a monthly amount, officially register their business in the app and own a space for conversation with customers. So they can easily connect with local users.

In the first version, by making their account special, businesses receive a badge and their chat is activated. It seems that by receiving 100,000 tomans per month a good range of local businesses can be attracted to this network.

After pressing the “Become special” button, the business owner reads the benefits of this plan and completes their business information. Then they click the payment button and activate this capability.

To implement this version we can use open-source chat infrastructure or Divar’s chat system, which brings development cost down a great deal.

In the end, with two backend programmers, one front-end programmer, and one product designer for one month we can reach this capability. For marketing this work we can also design a page and introduce the capability inside the app itself as a banner.

**Metric: number of stores acquired / click conversion on specials / duration of user chats**

**KPI: 1,000 businesses becoming special in the first month after soft launch nationwide (in the soft launch the banner is shown in the app at limited hours so inbound volume is controlled) / 1 percent more conversion on stores relative to the normal state**

**Cost: 40 million tomans (assuming 10 million tomans salary for programmer and designer)**

**Revenue: 100 million tomans**

### Implementing version 2: connection with Divar chat and the ability to sell online

In this version businesses are connected to their Divar page and can sell their goods on Divar online. In that case they can also introduce a variety of goods to local people.

To implement this capability three backend programmers, one product designer, and two Android programmers are needed for 1 month.

This capability may of course have complex logistical and integration complexities.

**Metric: number of stores acquired / click conversion on specials / duration of user chats / number of purchases relative to active stores**

**KPI: 10,000 businesses becoming special nationwide / 5 percent conversion on stores relative to the normal state**

**Cost: 60 million tomans (assuming 10 million tomans salary for programmer and designer)**

**Revenue: 1 billion tomans**

# Roadmap

Given the cost–benefit analysis and comparing the cost of each item, the “making businesses special and the ability to chat” capability is among the most money-making methods.

|  |  | **Benefit** | **Cost** |
| --- | --- | --- | --- |
| Name | **Value** | **revenue** | **Customer** | **Strategic** | **Org needs** | **Operation reduce** | **Developer** | **Business** | **Operation** | **Risk** |
|  | **500** | **60** | **20** | **20** | **0** | **0** | **20** | **30** | **40** | 10 |
| Ranking businesses higher in search | \-30 | 3 | 3 | 3 | 0 | 0 | 4 | 2 | 4 | 3 |
| Pinning particular businesses | 200 | 4 | 4 | 4 | 0 | 0 | 2 | 5 | 0 | 1 |
| Special businesses and the ability to chat | 250 | 4 | 5 | 3 | 0 | 1 | 4 | 1 | 0 | 4 |

Even so, we can implement the first version of each of these capabilities and complete the full version over time.

After three months (considering error and unforeseen events, after 5 months) the status of each of the MVPs is examined, and based on goals reached or not reached we decide to continue developing each. We assume all three MVPs reached what we expected, so in the rest of the path we develop the ads feature, because in later versions it has essential, vital changes and in practice the capability reaches its key goals in versions 2 and 3.

| Month | Revenue (million tomans) |  |
| --- | --- | --- |
| First | 100 | Implementing version 1: showing a special badge to businesses and the ability to chat with customers |
| Second | 300 | Implementing version 1: offline collaboration and showing a static icon |
| Third | 60 | Implementing version 1: showing an ad tag in some searches in a particular neighborhood |
| Fourth |  | Examining data and analyzing results to replan the roadmap (assuming the conjectures are confirmed) |
| Fifth | 600 | Implementing version 2: creating a panel for businesses to define a campaign |
| Sixth | 6000 | Implementing version 3: creating a dedicated offer and showing ads based on user attributes |
| Seventh | 1000 | Implementing version 2: connection with Divar chat and the ability to sell online |
| Eighth | 5000 | Implementing version 2: announcing discounts, festivals, and prizes as a popup during routing |
