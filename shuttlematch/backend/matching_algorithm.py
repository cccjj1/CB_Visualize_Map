#!/usr/bin/env python3
"""
Campus Shuttle Matching Algorithm
Uses standalone_optimizer.py for genetic algorithm optimization
"""
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

# Import optimizer classes from standalone_optimizer
from standalone_optimizer import (
    ImprovedGeneticOptimizer, Request, Stop, Trip, Assignment
)

# Import map generator
try:
    from map_generator import GoogleMapsGenerator
    MAP_GENERATION_AVAILABLE = True
except ImportError:
    MAP_GENERATION_AVAILABLE = False

def load_data():
    """Load all data"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    print("📥 Loading data...")
    
    # Load location data
    lat_lon_file = os.path.join(data_dir, 'lat-lon.csv')
    stops_df = pd.read_csv(lat_lon_file)
    stops = []
    for idx, row in stops_df.iterrows():
        stop = Stop(
            stop_id=f"STOP_{idx+1:03d}",
            name=row['Name'].strip(),
            lat=float(row['Latitude']),
            lng=float(row['Longitude']),
            stop_type='CAMPUS'
        )
        stops.append(stop)
    
    print(f"✅ Loaded {len(stops)} locations")
    
    # Load time matrix
    time_matrix_file = os.path.join(data_dir, 'matrix_12x12_time.csv')
    time_matrix_df = pd.read_csv(time_matrix_file, index_col=0)
    time_matrix_df.columns = [col.strip() for col in time_matrix_df.columns]
    time_matrix_df.index = [idx.strip() for idx in time_matrix_df.index]
    time_matrix = time_matrix_df.values
    
    print(f"✅ Loaded time matrix {time_matrix.shape}")
    
    # Load request data
    mock_file = os.path.join(data_dir, 'mock_request.csv')
    mock_df = pd.read_csv(mock_file)
    
    # Create location name to STOP_ID mapping
    location_to_stop_id = {}
    for idx, row in stops_df.iterrows():
        location_to_stop_id[row['Name'].strip()] = f"STOP_{idx+1:03d}"
    
    # Create Request objects
    requests = []
    for idx, row in mock_df.iterrows():
        origin = row['origin_stop_id'].strip()
        dest = row['dest_stop_id'].strip()
        
        origin_stop_id = location_to_stop_id.get(origin, f"STOP_001")
        dest_stop_id = location_to_stop_id.get(dest, f"STOP_002")
        
        request = Request(
            request_id=f"R{idx+1:06d}",
            student_id=row['student_id'].strip(),
            origin_stop_id=origin_stop_id,
            dest_stop_id=dest_stop_id,
            eta=str(row['eta']).strip(),
            boarding_time=str(row['boarding_time']).strip(),
            early_tol=int(row['early_tol']),
            late_tol=int(row['late_tol'])
        )
        requests.append(request)
    
    print(f"✅ Loaded {len(requests)} requests")
    
    return stops, requests, time_matrix, mock_df, location_to_stop_id

def run_optimization(stops, requests, time_matrix):
    """Run optimization algorithm"""
    print("\n🧬 Initializing optimizer...")
    
    optimizer = ImprovedGeneticOptimizer(
        requests=requests,
        stops=stops,
        time_matrix=time_matrix,
        capacity=12,
        min_passengers=2,
        max_vehicles=30,
        population_size=50,
        generations=50,
        mutation_rate=0.15,
        max_detour_factor=1.5
    )
    
    print("⏳ Running optimization algorithm...")
    trips, assignments = optimizer.optimize()
    
    print(f"✅ Optimization complete:")
    print(f"   - Generated routes: {len(trips)}")
    print(f"   - Matched passengers: {len(assignments)}")
    
    return trips, assignments

def generate_matches(mock_df, requests, assignments):
    """Generate matches from optimization results"""
    print("\n📊 Generating match results...")
    
    # Create mapping: request_id -> Request object
    request_map = {req.request_id: req for req in requests}
    
    # Create mapping: student_id -> match info (including trip_id)
    assignment_map = {}
    for assignment in assignments:
        # Get the request from the request_id
        request_obj = request_map.get(assignment.request_id)
        if request_obj:
            student_id = request_obj.student_id
            assignment_map[student_id] = {
                'matched': True,
                'pickup_time': assignment.boarding_time,
                'arrive_time': assignment.alighting_time,
                'trip_id': assignment.trip_id
            }
    
    # Generate match records for all requests
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    matches = []
    
    for idx, row in mock_df.iterrows():
        student_id = row['student_id'].strip()
        match_result = dict(row)
        match_result['request_date'] = tomorrow
        
        if student_id in assignment_map:
            # Matched
            info = assignment_map[student_id]
            match_result['matched'] = True
            match_result['pickup_time'] = info['pickup_time']
            match_result['arrive_time'] = info['arrive_time']
            match_result['trip_id'] = info['trip_id']
        else:
            # Not matched
            match_result['matched'] = False
            match_result['pickup_time'] = ''
            match_result['arrive_time'] = ''
            match_result['trip_id'] = ''
        
        matches.append(match_result)
    
    matched_count = sum(1 for m in matches if m['matched'] == True or m['matched'] == 'True')
    print(f"✅ Generated: {matched_count}/{len(matches)} requests matched")
    
    return matches

def save_matches(matches):
    """Save match results"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    matches_file = os.path.join(data_dir, 'matches.csv')
    
    matches_df = pd.DataFrame(matches)
    matches_df.to_csv(matches_file, index=False)
    print(f"💾 Results saved to {matches_file}")

def save_shuttle_routes(trips, stops):
    """Save shuttle route information to CSV"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    routes_file = os.path.join(data_dir, 'shuttle_routes.csv')
    
    # Create stop_id to name mapping
    stop_dict = {stop.stop_id: stop.name for stop in stops}
    
    # Build route records
    routes = []
    for trip in trips:
        # Extract stop names from route IDs
        route_stops = []
        for stop_id in trip.route:
            stop_name = stop_dict.get(stop_id, stop_id)
            route_stops.append(stop_name)
        
        route_record = {
            'trip_id': trip.trip_id,
            'vehicle_id': trip.vehicle_id,
            'start_time': trip.start_time,
            'end_time': trip.end_time,
            'start_stop': stop_dict.get(trip.start_stop_id, trip.start_stop_id),
            'end_stop': stop_dict.get(trip.end_stop_id, trip.end_stop_id),
            'duration_minutes': trip.duration_minutes,
            'passenger_count': trip.passenger_count,
            'route_sequence': ' -> '.join(route_stops)
        }
        routes.append(route_record)
    
    routes_df = pd.DataFrame(routes)
    routes_df.to_csv(routes_file, index=False)
    print(f"💾 Shuttle routes saved to {routes_file}")

def generate_route_maps(api_key: str = None):
    """Generate Google Maps images for shuttle routes"""
    if not MAP_GENERATION_AVAILABLE:
        print("⚠️ Map generation not available (requests library not installed)")
        return
    
    if not api_key:
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            print("⚠️ GOOGLE_MAPS_API_KEY not set, skipping map generation")
            return
    
    try:
        print("\n🗺️ Generating route maps...")
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        maps_dir = os.path.join(data_dir, 'maps')
        os.makedirs(maps_dir, exist_ok=True)
        
        generator = GoogleMapsGenerator(api_key)
        
        # Load data
        lat_lon_file = os.path.join(data_dir, 'lat-lon.csv')
        routes_file = os.path.join(data_dir, 'shuttle_routes.csv')
        
        locations = generator.load_locations(lat_lon_file)
        routes = generator.load_routes(routes_file)
        
        # Generate individual route maps
        generated_count = 0
        for route in routes:
            trip_id = route['trip_id']
            output_path = os.path.join(maps_dir, f"{trip_id}.png")
            
            if generator.save_route_map(route, locations, output_path):
                generated_count += 1
                print(f"  ✅ Generated map for {trip_id}")
            else:
                print(f"  ❌ Failed to generate map for {trip_id}")
        
        # Generate overall map
        overall_output = os.path.join(maps_dir, 'all_routes.png')
        if generator.save_all_routes_map(routes, locations, overall_output):
            generated_count += 1
            print(f"  ✅ Generated overall map showing all routes")
        
        print(f"✅ Generated {generated_count} maps")
        
    except Exception as e:
        print(f"❌ Error generating maps: {str(e)}")

def main():
    """Main function"""
    try:
        print("🚌 Starting Campus Shuttle Optimization Algorithm")
        print("="*60)
        
        # Load data
        stops, requests, time_matrix, mock_df, location_to_stop_id = load_data()
        
        # Run optimization
        trips, assignments = run_optimization(stops, requests, time_matrix)
        
        # Generate match results
        matches = generate_matches(mock_df, requests, assignments)
        
        # Save results
        save_matches(matches)
        
        # Save shuttle routes
        save_shuttle_routes(trips, stops)
        
        # Generate maps (if API key available)
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if api_key:
            generate_route_maps(api_key)
        
        print("\n" + "="*60)
        print("✅ Optimization Complete!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
