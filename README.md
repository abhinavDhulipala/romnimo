# Romnimo

This project aims to explore better guarantees when we have a complete world state (the world view input is fed with an omniscient camera).

We set up a world, which is a 4 X 4 piece of plywood with 8 intersections with curves. There are passengers (virtualized), scattered throughout the map, that the cars are responsible for picking up. The robots dynamically respond to crashes and “changes in road conditions” and reroute cars accordingly. The high level idea is to split responsibility between the vehicles and the server.
