# def lookup(library):
#     """Look up search query via google."""

#     if "library" in library:

#         # Contact API - won't work as removed API key because got bad email from G once uploaded to github :0
#         try:
#             response = requests.get(f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote_plus(library)}&inputtype=textquery&fields=formatted_address,name,user_ratings_total,place_id&key=")
#             response.raise_for_status()

#         except requests.RequestException:
#             return None

#         # Parse response
#         try:
#             libraryDetails = response.json()

#             return {
#                 "name" : libraryDetails["candidates"][0]["name"],
#                 # "place_id" : libraryDetails["candidates"][0]["place_id"],
#                 "address" : libraryDetails["candidates"][0]["formatted_address"],
#                 "ratings" : libraryDetails["candidates"][0]["user_ratings_total"]
#             }

#         except (KeyError, TypeError, ValueError):
#             return None

#     else:
#         library = library + " library"
#         return lookup(library)