import torch
print(torch.cuda.is_available())


from geoparser import Geoparser
geo= Geoparser()
docs = geo.parse(["LA wildfire damages set to cost record $135bn Analysts estimate economic losses at more than $135bn as the fires burn through some of the most expensive property in the US. The Los Angeles wildfires are on track to be among the costliest in US history, with losses already expected to exceed $135bn (£109.7bn). In a preliminary estimate, private forecaster Accuweather said it expected losses of between $135bn-$150bn as the blazes rip through an area that is home to some of the most expensive property in the US. The insurance industry is also bracing for a major hit, with analysts from firms such as Morningstar and JP Morgan forecasting insured losses of more than $8bn. Fire authorities say more than 5,300 structures have been destroyed by the Palisades blaze, while more than 5,000 structures have been destroyed by the Eaton Fire. With authorities still working to contain the fires, the scope of the losses is still unfolding. These fast-moving, wind-driven infernos have created one of the costliest wildfire disasters in modern US history, AccuWeather Chief Meteorologist Jonathan Porter said. The 2018 fire that broke out in northern California near the town of Paradise currently ranks as the disaster with highest insured costs, at roughly $12.5bn, according to insurance giant Aon. That blaze, known as the Camp fire, killed 85 people and displaced more than 50,000. Aon said the high property values in this case mean it is likely to end up as one of the top five costliest wildfires on its list. Including properties that are not insured, the overall losses will be even bigger. Even after the situation is under control, Mr Porter said the events could have long-term effects on health and tourism. It also spells trouble for the insurance industry, which was already in crisis. Homeowners in the US with mortgages are typically required by banks to have property insurance. But companies have been hiking prices - or cancelling coverage altogether - in the face of increasing risks of natural disaster such as fires, floods and hurricanes. As companies stop offering coverage, people are turning in surging numbers to home insurance plans offered by state governments, which are typically more expensive while offering less protection. In California, the number of policies offered through the state's Fair plan has more than doubled since 2020, from about 200,000 to more than 450,000 in September of last year. Areas hit by the fires rank as some of the places with highest take-up, according to data from the programme, which was already warning of risks to its financial stability. Denise Rappmund, a senior analyst at Moody's Ratings, said the fires would have widespread, negative impacts for the state's broader insurance market. Increased recovery costs will likely drive up premiums and may reduce property insurance availability, she said, adding that the state was also facing potential long-term damage to property values and strain to public finances."])
for doc in docs:
    print(f"Document: {doc.text}")
    for toponym in doc.toponyms:
        print(f"- Toponym: {toponym.text}")
        location = toponym.location
        if location:
            print(f"  Resolved Location: {location['name']}, {location['country_name']}")
            print(f"  Feature Type: {location['feature_type']}")
            print(f"  Coordinates: ({location['latitude']}, {location['longitude']})")
            print(f"  Score: {toponym.score}")
        else:
            print("Location could not be resolved.")
    print()