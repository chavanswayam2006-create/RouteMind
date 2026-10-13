% ==========================================================
% RouteMind AI - Prolog Knowledge Base (ISO Prolog)
% Intelligent Package Routing & Dispatch Rules
% ==========================================================

% --- DYNAMIC DECLARATIONS ---
:- dynamic road/6.
:- dynamic hub/3.
:- dynamic parcel/5.

% --- HUB FACTS: hub(Id, Name, Capacity) ---
hub('A', 'Central Dispatch Warehouse', 500).
hub('B', 'North Junction', 250).
hub('C', 'East Junction', 200).
hub('D', 'Industrial Hub', 350).
hub('E', 'City Centre Hub', 400).
hub('F', 'South Junction', 200).
hub('G', 'Final Delivery Hub', 600).

% --- ROAD FACTS: road(From, To, DistanceKm, TimeMin, CongestionPct, Status) ---
road('A', 'B', 12.0, 15.0, 25, unblocked).
road('B', 'A', 12.0, 15.0, 25, unblocked).
road('A', 'D', 14.0, 18.0, 30, unblocked).
road('D', 'A', 14.0, 18.0, 30, unblocked).
road('B', 'C', 18.0, 22.0, 20, unblocked).
road('C', 'B', 18.0, 22.0, 20, unblocked).
road('B', 'D', 15.0, 20.0, 40, unblocked).
road('D', 'B', 15.0, 20.0, 40, unblocked).
road('B', 'E', 16.0, 25.0, 55, unblocked).
road('E', 'B', 16.0, 25.0, 55, unblocked).
road('C', 'E', 12.0, 16.0, 45, unblocked).
road('E', 'C', 12.0, 16.0, 45, unblocked).
road('C', 'G', 16.0, 20.0, 35, unblocked).
road('G', 'C', 16.0, 20.0, 35, unblocked).
road('D', 'E', 15.0, 18.0, 30, unblocked).
road('E', 'D', 15.0, 18.0, 30, unblocked).
road('D', 'F', 20.0, 24.0, 20, unblocked).
road('F', 'D', 20.0, 24.0, 20, unblocked).
road('E', 'G', 14.0, 16.0, 40, unblocked).
road('G', 'E', 14.0, 16.0, 40, unblocked).
road('E', 'F', 13.0, 17.0, 25, unblocked).
road('F', 'E', 13.0, 17.0, 25, unblocked).
road('F', 'G', 12.0, 15.0, 25, unblocked).
road('G', 'F', 12.0, 15.0, 25, unblocked).

% --- PARCEL FACTS: parcel(ParcelId, Priority, Destination, WeightKg, MaxDelayMin) ---
parcel('PKG-901', high, 'G', 4.5, 30).
parcel('PKG-902', standard, 'E', 12.0, 90).
parcel('PKG-903', high, 'G', 1.8, 20).
parcel('PKG-904', economy, 'D', 25.0, 180).

% --- LOGICAL RULES ---

% Rule 1: Road availability (must be unblocked)
available_road(X, Y, Dist, Time, Cong) :-
    road(X, Y, Dist, Time, Cong, unblocked).

% Rule 2: High priority dispatch eligibility (unblocked AND congestion <= 60%)
can_dispatch_high_priority(X, Y) :-
    road(X, Y, _, _, Cong, unblocked),
    Cong =< 60.

% Rule 3: Standard dispatch eligibility (any unblocked road)
can_dispatch(X, Y, high) :- can_dispatch_high_priority(X, Y).
can_dispatch(X, Y, standard) :- road(X, Y, _, _, _, unblocked).
can_dispatch(X, Y, economy) :- road(X, Y, _, _, _, unblocked).

% Rule 4: Blocked road avoidance check
is_blocked(X, Y) :- road(X, Y, _, _, _, blocked).

% Rule 5: Recursive path existence with cycle avoidance
connected_path(X, Y, [X, Y]) :-
    road(X, Y, _, _, _, unblocked).
connected_path(X, Y, [X|Rest]) :-
    road(X, Z, _, _, _, unblocked),
    Z \= Y,
    connected_path(Z, Y, Rest).